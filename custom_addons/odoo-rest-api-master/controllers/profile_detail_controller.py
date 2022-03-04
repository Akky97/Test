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
    @http.route('/api/v1/c/res.partner.view', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def profile_detail_view(self, **params):
        try:
            model = 'res.partner'
            records = request.env[model].sudo().search([('id', '=', 14)])
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        try:
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            temp = []
            for i in records:
                other_addresses = []
                for j in i.child_ids:
                    if j.type == 'invoice' or j.type == 'delivery':
                        other_addresses.append({"id": j.id, "name": j.name, "phone": j.phone if j.phone != False else "",
                                                "mobile": j.mobile if j.mobile != False else "",
                                                "email": j.email if j.email != False else "",
                                                "street": j.street if j.street != False else "",
                                                "street2": j.street2 if j.street2 != False else "",
                                                "city": j.city if j.city != False else "",
                                                "state_id": j.state_id.id if j.state_id.id != False else "",
                                                "state_name": j.state_id.name if j.state_id.name != False else "",
                                                "zip": j.zip if j.zip != False else "",
                                                "country_id": j.country_id.id if j.country_id.id != False else "",
                                                "country_name": j.country_id.name if j.country_id.name != False else "",
                                                "image": base_url.value + '/web/image/res.partner/' + str(j.id) + "/image_1920",
                                                "website": j.website if j.website != False else ""})
                temp.append({"id": i.id, "name": i.name, "phone": i.phone if i.phone != False else "",
                             "mobile": i.mobile if i.mobile != False else "",
                             "email": i.email if i.email != False else "",
                             "street": i.street if i.street != False else "",
                             "street2": i.street2 if i.street2 != False else "",
                             "city": i.city if i.city != False else "",
                             "state_id": i.state_id.id if i.state_id.id != False else "",
                             "state_name": i.state_id.name if i.state_id.name != False else "",
                             "zip": i.zip if i.zip != False else "",
                             "country_id": i.country_id.id if i.country_id.id != False else "",
                             "country_name": i.country_id.name if i.country_id.name != False else "",
                             "image": base_url.value + '/web/image/res.partner/' + str(i.id) + "/image_1920",
                             "website": i.website if i.website != False else "", "other_addresses": other_addresses})
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "result": temp
        }
        return return_Response(res)
