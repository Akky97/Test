# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re
import werkzeug

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

emails_split = re.compile(r"[;,\n\r]+")


class LessonInvite(models.TransientModel):
    _name = 'lesson.invite'
    _description = 'Lesson Invitation Wizard'
    
    @api.model
    def _get_default_from(self):
        if self.env.user.email:
            return tools.formataddr((self.env.user.name, self.env.user.email))
        raise UserError(_("Unable to post message, please configure the sender's email address."))
    
    subject = fields.Char('Subject', compute='_compute_subject', store=True)
    body = fields.Html('Contents', sanitize_style=True,readonly=False, compute='_compute_body', store=True)
    template_id = fields.Many2one(
        'mail.template', 'Use template', index=True)
    # origin
    email_from = fields.Char('From', default=_get_default_from, help="Email address of the sender.")
    lesson_id = fields.Many2one('slide.slide', string='Lesson', required=True)
    lesson_start_url = fields.Char('Lesson URL', compute='_compute_lesson_start_url')
    user_ids = fields.Many2many(
        'res.users', 'lesson_invite_user_ids', 'lesson_invite_id', 'user_id', string='Recipients')
    
    
    def action_invite(self):
        self.ensure_one()
        lst=''
        for user in self.user_ids:
            lst += str(user.partner_id.email) + ','
        outgoing_server_name = self.env['ir.mail_server'].sudo().search([],limit=1).smtp_user
        if outgoing_server_name and self.template_id:
            self.template_id.email_to = lst
            self.template_id.send_mail(self.lesson_id.id, force_send=True)

        return {'type': 'ir.actions.act_window_close'}
    
    
    @api.depends('template_id')
    def _compute_subject(self):
        for invite in self:
            if invite.template_id:
                invite.subject = invite.template_id.subject
            elif not invite.subject:
                invite.subject = False
                
                
    @api.depends('template_id')
    def _compute_body(self):
        for invite in self:
            if invite.template_id:
                invite.body = invite.template_id.body_html
            elif not invite.body:
                invite.body = False
                
                
    @api.depends('lesson_id')
    def _compute_lesson_start_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for invite in self:
            lesson_url= '/slides/slide/%s?fullscreen=1'% invite.lesson_id.id
            # lesson_url= '/slides/slide/%s'% invite.lesson_id.id
            invite.lesson_start_url = werkzeug.urls.url_join(base_url, lesson_url) if invite.lesson_id else False
            
            
            
