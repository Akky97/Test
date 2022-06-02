# -*- coding: utf-8 -*-
import codecs
import zipfile

from odoo import api, fields, models, tools, _
from odoo.exceptions import AccessError, UserError,ValidationError
from datetime import datetime, date

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from lxml import etree
import io
import xlrd
import xlwt
from io import BytesIO
import base64
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from xlsxwriter.workbook import Workbook
from io import StringIO
import uuid
import logging


_logger = logging.getLogger(__name__)

class CustomElearningInherit(models.Model):
    _inherit = 'slide.channel'

    def _default_access_token(self):
        return uuid.uuid4().hex

    custom_html_description = fields.Html(
        'Description', translate=True,
        help="The description that is displayed on top of the course page")
    custom_tag_ids = fields.Many2many(
        'slide.channel.tag', 'slide_channel_tag_rel', 'channel_id', 'tag_id',
        string='Course Keywords', help='Used to categorize and filter displayed channels/courses')
    custom_visibility = fields.Selection([
        ('public', 'Public'), ('private', 'Private'), ('semi_public', 'Semi-Public')],
        default='public', string='Choose', required=True,
        help='Applied directly as ACLs. Allow to hide channels and their content for non members.',track_visibility='onchange')
    course_duration = fields.Float('Course Duration', digits=(10, 4),
                                   help="The estimated completion time for the Course",track_visibility='onchange')
    required_course = fields.Many2many('slide.channel', 'channel_id', 'partner_id', 'tag_id', string='Required Course',track_visibility='onchange')
    course_category_id = fields.Many2one('course.category', string='Category',track_visibility='onchange')
    revision_message = fields.Char(string='Course Revision', tracking=True)
    is_revision = fields.Boolean(
        'Allow Revision', default=False,
        help=" To check status of course based on the message added for revision.",track_visibility='onchange')
    
    
    channel_type = fields.Selection([
        ('training', 'Training'), ('documentation', 'Documentation')],
        string="Course type", default="training", required=True,track_visibility='onchange')
    # pass_fail = fields.Selection([
    #     ('all_pass', 'Disable'), ('pass', 'Enable')],
    #     default='all_pass', required=True,
    #     help='Option of pass/fail to add passing percentage.')
    # custom_pass_percent = fields.Char("Required Passing(%)", required=True, default=0, translate=True)
    availability_option = fields.Boolean(string='Course Availability', default=True)
    course_open_date = fields.Datetime(string='Open Date',track_visibility='onchange')
    course_close_date = fields.Datetime(string='Close Date',track_visibility='onchange')
    nominated_user_ids = fields.Many2many('res.users', 'channel_user_rel', 'channel_id', 'user_id',
                                          string='Nominated Users')

    lang_values = fields.Selection([
        ('english', 'English'), ('hindi', 'Hindi'), ('gujarati', 'Gujarati'), ('marathi', 'Marathi'),
        ('assamese', 'Assamese'), ('tamil', 'Tamil')
        , ('kannada', 'Kannada'), ('malyalam', 'Malyalam'), ('telugu', 'Telugu')],
        string='Language',track_visibility='onchange')
    
    allow_comment = fields.Boolean(
        "Allow rating on Course", default=True,
        help="If checked it allows members to either:\n"
             " * like content and post comments on documentation course;\n"
             " * post comment and review on training course;",track_visibility='onchange')

    lang_id = fields.Many2one('res.lang', string='Language')

    # member_live_count
    members_count_live = fields.Integer('Live Attendance')
    is_featured = fields.Boolean('Featured',track_visibility='onchange')
    featured_group_id = fields.Many2one('res.groups', 'Featured Groups',track_visibility='onchange')

    channel_access_token = fields.Char('Invitation Token', default=_default_access_token)
    journey_name_ids = fields.Many2many('course.journey', string='Journey', compute="_compute_journey_names")
    load_nominated_user = fields.Binary('Upload Nominated Sheet')
    user_ids = fields.Many2many('res.users', string='User', default=lambda self: self.env['res.users'].search([]))
    recommend_users_ids = fields.One2many('recommend.users', 'recommend_courses_id', string='Recommend Users')
    likes = fields.Integer('Likes')
    dislikes = fields.Integer('Dislikes')
    course_successfully_created= fields.Boolean('Course Successfully Created',default=False)
    
    has_certificate = fields.Boolean('Has Certificate',default=False,copy=False,compute="_compute_has_certificate")
    has_quiz = fields.Boolean('Has Quiz',default=False,copy=False,compute="_compute_has_quiz")


    @api.depends('slide_ids')
    def newpublish_url(self):
        for rec in self:
            slide_slide = self.env['slide.slide'].sudo().search([('id', 'in', rec.slide_ids.ids),('live_session', '=', 'yes')])
            if slide_slide:
                opendate = slide_slide.lesson_open_date
                closedate = slide_slide.lesson_close_date
                now = datetime.now()
                time_delt1 = timedelta(hours=5, minutes=30)
                nowtime = (now + time_delt1).strftime('%Y-%m-%d')
                nowopen = (opendate + time_delt1).strftime('%Y-%m-%d')
                nowopen1 = (opendate + time_delt1).strftime('%Y-%m-%d %H:%M:%S')
                nowclose1 = (closedate + time_delt1).strftime('%Y-%m-%d %H:%M:%S')
                d1 = datetime.strptime(nowclose1, "%Y-%m-%d %H:%M:%S")
                d2 = datetime.strptime(nowopen1, "%Y-%m-%d %H:%M:%S")
                print((d1-d2).days * 24 * 60 / 60)
                if nowopen == nowtime:
                    slide_slide.is_published = True
                    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    lesson_url = '/slides/slide/%s' % slide_slide.id
                    finalurl = base_url + lesson_url
                    existing = self.env['slide.channel.partner'].sudo().search([('channel_id', 'in', self.ids)])
                    self.env['calendar.event'].sudo().create({'name': slide_slide.name, 'start': opendate,'partner_ids':existing.partner_id})
                    for alluser in existing:
                        if alluser.partner_email != False:
                            outgoing_server_name = self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
                            template_id = self.env.ref('ecom_lms.email_template_course_live_session')
                            if template_id and outgoing_server_name:
                                template_id.email_from = outgoing_server_name
                                template_id.email_to = alluser.partner_email
                                template_id.subject = "Live Session of Course"
                                template_id.body_html = """<html>
                                                            <head></head>
                                                            <body>
                                                            <p>Dear User</p>
                                                            <p>Please click on the Start Button for Live Session.</p>
                                                            <p><a href=""" + str(finalurl) + """ style="padding: 5px 10px; color: #FFFFFF; text-decoration: none; background-color: #875A7B; border: 1px solid #875A7B; border-radius: 3px">Start Button</a></p>
                                                            <p>Thankyou</p>"""
                                template_id.send_mail(alluser.id, force_send=True)


    @api.depends('slide_ids')
    def _compute_has_quiz(self):
        for rec in self:
            slide_slide = self.env['slide.slide'].sudo().search([('id','in',rec.slide_ids.ids),('slide_type','=','quiz')])
            if slide_slide:
                rec.has_quiz = True
            else:
                rec.has_quiz = False

    @api.depends('slide_ids')
    def _compute_has_certificate(self):
        for rec in self:
            slide_slide = self.env['slide.slide'].sudo().search([('id','in',rec.slide_ids.ids),('slide_type','=','certification'),('survey_id','!=',False)])
            if slide_slide:
                rec.has_certificate = True
            else:
                rec.has_certificate = False


    def action_zip_download(self):
        content, content_type = self.env.ref('ecom_lms.action_report_course_content')._render(self.id)
        attachment_id = self.env['ir.attachment'].create({
            'name': '%s' % (self.name) + '_content.pdf',
            'type': 'binary',
            'datas': base64.encodebytes(content),
            'res_model': 'slide.channel',
            'res_id': self.id
        })

        import os, zipfile
        # function to convert binary data
        def isBase64_decodestring(s):
            try:
                return base64.decodebytes(s)
            except Exception as e:
                raise ValidationError('Error:', +str(e))

        # getting working module where your current python file (model.py) exists
        from odoo.modules.module import get_module_resource
        path = get_module_resource('ecom_lms', 'static/src/zip_folder')

        # creating dynamic path to create zip file
        if self.slide_ids:
            list_files = []
            file_name_zip = self.name + "_zip.rar"
            zipfilepath = os.path.join(path, file_name_zip)
            for idx, rec in enumerate(self.slide_ids):
                if rec.slide_type == 'video' and rec.slide_attachment:
                    file_name = str(rec.slide_attachment.name.strip().replace(' ', '_').replace('-', '_'))
                    # creating file name (like example.txt) in which we have to write binary field data or attachment
                    object_name = file_name
                    object_handle = open(object_name, "wb")
                    # writing binary data into file handle
                    object_handle.write(isBase64_decodestring(rec.slide_attachment.datas))
                    object_handle.close()
                    list_files.append(object_name)

                if rec.slide_type == 'infographic' and rec.image_1920:
                    file_name = str(rec.name.strip().replace(' ', '_').replace('-', '_'))
                    # creating file name (like example.txt) in which we have to write binary field data or attachment
                    object_name = file_name
                    object_handle = open(object_name, "wb")
                    # writing binary data into file handle
                    object_handle.write(isBase64_decodestring(rec.image_1920))
                    object_handle.close()
                    list_files.append(object_name)


                if rec.slide_type == 'scorm' and rec.scorm_data:
                    file_name = str(rec.scorm_data.name.strip().replace(' ', '_').replace('-', '_'))
                    # creating file name (like example.txt) in which we have to write binary field data or attachment
                    object_name = file_name
                    object_handle = open(object_name, "wb")
                    # writing binary data into file handle
                    object_handle.write(isBase64_decodestring(rec.scorm_data.datas))
                    object_handle.close()
                    list_files.append(object_name)

                if rec.slide_type == 'document' or rec.slide_type == 'presentation':
                    if rec.datas and rec.file_name:
                        file_name = str(rec.file_name.strip().replace(' ', '_').replace('-', '_'))
                        # creating file name (like example.txt) in which we have to write binary field data or attachment
                        object_name = file_name
                        object_handle = open(object_name, "wb")
                        # writing binary data into file handle
                        object_handle.write(isBase64_decodestring(rec.datas))
                        object_handle.close()
                        list_files.append(object_name)
            if attachment_id:
                file_name = str(attachment_id.name.strip().replace(' ', '_').replace('-', '_'))
                # creating file name (like example.txt) in which we have to write binary field data or attachment
                object_name = file_name
                object_handle = open(object_name, "wb")
                # writing binary data into file handle
                object_handle.write(isBase64_decodestring(attachment_id.datas))
                object_handle.close()
                list_files.append(object_name)
            # creating zip file in above mentioned path
            with zipfile.ZipFile(zipfilepath, "w") as zipF:
                for file in list_files:
                    zipF.write(file, compress_type=zipfile.ZIP_DEFLATED)

            # code snipet for downloading zip file
            return {
            'type': 'ir.actions.act_url',
            'url': str('/ecom_lms/static/src/zip_folder/' + str(file_name_zip)),
            'target': 'new'}

    def zip_test_button_method(self):
        pass
    
    def unlink(self):
        if self.env.user.has_group('ecom_lms.super_admin_group'):
            return super(CustomElearningInherit, self).unlink()
        else:
            raise ValidationError('You do not have access to delete.')
    
    
    @api.constrains('availability_option','course_open_date','course_close_date')
    def _constrains_course_open_close_date(self):
        for record in self:
            if not record.availability_option or not record.course_open_date or not record.course_close_date:
                raise UserError(_('You cannot create Course without  Course Availability and Open/Close Date'))
            current_date =datetime.now()
            # if record.course_open_date < datetime.now():
            #     raise UserError(_('Open Date Should not be less than Today date'))
            
            if record.course_close_date < datetime.now():
                raise UserError(_("Close Date should not be less than or equal to Today's Date"))
            
            if record.course_open_date >= record.course_close_date:
                raise UserError(_('Open Date should not be greater than or equal to Close date'))
                

    def _default_users(self):
        return lambda self: self.env['res.users'].search([('share', '=', False)])

    @api.onchange('lang_values')
    def onchange_lang_values(self):
        if self.lang_values:
            course_title_translations_id = self.env['course.title.translation.wiz'].search(
                [('course_id', '=', self._origin.id)], limit=1)
            _logger.info("cccccccccccccccccccc %s %s", course_title_translations_id,course_title_translations_id.course_id, self._origin.id)
            if course_title_translations_id.course_id:
                if course_title_translations_id:
                    for title_tanslate_line in course_title_translations_id.language_translation_ids:
                        if title_tanslate_line.language_id == self.lang_values:
                            self.name = title_tanslate_line.translation_val

            if self.slide_ids:
                for slide in self.slide_ids:
                    lesson_title_translations_id = self.env['lesson.title.translation'].search(
                        [('slide_id', '=', slide._origin.id)], limit=1)
                    if lesson_title_translations_id:
                        for slide_title_tanslate_line in lesson_title_translations_id.lesson_lang_translation_ids:
                            if slide_title_tanslate_line.language_id == self.lang_values:
                                slide.name = slide_title_tanslate_line.translation_val

    def translate_course_title_data(self):
        translate_course_id = self.env['course.title.translation.wiz'].search([('course_id', '=', self.id)], limit=1)
        if translate_course_id:
            return {
                'name': ('Translate'),
                'view_mode': 'form',
                'res_model': 'course.title.translation.wiz',
                'views': [(self.env.ref('ecom_lms.course_title_translation_wiz_form_view').id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': translate_course_id.id,
            }

        else:
            title_translation_id = self.env['course.title.translation.wiz'].create({'course_id': self.id})
            return {
                'name': ('Translate'),
                'view_mode': 'form',
                'res_model': 'course.title.translation.wiz',
                'views': [(self.env.ref('ecom_lms.course_title_translation_wiz_form_view').id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': title_translation_id.id,
            }

    def action_nominated_user_upload(self):
        for channel in self:
            data_decode = channel.load_nominated_user
            if not data_decode:
                raise UserError(_('Please Choose The File!'))

            val = base64.decodestring(data_decode)
            fp = BytesIO()
            fp.write(val)
            wb = xlrd.open_workbook(file_contents=fp.getvalue())
            wb.sheet_names()
            sheet_name = wb.sheet_names()
            sh = wb.sheet_by_name(sheet_name[0])
            n_rows = sh.nrows
            user_lst = []
            for row in range(1, n_rows):
                if sh.row_values(row)[0] and sh.row_values(row)[1]:
                    user_id = self.env['res.users'].search([('id', '=', int(sh.row_values(row)[1]))])
                    if user_id.name != sh.row_values(row)[0]:
                        raise UserError(_("The user name and odoo ID don't match. Please retry with the correct details."))
                    if not user_id:
                        raise UserError(_('This User does not exist in odoo!'))
                    else:
                        if user_id.id not in user_lst:
                            user_lst.append(user_id.id)
            existing_nomi_users=[]                
            if self.nominated_user_ids:
                for nom in self.nominated_user_ids:
                    if nom.id not in existing_nomi_users:
                        existing_nomi_users.append(nom.id)
            final_lst=existing_nomi_users+user_lst
            final_unique_list=list(set(final_lst))
            channel.sudo().nominated_user_ids = [(6, 0, final_unique_list)]

            return True

    def _compute_journey_names(self):
        for val in self:
            journey_lst = []
            cr = self.env.cr
            cr.execute('SELECT id FROM course_journey')
            jouneys = cr.fetchall()
            if jouneys:
                for row in jouneys:
                    journey_id = self.env['course.journey'].browse(row)
                    if val in journey_id.course_name_ids:
                        journey_lst.append(journey_id.id)
                val.journey_name_ids = [(6, 0, journey_lst)]
            else:
                val.journey_name_ids = False

    def action_redirect_to_members_live(self, state=None):

        action = self.env["ir.actions.actions"]._for_xml_id("ecom_lms.inherited_slide_channel_partner_action")
        action['domain'] = []

        if len(self) == 1:
            action['display_name'] = _('Attendees of %s', self.name)
            action['context'] = {'active_test': False, 'default_channel_id': self.id}
            # if state:
            action['domain'] += [('initailattendance', '=', True), ('channel_id', 'in', self.ids)]
        for record in self:
            record.members_count_live = self.env['slide.channel.partner'].search_count(
                [('initailattendance', '=', True), ('channel_id', 'in', record.ids)])

        return action

        # print(action,"actionname")

    @api.model
    def create(self, values):
        res = super(CustomElearningInherit, self).create(values)
        current_date= datetime.now()
        if res.course_open_date.date() < current_date.date():
                raise UserError(_("Open Date should not be less than Today's date"))
        if res.channel_partner_ids:
            for channel_partner in res.channel_partner_ids:
                user_val_id= self.env['res.users'].sudo().search([('partner_id','=',channel_partner.partner_id.id)],limit=1)
                if user_val_id:
                    channel_partner.custom_user_id=user_val_id.id

        outgoing_server_name = self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
        template_id = self.env.ref('ecom_lms.email_template_featured_course')
        user_mail_lst = ''
        topic_of_intererst_user_lst = ''
        if res.is_featured and res.featured_group_id:
            users_ids = self.env['res.users'].search([])
            for user in users_ids:
                if res.featured_group_id in user.groups_id:
                    user_mail_lst += str(user.partner_id.email) + ','
        if template_id and outgoing_server_name and len(user_mail_lst) > 0:
            template_id.email_to = user_mail_lst
            template_id.send_mail(res.id, force_send=True)
        if res.course_category_id:
            category_template_id = self.env.ref('ecom_lms.email_template_topic_of_interest')
            users_ids = self.env['res.users'].search([])
            for user in users_ids:
                for user in users_ids:
                    if res.course_category_id in user.topic_of_interest_ids:
                        topic_of_intererst_user_lst += str(user.partner_id.email) + ','
            if category_template_id and outgoing_server_name and len(topic_of_intererst_user_lst) > 0:
                category_template_id.email_to = topic_of_intererst_user_lst
                category_template_id.send_mail(res.id, force_send=True)

                
        translation_wiz= self.env['course.title.translation.wiz'].create({'course_id':res.id})
        translation_line=self.env['language.translation.line'].create({'language_id':res.lang_values,'translation_val':res.name,'course_transaltion_wiz_id':translation_wiz.id})
        res.course_successfully_created=True
        # if res.slide_ids:
        #     raise UserError(_("1st Save the course"))
        return res

    def write(self, values):
        user_mail_lst = ''
        topic_of_intererst_user_lst = ''
        outgoing_server_name = self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
        template_id = self.env.ref('ecom_lms.email_template_featured_course')
        current_date= datetime.now()
        old_required_course_lst= []
        old_nominated_user_lst= []
        old_content_email_id = self.publish_template_id
        old_share_template_id = self.share_template_id
        old_website_id = self.website_id
        
        if 'website_id' in values:
            new_website_id=''
            updated_website_id = values.get('website_id')
            website_val_id=self.env['website'].sudo().browse(updated_website_id)
            if website_val_id:
                new_website_id = website_val_id.name
                
            website_msg = 'Website :'+str(old_website_id.name)+'-->'+str(new_website_id)
            self.message_post(body=website_msg) 
        
        if 'share_template_id' in values:
            new_share_template_id=''
            share_temp_id = values.get('share_template_id')
            template_share=self.env['mail.template'].sudo().browse(share_temp_id)
            if template_share:
                new_share_template_id = template_share.name
                
            share_template_msg = 'Share Template :'+str(old_share_template_id.name)+'-->'+str(new_share_template_id)
            self.message_post(body=share_template_msg) 
        
        if 'publish_template_id' in values:
            new_content_email_id=''
            publish_temp_id = values.get('publish_template_id')
            template_publish=self.env['mail.template'].sudo().browse(publish_temp_id)
            if template_publish:
                new_content_email_id = template_publish.name
                
            content_email_msg = 'New Content Email:'+str(old_content_email_id.name)+'-->'+str(new_content_email_id)
            self.message_post(body=content_email_msg) 
        
        if self.nominated_user_ids:
            for nominated_user in self.nominated_user_ids:
                old_nominated_user_lst.append(nominated_user.name)
                
        if 'nominated_user_ids' in values:
            new_nominated_user_lst= []
            nominate_user_ids= values.get('nominated_user_ids')
            for nom_user in nominate_user_ids:
                for user_nomi in nom_user[2]:
                    new_user_nomi=self.env['res.users'].sudo().browse(user_nomi)
                    if new_user_nomi:
                        new_nominated_user_lst.append(new_user_nomi.name)
            req_nominated_user_msg = 'Nominated Users:'+str(old_nominated_user_lst)+'-->'+str(new_nominated_user_lst)
            self.message_post(body=req_nominated_user_msg) 
                
        if self.required_course:
            for res_course in self.required_course:
                old_required_course_lst.append(res_course.name)
        if 'required_course' in values:
            new_required_course_lst= []
            required_course_ids= values.get('required_course')
            for req in required_course_ids:
                for course_req in req[2]:
                    new_course_id=self.env['slide.channel'].sudo().browse(course_req)
                    if new_course_id:
                        new_required_course_lst.append(new_course_id.name)
            req_course_msg = 'Required Course:'+str(old_required_course_lst)+'-->'+str(new_required_course_lst)
            self.message_post(body=req_course_msg)       
                
                
        if 'course_open_date' in values:
            open_date= values.get('course_open_date')
            open_date = datetime.strptime(values.get('course_open_date'), '%Y-%m-%d %H:%M:%S')
            if open_date.date() < current_date.date():
                raise UserError(_("Open Date should not be less than Today's date"))
            
        if 'is_featured' in values and 'featured_group_id' in values:
            feature_group_id = values.get('featured_group_id')
            new_feature_group_id = self.env['res.groups'].browse(feature_group_id)

            users_ids = self.env['res.users'].search([])
            for user in users_ids:
                if new_feature_group_id in user.groups_id:
                    user_mail_lst += str(user.partner_id.email) + ','

            if template_id and outgoing_server_name and len(user_mail_lst) > 0:
                template_id.email_to = user_mail_lst
                template_id.send_mail(self.id, force_send=True)

        if 'course_category_id' in values:
            course_categ_id = values.get('course_category_id')
            course_categ_obj = self.env['course.category'].browse(course_categ_id)
            category_template_id = self.env.ref('ecom_lms.email_template_topic_of_interest')
            users_ids = self.env['res.users'].search([])
            for user in users_ids:
                if course_categ_obj in user.topic_of_interest_ids:
                    topic_of_intererst_user_lst += str(user.partner_id.email) + ','

            if category_template_id and outgoing_server_name and len(topic_of_intererst_user_lst) > 0:
                category_template_id.email_to = topic_of_intererst_user_lst
                category_template_id.send_mail(self.id, force_send=True)

        res = super(CustomElearningInherit, self).write(values)
        if self.slide_ids and self.lang_values:
            for slide in self.slide_ids:
                if slide.question_ids:
                    for slide_qus in slide.question_ids:
                        slide_qus_title_translations_id = self.env['slide.question.title.translation'].search(
                            [('slide_id', '=', slide.id), ('slide_qus_id', '=', slide_qus.id)], limit=1)
                        if slide_qus_title_translations_id:
                            for slide_qus_title_tanslate_line in slide_qus_title_translations_id.slide_qus_lang_translation_ids:
                                if slide_qus_title_tanslate_line.language_id == self.lang_values:
                                    slide_qus.question = slide_qus_title_tanslate_line.translation_value

                        if slide_qus.answer_ids:
                            for slide_ans in slide_qus.answer_ids:
                                slide_ans_title_translations_id = self.env['slide.answer.title.translation'].search(
                                    [('slide_ans_id', '=', slide_ans.id), ('slide_qus_id', '=', slide_qus.id)], limit=1)
                                if slide_ans_title_translations_id:
                                    for slide_ans_title_tanslate_line in slide_ans_title_translations_id.slide_ans_lang_translation_ids:
                                        if slide_ans_title_tanslate_line.language_id == self.lang_values:
                                            slide_ans.text_value = slide_ans_title_tanslate_line.translation_value

                                slide_ans_comment_translations_id = self.env['slide.answer.comment.translation'].search(
                                    [('slide_ans_id', '=', slide_ans.id), ('slide_qus_id', '=', slide_qus.id)], limit=1)
                                if slide_ans_comment_translations_id:
                                    for slide_ans_comment_tanslate_line in slide_ans_comment_translations_id.slide_ans_comment_lang_translation_ids:
                                        if slide_ans_comment_tanslate_line.language_id == self.lang_values:
                                            slide_ans.comment = slide_ans_comment_tanslate_line.translation_value
        return res

    @api.model
    def _action_add_members(self, target_partners, **member_values):
        """ Add the target_partner as a member of the channel (to its slide.channel.partner).
        This will make the content (slides) of the channel available to that partner.

        Returns the added 'slide.channel.partner's (! as sudo !)
        """
        index = 0
        course = []
        index1 = 0
        course1 = []
        index2 = 0
        course2 = []

        to_join = self._filter_add_members(target_partners, **member_values)
        if self.course_open_date and self.course_close_date:
            if self.course_open_date <= datetime.now() and self.course_close_date >= datetime.now():
                if to_join:
                    existing = self.env['slide.channel.partner'].sudo().search([
                        ('channel_id', 'in', self.ids),
                        ('partner_id', 'in', target_partners.ids)
                    ])

                    existing_map = dict((cid, list()) for cid in self.ids)
                    for item in existing:
                        existing_map[item.channel_id.id].append(item.partner_id.id)

                    to_create_values = [
                        dict(channel_id=channel.id, partner_id=partner.id, **member_values)
                        for channel in to_join
                        for partner in target_partners if partner.id not in existing_map[channel.id]
                    ]
                    if to_create_values:
                        channel_idnew = to_create_values[0]['channel_id']
                        currentcourse = self.env['slide.channel'].sudo().search([('id', '=', channel_idnew)])
                        req_course = currentcourse

                        if req_course:
                            for i in req_course:
                                newi = i.required_course
                                for j in newi:
                                    index1 += 1
                                    course1.append(j.name)
                                    final = j.id
                                    requiredcourse = self.env['slide.channel.partner'].sudo().search(
                                        [('channel_id', '=', int(final)),
                                         ('partner_id', '=', self.env.user.partner_id.id)])
                                    if requiredcourse:
                                        index2 += 1
                                        course2.append(requiredcourse)

                                    if requiredcourse:
                                        for m in requiredcourse:
                                            requirednew = m.completion

                                            if requirednew < 100:
                                                currentcourses = self.env['slide.channel'].sudo().search(
                                                    [('id', '=', m.channel_id.id)])
                                                index += 1
                                                course.append(currentcourses.name)

                            if index != 0:
                                s = ""
                                for item in course:
                                    s += item + str(',')
                                    raise UserError("Please Complete required course. '" + str(s) + "'")

                            if index1 != 0 and index2 == 0:
                                t = ""
                                for item1 in course1:
                                    t += item1 + str(',')
                                    raise UserError("Please Join the Required Courses.'" + str(t) + "'")

                    slide_partners_sudo = self.env['slide.channel.partner'].sudo().create(to_create_values)
                    user_id= self.env['res.users'].sudo().search([('partner_id','=',slide_partners_sudo.partner_id.id)],limit=1)
                    if user_id:
                        slide_partners_sudo.custom_user_id=user_id.id

                    to_join.message_subscribe(partner_ids=target_partners.ids,
                                              subtype_ids=[
                                                  self.env.ref('website_slides.mt_channel_slide_published').id])
                    return slide_partners_sudo
            else:
                raise UserError("Wait for course availability")
        return self.env['slide.channel.partner'].sudo()


class CourseLanguage(models.Model):
    _name = 'course.lang'
    _description = 'Course Language Module'

    name = fields.Selection([
        ('english', 'English'), ('hindi', 'Hindi'), ('marathi', 'Marathi'), ('telugu', 'Telugu')],
        default='public', string='Choose Language',
        help='Applied directly as ACLs. Allow to hide channels and their content for non members.')


class CourseCategory(models.Model):
    _name = 'course.category'
    _description = 'Course Category Module'

    parent_id = fields.Many2one('course.category', string='Parent Category')
    name = fields.Char(string='Title')
    description = fields.Text(string='Description')


class liveattendanceuser(models.Model):
    _inherit = 'slide.channel.partner'

    initailattendance = fields.Boolean(string="Initial Attend", store=True)
    completeattend = fields.Boolean(string="Complete Attend", store=True)
    expired_status = fields.Boolean(string='Expired', compute='_expired_status', store=True)
    custom_user_id = fields.Many2one('res.users', string='User Name')
    user_code = fields.Char(string='User Code', compute='_user_code_val')
    channel_liked = fields.Boolean('Liked', default=False, store=True)
    channel_disliked = fields.Boolean('DisLiked', default=False, store=True)
    course_joined = fields.Boolean('Joined', default=False, store=True)
    not_liked_disliked = fields.Boolean('Blank', default=False, )
    time_left = fields.Float(string="Time Left", compute='_compute_time_left')


    def unlink(self):
        if self.env.user.has_group('ecom_lms.super_admin_group'):
            return super(liveattendanceuser, self).unlink()
        else:
            raise ValidationError('You do not have access to delete.')
    
    # @api.depends('journey_id.courses_ids')
    def _compute_time_left(self):
        for val in self:
            val.time_left=0.0
            include_quiz=False
            if val.custom_user_id and val.partner_id:
                slides = self.env['slide.slide'].sudo().search([('channel_id', '=', val.channel_id.id)])
                channel_progress = dict((sid, dict()) for sid in slides.ids)
                if not val.custom_user_id._is_public() and val.channel_id.is_member:
                    slide_partners = self.env['slide.slide.partner'].sudo().search([
                        ('channel_id', '=', val.channel_id.id),
                        ('partner_id', '=', val.custom_user_id.partner_id.id),
                        ('slide_id', 'in', slides.ids)
                    ])
                    for slide_partner in slide_partners:
                        channel_progress[slide_partner.slide_id.id].update(slide_partner.read()[0])
                        if slide_partner.slide_id.question_ids:
                            gains = [slide_partner.slide_id.quiz_first_attempt_reward,
                                     slide_partner.slide_id.quiz_second_attempt_reward,
                                     slide_partner.slide_id.quiz_third_attempt_reward,
                                     slide_partner.slide_id.quiz_fourth_attempt_reward]
                            channel_progress[slide_partner.slide_id.id]['quiz_gain'] = gains[slide_partner.quiz_attempts_count] if slide_partner.quiz_attempts_count < len(gains) else gains[-1]
        
                if include_quiz:
                    quiz_info = slides._compute_quiz_info(self.env.user.partner_id, quiz_done=False)
                    for slide_id, slide_info in quiz_info.items():
                        channel_progress[slide_id].update(slide_info)
                time_left_val=0.0
                for sl in val.channel_id.slide_ids:
                    if channel_progress[sl.id].get('completed') != True:
                        if sl.is_published:
                            time_left_val=time_left_val+sl.completion_time
                        
                val.time_left = time_left_val
    # joined_attendee_status = fields.Boolean('Attendee Status',compute="_compute_joined_attendee_status",default=False,)
    #
    # def _compute_joined_attendee_status(self):
    #     print('!QQQQQQQQQQQQQQQQQQQQQQQqqqqqq')
    #     for rec in self:
    #         current_user_partner_id = self.env.user
    #         print('@@@@@@@@@@@@@@@@@',current_user_partner_id)
    # @api.depends('channel_liked',"channel_disliked","course_joined")
    # def _compute_like_dislike_status(self):
    #     print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    #     for rec in self:
    #         if not rec.channel_liked and not rec.channel_disliked:
    #             rec.not_liked_disliked = True

    @api.onchange('custom_user_id')
    def _onchange_custom_user_id(self):
        if self.custom_user_id:
            if self.custom_user_id.partner_id:
                self.partner_id = self.custom_user_id.partner_id.id
            else:
                self.partner_id = False
        else:
            self.partner_id = False

    @api.depends('partner_id')
    def _user_code_val(self):
        for val in self:
            code = ''
            if val.partner_id:
                user_id = self.env['res.users'].sudo().search([('partner_id', '=', val.partner_id.id)], limit=1)
                if user_id:
                    if user_id.customer_code:
                        code = user_id.customer_code
                    if user_id.pre_joinee_code:
                        code = user_id.pre_joinee_code
                    if user_id.emp_code and user_id.is_employee:
                        code = user_id.emp_code
            val.user_code = code

    @api.depends('channel_id.course_close_date', 'completion')
    def _expired_status(self):
        for val in self:
            if val.channel_id.course_close_date:
                new_date = datetime.now()
                a = new_date.strftime("%Y-%m-%d %H:%M:%S")
                b = val.channel_id.course_close_date.strftime("%Y-%m-%d %H:%M:%S")
                if b < a:
                    if not val.expired_status:
                        if val.completion != 100:
                            val.expired_status = True
                        # else:
                        #     print("vvvvvvvvvvv", val.completion)
                        #     val.expired_status = False
                else:
                    if val.expired_status:
                        if val.completion != 100:
                            val.unlink()

    @api.onchange('completion')
    def _fullcomplete(self):
        if self.completion == 100:
            self.completeattend = True

        else:
            self.completeattend = False

    @api.onchange('completeattend')
    def testone_notification(self):
        for i in self:
            newcompleted = i.completeattend
            newurl = self.env['slide.channel.partner'].sudo().search(
                [('completeattend', '=', newcompleted), ('partner_id', '=', i.partner_id.id)])

            slide = self.env['slide.slide'].sudo().search([('id', 'in', newurl.channel_id.slide_ids.ids)])
            for j in newurl.channel_id.slide_ids:
                if j.slide_type == 'certification':
                    certification_url = slide._generate_certification_url().get(j.id)
                    if certification_url:
                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        finalurl = base_url + str(certification_url)
                        if newcompleted == True and i.completion == 100:
                            outgoing_server_name = self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
                            template_id = self.env.ref('ecom_lms.email_template_course_feedback')
                            if template_id and outgoing_server_name:
                                template_id.email_from = outgoing_server_name
                                template_id.email_to = i.partner_email
                                template_id.subject = "Submit Certification/Feedback"
                                template_id.body_html = """ <html>
                                                   <head></head>
                                                   <body>
                                                   <p>Dear """ + i.partner_id.name + """</p>
                                                    <p>
                                                   Please click on the Start Button to Test Certification for the completed """ + i.channel_id.name + """course.

                                                    </p>
                                                    <p>
                                                     <a href=""" + str(finalurl) + """
                            style="padding: 5px 10px; color: #FFFFFF; text-decoration: none; background-color: #875A7B; border: 1px solid #875A7B; border-radius: 3px">
                            Start Button</a></p>
                            <p>Thankyou</p>"""
                                template_id.send_mail(j.id, force_send=True)
            return

    def _recompute_completion(self):
        read_group_res = self.env['slide.slide.partner'].sudo().read_group(
            ['&', '&', ('channel_id', 'in', self.mapped('channel_id').ids),
             ('partner_id', 'in', self.mapped('partner_id').ids),
             ('completed', '=', True),
             ('slide_id.is_published', '=', True),
             ('slide_id.active', '=', True)],
            ['channel_id', 'partner_id'],
            groupby=['channel_id', 'partner_id'], lazy=False)
        mapped_data = dict()
        for item in read_group_res:
            mapped_data.setdefault(item['channel_id'][0], dict())
            mapped_data[item['channel_id'][0]][item['partner_id'][0]] = item['__count']

        partner_karma = dict.fromkeys(self.mapped('partner_id').ids, 0)
        for record in self:
            record.completed_slides_count = mapped_data.get(record.channel_id.id, dict()).get(record.partner_id.id, 0)
            record.completion = 100.0 if record.completed else round(
                100.0 * record.completed_slides_count / (record.channel_id.total_slides or 1))

            if not record.completed and record.channel_id.active and record.completed_slides_count >= record.channel_id.total_slides:
                record.completed = True
                partner_karma[record.partner_id.id] += record.channel_id.karma_gen_channel_finish

            if record.completion == 100.0:
                template_id = self.env.ref('ecom_lms.email_template_course_completed')
                suggested_template_id = self.env.ref('ecom_lms.email_template_just_completed_by_user')
                outgoing_server_name = self.env['ir.mail_server'].sudo().search([('sequence', '=', 11)],
                                                                                limit=1).smtp_user
                if outgoing_server_name and template_id:
                    template_id.email_from = outgoing_server_name
                    template_id.send_mail(record.id, force_send=True)
                channel_partner_lst = []
                user_lst = ''
                if outgoing_server_name and suggested_template_id:
                    if record.channel_id.sudo().channel_partner_ids:
                        for channel_partner in record.channel_id.sudo().channel_partner_ids:
                            channel_partner_lst.append(channel_partner.partner_id.id)

                    user_ids = self.env['res.users'].search([])
                    for user in user_ids:
                        if user.partner_id.id not in channel_partner_lst:
                            user_lst += str(user.partner_id.email) + ','

                    suggested_template_id.email_from = self.env.user.partner_id.email
                    suggested_template_id.email_to = user_lst
                    suggested_template_id.send_mail(record.id, force_send=True)

        partner_karma = {partner_id: karma_to_add
                         for partner_id, karma_to_add in partner_karma.items() if karma_to_add > 0}

        if partner_karma:
            users = self.env['res.users'].sudo().search([('partner_id', 'in', list(partner_karma.keys()))])
            for user in users:
                users.add_karma(partner_karma[user.partner_id.id])

    def score_details(self, slide_id):
        val = ''
        if slide_id:
            if slide_id:
                if slide_id.quiz_first_attempt_reward and slide_id.quiz_second_attempt_reward and slide_id.quiz_third_attempt_reward and slide_id.quiz_fourth_attempt_reward:
                    val = slide_id.quiz_fourth_attempt_reward

                elif slide_id.quiz_first_attempt_reward and slide_id.quiz_second_attempt_reward and slide_id.quiz_third_attempt_reward and not slide_id.quiz_fourth_attempt_reward:
                    val = slide_id.quiz_third_attempt_reward

                elif slide_id.quiz_first_attempt_reward and slide_id.quiz_second_attempt_reward and not slide_id.quiz_third_attempt_reward and not slide_id.quiz_fourth_attempt_reward:
                    val = slide_id.quiz_second_attempt_reward

                elif slide_id.quiz_first_attempt_reward and not slide_id.quiz_second_attempt_reward and not slide_id.quiz_third_attempt_reward and not slide_id.quiz_fourth_attempt_reward:
                    val = slide_id.quiz_first_attempt_reward
        return val

    def assessment_details(self, channel_id):
        val = ''
        if channel_id:
            first_bool = False
            if channel_id.slide_ids:
                for slide in channel_id.slide_ids:
                    if slide.slide_type == 'document':
                        if not first_bool:
                            val = slide.name
                            first_bool = True
                        else:
                            val = val + ',' + slide.name

        return val

    # def quiz_details_details(self, channel_id):
    #     val=''
    #     if channel_id:
    #         cust_id=self.env['slide.channel'].browse(channel_id)
    #         if cust_id.slide_ids:
    #             for slide in cust_id.slide_ids:
    #                 if slide.slide_type == 'quiz':
    #                     val=val+slide.name
    #
    #     return val
    #
    # def score_details(self, channel_id):
    #     val=''
    #     if channel_id:
    #         cust_id=self.env['slide.channel'].browse(channel_id)
    #         if cust_id.slide_ids:
    #             for slide in cust_id.slide_ids:
    #                 if slide.slide_type == 'quiz':
    #                     val=val+slide.name
    #
    #     return val

    
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res=super(liveattendanceuser, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type != 'search' and (self.env.user.has_group('ecom_lms.trainer_user_group')):
            root = etree.fromstring(res['arch'])
            root.set('create', 'false')
            res['arch'] = etree.tostring(root)
        return res
    
    
    @api.model
    def create(self, values):
        res = super(liveattendanceuser, self).create(values)
        template_id = self.env.ref('ecom_lms.email_template_assigned_user')

        outgoing_server_name = self.env['ir.mail_server'].sudo().search([('sequence', '=', 11)], limit=1).smtp_user

        if outgoing_server_name and template_id:
            template_id.email_from = self.env.user.partner_id.email
            template_id.send_mail(res.id, force_send=True)

        suggested_template_id = self.env.ref('ecom_lms.email_template_just_started_by_user')
        user_lst = ''
        channel_partner_lst = []
        if outgoing_server_name and suggested_template_id:

            if res.channel_id.sudo().channel_partner_ids:
                for channel_partner in res.channel_id.sudo().channel_partner_ids:
                    channel_partner_lst.append(channel_partner.partner_id.id)

            user_ids = self.env['res.users'].search([])
            for user in user_ids:
                if user.partner_id.id not in channel_partner_lst:
                    user_lst += str(user.partner_id.email) + ','

            suggested_template_id.email_from = self.env.user.partner_id.email
            suggested_template_id.email_to = user_lst
            suggested_template_id.send_mail(res.id, force_send=True)
        if not res.channel_liked and not res.channel_disliked:
            res.not_liked_disliked = True
        res.course_joined = True
        return res

    def course_delay_method(self):
        current_date = datetime.now()
        template_id = self.env.ref('ecom_lms.email_template_delay_user')
        outgoing_server_name = self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
        delay_courses = self.env['slide.channel'].sudo().search([('course_close_date', '!=', False)])
        delay_course_lst = []
        for delay in delay_courses:
            if delay.course_close_date.date() < current_date.date():
                for delay_partner in delay.sudo().channel_partner_ids:
                    if delay_partner.completion != 100:
                        if delay.id not in delay_course_lst:
                            delay_course_lst.append(delay.id)
                        if outgoing_server_name and template_id:
                            template_id.email_from = outgoing_server_name
                            template_id.send_mail(delay_partner.id, force_send=True)

        usr_lst = []
        users = self.env['res.users'].search([])
        for user in users:
            if user.has_group('base.group_system'):
                usr_lst.append(user.id)
        user_mail_lst = ''
        for admin_user in usr_lst:
            user_id = self.env['res.users'].browse(admin_user)
            user_mail_lst += str(user_id.partner_id.email) + ','
        if len(delay_course_lst) > 0:
            template_id1 = self.env.ref('ecom_lms.email_template_delay_course_lst_to_Admin')
            if outgoing_server_name and template_id1:
                template_id1.email_from = outgoing_server_name

                string = 'Delayed Course List'
                wb = xlwt.Workbook(encoding='utf-8')
                worksheet = wb.add_sheet(string)
                filename = 'Delayed Course List' + '.xls'
                style_value = xlwt.easyxf(
                    'font: bold on, name Arial ,colour_index black;')
                style_header = xlwt.easyxf(
                    'font: bold on ,colour_index red;' "borders: top double , bottom double ,left double , right double;")

                worksheet.write_merge(0, 0, 0, 5, "Delayed Course List", xlwt.easyxf(
                    'font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz center;'))

                worksheet.write(1, 0, 'Course Name', style_value)
                worksheet.write(1, 1, 'Due Date', style_value)
                worksheet.write(1, 2, 'User Name', style_value)
                worksheet.write(1, 3, 'User code/ID', style_value)
                # worksheet.write(1, 1, 'Close Date', style_value)
                a = 2

                if len(delay_course_lst) > 0:
                    for lst in delay_course_lst:
                        course_id = self.env['slide.channel'].sudo().browse(lst)
                        due_date = ''

                        due_date = course_id.course_close_date.strftime('%d-%m-%Y')

                        worksheet.write(a, 0, course_id.name or '')
                        worksheet.write(a, 1, due_date or '')
                        if course_id.sudo().channel_partner_ids:
                            for channel_partner in course_id.sudo().channel_partner_ids:
                                user = self.env['res.users'].search(
                                    [('partner_id', '=', channel_partner.partner_id.id)], limit=1)
                                if user:
                                    worksheet.write(a, 2, user.name or '')
                                    worksheet.write(a, 3, user.customer_code or '')
                                    a += 1
                                else:
                                    a += 1
                        else:
                            a += 1

                fp = io.BytesIO()
                wb.save(fp)
                out = base64.encodestring(fp.getvalue())
                view_report_status_id = self.env['delayed.course.list.view.report'].create(
                    {'excel_file': out, 'file_name': filename})

                attachment_id = self.env['ir.attachment'].create({'name': 'Delayed Course List.xlsx',
                                                                  'store_fname': filename,
                                                                  'datas': out})

                template_id1.attachment_ids = [(6, 0, [attachment_id.id])]
                template_id1.email_to = user_mail_lst

                template_id1.send_mail(self.id, force_send=True)


class RecommendedUsers(models.Model):
    _name = 'recommend.users'

    res_user_id = fields.Many2one('res.users', string='Users')
    recommend_courses_id = fields.Many2one('slide.channel')


class delayed_course_list_view_report(models.TransientModel):
    _name = 'delayed.course.list.view.report'
    _rec_name = 'excel_file'

    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64)







