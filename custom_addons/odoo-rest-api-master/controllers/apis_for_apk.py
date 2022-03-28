from .exceptions import QueryFormatError
from .error_or_response_parser import *
from odoo.addons.website_sale.controllers.main import WebsiteSale
import phonenumbers
from odoo import http, _, exceptions, SUPERUSER_ID
from odoo.http import request


def get_sale_order_line(order_id=None, order_line_id = None):

    saleOrderLine = []
    count = 0
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
                'price_unit': rec.price_unit if rec.price_unit != False else "",
                'price_subtotal': rec.price_subtotal if rec.price_subtotal != False else "",
                'price_tax': rec.price_tax if rec.price_tax != False else "",
                'price_total': rec.price_total if rec.price_total != False else "",
                'quantity': rec.product_uom_qty if rec.product_uom_qty != False else "",
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
                    'amount_untaxed': order.amount_untaxed if order.amount_untaxed != False else "",
                    'amount_tax': order.amount_tax if order.amount_tax != False else "",
                    'amount_total': order.amount_total if order.amount_total != False else "",
                    'symbol': order.currency_id.symbol if order.currency_id.symbol != False else "",
                    'count': request.session.get('count')
                })
            else:
                message = {"message": "Cart is Empty", "status": 200}
                return return_Response(message)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {"result": sale_order}
        return return_Response(res)

