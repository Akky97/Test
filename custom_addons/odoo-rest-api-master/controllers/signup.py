import logging
import json
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
            email = jdata.get('email')
            name = jdata.get('name')
            password = jdata.get('password')
            confirm_password = jdata.get('confirm_password')
            qcontext.update({"login": email, "name": name, "password": password,
                             "confirm_password": confirm_password})
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
                    res = {"message": "Account Successfully Created","status_code":200}
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
