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
from odoo.addons.website_sale.controllers.main import WebsiteSale
_logger = logging.getLogger(__name__)


def get_sale_order_line(order_id=None, order_line_id = None):
    saleOrderLine = {}
    solObject = request.env['sale.order.line'].sudo()
    if order_id:
        solObject = solObject.search([('order_id','=',order_id)])
    if order_line_id:
        solObject = solObject.search([('order_id','=',order_id)])
    if solObject:
        for rec in solObject:
            saleOrderLine[rec.id] = {
                'id': rec.id if rec.id != False else "",
                'name': rec.name if rec.name != False else "",
                'product_id': rec.product_id.id if rec.product_id.id != False else "",
                'product_name': rec.product_id.name if rec.product_id.name != False else "",
                'price_unit': rec.price_unit if rec.price_unit != False else "",
                'price_subtotal': rec.price_subtotal if rec.price_subtotal != False else "",
                'price_tax': rec.price_tax if rec.price_tax != False else "",
                'price_total': rec.price_total if rec.price_total != False else "",
                'tax_id': [{i.id:i.name} for i in rec.tax_id],
                'qty_delivered': rec.qty_delivered if rec.qty_delivered != False else "",
                'qty_invoiced': rec.qty_invoiced if rec.qty_invoiced != False else ""
            }
    print('sale order line details', saleOrderLine)
    return saleOrderLine


def optional_products(order_id=None):
    optionalProduct = {}
    if order_id:
        optionalProductObj = request.env['sale.order.option'].sudo().search([('order_id','=',order_id)])
        if optionalProductObj:
            for i in optionalProductObj:
                optionalProduct[i.id]={
                    'id':i.id if i.id != False else "",
                    'name':i.name if i.name != False else "",
                    'product_id':i.product_id.id if i.product_id.id != False else "",
                    'product_name':i.product_id.name if i.product_id.name != False else "",
                    'price_unit':i.price_unit if i.price_unit != False else "",
                    'discount': i.discount if i.discount != False else "",
                    'uom_id': i.uom_id.id if i.uom_id.id != False else "",
                    'uom_name': i.uom_id.name if i.uom_id.name != False else "",
                    'quantity': i.quantity if i.quantity != False else ""
                }
    return optionalProduct


def get_address(id):
    address ={}
    if id:
        res_id = request.env['ir.attachment'].sudo()
        res_id = res_id.sudo().search([('res_model', '=', 'res.partner'),
                                       ('res_field', '=', 'image_1920'),
                                       ('res_id', 'in', [id])])
        base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
        address = {"id": id.id, "name": id.name, "phone": id.phone if id.phone != False else "",
                           "mobile": id.mobile if id.mobile != False else "",
                           "email": id.email if id.email != False else "",
                           "street": id.street if id.street != False else "",
                           "street2": id.street2 if id.street2 != False else "",
                           "city": id.city if id.city != False else "",
                           "state_id": id.state_id.id if id.state_id.id != False else "",
                           "state_name": id.state_id.name if id.state_id.name != False else "",
                           "zip": id.zip if id.zip != False else "",
                           "country_id": id.country_id.id if id.country_id.id != False else "",
                           "country_name": id.country_id.name if id.country_id.name != False else "",
                           "website": id.website if id.website != False else "",
                           "image":  base_url.value + '/web/image/' + str(res_id.id),}
    print('address details', address)
    return address


class SaleOrderController(http.Controller):
    # @validate_token
    @http.route('/api/v1/c/sale_orders/<partner_id>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def sale_order_list_view(self, partner_id=None ,**params):
        try:
            if not partner_id:
                error = {"message": "partner_id is not present in the request", "status": 400}
                return return_Response_error(error)
            model = 'sale.order'
            records = request.env[model].sudo().search([('partner_id', '=', int(partner_id))])
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        try:
            sale_order_data = []
            for i in records:
                value ={
                    'id' :i.id,
                    'name':i.name if i.name != False else "",
                    'order_line': get_sale_order_line(order_id=i.id),
                    'partner_id': get_address(i.partner_id),
                    'partner_invoice_id': get_address(i.partner_invoice_id),
                    'partner_shipping_id': get_address(i.partner_shipping_id),
                    'date_order': str(i.date_order) if str(i.date_order) != False else "",
                    'currency_id': i.currency_id.id if i.currency_id.id != False else "",
                    'currency_name': i.currency_id.name if i.currency_id.name != False else "",
                    'company_id': i.company_id.id if i.company_id.id != False else "",
                    'company_name': i.company_id.name if i.company_id.name != False else "",
                    'pricelist_id': i.pricelist_id.id if i.pricelist_id.id != False else "",
                    'pricelist_name': i.pricelist_id.name if i.pricelist_id.name != False else "",
                    'state': i.state if i.state != False else "",
                    'user_id': i.user_id.id if i.user_id.id != False else "",
                    'user_name': i.user_id.name if i.user_id.name != False else "",
                    'amount_untaxed': i.amount_untaxed if i.amount_untaxed != False else "",
                    'amount_tax': i.amount_tax if i.amount_tax != False else "",
                    'amount_total': i.amount_total if i.amount_total != False else "",
                    'picking_policy': i.picking_policy if i.picking_policy != False else "",
                    'warehouse_id': i.warehouse_id.id if i.warehouse_id.id != False else "",
                    'warehouse_name': i.warehouse_id.name if i.warehouse_id.name != False else "",
                    'optional_products': optional_products(i.id),
                    'invoice_status': i.invoice_status if i.invoice_status != False else "",
                    'fiscal_position_id': i.fiscal_position_id.id if i.fiscal_position_id.id != False else ""
                }
                sale_order_data.append(value)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(sale_order_data),
            "result": sale_order_data
        }
        return return_Response(res)


class WebsiteSale(WebsiteSale):
    @validate_token
    @http.route('/api/v1/c/cart_update', type='http', auth='public', methods=['POST'], csrf=False, cors='*', website=True)
    def cart_update(self, **params):
        try:
            jdata = json.loads(request.httprequest.stream.read())
            if not jdata.get('product_id') or not jdata.get('set_qty') or not jdata.get('add_qty'):
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
            product_id = int(jdata.get('product_id')) or False
            set_qty = int(jdata.get('set_qty')) or 0
            add_qty = int(jdata.get('add_qty')) or 1
            sale_order = request.website.sale_get_order()
            if sale_order.state != 'draft':
                request.session['sale_order_id'] = None
                sale_order = request.website.sale_get_order(force_create=True)
            if product_id:
                sale_order._cart_update(
                    product_id=int(product_id),
                    add_qty=add_qty,
                    set_qty=set_qty,
                    product_custom_attribute_values=None,
                    no_variant_attribute_values=None
                )
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {"result": 'Updated cart Successfully', "status": 200}
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/product.wishlist', type='http', auth='none', methods=['POST'], csrf=False, cors='*', website=True)
    def add_to_wishlistlist(self):
        try:
            website_id = request.env['website'].get_current_website()
            pricelist_id = website_id.get_current_pricelist()
            jdata = json.loads(request.httprequest.stream.read())
            if not jdata.get('product_id'):
                error = {"message": "Product id is not present in the request", "status": 400}
                return return_Response_error(error)
            if not jdata.get('partner_id'):
                error = {"message": "Partner id is not present in the request", "status": 400}
                return return_Response_error(error)
            product_id = jdata.get('product_id')
            partner_id = jdata.get('partner_id')
            model = 'product.product'
            product_id = request.env[model].sudo().search([('id', '=', int(product_id))])
            model = 'product.wishlist'
            records = request.env[model].sudo().search(
                [('partner_id', '=', partner_id), ('product_id', '=', product_id.id)])

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        try:
            if not records:
                values = {
                    'partner_id': partner_id,
                    'product_id': product_id.id,
                    'pricelist_id': pricelist_id.id,
                    'price': product_id.product_tmpl_id.list_price,
                    'website_id': website_id.id
                }
                request.env['product.wishlist'].sudo().create(values)

            else:
                error = {"message": "The Selected Product is in wishlist", "status": 200}
                return return_Response(error)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "message": 'Product Added Successfully', 'status': 200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/delete/product.wishlist', type='http', auth='none', methods=['POST'], csrf=False, cors='*', website=True)
    def remove_from_wishlistlist(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())

            if not jdata.get('product_id'):
                error = {"message": "Product id is not present in the request", "status": 400}
                return return_Response_error(error)
            product_id = int(jdata.get('product_id'))
            if not jdata.get('partner_id'):
                error = {"message": "Partner id is not present in the request", "status": 400}
                return return_Response_error(error)
            partner_id = int(jdata.get('partner_id'))
            model = 'product.wishlist'
            records = request.env[model].sudo().search(
                [('partner_id', '=', partner_id), ('product_id', '=', product_id)])
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        try:
            if records:
                for rec in records:
                    rec.unlink()
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "result": 'Product Deleted Successfully', "status": 200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/product.wishlist', type='http', auth='public', methods=['GET'], csrf=False, cors='*', website=True)
    def get_wishlistlist(self, **params):
        try:
            wishList = []
            if "partner_id" not in params:
                error = {"message": "Partner Id is not present in request", "status": 400}
                return return_Response_error(error)
            partner_id = int(params["partner_id"])
            model = 'product.wishlist'
            records = request.env[model].sudo().search([('partner_id', '=', partner_id)])
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        try:
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            temp = []
            if records:
                for rec in records:
                    i = request.env['product.product'].sudo().search([('id', '=', rec.product_id.id)])
                    image = []
                    category = []
                    variant = []
                    sellers = []
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
                                 "stock": i.qty_available,
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
                                      "image": base_url.value + '/web/image/product.template/' + str(
                                          i.id) + "/image_1920"}]
                                 })

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "result": temp
        }
        return return_Response(res)

