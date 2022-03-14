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
            email_veri = request.env['email.verification'].sudo().search([('email', '=', email)], limit=1)
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
                    email_get = request.env['email.verification'].sudo().search([('email', '=', email)], limit=1)
                    email_get.sudo().unlink()
                    return return_Response(res)
                except KeyError as e:
                    msg = e.args[0]
                    return error_response(e, msg)
                except (SignupError, AssertionError) as e:
                    user = request.env["res.users"].sudo().search([("login", "=", qcontext.get('login'))])
                    if user:
                        print("user", user)
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
            print(name, email)
            template = request.env.ref('odoo-rest-api-master.send_otp_email_template',
                                       raise_if_not_found=False)
            print(template)
            outgoing_server_name = request.env['ir.mail_server'].sudo().search([], limit=1).smtp_user
            print(outgoing_server_name)
            otp = random.randint(100000, 999999);
            print(otp)
            if outgoing_server_name:
                email_check = request.env['res.users'].sudo().search([('login', '=', email)])
                print(email_check)
                if email_check:
                    msg = {"message": "User already exist!!", "status_code": 400}
                    return return_Response_error(msg)
                template.email_from = outgoing_server_name
                template.email_to = email
                template.body_html = int(otp)
                template.sudo().send_mail(3, force_send=True)
                vals = {'email': email, 'otp': otp}
                data = request.env['email.verification'].sudo().create(vals)
                print(data)
                res = {"message": "OTP sent Successfully!!", "status_code": 200}
                return return_Response(res)
        except Exception as e:
            msg = {"message": str(e), "status_code": 400}
            return return_Response_error(msg)


