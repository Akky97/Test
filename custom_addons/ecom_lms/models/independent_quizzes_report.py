import uuid

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class IndependentQuizReport(models.Model):
    _name = 'quiz.report'
    _description = 'Quiz Report'
    _rec_name = 'quiz_id'


    quiz_id = fields.Many2one('quizzes.question', index=True, required=True, ondelete='cascade')
    start_datetime = fields.Datetime('Start date and time', readonly=True)
    deadline = fields.Datetime('Deadline', help="Datetime until customer can open the Lesson Quiz and submit answers")
    independent_quiz_time_limit_reached = fields.Boolean("Lesson Time Limit Reached",
                                               compute='_compute_lesson_time_limit_reached')
    access_token = fields.Char('Identification token', default=lambda self: str(uuid.uuid4()), readonly=True,
                               required=True, copy=False)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    user_id = fields.Many2one('res.users', string='User', readonly=True)
    completed = fields.Boolean('Done', default=False)
    attempts_num = fields.Integer("Attempt no")



    attendee_ids = fields.Many2many('res.partner', required=True, ondelete='cascade')
    partner_email = fields.Char("Responsible Person's Email" ,readonly=True)
    custom_question_id = fields.Many2one('quizzes.question', string="Quizzes")
    responsible_person_id = fields.Many2one('res.users', string='Responsible',default=lambda self: self.env.user)
    no_of_attempts = fields.Integer('Number of Attemps' , related='quiz_id.no_of_attempts')
    description_short = fields.Char('Quiz Description')
    quiz_line = fields.One2many('quiz.report.line','quiz_report_id',string='Quiz Report Line')
    quiz_completed = fields.Boolean('Quiz Completed')

class CustomAnswerLine(models.Model):
    _name = 'answer.line'

    options = fields.Char('Options')
    slide_ans_id = fields.Many2one('slide.answer','Options')
    quiz_report_line_id = fields.Many2one('quiz.report.line','Quiz Line')



class IndependentQuizReportLine(models.Model):
    _name = 'quiz.report.line'

    quiz_report_id = fields.Many2one('quiz.report',string='Quiz Report')
    quiz_id = fields.Many2one('quizzes.question',)
    quiz_question_id = fields.Many2one('slide.question',domain="[('custom_question_id', '=', quiz_id)]")
    selected_answer = fields.Char('Selected Answer')
    correct_answer = fields.Char('Correct Answer')
    answer_score = fields.Float('Score for this choice')
    option_ids = fields.One2many('answer.line',"quiz_report_line_id",string='Options')
    
    