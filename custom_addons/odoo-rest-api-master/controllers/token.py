# Part of odoo. See LICENSE file for full copyright and licensing details.
import logging
import json
import werkzeug.wrappers
from odoo import http
from odoo.http import request


"""Common methods"""
import ast
import logging
import json

from odoo.http import Response
from odoo.tools import date_utils

_logger = logging.getLogger(__name__)

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
                    if isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], int) and isinstance(value[1], str):
                        _int, _str = value
                        _key = key.replace('_id', '').replace('_uid', '')
                        _key_id = '{}_id'.format(_key)
                        item[_key_id] = _int
                        item[_key]    = _str
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
    _limit  = payload.get('limit')
    _order  = payload.get('order')
    if _domain:
        domain_list = parse_list(_domain)
        domain = parse_domain(domain_list)
    if _fields:
        fields += parse_list(_fields)
    if _offset:
        offset = int(_offset)
    if _limit:
        limit  = int(_limit)
    if _order:
        parsed_order = parse_list(_order)
        order  = ','.join(parsed_order) if parsed_order else None
    return [domain, fields, offset, limit, order]


_logger = logging.getLogger(__name__)

expires_in = 'odoo-rest-api-master.access_token_expires_in'

class AccessToken(http.Controller):
    """."""

    @http.route('/api/auth/token', methods=['POST'], type='http', auth='none', csrf=False)
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
            db, username, password = kwargs['db'], kwargs['login'], kwargs['password']
            print(db,username,password,"PASWWORDSS")
        except Exception as e:
            # Invalid database:
            error = 'missing'
            info = 'either of the following are missing [db, username,password]'
            status = 403
            _logger.error(info)
            return invalid_response(error, info, status)

        # Login in odoo database:
        try:
            request.session.authenticate(db, username, password)
        except Exception as e:
            # Invalid database:
            error = 'invalid_database'
            info = "The database name is not valid {}".format((e))
            _logger.error(info)
            return invalid_response(error, info)

        uid = request.session.uid

        print(uid,"UID")

        # odoo login failed:
        if not uid:
            error = 'authentication failed'
            info = 'authentication failed'
            _logger.error(info)
            return invalid_response(error, info)

        # Generate tokens
        access_token = request.env['api.access_token'].sudo().find_one_or_create_token(
            user_id=uid, create=True)
        print(access_token,"AAACC")

        # Successful response:
        return token_response({
            'uid': uid,
            'user_context': request.session.get_context(),
            'company_id': request.env.user.company_id.id,
            'access_token': access_token,
            'expires_in': request.env.ref(expires_in).sudo().value,
        })

    @http.route('/api/auth/token', methods=['DELETE'], type='http', auth='none', csrf=False)
    def delete(self, **kwargs):
        """."""
        request_token = request.httprequest.headers.get('access_token')
        access_token  = request.env['api.access_token'].sudo().search([('token', '=', request_token)])
        if not access_token:
            error = 'no_access_token'
            info = 'No access token was provided in request!'
            _logger.error(info)
            return invalid_response(error, info, 400)

        for token in access_token:
            token.unlink()

        # Successful response:
        return valid_response({
            'desc': 'token successfully deleted',
            'delete': True
        })