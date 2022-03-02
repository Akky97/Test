import json
import math
import logging
import requests
import ast
from odoo import http, _, exceptions
from odoo.http import request
from .serializers import Serializer
from .exceptions import QueryFormatError
from .error_or_response_parser import *

_logger = logging.getLogger(__name__)


class OdooAPI(http.Controller):
    @http.route('/api/v1/c/res.company.view', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def product_template_view(self, **params):
        try:
            model = 'res.company'
            records = request.env[model].sudo().search([('name', '=', 'Pando Mall')])
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        try:
            temp = []
            for i in records:
                temp.append({"id": i.id, "name": i.name, "phone": i.phone, "email": i.email,
                             "address": i.street
                             + ", " + i.city + ", " + i.state_id.name
                             + ", " + i.zip + ", " + i.country_id.name,
                             "website": i.website, "currency_id": i.currency_id.id if i.currency_id.id != False else '',
                             "currency_name": i.currency_id.name if i.currency_id.name != False else ''})
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "result": temp
        }
        return return_Response(res)
