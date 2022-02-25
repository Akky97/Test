from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class customElearningQuestion(models.Model):
    _inherit = 'slide.question'

    custom_question_type = fields.Selection([
        ('text_box', 'Long Answer'),
        ('char_box', 'Short Answer'),
        ('numerical_box', 'Fill in the Blanks'),
        ('simple_choice', 'True/False'),
        ('multiple_choice', 'Multiple choice'),
    ],
        default='text_box', required=True, help='To choose question type.')

    is_scored_question = fields.Boolean(
        'Scored', compute='_compute_is_scored_question',
        readonly=False, store=True, copy=True,
        help="Include this question as part of quiz scoring. Requires an answer and answer score to be taken into account.")
    description = fields.Html(string="Description")
    is_page = fields.Boolean('Is a page?')
    textchar = fields.Text(string="Multiple Line Text Box")
    charbox = fields.Text(string="Single Line Text Box")
    # scoring_type = fields.Selection(related='survey_id.scoring_type', string='Scoring Type', readonly=True)
    # survey_id = fields.Many2one('slide.slide', string='Start', ondelete='cascade')

    # -- options
    cons_mandatory = fields.Boolean(string="Mandatory Answer")

    # -- matrix
    matrix_subtype = fields.Selection([
        ('simple', 'One choice per row'),
        ('multiple', 'Multiple choices per row')], string='Matrix Type', default='simple')
    matrix_row_ids = fields.One2many(
        'slide.answer', 'matrix_question_id', string='Matrix Rows', copy=True,
        help='Labels used for proposed choices: rows of matrix')

    # -- char_box
    save_as_email = fields.Boolean(
        "Save as user email", compute='_compute_save_as_email', readonly=False, store=True, copy=True,
        help="If checked, this option will save the user's answer as its email address.")
    save_as_nickname = fields.Boolean(
        "Save as user nickname", compute='_compute_save_as_nickname', readonly=False, store=True, copy=True,
        help="If checked, this option will save the user's answer as its nickname.")

    # -- display & timing options
    column_nb = fields.Selection([
        ('12', '1'), ('6', '2'), ('4', '3'), ('3', '4'), ('2', '6')],
        string='Number of columns', default='12',
        help='These options refer to col-xx-[12|6|4|3|2] classes in Bootstrap for dropdown-based simple and multiple choice questions.')
    is_time_limited = fields.Boolean("The question is limited in time",
                                     help="Currently only supported for live sessions.")
    time_limit = fields.Integer("Time limit (seconds)")

    # -- simple choice / multiple choice / matrix
    suggested_answer_ids = fields.One2many(
        'slide.answer', 'question_id', string='Types of answers', copy=True,
        help='Labels used for proposed choices: simple choice, multiple choice and columns of matrix')
    allow_value_image = fields.Boolean('Images on answers',
                                       help='Display images in addition to answer label. Valid only for simple / multiple choice questions.')

    # -- scoreable/answerable simple answer_types: numerical_box / date / datetime
    answer_numerical_box = fields.Float('Correct numerical answer', help="Correct number answer for this question.")
    answer_date = fields.Date('Correct date answer', help="Correct date answer for this question.")
    answer_datetime = fields.Datetime('Correct datetime answer', help="Correct date and time answer for this question.")
    answer_score = fields.Float('Score', help="Score value for a correct answer to this question.")

    # -- question validation
    validation_required = fields.Boolean('Validate entry')
    validation_email = fields.Boolean('Input must be an email')
    validation_length_min = fields.Integer('Minimum Text Length', default=0)
    validation_length_max = fields.Integer('Maximum Text Length', default=0)
    validation_min_float_value = fields.Float('Minimum value', default=0.0)
    validation_max_float_value = fields.Float('Maximum value', default=0.0)
    validation_min_date = fields.Date('Minimum Date')
    validation_max_date = fields.Date('Maximum Date')
    validation_min_datetime = fields.Datetime('Minimum Datetime')
    validation_max_datetime = fields.Datetime('Maximum Datetime')
    validation_error_msg = fields.Char('Validation Error message', translate=True,
                                       default=lambda self: _("The answer you entered is not valid."))
    constr_mandatory = fields.Boolean('Mandatory Answer')
    constr_error_msg = fields.Char('Error message', translate=True,
                                   default=lambda self: _("This question requires an answer."))

    # -- comments (simple choice, multiple choice, matrix (without count as an answer))
    comments_allowed = fields.Boolean('Show Comments Field')
    comments_message = fields.Char('Comment Message', translate=True,
                                   default=lambda self: _("If other, please specify:"))
    comment_count_as_answer = fields.Boolean('Comment Field is an Answer Choice')

    def translate_slide_qus_title_data(self):
        translate_slide_qus_id = self.env['slide.question.title.translation'].search(
            [('slide_qus_id', '=', self.id), ('slide_id', '=', self.slide_id.id)], limit=1)
        if translate_slide_qus_id:
            return {
                'name': ('Translate'),
                'view_mode': 'form',
                'res_model': 'slide.question.title.translation',
                'views': [(self.env.ref('ecom_lms.slide_qus_title_translation_wiz_form_view').id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': translate_slide_qus_id.id,
            }

        else:
            title_translation_id = self.env['slide.question.title.translation'].create(
                {'slide_qus_id': self.id, 'slide_id': self.slide_id.id})
            return {
                'name': ('Translate'),
                'view_mode': 'form',
                'res_model': 'slide.question.title.translation',
                'views': [(self.env.ref('ecom_lms.slide_qus_title_translation_wiz_form_view').id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': title_translation_id.id,
            }

    @api.constrains('answer_ids')
    def _check_answers_integrity(self):
        for question in self:
            if len(question.answer_ids.filtered(lambda answer: answer.is_correct)) != 1:
                return
                # raise ValidationError(_('Question "%s" must have 1 correct answer', question.question))
            if len(question.answer_ids) < 2:
                return
                # raise ValidationError(
                #     _('Question "%s" must have 1 correct answer and at least 1 incorrect answer', question.question))

    @api.depends('custom_question_type', 'validation_email')
    def _compute_save_as_email(self):
        for question in self:
            if question.custom_question_type != 'char_box' or not question.validation_email:
                question.save_as_email = False

    @api.depends('custom_question_type')
    def _compute_save_as_nickname(self):
        for question in self:
            if question.custom_question_type != 'char_box':
                question.save_as_nickname = False

    @api.depends('is_page')
    def _compute_question_type(self):
        for question in self:
            if not question.custom_question_type or question.is_page:
                question.custom_question_type = False

    @api.depends('custom_question_type', 'answer_date', 'answer_datetime', 'answer_numerical_box')
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
            if question.is_scored_question is None:
                question.is_scored_question = False
            elif question.custom_question_type == 'date':
                question.is_scored_question = bool(question.answer_date)
            elif question.custom_question_type == 'datetime':
                question.is_scored_question = bool(question.answer_datetime)
            elif question.custom_question_type == 'numerical_box' and question.answer_numerical_box:
                question.is_scored_question = True
            elif question.custom_question_type in ['simple_choice', 'multiple_choice']:
                question.is_scored_question = True
            else:
                question.is_scored_question = False


class customElearningAnswers(models.Model):
    _inherit = 'slide.answer'

    matrix_question_id = fields.Many2one('slide.question', string='Question (as matrix row)', ondelete='cascade')
    value_image = fields.Image('Image', max_width=256, max_height=256)
    answer_score = fields.Float('Score for this choice',
                                help="A positive score indicates a correct choice; a negative or null score indicates a wrong answer")

    @api.constrains('question_id', 'matrix_question_id')
    def _check_question_not_empty(self):
        """Ensure that field question_id XOR field matrix_question_id is not null"""
        for label in self:
            if not bool(label.question_id) != bool(label.matrix_question_id):
                raise ValidationError(_("A label must be attached to only one question."))

    def translate_slide_ans_title_data(self):
        translate_slide_ans_id = self.env['slide.answer.title.translation'].search(
            [('slide_qus_id', '=', self.question_id.id), ('slide_ans_id', '=', self.id)], limit=1)
        if translate_slide_ans_id:
            return {
                'name': ('Translate'),
                'view_mode': 'form',
                'res_model': 'slide.answer.title.translation',
                'views': [(self.env.ref('ecom_lms.slide_ans_title_translation_wiz_form_view').id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': translate_slide_ans_id.id,
            }

        else:
            title_translation_id = self.env['slide.answer.title.translation'].create(
                {'slide_qus_id': self.question_id.id, 'slide_ans_id': self.id})
            return {
                'name': ('Translate'),
                'view_mode': 'form',
                'res_model': 'slide.answer.title.translation',
                'views': [(self.env.ref('ecom_lms.slide_ans_title_translation_wiz_form_view').id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': title_translation_id.id,
            }

    def translate_slide_ans_comment_data(self):
        translate_slide_ans_id = self.env['slide.answer.comment.translation'].search(
            [('slide_qus_id', '=', self.question_id.id), ('slide_ans_id', '=', self.id)], limit=1)
        if translate_slide_ans_id:
            return {
                'name': ('Translate'),
                'view_mode': 'form',
                'res_model': 'slide.answer.comment.translation',
                'views': [(self.env.ref('ecom_lms.slide_ans_comment_translation_wiz_form_view').id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': translate_slide_ans_id.id,
            }

        else:
            comment_translation_id = self.env['slide.answer.comment.translation'].create(
                {'slide_qus_id': self.question_id.id, 'slide_ans_id': self.id})
            return {
                'name': ('Translate'),
                'view_mode': 'form',
                'res_model': 'slide.answer.comment.translation',
                'views': [(self.env.ref('ecom_lms.slide_ans_comment_translation_wiz_form_view').id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': comment_translation_id.id,
            }








