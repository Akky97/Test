import logging
import json
import smtplib

import werkzeug.wrappers
from odoo import http
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
import logging
import werkzeug

from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db, Home, SIGN_UP_REQUEST_PARAMS
from odoo.addons.base_setup.controllers.main import BaseSetup
from odoo.exceptions import UserError
from odoo.http import request
from .error_or_response_parser import *

"""Common methods"""
import ast
import logging
import json
import random
import math

from odoo.http import Response
from odoo.tools import date_utils

_logger = logging.getLogger(__name__)


class SignupAPI(AuthSignupHome):
    @http.route('/api/v1/c/customer/signup', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def signup(self):
        try:
            qcontext = self.get_auth_signup_qcontext()
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if not jdata.get('email') or not jdata.get('name') or not jdata.get('password') or not jdata.get('otp'):
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
            email = jdata.get('email')
            name = jdata.get('name')
            password = jdata.get('password')
            otp = jdata.get('otp')
            confirm_password = jdata.get('confirm_password')
            qcontext.update({"login": email, "name": name, "password": password,
                             "confirm_password": confirm_password})
            email_veri = request.env['email.verification'].sudo().search([('email', '=', email)], limit=1,order='create_date desc')
            if email_veri and int(email_veri.otp) == int(otp):
                pass
            else:
                msg = {"message": "OTP not verified!!", "status_code": 400}
                return return_Response_error(msg)
            if not qcontext.get('token') and not qcontext.get('signup_enabled'):
                raise werkzeug.exceptions.NotFound()

            if 'error' not in qcontext and request.httprequest.method == 'POST':
                try:
                    self.do_signup(qcontext)
                    # Send an account creation confirmation email
                    if qcontext.get('token'):
                        User = request.env['res.users']
                        user_sudo = User.sudo().search(
                            User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                        )
                        template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                                   raise_if_not_found=False)
                        if user_sudo and template:
                            template.sudo().send_mail(user_sudo.id, force_send=True)
                    res = {"message": "Account Successfully Created", "status_code": 200}
                    email_get = request.env['email.verification'].sudo().search([('email', '=', email)],order='create_date desc',limit=1)
                    email_get.sudo().unlink()
                    return return_Response(res)
                except KeyError as e:
                    msg = e.args[0]
                    return error_response(e, msg)
                except (SignupError, AssertionError) as e:
                    user = request.env["res.users"].sudo().search([("login", "=", qcontext.get('login'))])
                    if user:
                        msg = {"message": "Another user is already registered using this email address.","status_code":400}
                        return return_Response_error(msg)
                    else:
                        msg = {"message": "Could not create a new account.","status_code":400}
                        return return_Response_error(msg)
        except Exception as e:
            msg = {"message": "Something Went Wrong.","status_code":400}
            return return_Response_error(msg)

    @http.route('/api/v1/c/customer/sendotp', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def sendmail_custom(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
            if not jdata.get('name') or not jdata.get('email'):
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
            name = jdata.get('name')
            email = jdata.get('email')
            template = request.env.ref('odoo-rest-api-master.send_otp_email_template',
                                       raise_if_not_found=False)
            outgoing_server_name = request.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
            otp = random.randint(100000, 999999)
            if outgoing_server_name:
                email_check = request.env['res.users'].sudo().search([('login', '=', email)])
                if email_check:
                    msg = {"message": "User already exist!!", "status_code": 400}
                    return return_Response_error(msg)
                template.email_from = outgoing_server_name
                template.email_to = email
                template.body_html = f"""<![CDATA[
                                            <div class="container-fluid">
                <div class="row" style="background: #5297F8; height: 50px;"><img src="https://stagingbackend.pandostores.com/odoo-rest-api-master/static/src/image/Pando_logo.svg"/></div>
                <div>
                <p>Dear {name}</p>
                <br />
                <h2>Your Signup OTP is {otp}</h2>
                <br />
                <p><strong> Please note:-</strong>This OTP has also been sent to your chosen email id. Please se do not share this OTP with anyone for security reasons.</p>
                <br />
                <p><strong> In case you have not requested this action, please contact us. </strong></p>
                <p><strong>Phone number :-</strong> +65 6589 8807</p>
                </div>
                <br />
                <div style="text-align: center; background: #EEF5FF; padding: 15px;"><a href="https://pandostores.com/"> https://pandostores.com </a></div>
                </div>"""
                template.sudo().send_mail(3, force_send=True)
                vals = {'email': email, 'otp': otp}
                data = request.env['email.verification'].sudo().create(vals)
                res = {"message": "OTP sent Successfully!!", "status_code": 200}
                return return_Response(res)
        except Exception as e:
            msg = {"message": str(e), "status_code": 400}
            return return_Response_error(msg)

    @http.route('/api/v1/c/customer/forgot_password_send_otp', type='http', auth='public', methods=['POST'], csrf=False,
                cors='*')
    def forgot_password_send_otp(self):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata and jdata.get('email'):
                email = jdata.get('email')
                user = request.env['res.users'].sudo().search([('login', '=', email)])
                if user:
                    name = user.partner_id.name
                    template = request.env.ref('odoo-rest-api-master.send_otp_email_template',
                                               raise_if_not_found=False)
                    outgoing_server_name = request.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
                    otp = random.randint(100000, 999999)
                    if outgoing_server_name:
                        template.email_from = outgoing_server_name
                        template.email_to = email
                        template.body_html = f"""<![CDATA[
                            <p>Dear {name},
                            <br/><br/>
                            You have requested to change password. So your OTP is {otp}
                            <br/><br/>
                            Thanks and Regards<br/>
                            Pando Store
                            </p>"""
                        template.sudo().send_mail(3, force_send=True)
                        vals = {'email': email, 'otp': otp}
                        email_otp = request.env['forgot.password'].sudo().search([('email', '=', email)])
                        if email_otp:
                            email_otp.sudo().write({'otp': otp})
                        else:
                            data = request.env['forgot.password'].sudo().create(vals)
                        res = {"message": "OTP sent Successfully!!", "status_code": 200}
                        return return_Response(res)
                else:
                    msg = {"message": "User does not exist!!", "status_code": 400}
                    return return_Response_error(msg)
            else:
                msg = {"message": "Email is not present in parameter", "status_code": 400}
                return return_Response_error(msg)
        except Exception as e:
            msg = {"message": str(e), "status_code": 400}
            return return_Response_error(msg)

    @http.route('/api/v1/c/customer/forgot_password', type='http', auth='public', methods=['POST'], csrf=False,
                cors='*')
    def forgot_password(self):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata and jdata.get('email') and jdata.get('otp') and jdata.get('password'):
                email = jdata.get('email')
                otp = jdata.get('otp')
                psw = jdata.get('password')
                user = request.env['res.users'].sudo().search([('login', '=', email)])
                if not user:
                    msg = {"message": "User does not exist!!", "status_code": 400}
                    return return_Response_error(msg)
                email_otp = request.env['forgot.password'].sudo().search([('email', '=', email)],
                                                                         order='create_date desc', limit=1)
                if not email_otp:
                    msg = {"message": "Please Resend OTP", "status_code": 400}
                    return return_Response_error(msg)
                if user and email_otp:
                    if int(otp) == int(email_otp.otp):
                        user.sudo().write({'password': psw})
                        msg = {"message": "Password has been Changed Successfully", "status_code": 200}
                        return return_Response(msg)
                    else:
                        msg = {"message": "OTP Is Incorrect", "status_code": 200}
                        return return_Response(msg)
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except Exception as e:
            msg = {"message": str(e), "status_code": 400}
            return return_Response_error(msg)


