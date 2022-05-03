import logging
import odoo
from odoo import http, _, exceptions, fields, registry, SUPERUSER_ID, api
from datetime import timedelta, time
from odoo.tools.float_utils import float_round
from odoo.http import request
from .exceptions import QueryFormatError
from .error_or_response_parser import *
import psycopg2

_logger = logging.getLogger(__name__)


def _compute_sales_count(self):
    count =0
    date_from = fields.Datetime.to_string(fields.datetime.combine(fields.datetime.now() - timedelta(days=365),
                                                                  time.min))
    res = request.env['sale.report'].sudo().search([('product_id','=',self.id),('date', '>=', date_from),('state', 'in', ['sale','done','paid'])])
    if res:
        for r in res:
            count += r.product_uom_qty
    return count

def get_rating_permission(product):
    result = request.env['sale.order.line'].sudo().search([('product_id', '=', product.id), ('order_id.partner_id', '=', request.env.user.partner_id.id)])
    if result:
        return True
    else:
        return False

def get_product_details(warehouse, records):
    base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
    temp = []
    for i in records:
        image = []
        category = []
        variant = []
        sellers = []
        try:
            db_name = odoo.tools.config.get('db_name')
            db_registry = registry(db_name)
            with db_registry.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                prod = env['product.product'].sudo().browse([i.id])
                prod.sudo().write({'sale_count_pando': _compute_sales_count(self=prod)})
            cr.commit()
            cr.close()
        except psycopg2.Error:
            pass
        result = request.env['pando.images'].sudo().search([('product_id', '=', i.id)])
        if not result:
            result = request.env['pando.images'].sudo().search([('product_id.product_tmpl_id', '=', i.product_tmpl_id.id)])
        base_image = {}
        for j in result:
            if j.type == 'multi_image':
                image.append({"id": j.product_id.id,
                              "image": j.image_url,
                              "url": j.image_url,
                              'name': j.image_name,
                              })
            else:
                base_image = {
                    "id": j.product_id.id,
                    "image_url": j.image_url,
                    'image_name': j.image_name
                }
        for z in i.public_categ_ids:
            category.append({"id": z.id, "name": z.name, "slug": z.name.lower().replace(" ", "-"),
                             "image": base_url.value + '/web/image/product.public.category/' + str(
                                 z.id) + "/image_1920", })
        # product attribute_data created here
        values = []
        attribute_name = ''
        id = []
        data = []
        for c in i.product_template_attribute_value_ids:
            id.append(c.attribute_id.id)
        variant_name = ''
        for attr_id in list(set(id)):
            for b in i.product_template_attribute_value_ids:
                if attr_id == b.attribute_id.id:
                    attribute_name = b.attribute_id.name
                    if attribute_name.lower() == 'color':
                        values.append({"color": b.product_attribute_value_id.name,
                                       "color_name": b.product_attribute_value_id.html_color})
                    else:
                        values.append({"id": b.id, "name": b.name, "slug": None,
                                       "pivot": {"components_variants_variant_id": i.id,
                                                 "component_id": b.id}})
                    variant_name += '('+b.name + ')'

            data.append({attribute_name: values})
            values = []
        res_data = {"id": i.id, "price": i.list_price,
                    "pivot": {"product_id": i.id, "component_id": i.id}}

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

        # End here


        for n in i.seller_ids:
            sellers.append({"id": n.id, "vendor": n.name.name, "vendor_id": n.name.id})

        temp.append({"id": i.id, "name": i.name+variant_name,
                     'url': base_image.get('image_url') if 'image_url' in base_image else "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/330px-No-Image-Placeholder.svg.png?20200912122019" ,
                     'image': base_image.get('image_url') if 'image_url' in base_image else "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/330px-No-Image-Placeholder.svg.png?20200912122019" ,
                     'image_name': base_image.get('image_name') if 'image_name' in base_image else '',
                     'type': i.type, 'sale_price': i.list_price, "price": i.standard_price,
                     'description': i.description if i.description != False else '',
                     'short_desc': i.description_sale if i.description_sale != False else '',
                     'categ_id': i.categ_id.id if i.categ_id.id != False else '',
                     'categ_name': i.categ_id.name if i.categ_id.name != False else '',
                     "category": category,
                     "create_uid": i.create_uid.id if i.create_uid.id != False else '',
                     "create_name": i.create_uid.name if i.create_uid.name != False else '',
                     # "write_uid": i.write_uid.id if i.write_uid.id != False else '',
                     # "write_name": i.write_uid.name if i.write_uid.name != False else '',
                     "variants": variant,
                     "stock": i.with_context(warehouse=warehouse.id).virtual_available if i.with_context(
                         warehouse=warehouse.id).virtual_available > 0 else 0.0,
                     "sm_pictures": image,
                     "featured": i.website_ribbon_id.html if i.website_ribbon_id.html != False else '',
                     "seller_ids": sellers,
                     "slug": i.id,
                     "top": True if i.website_ribbon_id.html == 'Trending' else None,
                     "new": True if i.website_ribbon_id.html == 'New' else None,
                     "author": "Pando-Stores",
                     "sold": i.sale_count_pando,
                     "review": 2,
                     "rating": 3,
                     "rating_permission": get_rating_permission(i),
                     "marketplace_seller_id": i.marketplace_seller_id.id,
                     "marketplace_seller_name": i.marketplace_seller_id.name,
                     "additional_info": i.additional_info if i.additional_info else '',
                     "shipping_return": i.shipping_return if i.shipping_return else '',
                     "pictures": [
                         {
                            'url': base_image.get('image_url') if 'image_url' in base_image else "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/330px-No-Image-Placeholder.svg.png?20200912122019" ,
                            'image': base_image.get('image_url') if 'image_url' in base_image else "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/330px-No-Image-Placeholder.svg.png?20200912122019" }]
                     })
    return temp



class OdooAPI(http.Controller):
    @http.route('/api/v1/c/product.template.view', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def product_template_view(self, **params):
        try:
            domain = [('is_product_publish', '=', True), ('is_published', '=', True), ('type', '=', 'product'), ('marketplace_status', 'in', ['approved'])]
            model = 'product.product'
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)

        if "country_id" in params and params.get('country_id'):
            domain.append(('country_id', '=', int(params.get('country_id'))))

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
                search = 'sale_count_pando DESC'
            elif orders == 'sale':
                search = 'sale_count_pando DESC'
                domain.append(('website_ribbon_id.html', '=', 'Sale'))
        limit = 0
        offset = 0
        if "page" in params:
            limit = 12
            page = int(params["page"])
            offset = (page - 1) * 12
        record_count = request.env[model].sudo().search_count(domain)
        records = request.env[model].sudo().search(domain, order=search, limit=limit, offset=offset)
        if ("orderBy" in params and params['orderBy'] == 'featured') or ("orderBy" in params and params['orderBy'] == 'sale'):
            for res in records:
                try:
                    db_name = odoo.tools.config.get('db_name')
                    db_registry = registry(db_name)
                    with db_registry.cursor() as cr:
                        env = api.Environment(cr, SUPERUSER_ID, {})
                        prod = env['product.product'].sudo().browse([res.id])
                        prod.sudo().write({'sale_count_pando': _compute_sales_count(self=prod)})
                    cr.commit()
                    cr.close()
                except psycopg2.Error:
                    pass

            records = request.env[model].sudo().search(domain, order=search, limit=limit, offset=offset)
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1
        website = request.env['website'].sudo().browse(1)
        try:
            warehouse = request.env['stock.warehouse'].sudo().search(
                [('company_id', '=', website.company_id.id)], limit=1)
            temp = get_product_details(warehouse,records)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "total_count": record_count,
            "count": len(temp),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "products": temp,
            'symbol': website.company_id.currency_id.symbol if website.company_id.currency_id.symbol != False else ""
        }

        return return_Response(res)

    @http.route('/api/v1/c/product.template.view/<product_id>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def product_template_view_single(self, product_id=None, **params):
        model = 'product.product'
        try:
            if not product_id:
                error = {"message": "Product id is not present in the request", "status": 400}
                return return_Response_error(error)
            records = request.env[model].sudo().search([('id', '=', int(product_id))])
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1
        website = request.env['website'].sudo().browse(1)
        try:
            warehouse = request.env['stock.warehouse'].sudo().search(
                [('company_id', '=', website.company_id.id)], limit=1)
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            temp = []
            temp = get_product_details(warehouse, records)
            # for i in records:
            #     image = []
            #     category = []
            #     variant = []
            #     sellers = []
            #     _compute_sales_count(self=i)
            #     i.sale_count_pando = i.sales_count
            #     for j in i.product_template_image_ids:
            #         image.append({"id": j.id, "name": j.name,
            #                       "image": base_url.value + '/web/image/product.image/' + str(j.id) + "/image_1920",
            #                       'url': base_url.value + '/web/image/product.image/' + str(j.id) + "/image_1920",
            #                       })
            #     for z in i.public_categ_ids:
            #         category.append({"id": z.id, "name": z.name, "slug": z.name.lower().replace(" ", "-"),
            #                          "image": base_url.value + '/web/image/product.public.category/' + str(
            #                              z.id) + "/image_1920", })
            #     product_var = request.env['product.product'].sudo().search([('id', '=', int(i.id))])
            #     for k in product_var:
            #         values = []
            #         attribute_name = ''
            #         id = []
            #         data = []
            #         for c in k.product_template_attribute_value_ids:
            #             id.append(c.attribute_id.id)
            #         for attr_id in list(set(id)):
            #             for b in k.product_template_attribute_value_ids:
            #                 if attr_id == b.attribute_id.id:
            #                     attribute_name = b.attribute_id.name
            #                     if attribute_name.lower() == 'color':
            #                         values.append({"color": b.product_attribute_value_id.name,
            #                                        "color_name": b.product_attribute_value_id.html_color})
            #                     else:
            #                         values.append({"id": b.id, "name": b.name, "slug": None,
            #                                        "pivot": {"components_variants_variant_id": k.id,
            #                                                  "component_id": b.id}})
            #             data.append({attribute_name: values})
            #             values = []
            #         res_data = {"id": k.id, "price": k.list_price,
            #                     "pivot": {"product_id": i.id, "component_id": k.id}}
            #
            #         if len(data) != 0:
            #             for dic in data:
            #                 res = list(dic.items())[0]
            #
            #                 # if len
            #                 if res[0].lower() == 'color':
            #                     res_data.update(
            #                         {"color": res[1][0].get('color'), "color_name": res[1][0].get('color_name')})
            #                 else:
            #                     res_data.update(dic)
            #
            #             variant.append(res_data)
            #         else:
            #             pass
            #
            #     for n in i.seller_ids:
            #         sellers.append({"id": n.id, "vendor": n.name.name, "vendor_id": n.name.id})
            #
            #     temp.append({"id": i.id, "name": i.name,
            #                  'url': base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920",
            #                  'image': base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920",
            #                  'type': i.type, 'sale_price': i.list_price, "price": i.standard_price,
            #                  'description': i.description if i.description != False else '',
            #                  'short_desc': i.description_sale if i.description_sale != False else '',
            #                  'categ_id': i.categ_id.id if i.categ_id.id != False else '',
            #                  'categ_name': i.categ_id.name if i.categ_id.name != False else '',
            #                  "category": category,
            #                  "create_uid": i.create_uid.id if i.create_uid.id != False else '',
            #                  "create_name": i.create_uid.name if i.create_uid.name != False else '',
            #                  "write_uid": i.write_uid.id if i.write_uid.id != False else '',
            #                  "write_name": i.write_uid.name if i.write_uid.name != False else '',
            #                  "variants": variant,
            #                  # "stock": i.qty_available,
            #                  "stock": i.with_context(warehouse=warehouse.id).virtual_available if i.with_context(warehouse=warehouse.id).virtual_available>0 else 0.0,
            #                  "sm_pictures": image,
            #                  "featured": i.website_ribbon_id.html if i.website_ribbon_id.html != False else '',
            #                  "seller_ids": sellers,
            #                  "slug": i.id,
            #                  "top": True if i.website_ribbon_id.html == 'Trending' else None,
            #                  "new": True if i.website_ribbon_id.html == 'New' else None,
            #                  "author": "Pando-Stores",
            #                  "sold": i.sales_count,
            #                  "review": 2,
            #                  "rating": 3,
            #                  "marketplace_seller_id": i.marketplace_seller_id.id,
            #                  "marketplace_seller_name": i.marketplace_seller_id.name,
            #                  "additional_info": i.additional_info if i.additional_info else '',
            #                  "shipping_return": i.shipping_return if i.shipping_return else '',
            #                  "pictures": [
            #                      {'url': base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920",
            #                       "image": base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920"}]
            #                  })
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "products": temp,
            'symbol': website.company_id.currency_id.symbol if website.company_id.currency_id.symbol != False else ""
        }
        return return_Response(res)

    @http.route('/api/v1/c/categ/product.template.view', type='http', auth='public', methods=['GET', 'POST'], csrf=False,
                cors='*')
    def product_template_view_by_categ(self, **params):
        try:
            domain = [('is_product_publish', '=', True), ('is_published', '=', True), ('type', '=', 'product'), ('marketplace_status', 'in', ['approved'])]
            model = 'product.product'
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
                search = 'sale_count_pando DESC'
        limit = 0
        offset = 0
        if "page" in params:
            limit = 12
            page = int(params["page"])
            offset = (page - 1) * 12

        if "search" in params:
            search_data = params["search"]
            domain.append(('name', 'ilike', search_data))

        if "category" in params and params.get('category'):
            domain.append(('public_categ_ids', 'in', [int(params["category"])]))

        if "country_id" in params and params.get('country_id'):
            domain.append(('country_id', '=', int(params.get('country_id'))))
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        if jdata and 'attr' in jdata:
            domain.append(('product_template_attribute_value_ids.product_attribute_value_id', 'in', jdata.get('attr')))
        record_count = request.env[model].sudo().search_count(domain)
        records = request.env[model].sudo().search(domain, order=search, limit=limit, offset=offset)
        if ("orderBy" in params and params['orderBy'] == 'featured') or ("orderBy" in params and params['orderBy'] == 'sale'):
            for res in records:
                try:
                    db_name = odoo.tools.config.get('db_name')
                    db_registry = registry(db_name)
                    with db_registry.cursor() as cr:
                        env = api.Environment(cr, SUPERUSER_ID, {})
                        prod = env['product.product'].sudo().browse([res.id])
                        prod.sudo().write({'sale_count_pando': _compute_sales_count(self=prod)})
                    cr.commit()
                    cr.close()
                except psycopg2.Error:
                    pass
            records = request.env[model].sudo().search(domain, order=search, limit=limit, offset=offset)
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1
        website = request.env['website'].sudo().browse(1)
        try:
            warehouse = request.env['stock.warehouse'].sudo().search(
                [('company_id', '=', website.company_id.id)], limit=1)
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            temp = []
            temp = get_product_details(warehouse, records)
            # for i in records:
            #     image = []
            #     category = []
            #     variant = []
            #     sellers = []
            #     _compute_sales_count(self=i)
            #     i.sale_count_pando = i.sales_count
            #     for j in i.product_template_image_ids:
            #         image.append({"id": j.id, "name": j.name,
            #                       "image": base_url.value + '/web/image/product.image/' + str(j.id) + "/image_1920",
            #                       'url': base_url.value + '/web/image/product.image/' + str(j.id) + "/image_1920",
            #                       })
            #     for z in i.public_categ_ids:
            #         category.append({"id": z.id, "name": z.name, "slug": z.name.lower().replace(" ", "-"),
            #                          "image": base_url.value + '/web/image/product.public.category/' + str(
            #                              z.id) + "/image_1920", })
            #     product_var = request.env['product.product'].sudo().search([('id', '=', int(i.id))])
            #     for k in product_var:
            #         values = []
            #         attribute_name = ''
            #         id = []
            #         data = []
            #         for c in k.product_template_attribute_value_ids:
            #             id.append(c.attribute_id.id)
            #         for attr_id in list(set(id)):
            #             for b in k.product_template_attribute_value_ids:
            #                 if attr_id == b.attribute_id.id:
            #                     attribute_name = b.attribute_id.name
            #                     if attribute_name.lower() == 'color':
            #                         values.append({"color": b.product_attribute_value_id.name,
            #                                        "color_name": b.product_attribute_value_id.html_color})
            #                     else:
            #                         values.append({"id": b.id, "name": b.name, "slug": None,
            #                                        "pivot": {"components_variants_variant_id": k.id,
            #                                                  "component_id": b.id}})
            #             data.append({attribute_name: values})
            #             values = []
            #         res_data = {"id": k.id, "price": k.list_price,
            #                     "pivot": {"product_id": i.id, "component_id": k.id}}
            #
            #         if len(data) != 0:
            #             for dic in data:
            #                 res = list(dic.items())[0]
            #
            #                 # if len
            #                 if res[0].lower() == 'color':
            #                     res_data.update(
            #                         {"color": res[1][0].get('color'), "color_name": res[1][0].get('color_name')})
            #                 else:
            #                     res_data.update(dic)
            #
            #             variant.append(res_data)
            #         else:
            #             pass
            #
            #     for n in i.seller_ids:
            #         sellers.append({"id": n.id, "vendor": n.name.name, "vendor_id": n.name.id})
            #
            #     temp.append({"id": i.id, "name": i.name,
            #                  'url': base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920",
            #                  'image': base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920",
            #                  'type': i.type, 'sale_price': i.list_price, "price": i.standard_price,
            #                  'description': i.description if i.description != False else '',
            #                  'short_desc': i.description_sale if i.description_sale != False else '',
            #                  'categ_id': i.categ_id.id if i.categ_id.id != False else '',
            #                  'categ_name': i.categ_id.name if i.categ_id.name != False else '',
            #                  "category": category,
            #                  "create_uid": i.create_uid.id if i.create_uid.id != False else '',
            #                  "create_name": i.create_uid.name if i.create_uid.name != False else '',
            #                  "write_uid": i.write_uid.id if i.write_uid.id != False else '',
            #                  "write_name": i.write_uid.name if i.write_uid.name != False else '',
            #                  "variants": variant,
            #                  # "stock": i.qty_available,
            #                  "stock": i.with_context(warehouse=warehouse.id).virtual_available if i.with_context(
            #                      warehouse=warehouse.id).virtual_available > 0 else 0.0,
            #                  "sm_pictures": image,
            #                  "featured": i.website_ribbon_id.html if i.website_ribbon_id.html != False else '',
            #                  "seller_ids": sellers,
            #                  "slug": i.id,
            #                  "top": True if i.website_ribbon_id.html == 'Trending' else None,
            #                  "new": True if i.website_ribbon_id.html == 'New' else None,
            #                  "author": "Pando-Stores",
            #                  "sold": i.sales_count,
            #                  "review": 2,
            #                  "rating": 3,
            #                  "marketplace_seller_id": i.marketplace_seller_id.id,
            #                  "marketplace_seller_name": i.marketplace_seller_id.name,
            #                  "additional_info": i.additional_info if i.additional_info else '',
            #                  "shipping_return": i.shipping_return if i.shipping_return else '',
            #                  "pictures": [
            #                      {'url': base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920",
            #                       "image": base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920"}]
            #                  })
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)

        res = {
            "total_count": record_count,
            "count": len(temp),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "products": temp,
            'symbol': website.company_id.currency_id.symbol if website.company_id.currency_id.symbol != False else ""
        }
        return return_Response(res)

    @http.route('/api/v1/c/product.category.view', type='http', auth='public', methods=['GET', 'POST'], csrf=False, cors='*')
    def product_category_view(self, **params):
        country_id = False
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
        if "country_id" in params and params.get('country_id'):
            country_id = int(params.get('country_id'))

        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        attr = False
        if jdata and 'attr' in jdata:
            lst = jdata.get('attr')
            attr = ('product_template_attribute_value_ids.product_attribute_value_id', 'in', jdata.get('attr'))

        if "type" in params and params['type'] == 'popularCategory':
            rec = request.env[model].sudo().search([])
            for j in rec:
                total_count = 0
                dom = [('public_categ_ids', 'in', [j.id]), ('is_product_publish', '=', True), ('is_published', '=', True), ('type', '=', 'product'), ('marketplace_status', 'in', ['approved'])]
                domain = dom.append(('country_id', '=', country_id)) if country_id else dom
                if attr:
                    domain.append(attr)
                search_product = request.env['product.product'].sudo().search(domain)
                for res in search_product:
                    try:
                        db_name = odoo.tools.config.get('db_name')
                        db_registry = registry(db_name)
                        with db_registry.cursor() as cr:
                            env = api.Environment(cr, SUPERUSER_ID, {})
                            prod = env['product.product'].sudo().browse([res.id])
                            prod.sudo().write({'sale_count_pando': _compute_sales_count(self=prod)})
                        cr.commit()
                        cr.close()
                    except psycopg2.Error:
                        pass
                    total_count += res.sale_count_pando
                j.total_sold_count = total_count
            orders = 'total_sold_count DESC'
            limit = 6
        records = request.env[model].sudo().search([], order=orders, limit=limit, offset=offset)
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        try:
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            temp = []
            for i in records:
                domain = [('public_categ_ids', 'in', [i.id]), ('is_product_publish', '=', True), ('is_published', '=', True), ('type', '=', 'product'), ('marketplace_status', 'in', ['approved'])]
                if country_id:
                    domain.append(('country_id', '=', country_id))
                if attr:
                    domain.append(attr)
                search_count = request.env['product.product'].sudo().search_count(domain)
                temp.append({"id": i.id, "name": i.name,
                             "image": base_url.value + '/web/image/product.public.category/' + str(
                                 i.id) + "/image_1920",
                             'parent_id': i.parent_id.id if i.parent_id.id != False else '',
                             'parent_name': i.parent_id.name if i.parent_id.name != False else '',
                             "product_count": search_count, 'total_product_sale_count': i.total_sold_count})
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
        website = request.env['website'].sudo().browse(1)
        try:
            domain = [('is_product_publish', '=', True), ('is_published', '=', True), ('type', '=', 'product'), ('marketplace_status', 'in', ['approved'])]
            categ_id = []
            if 'search' in params:
                model = 'product.public.category'
                try:
                    categ_id = request.env[model].sudo().search([('name', 'ilike', params['search'])]).ids
                    country_id = int(params['country_id']) if "country_id" in params and params['country_id'] else False
                    if categ_id:
                        if country_id:
                            domain = ['&', ('is_published', '=', True), '&',
                                      ('country_id', '=', country_id), '|',
                                      ('name', 'ilike', params['search']),
                                      ('public_categ_ids', 'in', categ_id), ('type', '=', 'product'), ('marketplace_status', 'in', ['approved']), ('is_product_publish', '=', True)]
                        else:
                            domain = ['&', ('is_published', '=', True), '|', ('name', 'ilike', params['search']),
                                      ('public_categ_ids', 'in', categ_id), ('type', '=', 'product'), ('marketplace_status', 'in', ['approved']), ('is_product_publish', '=', True)]
                    else:
                        if country_id:
                            domain = [('is_product_publish', '=', True), ('is_published', '=', True), ('country_id', '=', country_id),
                                      ('name', 'ilike', params['search']), ('type', '=', 'product'), ('marketplace_status', 'in', ['approved'])]
                        else:
                            domain = [('is_product_publish', '=', True), ('is_published', '=', True), ('name', 'ilike', params['search']),
                                      ('type', '=', 'product'), ('marketplace_status', 'in', ['approved'])]

                except KeyError as e:
                    msg = "The model `%s` does not exist." % model
                    return error_response(e, msg)
            else:
                error = {"message": "Something Went Wrong", "status": 400}
                return return_Response_error(error)
            model = 'product.product'
            record = request.env[model].sudo().search(domain)
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            warehouse = request.env['stock.warehouse'].sudo().search(
                [('company_id', '=', website.company_id.id)], limit=1)
            # temp = []
            temp = get_product_details(warehouse, record)
            # for i in record:
            #     image = []
            #     category = []
            #     variant = []
            #     sellers = []
            #     _compute_sales_count(self=i)
            #     i.sale_count_pando = i.sales_count
            #     for j in i.product_template_image_ids:
            #         image.append({"id": j.id, "name": j.name,
            #                       "image": base_url.value + '/web/image/product.image/' + str(j.id) + "/image_1920",
            #                       'url': base_url.value + '/web/image/product.product/' + str(
            #                           j.id) + "/image_1920",
            #                       })
            #     for z in i.public_categ_ids:
            #         category.append({"id": z.id, "name": z.name, "slug": z.name.lower().replace(" ", "-"),
            #                          "image": base_url.value + '/web/image/product.public.category/' + str(
            #                              z.id) + "/image_1920", })
            #     product_var = request.env['product.product'].sudo().search([('id', '=', int(i.id))])
            #     for k in product_var:
            #         values = []
            #         attribute_name = ''
            #         id = []
            #         data = []
            #         for c in k.product_template_attribute_value_ids:
            #             id.append(c.attribute_id.id)
            #         for attr_id in list(set(id)):
            #             for b in k.product_template_attribute_value_ids:
            #                 if attr_id == b.attribute_id.id:
            #                     attribute_name = b.attribute_id.name
            #                     if attribute_name.lower() == 'color':
            #                         values.append({"color": b.product_attribute_value_id.name,
            #                                        "color_name": b.product_attribute_value_id.html_color})
            #                     else:
            #                         values.append({"id": b.id, "name": b.name, "slug": None,
            #                                        "pivot": {"components_variants_variant_id": k.id,
            #                                                  "component_id": b.id}})
            #             data.append({attribute_name: values})
            #             values = []
            #         res_data = {"id": k.id, "price": k.list_price,
            #                     "pivot": {"product_id": i.id, "component_id": k.id}}
            #
            #         if len(data) != 0:
            #             for dic in data:
            #                 res = list(dic.items())[0]
            #
            #                 # if len
            #                 if res[0].lower() == 'color':
            #                     res_data.update(
            #                         {"color": res[1][0].get('color'), "color_name": res[1][0].get('color_name')})
            #                 else:
            #                     res_data.update(dic)
            #
            #             variant.append(res_data)
            #         else:
            #             pass
            #
            #     for n in i.seller_ids:
            #         sellers.append({"id": n.id, "vendor": n.name.name, "vendor_id": n.name.id})
            #
            #     temp.append({"id": i.id, "name": i.name,
            #                  'url': base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920",
            #                  'image': base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920",
            #                  'type': i.type, 'sale_price': i.list_price, "price": i.standard_price,
            #                  'description': i.description if i.description != False else '',
            #                  'short_desc': i.description_sale if i.description_sale != False else '',
            #                  'categ_id': i.categ_id.id if i.categ_id.id != False else '',
            #                  'categ_name': i.categ_id.name if i.categ_id.name != False else '',
            #                  "category": category,
            #                  "create_uid": i.create_uid.id if i.create_uid.id != False else '',
            #                  "create_name": i.create_uid.name if i.create_uid.name != False else '',
            #                  "write_uid": i.write_uid.id if i.write_uid.id != False else '',
            #                  "write_name": i.write_uid.name if i.write_uid.name != False else '',
            #                  "variants": variant,
            #                  # "stock": i.qty_available,
            #                  "stock": i.with_context(warehouse=warehouse.id).virtual_available if i.with_context(
            #                      warehouse=warehouse.id).virtual_available > 0 else 0.0,
            #                  "sm_pictures": image,
            #                  "featured": i.website_ribbon_id.html if i.website_ribbon_id.html != False else '',
            #                  "seller_ids": sellers,
            #                  "slug": i.id,
            #                  "top": True if i.website_ribbon_id.html == 'Trending' else None,
            #                  "new": True if i.website_ribbon_id.html == 'New' else None,
            #                  "author": "Pando-Stores",
            #                  "sold": i.sales_count,
            #                  "review": 2,
            #                  "rating": 3,
            #                  "marketplace_seller_id": i.marketplace_seller_id.id,
            #                  "marketplace_seller_name": i.marketplace_seller_id.name,
            #                  "additional_info": i.additional_info if i.additional_info else '',
            #                  "shipping_return": i.shipping_return if i.shipping_return else '',
            #                  "pictures": [{'url': base_url.value + '/web/image/product.product/' + str(
            #                      i.id) + "/image_1920",
            #                                "image": base_url.value + '/web/image/product.product/' + str(
            #                                    i.id) + "/image_1920"}]
            #                  })

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "products": temp,
            'symbol': website.company_id.currency_id.symbol if website.company_id.currency_id.symbol != False else ""
        }
        return return_Response(res)

    @http.route('/api/v1/c/product.attribute', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def product_attribute_value_list(self, **params):
        try:
            model = 'product.attribute'
            record = request.env[model].sudo().search([])
            attr = []
            for rec in record:
                valueRecord = request.env['product.attribute.value'].sudo().search([('attribute_id', '=', rec.id)])
                temp = []
                for i in valueRecord:
                    vals = {
                        'id': i.id,
                        'name': i.name,
                        'html_color': i.html_color
                    }
                    temp.append(vals)
                vals = {
                    'attribute_id': rec.id,
                    'attribute_name': rec.name,
                    'type': rec.display_type,
                    'value': temp
                }
                attr.append(vals)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(attr),
            "result": attr
        }
        return return_Response(res)


    def get_product_list(self,lst):
        pro = []
        record=[]
        for rec in lst:
            if pro:
                domain = [('product_attribute_value_id', '=', rec), ('product_tmpl_id', 'in', pro)]
            else:
                domain = [('product_attribute_value_id', '=', rec)]
            model = 'product.template.attribute.value'
            record = request.env[model].sudo().search(domain).product_tmpl_id.ids
            if record:
                pro = record
            else:
                return record
        return record

    @http.route('/api/v1/c/product.attribute.filter', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def product_attribute_filter(self, **params):
        try:
            record = []
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                lst = jdata.get('attr')
                record = self.get_product_list(lst)
            records = request.env['product.product'].sudo().search([('product_tmpl_id','in',record)])
            website = request.env['website'].sudo().browse(1)
            warehouse = request.env['stock.warehouse'].sudo().search(
                [('company_id', '=', website.company_id.id)], limit=1)
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            temp = []
            for i in records:
                l = i.product_template_attribute_value_ids.product_attribute_value_id.ids
                if all(item in lst for item in l) or all(item in l for item in lst):
                    image = []
                    category = []
                    variant = []
                    sellers = []
                    _compute_sales_count(self=i)
                    i.sale_count_pando = i.sales_count
                    for j in i.product_template_image_ids:
                        image.append({"id": j.id, "name": j.name,
                                      "image": base_url.value + '/web/image/product.image/' + str(j.id) + "/image_1920",
                                      'url': base_url.value + '/web/image/product.image/' + str(j.id) + "/image_1920",
                                      })
                    for z in i.public_categ_ids:
                        category.append({"id": z.id, "name": z.name, "slug": z.name.lower().replace(" ", "-"),
                                         "image": base_url.value + '/web/image/product.public.category/' + str(
                                             z.id) + "/image_1920", })
                    product_var = request.env['product.product'].sudo().search([('id', '=', int(i.id))])
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

                    temp.append({"id": i.id, "name": i.name,
                                 'url': base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920",
                                 'image': base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920",
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
                                 # "stock":i.qty_available,
                                 "stock": i.with_context(warehouse=warehouse.id).virtual_available if i.with_context(
                                     warehouse=warehouse.id).virtual_available > 0 else 0.0,
                                 "sm_pictures": image,
                                 "featured": i.website_ribbon_id.html if i.website_ribbon_id.html != False else '',
                                 "seller_ids": sellers,
                                 "slug": i.id,
                                 "top": True if i.website_ribbon_id.html == 'Trending' else None,
                                 "new": True if i.website_ribbon_id.html == 'New' else None,
                                 "author": "Pando-Stores",
                                 "sold": i.sales_count,
                                 "review": 2,
                                 "rating": 3,
                                 "additional_info": i.additional_info if i.additional_info else '',
                                 "shipping_return": i.shipping_return if i.shipping_return else '',
                                 "pictures": [
                                     {'url': base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920",
                                      "image": base_url.value + '/web/image/product.product/' + str(
                                          i.id) + "/image_1920"}],
                                 "aaaa":i.product_template_attribute_value_ids.ids
                                 })
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "total_count": len(temp),
            "count": len(temp),
            "prev": None,
            "current": 1,
            "next": None,
            "total_pages": 1,
            "products": temp
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/product.graph.data', type='http', auth='public', methods=['GET'], csrf=False,
                cors='*')
    def product_graph_data(self, **params):
        try:
            user = request.env.user.partner_id.id
            domain = [('marketplace_seller_id', '=', user), ('is_product_publish', '=', True),
                      ('is_published', '=', True), ('type', '=', 'product'),
                      ('marketplace_status', 'in', ['approved'])]
            records = request.env['product.product'].sudo().search(domain)
            count_list = []
            for res in records:
                count_list.append({'id': res.id, 'name': res.name, 'count': _compute_sales_count(self=res)})
            new_lst = sorted(count_list, key=lambda i: i['count'], reverse=True)
            list_of_prod_ids = list(map(lambda d: d['id'], new_lst))
            prod_records = request.env['product.product'].sudo().browse(list_of_prod_ids)
            prod_name = []
            prod_sale_count = []
            for i in prod_records:
                prod_name.append(i.name)
                prod_sale_count.append(_compute_sales_count(self=i))
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "prod_name": prod_name,
            "prod_sale_count": prod_sale_count
        }
        return return_Response(res)

