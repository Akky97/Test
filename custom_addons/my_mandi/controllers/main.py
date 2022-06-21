"""Part of odoo. See LICENSE file for full copyright and licensing details."""

import functools
import logging
import dateutil.parser
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


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

def validate_token(func):
    """."""
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        access_token = request.httprequest.headers.get('access_token')
        if not access_token:
            return invalid_response('access_token_not_found', 'missing access token in request header', 401)
        access_token_data = request.env['api.access_token'].sudo().search(
            [('token', '=', access_token)], order='id DESC', limit=1)

        if access_token_data.find_one_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_response('access_token', 'token seems to have expired or invalid', 401)

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)
    return wrap

def validate_id(func):
    """."""
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        id = kwargs['id']
        try:
            kwargs['id'] = int(id)
        except Exception as e:
            return invalid_response('invalid object id', 'invalid id %s' % id)
        else:
            return func(self, *args, **kwargs)
    return wrap

def validate_model(func):
    """."""
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        model = kwargs['model']
        _model = request.env['ir.model'].sudo().search(
            [('model', '=', model)], limit=1)
        if not _model:
            return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model, 404)
        return func(self, *args, **kwargs)
    return wrap

def parse_data(func):
    """."""
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        result = {}
        for key, value in kwargs.items():
            converted_value = value
            if isinstance(value, str):
                if value in ['true', 'True']:
                    converted_value = True
                elif value in ['false', 'False']:
                    converted_value = False
                else:
                    try:
                        converted_value = int(value)
                    except Exception:
                        try:
                            converted_value = dateutil.parser.parse(value)
                        except Exception:
                            pass
            result[key] = converted_value
        return func(self, *args, **result)
    return wrap

class APIController(http.Controller):
    """."""

    @validate_token
    @validate_id
    @validate_model
    @http.route('/api/<model>/<id>', type='http', auth="none", methods=['GET'], csrf=False)
    def get(self, model=None, id=None):
        """Get record by id.
        Basic usage:
        import requests

        headers = {
            'charset': 'utf-8',
            'access-token': 'access_token'
        }
        model = 'res.partner'
        id = 100
        req = requests.get('{}/api/{}/{}'.format(base_url, model, id), headers=headers)
        print(req.json())
        """
        try:
            record = request.env[model].sudo().browse(id)
            if record.read():
                return valid_response(prepare_response(record.read(), one=True))
            else:
                return invalid_response('missing_record',
                                        'record object with id %s could not be found' % (id, model), 404)
        except Exception as e:
            return invalid_response('exception', str(e))

    @validate_token
    @validate_model
    @http.route('/api/<model>', type='http', auth="none", methods=['GET'], csrf=False)
    def search(self, model=None, **kwargs):
        """Get records by search query.
        Basic usage:
        import requests

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8',
            'access-token': 'access_token'
        }
        model = 'res.partner'
        data = {
            'domain': "[('supplier','=',True),('parent_id','=', False)]",
            'order': 'name asc',
            'limit': 10,
            'offset': 0,
            'fields': "['name', 'supplier', 'parent_id']"
        }
        ###
        #You can ommit unnessesary query params
        #data = {
        #    'domain': "[('supplier','=',True),('parent_id','=', False)]",
        #    'limit': 10
        #}
        ###
        #You can also use JSON-like domains
        #data = {
        #    'domain': "{'id':100, 'parent_id!':true}",
        #    'limit': 10
        #}
        req = requests.get('{}/api/{}/'.format(base_url, model), headers=headers, params=data)
        print(req.json())
        """
        domain, fields, offset, limit, order = extract_arguments(kwargs)
        data = request.env[model].sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        return valid_response(prepare_response(data))

    @validate_token
    @validate_model
    @parse_data
    @http.route('/api/<model>', type='http', auth="none", methods=['POST'], csrf=False)
    def create(self, model=None, **kwargs):
        """Create a new record.
        Basic usage:
        import requests

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8',
            'access-token': 'access_token'
        }
        model = 'res.partner'
        data = {
            'name': 'Babatope Ajepe',
            'country_id': 105,
            'child_ids': [
                {
                    'name': 'Contact',
                    'type': 'contact'
                },
                {
                    'name': 'Invoice',
                    'type': 'invoice'
                }
            ],
            'category_id': [{'id': 9}, {'id': 10}]
        }
        req = requests.post('{}/api/{}/'.format(base_url, model), headers=headers, data=data)
        print(req.json())
        """

        try:
            record = request.env[model].sudo().create(kwargs)
            record.refresh()
            return valid_response(prepare_response(record.read(), one=True))
        except Exception as e:
            return invalid_response('params', e)


    @validate_token
    @validate_id
    @validate_model
    @parse_data
    @http.route('/api/<model>/<id>', type='http', auth="none", methods=['PUT'], csrf=False)
    def put(self, model=None, id=None, **kwargs):
        """Update existing record.
        Basic usage:
        import requests

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8',
            'access-token': 'access_token'
        }
        model = 'res.partner'
        id = 100
        data = {
            'name': 'Babatope Ajepe',
            'country_id': 103,
            'category_id': [{'id': 9}]
        }
        req = requests.put('{}/api/{}/{}'.format(base_url, model, id), headers=headers, data=data)
        print(req.json())
        """
        try:
            record = request.env[model].sudo().browse(id)
            if record.read():
                result = record.write(kwargs)
                record.refresh()
                return valid_response(prepare_response(record.read(), one=True))
            else:
                return invalid_response('missing_record', 'record object with id %s could not be found' % id, 404)
        except Exception as e:
            return invalid_response('exception', str(e))

    @validate_token
    @validate_id
    @validate_model
    @parse_data
    @http.route('/api/<model>/<id>/<action>', type='http', auth="none", methods=['PATCH'], csrf=False)
    def patch(self, model=None, id=None, action=None, **kwargs):
        """Call action for model.
        Basic usage:
        import requests

        headers = {
            'charset': 'utf-8',
            'access-token': 'access_token'
        }
        model = 'res.partner'
        id = 100
        action = 'delete'
        req = requests.patch('{}/api/res.{}/{}'.format(base_url, model, id, action), headers=headers)
        print(req.content)
        """

        try:
            record = request.env[model].sudo().browse(id)
            if record.read():
                _callable = action in [method for method in dir(
                    record) if callable(getattr(record, method))]
                if _callable:
                    # action is a dynamic variable.
                    getattr(record, action)()
                record.refresh()
                return valid_response(prepare_response(record.read(), one=True))
            else:
                return invalid_response('missing_record',
                                        'record object with id %s could not be found or %s object has no method %s' % (id, model, action), 404)
        except Exception as e:
            return invalid_response('exception', e, 503)

    @validate_token
    @validate_id
    @validate_model
    @http.route('/api/<model>/<id>', type='http', auth="none", methods=['DELETE'], csrf=False)
    def delete(self, model=None, id=None):
        """Delete existing record.
        Basic usage:
        import requests

        headers = {
            'charset': 'utf-8',
            'access-token': 'access_token'
        }
        model = 'res.partner'
        id = 100
        req = requests.delete('{}/api/{}/{}'.format(base_url, model, id), headers=headers)
        print(req.json())
        """

        try:
            record = request.env[model].sudo().browse(id)
            if record.read():
                record.unlink()
                return valid_response(None, status=204)
            else:
                return invalid_response('missing_record', 'record object with id %s could not be found' % id, 404)
        except Exception as e:
            return invalid_response('exception', str(e), 503)
