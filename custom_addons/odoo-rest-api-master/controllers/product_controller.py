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


def _compute_quantities(self):
    res = self._compute_quantities_dict()
    qty_available = res[self.id]['qty_available']
    return res[self.id]['qty_available']


def _product_available(self, name, arg):
    return self._compute_quantities_dict()


def _compute_quantities_dict(self):
    variants_available = self.mapped('product_variant_ids')._product_available()
    prod_available = {}
    for template in self:
        qty_available = 0
        for p in template.product_variant_ids:
            qty_available += variants_available[p.id]["qty_available"]
        prod_available[template.id] = {
            "qty_available": qty_available,
        }
    return prod_available


class OdooAPI(http.Controller):
    @http.route('/api/v1/c/product.template.view', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def product_template_view(self, **params):
        try:
            model = 'product.template'
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        if "query" in params:
            query = params["query"]
        else:
            query = "{*}"
        search = ''
        if "orderBy" in params:
            orders = params["orderBy"]
            if orders == 'rating':
                pass
            elif orders == 'new':
                search = 'create_date DESC'
            elif orders == 'featured':
                search = ''
        limit = 0
        offset = 0
        if "page" in params:
            limit = 12
            page = int(params["page"])
            offset = (page - 1) * 12
        record_count = request.env[model].sudo().search_count([('is_published', '=', True)])
        records = request.env[model].sudo().search([('is_published', '=', True)], order=search, limit=limit, offset=offset)
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        try:
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            temp = []
            for i in records:
                image = []
                category=[]
                variant=[]
                sellers=[]
                for j in i.product_template_image_ids:
                    image.append({"id": j.id, "name": j.name,
                                  "image": base_url.value + '/web/image/product.image/' + str(j.id) + "/image_1920",
                                  'url': base_url.value + '/web/image/product.template/' + str(j.id) + "/image_1920",
                                  })
                for z in i.public_categ_ids:
                    category.append({"id": z.id, "name": z.name,"slug":z.name.lower().replace(" ","-"),
                             "image": base_url.value + '/web/image/product.public.category/' + str(z.id) + "/image_1920",})
                product_var = request.env['product.product'].sudo().search([('product_tmpl_id', '=', int(i.id))])
                for k in product_var:
                    values = []
                    attribute_name = ''
                    id = []
                    data = []
                    for c in k.product_template_attribute_value_ids:
                        id.append(c.attribute_id.id)
                    for attr_id in list(set(id)):
                        for b in k.product_template_attribute_value_ids:
                            if attr_id == b.attribute_id.id:
                                attribute_name = b.attribute_id.name
                                if attribute_name.lower() == 'color':
                                    values.append({"color": b.product_attribute_value_id.name,
                                                   "color_name": b.product_attribute_value_id.html_color})
                                else:
                                    values.append({"id": b.id, "name": b.name, "slug": None,
                                                   "pivot": {"components_variants_variant_id": k.id,
                                                             "component_id": b.id}})
                        data.append({attribute_name: values})
                        values = []
                    res_data = {"id": k.id, "price": k.list_price,
                                "pivot": {"product_id": i.id, "component_id": k.id}}

                    if len(data) != 0:
                        for dic in data:
                            res = list(dic.items())[0]

                            # if len
                            if res[0].lower() == 'color':
                                res_data.update(
                                    {"color": res[1][0].get('color'), "color_name": res[1][0].get('color_name')})
                            else:
                                res_data.update(dic)


                        variant.append(res_data)
                    else:
                        pass

                for n in i.seller_ids:
                    sellers.append({"id": n.id, "vendor": n.name.name,"vendor_id": n.name.id})
                data = _compute_quantities(self=i)

                temp.append({"id": i.id, "name": i.name,
                             'url': base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920",
                             'image': base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920",
                             'type': i.type, 'sale_price': i.list_price, "price": i.standard_price,
                             'description': i.description if i.description != False else '',
                             'short_desc': i.description_sale if i.description_sale != False else '',
                             'categ_id': i.categ_id.id if i.categ_id.id != False else '',
                             'categ_name': i.categ_id.name if i.categ_id.name != False else '',
                             "category":category,
                             "create_uid":i.create_uid.id if i.create_uid.id != False else '',
                             "create_name":i.create_uid.name if i.create_uid.name != False else '',
                             "write_uid":i.write_uid.id if i.write_uid.id != False else '',
                             "write_name":i.write_uid.name if i.write_uid.name != False else '',
                             "variants":variant,
                             "stock":data,
                             "sm_pictures": image,
                             "featured":i.website_ribbon_id.html if i.website_ribbon_id.html != False else '',
                             "seller_ids":sellers,
                             "slug":i.id,
                             "top": True if i.website_ribbon_id.html == 'Trending' else None,
                             "new": True if i.website_ribbon_id.html == 'New' else None,
                             "author":"Pando-Stores",
                             "sold":10,
                             "review":2,
                             "rating":3,
                             "additional_info": i.additional_info,
                             "shipping_return": i.shipping_return,
                             "pictures": [{'url': base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920","image": base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920"}]
                             })
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "total_count": record_count,
            "count": len(temp),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "products": temp
        }

        return return_Response(res)

    @http.route('/api/v1/c/product.template.view/<product_id>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def product_template_view_single(self, product_id=None, **params):
        model = 'product.template'
        try:
            if not product_id:
                error = {"message": "product_id is not present in the request", "status": 400}
                return return_Response_error(error)
            records = request.env[model].sudo().search([('id', '=', int(product_id))])
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        try:
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            temp = []
            for i in records:
                image = []
                category = []
                variant = []
                sellers = []
                for j in i.product_template_image_ids:
                    image.append({"id": j.id, "name": j.name,
                                  'url': base_url.value + '/web/image/product.template/' + str(j.id) + "/image_1920",
                                  "image": base_url.value + '/web/image/product.image/' + str(j.id) + "/image_1920"})
                for z in i.public_categ_ids:
                    category.append({"id": z.id, "name": z.name, "slug": z.name.lower().replace(" ", "-"),
                                     "image": base_url.value + '/web/image/product.public.category/' + str(
                                         z.id) + "/image_1920", })
                product_var = request.env['product.product'].sudo().search([('product_tmpl_id', '=', int(i.id))])
                for k in product_var:
                    values = []
                    attribute_name = ''
                    id = []
                    data = []
                    for c in k.product_template_attribute_value_ids:
                        id.append(c.attribute_id.id)
                    for attr_id in list(set(id)):
                        for b in k.product_template_attribute_value_ids:
                            if attr_id == b.attribute_id.id:
                                attribute_name = b.attribute_id.name
                                if attribute_name.lower() == 'color':
                                    values.append({"color": b.product_attribute_value_id.name,
                                                   "color_name": b.product_attribute_value_id.html_color})
                                else:
                                    values.append({"id": b.id, "name": b.name, "slug": None,
                                                   "pivot": {"components_variants_variant_id": k.id, "component_id": b.id}})
                        data.append({attribute_name: values})
                        values = []
                    res_data = {"id": k.id, "price": k.list_price,
                                "pivot": {"product_id": i.id, "component_id": k.id}}

                    if len(data) != 0:
                        for dic in data:
                            res = list(dic.items())[0]

                            # if len
                            if res[0].lower() == 'color':
                                res_data.update(
                                    {"color": res[1][0].get('color'), "color_name": res[1][0].get('color_name')})
                            else:
                                res_data.update(dic)


                        variant.append(res_data)
                    else:
                        pass

                for n in i.seller_ids:
                    sellers.append({"id": n.id, "vendor": n.name.name, "vendor_id": n.name.id})
                data = _compute_quantities(self=i)
                temp.append({"id": i.id, "name": i.name,
                             'url': base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920",
                             'image': base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920",
                             'type': i.type, 'sale_price': i.list_price, "price": i.standard_price,
                             'description': i.description if i.description != False else '',
                             'short_desc': i.description_sale if i.description_sale != False else '',
                             'categ_id': i.categ_id.id if i.categ_id.id != False else '',
                             'categ_name': i.categ_id.name if i.categ_id.name != False else '',
                             "category": category,
                             "create_uid": i.create_uid.id if i.create_uid.id != False else '',
                             "create_name": i.create_uid.name if i.create_uid.name != False else '',
                             "write_uid": i.write_uid.id if i.write_uid.id != False else '',
                             "write_name": i.write_uid.name if i.write_uid.name != False else '',
                             "variants": variant,
                             "stock": data,
                             "sm_pictures": image,
                             "featured": i.website_ribbon_id.html if i.website_ribbon_id.html != False else '',
                             "seller_ids": sellers,
                             "slug": i.id,
                             "top": True if i.website_ribbon_id.html == 'Trending' else None,
                             "new": True if i.website_ribbon_id.html == 'New' else None,
                             "author": "Pando-Stores",
                             "sold": 10,
                             "review": 2,
                             "rating": 3,
                             "additional_info": i.additional_info,
                             "shipping_return": i.shipping_return,
                             "pictures": [{ 'url': base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920","image": base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920"}]
                             })
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "products": temp
        }
        return return_Response(res)

    @http.route('/api/v1/c/categ/product.template.view', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def product_template_view_by_categ(self, **params):
        try:
            model = 'product.template'
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)

        search = ''
        if "orderBy" in params:
            orders = params["orderBy"]
            if orders == 'rating':
                pass
            elif orders == 'new':
                search = 'create_date DESC'
            elif orders == 'featured':
                search = ''
        limit = 0
        offset = 0
        if "page" in params:
            limit = 12
            page = int(params["page"])
            offset = (page - 1) * 12
        if "search" in params:
            search_data = params["search"]
            record_count = request.env[model].sudo().search_count([('is_published', '=', True), ('name', 'ilike', search_data)])
            records = request.env[model].sudo().search(
                [('is_published', '=', True), ('name', 'ilike', search_data)], order=search, limit=limit,
                offset=offset)
        elif "category" not in params:
            record_count = request.env[model].sudo().search_count([('is_published', '=', True)])
            records = request.env[model].sudo().search(
                [('is_published', '=', True)], order=search, limit=limit,
                offset=offset)
        else:
            record_count = request.env[model].sudo().search_count(
                [('is_published', '=', True), ('public_categ_ids', 'in', [int(params["category"])])])
            records = request.env[model].sudo().search([('is_published', '=', True), ('public_categ_ids', 'in', [int(params["category"])])], order=search, limit=limit,
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
                category = []
                variant = []
                sellers = []
                for j in i.product_template_image_ids:
                    image.append({"id": j.id, "name": j.name,
                                  "image": base_url.value + '/web/image/product.image/' + str(j.id) + "/image_1920",
                                  'url': base_url.value + '/web/image/product.template/' + str(j.id) + "/image_1920",
                                  })
                for z in i.public_categ_ids:
                    category.append({"id": z.id, "name": z.name, "slug": z.name.lower().replace(" ", "-"),
                                     "image": base_url.value + '/web/image/product.public.category/' + str(
                                         z.id) + "/image_1920", })
                product_var = request.env['product.product'].sudo().search([('product_tmpl_id', '=', int(i.id))])
                for k in product_var:
                    values = []
                    attribute_name = ''
                    id = []
                    data = []
                    for c in k.product_template_attribute_value_ids:
                        id.append(c.attribute_id.id)
                    for attr_id in list(set(id)):
                        for b in k.product_template_attribute_value_ids:
                            if attr_id == b.attribute_id.id:
                                attribute_name = b.attribute_id.name
                                if attribute_name.lower() == 'color':
                                    values.append({"color": b.product_attribute_value_id.name,
                                                   "color_name": b.product_attribute_value_id.html_color})
                                else:
                                    values.append({"id": b.id, "name": b.name, "slug": None,
                                                   "pivot": {"components_variants_variant_id": k.id,
                                                             "component_id": b.id}})
                        data.append({attribute_name: values})
                        values = []
                    res_data = {"id": k.id, "price": k.list_price,
                                "pivot": {"product_id": i.id, "component_id": k.id}}
                    if len(data) != 0:
                        for dic in data:
                            res = list(dic.items())[0]
                            # if len
                            if res[0].lower() == 'color':
                                res_data.update(
                                    {"color": res[1][0].get('color'), "color_name": res[1][0].get('color_name')})
                            else:
                                res_data.update(dic)

                        variant.append(res_data)
                    else:
                        pass

                for n in i.seller_ids:
                    sellers.append({"id": n.id, "vendor": n.name.name, "vendor_id": n.name.id})
                data = _compute_quantities(self=i)
                temp.append({"id": i.id, "name": i.name,
                             'image': base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920",
                             'url': base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920",
                             'type': i.type, 'sale_price': i.list_price, "price": i.standard_price,
                             'description': i.description if i.description != False else '',
                             'short_desc': i.description_sale if i.description_sale != False else '',
                             'categ_id': i.categ_id.id if i.categ_id.id != False else '',
                             'categ_name': i.categ_id.name if i.categ_id.name != False else '',
                             "category": category,
                             "create_uid": i.create_uid.id if i.create_uid.id != False else '',
                             "create_name": i.create_uid.name if i.create_uid.name != False else '',
                             "write_uid": i.write_uid.id if i.write_uid.id != False else '',
                             "write_name": i.write_uid.name if i.write_uid.name != False else '',
                             "variants": variant,
                             "stock": data,
                             "sm_pictures": image,
                             "featured": i.website_ribbon_id.html if i.website_ribbon_id.html != False else '',
                             "seller_ids": sellers,
                             "slug": i.id,
                             "top": True if i.website_ribbon_id.html == 'Trending' else None,
                             "new": True if i.website_ribbon_id.html == 'New' else None,
                             "author": "Pando-Stores",
                             "sold": 10,
                             "review": 2,
                             "rating": 3,
                             "additional_info": i.additional_info,
                             "shipping_return": i.shipping_return,
                             "pictures":[{"image":base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920", 'url': base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920",}]
                             })
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)

        res = {
            "total_count": record_count,
            "count": len(temp),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "products": temp
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
            "products": temp
        }
        return return_Response(res)

    @http.route('/api/v1/c/product.template.search', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def product_template_search(self, **params):
        try:
            domain = []
            if 'search' in params and 'categ_id' in params:
                domain = ['&', ('is_published', '=', True), '|', ('name', 'ilike', params['search']),
                          ('public_categ_ids', 'in', [int(params['categ_id'])])]
            if 'search' in params and 'categ_id' not in params:
                domain = [('is_published', '=', True), ('name', 'ilike', params['search'])]
            if 'search' not in params and 'categ_id' in params:
                domain = [('is_published', '=', True), ('public_categ_ids', 'in', [int(params['categ_id'])])]
            model = 'product.template'
            record = request.env[model].sudo().search(domain)
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            temp = []
            for i in record:
                    image = []
                    category = []
                    variant = []
                    sellers = []
                    for j in i.product_template_image_ids:
                        image.append({"id": j.id, "name": j.name,
                                      "image": base_url.value + '/web/image/product.image/' + str(j.id) + "/image_1920",
                                      'url': base_url.value + '/web/image/product.template/' + str(
                                          j.id) + "/image_1920",
                                      })
                    for z in i.public_categ_ids:
                        category.append({"id": z.id, "name": z.name, "slug": z.name.lower().replace(" ", "-"),
                                         "image": base_url.value + '/web/image/product.public.category/' + str(
                                             z.id) + "/image_1920", })
                    product_var = request.env['product.product'].sudo().search([('product_tmpl_id', '=', int(i.id))])
                    for k in product_var:
                        values = []
                        attribute_name = ''
                        id = []
                        data = []
                        for c in k.product_template_attribute_value_ids:
                            id.append(c.attribute_id.id)
                        for attr_id in list(set(id)):
                            for b in k.product_template_attribute_value_ids:
                                if attr_id == b.attribute_id.id:
                                    attribute_name = b.attribute_id.name
                                    if attribute_name.lower() == 'color':
                                        values.append({"color": b.product_attribute_value_id.name,
                                                       "color_name": b.product_attribute_value_id.html_color})
                                    else:
                                        values.append({"id": b.id, "name": b.name, "slug": None,
                                                       "pivot": {"components_variants_variant_id": k.id,
                                                                 "component_id": b.id}})
                            data.append({attribute_name: values})
                            values = []
                        res_data = {"id": k.id, "price": k.list_price,
                                    "pivot": {"product_id": i.id, "component_id": k.id}}

                        if len(data) != 0:
                            for dic in data:
                                res = list(dic.items())[0]

                                # if len
                                if res[0].lower() == 'color':
                                    res_data.update(
                                        {"color": res[1][0].get('color'), "color_name": res[1][0].get('color_name')})
                                else:
                                    res_data.update(dic)

                            variant.append(res_data)
                        else:
                            pass

                    for n in i.seller_ids:
                        sellers.append({"id": n.id, "vendor": n.name.name, "vendor_id": n.name.id})
                    data = _compute_quantities(self=i)

                    temp.append({"id": i.id, "name": i.name,
                                 'url': base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920",
                                 'image': base_url.value + '/web/image/product.template/' + str(i.id) + "/image_1920",
                                 'type': i.type, 'sale_price': i.list_price, "price": i.standard_price,
                                 'description': i.description if i.description != False else '',
                                 'short_desc': i.description_sale if i.description_sale != False else '',
                                 'categ_id': i.categ_id.id if i.categ_id.id != False else '',
                                 'categ_name': i.categ_id.name if i.categ_id.name != False else '',
                                 "category": category,
                                 "create_uid": i.create_uid.id if i.create_uid.id != False else '',
                                 "create_name": i.create_uid.name if i.create_uid.name != False else '',
                                 "write_uid": i.write_uid.id if i.write_uid.id != False else '',
                                 "write_name": i.write_uid.name if i.write_uid.name != False else '',
                                 "variants": variant,
                                 "stock": data,
                                 "sm_pictures": image,
                                 "featured": i.website_ribbon_id.html if i.website_ribbon_id.html != False else '',
                                 "seller_ids": sellers,
                                 "slug": i.id,
                                 "top": True if i.website_ribbon_id.html == 'Trending' else None,
                                 "new": True if i.website_ribbon_id.html == 'New' else None,
                                 "author": "Pando-Stores",
                                 "sold": 10,
                                 "review": 2,
                                 "rating": 3,
                                 "additional_info": i.additional_info,
                                 "shipping_return": i.shipping_return,
                                 "pictures": [{'url': base_url.value + '/web/image/product.template/' + str(
                                     i.id) + "/image_1920",
                                               "image": base_url.value + '/web/image/product.template/' + str(
                                                   i.id) + "/image_1920"}]
                                 })

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "products": temp
        }
        return return_Response(res)

