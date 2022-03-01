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
    @http.route('/api/v1/c/product.template.view', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def product_template_view(self, **params):
        try:
            model = 'product.template'
            records = request.env[model].sudo().search([])
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        if "query" in params:
            query = params["query"]
        else:
            query = "{*}"
        if "order" in params:
            orders = params["order"]
        else:
            orders = ""
        if "limit" in params:
            limit = int(params["limit"])
        if "offset" in params:
            offset = int(params["offset"])
        if "filter" in params:
            filters = params["filter"]
            records = request.env[model].search(ast.literal_eval(filters), order=orders, limit=limit, offset=offset)

        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "page_size" in params:
            page_size = int(params["page_size"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)
            if "page" in params:
                current_page = int(params["page"])
            else:
                current_page = 1  # Default page Number
            start = page_size * (current_page - 1)
            stop = current_page * page_size
            records = records[start:stop]
            next_page = current_page + 1 \
                if 0 < current_page + 1 <= total_page_number \
                else None
            prev_page = current_page - 1 \
                if 0 < current_page - 1 <= total_page_number \
                else None
        try:
            base_url = request.env['ir.config_parameter'].search([('key', '=', 'web.base.url')], limit=1)
            temp = []
            for i in records:
                temp.append({"id": i.id, "name": i.name,
                             'image': base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920",
                             'type': i.type, 'sales_price': i.list_price, "cost_price": i.standard_price,
                             'description': i.description if i.description != False else '',
                             'description_sale': i.description_sale if i.description_sale != False else '',
                             'categ_id': i.categ_id.id if i.categ_id.id != False else '',
                             'categ_name': i.categ_id.name if i.categ_id.name != False else ''})
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "result": temp
        }
        return return_Response(res)

