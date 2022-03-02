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
        else:
            limit = ""
        if "offset" in params:
            offset = int(params["offset"])
        else:
            offset = ""
        records = request.env[model].sudo().search([('is_published', '=', True)], order=orders, limit=limit, offset=offset)
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        try:
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            temp = []
            for i in records:
                image = []
                for j in i.product_template_image_ids:
                    image.append({"id": j.id, "name": j.name,
                                  "image": base_url.value + '/web/image/product.image/' + str(j.id) + "/image_1920"})
                temp.append({"id": i.id, "name": i.name,
                             'image': base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920",
                             'type': i.type, 'sales_price': i.list_price, "cost_price": i.standard_price,
                             'description': i.description if i.description != False else '',
                             'description_sale': i.description_sale if i.description_sale != False else '',
                             'categ_id': i.categ_id.id if i.categ_id.id != False else '',
                             'categ_name': i.categ_id.name if i.categ_id.name != False else '',
                             "additional_images": image})
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

    @http.route('/api/v1/c/categ/product.template.view', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def product_template_view_by_categ(self, **params):
        try:
            model = 'product.template'
            categ = params["categ_id"]
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
        else:
            limit = ""
        if "offset" in params:
            offset = int(params["offset"])
        else:
            offset = ""
        records = request.env[model].sudo().search([('is_published', '=', True), ('public_categ_ids', 'in', [int(categ)])], order=orders, limit=limit,
                                                   offset=offset)
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        try:
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            temp = []
            for i in records:
                image = []
                for j in i.product_template_image_ids:
                    image.append({"id": j.id, "name": j.name,
                                  "image": base_url.value + '/web/image/product.image/' + str(j.id) + "/image_1920"})
                web_categ = []
                for z in i.public_categ_ids:
                    web_categ.append({"id": z.id, "name": z.name})
                temp.append({"id": i.id, "name": i.name,
                             'image': base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920",
                             'type': i.type, 'sales_price': i.list_price, "cost_price": i.standard_price,
                             'description': i.description if i.description != False else '',
                             'description_sale': i.description_sale if i.description_sale != False else '',
                             'public_categ_ids': web_categ, "additional_images": image})
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

    @http.route('/api/v1/c/product.category.view', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def product_category_view(self, **params):
        try:
            model = 'product.public.category'
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
        else:
            limit = ""
        if "offset" in params:
            offset = int(params["offset"])
        else:
            offset = ""
        records = request.env[model].sudo().search([], order=orders, limit=limit, offset=offset)
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        try:
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            temp = []
            for i in records:
                search_count = request.env['product.template'].sudo().search_count([('public_categ_ids', 'in', [i.id])])
                temp.append({"id": i.id, "name": i.name,
                             "image": base_url.value + '/web/image/product.public.category/' + str(i.id) + "/image_1920",
                             'parent_id': i.parent_id.id if i.parent_id.id != False else '',
                             'parent_name': i.parent_id.name if i.parent_id.name != False else '',
                             "product_count": search_count})
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
