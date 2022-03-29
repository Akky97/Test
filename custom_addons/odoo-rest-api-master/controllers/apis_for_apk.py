from .exceptions import QueryFormatError
from .error_or_response_parser import *
from odoo.addons.website_sale.controllers.main import WebsiteSale
import phonenumbers
from odoo import http, _, exceptions, SUPERUSER_ID
from odoo.http import request


def get_sale_order_line(order_id=None, order_line_id = None):

    saleOrderLine = []
    count = 0
    base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)

    solObject = request.env['sale.order.line'].sudo()
    if order_id:
        solObject = solObject.search([('order_id','=',order_id)])
    if order_line_id:
        solObject = solObject.search([('order_id','=',order_id)])
    if solObject:
        for rec in solObject:
            saleOrderLine.append({
                'id': rec.id if rec.id != False else "",
                'name': rec.name if rec.name != False else "",
                'product_id': rec.product_id.id if rec.product_id.id != False else "",
                'product_name': rec.product_id.name if rec.product_id.name != False else "",
                'price_unit': rec.price_unit if rec.price_unit != False else 0.0,
                'price_subtotal': rec.price_subtotal if rec.price_subtotal != False else 0.0,
                'price_tax': rec.price_tax if rec.price_tax != False else 0.0,
                'price_total': rec.price_total if rec.price_total != False else 0.0,
                'quantity': rec.product_uom_qty if rec.product_uom_qty != False else 0.0,
                "image": base_url.value + '/web/image/product.product/' + str(rec.product_id.id) + "/image_1920",
                # 'qty_delivered': rec.qty_delivered if rec.qty_delivered != False else "",
                # 'qty_invoiced': rec.qty_invoiced if rec.qty_invoiced != False else ""
            })
            count += rec.product_uom_qty
        request.session['count'] = count
        # saleOrderLine['count'] = count
    print('sale order line details', saleOrderLine)
    return saleOrderLine

class WebsiteSale(WebsiteSale):

    @validate_token
    @http.route('/api/v1/apk/get_cart', type='http', auth='public', methods=['GET'], csrf=False, cors='*',
                website=True)
    def get_cart_apk(self, **params):
        try:
            sale_order = []
            website = request.website
            partner = request.env.user.partner_id
            # order = sale_get_order(self=request.website, partner_id=partner.id)
            order = request.env['sale.order'].sudo().search([('state', '=', 'draft'),
                                                             ('partner_id', '=', partner.id),
                                                             ('website_id', '=', website.id)],
                                                            order='write_date DESC', limit=1)
            if order and order.order_line:
                sale_order.append({
                    'id': order.id,
                    'order_line': get_sale_order_line(order_id=order.id),
                    'amount_untaxed': order.amount_untaxed if order.amount_untaxed != False else 0.0,
                    'amount_tax': order.amount_tax if order.amount_tax != False else 0.0,
                    'amount_total': order.amount_total if order.amount_total != False else 0.0,
                    'symbol': order.currency_id.symbol if order.currency_id.symbol != False else "",
                    'count': int(request.session.get('count'))
                })
            else:
                message = {"message": "Cart is Empty", "status": 200}
                return return_Response(message)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {"result": sale_order}
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/apk/product.wishlist', type='http', auth='public', methods=['GET'], csrf=False, cors='*', website=True)
    def get_wishlistlist_apk(self, **params):
        try:
            wishList = []
            if "partner_id" not in params:
                error = {"message": "Partner id is not present in request", "status": 400}
                return return_Response_error(error)
            partner_id = int(params["partner_id"])
            model = 'product.wishlist'
            records = request.env[model].sudo().search([('partner_id', '=', partner_id)])
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        try:
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            temp = []
            category = []
            if records:
                for rec in records:
                    i = request.env['product.product'].sudo().search([('id', '=', rec.product_id.id)])
                    for z in i.public_categ_ids:
                        category.append({"id": z.id, "name": z.name, "slug": z.name.lower().replace(" ", "-"),
                                         "image": base_url.value + '/web/image/product.public.category/' + str(
                                             z.id) + "/image_1920", })

                    temp.append({"id": i.id, "name": i.name,
                                 'image': base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920",
                                 'type': i.type, 'sale_price': i.list_price, "price": i.standard_price,
                                 'description': i.description if i.description != False else '',
                                 "stock": i.qty_available,
                                 "sold": i.sales_count,
                                 "review": 2,
                                 "rating": 3,
                                 'categ_id': i.categ_id.id if i.categ_id.id != False else '',
                                 'categ_name': i.categ_id.name if i.categ_id.name != False else '',
                                 "category": category}
                                )

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "result": temp
        }
        return return_Response(res)
