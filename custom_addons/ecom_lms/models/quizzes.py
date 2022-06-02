from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class CustomQuizzes(models.Model):
    _name = 'quizzes.question'
    _inherit = [
        'mail.thread',
        'image.mixin',
        'website.seo.metadata', 'website.published.mixin']

    active = fields.Boolean('Active', default= True)
    sequence = fields.Integer("Sequence")
    name = fields.Char('Quiz Name', required=True, translate=True)
    custom_quiz_ids = fields.One2many("slide.question", "custom_question_id", string="Questions")
    # tag_ids = fields.Many2many('slide.tag', 'rel_slide_tag', 'slide_id', 'tag_id', string='Tags')

    is_resume = fields.Boolean(
        'Allow Resume', default=False,
        help="To allow users to leave the Lesson incomplete and then resume it from where they left off.")
    is_skipping = fields.Boolean(
        'Allow Skipping', default=False,
        help="To allow users to skip questions in the Lesson.")
    is_jumping = fields.Boolean(
        'Allow Jumping', default=False,
        help="To allow users to jump between questions using a menu in the Lesson.")
    is_backward_navigation = fields.Boolean(
        'Navigate Back', default=False,
        help="To allow user to go back and revisit their answers.")
    is_repeat_until_correct = fields.Boolean(
        'Repeat Until Correct', default=False,
        help="Require the user to re-try the question until they answer it correctly.")
    is_mark_doubtful = fields.Boolean(
        'Mark Doubtful', default=False,
        help="To allow user to mention if they are not sure about the answer.")
    is_passed_status = fields.Boolean(
        'Passed Status', default=False,
        help="Show the status, if the user has previously passed.")
    random_question = fields.Selection([
        ('serial', 'Serialized Questions'), ('random', 'Randomized Questions')],
        default='serial', string='Question Order', required=True,
        help='Choose whether questions to display in lessons are serialized or randomized.')
    feedback_time = fields.Selection([
        ('end_lesson', 'At the end of Lesson'), ('each_question', 'After Each Questions'), ('not_show', 'Do Not Show')],
        default='end_lesson', string='Feedback', required=True,
        help='Choose whether questions to display in lessons are serialized or randomized.')
    result_stored = fields.Selection([
        ('the_best', 'The best'), ('the_newest', 'The newest'), ('all', 'All')],
        default='the_best', string='Result Stored', required=True,
        help='Option should be available for storing the result of users.')
    display_solution = fields.Boolean(
        'Display Solution', default=False,
        help="Display the user's and correct answers for all questions along with the score for each question.")
    multiple_take = fields.Boolean(
        'Multiple Take', default=False,
        help="Number of times a user is allowed to take the lesson.")
    num_of_takes = fields.Char("Takes Allowed", required=True, default=0, translate=True)
    quiz_image = fields.Image('Quiz Image')
    description_short = fields.Char('Description')
    quiz_attendee = fields.One2many('quiz.partner',"quiz_id", string='Attendee')
    quiz_attendee_name = fields.Many2many('res.partner', string='Attendee',compute="_compute_attendee_names")
    no_of_attempts = fields.Integer('Number of Attemps' , default=0)
    responsible_person_id = fields.Many2one('res.users', string='Responsible',default=lambda self: self.env.user)
    # quiz_report_id = fields.Many2one('quiz.report')

    def _compute_attendee_names(self):
        for val in self:
            quiz_attendee_lst = []
            if val.quiz_attendee:
                for quiz_att in val.quiz_attendee:
                    quiz_attendee_lst.append(quiz_att.partner_id.id)
                val.quiz_attendee_name = [(6, 0, quiz_attendee_lst)]
            else:
                val.quiz_attendee_name = False


    @api.model
    def create(self, values):
        res = super(CustomQuizzes, self).create(values)
        quiz_name = values.get('name')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        internal_users = self.env['res.users'].search([])
        template_id = self.env.ref('ecom_lms.independent_quiz_email_template')
        outgoing_server_name = self.env['ir.mail_server'].sudo().search([],limit=1).smtp_user
        if outgoing_server_name and template_id:
            for user in internal_users:
                template_id.email_from = outgoing_server_name
                template_id.email_to = user.partner_id.email
                template_id.subject = 'New quizzes independent of courses are enabled'
                template_id.body_html = """ <html>
                                       <head></head>
                                       <body>
                                       <p>Dear """ + user.name + """</p>
                                        <p>
                                       The New Quiz <strong>"""+ quiz_name +"""</strong> is enabled in the LMS System. Please click on the sharable link and Start.
                                        </p>
                                        <p>
                                         <a href=""" + str(base_url+"/recommend-quiz?ref="+(str(res.id))) + """
                style="padding: 5px 10px; color: #FFFFFF; text-decoration: none; background-color: #875A7B; border: 1px solid #875A7B; border-radius: 3px">
                Click Here</a></p>"""
                mail_sent = template_id.send_mail(user.id, force_send=True)
        return res

    # @api.model
    # def write(self, values):
    #     print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%',self,values)
    #     res = super(CustomQuizzes, self).write(values)
    #     if values.get('no_of_attempts'):
    #         quiz_report_update = self.env['quiz.report'].sudo().write(
    #                     {'quiz_id': self.id,
    #                      'no_of_attempts': values.get('no_of_attempts')})
    #         print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', quiz_report_update)
    #     return res


    def action_redirect_to_quiz_members(self, state=None):
        action = self.env["ir.actions.actions"]._for_xml_id("ecom_lms.independent_partner_action")
        action['domain'] = [('quiz_id', 'in', self.ids)]
        if len(self) == 1:
            action['display_name'] = _('Attendees of %s', self.name)
            action['context'] = {'active_test': False, 'default_quiz_id': self.id}
        # if state:
        #     action['domain'] += [('completed', '=', state == 'completed')]
        return action



class CustomSlideQuestionsModel(models.Model):
    _inherit = 'slide.question'

    active = fields.Boolean('Active', default=True)
    custom_question_id = fields.Many2one('quizzes.question', string="Quizzes")
    slide_id = fields.Many2one('slide.slide', string="Content", required=False)


class CustomSlideAnswerModel(models.Model):
    _inherit = "slide.answer"




class QuizPartner(models.Model):
    _name = 'quiz.partner'
    _description = 'Quiz(Members)'
    rec_name = 'partner_id'



    quiz_id = fields.Many2one('quizzes.question', index=True, required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', index=True, required=True, ondelete='cascade')
    partner_email = fields.Char(related='partner_id.email', readonly=True)
    # quiz_report_id = fields.Many2one('quiz.report', index=True, required=True, ondelete='cascade')


    # @api.model
    # def create(self, values):
    #     print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    #     res = super(QuizPartner, self).create(values)
    #     print('sssssssssssssssssssssssssssssssssssssssss',values)
    #     if values.get('partner_id') or values.get('quiz_id'):
    #         quiz_attendee_lst = []
    #         for rec in self:
    #             if rec.quiz_id.quiz_attendee:
    #                 for quiz_att in rec.quiz_attendee:
    #                     quiz_attendee_lst.append(quiz_att.partner_id.id)
    #         quiz_report_update = self.env['quiz.report'].sudo().write(
    #             {'quiz_id': int(values.get('quiz_id')),
    #              'quiz_attendee_name': [6,0,quiz_attendee_lst]})
    #         print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', quiz_report_update)
    #     return res




    # @api.onchange('quiz_id','partner_id')
    # def _onchange_attendee_name(self):
    #     print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
    #     for rec in self:
    #         print('****************************************')
    #         quiz_report_id.attendee_ids = rec.quiz_attendee_name