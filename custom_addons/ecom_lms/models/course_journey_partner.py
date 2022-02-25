from odoo import api, fields, models, tools, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import AccessError
from odoo.osv import expression
from datetime import datetime, date


class CourseJourneyPartner(models.Model):
    _name = 'course.journey.partner'
    _description = 'Journey Partners (Members)'

    journey_id = fields.Many2one('course.journey', index=True, required=True, ondelete='cascade')
    # completed = fields.Boolean('Is Completed', help='Channel validated, even if slides / lessons are added once done.')
    completion = fields.Integer('% Completed Slides')
    journey_completion = fields.Integer('% Completed Journey', compute='_compute_jounrey_completed')
    journey_completed_mail = fields.Boolean('Completed Journey Mail')
    journey_completed = fields.Boolean('Completed Journey', compute='_compute_jounrey_completed_val')
    journey_complete_date = fields.Datetime('Date', readonly=True)
    # completed_slides_count = fields.Integer('# Completed Slides')
    partner_id = fields.Many2one('res.partner', index=True, required=True, ondelete='cascade')
    partner_email = fields.Char(related='partner_id.email', readonly=True)
    journey_liked = fields.Boolean('Liked', default=False, store=True)
    journey_disliked = fields.Boolean('DisLiked', default=False, store=True)
    journey_not_liked_disliked = fields.Boolean('Blank', default=False, )
    journey_joined = fields.Boolean('Joined', default=False, store=True)


    @api.model
    def create(self, values):
        res = super(CourseJourneyPartner, self).create(values)
        template_id = self.env.ref('ecom_lms.email_template_joined_joureny')

        outgoing_server_name = self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
        if outgoing_server_name and template_id:
            template_id.email_from = self.env.user.partner_id.email
            template_id.send_mail(res.id, force_send=True)
        if res.journey_id:
            if res.journey_id.courses_ids:
                for course_line in res.journey_id.courses_ids:
                    cr = self.env.cr
                    cr.execute('SELECT id FROM slide_channel_partner where partner_id = %s and channel_id = %s',
                               (res.partner_id.id, course_line.course_id.id,))
                    course_attendees = cr.fetchall()
                    # course_attendees = self.env['slide.channel.partner'].search([('partner_id','=',res.partner_id.id),('channel_id','=',course_line.course_id.id)])
                    if not course_attendees:
                        user_id= self.env['res.users'].sudo().search([('partner_id','=',res.partner_id.id)],limit=1)
                        channel_partner = self.env['slide.channel.partner'].create({'partner_id': res.partner_id.id,
                                                                                    'custom_user_id':user_id.id,
                                                                                    'channel_id': course_line.course_id.id, })

        if not res.journey_liked and not res.journey_disliked:
            res.journey_not_liked_disliked = True
        res.journey_joined = True
        return res

    @api.depends('journey_id.courses_ids')
    def _compute_jounrey_completed(self):
        for val in self:
            if val.journey_id:
                sum = 0.0
                journey_comp = 0
                no_of_courses = 0.0
                val.journey_completion = 0.0
                if val.journey_id.courses_ids:
                    for course in val.journey_id.courses_ids:
                        no_of_courses = no_of_courses + 1
                        if course.sudo().course_id.sudo().channel_partner_ids:
                            for course_partner in course.sudo().course_id.channel_partner_ids:
                                if course_partner.partner_id == val.partner_id:
                                    sum = sum + course_partner.completion

                    journey_comp = sum / no_of_courses
                    if journey_comp == 100:
                        val.journey_completed_mail = True
                        if not val.journey_complete_date:
                            val.journey_complete_date = datetime.now()
                    else:
                        val.journey_completed_mail = False
                        val.journey_complete_date = ''
                val.journey_completion = journey_comp

    @api.depends('journey_completed_mail')
    def _compute_jounrey_completed_val(self):
        for val in self:
            val.journey_completed = False
            if val.journey_completed_mail and val.journey_complete_date and val.journey_completion == 100:
                complet_date = val.journey_complete_date.replace(second=0, microsecond=0)
                current_date = datetime.now()
                current_date_new = current_date.replace(second=0, microsecond=0)
                if current_date_new == complet_date:
                    template_id = self.env.ref('ecom_lms.email_template_journey_completed')
                    outgoing_server_name = self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
                    if outgoing_server_name and template_id:
                        template_id.email_from = outgoing_server_name
                        a = template_id.send_mail(val.id, force_send=True)
                        val.journey_completed = True
                else:
                    val.journey_completed = False

    def unlink(self):
        for val in self:
            if val.journey_id and val.journey_id.courses_ids:
                all_closed=1
                for course in val.journey_id.courses_ids:
                    if course.course_id.sudo().channel_partner_ids:
                        for course_partner in course.course_id.sudo().channel_partner_ids:
                            if course_partner.partner_id == val.partner_id:
                                course_partner.unlink()
                                
                                
                #     if course.course_id.course_close_date:
                #         date_now = datetime.now()
                #         if date_now.date() > course.course_id.course_close_date.date():
                #             all_closed=all_closed+1
                #
                # if all_closed>1:
                #     val.unlink()
                #


        return super(CourseJourneyPartner, self).unlink()

    # def unlink(self):
    #     """
    #     Override unlink method :
    #     Remove attendee from a channel, then also remove slide.slide.partner related to.
    #     """
    #     removed_slide_partner_domain = []
    #     for channel_partner in self:
    #         # find all slide link to the channel and the partner
    #         removed_slide_partner_domain = expression.OR([
    #             removed_slide_partner_domain,
    #             [('partner_id', '=', channel_partner.partner_id.id),
    #              ('slide_id', 'in', channel_partner.channel_id.slide_ids.ids)]
    #         ])
    #     if removed_slide_partner_domain:
    #         self.env['slide.slide.partner'].search(removed_slide_partner_domain).unlink()
    #     return super(CourseJourneyPartner, self).unlink()