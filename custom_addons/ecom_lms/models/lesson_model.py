import tempfile

import certifi
from google.auth.transport import urllib3

from odoo import api, fields, models, _
import zipfile
import tempfile
from werkzeug import urls
import requests
from odoo.http import request
from odoo.exceptions import AccessError, UserError, ValidationError
import re
import base64
import io
from datetime import datetime

import PyPDF2

class CustomElearningLesson(models.Model):
    _inherit = 'slide.slide'

    custom_description = fields.Html(
        'Description', translate=True,
        help="The description that is displayed on top of the course page, just below the title")
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
        'Backwards Navigation', default=False,
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
    is_revision = fields.Boolean(
        'Revision', default=False,
        help="To check status of course based on message added for revision.")
    random_question = fields.Selection([
        ('serial', 'Serialized Questions'), ('random', 'Randomized Questions')],
        default='serial', string='Question Order', required=True,
        help='Choose whether questions to display in lessons are serialized or randomized.')
    live_session = fields.Selection([('yes','Yes'),('no','No')],string="Live Session",default='no')
    # slide_type = fields.Selection(selection_add=[('feedback', 'Feedback')])

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
    revision_message = fields.Char(string='Lesson Revision', tracking=True)
    is_revision = fields.Boolean(
        'Revision', default=False,
        help=" To check status of course based on the message added for revision.")
    lesson_open_date = fields.Datetime('Open Date')
    lesson_close_date = fields.Datetime('Close Date')
    pass_fail = fields.Selection([
        ('all_pass', 'Disable'), ('pass', 'Enable')],
        default='all_pass', required=True,
        help='Option of pass/fail to add passing percentage.')
    custom_pass_percent = fields.Char("Required Passing(%)", required=True, default=0, translate=True)
    custom_url = fields.Char('URL', help="Youtube or Google Document URL")
    course_category_id = fields.Many2one('course.category', string='Course Category')
    custom_pass_percent = fields.Char("Required Passing(%)", default=0, translate=True,track_visibility='onchange')
    custom_url = fields.Char('URL', help="Youtube or Google Document URL",track_visibility='onchange')
    course_category_id = fields.Many2one('course.category', string='Course Category',track_visibility='onchange')
    lesson_weight = fields.Integer('Weight',track_visibility='onchange')
    is_time_limited = fields.Boolean('The Quiz is limited in time')
    time_limit = fields.Float("Time limit (minutes)", default=10)
    completion_time = fields.Float('Duration', digits=(10, 4),default=0.166, help="The estimated completion time for this slide")
    
    slide_type = fields.Selection([
        ('infographic', 'Infographic'),
        ('webpage', 'Web Page'),
        ('presentation', 'Presentation'),
        ('document', 'Document'),
        ('video', 'Video/Audio'),
        ('quiz', "Quiz")],
        string='Type',required=True,
        default='document',
        help="The document type will be set automatically based on the document URL and properties (e.g. height and width for presentation and document).")
    
    doc_type = fields.Selection([('doc','.docx'),('pdf','.pdf')],default='doc',string='Document Type')
    ppt_type = fields.Selection([('ppt','.ppt/.pptx')],default='ppt',string='Presentation Type')
    file_name = fields.Char('Upload File Name', size=64)
    live_url = fields.Char(string="Live Session Url")

    @api.onchange('live_session')
    def _onchange_livesession(self):
        if self.live_session == 'no':
            self.live_url = ''


    #
    # @api.onchange('datas')
    # def _on_change_datas(self):
    #     """ For PDFs, we assume that it takes 5 minutes to read a page.
    #         If the selected file is not a PDF, it is an image (You can
    #         only upload PDF or Image file) then the slide_type is changed
    #         into infographic and the uploaded dataS is transfered to the
    #         image field. (It avoids the infinite loading in PDF viewer)"""
    #     if self.datas:
    #         if self.file_name.endswith('.doc') or self.file_name.endswith('.docx'):
    #             self.doc_type = 'doc'
    #             self.slide_type = 'document'
    #             self.completion_time = 0.0
    #             self.datas = self.datas
    #
    #
    #         elif self.file_name.endswith('.pdf'):
    #             self.doc_type = 'pdf'
    #             self.slide_type = 'document'
    #             self.datas = self.datas
    #
    #             data = base64.b64decode(self.datas)
    #             if data.startswith(b'%PDF-'):
    #                 pdf = PyPDF2.PdfFileReader(io.BytesIO(data), overwriteWarnings=False, strict=False)
    #                 self.completion_time = (5 * len(pdf.pages)) / 60
    #
    #         elif self.file_name.endswith('.ppt') or self.file_name.endswith('.pptx'):
    #             self.ppt_type = 'ppt'
    #             self.slide_type = 'presentation'
    #             self.completion_time = 0.0
    #             self.datas = self.datas
    #
    #
    #         elif self.file_name.endswith('.mp4'):
    #             self.slide_type = 'video'
    #             self.datas = self.datas
    #
    #         else:
    #             self.slide_type = 'infographic'
    #             self.image_1920 = self.datas
    #             self.datas = None
    #             # raise UserError(_('LMS only support content in doc, pdf, ppt, format'))
    #
    #
    #
    #         # else:
    #         #     """ In else part if assign slide_type as Infographics it doesn't read doc file."""
    #         #     self.file_name == ''
    #         #     raise UserError(_('LMS only support content in doc, pdf, ppt, format'))
    #     else:
    #         self.doc_type = None
    #         self.ppt_type = None
    #         self.slide_type = 'document'



    @api.model
    def create(self, values):
        channel_id = self._context.get('default_channel_id')
        if channel_id:
            values['channel_id'] = channel_id
        # opendate = values.get['lesson_open_date']
        # closedate = values.get['lesson_close_date']
        # if opendate < datetime.now():
        #     raise UserError(_("Open Date should be greater Current Date."))
        # if closedate < opendate:
        #     raise UserError(_("Close Date should be greater Open Date."))
        res = super(CustomElearningLesson, self).create(values)
        return res
    
    
    @api.onchange('completion_time')
    def _on_change_completion_time(self):
        if not self.completion_time:
            raise UserError(_('Lesson Duration Cannot be Zero '))

    # @api.constrains('completion_time')
    # def _constrains_completion_time(self):
    #     for record in self:
    #         if not record.completion_time:
    #             raise UserError(_('Lesson Duration Cannot be Zero '))
    
    
    
    def _parse_youtube_document(self, document_id, only_preview_fields):
        """ If we receive a duration (YT video), we use it to determine the slide duration.
        The received duration is under a special format (e.g: PT1M21S15, meaning 1h 21m 15s). """

        key = self.env['website'].get_current_website().website_slide_google_app_key
        fetch_res = self._fetch_data('https://www.googleapis.com/youtube/v3/videos', {'id': document_id, 'key': key, 'part': 'snippet,contentDetails', 'fields': 'items(id,snippet,contentDetails)'}, 'json')
        if fetch_res.get('error'):
            return {'error': self._extract_google_error_message(fetch_res.get('error'))}

        values = {'slide_type': 'video', 'document_id': document_id}
        items = fetch_res['values'].get('items')
        if not items:
            return {'error': _('Please enter valid Youtube or Google Doc URL')}
        youtube_values = items[0]

        youtube_duration = youtube_values.get('contentDetails', {}).get('duration')
        if youtube_duration:
            parsed_duration = re.search(r'^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$', youtube_duration)
            if parsed_duration:
                values['completion_time'] = (int(parsed_duration.group(1) or 0)) + \
                                            (int(parsed_duration.group(2) or 0) / 60) + \
                                            (int(parsed_duration.group(3) or 0) / 3600)

        if youtube_values.get('snippet'):
            snippet = youtube_values['snippet']
            if only_preview_fields:
                values.update({
                    'url_src': snippet['thumbnails']['high']['url'],
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'custom_description': snippet['description'],
                })

                return values

            values.update({
                'name': snippet['title'],
                'image_1920': self._fetch_data(snippet['thumbnails']['high']['url'], {}, 'image')['values'],
                'description': snippet['description'],
                'custom_description': snippet['description'],
                'mime_type': False,
            })
        return {'values': values}
    
    
    
    
    
    
    # <------------------Onedrive video player in lessson code-------------------------->
    
    # @api.model
    # def _parse_onedrive_document(self, document_id, only_preview_fields):
    #     params = {}
    #     params['projection'] = 'BASIC'
    #     print ("yyyyyyyyyyyyyyyy",self.env)
    #     if 'google.drive.config' in self.env:
    #         access_token = self.env['google.drive.config'].get_access_token()
    #         if access_token:
    #             params['access_token'] = access_token
    #     if not params.get('access_token'):
    #         params['key'] = self.env['website'].get_current_website().website_slide_google_app_key
    #     google_values={}
    #     # fetch_res = self._fetch_data('https://api.onedrive.com/v1.0/drive/root/%s' % document_id, params, "json")
    #     # fetch_res = self._fetch_data('http://1drv.ms/%s' % document_id, params, "json")
    #     # print ("hhhhhhhhhhhhhhhh",fetch_res)
    #     # if fetch_res.get('error'):
    #     #     return {'error': self._extract_google_error_message(fetch_res.get('error'))}
    #
    #     # google_values = fetch_res['values']
    #     google_values['mimeType']='video/mp4'
    #     google_values['title']='ttttttttttt'
    #     if only_preview_fields:
    #         return {
    #             # 'url_src': google_values['thumbnailLink'],
    #             'title': 'tttttttttt',
    #         }
    #
    #     values = {
    #         # 'name': google_values['title'],
    #         # 'image_1920': self._fetch_data(google_values['thumbnailLink'].replace('=s220', ''), {}, 'image')['values'],
    #         'mime_type': google_values['mimeType'],
    #         'document_id': document_id,
    #     }
    #     if google_values['mimeType'].startswith('video/'):
    #         values['slide_type'] = 'video'
    #     elif google_values['mimeType'].startswith('image/'):
    #         values['datas'] = values['image_1920']
    #         values['slide_type'] = 'infographic'
    #     elif google_values['mimeType'].startswith('application/vnd.google-apps'):
    #         values['slide_type'] = get_slide_type(values)
    #         if 'exportLinks' in google_values:
    #             values['datas'] = self._fetch_data(google_values['exportLinks']['application/pdf'], params, 'pdf')['values']
    #     elif google_values['mimeType'] == 'application/pdf':
    #         # TODO: Google Drive PDF document doesn't provide plain text transcript
    #         values['datas'] = self._fetch_data(google_values['webContentLink'], {}, 'pdf')['values']
    #         values['slide_type'] = get_slide_type(values)
    #
    #     return {'values': values}
    #
    # def _find_document_data_from_url(self, url):
    #     url_obj = urls.url_parse(url)
    #     print ("url_obj.ascii_host",url_obj.ascii_host)
    #     if url_obj.ascii_host == 'onedrive.live.com':
    #         # expr = re.compile(r'(^https:\/\/onedrive.live.com)')
    #         expr = re.compile(r'(^https:\/\/onedrive.live.com|^https:\/\/onedrive.live.com).*\/?authkey=%([^\/]*)')
    #         print ("exprexprexprexprexpr",expr)
    #         arg = expr.match(url)
    #         print ("dddddddddddd",arg)
    #         document_id = arg and arg.group(2) or False
    #         print ("kkkkkkkkkkkk",document_id)
    #         if document_id:
    #             return ('onedrive', document_id)
    #     if url_obj.ascii_host == 'youtu.be':
    #         return ('youtube', url_obj.path[1:] if url_obj.path else False)
    #     elif url_obj.ascii_host in ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'www.youtube-nocookie.com'):
    #         v_query_value = url_obj.decode_query().get('v')
    #         if v_query_value:
    #             return ('youtube', v_query_value)
    #         split_path = url_obj.path.split('/')
    #         if len(split_path) >= 3 and split_path[1] in ('v', 'embed'):
    #             return ('youtube', split_path[2])
    #
    #     expr = re.compile(r'(^https:\/\/docs.google.com|^https:\/\/drive.google.com).*\/d\/([^\/]*)')
    #     print ("eeeeeeeeeeeeee",expr)
    #     arg = expr.match(url)
    #     print ("arggggggggggggg",arg)
    #     document_id = arg and arg.group(2) or False
    #     if document_id:
    #         return ('google', document_id)
    #
    #     return (None, False)
    #
    # def _parse_document_url(self, url, only_preview_fields=False):
    #     document_source, document_id = self._find_document_data_from_url(url)
    #     print ("aaaaaaaaaaaaaaaa",document_source,document_id)
    #     if document_source and hasattr(self, '_parse_%s_document' % document_source):
    #         print ("rrrrrrrrrrrr")
    #         return getattr(self, '_parse_%s_document' % document_source)(document_id, only_preview_fields)
    #     return {'error': _('Unknown document')}
    #
    #
    #
    # @api.depends('document_id', 'slide_type', 'mime_type')
    # def _compute_embed_code(self):
    #     base_url = request and request.httprequest.url_root or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     if base_url[-1] == '/':
    #         base_url = base_url[:-1]
    #     for record in self:
    #         if record.datas and (not record.document_id or record.slide_type in ['document', 'presentation']):
    #             slide_url = base_url + url_for('/slides/embed/%s?page=1' % record.id)
    #             record.embed_code = '<iframe src="%s" class="o_wslides_iframe_viewer" allowFullScreen="true" height="%s" width="%s" frameborder="0"></iframe>' % (slide_url, 315, 420)
    #         elif record.slide_type == 'video' and record.document_id:
    #             if not record.mime_type:
    #                 # embed youtube video
    #                 query = urls.url_parse(record.url).query
    #                 query = query + '&theme=light' if query else 'theme=light'
    #                 record.embed_code = '<iframe src="//www.youtube-nocookie.com/embed/%s?%s" allowFullScreen="true" frameborder="0"></iframe>' % (record.document_id, query)
    #             else:
    #                 print ("qqqqqqqqqqq",record.document_id)
    #                 # record.embed_code ='<iframe src="https://onedrive.live.com/download?cid=3C02A4FB2D41B5AF&resid=3C02A4FB2D41B5AF%21110&authkey=AHG4X3e98T5brNo" width="98" height="120" frameborder="0" scrolling="no" allowfullscreen></iframe>'
    #
    #
    #                 # record.embed_code ='<iframe src="https://onedrive.live.com/embed?cid=3C02A4FB2D41B5AF&resid=3C02A4FB2D41B5AF%21110&authkey=AHG4X3e98T5brNo" width="98" height="120" frameborder="0" scrolling="no" allowfullscreen></iframe>'
    #
    #                 # record.embed_code = '<iframe src="//onedrive.live.com/?authkey=AHG4X3e98T5brNo/preview" allowFullScreen="true" frameborder="0"></iframe>'
    #                 url= '%'+record.document_id
    #                 print ("urlllllllllllll",url)
    #
    #                 record.embed_code = '<iframe src="//onedrive.live.com/?authkey=%s/preview" allowFullScreen="true" frameborder="0"></iframe>' % (url)
    #                 # embed google doc video
    #                 # record.embed_code = '<iframe src="//drive.google.com/file/d/%s/preview" allowFullScreen="true" frameborder="0"></iframe>' % (record.document_id)
    #         else:
    #             record.embed_code = False
    #
    #
    # @api.onchange('url')
    # def _on_change_url(self):
    #     self.ensure_one()
    #     if self.url:
    #         res = self._parse_document_url(self.url)
    #         print ("anchal-------------",res)
    #         if res.get('error'):
    #             raise Warning(res.get('error'))
    #         values = res['values']
    #         if not values.get('document_id'):
    #             raise Warning(_('Please enter valid Youtube or Google Doc URL'))
    #         for key, value in values.items():
    #             self[key] = value
    #

    
    def get_lesson_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        lesson_url= '/slides/slide/%s?fullscreen=1'% self.id
        # lesson_url= '/slides/slide/%s'% self.id
        return werkzeug.urls.url_join(base_url, lesson_url) if self.id else False
    
    def action_send_lesson(self):
        """ Open a window to compose an email, pre-filled with the Lesson message """
        # Ensure that this survey has at least one page with at least one question.
        # if (not self.page_ids and self.questions_layout == 'page_per_section') or not self.question_ids:
        #     raise exceptions.UserError(_('You cannot send an invitation for a survey that has no questions.'))
        #
        # if self.state == 'closed':
        #     raise exceptions.UserError(_("You cannot send invitations for closed surveys."))

    def translate_lesson_title_data(self):
        translate_lesson_id = self.env['lesson.title.translation'].search([('slide_id', '=', self.id)], limit=1)
        if translate_lesson_id:
            return {
                'name': ('Translate'),
                'view_mode': 'form',
                'res_model': 'lesson.title.translation',
                'views': [(self.env.ref('ecom_lms.lesson_title_translation_wiz_form_view').id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': translate_lesson_id.id,
            }

        else:
            title_translation_id = self.env['lesson.title.translation'].create({'slide_id': self.id})
            return {
                'name': ('Translate'),
                'view_mode': 'form',
                'res_model': 'lesson.title.translation',
                'views': [(self.env.ref('ecom_lms.lesson_title_translation_wiz_form_view').id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': title_translation_id.id,
            }

    @api.depends('slide_partner_ids.slide_id')
    def _compute_slide_views(self):

        read_group_res = self.env['slide.slide.partner'].sudo().read_group(
            [('slide_id', 'in', self.ids)],
            ['slide_id'],
            groupby=['slide_id']
        )
        mapped_data = dict((res['slide_id'][0], res['slide_id_count']) for res in read_group_res)

        for slide in self:
            newslide = slide.live_session
            if newslide == True:
                slidenew = self.env['slide.channel.partner'].sudo().search([('channel_id', '=', slide.channel_id.id),
                                                                            ('partner_id', '=',
                                                                             slide.env.user.partner_id.id)])
                slidenew.write({"initailattendance": True})
            slide.slide_views = mapped_data.get(slide.id, 0)


    @api.onchange('custom_url')
    def _on_change_custom_url(self):
        # try using if not
        if self.custom_url == False:
            pass
        else:
            lines = []
            vals = {'name': self.custom_url, 'link': self.custom_url}
            lines.append((0, 1, vals))
            self.link_ids = lines

    @api.onchange('slide_type')
    def _on_change_slide(self):
        if not 'slide_type' == 'webpage':
            lines = []
            vals = {'name': self.custom_url, 'link': self.custom_url}
            lines.append((5, 1, vals))
            self.link_ids = lines

    # @api.onchange('survey_id')
    # def _on_change_survey(self):
    #     print(self.survey_id,"66666666666666")
    #     if not 'survey_id' == 'NULL' and '' and False:
    #         lines = []
    #         vals = {'name': self.custom_url, 'link': self.custom_url}
    #         lines.append((5, 1, vals))
    #         self.link_ids = lines

    # NEED ONCHANGE ON SLIDE_TYPE TO REMOVE THE EXTERNAL FIELD
    # @api.model
    # def create(self, values):
    #     if values.get('custom_url'):
    #         values['link_ids'] = [(0, None, {'name': values.get('custom_url'), 'link': values.get('custom_url')})]
    #     # print(values)
    #     result = super(CustomElearningLesson, self).create(values)
    #
    #     return result
    #
    # def write(self, vals):
    #     res = super(CustomElearningLesson, self).write(vals)
    #     print(vals)
    #     if vals.get('slide_type') != 'webpage':
    #         print("asdasdasd")
    #     return res
    
    
class SlidePartnerRelation(models.Model):
    _inherit = 'slide.slide.partner'
    
    # wrong_qus_ids= fields.Many2many('slide.question', string='Wrong Question')
    
    
    wrong_qus_line= fields.One2many('slide.slide.partner.wrong.question', 'slide_partner_id', string='Wrong Ans')



class SlideSlidePartnerWrongQuestion(models.Model):
    _name = 'slide.slide.partner.wrong.question'

    slide_partner_id= fields.Many2one('slide.slide.partner','Slide Partner')
    wrong_attempt_count= fields.Integer('Wrong Attempt')
    wrong_qus_ids= fields.Many2many('slide.question', string='Wrong Question')
    
    
        
        
    
    
    
    
    
    
