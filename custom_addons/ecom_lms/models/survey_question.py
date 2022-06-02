# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import collections
import json
import itertools
import operator
from odoo.tools.translate import html_translate
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import base64
import logging
import os
import qrcode

from io import BytesIO


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    # validation_email = fields.Boolean('Input must be an email')

    custom_question_type = fields.Selection([
        ('text_box', 'Long Answer'),
        ('char_box', 'Short Answer'),
        ('numerical_box', 'Fill in the Blanks'),
        ('simple_choice', 'True/False'),
        ('multiple_choice', 'Multiple choice'),
    ],
        default='text_box', readonly=False, store=True, compute='_compute_custom_question_type',
        help='To choose question type.')

    certificate_wiz_id = fields.Many2one('upload.certificate.quiz', 'Certificate Wiz')

    @api.depends('custom_question_type', 'scoring_type', 'answer_date', 'answer_datetime', 'answer_numerical_box')
    def _compute_is_scored_question(self):
        """ Computes whether a question "is scored" or not. Handles following cases:
          - inconsistent Boolean=None edge case that breaks tests => False
          - survey is not scored => False
          - 'date'/'datetime'/'numerical_box' question types w/correct answer => True
            (implied without user having to activate, except for numerical whose correct value is 0.0)
          - 'simple_choice / multiple_choice': set to True even if logic is a bit different (coming from answers)
          - question_type isn't scoreable (note: choice questions scoring logic handled separately) => False
        """
        for question in self:
            if question.is_scored_question is None or question.scoring_type == 'no_scoring':
                question.is_scored_question = False
            # elif question.custom_question_type == 'date':
            #     question.is_scored_question = bool(question.answer_date)
            # elif question.custom_question_type == 'datetime':
            #     question.is_scored_question = bool(question.answer_datetime)
            elif question.custom_question_type == 'numerical_box' and question.answer_numerical_box:
                question.is_scored_question = True
            elif question.custom_question_type in ['simple_choice', 'multiple_choice']:
                question.is_scored_question = True
            else:
                question.is_scored_question = False

    @api.depends('is_page')
    def _compute_custom_question_type(self):
        for question in self:
            if not question.custom_question_type or question.is_page:
                question.custom_question_type = False

    @api.depends('custom_question_type')
    def _compute_save_as_nickname(self):
        for question in self:
            if question.custom_question_type != 'char_box':
                question.save_as_nickname = False

    def _prepare_statistics(self, user_input_lines):

        """ Compute statistical data for questions by counting number of vote per choice on basis of filter """
        all_questions_data = []
        for question in self:
            question_data = {'question': question, 'is_page': question.is_page}

            if question.is_page:
                all_questions_data.append(question_data)
                continue

            # fetch answer lines, separate comments from real answers
            all_lines = user_input_lines.filtered(lambda line: line.question_id == question)
            if question.custom_question_type in ['simple_choice', 'multiple_choice']:
                answer_lines = all_lines.filtered(
                    lambda line: line.answer_type == 'suggestion' or (
                            line.answer_type == 'char_box' and question.comment_count_as_answer)
                )
                comment_line_ids = all_lines.filtered(lambda line: line.answer_type == 'char_box')
            else:
                answer_lines = all_lines
                comment_line_ids = self.env['survey.user_input.line']
            skipped_lines = answer_lines.filtered(lambda line: line.skipped)
            done_lines = answer_lines - skipped_lines
            question_data.update(
                answer_line_ids=answer_lines,
                answer_line_done_ids=done_lines,
                answer_input_done_ids=done_lines.mapped('user_input_id'),
                answer_input_skipped_ids=skipped_lines.mapped('user_input_id'),
                comment_line_ids=comment_line_ids)
            question_data.update(question._get_stats_summary_data(answer_lines))

            # prepare table and graph data
            table_data, graph_data = question._get_stats_data(answer_lines)
            question_data['table_data'] = table_data
            question_data['graph_data'] = json.dumps(graph_data)

            all_questions_data.append(question_data)
        return all_questions_data


class Survey(models.Model):
    _name = 'survey.survey'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin', 'survey.survey']

    signature_tem = fields.Html(string="Digital Signature")

    def attempts_val(self, partner_id):
        count = 0
        if partner_id:
            attempts_ids = self.env['survey.user_input'].sudo().search(
                [('partner_id', '=', partner_id.id), ('survey_id', '=', self.id)])

            if attempts_ids:
                for attempt in attempts_ids:
                    count = count + 1

        return count


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input.line'

    @api.model
    def _get_answer_score_values(self, vals, compute_speed_score=True):
        """ Get values for: answer_is_correct and associated answer_score.

        Requires vals to contain 'answer_type', 'question_id', and 'user_input_id'.
        Depending on 'answer_type' additional value of 'suggested_answer_id' may also be
        required.

        Calculates whether an answer_is_correct and its score based on 'answer_type' and
        corresponding question. Handles choice (answer_type == 'suggestion') questions
        separately from other question types. Each selected choice answer is handled as an
        individual answer.

        If score depends on the speed of the answer, it is adjusted as follows:
         - If the user answers in less than 2 seconds, they receive 100% of the possible points.
         - If user answers after that, they receive 50% of the possible points + the remaining
            50% scaled by the time limit and time taken to answer [i.e. a minimum of 50% of the
            possible points is given to all correct answers]

        Example of returned values:
            * {'answer_is_correct': False, 'answer_score': 0} (default)
            * {'answer_is_correct': True, 'answer_score': 2.0}
        """
        user_input_id = vals.get('user_input_id')
        answer_type = vals.get('answer_type')
        question_id = vals.get('question_id')
        if not question_id:
            raise ValueError(_('Computing score requires a question in arguments.'))
        question = self.env['survey.question'].browse(int(question_id))

        # default and non-scored questions
        answer_is_correct = False
        answer_score = 0

        # record selected suggested choice answer_score (can be: pos, neg, or 0)
        if question.custom_question_type in ['simple_choice', 'multiple_choice']:
            if answer_type == 'suggestion':
                suggested_answer_id = vals.get('suggested_answer_id')
                if suggested_answer_id:
                    question_answer = self.env['survey.question.answer'].browse(int(suggested_answer_id))
                    answer_score = question_answer.answer_score
                    answer_is_correct = question_answer.is_correct
        # for all other scored question cases, record question answer_score (can be: pos or 0)
        elif question.is_scored_question:
            answer = vals.get('value_%s' % answer_type)
            if answer_type == 'numerical_box':
                answer = float(answer)
            elif answer_type == 'date':
                answer = fields.Date.from_string(answer)
            elif answer_type == 'datetime':
                answer = fields.Datetime.from_string(answer)
            if answer and answer == question['answer_%s' % answer_type]:
                answer_is_correct = True
                answer_score = question.answer_score

        if compute_speed_score and answer_score > 0:
            user_input = self.env['survey.user_input'].browse(user_input_id)
            session_speed_rating = user_input.exists() and user_input.is_session_answer and user_input.survey_id.session_speed_rating
            if session_speed_rating:
                max_score_delay = 2
                time_limit = question.time_limit
                now = fields.Datetime.now()
                seconds_to_answer = (now - user_input.survey_id.session_question_start_time).total_seconds()
                question_remaining_time = time_limit - seconds_to_answer
                # if answered within the max_score_delay => leave score as is
                if question_remaining_time < 0:  # if no time left
                    answer_score /= 2
                elif seconds_to_answer > max_score_delay:
                    time_limit -= max_score_delay  # we remove the max_score_delay to have all possible values
                    score_proportion = (time_limit - seconds_to_answer) / time_limit
                    answer_score = (answer_score / 2) * (1 + score_proportion)

        return {
            'answer_is_correct': answer_is_correct,
            'answer_score': answer_score
        }


class SurveyUserInput(models.Model):
    _name = "survey.user_input"
    _inherit = ['portal.mixin', 'survey.user_input']

    qr_code = fields.Binary(attachment=True)

    def save_lines(self, question, answer, comment=None):
        """ Save answers to questions, depending on question type

            If an answer already exists for question and user_input_id, it will be
            overwritten (or deleted for 'choice' questions) (in order to maintain data consistency).
        """
        old_answers = self.env['survey.user_input.line'].search([
            ('user_input_id', '=', self.id),
            ('question_id', '=', question.id)
        ])

        if question.custom_question_type in ['char_box', 'text_box', 'numerical_box']:
            self._save_line_simple_answer(question, old_answers, answer)
            if question.save_as_email and answer:
                self.write({'email': answer})
            if question.save_as_nickname and answer:
                self.write({'nickname': answer})

        elif question.custom_question_type in ['simple_choice', 'multiple_choice']:
            self._save_line_choice(question, old_answers, answer, comment)
        # elif question.question_type == 'matrix':
        #     self._save_line_matrix(question, old_answers, answer, comment)
        else:
            raise AttributeError(question.question_type + ": This type of question has no saving function")

    def _save_line_choice(self, question, old_answers, answers, comment):
        if not (isinstance(answers, list)):
            answers = [answers]
        vals_list = []
        if question.custom_question_type == 'simple_choice':
            if not question.comment_count_as_answer or not question.comments_allowed or not comment:
                vals_list = [self._get_line_answer_values(question, answer, 'suggestion') for answer in answers]
        elif question.custom_question_type == 'multiple_choice':
            vals_list = [self._get_line_answer_values(question, answer, 'suggestion') for answer in answers]

        if comment:
            vals_list.append(self._get_line_comment_values(question, comment))

        old_answers.sudo().unlink()
        return self.env['survey.user_input.line'].create(vals_list)

    def _save_line_simple_answer(self, question, old_answers, answer):
        vals = self._get_line_answer_values(question, answer, question.custom_question_type)
        if old_answers:
            old_answers.write(vals)
            return old_answers
        else:
            return self.env['survey.user_input.line'].create(vals)

    @api.depends('user_input_line_ids.answer_score', 'user_input_line_ids.question_id',
                 'predefined_question_ids.answer_score')
    def _compute_scoring_values(self):
        for user_input in self:
            # sum(multi-choice question scores) + sum(simple answer_type scores)
            total_possible_score = 0
            for question in user_input.predefined_question_ids:
                if question.custom_question_type in ['simple_choice', 'multiple_choice']:
                    total_possible_score += sum(
                        score for score in question.mapped('suggested_answer_ids.answer_score') if score > 0)
                elif question.is_scored_question:
                    total_possible_score += question.answer_score

            if total_possible_score == 0:
                user_input.scoring_percentage = 0
                user_input.scoring_total = 0
            else:
                score_total = sum(user_input.user_input_line_ids.mapped('answer_score'))
                user_input.scoring_total = score_total
                score_percentage = (score_total / total_possible_score) * 100
                user_input.scoring_percentage = round(score_percentage, 2) if score_percentage > 0 else 0

    def _prepare_statistics(self):
        res = dict((user_input, {
            'correct': 0,
            'incorrect': 0,
            'partial': 0,
            'skipped': 0,
        }) for user_input in self)
        scored_questions = self.mapped('predefined_question_ids').filtered(lambda question: question.is_scored_question)

        for question in scored_questions:
            if question.custom_question_type in ['simple_choice', 'multiple_choice']:
                question_correct_suggested_answers = question.suggested_answer_ids.filtered(
                    lambda answer: answer.is_correct)
            for user_input in self:
                user_input_lines = user_input.user_input_line_ids.filtered(lambda line: line.question_id == question)
                if question.custom_question_type in ['simple_choice', 'multiple_choice']:
                    res[user_input][
                        self._choice_question_answer_result(user_input_lines, question_correct_suggested_answers)] += 1
                else:
                    res[user_input][self._simple_question_answer_result(user_input_lines)] += 1

        return [[
            {'text': _("Correct"), 'count': res[user_input]['correct']},
            {'text': _("Partially"), 'count': res[user_input]['partial']},
            {'text': _("Incorrect"), 'count': res[user_input]['incorrect']},
            {'text': _("Unanswered"), 'count': res[user_input]['skipped']}
        ] for user_input in self]


class SurveyTemplate(models.Model):
    _name = 'survey.template'

    website_description = fields.Html('Website Description', translate=html_translate, sanitize_attributes=False,
                                      sanitize_form=False)
    # _inherit = ['hr.payslip','portal.mixin']
