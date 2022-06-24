# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request

"""Common methods"""
import ast
import logging
from odoo.http import Response
from odoo.tools import date_utils
from .error_or_response_parser import *
from .exceptions import QueryFormatError

_logger = logging.getLogger(__name__)

from werkzeug.wrappers import BaseResponse
from odoo.tools.config import config

original_set_cookie = BaseResponse.set_cookie


def set_cookie(self, key, value='', max_age=None, expires=None,
               path='/', domain=None, secure=False, httponly=False):
    if expires != 0 and max_age != 0:  # not delete
        if config.get('cookie_max_age') is not None:
            max_age = int(config['cookie_max_age'])
        if config.get('cookie_secure') is not None:
            secure = bool(config['cookie_secure'])
        if config.get('cookie_domain') is not None:
            domain = config['cookie_domain']

    return original_set_cookie(self, key, value=value, max_age=max_age, expires=expires, path=path, domain=domain,
                               secure=secure, httponly=httponly)


BaseResponse.set_cookie = set_cookie


def token_response(data):
    """Token Response
    This will be return when token request was successfully processed."""
    return Response(
        json.dumps(data),
        status=200,
        content_type='application/json; charset=utf-8',
        headers=[
            ('Cache-Control', 'no-store'),
            ('Pragma', 'no-cache')
        ]
    )


def valid_response(data, status=200):
    """Valid Response
    This will be return when the http request was successfully processed."""
    response = None

    if data is None:
        response = None
    elif isinstance(data, str):
        response = json.dumps({
            'message': data
        })
    elif isinstance(data, list):
        response = json.dumps({
            'count': len(data),
            'data': data
        }, sort_keys=True, default=date_utils.json_default)
    else:
        response = json.dumps({
            'data': data
        }, sort_keys=True, default=date_utils.json_default)

    return Response(
        response,
        status=status,
        content_type='application/json; charset=utf-8'
    )


def invalid_response(error, message=None, status=401):
    """Invalid Response
    This will be the return value whenever the server runs into an error
    either from the client or the server."""

    response = json.dumps({
        'type': error,
        'message': str(message) if str(message) else 'wrong arguments (missing validation)'
    })

    return Response(
        response,
        status=status,
        content_type='application/json; charset=utf-8'
    )


def prepare_response(data, one=False):
    """Replaces ids as lists with two different keys with id and string values.
    Like: {country_id: [1, 'United States'], company_currency: [1, 'EUR']} => {country_id: 1, country: 'United States', company_currency_id: 1, company_currency: 'EUR'}.
    Also records in Odoo are lists, and when we need only record itself, returned first list item or None"""
    result = None

    if isinstance(data, list):
        result = []
        for _result in data:
            if isinstance(_result, dict):
                item = {}
                for key, value in _result.items():
                    if isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], int) and isinstance(
                            value[1], str):
                        _int, _str = value
                        _key = key.replace('_id', '').replace('_uid', '')
                        _key_id = '{}_id'.format(_key)
                        item[_key_id] = _int
                        item[_key] = _str
                    else:
                        item[key] = value
            else:
                item = _result
            result.append(item)

        if one:
            if len(result) > 0:
                result = result[0]
            else:
                result = None
    return result


def parse_dict(obj):
    keys = list(obj.keys())
    if len(keys) == 0:
        return None

    key = keys[0]
    if len(key) == 0:
        return None

    value = obj[key]

    left, center, right = '', '', value

    if key[-1] == '!':
        center = '!='
        left = key[0:-1]
    else:
        center = '='
        left = key

    return (left, center, right)


def parse_expr(expr):
    if isinstance(expr, tuple):
        return expr
    if isinstance(expr, list):
        return tuple(expr)
    elif isinstance(expr, dict):
        return parse_dict(expr)


def parse_domain(prepared):
    result = []
    for expr in prepared:
        obj = parse_expr(expr)
        if obj:
            result.append(obj)
    return result


def parse_list(domain):
    if isinstance(domain, str):
        if not (domain[0] == '[' and domain[-1] == ']'):
            domain = '[{0}]'.format(domain)
        domain = ast.literal_eval(domain)
    return domain


def extract_arguments(payload={}):
    """Parse "[('id','=','100')]" or {'id': '100'} notation as domain
    """
    domain, fields, offset, limit, order = [], [], 0, 0, None
    _domain = payload.get('domain')
    _fields = payload.get('fields')
    _offset = payload.get('offset')
    _limit = payload.get('limit')
    _order = payload.get('order')
    if _domain:
        domain_list = parse_list(_domain)
        domain = parse_domain(domain_list)
    if _fields:
        fields += parse_list(_fields)
    if _offset:
        offset = int(_offset)
    if _limit:
        limit = int(_limit)
    if _order:
        parsed_order = parse_list(_order)
        order = ','.join(parsed_order) if parsed_order else None
    return [domain, fields, offset, limit, order]


_logger = logging.getLogger(__name__)

expires_in = 'my_mandi.access_token_expires_in'


class AccessToken(http.Controller):
    """."""

    @http.route('/api/auth/token', methods=['POST'], type='http', auth='none', csrf=False, cors='*')
    def token(self, **kwargs):
        """The token URL to be used for getting the access_token:
        Args:
            **post must contain login and password.
        Returns:
            returns https response code 404 if failed error message in the body in json format
            and status code 202 if successful with the access_token.
        Example:
           import requests
           headers = {'content-type': 'text/plain', 'charset':'utf-8'}
           data = {
               'login': 'admin',
               'password': 'admin',
               'db': 'galago.ng'
            }
           base_url = 'http://odoo.ng'
           req = requests.post(
               '{}/api/auth/token'.format(base_url), data=data, headers=headers)
           content = json.loads(req.content.decode('utf-8'))
           headers.update(access-token=content.get('access_token'))
        """
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        db = jdata.get('db')
        login = jdata.get('login')
        password = jdata.get('password')
        try:
            db, username, password = db, login, password
        except Exception as e:
            # Invalid database:
            error = 'missing'
            info = 'either of the following are missing [db, username,password]'
            status = 403
            _logger.error(info)
            return invalid_response(error, info, status)

        # Login in odoo database:
        try:
            # request.session.logout()
            user = request.env['res.users'].sudo().search([('login', '=', login)])
            request.session.authenticate(db, login, password)
            r = request.env['ir.http'].session_info()
        except Exception as e:
            # Invalid database:
            error = 'invalid_database'
            info = "E-mail or Password is not valid"
            _logger.error(info)
            return invalid_response(error, info)

        uid = request.session.uid
        res_id = request.env['ir.attachment'].sudo()
        res_id = res_id.sudo().search([('res_model', '=', 'res.partner'),
                                       ('res_field', '=', 'image_1920'),
                                       ('res_id', 'in', [request.env.user.partner_id.id])])
        # res_id.sudo().write({"public": True})
        # odoo login failed:
        if not uid:
            error = 'authentication failed'
            info = 'authentication failed'
            _logger.error(info)
            return invalid_response(error, info)
        # Generate tokens
        access_token = request.env['api.access_token'].sudo().find_one_or_create_token(
            user_id=uid, create=True)
        # Successful response:
        print(request.httprequest.headers, ":fg")
        base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)

        return token_response({
            'uid': uid,
            'user_context': request.session.get_context(),
            'company_id': request.env.user.company_id.id,
            'email': request.env.user.partner_id.email,
            'name': request.env.user.name,
            "image": base_url.value + '/web/image/res.partner/' + str(request.env.user.partner_id.id) + "/image_1920",
            'access_token': access_token,
            'expires_in': request.env.ref(expires_in).sudo().value,
            'session_id': request.session.sid,
            'partner_id': request.env.user.partner_id.id,
            'country_id': request.env.user.partner_id.country_id.id,
            'user_type': request.env.user.user_type
        })

    @http.route('/api/logout/auth/token', methods=['POST'], type='http', auth='none', csrf=False, cors='*')
    def delete(self, **params):
        """."""
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if not jdata.get('access_token'):
                msg = {"message": "Please provide access token", "status_code": 400}
                return return_Response_error(msg)
            request_token = jdata.get('access_token')
            access_token = request.env['api.access_token'].sudo().search([('token', '=', request_token)])

            for token in access_token:
                token.unlink()
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)

        # Successful response:
        res = {
            "result": "Access Token Deleted Successfully", "status": 200
        }
        return return_Response(res)

