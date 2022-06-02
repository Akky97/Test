import logging
import base64
from future.backports.datetime import timedelta
from odoo import api, fields, models, _
from odoo.addons.web.controllers.main import ensure_db, Session
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.website_slides.controllers.main import WebsiteSlides
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website_profile.controllers.main import WebsiteProfile
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import AccessError
from odoo import http, tools, _, SUPERUSER_ID
from odoo.http import content_disposition, Controller, request, route
from operator import itemgetter
from odoo.osv import expression
from collections import OrderedDict

from odoo.addons.website.controllers.main import Website
from odoo.addons.survey.controllers.main import Survey
from odoo.addons.portal.controllers.web import Home
from datetime import datetime, date, time
from odoo.addons.web.controllers.main import Home

from datetime import datetime, timedelta

import sys
import logging
import json
import random
import math

import odoo
from simplecrypt import encrypt, decrypt
from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError, AccessDenied
from odoo.http import content_disposition, Controller, request, route
from odoo.tools import consteq

from dateutil.relativedelta import relativedelta
from odoo.tools import format_datetime, format_date, is_html_empty
from operator import itemgetter

from odoo.tools import date_utils
from odoo.osv.expression import AND, OR
from odoo.osv import expression
import requests

import werkzeug

_logger = logging.getLogger(__name__)





class SathiApiControllers(http.Controller):

    def validate_keys(self, mandatory_keys, request_data_keys):
        return all(el in request_data_keys for el in mandatory_keys)

    # def login_with_creds(self, request_data):
    #     db = 'ecom_db14_duplicate'
    #     if self.validate_keys(['user_code' ,'token'], request_data.keys()):
    #         login = request_data['user_code']
    #         user_id = request.env["res.users"].sudo().search(['|','|',('emp_code', '=',login),('customer_code', '=', login),('pre_joinee_code', '=', login)],limit=1)
    #         if user_id:
    #             user_id.user_token= request_data['token']
    #             password= user_id.user_pw
    #             return request.session.authenticate(db, login, password)
    #         else:
    #             return False
    #     else:
    #         return False
        
    def login_with_creds(self, request_data):
        if self.validate_keys(['user_code', 'token'], request_data.keys()):
            db = 'odoodb3'
            login = request_data['user_code']
            user_id = request.env["res.users"].sudo().search(['|','|',('emp_code', '=',login),('customer_code', '=', login),('pre_joinee_code', '=', login)],limit=1)
            if user_id:
                user_id.user_token= request_data['token']
                password= user_id.user_pw
                return request.session.authenticate(db, login, password)
            else:
                return False
        else:
            return False
        
        
    @http.route('/sathi_app/authenticate', auth='none',cors="*",type='json', csrf=False)
    def sathi_authenticate(self, **kwargs):
        # if self.login_with_creds(request.jsonrequest):
        if not self.validate_keys(['user_code','token'], request.jsonrequest.keys()):
            return "Please set the correct Input parameters"
        # emp_values={"user_code":kwargs['user_code'],"token":kwargs['token']}
        is_authenticated = self.login_with_creds(request.jsonrequest)
        dic = request.jsonrequest
        if not is_authenticated:
            return {"error":"Authentication detail not received"}
            # return response_ok(error="Authentication detail not received")
        else:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            pager_url= base_url+'/slides'
            login = dic['user_code']
            user_id = request.env["res.users"].sudo().search(['|','|',('emp_code', '=',login),('customer_code', '=', login),('pre_joinee_code', '=', login)],limit=1)
            
            if not user_id.image_1920:
                profile_url="/profile/view/user/%d" % user_id.id
                profile_pager_url= base_url+profile_url
                return {
                    "status": "Success",
                    "url": profile_pager_url
                }
            else:
                return {
                    "status": "Success",
                    "url": pager_url
                }
        
        
        
        
    # @http.route('/sathi_app/authenticate', type='http', auth="none",
    #             cors="*", csrf=False,methods=['POST'],)
    # def sathi_authenticate(self, **kwargs):
    #     if not self.validate_keys(['user_code','token'], kwargs.keys()):
    #         return "Please set the correct Input parameters"
    #
    #     emp_values={"user_code":kwargs['user_code'],"token":kwargs['token']}
    #
    #     is_authenticated = self.login_with_creds(emp_values)
    #     if not is_authenticated:
    #         return json.dumps({'error': 'Authentication detail not received'})
    #     else:
    #         base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #         pager_url= base_url+'/slides'
    #
    #         return werkzeug.utils.redirect(pager_url)


    # @http.route('/sathi_app/authenticate', type='http', auth="none",
    #             cors="*", csrf=False,methods=['POST'],)
    # def sathi_authenticate(self, **kwargs):
    #     url = 'https://test.ecomexpress.in:8001/v2/get-user-token'
    #     # #
    #     headers = {
    #         "Content-Type": "application/json",
    #         "app-code": "LMS",
    #         "cache-control": "no-cache",
    #         "postman-token": "a0b06829-a967-c501-75dc-088d74aa59f0",
    #         "username": "39679",
    #         "password": 'Smc@Sso123',
    #       }
    #     #
    #     print ("Aaaaaaaa")
    #     try:
    #         r = requests.post(url, headers=headers)
    #         print ("bbbbbbbbbbbbbb",r)
    #         # _logger.info("Auth API Response : %s " % str(r.content))
    #         j = json.loads(r.text)
    #     except Exception as e:
    #         msg = "API Error: %s" %e
    #         print ("ccccccccccccccc",msg)
    #         raise UserError(msg)
    #
    #
    #     data_val = j.get('result')
    #     api_data = eval(data_val)
    #     emp_values = api_data.get('data')
    #
    #     # emp_values={"username":"admin","customer_code":"123-hjk"}
    #
    #     is_authenticated = self.login_with_creds(emp_values)
    #     if not is_authenticated:
    #         return json.dumps({'error': 'Authentication detail not received'})
    #     else:
    #         base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #         pager_url= base_url+'/slides'
    #         return werkzeug.utils.redirect(pager_url)
            


class LoginHome(AuthSignupHome):

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        result = super(LoginHome, self).web_login(*args, **kw)
        if request.params.get('type') == 'customer':
            print("In Customer")
        if request.params.get('type') == 'employee':
            print("Employee")
        if request.params.get('type') == 'candidate':
            print("In Candidate")
        if request.uid != 4:
            if request.env.user.login_type == 'employee-onroll' or request.env.user.login_type == 'employee-offroll':
                values = {'name':request.env.user.id,
                          'user_code':request.env.user.emp_code,
                          'designation':request.env.user.designation,
                          'state_name':request.env.user.state_id.name,
                          'work_location_code':request.env.user.work_location,
                          'cost_type_code':None,
                          'band_code':request.env.user.band,
                          'region':request.env.user.region,
                          'check_in':fields.datetime.now(),
                          'number_of_login':1,
                          'logout': False
                          }
                res = request.env['time.spent.report'].sudo().create(values)
            if request.env.user.login_type == 'customer':
                values = {'name':request.env.user.id,
                          'user_code':request.env.user.customer_code,
                          'designation':request.env.user.designation,
                          'state_name':request.env.user.state_id.name,
                          'work_location_code':request.env.user.work_location,
                          'cost_type_code':None,
                          'band_code':request.env.user.band,
                          'region':request.env.user.region,
                          'check_in':fields.datetime.now(),
                          'number_of_login': 1,
                          'logout': False
                          }
                res = request.env['time.spent.report'].sudo().create(values)
            if request.env.user.login_type == 'candidate':
                values = {'name':request.env.user.id,
                          'user_code':request.env.user.pre_joinee_code,
                          'designation':request.env.user.designation,
                          'state_name':request.env.user.state_id.name,
                          'work_location_code':request.env.user.work_location,
                          'cost_type_code':None,
                          'band_code':request.env.user.band,
                          'region':request.env.user.region,
                          'check_in':fields.datetime.now(),
                          'number_of_login': 1,
                          'logout': False
                          }
                res = request.env['time.spent.report'].sudo().create(values)
        return result
    

    @http.route()
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        response = super(LoginHome, self).web_auth_reset_password(*args, **kw)
        if (
                request.httprequest.method == "POST"
                and qcontext.get("login")
                and "error" not in qcontext
                and qcontext.get("password") == qcontext.get("confirm_password")
        ):
            try:
                if qcontext.get('token'):
                    if not request.env.user.first_logged_in:
                        redirect_url = '/web/login?redirect=/web/change_language'
                        request.env.user.first_logged_in=True
                        return request.redirect(redirect_url)
                    else:
                        # self.do_signup(qcontext)
                        template = request.env.ref('ecom_lms.ecom_password_reset_email_template',
                                           raise_if_not_found=False)
                        user_sudo = request.env.user
                        outgoing_server_name = request.env['ir.mail_server'].sudo().search([],limit=1).smtp_user
                        if outgoing_server_name:
                            template.email_from = outgoing_server_name
                            if user_sudo and template:
                                template.sudo().send_mail(user_sudo.id, force_send=True)
                        return self.web_login(*args, **kw)

                    # return request.redirect(redirect_url)
            except Exception as e:
                qcontext['error'] = f"{e}"
                _logger.exception('Error when resetting password')
                
        return response

    @http.route(['/web/change_language'], type='http', auth="user", website=True, sitemap=True)
    def web_change_language(self, *args, **kw):
        first_login = False
        values = dict()
        language = kw.get('language')
        categories = request.env['course.category'].sudo().search([])
        category_list = []
        employee = False
        employee = False
        if request.env.user:
            if request.env.user.is_employee:
                employee = True
            else:
                employee = False
        # catg = kw.get('category_id')
        if (
                request.httprequest.method == "POST"
        ):
            try:
                redirect_url = '/slides/my/languages'
                user = request.env.user

                if request.httprequest.form.getlist('category_id'):
                    selected_topic = request.httprequest.form.getlist('category_id')
                    for topic in selected_topic:
                        topic1 = topic.split('course.category(')
                        final_topic = topic1[1].split(',')
                        new_category_id = request.env['course.category'].browse(int(final_topic[0]))
                        category_list.append(new_category_id.id)
                    user.topic_of_interest_ids = [(6, 0, category_list)]

                lang = request.lang.code if request.lang.code in request.website.mapped('language_ids.code') else None
                lang_lst = request.website.mapped('language_ids.code')
                selected_lang = request.params.get("language")

                change_lang = request.lang.code
                if lang and selected_lang:
                    if selected_lang == 'english':
                        change_lang = 'en_IN'
                        user.lang = change_lang
                        redirect_url = '/slides/my/languages'
                    if selected_lang == 'hindi':
                        change_lang = 'hi_IN'
                        user.lang = change_lang
                        redirect_url = '/slides/my/languages'
                        # redirect_url = '/hi/slides'
                    if selected_lang == 'gujarati':
                        change_lang = 'gu_IN'
                        user.lang = change_lang
                        redirect_url = '/slides/my/languages'
                        # redirect_url = '/gu/slides'
                    if selected_lang == 'telugu':
                        change_lang = 'te_IN'
                        user.lang = change_lang
                        redirect_url = '/slides/my/languages'
                        # redirect_url = '/te/slides'

                    if selected_lang == 'marathi':
                        change_lang = 'ma_IN'
                        user.lang = change_lang
                        redirect_url = '/slides/my/languages'
                        # redirect_url = '/te/slides'

                    if selected_lang == 'assamese':
                        change_lang = 'assa_IN'
                        user.lang = change_lang
                        redirect_url = '/slides/my/languages'
                        # redirect_url = '/te/slides'

                    if selected_lang == 'tamil':
                        change_lang = 'ta_IN'
                        user.lang = change_lang
                        redirect_url = '/slides/my/languages'
                        # redirect_url = '/te/slides'
                    if selected_lang == 'kannada':
                        change_lang = 'ka_IN'
                        user.lang = change_lang
                        redirect_url = '/slides/my/languages'
                        # redirect_url = '/te/slides'
                    if selected_lang == 'malyalam':
                        change_lang = 'mal_IN'
                        user.lang = change_lang
                        redirect_url = '/slides/my/languages'
                        # redirect_url = '/te/slides'

                redirect = request.redirect(redirect_url)
                redirect.set_cookie('frontend_lang', change_lang)
                cookie_lang = request.httprequest.cookies.get('frontend_lang')
                # template = request.env.ref('auth_signup.mail_template_user_signup_account_created',raise_if_not_found=False)
                template = request.env.ref('ecom_lms.ecom_mail_template_user_signup_account_created',
                                           raise_if_not_found=False)
                user_sudo = request.env.user

                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
                return redirect
            except Exception as e:
                _logger.exception(f'Exception {e}')
        values.update({
            'categories': categories if categories else None,
            'language': language,
            'usr_register_bool': True,
            'employee': employee,
            'first_login': True,
        })
        return request.render("ecom_lms.change_language_template", values)
    
    
class Surveynew(Survey):

    def _prepare_survey_data(self, survey_sudo, answer_sudo, **post):
        """ This method prepares all the data needed for template rendering, in function of the survey user input state.
            :param post:
                - previous_page_id : come from the breadcrumb or the back button and force the next questions to load
                                     to be the previous ones. """
        data = {
            'is_html_empty': is_html_empty,
            'survey': survey_sudo,
            'answer': answer_sudo,
            'breadcrumb_pages': [{
                'id': page.id,
                'title': page.title,
            } for page in survey_sudo.page_ids],
            'format_datetime': lambda dt: format_datetime(request.env, dt, dt_format=False),
            'format_date': lambda date: format_date(request.env, date)
        }
        if survey_sudo.questions_layout != 'page_per_question':
            triggering_answer_by_question, triggered_questions_by_answer, selected_answers = answer_sudo._get_conditional_values()
            data.update({
                'triggering_answer_by_question': {
                    question.id: triggering_answer_by_question[question].id for question in triggering_answer_by_question.keys()
                    if triggering_answer_by_question[question]
                },
                'triggered_questions_by_answer': {
                    answer.id: triggered_questions_by_answer[answer].ids
                    for answer in triggered_questions_by_answer.keys()
                },
                'selected_answers': selected_answers.ids
            })

        if not answer_sudo.is_session_answer and survey_sudo.is_time_limited and answer_sudo.start_datetime:
            data.update({
                'timer_start': answer_sudo.start_datetime.isoformat(),
                'time_limit_minutes': survey_sudo.time_limit
            })

        page_or_question_key = 'question' if survey_sudo.questions_layout == 'page_per_question' else 'page'

        # Bypass all if page_id is specified (comes from breadcrumb or previous button)
        if 'previous_page_id' in post:
            previous_page_or_question_id = int(post['previous_page_id'])
            new_previous_id = survey_sudo._get_next_page_or_question(answer_sudo, previous_page_or_question_id, go_back=True).id
            page_or_question = request.env['survey.question'].sudo().browse(previous_page_or_question_id)
            data.update({
                page_or_question_key: page_or_question,
                'previous_page_id': new_previous_id,
                'has_answered': answer_sudo.user_input_line_ids.filtered(lambda line: line.question_id.id == new_previous_id),
                'can_go_back': survey_sudo._can_go_back(answer_sudo, page_or_question),
            })
            return data

        if answer_sudo.state == 'in_progress':
            if answer_sudo.is_session_answer:
                next_page_or_question = survey_sudo.session_question_id
            else:
                next_page_or_question = survey_sudo._get_next_page_or_question(
                    answer_sudo,
                    answer_sudo.last_displayed_page_id.id if answer_sudo.last_displayed_page_id else 0)

                if next_page_or_question:
                    data.update({
                        'survey_last': survey_sudo._is_last_page_or_question(answer_sudo, next_page_or_question)
                    })

            if answer_sudo.is_session_answer and next_page_or_question.is_time_limited:
                data.update({
                    'timer_start': survey_sudo.session_question_start_time.isoformat(),
                    'time_limit_minutes': next_page_or_question.time_limit / 60
                })

            data.update({
                page_or_question_key: next_page_or_question,
                'has_answered': answer_sudo.user_input_line_ids.filtered(lambda line: line.question_id == next_page_or_question),
                'can_go_back': survey_sudo._can_go_back(answer_sudo, next_page_or_question),
            })
            if survey_sudo.questions_layout != 'one_page':
                data.update({
                    'previous_page_id': survey_sudo._get_next_page_or_question(answer_sudo, next_page_or_question.id, go_back=True).id
                })
        elif answer_sudo.state == 'done' or answer_sudo.survey_time_limit_reached:
            # Display success message
            # if survey_sudo.scoring_type != 'no_scoring':
            #     data = http.request.env['slide.channel.partner'].sudo().search([('completeattend', '=', True), ('custom_user_id', '=', request.env.user.id)],limit=1)._fullcompletenew()
            #     print(data, "nullllllllllllllllllllllllll")
            return self._prepare_survey_finished_values(survey_sudo, answer_sudo)

        return data

    def _generate_report(self, user_input, download=True):
        surveynew = request.env['survey.user_input'].sudo().search([('id','=',user_input.id)])
        print(surveynew.survey_id.certification_mail_template_id.report_template.report_name,"ssnew")
        testingsurvey = surveynew.survey_id.certification_mail_template_id.report_template
        report = testingsurvey._render_qweb_pdf([user_input.id], data={'report_type': 'pdf'})[0]

        report_content_disposition = content_disposition('Certification.pdf')
        if not download:
            content_split = report_content_disposition.split(';')
            content_split[0] = 'inline'
            report_content_disposition = ';'.join(content_split)

        return request.make_response(report, headers=[
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(report)),
            ('Content-Disposition', report_content_disposition),
        ])

# class CustomWebsite(Website):
#     @http.route()
#     def index(self, *args, **kw):
#         response = super(CustomWebsite, self).index(*args, **kw)
#         url = '/slides'
#
#
#         return http.local_redirect('/slides')


class CustomWebsiteSlides(WebsiteSlides):

    @http.route('/slides/all/lang/filter', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_language_filer(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        User = request.env['res.users']
        if post.get('filtered_language'):
            filter_lang = post.get('filtered_language')
            request.env.user.filter_lang_from_website = filter_lang
        else:
            filter_lang = request.env.user.filter_lang_from_website
        channels_ids = request.env['slide.channel'].search(domain, order=order)
        channels_lst = []
        for channel in channels_ids:
            if channel.custom_visibility == 'private':
                user_lst = []
                for channel_partner in channel.sudo().channel_partner_ids:
                    user = request.env['res.users'].search([('partner_id', '=', channel_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        user_lst.append(user.id)
                if request.env.user.id in user_lst:
                    channels_lst.append(channel.id)

            elif channel.custom_visibility == 'semi_public':
                user_lst = []
                for channel_user in channel.sudo().nominated_user_ids:
                    user_lst.append(channel_user.id)
                if request.env.user.id in user_lst:
                    channels_lst.append(channel.id)
            else:
                channels_lst.append(channel.id)

        channels_ids1 = request.env['slide.channel'].browse(channels_lst)
        final_channel_lst = []
        for channel1 in channels_ids1:
            if channel1.lang_values == filter_lang:
                final_channel_lst.append(channel1.id)

        channels = request.env['slide.channel'].browse(final_channel_lst)

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)
        category_details = request.env['course.category'].sudo().search([])

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'category_details': category_details,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
            # 'categ_val_bool':True,
            'filter_lang_val_bool': True,
            'filter_lang_selected': filter_lang
            # 'filter_categ_id':category_id.name,
        })

        return request.render('website_slides.courses_all', values)
    
    @http.route('/slides/all/lang/pwa/filter', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_language_pwa_filer(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        User = request.env['res.users']
        if post.get('filtered_language'):
            filter_lang = post.get('filtered_language')
            request.env.user.filter_lang_from_website = filter_lang
        else:
            filter_lang = request.env.user.filter_lang_from_website
        channels_ids = request.env['slide.channel'].search(domain, order=order)
        channels_lst = []
        for channel in channels_ids:
            if channel.custom_visibility == 'private':
                user_lst = []
                for channel_partner in channel.sudo().channel_partner_ids:
                    user = request.env['res.users'].search([('partner_id', '=', channel_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        user_lst.append(user.id)
                if request.env.user.id in user_lst:
                    channels_lst.append(channel.id)

            elif channel.custom_visibility == 'semi_public':
                user_lst = []
                for channel_user in channel.sudo().nominated_user_ids:
                    user_lst.append(channel_user.id)
                if request.env.user.id in user_lst:
                    channels_lst.append(channel.id)
            else:
                channels_lst.append(channel.id)

        channels_ids1 = request.env['slide.channel'].browse(channels_lst)
        final_channel_lst = []
        for channel1 in channels_ids1:
            if channel1.lang_values == filter_lang:
                final_channel_lst.append(channel1.id)

        channels = request.env['slide.channel'].browse(final_channel_lst)

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)
        category_details = request.env['course.category'].sudo().search([])

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'category_details': category_details,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
            # 'categ_val_bool':True,
            'filter_lang_val_bool': True,
            'filter_lang_selected': filter_lang
            # 'filter_categ_id':category_id.name,
        })

        return request.render('ecom_lms.lms_pwa_all_courses_filter', values)

    @http.route('/slides/all/category', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_all_category(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        User = request.env['res.users']
        if post.get('category_id'):
            categ_id1 = post.get('category_id')
            request.env.user.categ_from_website = categ_id1
        else:
            categ_id1 = request.env.user.categ_from_website
        categ_new_id1 = categ_id1.split('(')
        categ_id2 = categ_new_id1[1].split(',')
        category_id = request.env['course.category'].sudo().search([('id', '=', int(categ_id2[0]))])

        channels_ids = request.env['slide.channel'].search(domain, order=order)
        channels_lst = []
        for channel in channels_ids:
            if channel.custom_visibility == 'private':
                user_lst = []
                for channel_partner in channel.sudo().channel_partner_ids:
                    user = request.env['res.users'].search([('partner_id', '=', channel_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        user_lst.append(user.id)
                if request.env.user.id in user_lst:
                    channels_lst.append(channel.id)

            elif channel.custom_visibility == 'semi_public':
                user_lst = []
                for channel_user in channel.sudo().nominated_user_ids:
                    user_lst.append(channel_user.id)
                if request.env.user.id in user_lst:
                    channels_lst.append(channel.id)
            else:
                channels_lst.append(channel.id)

        channels_ids1 = request.env['slide.channel'].browse(channels_lst)
        final_channel_lst = []
        for channel1 in channels_ids1:
            if channel1.course_category_id.id == category_id.id:
                final_channel_lst.append(channel1.id)

        channels = request.env['slide.channel'].browse(final_channel_lst)
        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)
        category_details = request.env['course.category'].sudo().search([])

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'category_details': category_details,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
            'categ_val_bool': True,
            'filter_categ_id': category_id.name,
        })

        return request.render('website_slides.courses_all', values)
    
    @http.route('/slides/all/pwa/category', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_all_pwa_category(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        User = request.env['res.users']
        if post.get('category_id'):
            categ_id1 = post.get('category_id')
            request.env.user.categ_from_website = categ_id1
        else:
            categ_id1 = request.env.user.categ_from_website
        categ_new_id1 = categ_id1.split('(')
        categ_id2 = categ_new_id1[1].split(',')
        category_id = request.env['course.category'].sudo().search([('id', '=', int(categ_id2[0]))])

        channels_ids = request.env['slide.channel'].search(domain, order=order)
        channels_lst = []
        for channel in channels_ids:
            if channel.custom_visibility == 'private':
                user_lst = []
                for channel_partner in channel.sudo().channel_partner_ids:
                    user = request.env['res.users'].search([('partner_id', '=', channel_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        user_lst.append(user.id)
                if request.env.user.id in user_lst:
                    channels_lst.append(channel.id)

            elif channel.custom_visibility == 'semi_public':
                user_lst = []
                for channel_user in channel.sudo().nominated_user_ids:
                    user_lst.append(channel_user.id)
                if request.env.user.id in user_lst:
                    channels_lst.append(channel.id)
            else:
                channels_lst.append(channel.id)

        channels_ids1 = request.env['slide.channel'].browse(channels_lst)
        final_channel_lst = []
        for channel1 in channels_ids1:
            if channel1.course_category_id.id == category_id.id:
                final_channel_lst.append(channel1.id)

        channels = request.env['slide.channel'].browse(final_channel_lst)
        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)
        category_details = request.env['course.category'].sudo().search([])

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'category_details': category_details,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
            'categ_val_bool': True,
            'filter_categ_id': category_id.name,
        })

        return request.render('ecom_lms.lms_pwa_all_courses_filter', values)

    @http.route('/home-region-wise/most-courses', type='http', auth="public", website=True, sitemap=True)
    def home_region_most_courses(self, slide_type=None, my=False, **post):
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)
        region_val = ''
        if post.get('home_region'):
            request.env.user.home_region_from_website = post.get('home_region')
            region_val = post.get('home_region')
        else:
            region_val = request.env.user.home_region_from_website

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        region_user_ids = request.env['res.users'].sudo().search([('region', '=', region_val)])
        course_lst = []
        for user in region_user_ids:
            channel_partner_ids = request.env['slide.channel.partner'].sudo().search(
                [('partner_id', '=', user.partner_id.id), ('completion', '=', 100)])
            if channel_partner_ids:
                for channel_partner in channel_partner_ids:
                    if channel_partner.channel_id.id not in course_lst:
                        course_lst.append(channel_partner.channel_id.id)

        channels = request.env['slide.channel'].sudo().browse(course_lst)
        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('website_slides.courses_all', values)

    @http.route('/home/employee-with-most-certification', type='http', auth="public", website=True, sitemap=True)
    def home_employee_with_most_certification(self, slide_type=None, my=False, **post):
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        partner_lst = []
        user_input_ids = request.env['survey.user_input'].sudo().search([('scoring_success', '=', True)])
        if user_input_ids:
            for user_input in user_input_ids:
                if user_input.partner_id.id not in partner_lst:
                    partner_lst.append(user_input.partner_id.id)
        usr_lst = []
        if len(partner_lst) > 0:
            for partner in partner_lst:
                user_id = request.env['res.users'].sudo().search([('partner_id', '=', partner)], limit=1)
                if user_id:
                    if user_id not in usr_lst:
                        usr_lst.append(user_id.id)

        employees_details = request.env['res.users'].sudo().browse(usr_lst)
        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'employees_details': employees_details,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('ecom_lms.emp_with_most_certificate_template', values)

    @http.route('/home/employee-with-most-completed-course', type='http', auth="public", website=True, sitemap=True)
    def home_employee_with_most_completed_course(self, slide_type=None, my=False, **post):
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))
        partner_lst = []
        channel_partner_ids = request.env['slide.channel.partner'].sudo().search([('completion', '=', 100)])
        for channel_partner in channel_partner_ids:
            if channel_partner.partner_id.id not in partner_lst:
                partner_lst.append(channel_partner.partner_id.id)
        user_lst = []
        for partner in partner_lst:
            user_id = request.env['res.users'].sudo().search([('partner_id', '=', partner)], limit=1)
            if user_id:
                user_lst.append(user_id.id)

        users = request.env['res.users'].sudo().browse(user_lst)

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'top3_users': self._get_top3_users(),
            'employees_completed_details': users
        })

        return request.render('ecom_lms.emp_with_most_completed_course_template', values)

    @http.route('/slides/all', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        # domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my)
        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].search(domain, order=order)
        channels_lst = []
        for channel in channels_ids:
            if channel.custom_visibility == 'private':
                user_lst = []
                for channel_partner in channel.sudo().channel_partner_ids:
                    user = request.env['res.users'].search([('partner_id', '=', channel_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        user_lst.append(user.id)
                if request.env.user.id in user_lst:
                    channels_lst.append(channel.id)

            elif channel.custom_visibility == 'semi_public':
                user_lst = []
                for channel_user in channel.sudo().nominated_user_ids:
                    user_lst.append(channel_user.id)
                if request.env.user.id in user_lst:
                    channels_lst.append(channel.id)
            else:
                channels_lst.append(channel.id)

        channels = request.env['slide.channel'].browse(channels_lst)
        all_channels_values_ids = request.env['slide.channel'].sudo().browse(channels_lst)
        tags_like_searching = request.env['slide.channel.tag'].sudo().search([('name', 'ilike', post.get('search'))])
        name_relavant_channel_ids = request.env['slide.channel'].sudo().search([('name', 'ilike', post.get('search'))])
        tag_searched_channel_lst = []
        if post.get('search'):
            channels_values_ids = request.env['slide.channel'].sudo().browse(channels_lst)
            for channel_values_id in channels_values_ids:
                if channel_values_id.custom_tag_ids:
                    for custom_tag in channel_values_id.custom_tag_ids:
                        if custom_tag in tags_like_searching or channel_values_id in name_relavant_channel_ids:
                            if channel_values_id.id not in tag_searched_channel_lst:
                                tag_searched_channel_lst.append(channel_values_id.id)

                else:
                    if channel_values_id in name_relavant_channel_ids:
                        if channel_values_id.id not in tag_searched_channel_lst:
                            tag_searched_channel_lst.append(channel_values_id.id)
            channels = request.env['slide.channel'].sudo().browse(tag_searched_channel_lst)
        else:
            channels = request.env['slide.channel'].sudo().browse(channels_lst)

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        category_details = request.env['course.category'].sudo().search([])

        values = self._prepare_user_values(**post)
        published_channels = channels.filtered(lambda a: a.is_published)
        values.update({
            'channels': published_channels,
            'tag_groups': tag_groups,
            'category_details': category_details,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('website_slides.courses_all', values)
    
    
    
    @http.route('/slides/pwa/all', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_pwa_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        # domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my)
        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].search(domain, order=order)
        channels_lst = []
        for channel in channels_ids:
            if channel.custom_visibility == 'private':
                user_lst = []
                for channel_partner in channel.sudo().channel_partner_ids:
                    user = request.env['res.users'].search([('partner_id', '=', channel_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        user_lst.append(user.id)
                if request.env.user.id in user_lst:
                    channels_lst.append(channel.id)

            elif channel.custom_visibility == 'semi_public':
                user_lst = []
                for channel_user in channel.sudo().nominated_user_ids:
                    user_lst.append(channel_user.id)
                if request.env.user.id in user_lst:
                    channels_lst.append(channel.id)
            else:
                channels_lst.append(channel.id)

        channels = request.env['slide.channel'].browse(channels_lst)
        all_channels_values_ids = request.env['slide.channel'].sudo().browse(channels_lst)
        tags_like_searching = request.env['slide.channel.tag'].sudo().search([('name', 'ilike', post.get('search'))])
        name_relavant_channel_ids = request.env['slide.channel'].sudo().search([('name', 'ilike', post.get('search'))])
        tag_searched_channel_lst = []
        if post.get('search'):
            channels_values_ids = request.env['slide.channel'].sudo().browse(channels_lst)
            for channel_values_id in channels_values_ids:
                if channel_values_id.custom_tag_ids:
                    for custom_tag in channel_values_id.custom_tag_ids:
                        if custom_tag in tags_like_searching or channel_values_id in name_relavant_channel_ids:
                            if channel_values_id.id not in tag_searched_channel_lst:
                                tag_searched_channel_lst.append(channel_values_id.id)

                else:
                    if channel_values_id in name_relavant_channel_ids:
                        if channel_values_id.id not in tag_searched_channel_lst:
                            tag_searched_channel_lst.append(channel_values_id.id)
            channels = request.env['slide.channel'].sudo().browse(tag_searched_channel_lst)
        else:
            channels = request.env['slide.channel'].sudo().browse(channels_lst)

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)
        category_details = request.env['course.category'].sudo().search([])
        values = self._prepare_user_values(**post)
        published_channels = channels.filtered(lambda a: a.is_published)
        values.update({
            'channels': published_channels,
            'tag_groups': tag_groups,
            'category_details': category_details,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('ecom_lms.lms_pwa_all_courses_filter', values)

    @http.route('/my/certifications', type='http', auth="public", website=True, sitemap=True)
    def certificate_my(self, slide_type='certification', my=False, **post):
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)
        cr = request.env.cr
        cr.execute('SELECT id FROM survey_user_input where partner_id = %s and scoring_success = %s',
                   (request.env.user.partner_id.id, True,))
        survey_user_ids = cr.fetchall()
        # survey_user_ids= request.env['survey.user_input'].sudo().search([('partner_id','=',request.env.user.partner_id.id),('scoring_success','=',True)])
        servey_lst = []
        for certifications_val in survey_user_ids:
            certification_val = request.env['survey.user_input'].browse(certifications_val)
            if certification_val.survey_id.id not in servey_lst:
                servey_lst.append(certification_val.survey_id.id)
        certification_details = request.env['survey.survey'].sudo().browse(servey_lst)

        values = self._prepare_user_values(**post)
        values.update({
            'certification_details': certification_details,
            'top3_users': self._get_top3_users(),
        })

        return request.render('ecom_lms.certification_template_main', values)

    @http.route(['/certification/<model("survey.survey"):certification>'], type='http', auth="public", website=True)
    def channel_certification(self, certification, report_type=None, access_token=None, message=False, download=False,
                              **kw):
        if certification:
            user_input = request.env['survey.user_input'].sudo().search(
                [('survey_id', '=', certification.id), ('scoring_success', '=', True)], limit=1)
            return request.render('ecom_lms.ecom_survey_template_default', {
                'user_input': user_input
            })

    # @http.route([
    #     '/my/certifications/<model("survey.survey"):certification>',
    # ], type='http', auth="public", website=True, sitemap=sitemap_slide)
    # def channel_certification(self, certification,access_token=None,  category=None, tag=None, page=1, slide_type=None,report_type=None, uncategorized=False, sorting=None,
    #             search=None, **kw):
    #     """
    #     Will return all necessary data to display the requested slide_channel along with a possible category.
    #     """
    #
    #     if certification:
    #         payslip_sudo = self._document_check_access('survey.user_input', certification, access_token=access_token)
    #
    #         user_in= request.env['survey.user_input'].search([('survey_id','=',certification.id),('scoring_success','=',True)],limit=1)
    #         pdf = request.env.ref('survey.certification_report').sudo()._render_qweb_pdf([user_in.id])[0]
    #         print ("user_inuser_inuser_in",user_in)
    #         values = {
    #             'user_input':user_in,
    #         }
    #         if report_type in ('html', 'pdf', 'text'):
    #             a= request._show_report(model=user_sudo, report_type=report_type, report_ref='survey.certification_report_view_modern', download=download)
    #         # survey.user_input
    #             return request.render(a,values)

    @http.route('/slides/my/languages/slides/all', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_lang_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].search(domain, order=order)
        channels_lst = []
        for channel in channels_ids:
            if channel.custom_visibility == 'private':
                user_lst = []
                for channel_partner in channel.sudo().channel_partner_ids:
                    user = request.env['res.users'].search([('partner_id', '=', channel_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        user_lst.append(user.id)
                if request.env.user.id in user_lst:
                    channels_lst.append(channel.id)

            elif channel.custom_visibility == 'semi_public':
                user_lst = []
                for channel_user in channel.sudo().nominated_user_ids:
                    user_lst.append(channel_user.id)
                if request.env.user.id in user_lst:
                    channels_lst.append(channel.id)
            else:
                channels_lst.append(channel.id)

        channels = request.env['slide.channel'].browse(channels_lst)
        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('website_slides.courses_all', values)

    @http.route('/slides/assigned/all', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_assigned_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].search(domain, order=order)

        channels_lst = []
        for channels_assigned in channels_ids:
            attendee_user_lst = []
            # if channels_popular.custom_visibility=='private':
            for channels_partner in channels_assigned.sudo().channel_partner_ids:
                if channels_partner.completion != 100:
                    user = request.env['res.users'].search([('partner_id', '=', channels_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        attendee_user_lst.append(user.id)
            if request.env.user.id in attendee_user_lst:

                if channels_assigned.course_close_date:
                    date_now = datetime.now()
                    if date_now.date() <= channels_assigned.course_close_date.date():
                        if channels_assigned.custom_visibility == 'private':
                            channels_assigned_private_user_lst = []
                            for channels_assigned_private_partner in channels_assigned.sudo().channel_partner_ids:
                                private_user = request.env['res.users'].search(
                                    [('partner_id', '=', channels_assigned_private_partner.partner_id.id)], limit=1)
                                if private_user:
                                    channels_assigned_private_user_lst.append(private_user.id)
                            if request.env.user.id in channels_assigned_private_user_lst:
                                channels_lst.append(channels_assigned.id)

                        elif channels_assigned.custom_visibility == 'semi_public':
                            channels_assigned_semi_user_lst = []
                            for channels_assigned_semi_user in channels_assigned.sudo().nominated_user_ids:
                                channels_assigned_semi_user_lst.append(channels_assigned_semi_user.id)

                            if request.env.user.id in channels_assigned_semi_user_lst:
                                channels_lst.append(channels_assigned.id)
                        else:
                            channels_lst.append(channels_assigned.id)
                else:
                    if channels_assigned.custom_visibility == 'private':
                        channels_assigned_private_user_lst = []
                        for channels_assigned_private_partner in channels_assigned.sudo().channel_partner_ids:
                            private_user = request.env['res.users'].search(
                                [('partner_id', '=', channels_assigned_private_partner.partner_id.id)], limit=1)
                            if private_user:
                                channels_assigned_private_user_lst.append(private_user.id)
                        if request.env.user.id in channels_assigned_private_user_lst:
                            channels_lst.append(channels_assigned.id)

                    elif channels_assigned.custom_visibility == 'semi_public':
                        channels_assigned_semi_user_lst = []
                        for channels_assigned_semi_user in channels_assigned.sudo().nominated_user_ids:
                            channels_assigned_semi_user_lst.append(channels_assigned_semi_user.id)

                        if request.env.user.id in channels_assigned_semi_user_lst:
                            channels_lst.append(channels_assigned.id)
                    else:
                        channels_lst.append(channels_assigned.id)

        # channels_assign=  request.env['slide.channel'].browse(channels_assigned_lst)

        filtered_lst = []
        channels_obj = request.env['slide.channel'].browse(channels_lst)

        for val in channels_obj:
            if val.course_close_date:
                if datetime.now() <= val.course_close_date:
                    filtered_lst.append(val.id)

        channels = request.env['slide.channel'].browse(filtered_lst)

        # channels=  request.env['slide.channel'].browse(channels_lst)
        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('website_slides.courses_all', values)


    @http.route('/slides/pwa/assigned/all', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_assigned_pwa_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].search(domain, order=order)

        channels_lst = []
        for channels_assigned in channels_ids:
            attendee_user_lst = []
            # if channels_popular.custom_visibility=='private':
            for channels_partner in channels_assigned.sudo().channel_partner_ids:
                if channels_partner.completion != 100:
                    user = request.env['res.users'].search([('partner_id', '=', channels_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        attendee_user_lst.append(user.id)
            if request.env.user.id in attendee_user_lst:

                if channels_assigned.course_close_date:
                    date_now = datetime.now()
                    if date_now.date() <= channels_assigned.course_close_date.date():
                        if channels_assigned.custom_visibility == 'private':
                            channels_assigned_private_user_lst = []
                            for channels_assigned_private_partner in channels_assigned.sudo().channel_partner_ids:
                                private_user = request.env['res.users'].search(
                                    [('partner_id', '=', channels_assigned_private_partner.partner_id.id)], limit=1)
                                if private_user:
                                    channels_assigned_private_user_lst.append(private_user.id)
                            if request.env.user.id in channels_assigned_private_user_lst:
                                channels_lst.append(channels_assigned.id)

                        elif channels_assigned.custom_visibility == 'semi_public':
                            channels_assigned_semi_user_lst = []
                            for channels_assigned_semi_user in channels_assigned.sudo().nominated_user_ids:
                                channels_assigned_semi_user_lst.append(channels_assigned_semi_user.id)

                            if request.env.user.id in channels_assigned_semi_user_lst:
                                channels_lst.append(channels_assigned.id)
                        else:
                            channels_lst.append(channels_assigned.id)
                else:
                    if channels_assigned.custom_visibility == 'private':
                        channels_assigned_private_user_lst = []
                        for channels_assigned_private_partner in channels_assigned.sudo().channel_partner_ids:
                            private_user = request.env['res.users'].search(
                                [('partner_id', '=', channels_assigned_private_partner.partner_id.id)], limit=1)
                            if private_user:
                                channels_assigned_private_user_lst.append(private_user.id)
                        if request.env.user.id in channels_assigned_private_user_lst:
                            channels_lst.append(channels_assigned.id)

                    elif channels_assigned.custom_visibility == 'semi_public':
                        channels_assigned_semi_user_lst = []
                        for channels_assigned_semi_user in channels_assigned.sudo().nominated_user_ids:
                            channels_assigned_semi_user_lst.append(channels_assigned_semi_user.id)

                        if request.env.user.id in channels_assigned_semi_user_lst:
                            channels_lst.append(channels_assigned.id)
                    else:
                        channels_lst.append(channels_assigned.id)

        # channels_assign=  request.env['slide.channel'].browse(channels_assigned_lst)

        filtered_lst = []
        channels_obj = request.env['slide.channel'].browse(channels_lst)

        for val in channels_obj:
            if val.course_close_date:
                if datetime.now() <= val.course_close_date:
                    filtered_lst.append(val.id)

        channels = request.env['slide.channel'].browse(filtered_lst)

        # channels=  request.env['slide.channel'].browse(channels_lst)
        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('ecom_lms.channel_pwa_view_all', values)
    
    


    @http.route('/slides/featured/all', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_featured_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].sudo().search(domain, order=order)

        channels_lst = []
        for channels_featured in channels_ids:
            featured_user_lst = []
            if channels_featured.is_featured and channels_featured.featured_group_id:
                if channels_featured.featured_group_id in request.env.user.groups_id:
                    if channels_featured.custom_visibility == 'private':
                        channels_featured_private_user_lst = []
                        for channels_featured_private_partner in channels_featured.sudo().channel_partner_ids:
                            private_user = request.env['res.users'].search(
                                [('partner_id', '=', channels_featured_private_partner.partner_id.id)], limit=1)
                            if private_user:
                                channels_featured_private_user_lst.append(private_user.id)
                        if request.env.user.id in channels_featured_private_user_lst:
                            channels_lst.append(channels_featured.id)

                    elif channels_featured.custom_visibility == 'semi_public':
                        channels_featured_semi_user_lst = []
                        for channels_featured_semi_user in channels_featured.sudo().nominated_user_ids:
                            channels_featured_semi_user_lst.append(channels_featured_semi_user.id)

                        if request.env.user.id in channels_featured_semi_user_lst:
                            channels_lst.append(channels_featured.id)
                    else:
                        channels_lst.append(channels_featured.id)

        filtered_lst = []
        channels_obj = request.env['slide.channel'].browse(channels_lst)

        for val in channels_obj:
            if val.course_close_date:
                if datetime.now() <= val.course_close_date:
                    filtered_lst.append(val.id)

        channels = request.env['slide.channel'].browse(filtered_lst)

        # channels=  request.env['slide.channel'].browse(channels_lst)
        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('website_slides.courses_all', values)
    
    @http.route('/slides/featured/pwa/all', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_featured_pwa_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].sudo().search(domain, order=order)

        channels_lst = []
        for channels_featured in channels_ids:
            featured_user_lst = []
            if channels_featured.is_featured and channels_featured.featured_group_id:
                if channels_featured.featured_group_id in request.env.user.groups_id:
                    if channels_featured.custom_visibility == 'private':
                        channels_featured_private_user_lst = []
                        for channels_featured_private_partner in channels_featured.sudo().channel_partner_ids:
                            private_user = request.env['res.users'].search(
                                [('partner_id', '=', channels_featured_private_partner.partner_id.id)], limit=1)
                            if private_user:
                                channels_featured_private_user_lst.append(private_user.id)
                        if request.env.user.id in channels_featured_private_user_lst:
                            channels_lst.append(channels_featured.id)

                    elif channels_featured.custom_visibility == 'semi_public':
                        channels_featured_semi_user_lst = []
                        for channels_featured_semi_user in channels_featured.sudo().nominated_user_ids:
                            channels_featured_semi_user_lst.append(channels_featured_semi_user.id)

                        if request.env.user.id in channels_featured_semi_user_lst:
                            channels_lst.append(channels_featured.id)
                    else:
                        channels_lst.append(channels_featured.id)

        filtered_lst = []
        channels_obj = request.env['slide.channel'].browse(channels_lst)

        for val in channels_obj:
            if val.course_close_date:
                if datetime.now() <= val.course_close_date:
                    filtered_lst.append(val.id)

        channels = request.env['slide.channel'].browse(filtered_lst)

        # channels=  request.env['slide.channel'].browse(channels_lst)
        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('ecom_lms.channel_pwa_view_all', values)

    @http.route('/slides/suggested/all', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_suggested_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].sudo().search(domain, order=order)

        channels_suggested_lst = []
        for channels_suggested in channels_ids:
            if channels_suggested.custom_visibility == 'semi_public':
                suggested_user_lst = []
                for channels_partner in channels_suggested.sudo().channel_partner_ids:
                    user = request.env['res.users'].search([('partner_id', '=', channels_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        suggested_user_lst.append(user.id)
                if request.env.user.id not in suggested_user_lst and request.env.user in channels_suggested.nominated_user_ids:
                    channels_suggested_lst.append(channels_suggested.id)

        completed_course_list = []
        for completed_course in channels_ids:
            if completed_course.custom_visibility != 'semi_public':

                for channels_partner in completed_course.sudo().channel_partner_ids:
                    if channels_partner.completion == 100:
                        if completed_course.id not in completed_course_list:
                            completed_course_list.append(completed_course.id)
        channels_comp_suggested_lst = []
        for channels_completed_suggested in completed_course_list:
            channel_comp_suggested = request.env['slide.channel'].browse(channels_completed_suggested)
            suggested_comp_user_lst = []
            for partner_val in channel_comp_suggested.sudo().channel_partner_ids:
                user_val = request.env['res.users'].search([('partner_id', '=', partner_val.partner_id.id)], limit=1)
                if user_val:
                    suggested_comp_user_lst.append(user_val.id)
            if request.env.user.id not in suggested_comp_user_lst:
                if channel_comp_suggested.custom_visibility == 'private':
                    channel_comp_suggested_private_user_lst = []
                    for channel_comp_suggested_private_partner in channel_comp_suggested.sudo().channel_partner_ids:
                        private_user = request.env['res.users'].search(
                            [('partner_id', '=', channel_comp_suggested_private_partner.partner_id.id)], limit=1)
                        if private_user:
                            channel_comp_suggested_private_user_lst.append(private_user.id)
                    if request.env.user.id in channel_comp_suggested_private_user_lst:
                        channels_comp_suggested_lst.append(channel_comp_suggested.id)

                elif channel_comp_suggested.custom_visibility == 'semi_public':
                    channel_comp_suggested_semi_user_lst = []
                    for channel_comp_suggested_semi_user in channel_comp_suggested.sudo().nominated_user_ids:
                        channel_comp_suggested_semi_user_lst.append(channel_comp_suggested_semi_user.id)

                    if request.env.user.id in channel_comp_suggested_semi_user_lst:
                        channels_comp_suggested_lst.append(channel_comp_suggested.id)
                else:
                    channels_comp_suggested_lst.append(channel_comp_suggested.id)

        just_started_courses = []
        recent_start_courses_lst = []
        today_date = datetime.now()
        today_only_date = today_date.date()
        started_courses_ids = request.env['slide.channel.partner'].sudo().search([])
        for started in started_courses_ids:
            if started.create_date:
                if started.create_date.date() == today_only_date:
                    just_started_courses.append(started.channel_id.id)

        if len(just_started_courses) > 0:
            for just_started in just_started_courses:
                started_user_lst = []
                channel_just_started = request.env['slide.channel'].browse(just_started)
                for just_start in channel_just_started.sudo().channel_partner_ids:
                    user_val = request.env['res.users'].search([('partner_id', '=', just_start.partner_id.id)], limit=1)
                    if user_val:
                        started_user_lst.append(user_val.id)
                if request.env.user.id not in started_user_lst:
                    if channel_just_started.custom_visibility == 'private':
                        channel_just_started_private_user_lst = []
                        for channel_just_started_private_partner in channel_just_started.sudo().channel_partner_ids:
                            private_user = request.env['res.users'].search(
                                [('partner_id', '=', channel_just_started_private_partner.partner_id.id)], limit=1)
                            if private_user:
                                channel_just_started_private_user_lst.append(private_user.id)
                        if request.env.user.id in channel_just_started_private_user_lst:
                            recent_start_courses_lst.append(channel_just_started.id)

                    elif channel_just_started.custom_visibility == 'semi_public':
                        channel_just_started_semi_user_lst = []
                        for channel_just_started_semi_user in channel_just_started.sudo().nominated_user_ids:
                            channel_just_started_semi_user_lst.append(channel_just_started_semi_user.id)

                        if request.env.user.id in channel_just_started_semi_user_lst:
                            recent_start_courses_lst.append(channel_just_started.id)
                    else:
                        recent_start_courses_lst.append(channel_just_started.id)

        interested_course_lst = []
        for interested_course in channels_ids:
            if interested_course.course_category_id in request.env.user.topic_of_interest_ids:
                interested_user_lst = []
                if interested_course.sudo().channel_partner_ids:
                    for partner_val1 in interested_course.sudo().channel_partner_ids:
                        user_val1 = request.env['res.users'].search([('partner_id', '=', partner_val1.partner_id.id)],
                                                                    limit=1)
                        if user_val1:
                            interested_user_lst.append(user_val1.id)

                if request.env.user.id not in interested_user_lst:
                    if interested_course.custom_visibility == 'private':
                        interested_course_private_user_lst = []
                        for interested_course_private_partner in interested_course.sudo().channel_partner_ids:
                            private_user = request.env['res.users'].search(
                                [('partner_id', '=', interested_course_private_partner.partner_id.id)], limit=1)
                            if private_user:
                                interested_course_private_user_lst.append(private_user.id)
                        if request.env.user.id in interested_course_private_user_lst:
                            interested_course_lst.append(interested_course.id)

                    elif interested_course.custom_visibility == 'semi_public':
                        interested_course_semi_user_lst = []
                        for interested_course_semi_user in interested_course.sudo().nominated_user_ids:
                            interested_course_semi_user_lst.append(interested_course_semi_user.id)

                        if request.env.user.id in interested_course_semi_user_lst:
                            interested_course_lst.append(interested_course.id)
                    else:
                        interested_course_lst.append(interested_course.id)

        final_suggested_lst = channels_suggested_lst + channels_comp_suggested_lst + recent_start_courses_lst + interested_course_lst
        final_suggested_lst = list(set(final_suggested_lst))

        filtered_lst = []
        channels_obj = request.env['slide.channel'].browse(final_suggested_lst)

        for val in channels_obj:
            if val.course_close_date:
                if datetime.now() <= val.course_close_date:
                    filtered_lst.append(val.id)

        channels = request.env['slide.channel'].browse(filtered_lst)

        # channels=  request.env['slide.channel'].browse(final_suggested_lst)
        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('website_slides.courses_all', values)
    
    @http.route('/slides/suggested/pwa/all', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_suggested_pwa_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].sudo().search(domain, order=order)

        channels_suggested_lst = []
        for channels_suggested in channels_ids:
            if channels_suggested.custom_visibility == 'semi_public':
                suggested_user_lst = []
                for channels_partner in channels_suggested.sudo().channel_partner_ids:
                    user = request.env['res.users'].search([('partner_id', '=', channels_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        suggested_user_lst.append(user.id)
                if request.env.user.id not in suggested_user_lst and request.env.user in channels_suggested.nominated_user_ids:
                    channels_suggested_lst.append(channels_suggested.id)

        completed_course_list = []
        for completed_course in channels_ids:
            if completed_course.custom_visibility != 'semi_public':

                for channels_partner in completed_course.sudo().channel_partner_ids:
                    if channels_partner.completion == 100:
                        if completed_course.id not in completed_course_list:
                            completed_course_list.append(completed_course.id)
        channels_comp_suggested_lst = []
        for channels_completed_suggested in completed_course_list:
            channel_comp_suggested = request.env['slide.channel'].browse(channels_completed_suggested)
            suggested_comp_user_lst = []
            for partner_val in channel_comp_suggested.sudo().channel_partner_ids:
                user_val = request.env['res.users'].search([('partner_id', '=', partner_val.partner_id.id)], limit=1)
                if user_val:
                    suggested_comp_user_lst.append(user_val.id)
            if request.env.user.id not in suggested_comp_user_lst:
                if channel_comp_suggested.custom_visibility == 'private':
                    channel_comp_suggested_private_user_lst = []
                    for channel_comp_suggested_private_partner in channel_comp_suggested.sudo().channel_partner_ids:
                        private_user = request.env['res.users'].search(
                            [('partner_id', '=', channel_comp_suggested_private_partner.partner_id.id)], limit=1)
                        if private_user:
                            channel_comp_suggested_private_user_lst.append(private_user.id)
                    if request.env.user.id in channel_comp_suggested_private_user_lst:
                        channels_comp_suggested_lst.append(channel_comp_suggested.id)

                elif channel_comp_suggested.custom_visibility == 'semi_public':
                    channel_comp_suggested_semi_user_lst = []
                    for channel_comp_suggested_semi_user in channel_comp_suggested.sudo().nominated_user_ids:
                        channel_comp_suggested_semi_user_lst.append(channel_comp_suggested_semi_user.id)

                    if request.env.user.id in channel_comp_suggested_semi_user_lst:
                        channels_comp_suggested_lst.append(channel_comp_suggested.id)
                else:
                    channels_comp_suggested_lst.append(channel_comp_suggested.id)

        just_started_courses = []
        recent_start_courses_lst = []
        today_date = datetime.now()
        today_only_date = today_date.date()
        started_courses_ids = request.env['slide.channel.partner'].sudo().search([])
        for started in started_courses_ids:
            if started.create_date:
                if started.create_date.date() == today_only_date:
                    just_started_courses.append(started.channel_id.id)

        if len(just_started_courses) > 0:
            for just_started in just_started_courses:
                started_user_lst = []
                channel_just_started = request.env['slide.channel'].browse(just_started)
                for just_start in channel_just_started.sudo().channel_partner_ids:
                    user_val = request.env['res.users'].search([('partner_id', '=', just_start.partner_id.id)], limit=1)
                    if user_val:
                        started_user_lst.append(user_val.id)
                if request.env.user.id not in started_user_lst:
                    if channel_just_started.custom_visibility == 'private':
                        channel_just_started_private_user_lst = []
                        for channel_just_started_private_partner in channel_just_started.sudo().channel_partner_ids:
                            private_user = request.env['res.users'].search(
                                [('partner_id', '=', channel_just_started_private_partner.partner_id.id)], limit=1)
                            if private_user:
                                channel_just_started_private_user_lst.append(private_user.id)
                        if request.env.user.id in channel_just_started_private_user_lst:
                            recent_start_courses_lst.append(channel_just_started.id)

                    elif channel_just_started.custom_visibility == 'semi_public':
                        channel_just_started_semi_user_lst = []
                        for channel_just_started_semi_user in channel_just_started.sudo().nominated_user_ids:
                            channel_just_started_semi_user_lst.append(channel_just_started_semi_user.id)

                        if request.env.user.id in channel_just_started_semi_user_lst:
                            recent_start_courses_lst.append(channel_just_started.id)
                    else:
                        recent_start_courses_lst.append(channel_just_started.id)

        interested_course_lst = []
        for interested_course in channels_ids:
            if interested_course.course_category_id in request.env.user.topic_of_interest_ids:
                interested_user_lst = []
                if interested_course.sudo().channel_partner_ids:
                    for partner_val1 in interested_course.sudo().channel_partner_ids:
                        user_val1 = request.env['res.users'].search([('partner_id', '=', partner_val1.partner_id.id)],
                                                                    limit=1)
                        if user_val1:
                            interested_user_lst.append(user_val1.id)

                if request.env.user.id not in interested_user_lst:
                    if interested_course.custom_visibility == 'private':
                        interested_course_private_user_lst = []
                        for interested_course_private_partner in interested_course.sudo().channel_partner_ids:
                            private_user = request.env['res.users'].search(
                                [('partner_id', '=', interested_course_private_partner.partner_id.id)], limit=1)
                            if private_user:
                                interested_course_private_user_lst.append(private_user.id)
                        if request.env.user.id in interested_course_private_user_lst:
                            interested_course_lst.append(interested_course.id)

                    elif interested_course.custom_visibility == 'semi_public':
                        interested_course_semi_user_lst = []
                        for interested_course_semi_user in interested_course.sudo().nominated_user_ids:
                            interested_course_semi_user_lst.append(interested_course_semi_user.id)

                        if request.env.user.id in interested_course_semi_user_lst:
                            interested_course_lst.append(interested_course.id)
                    else:
                        interested_course_lst.append(interested_course.id)

        final_suggested_lst = channels_suggested_lst + channels_comp_suggested_lst + recent_start_courses_lst + interested_course_lst
        final_suggested_lst = list(set(final_suggested_lst))

        filtered_lst = []
        channels_obj = request.env['slide.channel'].browse(final_suggested_lst)

        for val in channels_obj:
            if val.course_close_date:
                if datetime.now() <= val.course_close_date:
                    filtered_lst.append(val.id)

        channels = request.env['slide.channel'].browse(filtered_lst)

        # channels=  request.env['slide.channel'].browse(final_suggested_lst)
        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('ecom_lms.channel_pwa_view_all', values)

    @http.route('/slides/resumed/all', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_resumed_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].search(domain, order=order)

        channels_lst = []
        for channels_resumed in channels_ids:
            channels_resumed_user_lst = []
            # if channels_popular.custom_visibility=='private':
            for channels_resumed_partner in channels_resumed.sudo().channel_partner_ids:
                if channels_resumed_partner.completion < 100 and channels_resumed_partner.completion > 0:
                    user = request.env['res.users'].search(
                        [('partner_id', '=', channels_resumed_partner.partner_id.id)], limit=1)
                    if user:
                        channels_resumed_user_lst.append(user.id)
            if request.env.user.id in channels_resumed_user_lst:
                date_now = datetime.now()
                if channels_resumed.course_close_date:
                    if date_now.date() <= channels_resumed.course_close_date.date():
                        if channels_resumed.custom_visibility == 'private':
                            channels_resumed_private_user_lst = []
                            for channels_resumed_private_partner in channels_resumed.sudo().channel_partner_ids:
                                private_user = request.env['res.users'].search(
                                    [('partner_id', '=', channels_resumed_private_partner.partner_id.id)], limit=1)
                                if private_user:
                                    channels_resumed_private_user_lst.append(private_user.id)
                            if request.env.user.id in channels_resumed_private_user_lst:
                                channels_lst.append(channels_resumed.id)

                        elif channels_resumed.custom_visibility == 'semi_public':
                            channels_resumed_semi_user_lst = []
                            for channels_resumed_semi_user in channels_resumed.sudo().nominated_user_ids:
                                channels_resumed_semi_user_lst.append(channels_resumed_semi_user.id)

                            if request.env.user.id in channels_resumed_semi_user_lst:
                                channels_lst.append(channels_resumed.id)
                        else:
                            channels_lst.append(channels_resumed.id)

                else:

                    if channels_resumed.custom_visibility == 'private':
                        channels_resumed_private_user_lst = []
                        for channels_resumed_private_partner in channels_resumed.sudo().channel_partner_ids:
                            private_user = request.env['res.users'].search(
                                [('partner_id', '=', channels_resumed_private_partner.partner_id.id)], limit=1)
                            if private_user:
                                channels_resumed_private_user_lst.append(private_user.id)
                        if request.env.user.id in channels_resumed_private_user_lst:
                            channels_lst.append(channels_resumed.id)

                    elif channels_resumed.custom_visibility == 'semi_public':
                        channels_resumed_semi_user_lst = []
                        for channels_resumed_semi_user in channels_resumed.sudo().nominated_user_ids:
                            channels_resumed_semi_user_lst.append(channels_resumed_semi_user.id)

                        if request.env.user.id in channels_resumed_semi_user_lst:
                            channels_lst.append(channels_resumed.id)
                    else:
                        channels_lst.append(channels_resumed.id)

        filtered_lst = []
        channels_obj = request.env['slide.channel'].browse(channels_lst)

        for val in channels_obj:
            if val.course_close_date:
                if datetime.now() <= val.course_close_date:
                    filtered_lst.append(val.id)

        channels = request.env['slide.channel'].sudo().browse(filtered_lst)

        # channels=  request.env['slide.channel'].sudo().browse(channels_lst)
        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('website_slides.courses_all', values)
    
    @http.route('/slides/resumed/pwa/all', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_resumed_pwa_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].search(domain, order=order)

        channels_lst = []
        for channels_resumed in channels_ids:
            channels_resumed_user_lst = []
            # if channels_popular.custom_visibility=='private':
            for channels_resumed_partner in channels_resumed.sudo().channel_partner_ids:
                if channels_resumed_partner.completion < 100 and channels_resumed_partner.completion > 0:
                    user = request.env['res.users'].search([('partner_id', '=', channels_resumed_partner.partner_id.id)], limit=1)
                    if user:
                        channels_resumed_user_lst.append(user.id)
            if request.env.user.id in channels_resumed_user_lst:
                date_now = datetime.now()
                if channels_resumed.course_close_date:
                    if date_now.date() <= channels_resumed.course_close_date.date():
                        if channels_resumed.custom_visibility == 'private':
                            channels_resumed_private_user_lst = []
                            for channels_resumed_private_partner in channels_resumed.sudo().channel_partner_ids:
                                private_user = request.env['res.users'].search([('partner_id', '=', channels_resumed_private_partner.partner_id.id)], limit=1)
                                if private_user:
                                    channels_resumed_private_user_lst.append(private_user.id)
                            if request.env.user.id in channels_resumed_private_user_lst:
                                channels_lst.append(channels_resumed.id)

                        elif channels_resumed.custom_visibility == 'semi_public':
                            channels_resumed_semi_user_lst = []
                            for channels_resumed_semi_user in channels_resumed.sudo().nominated_user_ids:
                                channels_resumed_semi_user_lst.append(channels_resumed_semi_user.id)

                            if request.env.user.id in channels_resumed_semi_user_lst:
                                channels_lst.append(channels_resumed.id)
                        else:
                            channels_lst.append(channels_resumed.id)

                else:

                    if channels_resumed.custom_visibility == 'private':
                        channels_resumed_private_user_lst = []
                        for channels_resumed_private_partner in channels_resumed.sudo().channel_partner_ids:
                            private_user = request.env['res.users'].search([('partner_id', '=', channels_resumed_private_partner.partner_id.id)], limit=1)
                            if private_user:
                                channels_resumed_private_user_lst.append(private_user.id)
                        if request.env.user.id in channels_resumed_private_user_lst:
                            channels_lst.append(channels_resumed.id)

                    elif channels_resumed.custom_visibility == 'semi_public':
                        channels_resumed_semi_user_lst = []
                        for channels_resumed_semi_user in channels_resumed.sudo().nominated_user_ids:
                            channels_resumed_semi_user_lst.append(channels_resumed_semi_user.id)

                        if request.env.user.id in channels_resumed_semi_user_lst:
                            channels_lst.append(channels_resumed.id)
                    else:
                        channels_lst.append(channels_resumed.id)

        filtered_lst = []
        channels_obj = request.env['slide.channel'].browse(channels_lst)

        for val in channels_obj:
            if val.course_close_date:
                if datetime.now() <= val.course_close_date:
                    filtered_lst.append(val.id)

        channels = request.env['slide.channel'].sudo().browse(filtered_lst)

        # channels=  request.env['slide.channel'].sudo().browse(channels_lst)
        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('ecom_lms.channel_pwa_view_all', values)

    @http.route('/slides/completed/all', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_completed_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].search(domain, order=order)

        channels_lst = []
        for channels_completed in channels_ids:
            channels_completed_user_lst = []
            for channels_completed_partner in channels_completed.sudo().channel_partner_ids:
                if channels_completed_partner.completion == 100:
                    user = request.env['res.users'].search(
                        [('partner_id', '=', channels_completed_partner.partner_id.id)], limit=1)
                    if user:
                        channels_completed_user_lst.append(user.id)
            if request.env.user.id in channels_completed_user_lst:
                if channels_completed.custom_visibility == 'private':
                    channels_completed_private_user_lst = []
                    for channels_completed_private_partner in channels_completed.sudo().channel_partner_ids:
                        private_user = request.env['res.users'].search(
                            [('partner_id', '=', channels_completed_private_partner.partner_id.id)], limit=1)
                        if private_user:
                            channels_completed_private_user_lst.append(private_user.id)
                    if request.env.user.id in channels_completed_private_user_lst:
                        channels_lst.append(channels_completed.id)

                elif channels_completed.custom_visibility == 'semi_public':
                    channels_completed_semi_user_lst = []
                    for channels_completed_semi_user in channels_completed.sudo().nominated_user_ids:
                        channels_completed_semi_user_lst.append(channels_completed_semi_user.id)

                    if request.env.user.id in channels_completed_semi_user_lst:
                        channels_lst.append(channels_completed.id)
                else:
                    channels_lst.append(channels_completed.id)

        filtered_lst = []
        channels_obj = request.env['slide.channel'].browse(channels_lst)

        for val in channels_obj:
            if val.course_close_date:
                if datetime.now() <= val.course_close_date:
                    filtered_lst.append(val.id)

        channels = request.env['slide.channel'].sudo().browse(filtered_lst)

        # channels=  request.env['slide.channel'].sudo().browse(channels_lst)
        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('website_slides.courses_all', values)
    
    @http.route('/slides/completed/pwa/all', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_completed_pwa_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].search(domain, order=order)

        channels_lst = []
        for channels_completed in channels_ids:
            channels_completed_user_lst = []
            for channels_completed_partner in channels_completed.sudo().channel_partner_ids:
                if channels_completed_partner.completion == 100:
                    user = request.env['res.users'].search([('partner_id', '=', channels_completed_partner.partner_id.id)], limit=1)
                    if user:
                        channels_completed_user_lst.append(user.id)
            if request.env.user.id in channels_completed_user_lst:
                if channels_completed.custom_visibility == 'private':
                    channels_completed_private_user_lst = []
                    for channels_completed_private_partner in channels_completed.sudo().channel_partner_ids:
                        private_user = request.env['res.users'].search([('partner_id', '=', channels_completed_private_partner.partner_id.id)], limit=1)
                        if private_user:
                            channels_completed_private_user_lst.append(private_user.id)
                    if request.env.user.id in channels_completed_private_user_lst:
                        channels_lst.append(channels_completed.id)

                elif channels_completed.custom_visibility == 'semi_public':
                    channels_completed_semi_user_lst = []
                    for channels_completed_semi_user in channels_completed.sudo().nominated_user_ids:
                        channels_completed_semi_user_lst.append(channels_completed_semi_user.id)

                    if request.env.user.id in channels_completed_semi_user_lst:
                        channels_lst.append(channels_completed.id)
                else:
                    channels_lst.append(channels_completed.id)

        filtered_lst = []
        channels_obj = request.env['slide.channel'].browse(channels_lst)

        for val in channels_obj:
            if val.course_close_date:
                if datetime.now() <= val.course_close_date:
                    filtered_lst.append(val.id)

        channels = request.env['slide.channel'].sudo().browse(filtered_lst)

        # channels=  request.env['slide.channel'].sudo().browse(channels_lst)
        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('ecom_lms.channel_pwa_view_all', values)

    @http.route('/journey/all', type='http', auth="public", website=True, sitemap=True)
    def slides_journey_details_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].sudo().search(domain, order=order)
        final_suggested_lst = []
        for chaneel in channels_ids:
            final_suggested_lst.append(chaneel.id)

        channels = request.env['slide.channel'].browse(final_suggested_lst)

        journey_lst = []
        journey_ids = request.env['course.journey'].sudo().search([])

        for journey in journey_ids:
            journey_lst.append(journey.id)

        journey_all_details = request.env['course.journey'].sudo().browse(journey_lst)
        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'journey_all_details': journey_all_details,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('ecom_lms.journey_all', values)
    
    @http.route('/journey/pwa/all', type='http', auth="public", website=True, sitemap=True)
    def slides_journey_details_pwa_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].sudo().search(domain, order=order)
        final_suggested_lst = []
        for chaneel in channels_ids:
            final_suggested_lst.append(chaneel.id)

        channels = request.env['slide.channel'].browse(final_suggested_lst)

        journey_lst = []
        journey_ids = request.env['course.journey'].sudo().search([])

        for journey in journey_ids:
            journey_lst.append(journey.id)

        journey_all_details = request.env['course.journey'].sudo().browse(journey_lst)
        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'journey_all_details': journey_all_details,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('ecom_lms.journey_pwa_view_all', values)

    @http.route('/quizzes/all', type='http', auth="public", website=True, sitemap=True)
    def slides_quizzes_details_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].sudo().search(domain, order=order)
        final_suggested_lst = []
        for chaneel in channels_ids:
            final_suggested_lst.append(chaneel.id)

        channels = request.env['slide.channel'].browse(final_suggested_lst)

        quizzes_lst = []
        quizzes_ids = request.env['quizzes.question'].sudo().search([])
        for quizzes in quizzes_ids:
            quizzes_lst.append(quizzes.id)

        quizzes_all_details = request.env['quizzes.question'].sudo().browse(quizzes_lst)

        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'quizzes_all_details': quizzes_all_details,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('ecom_lms.quizzes_all', values)

    @http.route('/my-journey/all', type='http', auth="public", website=True, sitemap=True)
    def slides_my_journey_details_all(self, slide_type=None, my=False, **post):
        """ Home page displaying a list of courses displayed according to some
        criterion and search terms.

          :param string slide_type: if provided, filter the course to contain at
           least one slide of type 'slide_type'. Used notably to display courses
           with certifications;
          :param bool my: if provided, filter the slide.channels for which the
           current user is a member of
          :param dict post: post parameters, including

           * ``search``: filter on course description / name;
           * ``channel_tag_id``: filter on courses containing this tag;
           * ``channel_tag_group_id_<id>``: filter on courses containing this tag
             in the tag group given by <id> (used in navigation based on tag group);
        """
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].sudo().search(domain, order=order)
        final_suggested_lst = []
        for chaneel in channels_ids:
            final_suggested_lst.append(chaneel.id)

        channels = request.env['slide.channel'].browse(final_suggested_lst)

        journey_lst = []
        journey_ids = request.env['course.journey'].sudo().search([])

        for journey in journey_ids:
            journey_partner_lst = []
            if journey.journey_channel_partner_ids:
                for journey_partner in journey.journey_channel_partner_ids:
                    journey_partner_lst.append(journey_partner.partner_id.id)

            if request.env.user.partner_id.id in journey_partner_lst:
                journey_lst.append(journey.id)

        journey_all_details = request.env['course.journey'].sudo().browse(journey_lst)
        # channels_layouted = list(itertools.zip_longest(*[iter(channels)] * 4, fillvalue=None))

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'journey_all_details': journey_all_details,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('ecom_lms.journey_all', values)

    @http.route('/slides', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_home(self, **post):
        """ Home page for eLearning platform. Is mainly a container page, does not allow search / filter. """
        domain = request.website.website_domain()
        channels_all = request.env['slide.channel'].sudo().search(domain)
        # channels_all = request.env['slide.channel'].search(domain)
        lst = []
        channels_allnew = request.env['slide.channel'].search(domain)

        for val in channels_allnew:
            if val.course_close_date:
                if datetime.now() <= val.course_close_date:
                    newid = val.id
                    lst.append(newid)
        channels_all = request.env['slide.channel'].search([('id', '=', lst)])
        # channel_unlink = channels_allnew - channels_all
        # for val in channel_unlink:
        #     val._remove_membership(request.env.user.partner_id.ids)
        #     self._channel_remove_session_answers(val)

        if not request.env.user._is_public():
            # If a course is completed, we don't want to see it in first position but in last
            channels_my = channels_all.filtered(lambda channel: channel.is_member).sorted(
                lambda channel: 0 if channel.completed else channel.completion, reverse=True)[:3]
        else:
            channels_my = request.env['slide.channel']

        channels_popular_ids = channels_all.sorted('total_votes', reverse=True)[:3]
        channels_newest_ids = channels_all.sorted('create_date', reverse=True)[:3]

        achievements = request.env['gamification.badge.user'].sudo().search([('badge_id.is_published', '=', True)],
                                                                            limit=5)
        if request.env.user._is_public():
            challenges = None
            challenges_done = None
        else:
            challenges = request.env['gamification.challenge'].sudo().search([
                ('challenge_category', '=', 'slides'),
                ('reward_id.is_published', '=', True)
            ], order='id asc', limit=5)
            challenges_done = request.env['gamification.badge.user'].sudo().search([
                ('challenge_id', 'in', challenges.ids),
                ('user_id', '=', request.env.user.id),
                ('badge_id.is_published', '=', True)
            ]).mapped('challenge_id')

        users = request.env['res.users'].sudo().search([
            ('karma', '>', 0),
            ('website_published', '=', True)], limit=5, order='karma desc')

        channels_suggested_lst = []
        for channels_suggested in channels_all:
            if channels_suggested.custom_visibility == 'semi_public':
                suggested_user_lst = []
                for channels_partner in channels_suggested.sudo().channel_partner_ids:
                    user = request.env['res.users'].search([('partner_id', '=', channels_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        suggested_user_lst.append(user.id)
                if request.env.user.id not in suggested_user_lst and request.env.user in channels_suggested.nominated_user_ids:
                    channels_suggested_lst.append(channels_suggested.id)

        completed_course_list = []
        for completed_course in channels_all:
            if completed_course.custom_visibility != 'semi_public':

                for channels_partner in completed_course.sudo().channel_partner_ids:
                    if channels_partner.completion == 100:
                        if completed_course.id not in completed_course_list:
                            completed_course_list.append(completed_course.id)

        channels_comp_suggested_lst = []
        for channels_completed_suggested in completed_course_list:
            channel_comp_suggested = request.env['slide.channel'].sudo().browse(channels_completed_suggested)
            suggested_comp_user_lst = []
            for partner_val in channel_comp_suggested.sudo().channel_partner_ids:
                user_val = request.env['res.users'].search([('partner_id', '=', partner_val.partner_id.id)], limit=1)
                if user_val:
                    suggested_comp_user_lst.append(user_val.id)
            if request.env.user.id not in suggested_comp_user_lst:
                if channel_comp_suggested.custom_visibility == 'private':
                    comp_suggested_private_user_lst = []
                    for comp_suggested_private_partner in channel_comp_suggested.sudo().channel_partner_ids:
                        comp_suggested_private_user = request.env['res.users'].search(
                            [('partner_id', '=', comp_suggested_private_partner.partner_id.id)], limit=1)
                        if comp_suggested_private_user:
                            comp_suggested_private_user_lst.append(comp_suggested_private_user.id)
                    if request.env.user.id in comp_suggested_private_user_lst:
                        channels_comp_suggested_lst.append(channel_comp_suggested.id)
                elif channel_comp_suggested.custom_visibility == 'semi_public':
                    comp_suggested_semi_public_user_lst = []
                    for comp_suggested_semi_user in channel_comp_suggested.sudo().nominated_user_ids:
                        comp_suggested_semi_public_user_lst.append(comp_suggested_semi_user.id)
                    if request.env.user.id in comp_suggested_semi_public_user_lst:
                        channels_comp_suggested_lst.append(channel_comp_suggested.id)
                else:
                    channels_comp_suggested_lst.append(channel_comp_suggested.id)

        just_started_courses = []
        recent_start_courses_lst = []
        today_date = datetime.now()
        today_only_date = today_date.date()
        started_courses_ids = request.env['slide.channel.partner'].sudo().search([])
        for started in started_courses_ids:
            if started.create_date:
                if started.create_date.date() == today_only_date:
                    just_started_courses.append(started.channel_id.id)

        if len(just_started_courses) > 0:
            for just_started in just_started_courses:
                started_user_lst = []
                channel_just_started = request.env['slide.channel'].sudo().browse(just_started)
                for just_start in channel_just_started.sudo().channel_partner_ids:
                    user_val = request.env['res.users'].search([('partner_id', '=', just_start.partner_id.id)], limit=1)
                    if user_val:
                        started_user_lst.append(user_val.id)
                if request.env.user.id not in started_user_lst:
                    if channel_just_started.custom_visibility == 'private':
                        just_started_private_user_lst = []
                        for just_started_private_partner in channel_just_started.sudo().channel_partner_ids:
                            just_started_private_user = request.env['res.users'].search(
                                [('partner_id', '=', just_started_private_partner.partner_id.id)], limit=1)
                            if just_started_private_user:
                                just_started_private_user_lst.append(just_started_private_user.id)
                        if request.env.user.id in just_started_private_user_lst:
                            just_started_private_user_lst.append(channel_just_started.id)

                    elif channel_just_started.custom_visibility == 'semi_public':
                        just_started_semi_public_user_lst = []
                        for just_started_semi_user in channel_just_started.sudo().nominated_user_ids:
                            just_started_semi_public_user_lst.append(just_started_semi_user.id)
                        if request.env.user.id in just_started_semi_public_user_lst:
                            recent_start_courses_lst.append(channel_just_started.id)
                    else:
                        recent_start_courses_lst.append(channel_just_started.id)

        interested_course_lst = []
        for interested_course in channels_all:
            if interested_course.course_category_id in request.env.user.topic_of_interest_ids:
                interested_user_lst = []
                if interested_course.sudo().channel_partner_ids:
                    for partner_val1 in interested_course.sudo().channel_partner_ids:
                        user_val1 = request.env['res.users'].search([('partner_id', '=', partner_val1.partner_id.id)],
                                                                    limit=1)
                        if user_val1:
                            interested_user_lst.append(user_val1.id)
                if request.env.user.id not in interested_user_lst:
                    if interested_course.custom_visibility == 'private':
                        interested_private_user_lst = []
                        for channels_interested_private_partner in interested_course.sudo().channel_partner_ids:
                            interested_private_user = request.env['res.users'].search(
                                [('partner_id', '=', channels_interested_private_partner.partner_id.id)], limit=1)
                            if interested_private_user:
                                interested_private_user_lst.append(interested_private_user.id)
                        if request.env.user.id in interested_private_user_lst:
                            interested_course_lst.append(interested_course.id)

                    elif interested_course.custom_visibility == 'semi_public':
                        interested_semi_public_user_lst = []
                        for channels_interested_semi_user in interested_course.sudo().nominated_user_ids:
                            interested_semi_public_user_lst.append(channels_interested_semi_user.id)
                        if request.env.user.id in interested_semi_public_user_lst:
                            interested_course_lst.append(interested_course.id)
                    else:
                        interested_course_lst.append(interested_course.id)

        final_suggested_lst = channels_suggested_lst + channels_comp_suggested_lst + recent_start_courses_lst + interested_course_lst
        final_suggested_lst = list(set(final_suggested_lst))
        channels_suggested = request.env['slide.channel'].sudo().browse(final_suggested_lst)

        channels_assigned_lst = []
        for channels_assigned in channels_all:
            attendee_user_lst = []
            # if channels_popular.custom_visibility=='private':
            for channels_partner in channels_assigned.sudo().channel_partner_ids:
                if channels_partner.completion != 100:
                    user = request.env['res.users'].search([('partner_id', '=', channels_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        attendee_user_lst.append(user.id)
            if request.env.user.id in attendee_user_lst:
                if channels_assigned.course_close_date:
                    date_now = datetime.now()
                    if date_now.date() <= channels_assigned.course_close_date.date():
                        if channels_assigned.custom_visibility == 'private':
                            assigned_private_user_lst = []
                            for channels_assigned_private_partner in channels_assigned.sudo().channel_partner_ids:
                                assigned_private_user = request.env['res.users'].search(
                                    [('partner_id', '=', channels_assigned_private_partner.partner_id.id)], limit=1)
                                if assigned_private_user:
                                    assigned_private_user_lst.append(assigned_private_user.id)
                            if request.env.user.id in assigned_private_user_lst:
                                channels_assigned_lst.append(channels_assigned.id)

                        elif channels_assigned.custom_visibility == 'semi_public':
                            assigned_semi_public_user_lst = []
                            for channels_assigned_semi_user in channels_assigned.sudo().nominated_user_ids:
                                assigned_semi_public_user_lst.append(channels_assigned_semi_user.id)
                            if request.env.user.id in assigned_semi_public_user_lst:
                                channels_assigned_lst.append(channels_assigned.id)
                        else:
                            channels_assigned_lst.append(channels_assigned.id)

                else:
                    if channels_assigned.custom_visibility == 'private':
                        assigned_private_user_lst = []
                        for channels_assigned_private_partner in channels_assigned.sudo().channel_partner_ids:
                            assigned_private_user = request.env['res.users'].search(
                                [('partner_id', '=', channels_assigned_private_partner.partner_id.id)], limit=1)
                            if assigned_private_user:
                                assigned_private_user_lst.append(assigned_private_user.id)
                        if request.env.user.id in assigned_private_user_lst:
                            channels_assigned_lst.append(channels_assigned.id)
                    elif channels_assigned.custom_visibility == 'semi_public':
                        assigned_semi_public_user_lst = []
                        for channels_assigned_semi_user in channels_assigned.sudo().nominated_user_ids:
                            assigned_semi_public_user_lst.append(channels_assigned_semi_user.id)
                        if request.env.user.id in assigned_semi_public_user_lst:
                            channels_assigned_lst.append(channels_assigned.id)
                    else:
                        channels_assigned_lst.append(channels_assigned.id)

        channels_assign = request.env['slide.channel'].sudo().browse(channels_assigned_lst)

        channels_featured_lst = []
        for channels_featured in channels_all:
            featured_user_lst = []
            if channels_featured.is_featured and channels_featured.featured_group_id:
                if channels_featured.featured_group_id in request.env.user.groups_id:
                    if channels_featured.custom_visibility == 'private':
                        featured_private_user_lst = []
                        for channels_featured_partner in channels_featured.sudo().channel_partner_ids:
                            user = request.env['res.users'].search(
                                [('partner_id', '=', channels_featured_partner.partner_id.id)], limit=1)
                            if user:
                                featured_private_user_lst.append(user.id)
                        if request.env.user.id in featured_private_user_lst:
                            channels_featured_lst.append(channels_featured.id)

                    elif channels_featured.custom_visibility == 'semi_public':
                        featured_semi_public_user_lst = []
                        for channels_featured_user in channels_featured.sudo().nominated_user_ids:
                            featured_semi_public_user_lst.append(channels_featured_user.id)
                        if request.env.user.id in featured_semi_public_user_lst:
                            channels_featured_lst.append(channels_featured.id)

                    else:
                        channels_featured_lst.append(channels_featured.id)

        channels_feature = request.env['slide.channel'].sudo().browse(channels_featured_lst)

        channels_popular_lst = []
        for channels_popular in channels_popular_ids:
            if channels_popular.custom_visibility == 'private':
                popular_user_lst = []
                for channels_popular_partner in channels_popular.sudo().channel_partner_ids:
                    user = request.env['res.users'].search(
                        [('partner_id', '=', channels_popular_partner.partner_id.id)], limit=1)
                    if user:
                        popular_user_lst.append(user.id)
                if request.env.user.id in popular_user_lst:
                    channels_popular_lst.append(channels_popular.id)

            elif channels_popular.custom_visibility == 'semi_public':
                popular_user_lst = []
                for channels_popular_user in channels_popular.sudo().nominated_user_ids:
                    popular_user_lst.append(channels_popular_user.id)
                if request.env.user.id in popular_user_lst:
                    channels_popular_lst.append(channels_popular.id)
            else:
                channels_popular_lst.append(channels_popular.id)

        channels_popular = request.env['slide.channel'].browse(channels_popular_lst)

        channels_newest_lst = []
        for channels_newest in channels_newest_ids:
            if channels_newest.custom_visibility == 'private':
                newest_user_lst = []
                for channels_newest_partner in channels_newest.sudo().channel_partner_ids:
                    user = request.env['res.users'].search([('partner_id', '=', channels_newest_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        channels_newest_lst.append(user.id)
                if request.env.user.id in channels_newest_lst:
                    channels_newest_lst.append(channels_newest.id)

            elif channels_newest.custom_visibility == 'semi_public':
                newest_user_lst = []
                for channels_newest_user in channels_newest.sudo().nominated_user_ids:
                    newest_user_lst.append(channels_newest_user.id)

                if request.env.user.id in newest_user_lst:
                    channels_newest_lst.append(channels_newest.id)
            else:
                channels_newest_lst.append(channels_newest.id)

        channels_newest = request.env['slide.channel'].browse(channels_newest_lst)

        channels_newest = request.env['slide.channel'].browse(channels_newest_lst)

        channels_resumed_learning_lst = []
        for channels_resumed in channels_all:
            channels_resumed_user_lst = []
            # if channels_popular.custom_visibility=='private':
            for channels_resumed_partner in channels_resumed.sudo().channel_partner_ids:
                if channels_resumed_partner.completion < 100 and channels_resumed_partner.completion > 0:
                    user = request.env['res.users'].search(
                        [('partner_id', '=', channels_resumed_partner.partner_id.id)], limit=1)
                    if user:
                        channels_resumed_user_lst.append(user.id)
            if request.env.user.id in channels_resumed_user_lst:
                date_now = datetime.now()
                if channels_resumed.course_close_date:
                    if date_now.date() <= channels_resumed.course_close_date.date():
                        if channels_resumed.custom_visibility == 'private':
                            channels_resumed_private_user_lst = []
                            for channels_resumed_private_partner in channels_resumed.sudo().channel_partner_ids:
                                private_user = request.env['res.users'].search(
                                    [('partner_id', '=', channels_resumed_private_partner.partner_id.id)], limit=1)
                                if private_user:
                                    channels_resumed_private_user_lst.append(private_user.id)
                            if request.env.user.id in channels_resumed_private_user_lst:
                                channels_resumed_learning_lst.append(channels_resumed.id)

                        elif channels_resumed.custom_visibility == 'semi_public':
                            resumed_semi_user_lst = []
                            for channels_resumed_semi_user in channels_resumed.sudo().nominated_user_ids:
                                resumed_semi_user_lst.append(channels_resumed_semi_user.id)

                            if request.env.user.id in resumed_semi_user_lst:
                                channels_resumed_learning_lst.append(channels_resumed.id)
                        else:
                            channels_resumed_learning_lst.append(channels_resumed.id)
                else:
                    if channels_resumed.custom_visibility == 'private':
                        channels_resumed_private_user_lst = []
                        for channels_resumed_private_partner in channels_resumed.sudo().channel_partner_ids:
                            private_user = request.env['res.users'].search(
                                [('partner_id', '=', channels_resumed_private_partner.partner_id.id)], limit=1)
                            if private_user:
                                channels_resumed_private_user_lst.append(private_user.id)
                        if request.env.user.id in channels_resumed_private_user_lst:
                            channels_resumed_learning_lst.append(channels_resumed.id)

                    elif channels_resumed.custom_visibility == 'semi_public':
                        resumed_semi_user_lst = []
                        for channels_resumed_semi_user in channels_resumed.sudo().nominated_user_ids:
                            resumed_semi_user_lst.append(channels_resumed_semi_user.id)
                        if request.env.user.id in resumed_semi_user_lst:
                            channels_resumed_learning_lst.append(channels_resumed.id)

                    else:
                        channels_resumed_learning_lst.append(channels_resumed.id)

        channels_resumed = request.env['slide.channel'].sudo().browse(channels_resumed_learning_lst)
        channels_completed_lst = []

        for channels_completed in channels_all:
            channels_completed_user_lst = []
            # if channels_popular.custom_visibility=='private':
            for channels_completed_partner in channels_completed.sudo().channel_partner_ids:
                if channels_completed_partner.completion == 100:
                    user = request.env['res.users'].search(
                        [('partner_id', '=', channels_completed_partner.partner_id.id)], limit=1)
                    if user:
                        channels_completed_user_lst.append(user.id)

            if request.env.user.id in channels_completed_user_lst:
                if channels_completed.custom_visibility == 'private':
                    channels_complete_private_user_lst = []
                    for channels_complete_private_partner in channels_completed.sudo().channel_partner_ids:
                        complete_private_user = request.env['res.users'].search(
                            [('partner_id', '=', channels_complete_private_partner.partner_id.id)], limit=1)
                        if complete_private_user:
                            channels_complete_private_user_lst.append(complete_private_user.id)
                    if request.env.user.id in channels_complete_private_user_lst:
                        channels_completed_lst.append(channels_completed.id)

                elif channels_completed.custom_visibility == 'semi_public':
                    completed_semi_user_lst = []
                    for completed_semi_user in channels_completed.sudo().nominated_user_ids:
                        completed_semi_user_lst.append(completed_semi_user.id)
                    if request.env.user.id in completed_semi_user_lst:
                        channels_completed_lst.append(channels_completed.id)

                else:
                    channels_completed_lst.append(channels_completed.id)

        channels_complete = request.env['slide.channel'].sudo().browse(channels_completed_lst)

        journey_lst = []
        journey_ids = request.env['course.journey'].sudo().search([])

        for journey in journey_ids:
            journey_lst.append(journey.id)

        # for journey in journey_ids:
        #     journey_user_lst= []
        #     for journey_partner in journey.sudo().journey_channel_partner_ids:
        #        # if channels_completed_partner.completion == 100:
        #         user= request.env['res.users'].search([('partner_id','=',journey_partner.partner_id.id)],limit=1)
        #         if user:
        #             journey_user_lst.append(user.id)
        #
        #     if request.env.user.id in journey_user_lst:
        #         journey_lst.append(journey.id)

        journey_details = request.env['course.journey'].sudo().browse(journey_lst)
        
        
        
        completed_journey_list = []
        for completed_journey in journey_ids:
            for journey_partner in completed_journey.sudo().journey_channel_partner_ids:
                if journey_partner.journey_completion == 100:
                    if completed_journey.id not in completed_journey_list:
                        completed_journey_list.append(completed_journey.id)
                        
                        
        journey_comp_suggested_lst = []
        for journey_completed_suggested in completed_journey_list:
            journey_comp_suggested = request.env['course.journey'].sudo().browse(journey_completed_suggested)
            suggested_journey_comp_user_lst = []
            for journey_partner_val in journey_comp_suggested.sudo().journey_channel_partner_ids:
                user_val = request.env['res.users'].search([('partner_id', '=', journey_partner_val.partner_id.id)], limit=1)
                if user_val:
                    suggested_journey_comp_user_lst.append(user_val.id)
            if request.env.user.id not in suggested_journey_comp_user_lst:
                journey_comp_suggested_lst.append(journey_comp_suggested.id)
                
                
        just_started_journey = []
        recent_start_journey_lst = []
        today_date = datetime.now()
        today_only_date = today_date.date()
        started_journey_ids = request.env['course.journey.partner'].sudo().search([])
        for started_journey in started_journey_ids:
            if started_journey.create_date:
                if started_journey.create_date.date() == today_only_date:
                    just_started_journey.append(started_journey.journey_id.id)
    
        if len(just_started_journey) > 0:
            for just_started_j in just_started_journey:
                journey_started_user_lst = []
                journey_just_started = request.env['course.journey'].sudo().browse(just_started_j)
                for just_start_j in journey_just_started.sudo().journey_channel_partner_ids:
                    user_val = request.env['res.users'].search([('partner_id', '=', just_start_j.partner_id.id)], limit=1)
                    if user_val:
                        journey_started_user_lst.append(user_val.id)
                if request.env.user.id not in journey_started_user_lst:
                    recent_start_journey_lst.append(journey_just_started.id)
                    
                    
        interested_journey_lst = []
        for interested_journey in journey_ids:
            if interested_journey.courses_ids:
                for interested_journey_course in interested_journey.courses_ids:
                    if interested_journey_course.course_id.course_category_id in request.env.user.topic_of_interest_ids:
                        journey_interested_user_lst = []
                        if interested_journey.sudo().journey_channel_partner_ids:
                            for journey_partner_val1 in interested_journey.sudo().journey_channel_partner_ids:
                                journey_user_val1 = request.env['res.users'].search([('partner_id', '=', journey_partner_val1.partner_id.id)],limit=1)
                                if journey_user_val1:
                                    journey_interested_user_lst.append(journey_user_val1.id)
                        if request.env.user.id not in journey_interested_user_lst:
                            interested_journey_lst.append(interested_journey.id)
                            
                            
                            
        final_journey_suggested_lst = journey_comp_suggested_lst + recent_start_journey_lst + interested_journey_lst
        final_journey_suggested_lst = list(set(final_journey_suggested_lst))
        journey_suggested = request.env['course.journey'].sudo().browse(final_journey_suggested_lst)

        quizzes_lst = []
        quizzes_ids = request.env['quizzes.question'].sudo().search([])
        for quizzes in quizzes_ids:
            quizzes_lst.append(quizzes.id)

        quizzes_details = request.env['quizzes.question'].sudo().browse(quizzes_lst)

        values = self._prepare_user_values(**post)
        values.update({
            'channels_complete': channels_complete,
            'channels_resumed': channels_resumed,
            'channels_suggested': channels_suggested,
            'channels_assign': channels_assign,
            'channels_feature': channels_feature,
            'channels_my': channels_all,
            'channels_popular': channels_popular,
            'channels_newest': channels_newest,
            'achievements': achievements,
            'journey_details': journey_details,
            'journey_suggested':journey_suggested,
            'quizzes_details': quizzes_details,
            'users': users,
            'top3_users': self._get_top3_users(),
            'challenges': challenges,
            'challenges_done': challenges_done,
            'search_tags': request.env['slide.channel.tag']
        })

        return request.render('website_slides.courses_home', values)

    def sitemap_slide(env, rule, qs):
        Channel = env['slide.channel']
        dom = sitemap_qs2dom(qs=qs, route='/slides/', field=Channel._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for channel in Channel.search(dom):
            loc = '/slides/%s' % slug(channel)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}

    @http.route([
        '/slides/<model("slide.channel"):channel>',
        '/slides/<model("slide.channel"):channel>/page/<int:page>',
        '/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>',
        '/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>/page/<int:page>',
        '/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>',
        '/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>/page/<int:page>',
    ], type='http', auth="public", website=True, sitemap=sitemap_slide)
    def channel(self, channel, category=None, tag=None, page=1, slide_type=None, uncategorized=False, sorting=None,
                search=None, **kw):
        domain = request.website.website_domain()
        lst = []
        channels_allnew = request.env['slide.channel'].search(domain)
        for val in channels_allnew:
            if val.course_close_date:
                # current_date = datetime.now()
                if datetime.now() <= val.course_close_date:
                    newid = val.id
                    lst.append(newid)
        channels_all = request.env['slide.channel'].search([('id', 'in', lst)])
        """
        Will return all necessary data to display the requested slide_channel along with a possible category.
        """
        if not channel.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        domain = self._get_channel_slides_base_domain(channel)
        if channel.id in lst:
            pager_url = "/slides/%s" % (channel.id)

            pager_args = {}
            slide_types = dict(request.env['slide.slide']._fields['slide_type']._description_selection(request.env))
            if search:
                domain += [
                    '|', '|',
                    ('name', 'ilike', search),
                    ('description', 'ilike', search),
                    ('html_content', 'ilike', search)]
                pager_args['search'] = search
            else:
                if category:
                    domain += [('category_id', '=', category.id)]
                    pager_url += "/category/%s" % category.id
                elif tag:
                    domain += [('tag_ids.id', '=', tag.id)]
                    pager_url += "/tag/%s" % tag.id
                if uncategorized:
                    domain += [('category_id', '=', False)]
                    pager_args['uncategorized'] = 1
                elif slide_type:
                    domain += [('slide_type', '=', slide_type)]
                    pager_url += "?slide_type=%s" % slide_type

            # sorting criterion
            if channel.channel_type == 'documentation':
                default_sorting = 'latest' if channel.promote_strategy in ['specific', 'none',
                                                                           False] else channel.promote_strategy
                actual_sorting = sorting if sorting and sorting in request.env[
                    'slide.slide']._order_by_strategy else default_sorting
            else:
                actual_sorting = 'sequence'
            order = request.env['slide.slide']._order_by_strategy[actual_sorting]
            pager_args['sorting'] = actual_sorting

            slide_count = request.env['slide.slide'].sudo().search_count(domain)
            page_count = math.ceil(slide_count / self._slides_per_page)
            pager = request.website.pager(url=pager_url, total=slide_count, page=page,
                                          step=self._slides_per_page, url_args=pager_args,
                                          scope=page_count if page_count < self._pager_max_pages else self._pager_max_pages)

            query_string = None
            if category:
                query_string = "?search_category=%s" % category.id
            elif tag:
                query_string = "?search_tag=%s" % tag.id
            elif slide_type:
                query_string = "?search_slide_type=%s" % slide_type
            elif uncategorized:
                query_string = "?search_uncategorized=1"

            values = {
                'channel': channel,
                'main_object': channel,
                'active_tab': kw.get('active_tab', 'home'),
                # search
                'search_category': category,
                'search_tag': tag,
                'search_slide_type': slide_type,
                'search_uncategorized': uncategorized,
                'query_string': query_string,
                'slide_types': slide_types,
                'sorting': actual_sorting,
                'search': search,
                # chatter
                'rating_avg': channel.rating_avg,
                'rating_count': channel.rating_count,
                # display data
                'user': request.env.user,
                'pager': pager,
                'is_public_user': request.website.is_public_user(),
                # display upload modal
                'enable_slide_upload': 'enable_slide_upload' in kw,
            }
            if not request.env.user._is_public():
                last_message = request.env['mail.message'].search([
                    ('model', '=', channel._name),
                    ('res_id', '=', channel.id),
                    ('author_id', '=', request.env.user.partner_id.id),
                    ('message_type', '=', 'comment'),
                    ('is_internal', '=', False)
                ], order='write_date DESC', limit=1)
                if last_message:
                    last_message_values = last_message.read(['body', 'rating_value', 'attachment_ids'])[0]
                    last_message_attachment_ids = last_message_values.pop('attachment_ids', [])
                    if last_message_attachment_ids:
                        # use sudo as portal user cannot read access_token, necessary for updating attachments
                        # through frontend chatter -> access is already granted and limited to current user message
                        last_message_attachment_ids = json.dumps(
                            request.env['ir.attachment'].sudo().browse(last_message_attachment_ids).read(
                                ['id', 'name', 'mimetype', 'file_size', 'access_token']
                            )
                        )
                else:
                    last_message_values = {}
                    last_message_attachment_ids = []
                values.update({
                    'last_message_id': last_message_values.get('id'),
                    'last_message': tools.html2plaintext(last_message_values.get('body', '')),
                    'last_rating_value': last_message_values.get('rating_value'),
                    'last_message_attachment_ids': last_message_attachment_ids,
                })
                if channel.can_review:
                    values.update({
                        'message_post_hash': channel._sign_token(request.env.user.partner_id.id),
                        'message_post_pid': request.env.user.partner_id.id,
                    })

            # fetch slides and handle uncategorized slides; done as sudo because we want to display all
            # of them but unreachable ones won't be clickable (+ slide controller will crash anyway)
            # documentation mode may display less slides than content by category but overhead of
            # computation is reasonable
            if channel.promote_strategy == 'specific':
                values['slide_promoted'] = channel.sudo().promoted_slide_id
            else:
                values['slide_promoted'] = request.env['slide.slide'].sudo().search(domain, limit=1, order=order)

            limit_category_data = False
            if channel.channel_type == 'documentation':
                if category or uncategorized:
                    limit_category_data = self._slides_per_page
                else:
                    limit_category_data = self._slides_per_category

            values['category_data'] = channel._get_categorized_slides(
                domain, order,
                force_void=not category,
                limit=limit_category_data,
                offset=pager['offset'])
            values['channel_progress'] = self._get_channel_progress(channel, include_quiz=True)
            time_left = 0.0
            for sl in channel.slide_ids:
                if values['channel_progress'][sl.id].get('completed') != True:
                    if sl.is_published:
                        time_left = time_left + sl.completion_time
            
            values.update({
                    'time_left_value': time_left, })

            # for sys admins: prepare data to install directly modules from eLearning when
            # uploading slides. Currently supporting only survey, because why not.
            if request.env.user.has_group('base.group_system'):
                module = request.env.ref('base.module_survey')
                if module.state != 'installed':
                    values['modules_to_install'] = [{
                        'id': module.id,
                        'motivational': _('Evaluate and certify your students.'),
                    }]

            values = self._prepare_additional_channel_values(values, **kw)
            return request.render('website_slides.course_main', values)
        else:
            sys.tracebacklimit = 0
            raise AccessError(
                _('The availability of the course is expired. Please click on "Home" or "My Courses" to access your available content.'))
            pager_url = "/slides"
            return request.redirect(pager_url)
        
        
        
        
    @http.route([
        '/joined/pwa/slides/<model("slide.channel"):channel>',
        '/joined/pwa/slides/<model("slide.channel"):channel>/page/<int:page>',
        '/joined/pwa/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>',
        '/joined/pwa/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>/page/<int:page>',
        '/joined/pwa/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>',
        '/joined/pwa/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>/page/<int:page>',
    ], type='http', auth="public", website=True, sitemap=sitemap_slide)
    def joined_pwa_channel(self, channel, category=None, tag=None, page=1, slide_type=None, uncategorized=False, sorting=None,
                search=None, **kw):
        domain = request.website.website_domain()
        if not channel.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

            
        channel_partner_lst=[]
        if channel.sudo().channel_partner_ids:
            for partner_channel in channel.sudo().channel_partner_ids:
                channel_partner_lst.append(partner_channel.partner_id.id)
                
        if request.env.user.partner_id.id not in channel_partner_lst:
            channel_attendee_id = request.env['slide.channel.partner'].sudo().create({'partner_id': request.env.user.partner_id.id,
                                                                                      'channel_id':channel.id,
                                                                                      'custom_user_id':request.env.user.id})
            
        pager_url = "/pwa/slides/%s" % (channel.id)
        return request.redirect(pager_url)
        
        
        
        
    @http.route([
        '/pwa/slides/<model("slide.channel"):channel>',
        '/pwa/slides/<model("slide.channel"):channel>/page/<int:page>',
        '/pwa/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>',
        '/pwa/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>/page/<int:page>',
        '/pwa/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>',
        '/pwa/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>/page/<int:page>',
    ], type='http', auth="public", website=True, sitemap=sitemap_slide)
    def pwa_channel(self, channel, category=None, tag=None, page=1, slide_type=None, uncategorized=False, sorting=None,
                search=None, **kw):
        domain = request.website.website_domain()
        lst = []
        channels_allnew = request.env['slide.channel'].search(domain)
        for val in channels_allnew:
            if val.course_close_date:
                # current_date = datetime.now()
                if datetime.now() <= val.course_close_date:
                    newid = val.id
                    lst.append(newid)
        channels_all = request.env['slide.channel'].search([('id', 'in', lst)])
        """
        Will return all necessary data to display the requested slide_channel along with a possible category.
        """
        if not channel.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        domain = self._get_channel_slides_base_domain(channel)
        if channel.id in lst:
            pager_url = "/slides/%s" % (channel.id)

            pager_args = {}
            slide_types = dict(request.env['slide.slide']._fields['slide_type']._description_selection(request.env))
            if search:
                domain += [
                    '|', '|',
                    ('name', 'ilike', search),
                    ('description', 'ilike', search),
                    ('html_content', 'ilike', search)]
                pager_args['search'] = search
            else:
                if category:
                    domain += [('category_id', '=', category.id)]
                    pager_url += "/category/%s" % category.id
                elif tag:
                    domain += [('tag_ids.id', '=', tag.id)]
                    pager_url += "/tag/%s" % tag.id
                if uncategorized:
                    domain += [('category_id', '=', False)]
                    pager_args['uncategorized'] = 1
                elif slide_type:
                    domain += [('slide_type', '=', slide_type)]
                    pager_url += "?slide_type=%s" % slide_type

            # sorting criterion
            if channel.channel_type == 'documentation':
                default_sorting = 'latest' if channel.promote_strategy in ['specific', 'none',
                                                                           False] else channel.promote_strategy
                actual_sorting = sorting if sorting and sorting in request.env[
                    'slide.slide']._order_by_strategy else default_sorting
            else:
                actual_sorting = 'sequence'
            order = request.env['slide.slide']._order_by_strategy[actual_sorting]
            pager_args['sorting'] = actual_sorting

            slide_count = request.env['slide.slide'].sudo().search_count(domain)
            page_count = math.ceil(slide_count / self._slides_per_page)
            pager = request.website.pager(url=pager_url, total=slide_count, page=page,
                                          step=self._slides_per_page, url_args=pager_args,
                                          scope=page_count if page_count < self._pager_max_pages else self._pager_max_pages)

            query_string = None
            if category:
                query_string = "?search_category=%s" % category.id
            elif tag:
                query_string = "?search_tag=%s" % tag.id
            elif slide_type:
                query_string = "?search_slide_type=%s" % slide_type
            elif uncategorized:
                query_string = "?search_uncategorized=1"
                
            remaining_course_percent= 100-channel.completion
            audio_present_count=1
            video_present_count=1
            if channel.slide_ids:
                for audio_slide in channel.slide_ids:
                    if audio_slide.slide_type == 'video' and audio_slide.slide_attachment.mimetype == 'audio/mpeg':
                        audio_present_count=audio_present_count+1
                        
                    if audio_slide.slide_type == 'video' and audio_slide.slide_attachment.mimetype == 'video/mp4':
                        video_present_count=video_present_count+1
                        
        
            users_details= request.env['res.users'].search([])
            values = {
                'channel': channel,
                'main_object': channel,
                'active_tab': kw.get('active_tab', 'home'),
                # search
                'search_category': category,
                'search_tag': tag,
                'search_slide_type': slide_type,
                'search_uncategorized': uncategorized,
                'query_string': query_string,
                'slide_types': slide_types,
                'sorting': actual_sorting,
                'search': search,
                # chatter
                'rating_avg': channel.rating_avg,
                'rating_count': channel.rating_count,
                # display data
                'user': request.env.user,
                'pager': pager,
                'remaining_course_percent':remaining_course_percent,
                'is_public_user': request.website.is_public_user(),
                # display upload modal
                'enable_slide_upload': 'enable_slide_upload' in kw,
                'audio_present_count':audio_present_count,
                'video_present_count':video_present_count,
                'users_details':users_details,
            }
            if not request.env.user._is_public():
                last_message = request.env['mail.message'].search([
                    ('model', '=', channel._name),
                    ('res_id', '=', channel.id),
                    ('author_id', '=', request.env.user.partner_id.id),
                    ('message_type', '=', 'comment'),
                    ('is_internal', '=', False)
                ], order='write_date DESC', limit=1)
                if last_message:
                    last_message_values = last_message.read(['body', 'rating_value', 'attachment_ids'])[0]
                    last_message_attachment_ids = last_message_values.pop('attachment_ids', [])
                    if last_message_attachment_ids:
                        # use sudo as portal user cannot read access_token, necessary for updating attachments
                        # through frontend chatter -> access is already granted and limited to current user message
                        last_message_attachment_ids = json.dumps(
                            request.env['ir.attachment'].sudo().browse(last_message_attachment_ids).read(
                                ['id', 'name', 'mimetype', 'file_size', 'access_token']
                            )
                        )
                else:
                    last_message_values = {}
                    last_message_attachment_ids = []
                values.update({
                    'last_message_id': last_message_values.get('id'),
                    'last_message': tools.html2plaintext(last_message_values.get('body', '')),
                    'last_rating_value': last_message_values.get('rating_value'),
                    'last_message_attachment_ids': last_message_attachment_ids,
                })
                if channel.can_review:
                    values.update({
                        'message_post_hash': channel._sign_token(request.env.user.partner_id.id),
                        'message_post_pid': request.env.user.partner_id.id,
                    })

            # fetch slides and handle uncategorized slides; done as sudo because we want to display all
            # of them but unreachable ones won't be clickable (+ slide controller will crash anyway)
            # documentation mode may display less slides than content by category but overhead of
            # computation is reasonable
            if channel.promote_strategy == 'specific':
                values['slide_promoted'] = channel.sudo().promoted_slide_id
            else:
                values['slide_promoted'] = request.env['slide.slide'].sudo().search(domain, limit=1, order=order)

            limit_category_data = False
            if channel.channel_type == 'documentation':
                if category or uncategorized:
                    limit_category_data = self._slides_per_page
                else:
                    limit_category_data = self._slides_per_category

            values['category_data'] = channel._get_categorized_slides(
                domain, order,
                force_void=not category,
                limit=limit_category_data,
                offset=pager['offset'])
            values['channel_progress'] = self._get_channel_progress(channel, include_quiz=True)

            # for sys admins: prepare data to install directly modules from eLearning when
            # uploading slides. Currently supporting only survey, because why not.
            if request.env.user.has_group('base.group_system'):
                module = request.env.ref('base.module_survey')
                if module.state != 'installed':
                    values['modules_to_install'] = [{
                        'id': module.id,
                        'name': module.shortdesc,
                        'motivational': _('Evaluate and certify your students.'),
                    }]

            values = self._prepare_additional_channel_values(values, **kw)
            return request.render('ecom_lms.pwa_course_card_view_template', values)
            # return request.render('website_slides.course_main', values)
        else:
            sys.tracebacklimit = 0
            raise AccessError(_('The availability of the course is expired. Please click on "Home" or "My Courses" to access your available content.'))
            pager_url = "/slides"
            return request.redirect(pager_url)

    @http.route([
        '/journey/<model("course.journey"):journey>',
    ], type='http', auth="public", website=True, sitemap=sitemap_slide)
    def channel_journey(self, journey, category=None, tag=None, page=1, slide_type=None, uncategorized=False,
                        sorting=None,
                        search=None, **kw):

        if journey:

            # pager_url = "/slides/%s" % (journey.id)

            journey_subscribed = False
            journey_completion = 0
            journey_completed = False
            journey_count = 0
            if journey.journey_channel_partner_ids:
                for journey_partner in journey.journey_channel_partner_ids:
                    if journey_partner.partner_id == request.env.user.partner_id:
                        journey_completion = journey_partner.journey_completion
                        journey_completed = journey_partner.journey_completed_mail
                        journey_count = journey_count + 1
            if journey_count > 0:
                journey_subscribed = True
            values = {
                'journey_subscribed': journey_subscribed,
                'journey_completion': journey_completion,
                'journey_completed': journey_completed,
                'journey': journey,
                'user': request.env.user,
                'is_public_user': request.website.is_public_user(),
            }
            return request.render('ecom_lms.journey_main', values)

    @http.route(['/quiz/questions/<model("slide.question"):questions>'], type='http', auth="public", website=True,)
    def independent_quiz_questions(self, questions, **kw):
        quizzes = questions.custom_question_id
        values = {
            'questions': questions,
            'quizzes': quizzes,
        }
        return request.render('ecom_lms.independent_questions', values)

    @http.route(['/send/recommendation_mail'], type='http', auth="public", website=True,)
    def send_recommendation_mail(self, **kw):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        selected_course_id = kw.get('course_id')
        selected_user_email_lst = []
        selected_user_lst = []
        recommend_user_exist_lst = []
        selected_user = request.httprequest.form.getlist('user_id1')
        for user in selected_user:
            selected_id = request.env['res.users'].sudo().browse(int(user))
            course_id = request.env['slide.channel'].sudo().browse(int(selected_course_id))
            recommend_user_exist = request.env['recommend.users'].sudo().search([('res_user_id', '=', selected_id.id), ('recommend_courses_id', '=', course_id.id)])
            if recommend_user_exist:
                recommend_user_exist_lst.append(user)
            if not recommend_user_exist:
                selected_user_lst.append(user)
        if selected_user_lst:
            for user in selected_user_lst:
                selected_user_id = request.env['res.users'].sudo().browse(int(user))
                user_email = selected_user_id.partner_id.email
                if user_email:
                    selected_user_email_lst.append(user_email)
            template_id = request.env.ref('ecom_lms.email_template_course_recommendation').sudo()
            if selected_user_email_lst:
                if template_id and selected_user_email_lst:
                    outgoing_server_name = request.env['ir.mail_server'].sudo().search([],limit=1).smtp_user
                    template_id.email_from = outgoing_server_name
                    user_id = request.env.user.id
                    for email in selected_user_email_lst:
                        user_name = request.env['res.partner'].sudo().search([('email', '=', email)]).name
                        email_course_id = request.env['slide.channel'].sudo().browse(int(selected_course_id))
                        current_user = request.env['res.users'].sudo().browse(int(request.env.uid))
                        email_vals = {
                            # 'email_from': outgoing_server_name,
                            'email_from': outgoing_server_name,
                            'email_to': email,
                            "subject": 'This course is recommended to you',
                            "body_html": """ <html>
                                                   <head></head>
                                                   <body>
                                                   <p>Dear """ + str(user_name) + """</p>
                                                    <p>
                                                    """ + str(current_user.name) + """ recommend the <strong>""" + str(email_course_id.name) + """</strong> to you. Please click on the sharable link to join the course.Course Due date will be """ + str(email_course_id.course_close_date.date()) + """..
                                                    </p>
                                                    <p>
                                                     <a href=""" + str(base_url + "/recommend-course?ref=" + (str(selected_course_id))) + """
                            style="padding: 5px 10px; color: #FFFFFF; text-decoration: none; background-color: #875A7B; border: 1px solid #875A7B; border-radius: 3px">
                            Click Here</a></p>"""
                        }
                        mail_send = template_id.sudo().send_mail(user_id, force_send=True, email_values=email_vals)
                        if mail_send:
                            for user_id in selected_user_lst:
                                updated_recommned_users = request.env['recommend.users'].sudo().create({'res_user_id': user_id, 'recommend_courses_id':selected_course_id})
                            logging.info('Recommendation Mail has been sent')
                            recommend_user_name_exist_lst = []
                            vals = {
                                'recommend_user_name_exist_lst': recommend_user_name_exist_lst
                            }
                            if recommend_user_exist_lst:
                                for user in recommend_user_exist_lst:
                                    user_name = request.env['res.users'].sudo().search([('id', '=', user)]).name
                                    recommend_user_name_exist_lst.append(user_name)
                            return request.render("ecom_lms.customer_thanks", vals)
            else:
                raise ValidationError('No email id is connected to this user')

        else:
            raise ValidationError('Selected users already recommended earlier')
            # return request.render("ecom_lms.already_recommended",{})

    @http.route(['/recommend-course'], type='http', auth="public", website=True,)
    def recommend_course(self, **kw):
        selected_course_id = kw.get('ref')
        course_id = request.env['slide.channel'].sudo().browse(int(selected_course_id))
        pager_url = "/slides/%s" % (course_id.id)
        return request.redirect(pager_url)

    @http.route(['/recommend-quiz'], type='http', auth="public", website=True,)
    def recommend_quiz(self, **kw):
        selected_course_id = kw.get('ref')
        quiz_id = request.env['quizzes.question'].sudo().browse(int(selected_course_id))
        pager_url = "/quizzes/%s" % (quiz_id.id)
        return request.redirect(pager_url)
    
    @http.route(['/search/recommendation/<model("slide.channel"):channel>'], type='http', auth="public", website=True,)
    def search_recommend_name(self, channel,**kw):
        searched_term = kw.get('search')
        users_ids = request.env['res.users'].sudo().search([('name','ilike',searched_term)])
        values = {
            'user_details': users_ids,
            'channel': channel,
            'search_term':searched_term,
            'user': request.env.user,
        }
        return request.render('ecom_lms.recommend_form', values)

    @http.route(['/recommendation/<model("slide.channel"):channel>'], type='http', auth="public", website=True,)
    def share_quiz(self, channel, **kw):
        if request.env.user.id == request.env.ref('base.public_user').id:
            return request.render('web.login', {})
        else:
            users_ids = request.env['res.users'].sudo().search([],order='name ASC')

            values = {
                'user_details': users_ids,
                'channel': channel,
                'user': request.env.user,
            }
            return request.render('ecom_lms.recommend_form', values)

    @http.route(['/count/like/<model("slide.channel"):channel>'], type='http', auth="user", website=True)
    def like_count(self, channel, **post):
        path = post.get('ref')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url + path
        if channel.sudo().channel_partner_ids:
            for channel_partner in channel.channel_partner_ids:
                attendee_env = request.env['slide.channel.partner'].sudo().search(
                    [('channel_id', '=', channel.id), ('partner_id', '=', request.env.user.partner_id.id)])
                course_env = request.env['slide.channel'].sudo().search([('id', '=', channel.id)])
                if request.env.user.partner_id == channel_partner.partner_id:
                    # attendee_env.course_joined = True
                    if attendee_env.course_joined:
                        if channel_partner.channel_disliked:
                            if not channel_partner.channel_liked:
                                course_env.dislikes += -1
                                attendee_env.channel_disliked = False
                                course_env.likes += 1
                                attendee_env.channel_liked = True
                        if not channel_partner.channel_disliked and not channel_partner.channel_liked:
                            course_env.likes += 1
                            attendee_env.channel_liked = True
                            attendee_env.not_liked_disliked = False
        return request.redirect(url)


    @http.route(['/count/dislike/<model("slide.channel"):channel>'], type='http', auth="public", website=True)
    def dislike_count(self, channel, **post):
        path = post.get('ref')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url + path
        if channel.sudo().channel_partner_ids:
            for channel_partner in channel.channel_partner_ids:
                if request.env.user.partner_id == channel_partner.partner_id:
                    attendee_env = request.env['slide.channel.partner'].sudo().search(
                        [('channel_id', '=', channel.id), ('partner_id', '=', request.env.user.partner_id.id)])
                    course_env = request.env['slide.channel'].sudo().search([('id', '=', channel.id)])
                    # attendee_env.course_joined = True
                    if attendee_env.course_joined:
                        if not attendee_env.channel_liked and not attendee_env.channel_disliked:
                            course_env.dislikes += 1
                            attendee_env.channel_disliked = True
                            attendee_env.not_liked_disliked = False

                        if attendee_env.channel_liked:
                            if not attendee_env.channel_disliked:
                                course_env.likes += -1
                                attendee_env.channel_liked = False
                                course_env.dislikes += 1
                                attendee_env.channel_disliked = True
        return request.redirect(url)


    @http.route(['/journey/count/like/<model("course.journey"):journey>'], type='http', auth="user", website=True)
    def journey_like_count(self, journey, **post):
        path = post.get('ref')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url + path
        if journey.sudo().journey_channel_partner_ids:
            for journey_partner in journey.journey_channel_partner_ids:
                attendee_env = request.env['course.journey.partner'].sudo().search(
                    [('journey_id', '=', journey.id), ('partner_id', '=', request.env.user.partner_id.id)])
                journey_env = request.env['course.journey'].sudo().search([('id', '=', journey.id)])
                if request.env.user.partner_id == journey_partner.partner_id:
                    # attendee_env.course_joined = True
                    if attendee_env.journey_joined:
                        if journey_partner.journey_disliked:
                            if not journey_partner.journey_liked:
                                journey_env.dislikes += -1
                                attendee_env.journey_disliked = False
                                journey_env.likes += 1
                                attendee_env.journey_liked = True
                        if not journey_partner.journey_disliked and not journey_partner.journey_liked:
                            journey_env.likes += 1
                            attendee_env.journey_liked = True
                            attendee_env.journey_not_liked_disliked = False
        return request.redirect(url)


    @http.route(['/journey/count/dislike/<model("course.journey"):journey>'], type='http', auth="public", website=True)
    def Journey_dislike_count(self, journey, **post):
        path = post.get('ref')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url + path
        if journey.sudo().journey_channel_partner_ids:
            for journey_partner in journey.journey_channel_partner_ids:
                if request.env.user.partner_id == journey_partner.partner_id:
                    attendee_env = request.env['course.journey.partner'].sudo().search(
                        [('journey_id', '=', journey.id), ('partner_id', '=', request.env.user.partner_id.id)])
                    journey_env = request.env['course.journey'].sudo().search([('id', '=', journey.id)])
                    # attendee_env.course_joined = True
                    if attendee_env.journey_joined:
                        if not attendee_env.journey_liked and not attendee_env.journey_disliked:
                            journey_env.dislikes += 1
                            attendee_env.journey_disliked = True
                            attendee_env.journey_not_liked_disliked = False

                        if attendee_env.journey_liked:
                            if not attendee_env.journey_disliked:
                                journey_env.likes += -1
                                attendee_env.journey_liked = False
                                journey_env.dislikes += 1
                                attendee_env.journey_disliked = True
        return request.redirect(url)

    @http.route(['/submit/quizzes/'], type='http', auth="public", website=True,)
    def submit_independent_quiz(self,  **kw):
        values = {}
        input_dict = {}
        quiz_input_dict = {}
        query_strings = request.params.get('input_value')
        user_input_lst = query_strings.split(",")
        report_created = False
        correct_answer = ''
        submit_correct_answer = False
        independent_quiz_participation_id = ''
        for inputs in user_input_lst:
            params = inputs.split("/")
            inputed_values = params[0]
            question_id = params[-1]
            quiz_name = params[-2]
            selected_ans = inputed_values.split('=')
            selected_question = question_id.split('=')
            quiz_split = quiz_name.split('-')
            quiz_id = quiz_split[-1]
            input_dict[selected_question[-1]] = selected_ans[-1]
            quiz_input_dict[quiz_id] = input_dict
        for key, vals in quiz_input_dict.items():
            quizzes_exist = request.env['quizzes.question'].sudo().search([('id', '=', key)])
            if quizzes_exist:
                if not report_created:
                    independent_quiz_participation_id = request.env['quiz.report'].sudo().create(
                        {'quiz_id': quizzes_exist.id,
                         'start_datetime': datetime.now(),
                         'user_id': request.env.user.id,
                         'partner_id': request.env.user.partner_id.id,
                         'attempts_num': 1,
                         'quiz_completed': True,
                         })
                    if independent_quiz_participation_id:
                        for ques_id, ques_value in vals.items():
                            answer_score = ''
                            slide_question = request.env['slide.question'].sudo().search([('id','=',ques_id)])
                            independent_ans_ids = slide_question.answer_ids
                            for answers in independent_ans_ids:
                                if answers.is_correct:
                                    correct_answer = answers.text_value
                                    if ques_value == correct_answer:
                                        submit_correct_answer = True
                                        answer_score = answers.answer_score
                            quizzes_report_line = request.env['quiz.report.line'].sudo().create({'quiz_report_id': independent_quiz_participation_id.id,
                                                                                  'quiz_id': quizzes_exist.id,'quiz_question_id': slide_question.id,
                                                                                  'selected_answer': ques_value,'correct_answer': correct_answer,
                                                                                  'answer_score': answer_score})
    
        
                            if independent_ans_ids:
                                for rec in independent_ans_ids:
                                    res = request.env['answer.line'].sudo().create({'quiz_report_line_id':quizzes_report_line.id,
                                                                                    'slide_ans_id':rec.id,
                                                                                    })
                            if independent_quiz_participation_id:
                                report_created = True
                else:
                    updated_quiz_report_id = request.env['quiz.report'].sudo().search([('id','=',independent_quiz_participation_id.id)])
                    slide_question = request.env['slide.question'].sudo().search([('id','=',ques_id)])
                    independent_ans_ids = slide_question.answer_ids
                    for answers in independent_ans_ids:
                        if answers.is_correct:
                            correct_answer = answers.text_value
                            if ques_value == correct_answer:
                                submit_correct_answer = True
                                answer_score = answers.answer_score
                    report_created = True

                first_qus = False
                first_qus_bool = False
                qus_lst = []
                if quizzes_exist.custom_quiz_ids:
                    for qus in quizzes_exist.custom_quiz_ids:
                        qus_lst.append(qus.id)
                        if not first_qus_bool:
                            first_qus = qus.id
                            first_qus_bool = True
                
                right_count=1            
                if independent_quiz_participation_id:
                    if independent_quiz_participation_id.quiz_line:
                        for ind_quiz_line in independent_quiz_participation_id.quiz_line:
                            if ind_quiz_line.selected_answer != ind_quiz_line.correct_answer:
                                right_count =right_count+1
                                
                                

                values.update({
                    'quizzes': quizzes_exist,
                    'user': request.env.user,
                    'is_public_user': request.website.is_public_user(),
                    'first_qus': first_qus,
                    'right_count':right_count,
                    'independent_quiz_participation_id':independent_quiz_participation_id
                })
        return request.render('ecom_lms.submit_ecom_independent_quizzes_main', values)

    # @http.route(['/submit/quizzes/'], type='http', auth="public", website=True,)
    # def submit_independent_quiz(self,  **kw):
    #     values = {}
    #     input_dict = {}
    #     quiz_input_dict = {}
    #     query_strings = request.params.get('input_value')
    #     user_input_lst = query_strings.split(",")
    #     report_created = False
    #     correct_answer = ''
    #     submit_correct_answer = False
    #     independent_quiz_participation_id = ''
    #     for inputs in user_input_lst:
    #         params = inputs.split("/")
    #         inputed_values = params[0]
    #         question_id = params[-1]
    #         quiz_name = params[-2]
    #         selected_ans = inputed_values.split('=')
    #         selected_question = question_id.split('=')
    #         quiz_split = quiz_name.split('-')
    #         quiz_id = quiz_split[-1]
    #         input_dict[selected_question[-1]] = selected_ans[-1]
    #         quiz_input_dict[quiz_id] = input_dict
    #     for key, vals in quiz_input_dict.items():
    #         quizzes_exist = request.env['quizzes.question'].sudo().search([('id', '=', key)])
    #         if quizzes_exist:
    #             for ques_id, ques_value in vals.items():
    #                 answer_score = ''
    #                 if not report_created:
    #                     independent_quiz_participation_id = request.env['quiz.report'].sudo().create(
    #                         {'quiz_id': quizzes_exist.id,
    #                          'start_datetime': datetime.now(),
    #                          'user_id': request.env.user.id,
    #                          'partner_id': request.env.user.partner_id.id,
    #                          'attempts_num': 1,
    #                          'quiz_completed': True,
    #                          })
    #                     slide_question = request.env['slide.question'].sudo().search([('id','=',ques_id)])
    #                     independent_ans_ids = slide_question.answer_ids
    #                     for answers in independent_ans_ids:
    #                         if answers.is_correct:
    #                             correct_answer = answers.text_value
    #                             if ques_value == correct_answer:
    #                                 submit_correct_answer = True
    #                                 answer_score = answers.answer_score
    #                     quizzes_report_line = request.env['quiz.report.line'].sudo().create({'quiz_report_id': independent_quiz_participation_id.id,
    #                                                                           'quiz_id': quizzes_exist.id,'quiz_question_id': ques_id,
    #                                                                           'selected_answer': ques_value,'correct_answer': correct_answer,
    #                                                                           'answer_score': answer_score})
    #
    #                     print('TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT',type(int(quizzes_report_line.quiz_question_id.id)))
    #
    #                     if independent_ans_ids:
    #                         for rec in independent_ans_ids:
    #                             res = request.env['answer.line'].sudo().create({'quiz_report_line_id':quizzes_report_line.id,
    #                                                                             'slide_ans_id':rec.id,
    #                                                                             })
    #                     if independent_quiz_participation_id:
    #                         report_created = True
    #                 else:
    #                     updated_quiz_report_id = request.env['quiz.report'].sudo().search([('id','=',independent_quiz_participation_id.id)])
    #                     print('11111111111111111111111111111111111111111',independent_quiz_participation_id)
    #                     slide_question = request.env['slide.question'].sudo().search([('id','=',ques_id)])
    #                     independent_ans_ids = slide_question.answer_ids
    #                     for answers in independent_ans_ids:
    #                         if answers.is_correct:
    #                             correct_answer = answers.text_value
    #                             if ques_value == correct_answer:
    #                                 submit_correct_answer = True
    #                                 answer_score = answers.answer_score
    #                     report_created = True
    #
    #                 first_qus = False
    #                 first_qus_bool = False
    #                 qus_lst = []
    #                 if quizzes_exist.custom_quiz_ids:
    #                     for qus in quizzes_exist.custom_quiz_ids:
    #                         qus_lst.append(qus.id)
    #                         if not first_qus_bool:
    #                             first_qus = qus.id
    #                             first_qus_bool = True
    #
    #                 values.update({
    #                     'quizzes': quizzes_exist,
    #                     'user': request.env.user,
    #                     'is_public_user': request.website.is_public_user(),
    #                     'first_qus': first_qus,
    #                     'independent_quiz_participation_id':independent_quiz_participation_id
    #                 })
    #     return request.render('ecom_lms.submit_ecom_independent_quizzes_main', values)
    

    @http.route(['/start/quizzes/<model("quizzes.question"):quizzes>'], type='http', auth="public", website=True,)
    def start_quiz(self, quizzes, **kw):
        if request.env.user.id == request.env.ref('base.public_user').id:
            return request.render('web.login', {})
        else:
            if quizzes:
                quiz_report_exist = request.env['quiz.report'].sudo().search([('quiz_id', '=', quizzes.id)])
                quizzes_exist = request.env['quizzes.question'].sudo().search([('id', '=', quizzes.id)])
                current_user = request.env.user.partner_id.id
                if quizzes_exist:
                    for quiz in quizzes_exist:
                        no_of_attempts = 0
                        attendee_exist = request.env['quiz.partner'].sudo().search(
                            [('quiz_id', '=', quiz.id), ('partner_id', '=', current_user)])
                        if not attendee_exist:
                            quiz.no_of_attempts += 1
                        else:
                            no_of_attempts = quiz.no_of_attempts
                        quiz_update = request.env['quiz.report'].sudo().write(
                            {'quiz_id': quiz.id, 'attendee_ids': [4, current_user]})
                # if not quiz_report_exist:
                #     vals = { 'quiz_id':quizzes.id,
                #              'responsible_person_id':quizzes.responsible_person_id.id,
                #              'description_short':quizzes.description_short,
                #              'partner_email':quizzes.responsible_person_id.email,
                #              'no_of_attempts':quizzes.no_of_attempts,
                #              'attendee_ids':quizzes.quiz_attendee_name,
                #              'create_date':quizzes.create_date,
                #     }
                #     quiz_report = request.env['quiz.report'].create(vals)
                independent_quiz_partner_lst = []
                cr = request.env.cr
                cr.execute('SELECT id FROM quiz_partner where quiz_id = %s',
                           (quizzes.id,))
                independent_quiz_partners = cr.fetchall()
                if independent_quiz_partners:
                    for independent_quiz in independent_quiz_partners:
                        independent_quiz_partner_id = request.env['quiz.partner'].sudo().browse(independent_quiz)

                        if independent_quiz_partner_id.partner_id:
                            independent_quiz_partner_lst.append(independent_quiz_partner_id.partner_id.id)

                    if request.env.user.partner_id.id not in independent_quiz_partner_lst:
                        independent_quiz_partner = request.env['quiz.partner'].sudo().create(
                            {'partner_id': request.env.user.partner_id.id,
                             'quiz_id': quizzes.id, })
                else:
                    independent_quiz_partner = request.env['quiz.partner'].sudo().create(
                        {'partner_id': request.env.user.partner_id.id,
                         'quiz_id': quizzes.id, })

                independent_quiz_subscribed = False
                # journey_completion = 0
                # journey_completed = False
                independent_quiz_count = 0
                if quizzes.sudo().quiz_attendee:
                    for independent_quiz_partner in quizzes.quiz_attendee:
                        if independent_quiz_partner.partner_id == request.env.user.partner_id:
                            # journey_completion = journey_partner.journey_completion
                            # journey_completed = journey_partner.journey_completed_mail
                            independent_quiz_count = independent_quiz_count + 1

                if independent_quiz_count > 0:
                    independent_quiz_subscribed = True

                # independent_quiz_participation_id = request.env['quiz.report'].sudo().create(
                #     {'quiz_id': quizzes.id,
                #      'start_datetime': datetime.now(),
                #      'user_id': request.env.user.id,
                #      'partner_id': request.env.user.partner_id.id,
                #      'attempts_num': 1})

                first_qus = False
                first_qus_bool = False
                qus_lst = []
                if quizzes.custom_quiz_ids:
                    for qus in quizzes.custom_quiz_ids:
                        qus_lst.append(qus.id)
                        if not first_qus_bool:
                            first_qus = qus.id
                            first_qus_bool = True

                values = {
                    'independent_quiz_subscribed': independent_quiz_subscribed,
                    'quizzes': quizzes,
                    'user': request.env.user,
                    'is_public_user': request.website.is_public_user(),
                    'first_qus': first_qus
                }
                # return request.render('ecom_lms.ecom_independent_quizzes_main', values)
                return request.render('ecom_lms.ecom_independent_quizzes_main', values)

    # @http.route(['/quizzes/submitted-ans'], type='http', auth="public", website=True,)
    # def submitted_answer(self,**kw):
    #     user_id = kw.get('quizzes.users')
    #     internal_user = request.env['res.users'].browse(int(user_id))
    #     template_id = request.env.ref('ecom_lms.independent_quiz_email_template')
    #     outgoing_server_name = request.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
    #     if outgoing_server_name and template_id:
    #         template_id.email_from = outgoing_server_name
    #         template_id.email_to = internal_user.partner_id.email
    #         # mail_sent = template_id.send_mail(internal_user.id, force_send=True)
    #         mail_sent = True
    #         if mail_sent:
    #             return request.render('ecom_lms.customer_thanks', {})

    @http.route([
        '/journey/pwa/<model("course.journey"):journey>',
    ], type='http', auth="public", website=True, sitemap=sitemap_slide)
    def channel_pwa_journey(self, journey, category=None, tag=None, page=1, slide_type=None, uncategorized=False,
                        sorting=None,
                        search=None, **kw):

        if journey:
            print("aksjdbv")
            # pager_url = "/slides/%s" % (journey.id)

            journey_subscribed = False
            journey_completion = 0
            journey_completed = False
            journey_count = 0
            if journey.journey_channel_partner_ids:
                for journey_partner in journey.journey_channel_partner_ids:
                    if journey_partner.partner_id == request.env.user.partner_id:
                        journey_completion = journey_partner.journey_completion
                        journey_completed = journey_partner.journey_completed_mail
                        journey_count = journey_count + 1
            if journey_count > 0:
                journey_subscribed = True
            values = {
                'journey_subscribed': journey_subscribed,
                'journey_completion': journey_completion,
                'journey_completed': journey_completed,
                'journey': journey,
                'user': request.env.user,
                'is_public_user': request.website.is_public_user(),
            }
            return request.render('ecom_lms.pwa_journey_all_courses_template', values)


    @http.route([
        '/quizzes/<model("quizzes.question"):quizzes>',
    ], type='http', auth="public", website=True, sitemap=sitemap_slide)
    def quizzes_question(self, quizzes, category=None, tag=None, page=1, slide_type=None, uncategorized=False,
                         sorting=None,
                         search=None, **kw):
        """
        Will return all necessary data to display the requested slide_channel along with a possible category.
        """
        if quizzes:
            independent_quiz_subscribed = False
            # if quizzes.quiz_attendee.partner_id.id != request.env.user.partner_id.id:
            #     independent_quiz_subscribed = False
            # else:
            #     independent_quiz_subscribed = True
            pager_url = "/slides/%s" % (quizzes.id)

            values = {
                'quizzes': quizzes,
                'independent_quiz_subscribed': independent_quiz_subscribed,
            }
            return request.render('ecom_lms.quiz_card_view', values)

    @http.route(['/certificate/courses/<model("survey.survey"):certification>/<model("res.users"):employee>', ],
                type='http', auth="public", website=True, sitemap=sitemap_slide)
    def certificate_courses_employee(self, employee, certification, category=None, tag=None, page=1, slide_type=None,
                                     uncategorized=False, sorting=None,
                                     search=None, **kw):
        """
        Will return all necessary data to display the requested slide_channel along with a possible category.
        """
        if certification and employee:
            certification_course_lst = []
            user_input_ids = request.env['survey.user_input'].sudo().search(
                [('scoring_success', '=', True), ('partner_id', '=', employee.partner_id.id),
                 ('survey_id', '=', certification.id)])
            for user_input in user_input_ids:
                if user_input.slide_id.channel_id:
                    if user_input.slide_id.channel_id.id not in certification_course_lst:
                        certification_course_lst.append(user_input.slide_id.channel_id.id)

            certification_course_details = request.env['slide.channel'].sudo().browse(certification_course_lst)

            values = {
                'employee': employee,
                'certification_course_details': certification_course_details,
                'user': request.env.user,
                'is_public_user': request.website.is_public_user(),
            }
            return request.render('ecom_lms.employee_certification_course_card_temp_id', values)

    @http.route(['/certificate/employee/<model("res.users"):employee>', ], type='http', auth="public", website=True,
                sitemap=sitemap_slide)
    def certificate_employee(self, employee, category=None, tag=None, page=1, slide_type=None, uncategorized=False,
                             sorting=None,
                             search=None, **kw):
        """
        Will return all necessary data to display the requested slide_channel along with a possible category.
        """
        if employee:
            certification_lst = []
            user_input_ids = request.env['survey.user_input'].sudo().search(
                [('scoring_success', '=', True), ('partner_id', '=', employee.partner_id.id)])
            for user_input in user_input_ids:
                if user_input.survey_id.id not in certification_lst:
                    certification_lst.append(user_input.survey_id.id)

            certification_details = request.env['survey.survey'].sudo().browse(certification_lst)

            values = {
                'employee': employee,
                'certification_details': certification_details,
                'user': request.env.user,
                'is_public_user': request.website.is_public_user(),
            }
            return request.render('ecom_lms.employee_certification_card_details', values)

    @http.route(['/completed-course/employee/<model("res.users"):employee>', ], type='http', auth="public",
                website=True, sitemap=sitemap_slide)
    def completed_course_employee(self, employee, category=None, tag=None, page=1, slide_type=None, uncategorized=False,
                                  sorting=None,
                                  search=None, **kw):
        """
        Will return all necessary data to display the requested slide_channel along with a possible category.
        """
        if employee:
            course_lst = []
            channel_partner_ids = request.env['slide.channel.partner'].sudo().search(
                [('completion', '=', 100), ('partner_id', '=', employee.partner_id.id)])
            for channel_partner in channel_partner_ids:
                if channel_partner.channel_id.id not in course_lst:
                    course_lst.append(channel_partner.channel_id.id)

            completed_course_details = request.env['slide.channel'].sudo().browse(course_lst)

            values = {
                'employee': employee,
                'completed_course_details': completed_course_details,
                'user': request.env.user,
                'is_public_user': request.website.is_public_user(),
            }
            return request.render('ecom_lms.employee_course_completed_card_details', values)
        
        
    @http.route([
        '/pwa/join/journey/<model("course.journey"):journey>',
    ], type='http', auth="public", website=True, sitemap=sitemap_slide)
    def join_pwa_channel_journey(self, journey, category=None, tag=None, page=1, slide_type=None, uncategorized=False,
                             sorting=None,
                             search=None, **kw):
        """
        Will return all necessary data to display the requested slide_channel along with a possible category.
        """
        if journey:

            journey_partner_lst = []
            cr = request.env.cr
            cr.execute('SELECT id FROM course_journey_partner where journey_id = %s',
                       (journey.id,))
            jouney_partners = cr.fetchall()
            if jouney_partners:
                for journey_partner in jouney_partners:
                    journey_partner_id = request.env['course.journey.partner'].sudo().browse(journey_partner)

                    if journey_partner_id.partner_id:
                        journey_partner_lst.append(journey_partner_id.partner_id.id)

                if request.env.user.partner_id.id not in journey_partner_lst:
                    channel_partner = request.env['course.journey.partner'].sudo().create(
                        {'partner_id': request.env.user.partner_id.id,
                         'journey_id': journey.id, })

                    sum = 0.0
                    no_of_courses = 0.0
                    journey_comp = 0
                    channel_partner.journey_completion = 0.0
                    if journey.courses_ids:
                        for course in journey.courses_ids:
                            no_of_courses = no_of_courses + 1
                            if course.sudo().course_id.sudo().channel_partner_ids:
                                for course_partner in course.sudo().course_id.channel_partner_ids:
                                    if course_partner.partner_id == channel_partner.partner_id:
                                        sum = sum + course_partner.completion
                        journey_comp = sum / no_of_courses
                        if journey_comp == 100:
                            channel_partner.journey_completed_mail = True
                            if not channel_partner.journey_complete_date:
                                channel_partner.journey_complete_date = datetime.now()

                        else:
                            channel_partner.journey_completed_mail = False
                            channel_partner.journey_complete_date = ''
                    channel_partner.journey_completion = journey_comp
                    channel_partner.journey_completed = False
                    if channel_partner.journey_completed_mail and channel_partner.journey_complete_date and channel_partner.journey_completion == 100:
                        complet_date = channel_partner.journey_complete_date.replace(second=0, microsecond=0)
                        current_date = datetime.now()
                        current_date_new = current_date.replace(second=0, microsecond=0)
                        if current_date_new == complet_date:
                            template_id = request.env.ref('ecom_lms.email_template_journey_completed')
                            outgoing_server_name = request.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
                            if outgoing_server_name and template_id:
                                template_id.email_from = outgoing_server_name
                                a = template_id.send_mail(channel_partner.id, force_send=True)
                                channel_partner.journey_completed = True

                        else:
                            channel_partner.journey_completed = False
            else:
                channel_partner = request.env['course.journey.partner'].sudo().create(
                    {'partner_id': request.env.user.partner_id.id,
                     'journey_id': journey.id, })

                sum = 0.0
                no_of_courses = 0.0
                journey_comp = 0
                channel_partner.journey_completion = 0.0
                if journey.courses_ids:
                    for course in journey.courses_ids:
                        no_of_courses = no_of_courses + 1
                        if course.sudo().course_id.sudo().channel_partner_ids:
                            for course_partner in course.sudo().course_id.channel_partner_ids:
                                if course_partner.partner_id == channel_partner.partner_id:
                                    sum = sum + course_partner.completion
                    journey_comp = sum / no_of_courses
                    if journey_comp == 100:
                        channel_partner.journey_completed_mail = True
                        if not channel_partner.journey_complete_date:
                            channel_partner.journey_complete_date = datetime.now()

                    else:
                        channel_partner.journey_completed_mail = False
                        channel_partner.journey_complete_date = ''
                channel_partner.journey_completion = journey_comp
                channel_partner.journey_completed = False
                if channel_partner.journey_completed_mail and channel_partner.journey_complete_date and channel_partner.journey_completion == 100:
                    complet_date = channel_partner.journey_complete_date.replace(second=0, microsecond=0)
                    current_date = datetime.now()
                    current_date_new = current_date.replace(second=0, microsecond=0)
                    if current_date_new == complet_date:
                        template_id = request.env.ref('ecom_lms.email_template_journey_completed')
                        outgoing_server_name = request.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
                        if outgoing_server_name and template_id:
                            template_id.email_from = outgoing_server_name
                            a = template_id.send_mail(channel_partner.id, force_send=True)
                            channel_partner.journey_completed = True

                    else:
                        channel_partner.journey_completed = False

            journey_subscribed = False
            journey_completion = 0
            journey_completed = False
            journey_count = 0
            if journey.journey_channel_partner_ids:
                for journey_partner in journey.journey_channel_partner_ids:
                    if journey_partner.partner_id == request.env.user.partner_id:
                        journey_completion = journey_partner.journey_completion
                        journey_completed = journey_partner.journey_completed_mail
                        journey_count = journey_count + 1

            if journey_count > 0:
                journey_subscribed = True

            values = {
                'journey_subscribed': journey_subscribed,
                'journey_completion': journey_completion,
                'journey_completed': journey_completed,
                'journey': journey,
                'user': request.env.user,
                'is_public_user': request.website.is_public_user(),
            }
            return request.render('ecom_lms.pwa_journey_all_courses_template', values)
        
        

    @http.route([
        '/join/journey/<model("course.journey"):journey>',
    ], type='http', auth="public", website=True, sitemap=sitemap_slide)
    def join_channel_journey(self, journey, category=None, tag=None, page=1, slide_type=None, uncategorized=False,
                             sorting=None,
                             search=None, **kw):
        """
        Will return all necessary data to display the requested slide_channel along with a possible category.
        """
        if journey:

            journey_partner_lst = []
            cr = request.env.cr
            cr.execute('SELECT id FROM course_journey_partner where journey_id = %s',
                       (journey.id,))
            jouney_partners = cr.fetchall()
            if jouney_partners:
                for journey_partner in jouney_partners:
                    journey_partner_id = request.env['course.journey.partner'].sudo().browse(journey_partner)

                    if journey_partner_id.partner_id:
                        journey_partner_lst.append(journey_partner_id.partner_id.id)

                if request.env.user.partner_id.id not in journey_partner_lst:
                    channel_partner = request.env['course.journey.partner'].sudo().create(
                        {'partner_id': request.env.user.partner_id.id,
                         'journey_id': journey.id, })

                    sum = 0.0
                    no_of_courses = 0.0
                    journey_comp = 0
                    channel_partner.journey_completion = 0.0
                    if journey.courses_ids:
                        for course in journey.courses_ids:
                            no_of_courses = no_of_courses + 1
                            if course.sudo().course_id.sudo().channel_partner_ids:
                                for course_partner in course.sudo().course_id.channel_partner_ids:
                                    if course_partner.partner_id == channel_partner.partner_id:
                                        sum = sum + course_partner.completion
                        journey_comp = sum / no_of_courses
                        if journey_comp == 100:
                            channel_partner.journey_completed_mail = True
                            if not channel_partner.journey_complete_date:
                                channel_partner.journey_complete_date = datetime.now()

                        else:
                            channel_partner.journey_completed_mail = False
                            channel_partner.journey_complete_date = ''
                    channel_partner.journey_completion = journey_comp
                    channel_partner.journey_completed = False
                    if channel_partner.journey_completed_mail and channel_partner.journey_complete_date and channel_partner.journey_completion == 100:
                        complet_date = channel_partner.journey_complete_date.replace(second=0, microsecond=0)
                        current_date = datetime.now()
                        current_date_new = current_date.replace(second=0, microsecond=0)
                        if current_date_new == complet_date:
                            template_id = request.env.ref('ecom_lms.email_template_journey_completed')
                            outgoing_server_name = request.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
                            if outgoing_server_name and template_id:
                                template_id.email_from = outgoing_server_name
                                a = template_id.send_mail(channel_partner.id, force_send=True)
                                channel_partner.journey_completed = True

                        else:
                            channel_partner.journey_completed = False
            else:
                channel_partner = request.env['course.journey.partner'].sudo().create(
                    {'partner_id': request.env.user.partner_id.id,
                     'journey_id': journey.id, })

                sum = 0.0
                no_of_courses = 0.0
                journey_comp = 0
                channel_partner.journey_completion = 0.0
                if journey.courses_ids:
                    for course in journey.courses_ids:
                        no_of_courses = no_of_courses + 1
                        if course.sudo().course_id.sudo().channel_partner_ids:
                            for course_partner in course.sudo().course_id.channel_partner_ids:
                                if course_partner.partner_id == channel_partner.partner_id:
                                    sum = sum + course_partner.completion
                    journey_comp = sum / no_of_courses
                    if journey_comp == 100:
                        channel_partner.journey_completed_mail = True
                        if not channel_partner.journey_complete_date:
                            channel_partner.journey_complete_date = datetime.now()

                    else:
                        channel_partner.journey_completed_mail = False
                        channel_partner.journey_complete_date = ''
                channel_partner.journey_completion = journey_comp
                channel_partner.journey_completed = False
                if channel_partner.journey_completed_mail and channel_partner.journey_complete_date and channel_partner.journey_completion == 100:
                    complet_date = channel_partner.journey_complete_date.replace(second=0, microsecond=0)
                    current_date = datetime.now()
                    current_date_new = current_date.replace(second=0, microsecond=0)
                    if current_date_new == complet_date:
                        template_id = request.env.ref('ecom_lms.email_template_journey_completed')
                        outgoing_server_name = request.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
                        if outgoing_server_name and template_id:
                            template_id.email_from = outgoing_server_name
                            a = template_id.send_mail(channel_partner.id, force_send=True)
                            channel_partner.journey_completed = True

                    else:
                        channel_partner.journey_completed = False

            journey_subscribed = False
            journey_completion = 0
            journey_completed = False
            journey_count = 0
            if journey.journey_channel_partner_ids:
                for journey_partner in journey.journey_channel_partner_ids:
                    if journey_partner.partner_id == request.env.user.partner_id:
                        journey_completion = journey_partner.journey_completion
                        journey_completed = journey_partner.journey_completed_mail
                        journey_count = journey_count + 1

            if journey_count > 0:
                journey_subscribed = True

            values = {
                'journey_subscribed': journey_subscribed,
                'journey_completion': journey_completion,
                'journey_completed': journey_completed,
                'journey': journey,
                'user': request.env.user,
                'is_public_user': request.website.is_public_user(),
            }
            return request.render('ecom_lms.journey_main', values)

    @http.route('/slides/my/languages/change', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_my_languages_hi(self, **post):
        """ Home page for eLearning platform. Is mainly a container page, does not allow search / filter. """
        domain = request.website.website_domain()
        channels_all = request.env['slide.channel'].search(domain)
        if post.get('language') == 'english':
            selected_lang = 'english'
            request.env.user.lang_from_website = 'english'

        if post.get('language') == 'hindi':
            selected_lang = 'hindi'
            request.env.user.lang_from_website = 'hindi'

        if post.get('language') == 'gujarati':
            selected_lang = 'gujarati'
            request.env.user.lang_from_website = 'gujarati'

        if post.get('language') == 'telugu':
            selected_lang = 'telugu'
            request.env.user.lang_from_website = 'telugu'

        if post.get('language') == 'marathi':
            selected_lang = 'marathi'
            request.env.user.lang_from_website = 'marathi'

        if post.get('language') == 'assamese':
            selected_lang = 'assamese'
            request.env.user.lang_from_website = 'assamese'

        if post.get('language') == 'tamil':
            selected_lang = 'tamil'
            request.env.user.lang_from_website = 'tamil'

        if post.get('language') == 'kannada':
            selected_lang = 'kannada'
            request.env.user.lang_from_website = 'kannada'

        if post.get('language') == 'malyalam':
            selected_lang = 'malyalam'
            request.env.user.lang_from_website = 'malyalam'

        if post.get('language') == 'select':
            selected_lang = 'select'
            request.env.user.lang_from_website = 'No Language Selected'

        if not post.get('language'):
            if request.env.user.lang_from_website == 'No Language Selected':
                selected_lang = 'select'
            else:
                selected_lang = request.env.user.lang_from_website

        if not request.env.user._is_public():
            # If a course is completed, we don't want to see it in first position but in last
            channels_my = channels_all.filtered(lambda channel: channel.is_member).sorted(
                lambda channel: 0 if channel.completed else channel.completion, reverse=True)[:3]
        else:
            channels_my = request.env['slide.channel']
        channels_popular_ids = channels_all.sorted('total_votes', reverse=True)[:3]
        channels_newest_ids = channels_all.sorted('create_date', reverse=True)[:3]

        achievements = request.env['gamification.badge.user'].sudo().search([('badge_id.is_published', '=', True)],
                                                                            limit=5)
        if request.env.user._is_public():
            challenges = None
            challenges_done = None
        else:
            challenges = request.env['gamification.challenge'].sudo().search([
                ('challenge_category', '=', 'slides'),
                ('reward_id.is_published', '=', True)
            ], order='id asc', limit=5)
            challenges_done = request.env['gamification.badge.user'].sudo().search([
                ('challenge_id', 'in', challenges.ids),
                ('user_id', '=', request.env.user.id),
                ('badge_id.is_published', '=', True)
            ]).mapped('challenge_id')

        users = request.env['res.users'].sudo().search([
            ('karma', '>', 0),
            ('website_published', '=', True)], limit=5, order='karma desc')

        channels_completed_lst = []
        for channels_completed in channels_all:
            channels_completed_user_lst = []
            for channels_completed_partner in channels_completed.sudo().channel_partner_ids:
                if channels_completed_partner.completion == 100:
                    user = request.env['res.users'].search(
                        [('partner_id', '=', channels_completed_partner.partner_id.id)], limit=1)
                    if user:
                        channels_completed_user_lst.append(user.id)
            if request.env.user.id in channels_completed_user_lst:
                if selected_lang != 'select':
                    if channels_completed.lang_values == selected_lang:
                        channels_completed_lst.append(channels_completed.id)
                else:
                    channels_completed_lst.append(channels_completed.id)

        channels_complete = request.env['slide.channel'].sudo().browse(channels_completed_lst)

        channels_suggested_lst = []
        for channels_suggested in channels_all:
            if channels_suggested.custom_visibility == 'semi_public':
                suggested_user_lst = []
                for channels_partner in channels_suggested.sudo().channel_partner_ids:
                    user = request.env['res.users'].search([('partner_id', '=', channels_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        suggested_user_lst.append(user.id)
                if request.env.user.id not in suggested_user_lst and request.env.user in channels_suggested.nominated_user_ids:
                    if selected_lang != 'select':
                        if channels_suggested.lang_values == selected_lang:
                            channels_suggested_lst.append(channels_suggested.id)
                    else:
                        channels_suggested_lst.append(channels_suggested.id)

        completed_course_list = []
        for completed_course in channels_all:
            if completed_course.custom_visibility != 'semi_public':

                for channels_partner in completed_course.sudo().channel_partner_ids:
                    if channels_partner.completion == 100:
                        if completed_course.id not in completed_course_list:
                            completed_course_list.append(completed_course.id)
        channels_comp_suggested_lst = []
        for channels_completed_suggested in completed_course_list:
            channel_comp_suggested = request.env['slide.channel'].sudo().browse(channels_completed_suggested)
            suggested_comp_user_lst = []
            for partner_val in channel_comp_suggested.sudo().channel_partner_ids:
                user_val = request.env['res.users'].search([('partner_id', '=', partner_val.partner_id.id)], limit=1)
                if user_val:
                    suggested_comp_user_lst.append(user_val.id)
            if request.env.user.id not in suggested_comp_user_lst:
                if selected_lang != 'select':
                    if channel_comp_suggested.lang_values == selected_lang:
                        channels_comp_suggested_lst.append(channel_comp_suggested.id)
                else:
                    channels_comp_suggested_lst.append(channel_comp_suggested.id)

        just_started_courses = []
        recent_start_courses_lst = []
        today_date = datetime.now()
        today_only_date = today_date.date()
        started_courses_ids = request.env['slide.channel.partner'].sudo().search([])
        for started in started_courses_ids:
            if started.create_date:
                if started.create_date.date() == today_only_date:
                    just_started_courses.append(started.channel_id.id)

        if len(just_started_courses) > 0:
            for just_started in just_started_courses:
                started_user_lst = []
                channel_just_started = request.env['slide.channel'].sudo().browse(just_started)
                for just_start in channel_just_started.sudo().channel_partner_ids:
                    user_val = request.env['res.users'].search([('partner_id', '=', just_start.partner_id.id)], limit=1)
                    if user_val:
                        started_user_lst.append(user_val.id)
                if request.env.user.id not in started_user_lst:
                    if selected_lang != 'select':
                        if channel_just_started.lang_values == selected_lang:
                            recent_start_courses_lst.append(channel_just_started.id)
                    else:
                        recent_start_courses_lst.append(channel_just_started.id)

        interested_course_lst = []
        for interested_course in channels_all:
            if interested_course.course_category_id in request.env.user.topic_of_interest_ids:
                interested_user_lst = []
                if interested_course.sudo().channel_partner_ids:
                    for partner_val1 in interested_course.sudo().channel_partner_ids:
                        user_val1 = request.env['res.users'].search([('partner_id', '=', partner_val1.partner_id.id)],
                                                                    limit=1)
                        if user_val1:
                            interested_user_lst.append(user_val1.id)

                if request.env.user.id not in interested_user_lst:
                    if selected_lang != 'select':
                        if interested_course.lang_values == selected_lang:
                            interested_course_lst.append(interested_course.id)
                    else:
                        interested_course_lst.append(interested_course.id)

        final_suggested_lst = channels_suggested_lst + channels_comp_suggested_lst + recent_start_courses_lst + interested_course_lst
        final_suggested_lst = list(set(final_suggested_lst))
        channels_suggested = request.env['slide.channel'].sudo().browse(final_suggested_lst)

        channels_resumed_learning_lst = []
        for channels_resumed in channels_all:
            channels_resumed_user_lst = []
            # if channels_popular.custom_visibility=='private':
            for channels_resumed_partner in channels_resumed.sudo().channel_partner_ids:
                if channels_resumed_partner.completion < 100 and channels_resumed_partner.completion > 0:
                    user = request.env['res.users'].search(
                        [('partner_id', '=', channels_resumed_partner.partner_id.id)], limit=1)
                    if user:
                        channels_resumed_user_lst.append(user.id)
            if request.env.user.id in channels_resumed_user_lst:
                date_now = datetime.now()
                if channels_resumed.course_close_date:
                    if date_now.date() <= channels_resumed.course_close_date.date():
                        if selected_lang != 'select':
                            if channels_resumed.lang_values == selected_lang:
                                channels_resumed_learning_lst.append(channels_resumed.id)
                        else:
                            channels_resumed_learning_lst.append(channels_resumed.id)
                else:
                    if selected_lang != 'select':
                        if channels_resumed.lang_values == selected_lang:
                            channels_resumed_learning_lst.append(channels_resumed.id)
                    else:
                        channels_resumed_learning_lst.append(channels_resumed.id)

        channels_resumed = request.env['slide.channel'].sudo().browse(channels_resumed_learning_lst)

        channels_assigned_lst = []
        for channels_assigned in channels_all:
            attendee_user_lst = []
            # if channels_popular.custom_visibility=='private':
            for channels_partner in channels_assigned.sudo().channel_partner_ids:
                if channels_partner.completion != 100:
                    user = request.env['res.users'].search([('partner_id', '=', channels_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        attendee_user_lst.append(user.id)
            if request.env.user.id in attendee_user_lst:
                if channels_assigned.course_close_date:
                    date_now = datetime.now()
                    if date_now.date() <= channels_assigned.course_close_date.date():
                        if selected_lang != 'select':
                            if channels_assigned.lang_values == selected_lang:
                                channels_assigned_lst.append(channels_assigned.id)
                        else:
                            channels_assigned_lst.append(channels_assigned.id)

                else:
                    if selected_lang != 'select':
                        if channels_assigned.lang_values == selected_lang:
                            channels_assigned_lst.append(channels_assigned.id)
                    else:
                        channels_assigned_lst.append(channels_assigned.id)

        channels_assign = request.env['slide.channel'].browse(channels_assigned_lst)

        channels_featured_lst = []
        for channels_featured in channels_all:
            featured_user_lst = []
            if channels_featured.is_featured and channels_featured.featured_group_id:
                if channels_featured.featured_group_id in request.env.user.groups_id:
                    if selected_lang != 'select':
                        if channels_featured.lang_values == selected_lang:
                            channels_featured_lst.append(channels_featured.id)
                    else:
                        channels_featured_lst.append(channels_featured.id)

        channels_feature = request.env['slide.channel'].browse(channels_featured_lst)
        
        values = self._prepare_user_values(**post)
        values.update({
            'channels_feature': channels_feature,
            'channels_assign': channels_assign,
            'channels_complete': channels_complete,
            'channels_resumed': channels_resumed,
            'channels_my': channels_my,
            'channels_suggested': channels_suggested,
            # 'channels_popular': channels_popular,
            # 'channels_newest': channels_newest,
            'achievements': achievements,
            'users': users,
            'top3_users': self._get_top3_users(),
            'challenges': challenges,
            'challenges_done': challenges_done,
            'search_tags': request.env['slide.channel.tag'],
            'language_change': True,
            'language_switched': True
        })
        return request.render('website_slides.courses_home', values)

    @http.route('/slides/my/languages', type='http', auth="public", website=True, sitemap=True)
    def slides_channel_my_languages(self, **post):
        """ Home page for eLearning platform. Is mainly a container page, does not allow search / filter. """
        domain = request.website.website_domain()
        channels_all = request.env['slide.channel'].search(domain)
        if request.env.user.lang == 'en_IN':
            selected_lang = 'english'

        if request.env.user.lang == 'hi_IN':
            selected_lang = 'hindi'

        if request.env.user.lang == 'gu_IN':
            selected_lang = 'gujarati'

        if request.env.user.lang == 'te_IN':
            selected_lang = 'telugu'

        if request.env.user.lang == 'ma_IN':
            selected_lang = 'marathi'

        if request.env.user.lang == 'assa_IN':
            selected_lang = 'assamese'

        if request.env.user.lang == 'ta_IN':
            selected_lang = 'tamil'

        if request.env.user.lang == 'ka_IN':
            selected_lang = 'kannada'

        if request.env.user.lang == 'mal_IN':
            selected_lang = 'malyalam'

        if not request.env.user._is_public():
            # If a course is completed, we don't want to see it in first position but in last
            channels_my = channels_all.filtered(lambda channel: channel.is_member).sorted(
                lambda channel: 0 if channel.completed else channel.completion, reverse=True)[:3]
        else:
            channels_my = request.env['slide.channel']
        channels_popular_ids = channels_all.sorted('total_votes', reverse=True)[:3]
        channels_newest_ids = channels_all.sorted('create_date', reverse=True)[:3]

        achievements = request.env['gamification.badge.user'].sudo().search([('badge_id.is_published', '=', True)],
                                                                            limit=5)
        if request.env.user._is_public():
            challenges = None
            challenges_done = None
        else:
            challenges = request.env['gamification.challenge'].sudo().search([
                ('challenge_category', '=', 'slides'),
                ('reward_id.is_published', '=', True)
            ], order='id asc', limit=5)
            challenges_done = request.env['gamification.badge.user'].sudo().search([
                ('challenge_id', 'in', challenges.ids),
                ('user_id', '=', request.env.user.id),
                ('badge_id.is_published', '=', True)
            ]).mapped('challenge_id')

        users = request.env['res.users'].sudo().search([
            ('karma', '>', 0),
            ('website_published', '=', True)], limit=5, order='karma desc')

        # channels_popular_lst=[]
        # for channels_popular in channels_popular_ids:
        #     if channels_popular.custom_visibility=='private':
        #         popular_user_lst= []
        #         for channels_popular_partner in channels_popular.sudo().channel_partner_ids:
        #             user= request.env['res.users'].search([('partner_id','=',channels_popular_partner.partner_id.id)],limit=1)
        #             if user:
        #                 popular_user_lst.append(user.id)
        #         if request.env.user.id in popular_user_lst:
        #             if channels_popular.lang_values == selected_lang:
        #                 channels_popular_lst.append(channels_popular.id)
        #
        #
        #     elif channels_popular.custom_visibility=='semi_public':
        #         popular_user_lst= []
        #         for channels_popular_user in channels_popular.sudo().nominated_user_ids:
        #             popular_user_lst.append(channels_popular_user.id)
        #         if request.env.user.id in popular_user_lst:
        #             if channels_popular.lang_values == selected_lang:
        #                 channels_popular_lst.append(channels_popular.id)
        #     else:
        #         if channels_popular.lang_values == selected_lang:
        #             channels_popular_lst.append(channels_popular.id)
        #
        # channels_popular=  request.env['slide.channel'].browse(channels_popular_lst)
        #
        #
        # channels_newest_lst=[]
        # for channels_newest in channels_newest_ids:
        #     if channels_newest.custom_visibility=='private':
        #         newest_user_lst= []
        #         for channels_newest_partner in channels_newest.sudo().channel_partner_ids:
        #             user= request.env['res.users'].search([('partner_id','=',channels_newest_partner.partner_id.id)],limit=1)
        #             if user:
        #                 channels_newest_lst.append(user.id)
        #         if request.env.user.id in channels_newest_lst:
        #             if channels_newest.lang_values == selected_lang:
        #                 channels_newest_lst.append(channels_newest.id)
        #
        #     elif channels_newest.custom_visibility=='semi_public':
        #         newest_user_lst= []
        #         for channels_newest_user in channels_newest.sudo().nominated_user_ids:
        #             newest_user_lst.append(channels_newest_user.id)
        #
        #         if request.env.user.id in newest_user_lst:
        #             if channels_newest.lang_values == selected_lang:
        #                 channels_newest_lst.append(channels_newest.id)
        #     else:
        #         if channels_newest.lang_values == selected_lang:
        #             channels_newest_lst.append(channels_newest.id)
        # channels_newest=  request.env['slide.channel'].browse(channels_newest_lst)

        channels_completed_lst = []
        for channels_completed in channels_all:
            channels_completed_user_lst = []
            for channels_completed_partner in channels_completed.sudo().channel_partner_ids:
                if channels_completed_partner.completion == 100:
                    user = request.env['res.users'].search(
                        [('partner_id', '=', channels_completed_partner.partner_id.id)], limit=1)
                    if user:
                        channels_completed_user_lst.append(user.id)
            if request.env.user.id in channels_completed_user_lst:
                if channels_completed.lang_values == selected_lang:
                    channels_completed_lst.append(channels_completed.id)

        channels_complete = request.env['slide.channel'].sudo().browse(channels_completed_lst)

        channels_featured_lst = []
        for channels_featured in channels_all:
            featured_user_lst = []
            if channels_featured.is_featured and channels_featured.featured_group_id:
                if channels_featured.featured_group_id in request.env.user.groups_id:
                    if channels_featured.lang_values == selected_lang:
                        channels_featured_lst.append(channels_featured.id)

        channels_feature = request.env['slide.channel'].sudo().browse(channels_featured_lst)

        channels_assigned_lst = []
        for channels_assigned in channels_all:
            attendee_user_lst = []
            # if channels_popular.custom_visibility=='private':
            for channels_partner in channels_assigned.sudo().channel_partner_ids:
                if channels_partner.completion != 100:
                    user = request.env['res.users'].search([('partner_id', '=', channels_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        attendee_user_lst.append(user.id)
            if request.env.user.id in attendee_user_lst:
                if channels_assigned.course_close_date:
                    date_now = datetime.now()
                    if date_now.date() <= channels_assigned.course_close_date.date():
                        if channels_assigned.lang_values == selected_lang:
                            channels_assigned_lst.append(channels_assigned.id)

                else:
                    if channels_assigned.lang_values == selected_lang:
                        channels_assigned_lst.append(channels_assigned.id)

        channels_assign = request.env['slide.channel'].sudo().browse(channels_assigned_lst)

        channels_resumed_learning_lst = []
        for channels_resumed in channels_all:
            channels_resumed_user_lst = []
            # if channels_popular.custom_visibility=='private':
            for channels_resumed_partner in channels_resumed.sudo().channel_partner_ids:
                if channels_resumed_partner.completion < 100 and channels_resumed_partner.completion > 0:
                    user = request.env['res.users'].search(
                        [('partner_id', '=', channels_resumed_partner.partner_id.id)], limit=1)
                    if user:
                        channels_resumed_user_lst.append(user.id)
            if request.env.user.id in channels_resumed_user_lst:
                date_now = datetime.now()
                if channels_resumed.course_close_date:
                    if date_now.date() <= channels_resumed.course_close_date.date():
                        if channels_resumed.lang_values == selected_lang:
                            channels_resumed_learning_lst.append(channels_resumed.id)
                else:
                    if channels_resumed.lang_values == selected_lang:
                        channels_resumed_learning_lst.append(channels_resumed.id)

        channels_resumed = request.env['slide.channel'].sudo().browse(channels_resumed_learning_lst)

        channels_suggested_lst = []
        for channels_suggested in channels_all:
            if channels_suggested.custom_visibility == 'semi_public':
                suggested_user_lst = []
                for channels_partner in channels_suggested.sudo().channel_partner_ids:
                    user = request.env['res.users'].search([('partner_id', '=', channels_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        suggested_user_lst.append(user.id)
                if request.env.user.id not in suggested_user_lst and request.env.user in channels_suggested.nominated_user_ids:
                    if channels_suggested.lang_values == selected_lang:
                        channels_suggested_lst.append(channels_suggested.id)

        completed_course_list = []
        for completed_course in channels_all:
            if completed_course.custom_visibility != 'semi_public':

                for channels_partner in completed_course.sudo().channel_partner_ids:
                    if channels_partner.completion == 100:
                        if completed_course.id not in completed_course_list:
                            completed_course_list.append(completed_course.id)
        channels_comp_suggested_lst = []
        for channels_completed_suggested in completed_course_list:
            channel_comp_suggested = request.env['slide.channel'].sudo().browse(channels_completed_suggested)
            suggested_comp_user_lst = []
            for partner_val in channel_comp_suggested.sudo().channel_partner_ids:
                user_val = request.env['res.users'].search([('partner_id', '=', partner_val.partner_id.id)], limit=1)
                if user_val:
                    suggested_comp_user_lst.append(user_val.id)
            if request.env.user.id not in suggested_comp_user_lst:
                if channel_comp_suggested.lang_values == selected_lang:
                    channels_comp_suggested_lst.append(channel_comp_suggested.id)

        just_started_courses = []
        recent_start_courses_lst = []
        today_date = datetime.now()
        today_only_date = today_date.date()
        started_courses_ids = request.env['slide.channel.partner'].sudo().search([])
        for started in started_courses_ids:
            if started.create_date:
                if started.create_date.date() == today_only_date:
                    just_started_courses.append(started.channel_id.id)

        if len(just_started_courses) > 0:
            for just_started in just_started_courses:
                started_user_lst = []
                channel_just_started = request.env['slide.channel'].sudo().browse(just_started)
                for just_start in channel_just_started.sudo().channel_partner_ids:
                    user_val = request.env['res.users'].search([('partner_id', '=', just_start.partner_id.id)], limit=1)
                    if user_val:
                        started_user_lst.append(user_val.id)
                if request.env.user.id not in started_user_lst:
                    if channel_just_started.lang_values == selected_lang:
                        recent_start_courses_lst.append(channel_just_started.id)

        interested_course_lst = []
        for interested_course in channels_all:
            if interested_course.course_category_id in request.env.user.topic_of_interest_ids:
                interested_user_lst = []
                if interested_course.sudo().channel_partner_ids:
                    for partner_val1 in interested_course.sudo().channel_partner_ids:
                        user_val1 = request.env['res.users'].search([('partner_id', '=', partner_val1.partner_id.id)],
                                                                    limit=1)
                        if user_val1:
                            interested_user_lst.append(user_val1.id)

                if request.env.user.id not in interested_user_lst:
                    if interested_course.lang_values == selected_lang:
                        interested_course_lst.append(interested_course.id)

        final_suggested_lst = channels_suggested_lst + channels_comp_suggested_lst + recent_start_courses_lst + interested_course_lst
        final_suggested_lst = list(set(final_suggested_lst))
        channels_suggested = request.env['slide.channel'].sudo().browse(final_suggested_lst)

        values = self._prepare_user_values(**post)
        values.update({
            'channels_suggested': channels_suggested,
            'channels_complete': channels_complete,
            'channels_my': channels_my,
            'channels_feature': channels_feature,
            'channels_assign': channels_assign,
            'channels_resumed': channels_resumed,
            # 'channels_popular': channels_popular,
            # 'channels_newest': channels_newest,
            'achievements': achievements,
            'users': users,
            'top3_users': self._get_top3_users(),
            'challenges': challenges,
            'challenges_done': challenges_done,
            'search_tags': request.env['slide.channel.tag'],
            'language_change': True
        })
        return request.render("ecom_lms.user_profile_edit_main_first_login_ecom", values)

        # return request.render("website_profile.user_profile_edit_main", values)
        # return request.render('website_slides.courses_home', values)
    
    @http.route('/lms_example_view', type='http', auth="user", website=True, sitemap=True)
    def my_lms_example(self, args, *kw):
        return request.render('ecom_lms.lms_example_view1')
    
    
    
    @http.route('/slides/journey/suggested/pwa/all', type='http', auth="public", website=True, sitemap=True)
    def slides_journey_suggested_pwa_all(self, slide_type=None, my=False, **post):
        domain = request.website.website_domain()
        domain = self._build_channel_domain(domain, slide_type=slide_type, my=my, **post)

        order = self._channel_order_by_criterion.get(post.get('sorting'))

        channels_ids = request.env['slide.channel'].sudo().search(domain, order=order)
        final_suggested_lst = []
        for chaneel in channels_ids:
            final_suggested_lst.append(chaneel.id)

        channels = request.env['slide.channel'].browse(final_suggested_lst)

        journey_lst = []
        journey_ids = request.env['course.journey'].sudo().search([])
        completed_journey_list = []
        for completed_journey in journey_ids:
            for journey_partner in completed_journey.sudo().journey_channel_partner_ids:
                if journey_partner.journey_completion == 100:
                    if completed_journey.id not in completed_journey_list:
                        completed_journey_list.append(completed_journey.id)
                        
                        
        journey_comp_suggested_lst = []
        for journey_completed_suggested in completed_journey_list:
            journey_comp_suggested = request.env['course.journey'].sudo().browse(journey_completed_suggested)
            suggested_journey_comp_user_lst = []
            for journey_partner_val in journey_comp_suggested.sudo().journey_channel_partner_ids:
                user_val = request.env['res.users'].search([('partner_id', '=', journey_partner_val.partner_id.id)], limit=1)
                if user_val:
                    suggested_journey_comp_user_lst.append(user_val.id)
            if request.env.user.id not in suggested_journey_comp_user_lst:
                journey_comp_suggested_lst.append(journey_completed_suggested.id)
                
                
        just_started_journey = []
        recent_start_journey_lst = []
        today_date = datetime.now()
        today_only_date = today_date.date()
        started_journey_ids = request.env['course.journey.partner'].sudo().search([])
        for started_journey in started_journey_ids:
            if started_journey.create_date:
                if started_journey.create_date.date() == today_only_date:
                    just_started_journey.append(started_journey.journey_id.id)
    
        if len(just_started_journey) > 0:
            for just_started_j in just_started_journey:
                journey_started_user_lst = []
                journey_just_started = request.env['course.journey'].sudo().browse(just_started_j)
                for just_start_j in journey_just_started.sudo().journey_channel_partner_ids:
                    user_val = request.env['res.users'].search([('partner_id', '=', just_start_j.partner_id.id)], limit=1)
                    if user_val:
                        journey_started_user_lst.append(user_val.id)
                if request.env.user.id not in journey_started_user_lst:
                    recent_start_journey_lst.append(journey_just_started.id)
                    
                    
        interested_journey_lst = []
        for interested_journey in journey_ids:
            if interested_journey.courses_ids:
                for interested_journey_course in interested_journey.courses_ids:
                    if interested_journey_course.course_id.course_category_id in request.env.user.topic_of_interest_ids:
                        journey_interested_user_lst = []
                        if interested_journey.sudo().journey_channel_partner_ids:
                            for journey_partner_val1 in interested_journey.sudo().journey_channel_partner_ids:
                                journey_user_val1 = request.env['res.users'].search([('partner_id', '=', journey_partner_val1.partner_id.id)],limit=1)
                                if journey_user_val1:
                                    journey_interested_user_lst.append(journey_user_val1.id)
                        if request.env.user.id not in journey_interested_user_lst:
                            interested_journey_lst.append(interested_journey.id)
                            
                            
                            
        final_journey_suggested_lst = journey_comp_suggested_lst + recent_start_journey_lst + interested_journey_lst
        final_journey_suggested_lst = list(set(final_journey_suggested_lst))
        journey_all_details = request.env['course.journey'].sudo().browse(final_journey_suggested_lst)

        tag_groups = request.env['slide.channel.tag.group'].search(
            ['&', ('tag_ids', '!=', False), ('website_published', '=', True)])
        search_tags = self._extract_channel_tag_search(**post)

        values = self._prepare_user_values(**post)
        values.update({
            'channels': channels,
            'journey_all_details': journey_all_details,
            'tag_groups': tag_groups,
            'search_term': post.get('search'),
            'search_slide_type': slide_type,
            'search_my': my,
            'search_tags': search_tags,
            'search_channel_tag_id': post.get('channel_tag_id'),
            'top3_users': self._get_top3_users(),
        })

        return request.render('ecom_lms.journey_pwa_view_all', values)
    
    
    
    
    @http.route('/my/homepage', type='http', auth="public", website=True, sitemap=True)
    def my_homepage_example(self, **post):
        domain = request.website.website_domain()
        channels_all = request.env['slide.channel'].sudo().search(domain)
        # channels_all = request.env['slide.channel'].search(domain)
        lst = []
        channels_allnew = request.env['slide.channel'].search(domain)
    
        for val in channels_allnew:
            if val.course_close_date:
                if datetime.now() <= val.course_close_date:
                    newid = val.id
                    lst.append(newid)
        channels_all = request.env['slide.channel'].search([('id', '=', lst)])
        # channel_unlink = channels_allnew - channels_all
        # for val in channel_unlink:
        #     val._remove_membership(request.env.user.partner_id.ids)
        #     self._channel_remove_session_answers(val)
    
        if not request.env.user._is_public():
            # If a course is completed, we don't want to see it in first position but in last
            channels_my = channels_all.filtered(lambda channel: channel.is_member).sorted(
                lambda channel: 0 if channel.completed else channel.completion, reverse=True)[:3]
        else:
            channels_my = request.env['slide.channel']
    
        channels_popular_ids = channels_all.sorted('total_votes', reverse=True)[:3]
        channels_newest_ids = channels_all.sorted('create_date', reverse=True)[:3]
    
        achievements = request.env['gamification.badge.user'].sudo().search([('badge_id.is_published', '=', True)],
                                                                            limit=5)
        if request.env.user._is_public():
            challenges = None
            challenges_done = None
        else:
            challenges = request.env['gamification.challenge'].sudo().search([
                ('challenge_category', '=', 'slides'),
                ('reward_id.is_published', '=', True)
            ], order='id asc', limit=5)
            challenges_done = request.env['gamification.badge.user'].sudo().search([
                ('challenge_id', 'in', challenges.ids),
                ('user_id', '=', request.env.user.id),
                ('badge_id.is_published', '=', True)
            ]).mapped('challenge_id')
    
        users = request.env['res.users'].sudo().search([
            ('karma', '>', 0),
            ('website_published', '=', True)], limit=5, order='karma desc')
    
        channels_suggested_lst = []
        for channels_suggested in channels_all:
            if channels_suggested.custom_visibility == 'semi_public':
                suggested_user_lst = []
                for channels_partner in channels_suggested.sudo().channel_partner_ids:
                    user = request.env['res.users'].search([('partner_id', '=', channels_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        suggested_user_lst.append(user.id)
                if request.env.user.id not in suggested_user_lst and request.env.user in channels_suggested.nominated_user_ids:
                    channels_suggested_lst.append(channels_suggested.id)
    
        completed_course_list = []
        for completed_course in channels_all:
            if completed_course.custom_visibility != 'semi_public':
    
                for channels_partner in completed_course.sudo().channel_partner_ids:
                    if channels_partner.completion == 100:
                        if completed_course.id not in completed_course_list:
                            completed_course_list.append(completed_course.id)
    
        channels_comp_suggested_lst = []
        for channels_completed_suggested in completed_course_list:
            channel_comp_suggested = request.env['slide.channel'].sudo().browse(channels_completed_suggested)
            suggested_comp_user_lst = []
            for partner_val in channel_comp_suggested.sudo().channel_partner_ids:
                user_val = request.env['res.users'].search([('partner_id', '=', partner_val.partner_id.id)], limit=1)
                if user_val:
                    suggested_comp_user_lst.append(user_val.id)
            if request.env.user.id not in suggested_comp_user_lst:
                if channel_comp_suggested.custom_visibility == 'private':
                    comp_suggested_private_user_lst = []
                    for comp_suggested_private_partner in channel_comp_suggested.sudo().channel_partner_ids:
                        comp_suggested_private_user = request.env['res.users'].search(
                            [('partner_id', '=', comp_suggested_private_partner.partner_id.id)], limit=1)
                        if comp_suggested_private_user:
                            comp_suggested_private_user_lst.append(comp_suggested_private_user.id)
                    if request.env.user.id in comp_suggested_private_user_lst:
                        channels_comp_suggested_lst.append(channel_comp_suggested.id)
                elif channel_comp_suggested.custom_visibility == 'semi_public':
                    comp_suggested_semi_public_user_lst = []
                    for comp_suggested_semi_user in channel_comp_suggested.sudo().nominated_user_ids:
                        comp_suggested_semi_public_user_lst.append(comp_suggested_semi_user.id)
                    if request.env.user.id in comp_suggested_semi_public_user_lst:
                        channels_comp_suggested_lst.append(channel_comp_suggested.id)
                else:
                    channels_comp_suggested_lst.append(channel_comp_suggested.id)
    
        just_started_courses = []
        recent_start_courses_lst = []
        today_date = datetime.now()
        today_only_date = today_date.date()
        started_courses_ids = request.env['slide.channel.partner'].sudo().search([])
        for started in started_courses_ids:
            if started.create_date:
                if started.create_date.date() == today_only_date:
                    just_started_courses.append(started.channel_id.id)
    
        if len(just_started_courses) > 0:
            for just_started in just_started_courses:
                started_user_lst = []
                channel_just_started = request.env['slide.channel'].sudo().browse(just_started)
                for just_start in channel_just_started.sudo().channel_partner_ids:
                    user_val = request.env['res.users'].search([('partner_id', '=', just_start.partner_id.id)], limit=1)
                    if user_val:
                        started_user_lst.append(user_val.id)
                if request.env.user.id not in started_user_lst:
                    if channel_just_started.custom_visibility == 'private':
                        just_started_private_user_lst = []
                        for just_started_private_partner in channel_just_started.sudo().channel_partner_ids:
                            just_started_private_user = request.env['res.users'].search(
                                [('partner_id', '=', just_started_private_partner.partner_id.id)], limit=1)
                            if just_started_private_user:
                                just_started_private_user_lst.append(just_started_private_user.id)
                        if request.env.user.id in just_started_private_user_lst:
                            just_started_private_user_lst.append(channel_just_started.id)
    
                    elif channel_just_started.custom_visibility == 'semi_public':
                        just_started_semi_public_user_lst = []
                        for just_started_semi_user in channel_just_started.sudo().nominated_user_ids:
                            just_started_semi_public_user_lst.append(just_started_semi_user.id)
                        if request.env.user.id in just_started_semi_public_user_lst:
                            recent_start_courses_lst.append(channel_just_started.id)
                    else:
                        recent_start_courses_lst.append(channel_just_started.id)
    
        interested_course_lst = []
        for interested_course in channels_all:
            if interested_course.course_category_id in request.env.user.topic_of_interest_ids:
                interested_user_lst = []
                if interested_course.sudo().channel_partner_ids:
                    for partner_val1 in interested_course.sudo().channel_partner_ids:
                        user_val1 = request.env['res.users'].search([('partner_id', '=', partner_val1.partner_id.id)],
                                                                    limit=1)
                        if user_val1:
                            interested_user_lst.append(user_val1.id)
                if request.env.user.id not in interested_user_lst:
                    if interested_course.custom_visibility == 'private':
                        interested_private_user_lst = []
                        for channels_interested_private_partner in interested_course.sudo().channel_partner_ids:
                            interested_private_user = request.env['res.users'].search(
                                [('partner_id', '=', channels_interested_private_partner.partner_id.id)], limit=1)
                            if interested_private_user:
                                interested_private_user_lst.append(interested_private_user.id)
                        if request.env.user.id in interested_private_user_lst:
                            interested_course_lst.append(interested_course.id)
    
                    elif interested_course.custom_visibility == 'semi_public':
                        interested_semi_public_user_lst = []
                        for channels_interested_semi_user in interested_course.sudo().nominated_user_ids:
                            interested_semi_public_user_lst.append(channels_interested_semi_user.id)
                        if request.env.user.id in interested_semi_public_user_lst:
                            interested_course_lst.append(interested_course.id)
                    else:
                        interested_course_lst.append(interested_course.id)
    
        final_suggested_lst = channels_suggested_lst + channels_comp_suggested_lst + recent_start_courses_lst + interested_course_lst
        final_suggested_lst = list(set(final_suggested_lst))
        channels_suggested = request.env['slide.channel'].sudo().browse(final_suggested_lst)
    
        channels_assigned_lst = []
        for channels_assigned in channels_all:
            attendee_user_lst = []
            # if channels_popular.custom_visibility=='private':
            for channels_partner in channels_assigned.sudo().channel_partner_ids:
                if channels_partner.completion != 100:
                    user = request.env['res.users'].search([('partner_id', '=', channels_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        attendee_user_lst.append(user.id)
            if request.env.user.id in attendee_user_lst:
                if channels_assigned.course_close_date:
                    date_now = datetime.now()
                    if date_now.date() <= channels_assigned.course_close_date.date():
                        if channels_assigned.custom_visibility == 'private':
                            assigned_private_user_lst = []
                            for channels_assigned_private_partner in channels_assigned.sudo().channel_partner_ids:
                                assigned_private_user = request.env['res.users'].search(
                                    [('partner_id', '=', channels_assigned_private_partner.partner_id.id)], limit=1)
                                if assigned_private_user:
                                    assigned_private_user_lst.append(assigned_private_user.id)
                            if request.env.user.id in assigned_private_user_lst:
                                channels_assigned_lst.append(channels_assigned.id)
    
                        elif channels_assigned.custom_visibility == 'semi_public':
                            assigned_semi_public_user_lst = []
                            for channels_assigned_semi_user in channels_assigned.sudo().nominated_user_ids:
                                assigned_semi_public_user_lst.append(channels_assigned_semi_user.id)
                            if request.env.user.id in assigned_semi_public_user_lst:
                                channels_assigned_lst.append(channels_assigned.id)
                        else:
                            channels_assigned_lst.append(channels_assigned.id)
    
                else:
                    if channels_assigned.custom_visibility == 'private':
                        assigned_private_user_lst = []
                        for channels_assigned_private_partner in channels_assigned.sudo().channel_partner_ids:
                            assigned_private_user = request.env['res.users'].search(
                                [('partner_id', '=', channels_assigned_private_partner.partner_id.id)], limit=1)
                            if assigned_private_user:
                                assigned_private_user_lst.append(assigned_private_user.id)
                        if request.env.user.id in assigned_private_user_lst:
                            channels_assigned_lst.append(channels_assigned.id)
                    elif channels_assigned.custom_visibility == 'semi_public':
                        assigned_semi_public_user_lst = []
                        for channels_assigned_semi_user in channels_assigned.sudo().nominated_user_ids:
                            assigned_semi_public_user_lst.append(channels_assigned_semi_user.id)
                        if request.env.user.id in assigned_semi_public_user_lst:
                            channels_assigned_lst.append(channels_assigned.id)
                    else:
                        channels_assigned_lst.append(channels_assigned.id)
    
        channels_assign = request.env['slide.channel'].sudo().browse(channels_assigned_lst)
    
        channels_featured_lst = []
        for channels_featured in channels_all:
            featured_user_lst = []
            if channels_featured.is_featured and channels_featured.featured_group_id:
                if channels_featured.featured_group_id in request.env.user.groups_id:
                    if channels_featured.custom_visibility == 'private':
                        featured_private_user_lst = []
                        for channels_featured_partner in channels_featured.sudo().channel_partner_ids:
                            user = request.env['res.users'].search(
                                [('partner_id', '=', channels_featured_partner.partner_id.id)], limit=1)
                            if user:
                                featured_private_user_lst.append(user.id)
                        if request.env.user.id in featured_private_user_lst:
                            channels_featured_lst.append(channels_featured.id)
    
                    elif channels_featured.custom_visibility == 'semi_public':
                        featured_semi_public_user_lst = []
                        for channels_featured_user in channels_featured.sudo().nominated_user_ids:
                            featured_semi_public_user_lst.append(channels_featured_user.id)
                        if request.env.user.id in featured_semi_public_user_lst:
                            channels_featured_lst.append(channels_featured.id)
    
                    else:
                        channels_featured_lst.append(channels_featured.id)
    
        channels_feature = request.env['slide.channel'].sudo().browse(channels_featured_lst)
    
        channels_popular_lst = []
        for channels_popular in channels_popular_ids:
            if channels_popular.custom_visibility == 'private':
                popular_user_lst = []
                for channels_popular_partner in channels_popular.sudo().channel_partner_ids:
                    user = request.env['res.users'].search(
                        [('partner_id', '=', channels_popular_partner.partner_id.id)], limit=1)
                    if user:
                        popular_user_lst.append(user.id)
                if request.env.user.id in popular_user_lst:
                    channels_popular_lst.append(channels_popular.id)
    
            elif channels_popular.custom_visibility == 'semi_public':
                popular_user_lst = []
                for channels_popular_user in channels_popular.sudo().nominated_user_ids:
                    popular_user_lst.append(channels_popular_user.id)
                if request.env.user.id in popular_user_lst:
                    channels_popular_lst.append(channels_popular.id)
            else:
                channels_popular_lst.append(channels_popular.id)
    
        channels_popular = request.env['slide.channel'].browse(channels_popular_lst)
    
        channels_newest_lst = []
        for channels_newest in channels_newest_ids:
            if channels_newest.custom_visibility == 'private':
                newest_user_lst = []
                for channels_newest_partner in channels_newest.sudo().channel_partner_ids:
                    user = request.env['res.users'].search([('partner_id', '=', channels_newest_partner.partner_id.id)],
                                                           limit=1)
                    if user:
                        channels_newest_lst.append(user.id)
                if request.env.user.id in channels_newest_lst:
                    channels_newest_lst.append(channels_newest.id)
    
            elif channels_newest.custom_visibility == 'semi_public':
                newest_user_lst = []
                for channels_newest_user in channels_newest.sudo().nominated_user_ids:
                    newest_user_lst.append(channels_newest_user.id)
    
                if request.env.user.id in newest_user_lst:
                    channels_newest_lst.append(channels_newest.id)
            else:
                channels_newest_lst.append(channels_newest.id)
    
        channels_newest = request.env['slide.channel'].browse(channels_newest_lst)
    
        channels_newest = request.env['slide.channel'].browse(channels_newest_lst)
    
        channels_resumed_learning_lst = []
        for channels_resumed in channels_all:
            channels_resumed_user_lst = []
            # if channels_popular.custom_visibility=='private':
            for channels_resumed_partner in channels_resumed.sudo().channel_partner_ids:
                if channels_resumed_partner.completion < 100 and channels_resumed_partner.completion > 0:
                    user = request.env['res.users'].search(
                        [('partner_id', '=', channels_resumed_partner.partner_id.id)], limit=1)
                    if user:
                        channels_resumed_user_lst.append(user.id)
            if request.env.user.id in channels_resumed_user_lst:
                date_now = datetime.now()
                if channels_resumed.course_close_date:
                    if date_now.date() <= channels_resumed.course_close_date.date():
                        if channels_resumed.custom_visibility == 'private':
                            channels_resumed_private_user_lst = []
                            for channels_resumed_private_partner in channels_resumed.sudo().channel_partner_ids:
                                private_user = request.env['res.users'].search(
                                    [('partner_id', '=', channels_resumed_private_partner.partner_id.id)], limit=1)
                                if private_user:
                                    channels_resumed_private_user_lst.append(private_user.id)
                            if request.env.user.id in channels_resumed_private_user_lst:
                                channels_resumed_learning_lst.append(channels_resumed.id)
    
                        elif channels_resumed.custom_visibility == 'semi_public':
                            resumed_semi_user_lst = []
                            for channels_resumed_semi_user in channels_resumed.sudo().nominated_user_ids:
                                resumed_semi_user_lst.append(channels_resumed_semi_user.id)
    
                            if request.env.user.id in resumed_semi_user_lst:
                                channels_resumed_learning_lst.append(channels_resumed.id)
                        else:
                            channels_resumed_learning_lst.append(channels_resumed.id)
                else:
                    if channels_resumed.custom_visibility == 'private':
                        channels_resumed_private_user_lst = []
                        for channels_resumed_private_partner in channels_resumed.sudo().channel_partner_ids:
                            private_user = request.env['res.users'].search(
                                [('partner_id', '=', channels_resumed_private_partner.partner_id.id)], limit=1)
                            if private_user:
                                channels_resumed_private_user_lst.append(private_user.id)
                        if request.env.user.id in channels_resumed_private_user_lst:
                            channels_resumed_learning_lst.append(channels_resumed.id)
    
                    elif channels_resumed.custom_visibility == 'semi_public':
                        resumed_semi_user_lst = []
                        for channels_resumed_semi_user in channels_resumed.sudo().nominated_user_ids:
                            resumed_semi_user_lst.append(channels_resumed_semi_user.id)
                        if request.env.user.id in resumed_semi_user_lst:
                            channels_resumed_learning_lst.append(channels_resumed.id)
    
                    else:
                        channels_resumed_learning_lst.append(channels_resumed.id)
    
        channels_resumed = request.env['slide.channel'].sudo().browse(channels_resumed_learning_lst)
        channels_completed_lst = []
    
        for channels_completed in channels_all:
            channels_completed_user_lst = []
            # if channels_popular.custom_visibility=='private':
            for channels_completed_partner in channels_completed.sudo().channel_partner_ids:
                if channels_completed_partner.completion == 100:
                    user = request.env['res.users'].search(
                        [('partner_id', '=', channels_completed_partner.partner_id.id)], limit=1)
                    if user:
                        channels_completed_user_lst.append(user.id)
    
            if request.env.user.id in channels_completed_user_lst:
                if channels_completed.custom_visibility == 'private':
                    channels_complete_private_user_lst = []
                    for channels_complete_private_partner in channels_completed.sudo().channel_partner_ids:
                        complete_private_user = request.env['res.users'].search(
                            [('partner_id', '=', channels_complete_private_partner.partner_id.id)], limit=1)
                        if complete_private_user:
                            channels_complete_private_user_lst.append(complete_private_user.id)
                    if request.env.user.id in channels_complete_private_user_lst:
                        channels_completed_lst.append(channels_completed.id)
    
                elif channels_completed.custom_visibility == 'semi_public':
                    completed_semi_user_lst = []
                    for completed_semi_user in channels_completed.sudo().nominated_user_ids:
                        completed_semi_user_lst.append(completed_semi_user.id)
                    if request.env.user.id in completed_semi_user_lst:
                        channels_completed_lst.append(channels_completed.id)
    
                else:
                    channels_completed_lst.append(channels_completed.id)
    
        channels_complete = request.env['slide.channel'].sudo().browse(channels_completed_lst)
    
        journey_lst = []
        journey_ids = request.env['course.journey'].sudo().search([])
    
        for journey in journey_ids:
            journey_lst.append(journey.id)
    
        # for journey in journey_ids:
        #     journey_user_lst= []
        #     for journey_partner in journey.sudo().journey_channel_partner_ids:
        #        # if channels_completed_partner.completion == 100:
        #         user= request.env['res.users'].search([('partner_id','=',journey_partner.partner_id.id)],limit=1)
        #         if user:
        #             journey_user_lst.append(user.id)
        #
        #     if request.env.user.id in journey_user_lst:
        #         journey_lst.append(journey.id)
    
        journey_details = request.env['course.journey'].sudo().browse(journey_lst)
        
        
        
        completed_journey_list = []
        for completed_journey in journey_ids:
            for journey_partner in completed_journey.sudo().journey_channel_partner_ids:
                if journey_partner.journey_completion == 100:
                    if completed_journey.id not in completed_journey_list:
                        completed_journey_list.append(completed_journey.id)
                        
                        
        journey_comp_suggested_lst = []
        for journey_completed_suggested in completed_journey_list:
            journey_comp_suggested = request.env['course.journey'].sudo().browse(journey_completed_suggested)
            suggested_journey_comp_user_lst = []
            for journey_partner_val in journey_comp_suggested.sudo().journey_channel_partner_ids:
                user_val = request.env['res.users'].search([('partner_id', '=', journey_partner_val.partner_id.id)], limit=1)
                if user_val:
                    suggested_journey_comp_user_lst.append(user_val.id)
            if request.env.user.id not in suggested_journey_comp_user_lst:
                journey_comp_suggested_lst.append(journey_comp_suggested.id)
                
                
        just_started_journey = []
        recent_start_journey_lst = []
        today_date = datetime.now()
        today_only_date = today_date.date()
        started_journey_ids = request.env['course.journey.partner'].sudo().search([])
        for started_journey in started_journey_ids:
            if started_journey.create_date:
                if started_journey.create_date.date() == today_only_date:
                    just_started_journey.append(started_journey.journey_id.id)
    
        if len(just_started_journey) > 0:
            for just_started_j in just_started_journey:
                journey_started_user_lst = []
                journey_just_started = request.env['course.journey'].sudo().browse(just_started_j)
                for just_start_j in journey_just_started.sudo().journey_channel_partner_ids:
                    user_val = request.env['res.users'].search([('partner_id', '=', just_start_j.partner_id.id)], limit=1)
                    if user_val:
                        journey_started_user_lst.append(user_val.id)
                if request.env.user.id not in journey_started_user_lst:
                    recent_start_journey_lst.append(journey_just_started.id)
                    
                    
        interested_journey_lst = []
        for interested_journey in journey_ids:
            if interested_journey.courses_ids:
                for interested_journey_course in interested_journey.courses_ids:
                    if interested_journey_course.course_id.course_category_id in request.env.user.topic_of_interest_ids:
                        journey_interested_user_lst = []
                        if interested_journey.sudo().journey_channel_partner_ids:
                            for journey_partner_val1 in interested_journey.sudo().journey_channel_partner_ids:
                                journey_user_val1 = request.env['res.users'].search([('partner_id', '=', journey_partner_val1.partner_id.id)],limit=1)
                                if journey_user_val1:
                                    journey_interested_user_lst.append(journey_user_val1.id)
                        if request.env.user.id not in journey_interested_user_lst:
                            interested_journey_lst.append(interested_journey.id)
                            
                            
                            
        final_journey_suggested_lst = journey_comp_suggested_lst + recent_start_journey_lst + interested_journey_lst
        final_journey_suggested_lst = list(set(final_journey_suggested_lst))
        journey_suggested = request.env['course.journey'].sudo().browse(final_journey_suggested_lst)
                
    
        quizzes_lst = []
        quizzes_ids = request.env['quizzes.question'].sudo().search([])
        for quizzes in quizzes_ids:
            quizzes_lst.append(quizzes.id)
    
        quizzes_details = request.env['quizzes.question'].sudo().browse(quizzes_lst)
    
        values = self._prepare_user_values(**post)
        values.update({
            'channels_complete': channels_complete,
            'channels_resumed': channels_resumed,
            'channels_suggested': channels_suggested,
            'channels_assign': channels_assign,
            'channels_feature': channels_feature,
            'channels_my': channels_all,
            'channels_popular': channels_popular,
            'channels_newest': channels_newest,
            'achievements': achievements,
            'journey_details': journey_details,
            'journey_suggested': journey_suggested,
            'quizzes_details': quizzes_details,
            'users': users,
            'top3_users': self._get_top3_users(),
            'challenges': challenges,
            'challenges_done': challenges_done,
            'search_tags': request.env['slide.channel.tag']
        })
        return request.render('ecom_lms.my_homepage_veiw', values)

    @http.route('/my-courses', type='http', auth="user", website=True, sitemap=True)
    def my_course(self, *args, **kw):
        domain = request.website.website_domain()
        lst = []
        channels_allnew = request.env['slide.channel'].search(domain)

        for val in channels_allnew:
            if val.course_close_date:
                if datetime.now() <= val.course_close_date:
                    newid = val.id
                    lst.append(newid)
        channels_all = request.env['slide.channel'].search([('id', '=', lst)])
        
        my_channels_lst=[] 
        if channels_all:
            for all_chnl in channels_all:
                if all_chnl.custom_visibility == 'semi_public':
                    if all_chnl.nominated_user_ids:
                        for nominated_usr in all_chnl.sudo().nominated_user_ids:
                            if nominated_usr.partner_id == request.env.user.partner_id:
                                if all_chnl.id not in my_channels_lst:
                                    my_channels_lst.append(all_chnl.id)
                elif all_chnl.custom_visibility == 'public' or all_chnl.custom_visibility == 'private':
                    if all_chnl.sudo().channel_partner_ids:
                        for channel_partner_emp in all_chnl.sudo().channel_partner_ids:
                            if channel_partner_emp.partner_id == request.env.user.partner_id:
                                if all_chnl.id not in my_channels_lst:
                                    my_channels_lst.append(all_chnl.id)
                    
                # if all_chnl.sudo().channel_partner_ids:
                #     for channel_partner_emp in all_chnl.sudo().channel_partner_ids:
                #         if channel_partner_emp.partner_id == request.env.user.partner_id:
                #             if all_chnl not in my_channels_lst:
                #                 my_channels_lst.append(all_chnl.id)
        my_channels= request.env['slide.channel'].browse(my_channels_lst)
        # channel_unlink = channels_allnew - channels_all
        # for val in channel_unlink:
        #     val._remove_membership(request.env.user.partner_id.ids)
        #     self._channel_remove_session_answers(val)

        channels_my = channels_allnew.filtered(lambda channel: channel.is_member).sorted(
            lambda channel: 0 if channel.completed else channel.completion, reverse=True)[:3]

        # channel_unlink = self.env['slide.channel.partner'].sudo().search([('channel_id', '=', self.channel_id.id),
        #                                                             ('partner_id', '=', self.env.user.partner_id.id)])
        # channel_unlink.write({})

        channels_popular = channels_all.sorted('total_votes', reverse=True)[:3]
        channels_newest = channels_all.sorted('create_date', reverse=True)[:3]

        achievements = request.env['gamification.badge.user'].sudo().search([('badge_id.is_published', '=', True)],
                                                                            limit=5)
        if request.env.user._is_public():
            challenges = None
            challenges_done = None
        else:
            challenges = request.env['gamification.challenge'].sudo().search([
                ('challenge_category', '=', 'slides'),
                ('reward_id.is_published', '=', True)
            ], order='id asc', limit=5)
            challenges_done = request.env['gamification.badge.user'].sudo().search([
                ('challenge_id', 'in', challenges.ids),
                ('user_id', '=', request.env.user.id),
                ('badge_id.is_published', '=', True)
            ]).mapped('challenge_id')

        users = request.env['res.users'].sudo().search([
            ('karma', '>', 0),
            ('website_published', '=', True)], limit=5, order='karma desc')

        values = self._prepare_user_values(**kw)
        values.update({
            'channels_my':my_channels,
            # 'channels_my': channels_all,
            'channels_popular': channels_popular,
            'channels_newest': channels_newest,
            'achievements': achievements,
            'users': users,
            'top3_users': self._get_top3_users(),
            'challenges': challenges,
            'challenges_done': challenges_done,
            'search_tags': request.env['slide.channel.tag']
        })
        vals = dict()
        return request.render("ecom_lms.my_courses", values)
    
    @http.route('''/pwa/slides/slide/<model("slide.slide"):slide>''', type='http', auth="public", website=True,
                sitemap=True)
    def slide_pwa_view(self, slide, **kwargs):

        if not slide.channel_id.can_access_from_current_website() or not slide.active:
            raise werkzeug.exceptions.NotFound()
        self._set_viewed_slide(slide)

        values = self._get_slide_detail(slide)
        # quiz-specific: update with karma and quiz information
        if slide.question_ids:
            values.update(self._get_slide_quiz_data(slide))
        # sidebar: update with user channel progress
        values['channel_progress'] = self._get_channel_progress(slide.channel_id, include_quiz=True)
        users_details=request.env['res.users'].search([])
        # Allows to have breadcrumb for the previously used filter
        if slide.channel_id.course_close_date:
            if datetime.now() <= slide.channel_id.course_close_date:

                values.update({
                    'search_category': slide.category_id if kwargs.get('search_category') else None,
                    'search_tag': request.env['slide.tag'].browse(int(kwargs.get('search_tag'))) if kwargs.get(
                        'search_tag') else None,
                    'slide_types': dict(
                        request.env['slide.slide']._fields['slide_type']._description_selection(
                            request.env)) if kwargs.get(
                        'search_slide_type') else None,
                    'search_slide_type': kwargs.get('search_slide_type'),
                    'search_uncategorized': kwargs.get('search_uncategorized'),
                    'users_details':users_details,
                })
                values['channel'] = slide.channel_id
                # for val in values:
                values = self._prepare_additional_channel_values(values, **kwargs)
                values.pop('channel', None)

                values['signup_allowed'] = request.env['res.users'].sudo()._get_signup_invitation_scope() == 'b2c'
                
                pwa_slide_completed = self._set_completed_slide(slide)
                values['pwa_slide_completed'] = pwa_slide_completed

                # if kwargs.get('fullscreen') == '1':
                #     return request.render("website_slides.slide_fullscreen", values)
                return request.render("ecom_lms.lms_content_pdf_view_template", values)

            else:
                sys.tracebacklimit = 0
                raise AccessError(
                    _('The availability of the course is expired. Please click on "Home" or "My Courses" to access your available content.'))
                
                
                
                
    @http.route('''/share/user/fullscreen/slide/<model("slide.slide"):slide>''', type='http', auth="public", website=True,sitemap=True)
    def share_user_fullscreen_slide(self, slide, **kwargs):
        if not slide.channel_id.can_access_from_current_website() or not slide.active:
            raise werkzeug.exceptions.NotFound()
        self._set_viewed_slide(slide)
        pager_url = "/slides/slide/%s?fullscreen=1" % (slide.id)
        only_user_val= (kwargs['usr_detail_full_id']).split('(')
        user_val= only_user_val[1].split(',')
        user_id = int(user_val[0])
        user= request.env['res.users'].browse(user_id)
        template_id = request.env.ref('ecom_lms.email_template_course_recommendation').sudo()
        outgoing_server_name = request.env['ir.mail_server'].sudo().search([],limit=1).smtp_user
        current_user = request.env['res.users'].sudo().browse(int(request.env.uid))
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if template_id and user.partner_id.email and outgoing_server_name:
            email_vals = {
                        'email_to': user.partner_id.email,
                        "subject": 'This course is recommended to you',
                        "body_html": """ <html>
                                               <head></head>
                                               <body>
                                               <p>Dear """ + str(user.name) + """</p>
                                                <p>
                                                """ + str(current_user.name) + """ recommend the <strong>""" + str(slide.channel_id.name) + """</strong> to you. Please click on the sharable link to join the course.Course Due date will be """ + str(slide.channel_id.course_close_date.date()) + """..
                                                </p>
                                                <p>
                                                 <a href=""" + str(base_url + "/recommend-course?ref=" + (str(slide.channel_id.id))) + """
                        style="padding: 5px 10px; color: #FFFFFF; text-decoration: none; background-color: #875A7B; border: 1px solid #875A7B; border-radius: 3px">
                            Click Here</a></p>"""
                            
                        }
            mail_send = template_id.sudo().send_mail(user_id, force_send=True, email_values=email_vals)
            
            
            
            
            template_id.sudo().send_mail(user.id, force_send=True)
        return request.redirect(pager_url)
    
    
    @http.route('''/share/user/slide/<model("slide.slide"):slide>''', type='http', auth="public", website=True,sitemap=True)
    def share_user_slide(self, slide, **kwargs):
        if not slide.channel_id.can_access_from_current_website() or not slide.active:
            raise werkzeug.exceptions.NotFound()
        self._set_viewed_slide(slide)
        pager_url = "/slides/slide/%s" % (slide.id)
        only_user_val= (kwargs['usr_detail_id']).split('(')
        user_val= only_user_val[1].split(',')
        user_id = int(user_val[0])
        user= request.env['res.users'].browse(user_id)
        template_id = request.env.ref('ecom_lms.email_template_course_recommendation').sudo()
        outgoing_server_name = request.env['ir.mail_server'].sudo().search([],limit=1).smtp_user
        current_user = request.env['res.users'].sudo().browse(int(request.env.uid))
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if template_id and user.partner_id.email and outgoing_server_name:
            email_vals = {
                        'email_to': user.partner_id.email,
                        "subject": 'This course is recommended to you',
                        "body_html": """ <html>
                                               <head></head>
                                               <body>
                                               <p>Dear """ + str(user.name) + """</p>
                                                <p>
                                                """ + str(current_user.name) + """ recommend the <strong>""" + str(slide.channel_id.name) + """</strong> to you. Please click on the sharable link to join the course.Course Due date will be """ + str(slide.channel_id.course_close_date.date()) + """..
                                                </p>
                                                <p>
                                                 <a href=""" + str(base_url + "/recommend-course?ref=" + (str(slide.channel_id.id))) + """
                        style="padding: 5px 10px; color: #FFFFFF; text-decoration: none; background-color: #875A7B; border: 1px solid #875A7B; border-radius: 3px">
                            Click Here</a></p>"""
                            
                        }
            mail_send = template_id.sudo().send_mail(user_id, force_send=True, email_values=email_vals)
            
            
            
            
            template_id.sudo().send_mail(user.id, force_send=True)
        
        return request.redirect(pager_url)
    
    
    
    
    @http.route('''/share/user/pwa/slide/<model("slide.slide"):slide>''', type='http', auth="public", website=True,sitemap=True)
    def share_user_pwa_slide(self, slide, **kwargs):
        if not slide.channel_id.can_access_from_current_website() or not slide.active:
            raise werkzeug.exceptions.NotFound()
        self._set_viewed_slide(slide)
        pager_url = "/pwa/slides/slide/%s" % (slide.id)
        only_user_val= (kwargs['usr_detail_id']).split('(')
        if len(only_user_val)>1:
            user_val= only_user_val[1].split(',')
            user_id = int(user_val[0])
            user= request.env['res.users'].browse(user_id)
            template_id = request.env.ref('ecom_lms.email_template_course_recommendation').sudo()
            outgoing_server_name = request.env['ir.mail_server'].sudo().search([],limit=1).smtp_user
            current_user = request.env['res.users'].sudo().browse(int(request.env.uid))
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if template_id and user.partner_id.email and outgoing_server_name:
                email_vals = {
                            'email_to': user.partner_id.email,
                            "subject": 'This course is recommended to you',
                            "body_html": """ <html>
                                                   <head></head>
                                                   <body>
                                                   <p>Dear """ + str(user.name) + """</p>
                                                    <p>
                                                    """ + str(current_user.name) + """ recommend the <strong>""" + str(slide.channel_id.name) + """</strong> to you. Please click on the sharable link to join the course.Course Due date will be """ + str(slide.channel_id.course_close_date.date()) + """..
                                                    </p>
                                                    <p>
                                                     <a href=""" + str(base_url + "/recommend-course?ref=" + (str(slide.channel_id.id))) + """
                            style="padding: 5px 10px; color: #FFFFFF; text-decoration: none; background-color: #875A7B; border: 1px solid #875A7B; border-radius: 3px">
                                Click Here</a></p>"""
                                
                            }
                mail_send = template_id.sudo().send_mail(user_id, force_send=True, email_values=email_vals)
                
                
                
                
                template_id.sudo().send_mail(user.id, force_send=True)
        
        return request.redirect(pager_url)
    
    
    
    @http.route('''/share/user/channel/<model("slide.channel"):channel>''', type='http', auth="public", website=True,sitemap=True)
    def share_user_channel(self, channel, **kwargs):
        pager_url = "/pwa/slides/%s" % (channel.id)
        only_user_val= (kwargs['usr_detail_id']).split('(')
        print ("999999999999",len(only_user_val))
        if len(only_user_val) >1:
            user_val= only_user_val[1].split(',')
            user_id = int(user_val[0])
            user= request.env['res.users'].browse(user_id)
            template_id = request.env.ref('ecom_lms.email_template_course_recommendation').sudo()
            outgoing_server_name = request.env['ir.mail_server'].sudo().search([],limit=1).smtp_user
            current_user = request.env['res.users'].sudo().browse(int(request.env.uid))
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if template_id and user.partner_id.email and outgoing_server_name:
                email_vals = {
                            'email_to': user.partner_id.email,
                            "subject": 'This course is recommended to you',
                            "body_html": """ <html>
                                                   <head></head>
                                                   <body>
                                                   <p>Dear """ + str(user.name) + """</p>
                                                    <p>
                                                    """ + str(current_user.name) + """ recommend the <strong>""" + str(channel.name) + """</strong> to you. Please click on the sharable link to join the course.Course Due date will be """ + str(channel.course_close_date.date()) + """..
                                                    </p>
                                                    <p>
                                                     <a href=""" + str(base_url + "/recommend-course?ref=" + (str(channel.id))) + """
                            style="padding: 5px 10px; color: #FFFFFF; text-decoration: none; background-color: #875A7B; border: 1px solid #875A7B; border-radius: 3px">
                                Click Here</a></p>"""
                                
                            }
                mail_send = template_id.sudo().send_mail(user_id, force_send=True, email_values=email_vals)
                template_id.sudo().send_mail(user.id, force_send=True)
        
        return request.redirect(pager_url)



    @http.route('''/slides/slide/<model("slide.slide"):slide>''', type='http', auth="public", website=True,
                sitemap=True)
    def slide_view(self, slide, **kwargs):
        if not slide.channel_id.can_access_from_current_website() or not slide.active:
            raise werkzeug.exceptions.NotFound()
        self._set_viewed_slide(slide)

        values = self._get_slide_detail(slide)
        # quiz-specific: update with karma and quiz information
        if slide.question_ids:
            values.update(self._get_slide_quiz_data(slide))
            
        users_details= request.env['res.users'].search([])
            
        # sidebar: update with user channel progress
        values['channel_progress'] = self._get_channel_progress(slide.channel_id, include_quiz=True)
        # Allows to have breadcrumb for the previously used filter
        if slide.channel_id.course_close_date:
            if datetime.now() <= slide.channel_id.course_close_date:
                values.update({
                    'search_category': slide.category_id if kwargs.get('search_category') else None,
                    'search_tag': request.env['slide.tag'].browse(int(kwargs.get('search_tag'))) if kwargs.get(
                        'search_tag') else None,
                    'slide_types': dict(
                        request.env['slide.slide']._fields['slide_type']._description_selection(
                            request.env)) if kwargs.get(
                        'search_slide_type') else None,
                    'search_slide_type': kwargs.get('search_slide_type'),
                    'search_uncategorized': kwargs.get('search_uncategorized'),
                    'users_details':users_details
                })
                now = datetime.now()
                time_delt1 = timedelta(hours=5, minutes=30)
                nowtime = (now + time_delt1).strftime('%Y-%m-%d %H:%M:%S')
                nowclose = (slide.lesson_close_date + time_delt1).strftime('%Y-%m-%d %H:%M:%S')

                if nowtime > nowclose:
                    slide.is_published = False

                values['channel'] = slide.channel_id

                # for val in values:
                values = self._prepare_additional_channel_values(values, **kwargs)
                values.pop('channel', None)

                values['signup_allowed'] = request.env['res.users'].sudo()._get_signup_invitation_scope() == 'b2c'

                if kwargs.get('fullscreen') == '1':
                    return request.render("website_slides.slide_fullscreen", values)
                return request.render("website_slides.slide_main", values)

            else:
                sys.tracebacklimit = 0
                raise AccessError(
                    _('The availability of the course is expired. Please click on "Home" or "My Courses" to access your available content.'))


class customWebsiteSlidesquiz(WebsiteProfile):
    
    
    @http.route(['/profile/user/<int:user_id>'], type='http', auth="public", website=True)
    def view_user_profile(self, user_id, **post):
        user = self._check_user_profile_access(user_id)
        if not user:
            return request.render("website_profile.private_profile")
        values = self._prepare_user_values(**post)
        params = self._prepare_user_profile_parameters(**post)
        values.update(self._prepare_user_profile_values(user, **params))
        return request.render("website_profile.user_profile_edit_main", values)
    
    
    @http.route(['/profile/view/user/<int:user_id>'], type='http', auth="public", website=True)
    def view_user_every_login_profile(self, user_id, **post):
        user = self._check_user_profile_access(user_id)
        if not user:
            return request.render("website_profile.private_profile")
        values = self._prepare_user_values(**post)
        params = self._prepare_user_profile_parameters(**post)
        values.update(self._prepare_user_profile_values(user, **params))
        return request.render("ecom_lms.user_profile_edit_main_every_login_ecom", values)
    
    
    def _profile_edition_preprocess_values(self, user, **kwargs):
        
            # raise AccessError(
            #     _('User Image is Required'))
        values = {
            # 'name': kwargs.get('name'),
            'website': kwargs.get('website'),
            # 'email': kwargs.get('email'),
            # 'city': kwargs.get('city'),
            # 'country_id': int(kwargs.get('country')) if kwargs.get('country') else False,
            # 'website_description': kwargs.get('description'),
        }

        if 'clear_image' in kwargs:
            values['image_1920'] = False
        elif kwargs.get('ufile'):
            image = kwargs.get('ufile').read()
            values['image_1920'] = base64.b64encode(image)

        if request.uid == user.id:  # the controller allows to edit only its own privacy settings; use partner management for other cases
            values['website_published'] = kwargs.get('website_published') == 'True'
            
        return values
    

    @http.route('/profile/user/save', type='http', auth="user", methods=['POST'], website=True)
    def save_edited_profile(self, **kwargs):
        user_id = int(kwargs.get('user_id', 0))
        if user_id and request.env.user.id != user_id and request.env.user._is_admin():
            user = request.env['res.users'].browse(user_id)
        else:
            user = request.env.user
        values = self._profile_edition_preprocess_values(user, **kwargs)
        if not kwargs.get('ufile'):
            if not user.image_1920:
                return request.render('ecom_lms.user_profile_edit_first_login_image_not_found')
        if 'image_1920' in values:
            if not values['image_1920']:
                if not user.image_1920:
                    request.render('ecom_lms.user_profile_edit_first_login_image_not_found')
                image1 = kwargs.get('ufile').read()
                return request.render('ecom_lms.user_profile_edit_first_login_image_not_found')
            image1 = kwargs.get('ufile').read()
            user.image_1920=image1
        whitelisted_values = {key: values[key] for key in type(user).SELF_WRITEABLE_FIELDS if key in values}
        user.write(whitelisted_values)
        if kwargs.get('url_param'):
            return werkzeug.utils.redirect("/profile/user/%d?%s" % (user.id, kwargs['url_param']))
        else:
            return werkzeug.utils.redirect("/profile/user/%d" % user.id)
        
        

    def _get_slide_quiz_data(self, slide):

        checkrandom = request.env['slide.slide'].sudo().search(
            [('random_question', '=', 'random'), ('id', '=', slide.id)])
        checkserial = request.env['slide.slide'].sudo().search(
            [('random_question', '=', 'serial'), ('id', '=', slide.id)])
        for i in checkrandom:
            if i.random_question == 'random':
                slide_completed = slide.user_membership_id.sudo().completed
                values = {
                    'slide_questions': [{
                        'id': question.id,
                        'question': question.question,
                        'custom_question_type': question.custom_question_type,
                        'answer_ids': [{
                            'id': answer.id,
                            'text_value': answer.text_value,
                            'is_correct': answer.is_correct if slide_completed or request.website.is_publisher() else None,
                            'comment': answer.comment if request.website.is_publisher else None
                        } for answer in question.sudo().answer_ids],
                    } for question in slide.question_ids]
                }
                if 'slide_answer_quiz' in request.session:
                    slide_answer_quiz = json.loads(request.session['slide_answer_quiz'])
                    if str(slide.id) in slide_answer_quiz:
                        values['session_answers'] = slide_answer_quiz[str(slide.id)]
                values.update(self._get_slide_quiz_partner_info(slide))
                random.shuffle(values['slide_questions'])
                return values

        for f in checkserial:
            if f.random_question == 'serial':
                slide_completed = slide.user_membership_id.sudo().completed
                values = {
                    'slide_questions': [{
                        'id': question.id,
                        'question': question.question,
                        'custom_question_type': question.custom_question_type,
                        'answer_ids': [{
                            'id': answer.id,
                            'text_value': answer.text_value,
                            'is_correct': answer.is_correct if slide_completed or request.website.is_publisher() else None,
                            'comment': answer.comment if request.website.is_publisher else None
                        } for answer in question.sudo().answer_ids],
                    } for question in slide.question_ids]
                }
                if 'slide_answer_quiz' in request.session:
                    slide_answer_quiz = json.loads(request.session['slide_answer_quiz'])
                    if str(slide.id) in slide_answer_quiz:
                        values['session_answers'] = slide_answer_quiz[str(slide.id)]
                values.update(self._get_slide_quiz_partner_info(slide))
                return values

    @http.route('/slides/slide/quiz/submit', type="json", auth="public", website=True)
    def slide_quiz_submit(self, slide_id, answer_ids):
        if request.website.is_public_user():
            return {'error': 'public_user'}
        fetch_res = self._fetch_slide(slide_id)
        if fetch_res.get('error'):
            return fetch_res
        slide = fetch_res['slide']

        if slide.user_membership_id.sudo().completed:
            self._channel_remove_session_answers(slide.channel_id, slide)
            return {'error': 'slide_quiz_done'}

        all_questions = request.env['slide.question'].sudo().search([('slide_id', '=', slide.id)])

        user_answers = request.env['slide.answer'].sudo().search([('id', 'in', answer_ids)])
        # if user_answers.mapped('question_id') != all_questions:
        #     return {'error': 'slide_quiz_incomplete'}

        if user_answers.mapped('question_id') != all_questions:
            return {'error': 'slide_quiz_incomplete'}

        user_bad_answers = user_answers.filtered(lambda answer: not answer.is_correct)
        if user_bad_answers:
                
            slide_partner_val_id = request.env['slide.slide.partner'].search([('slide_id','=',slide.id),('partner_id','=',request.env.user.partner_id.id)],limit=1)
            
            wrong_attempt_ans_id= request.env['slide.slide.partner.wrong.question'].sudo().create({'slide_partner_id':slide_partner_val_id.id,'wrong_attempt_count':1})
            for bad_ans in user_bad_answers:
                wrong_attempt_ans_id.write({'wrong_qus_ids': [( 4, bad_ans.question_id.id)]})

        self._set_viewed_slide(slide, quiz_attempts_inc=True)
        quiz_info = self._get_slide_quiz_partner_info(slide, quiz_done=True)

        rank_progress = {}
        if not user_bad_answers:
            rank_progress['previous_rank'] = self._get_rank_values(request.env.user)
            slide._action_set_quiz_done()
            slide.action_set_completed()
            rank_progress['new_rank'] = self._get_rank_values(request.env.user)
            rank_progress.update({
                'description': request.env.user.rank_id.description,
                'last_rank': not request.env.user._get_next_rank(),
                'level_up': rank_progress['previous_rank']['lower_bound'] != rank_progress['new_rank']['lower_bound']
            })
        self._channel_remove_session_answers(slide.channel_id, slide)
        return {
            'answers': {
                answer.question_id.id: {
                    'is_correct': answer.is_correct,
                    'comment': answer.comment
                } for answer in user_answers
            },
            'completed': slide.user_membership_id.sudo().completed,
            'channel_completion': slide.channel_id.completion,
            'quizKarmaWon': quiz_info['quiz_karma_won'],
            'quizKarmaGain': quiz_info['quiz_karma_gain'],
            'quizAttemptsCount': quiz_info['quiz_attempts_count'],
            'rankProgress': rank_progress,
        }


class TimesheetCustomerPortal(CustomerPortal):
    
    @http.route(['/my/ceritifications', '/my/certifications/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_certifications(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='none',
                                 **kw):
        values = self._prepare_portal_layout_values()
        AccountInvoice = request.env['account.move']

        domain = [
            ('move_type', 'in', ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt'))]

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'invoice_date desc'},
            'duedate': {'label': _('Due Date'), 'order': 'invoice_date_due desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'invoices': {'label': _('Invoices'), 'domain': [('move_type', '=', ('out_invoice', 'out_refund'))]},
            'bills': {'label': _('Bills'), 'domain': [('move_type', '=', ('in_invoice', 'in_refund'))]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        invoice_count = AccountInvoice.search_count(domain)

        pager = portal_pager(
            url="/my/invoices",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=invoice_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        invoices = AccountInvoice.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_invoices_history'] = invoices.ids[:100]

        values.update({
            'date': date_begin,
            'invoices': invoices,
            'page_name': 'invoice',
            'pager': pager,
            'default_url': '/my/invoices',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("account.portal_my_invoices", values)


class WebsiteProfileCustom(WebsiteProfile):

    @http.route(['/profile/users',
                 '/profile/users/page/<int:page>'], type='http', auth="public", website=True, sitemap=True)
    def view_all_users_page(self, page=1, **kwargs):
        User = request.env['res.users']
        dom = [('karma', '>', 1), ('website_published', '=', True)]
        # Searches
        search_term = kwargs.get('search')
        group_by = kwargs.get('group_by', False)
        render_values = {
            'search': search_term,
            'group_by': group_by or 'all',
        }
        if search_term:
            dom = expression.AND(
                [['|', ('name', 'ilike', search_term), ('partner_id.commercial_company_name', 'ilike', search_term)],
                 dom])

        user_count = User.sudo().search_count(dom)
        my_user = request.env.user
        current_user_values = False
        if user_count:
            page_count = math.ceil(user_count / self._users_per_page)
            pager = request.website.pager(url="/profile/users", total=user_count, page=page, step=self._users_per_page,
                                          scope=page_count if page_count < self._pager_max_pages else self._pager_max_pages)

            users = User.sudo().search(dom, limit=self._users_per_page, offset=pager['offset'], order='karma DESC')
            user_values = self._prepare_all_users_values(users)

            # Get karma position for users (only website_published)
            position_domain = [('karma', '>', 1), ('website_published', '=', True)]
            position_map = self._get_position_map(position_domain, users, group_by)

            max_position = max([user_data['karma_position'] for user_data in position_map.values()], default=1)
            for user in user_values:
                user_data = position_map.get(user['id'], dict())
                user['position'] = user_data.get('karma_position', max_position + 1)
                user['karma_gain'] = user_data.get('karma_gain_total', 0)
            user_values.sort(key=itemgetter('position'))

            if my_user.website_published and my_user.karma and my_user.id not in users.ids:
                # Need to keep the dom to search only for users that appear in the ranking page
                current_user = User.sudo().search(expression.AND([[('id', '=', my_user.id)], dom]))
                if current_user:
                    current_user_values = self._prepare_all_users_values(current_user)[0]

                    user_data = self._get_position_map(position_domain, current_user, group_by).get(current_user.id, {})
                    current_user_values['position'] = user_data.get('karma_position', 0)
                    current_user_values['karma_gain'] = user_data.get('karma_gain_total', 0)

        else:
            user_values = []
            pager = {'page_count': 0}

        courses_ids = request.env['slide.channel'].sudo().search([])
        state_ids = request.env['res.country.state'].sudo().search([])
        render_values.update({
            'top3_users': user_values[:3] if not search_term and page == 1 else [],
            'users': user_values,
            'my_user': current_user_values,
            'pager': pager,
            'all_courses_ids': courses_ids,
            'all_state_ids': state_ids,
        })
        return request.render("website_profile.users_page_main", render_values)

    @http.route(['/course-wise/leadership/'], type='http', auth="public", website=True, sitemap=True)
    def view_all_users_coursewise(self, page=1, **kwargs):
        User = request.env['res.users']
        if kwargs.get('channel_id'):
            course_id = kwargs.get('channel_id')
            request.env.user.channel = course_id
        else:
            course_id = request.env.user.channel
        course_id1 = course_id.split('(')
        course_id2 = course_id1[1].split(',')
        channel_id = request.env['slide.channel'].search([('id', '=', int(course_id2[0]))])
        user_lst = []
        if channel_id:
            for course_partner in channel_id.sudo().channel_partner_ids:
                user = request.env['res.users'].sudo().search([('partner_id', '=', course_partner.partner_id.id)],
                                                              limit=1)
                if user:
                    user_lst.append(user.id)

            dom = [('karma', '>', 1), ('website_published', '=', True), ('id', 'in', user_lst)]
        else:
            dom = [('karma', '>', 1), ('website_published', '=', True)]

        # Searches
        search_term = kwargs.get('search')
        group_by = kwargs.get('group_by', False)
        render_values = {
            'search': search_term,
            'group_by': group_by or 'all',
        }
        if search_term:
            dom = expression.AND(
                [['|', ('name', 'ilike', search_term), ('partner_id.commercial_company_name', 'ilike', search_term)],
                 dom])

        user_count = User.sudo().search_count(dom)
        my_user = request.env.user
        current_user_values = False
        if user_count:
            page_count = math.ceil(user_count / self._users_per_page)
            pager = request.website.pager(url="/profile/users", total=user_count, page=page, step=self._users_per_page,
                                          scope=page_count if page_count < self._pager_max_pages else self._pager_max_pages)

            # users_ids = User.sudo().search(dom, limit=self._users_per_page, offset=pager['offset'], order='karma DESC')
            users = User.sudo().search(dom, limit=self._users_per_page, offset=pager['offset'], order='karma DESC')
            user_values = self._prepare_all_users_values(users)

            # Get karma position for users (only website_published)
            position_domain = [('karma', '>', 1), ('website_published', '=', True)]
            position_map = self._get_position_map(position_domain, users, group_by)

            max_position = max([user_data['karma_position'] for user_data in position_map.values()], default=1)
            for user in user_values:
                user_data = position_map.get(user['id'], dict())
                user['position'] = user_data.get('karma_position', max_position + 1)
                user['karma_gain'] = user_data.get('karma_gain_total', 0)
            user_values.sort(key=itemgetter('position'))

            if my_user.website_published and my_user.karma and my_user.id not in users.ids:
                # Need to keep the dom to search only for users that appear in the ranking page
                current_user = User.sudo().search(expression.AND([[('id', '=', my_user.id)], dom]))
                if current_user:
                    current_user_values = self._prepare_all_users_values(current_user)[0]

                    user_data = self._get_position_map(position_domain, current_user, group_by).get(current_user.id, {})
                    current_user_values['position'] = user_data.get('karma_position', 0)
                    current_user_values['karma_gain'] = user_data.get('karma_gain_total', 0)

        else:
            user_values = []
            pager = {'page_count': 0}

        render_values.update({
            'top3_users': user_values[:3] if not search_term and page == 1 else [],
            'users': user_values,
            'my_user': current_user_values,
            'pager': pager,
            'course_bool': True,
        })
        return request.render("website_profile.users_page_main", render_values)

    @http.route(['/region-wise/leadership'], type='http', auth="public", website=True, sitemap=True)
    def view_all_users_regionwise(self, page=1, **kwargs):
        User = request.env['res.users']
        if kwargs.get('res_state_id'):
            region_id = kwargs.get('res_state_id')
            request.env.user.region_from_website = region_id
        else:
            region_id = request.env.user.region_from_website

        user_lst = []
        if region_id:
            user = request.env['res.users'].sudo().search([('region', '=', region_id)])
            if user:
                for user_val in user:
                    user_lst.append(user_val.id)

            dom = [('karma', '>', 1), ('website_published', '=', True), ('id', 'in', user_lst)]

        # region_id1= region_id.split('(')
        # region_id2= region_id1[1].split(',')
        # state_id = request.env['res.country.state'].search([('id','=',int(region_id2[0]))])
        # user_lst= []
        # if state_id:
        #     user= request.env['res.users'].sudo().search([('state_id','=',state_id.id)])
        #     if user:
        #         for user_val in user:
        #             user_lst.append(user_val.id)
        #
        #     dom = [('karma', '>', 1), ('website_published', '=', True),('id', 'in', user_lst)]
        else:
            dom = [('karma', '>', 1), ('website_published', '=', True)]

        # Searches
        search_term = kwargs.get('search')
        group_by = kwargs.get('group_by', False)
        render_values = {
            'search': search_term,
            'group_by': group_by or 'all',
        }
        if search_term:
            dom = expression.AND(
                [['|', ('name', 'ilike', search_term), ('partner_id.commercial_company_name', 'ilike', search_term)],
                 dom])

        user_count = User.sudo().search_count(dom)
        my_user = request.env.user
        current_user_values = False
        if user_count:
            page_count = math.ceil(user_count / self._users_per_page)
            pager = request.website.pager(url="/profile/users", total=user_count, page=page, step=self._users_per_page,
                                          scope=page_count if page_count < self._pager_max_pages else self._pager_max_pages)

            # users_ids = User.sudo().search(dom, limit=self._users_per_page, offset=pager['offset'], order='karma DESC')
            users = User.sudo().search(dom, limit=self._users_per_page, offset=pager['offset'], order='karma DESC')
            user_values = self._prepare_all_users_values(users)

            # Get karma position for users (only website_published)
            position_domain = [('karma', '>', 1), ('website_published', '=', True)]
            position_map = self._get_position_map(position_domain, users, group_by)

            max_position = max([user_data['karma_position'] for user_data in position_map.values()], default=1)
            for user in user_values:
                user_data = position_map.get(user['id'], dict())
                user['position'] = user_data.get('karma_position', max_position + 1)
                user['karma_gain'] = user_data.get('karma_gain_total', 0)
            user_values.sort(key=itemgetter('position'))

            if my_user.website_published and my_user.karma and my_user.id not in users.ids:
                # Need to keep the dom to search only for users that appear in the ranking page
                current_user = User.sudo().search(expression.AND([[('id', '=', my_user.id)], dom]))
                if current_user:
                    current_user_values = self._prepare_all_users_values(current_user)[0]

                    user_data = self._get_position_map(position_domain, current_user, group_by).get(current_user.id, {})
                    current_user_values['position'] = user_data.get('karma_position', 0)
                    current_user_values['karma_gain'] = user_data.get('karma_gain_total', 0)

        else:
            user_values = []
            pager = {'page_count': 0}

        render_values.update({
            'top3_users': user_values[:3] if not search_term and page == 1 else [],
            'users': user_values,
            'my_user': current_user_values,
            'pager': pager,
            'region_bool': True,
        })
        return request.render("website_profile.users_page_main", render_values)


class CustomerPortal(Controller):
    
    @http.route(['/privacypolicy'], type='http', auth="user", website=True)
    def home(self, **kw):
        return request.render("website.footer_custom")


class TermsServices(http.Controller):
    
    @http.route(['/terms'], type='http', auth="public", website=True)
    def terms(self, **kw):
        return request.render("ecom_lms.request_form")


class PrivacyPolicy(Controller):
    
    @http.route(['/services'], type='http', auth="public", website=True)
    def privacy(self, **kw):
        return request.render("ecom_lms.privacy_form")

    def _get_login_redirect_url(uid, redirect=None):
        """ Decide if user requires a specific post-login redirect, e.g. for 2FA, or if they are
        fully logged and can proceed to the requested URL
        """
        if request.session.uid:  # fully logged
            return redirect or '/web'
    
        # partial session (MFA)
        url = request.env(user=uid)['res.users'].browse(uid)._mfa_url()
        if not redirect:
            return url
    
        parsed = werkzeug.urls.url_parse(url)
        qs = parsed.decode_query()
        qs['redirect'] = redirect
        return parsed.replace(query=werkzeug.urls.url_encode(qs)).to_url()


class CandidatePage(Controller):
    
    @http.route(['/candidate'], type='http', auth="public", website=True)
    def candidate(self, redirect=None, **kw):
        ensure_db()

        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.render("ecom_lms.candidate_login")

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid

            try:
                user_id = request.env["res.users"].sudo().search(
                    [('login', '=', request.params['login']), ('pre_joinee_code', '=', request.params['candidate'])])
                if user_id:

                    uid = request.session.authenticate(request.session.db, request.params['login'],
                                                       request.params['password'])

                    request.params['login_success'] = True
                    return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
                else:
                    request.uid = old_uid

                    values['error'] = _("Wrong login/password/Pre Joinee Code")

            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password/Pre Joinee Code")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render("ecom_lms.candidate_login", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def _login_redirect(self, uid, redirect=None):
        return _get_login_redirect_url(uid, redirect)

    @http.route(['/customer'], type='http', auth="public", website=True)
    def customer(self, redirect=None, **kw):
        ensure_db()

        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.render("ecom_lms.customer_login")

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()

        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid

            try:
                user_id = request.env["res.users"].sudo().search(
                    [('login', '=', request.params['login']), ('customer_code', '=', request.params['customer'])])
                if user_id:

                    uid = request.session.authenticate(request.session.db, request.params['login'],
                                                       request.params['password'])

                    request.params['login_success'] = True
                    return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
                else:
                    request.uid = old_uid

                    values['error'] = _("Wrong login/password/Customer Code")

            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password/Customer Code")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render("ecom_lms.customer_login", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route(['/employee'], type='http', auth="public", website=True)
    def employee(self, redirect=None, **kw):
        ensure_db()

        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.render("ecom_lms.employee_login")

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()

        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':

            old_uid = request.uid

            try:
                user_id = request.env["res.users"].sudo().search(
                    [('login', '=', request.params['login'])])
                if user_id:

                    uid = request.session.authenticate(request.session.db, request.params['login'],
                                                       request.params['password'])

                    request.params['login_success'] = True
                    return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
                else:
                    request.uid = old_uid

                    values['error'] = _("Wrong login/password")

            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render("ecom_lms.employee_login", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


class Custom_Website_course(http.Controller):
    
    @http.route('/accept/invite/lesson', type='http', auth="none")
    def lesson_accept(self, db, token, action, id, **kwargs):
        with request.env.registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            record = env['slide.slide'].search([('lesson_access_token', '=', token)])
            if record:
                if request.session.uid:
                    user = env['res.users'].browse(request.session.uid)
        return self.lesson_view(db, token, action, id, view='form')
    
    @http.route('/view/invited/lesson', type='http', auth="none")
    def lesson_view(self, db, token, action, id, view='form'):

        with request.env.registry.cursor() as cr:

            env = api.Environment(cr, SUPERUSER_ID, {})

            if request.session.uid:
                slide_id = request.env['slide.slide'].sudo().search([('id', '=', id)], limit=1)
                url = slide_id.get_lesson_url()
                return werkzeug.utils.redirect(url)
                # return slide_id.get_lesson_url()
            else:
                return werkzeug.utils.redirect('/web/login', 303)

    @http.route('/accept/slide/channel', type='http', auth="none")
    def accept(self, db, token, action, id, **kwargs):
        with request.env.registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            record = env['slide.channel'].search([('channel_access_token', '=', token)])
            if record:
                if request.session.uid:
                    user = env['res.users'].browse(request.session.uid)
                    # group_id=request.env.ref('shubbaktech_sale_invoice_approvals.group_partner_credit_limit_approve')
                    # if group_id in user.groups_id:
                    #     record.action_approve_credit_limit()
        return self.view(db, token, action, id, view='form')

    @http.route('/view/slide/channel', type='http', auth="none")
    def view(self, db, token, action, id, view='form'):

        with request.env.registry.cursor() as cr:

            env = api.Environment(cr, SUPERUSER_ID, {})

            if request.session.uid:
                return werkzeug.utils.redirect(
                    '/web?db=%s#id=%s&view_type=form&model=slide.channel' % (request.env.cr.dbname, id))
            else:
                #  env = api.Environment(request.cr, SUPERUSER_ID, request.context)
                #  website = env['website'].get_current_website()
                #  request.uid = website and website._get_cached('user_id')
                #
                #  return werkzeug.utils.redirect(
                #      '/web?db=%s#id=%s&view_type=form&model=sale.order' % (request.env.cr.dbname, id))
                return werkzeug.utils.redirect('/web/login', 303)

    @http.route('/accept/journey', type='http', auth="none")
    def accept_journey(self, db, token, action, id, **kwargs):
        with request.env.registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            record = env['course.journey'].search([('channel_access_token', '=', token)])
            if record:
                if request.session.uid:
                    user = env['res.users'].browse(request.session.uid)
                    # group_id=request.env.ref('shubbaktech_sale_invoice_approvals.group_partner_credit_limit_approve')
                    # if group_id in user.groups_id:
                    #     record.action_approve_credit_limit()
        return self.view_journey(db, token, action, id, view='form')

    @http.route('/view/accept/journey', type='http', auth="none")
    def view_journey(self, db, token, action, id, view='form'):

        with request.env.registry.cursor() as cr:

            env = api.Environment(cr, SUPERUSER_ID, {})

            if request.session.uid:
                return werkzeug.utils.redirect(
                    '/web?db=%s#id=%s&view_type=form&model=course.journey' % (request.env.cr.dbname, id))
            else:
                #  env = api.Environment(request.cr, SUPERUSER_ID, request.context)
                #  website = env['website'].get_current_website()
                #  request.uid = website and website._get_cached('user_id')
                #
                #  return werkzeug.utils.redirect(
                #      '/web?db=%s#id=%s&view_type=form&model=sale.order' % (request.env.cr.dbname, id))
                return werkzeug.utils.redirect('/web/login', 303)


class CustomSurvey(Survey):

    @http.route('/survey/submit/<string:survey_token>/<string:answer_token>', type='json', auth='public', website=True)
    def survey_submit(self, survey_token, answer_token, **post):
        """ Submit a page from the survey.
        This will take into account the validation errors and store the answers to the questions.
        If the time limit is reached, errors will be skipped, answers will be ignored and
        survey state will be forced to 'done'"""
        # Survey Validation
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        if access_data['validity_code'] is not True:
            return {'error': access_data['validity_code']}
        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        if answer_sudo.state == 'done':
            return {'error': 'unauthorized'}

        questions, page_or_question_id = survey_sudo._get_survey_questions(answer=answer_sudo,
                                                                           page_id=post.get('page_id'),
                                                                           question_id=post.get('question_id'))

        if not answer_sudo.test_entry and not survey_sudo._has_attempts_left(answer_sudo.partner_id, answer_sudo.email,
                                                                             answer_sudo.invite_token):
            # prevent cheating with users creating multiple 'user_input' before their last attempt
            return {'error': 'unauthorized'}
        if answer_sudo.survey_time_limit_reached or answer_sudo.question_time_limit_reached:
            if answer_sudo.question_time_limit_reached:
                time_limit = survey_sudo.session_question_start_time + relativedelta(
                    seconds=survey_sudo.session_question_id.time_limit
                )
                time_limit += timedelta(seconds=3)
            else:
                time_limit = answer_sudo.start_datetime + timedelta(minutes=survey_sudo.time_limit)
                time_limit += timedelta(seconds=10)
            if fields.Datetime.now() > time_limit:
                # prevent cheating with users blocking the JS timer and taking all their time to answer
                return {'error': 'unauthorized'}

        errors = {}
        # Prepare answers / comment by question, validate and save answers
        for question in questions:
            inactive_questions = request.env[
                'survey.question'] if answer_sudo.is_session_answer else answer_sudo._get_inactive_conditional_questions()
            if question in inactive_questions:  # if question is inactive, skip validation and save
                continue
            answer, comment = self._extract_comment_from_answers(question, post.get(str(question.id)))
            errors.update(question.validate_question(answer, comment))
            if not errors.get(question.id):
                answer_sudo.save_lines(question, answer, comment)
        if errors and not (answer_sudo.survey_time_limit_reached or answer_sudo.question_time_limit_reached):
            return {'error': 'validation', 'fields': errors}

        if not answer_sudo.is_session_answer:
            answer_sudo._clear_inactive_conditional_answers()

        if answer_sudo.survey_time_limit_reached or survey_sudo.questions_layout == 'one_page':
            answer_sudo._mark_done()
        elif 'previous_page_id' in post:
            # Go back to specific page using the breadcrumb. Lines are saved and survey continues
            return self._prepare_question_html(survey_sudo, answer_sudo, **post)
        else:
            vals = {'last_displayed_page_id': page_or_question_id}
            if not answer_sudo.is_session_answer:
                next_page = survey_sudo._get_next_page_or_question(answer_sudo, page_or_question_id)
                if not next_page:
                    answer_sudo._mark_done()

            answer_sudo.write(vals)
        if answer_sudo and answer_sudo.scoring_success and answer_sudo.slide_id:

            certification_url = answer_sudo.slide_id._generate_certification_url().get(answer_sudo.slide_id.id)
            if certification_url:

                base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                finalurl = base_url + str(certification_url)
                # if newcompleted == True and i.completion == 100:
                outgoing_server_name = request.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
                template_id = request.env.ref('ecom_lms.email_template_course_feedback')
                if template_id and outgoing_server_name:
                    template_id.email_from = outgoing_server_name
                    template_id.email_to = request.env.user.partner_id.email
                    template_id.subject = 'Submit Certification/Feedback'
                    template_id.body_html = """ <html>
                                       <head></head>
                                       <body>
                                       <p>Dear """ + request.env.user.partner_id.name + """</p>
                                        <p>
                                       Please click on the Start Button to Test Certification for the completed """ + answer_sudo.slide_id.channel_id.name + """course.

                                        </p>
                                        <p>
                                         <a href=""" + str(finalurl) + """
                style="padding: 5px 10px; color: #FFFFFF; text-decoration: none; background-color: #875A7B; border: 1px solid #875A7B; border-radius: 3px">
                Start Button</a></p>
                <p>Thankyou</p>"""
                    demo = template_id.send_mail(request.env.user.partner_id.id, force_send=True)
        return self._prepare_question_html(survey_sudo, answer_sudo)


class EcomWebsite(Website):

    def _login_redirect(self, uid, redirect=None):
        """ Redirect regular users (employees) to the backend) and others to
        the frontend
        """
        if not redirect and request.params.get('login_success'):
            user_id= request.env['res.users'].browse(uid)
            if request.env['res.users'].browse(uid).has_group('base.group_user'):
                if not user_id.image_1920:
                    redirect = "/profile/view/user/%d" % request.session.uid
                    
                else:
                    redirect = b'/web?' + request.httprequest.query_string
            else:
                if not user_id.image_1920:
                    redirect = "/profile/view/user/%d" % request.session.uid
                else:
                    redirect = '/slides'
        return super()._login_redirect(uid, redirect=redirect)


class EcomAuthSignupHome(AuthSignupHome):

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match. Please retype them correctly."))
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '')
        if lang in supported_lang_codes:
            values['lang'] = lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()



class EcomSession(Session):

    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        time_spent_records = request.env['time.spent.report'].sudo().search([('name','=',request.session.uid),('logout','=',False)])
        for rec in time_spent_records:
            rec.write({'logout':True,
                        'check_out':fields.datetime.now()})
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)

