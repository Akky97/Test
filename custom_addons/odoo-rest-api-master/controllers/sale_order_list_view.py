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
                # sale_order_data[i.id] ={
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
            # pricelist_context, pricelist_id = self._get_pricelist_context()
            website_id = request.env['website'].get_current_website()
            pricelist_id = website_id.get_current_pricelist()
            jdata = json.loads(request.httprequest.stream.read())
            if not jdata.get('product_id'):
                error = {"message": "Product id is not present in the request", "status": 400}
                return return_Response_error(error)
            if not jdata.get('variant_id'):
                variant_id = False
            else:
                variant_id = jdata.get('variant_id')
            if not jdata.get('partner_id'):
                error = {"message": "Partner id is not present in the request", "status": 400}
                return return_Response_error(error)
            product_id = jdata.get('product_id')
            partner_id = jdata.get('partner_id')
            if product_id and variant_id:
                model = 'product.product'
                product_id = request.env[model].sudo().search([('id', '=', int(variant_id))])
            elif product_id and not variant_id:
                model = 'product.product'
                product_id = request.env[model].sudo().search([('product_tmpl_id', '=', int(product_id))])
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
                error = {"message": "The Selected Product is in wishlist", "status": 400}
                return return_Response_error(error)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "result": 'Product Added Successfully', 'status': 200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/product.wishlist', type='http', auth='none', methods=['DELETE'], csrf=False, cors='*', website=True)
    def remove_from_wishlistlist(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())

            if not jdata.get('product_id'):
                error = {"message": "Product id is not present in the request", "status": 400}
                return return_Response_error(error)
            product_id = int(jdata.get('product_id'))
            if not jdata.get('product_id'):
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
            wishList = []
            if records:
                for rec in records:
                    values = {
                        'product_id': rec.product_id.id,
                        'product_name': rec.product_id.product_tmpl_id.name,
                        'image': base_url.value + '/web/image/product.template/' + str(
                            rec.id) + '/image_1920/' + rec.product_id.product_tmpl_id.name,
                        'pricelist_id': rec.pricelist_id.id,
                        'price': rec.product_id.product_tmpl_id.list_price,
                    }
                    wishList.append(values)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(wishList),
            "result": wishList
        }
        return return_Response(res)

