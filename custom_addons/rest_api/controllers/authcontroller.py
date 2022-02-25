# -*- coding: utf-8 -*-
from itertools import chain

from . import utility as utils
from .main import *
from odoo import http, tools, _
from odoo.addons.base.ir.ir_mail_server import MailDeliveryException
from odoo.http import request

_logger = logging.getLogger(__name__)


class IkinakiAUTH(http.Controller):

    # Ikinaki API for the Signup
    @http.route('/api/v1.0/signup', methods=['POST'], type='http', auth='none', csrf=False)
    def ikisignup(self, **post):
        name = post.get('name')
        email = post.get('email')
        vals = {'lang': 'en_US', 'groups_id': [(6, 0, [1, 8, 7])], 'tz': False, 'name': name, 'notify_email': 'always',
                'alias_contact': False, 'image': False, 'alias_id': False,
                 'signature': False, 'active': True, 'login': email, 'email': email,
                'action_id': False
                }
        try:
            responseData = request.env['res.users'].sudo().create(vals)
            returnData = {
                "status_cd": 1,
                "message": "user created",
                "id": int(responseData.id),
                "email": str(responseData.login),
                "name": str(responseData.partner_id.name)
            }
            return utils.generateResponse(status_code=200, response=returnData)
        except MailDeliveryException:
            responseData = {
                "status_code": 1,
                "message": "User Created but unable to send the password reset link",
                "user_id": responseData.id
            }
            return utils.generateResponse(status_code=200, response=responseData)
        except Exception as e:
            responseData = {
                "status_code": 0,
                "message": "Email-Id already exists",
                "error_message": str(e)
            }
            return utils.generateResponse(status_code=200, response=responseData)

    # ikinaki login
    @http.route('/api/v1.0/login', methods=['POST'], type='http', auth='none', csrf=False)
    def ikinakilogin(self, **post):
        email = post.get('email')
        password = post.get('password')
        db_name = odoo.tools.config.get('db_name')
        print(email, password, db_name)
        if not db_name:
            responseData = {
                "status_code": 0,
                "message": "it's necessary to set the parameter 'db_name' in Odoo config file!"
            }
            return utils.generateResponse(status_code=200, response=responseData)
        if not db_name or not email or not password:
            responseData = {
                "status_code": 0,
                "message": "Empty value of 'db' or 'username' or 'password'!"
            }
            return utils.generateResponse(status_code=200, response=responseData)
        try:
            request.session.authenticate(db_name, email, password)
        except:
            rsponseData = {
                "status_code": 0,
                "message": "Invalid database"
            }
            return utils.generateResponse(status_code=200, response=rsponseData)
        uid = request.session.uid
        if not uid:
            responseData = {
                "status_code": 0,
                "message": "Authentication Failed"
            }
            return utils.generateResponse(status_code=200, response=responseData)
        access_token = generate_token()
        expires_in = access_token_expires_in
        refresh_token = generate_token()
        refresh_expires_in = refresh_token_expires_in
        token_store.save_all_tokens(
            access_token=access_token,
            expires_in=expires_in,
            refresh_token=refresh_token,
            refresh_expires_in=refresh_expires_in,
            user_id=uid)
        responseData = {
            'uid': uid,
            'user_context': request.session.get_context() if uid else {},
            'company_id': request.env.user.company_id.id if uid else 'null',
            'access_token': access_token,
            'expires_in': expires_in,
            'refresh_token': refresh_token,
            'refresh_expires_in': refresh_expires_in,
            'partner_id': request.env.user.partner_id.id if uid else 'null'}
        return utils.generateResponse(status_code=200, response=responseData)


    @http.route('/api/v1.0/refresh', methods=['POST'], type='http', auth='none', csrf=False)
    @check_permissions
    def api_auth_refreshtoken(self, **post):
        refresh_token = post.get('refresh_token')
        if not refresh_token:
            responseData = {
                "status_cd": 0,
                "error_message": "No refresh token was provided in request!"
            }
            return utils.generateResponse(status_code=200, response=responseData)
        refresh_token_data = token_store.fetch_by_refresh_token(refresh_token)
        if not refresh_token_data:
            responseData = {
                "status_cd": 0,
                "error_message": "Token is expired or invalid!"
            }
            return utils.generateResponse(status_code=200, response=responseData)
        old_access_token = refresh_token_data['access_token']
        new_access_token = generate_token()
        uid = refresh_token_data['user_id']
        refresh_expires_in = refresh_token_expires_in
        token_store.update_access_token(
            old_access_token=old_access_token,
            new_access_token=new_access_token,
            expires_in=access_token_expires_in,
            refresh_token=refresh_token,
            user_id=uid)
        responseData = {
            'uid': uid,
            'user_context': request.session.get_context() if uid else {},
            'company_id': request.env.user.company_id.id if uid else 'null',
            'access_token': new_access_token,
            'expires_in': access_token_expires_in,
            'refresh_token': refresh_token,
            'refresh_expires_in': refresh_expires_in,
            'partner_id': request.env.user.partner_id.id if uid else 'null'}
        return utils.generateResponse(status_code=200, response=responseData)

        # Successful response:
        # return werkzeug.wrappers.Response(
        #     status=OUT__auth_refreshtoken__SUCCESS_CODE,
        #     content_type='application/json; charset=utf-8',
        #     headers=[('Cache-Control', 'no-store'),
        #              ('Pragma', 'no-cache')],
        #     response=json.dumps({
        #         'access_token': new_access_token,
        #     }),
        # )