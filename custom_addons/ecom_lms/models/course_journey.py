from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import uuid
from datetime import datetime, date


class CourseJourney(models.Model):
    _name = 'course.journey'
    _rec_name = 'description_short'
    

    def _default_access_token(self):
        return uuid.uuid4().hex

    name = fields.Char('Journey', default='/', readonly=True, copy=False)
    description_short = fields.Char(string="Journey Description")
    journey_image = fields.Image(string="Image")

    courses_ids = fields.One2many('course.journey.line', 'journey_id', string='Courses')

    partner_ids = fields.Many2many(
        'res.partner', 'course_journey_partner', 'journey_id', 'partner_id',
        string='Members', help="All members of the channel.", copy=False, depends=['journey_channel_partner_ids'])

    journey_channel_partner_ids = fields.One2many('course.journey.partner', 'journey_id', string='Members Information',
                                                  depends=['partner_ids'])
    members_count = fields.Integer('Attendees count', compute='_compute_jounrey_members_count')
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.uid)
    channel_access_token = fields.Char('Invitation Token', default=_default_access_token)

    course_name_ids = fields.Many2many('slide.channel', string='Courses', compute="_compute_course_names")

    journey_completion = fields.Integer('% Completed Journey', compute='_compute_jounrey_completion')
    journey_completed_mail = fields.Boolean('Completed Journey Mail', compute='_compute_jounrey_completion')
    course_count = fields.Integer('Course count', compute='_compute_journey_course_count')
    
    course_closed_bool = fields.Boolean('Course Closed', compute='_compute_course_closed_bool')
    likes = fields.Integer('Likes')
    dislikes = fields.Integer('Dislikes')
    
    
    @api.depends('courses_ids')
    def _compute_course_closed_bool(self):
        for val in self:
            all_closed=1
            val.course_closed_bool=False
            if val.courses_ids:
                for course in val.courses_ids:
                    if course.course_id.course_close_date:
                        date_now = datetime.now()
                        if date_now.date() > course.course_id.course_close_date.date():
                            all_closed=all_closed+1
                if all_closed>1:
                    if val.journey_channel_partner_ids:
                        for journey_partner in val.journey_channel_partner_ids:
                            journey_partner.unlink()
                            
                    val.course_closed_bool=True


    @api.depends('courses_ids')
    def _compute_journey_course_count(self):
        for val in self:
            count = 0
            if val.courses_ids:
                for course in val.courses_ids:
                    count = count + 1
            val.course_count = count

    def _compute_jounrey_completion(self):
        for val in self:
            val.journey_completion = 0
            val.journey_completed_mail = False
            if val.journey_channel_partner_ids:
                val.journey_completion = 0
                val.journey_completed_mail = False
                for journey_partner in val.journey_channel_partner_ids:
                    if journey_partner.partner_id == self.env.user.partner_id:
                        val.journey_completion = journey_partner.journey_completion
                        val.journey_completed_mail = journey_partner.journey_completed_mail
            else:
                val.journey_completion = 0
                val.journey_completed_mail = False

    def _compute_course_names(self):
        for val in self:
            course_lst = []
            if val.courses_ids:
                for course in val.courses_ids:
                    course_lst.append(course.course_id.id)
                val.course_name_ids = [(6, 0, course_lst)]
            else:
                val.course_name_ids = False

    @api.depends('journey_channel_partner_ids.journey_id')
    def _compute_jounrey_members_count(self):
        read_group_res = self.env['course.journey.partner'].sudo().read_group([('journey_id', 'in', self.ids)],
                                                                              ['journey_id'], 'journey_id')
        data = dict((res['journey_id'][0], res['journey_id_count']) for res in read_group_res)
        for journey in self:
            journey.members_count = data.get(journey.id, 0)

    def action_redirect_to_journey_members(self, state=None):
        action = self.env["ir.actions.actions"]._for_xml_id("ecom_lms.course_journey_partner_action")
        action['domain'] = [('journey_id', 'in', self.ids)]
        if len(self) == 1:
            action['display_name'] = _('Attendees of %s', self.name)
            action['context'] = {'active_test': False, 'default_journey_id': self.id}
        # if state:
        #     action['domain'] += [('completed', '=', state == 'completed')]
        return action

    @api.model
    def create(self, values):
        res = super(CourseJourney, self).create(values)
        # seq_obj = self.env['ir.sequence'].sudo().search([('code', '=', 'course.journey.seq')])
        if values.get('name', '/') == '/':
            res['name'] = self.env['ir.sequence'].sudo().next_by_code('course.journey.seq') or '/'
        template_id = self.env.ref('ecom_lms.email_template_new_joureny')

        outgoing_server_name = self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
        user_mail_lst = ''
        users_ids = self.env['res.users'].search([])
        for user in users_ids:
            user_mail_lst += str(user.partner_id.email) + ','

        if outgoing_server_name and template_id and len(user_mail_lst) > 0:
            template_id.email_from = outgoing_server_name
            template_id.email_to = user_mail_lst
            template_id.send_mail(res.id, force_send=True)

        return res


class CourseJourneyLine(models.Model):
    _name = 'course.journey.line'

    course_id = fields.Many2one('slide.channel', string='Course')
    journey_id = fields.Many2one('course.journey', string='Jouney')

