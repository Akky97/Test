from .exceptions import QueryFormatError
from .error_or_response_parser import *
from .payment_controllers import *
from odoo.addons.website_sale.controllers.main import WebsiteSale
import phonenumbers
from odoo import http, _, exceptions, SUPERUSER_ID
from odoo.http import request

def get_sale_order_line(order_id=None, order_line_id=None):
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
            count += 1
        request.session['count'] = count
        # saleOrderLine['count'] = count
    print('sale order line details', saleOrderLine)
    return saleOrderLine

def updatePriceListAPK(pricelist, order):
    if order and pricelist:
        request.session['website_sale_current_pl'] = pricelist
        values = {'pricelist_id': pricelist}
        order.write(values)
        for line in order.order_line:
            if line.exists():
                order._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=0)



def checkout_data_apk(order):
    shippingAddress = []
    Partner = False
    if order.partner_id != request.website.user_id.sudo().partner_id:
        Partner = order.partner_id.with_context(show_address=1).sudo()
        shippings = Partner.search([
            ("id", "child_of", order.partner_id.commercial_partner_id.ids),
            '|', ("type", "in", ["delivery", "other"]), ("id", "=", order.partner_id.commercial_partner_id.id)
        ], order='id desc')
        if shippings:
            shippingAddress = []
            for i in shippings:
                shippingAddress.append(get_address(i))
    sale_order= {
        'id': order.id,
        'name': order.name if order.name != False else "",
        'order_line': get_sale_order_line(order_id=order.id),
        'amount_untaxed': order.amount_untaxed if order.amount_untaxed != False else 0.0,
        'amount_tax': order.amount_tax if order.amount_tax != False else 0.0,
        'amount_total': order.amount_total if order.amount_total != False else 0.0,
        'symbol': order.currency_id.symbol if order.currency_id.symbol != False else ""
    }
    values = [{
        'order': sale_order,
        'shippingAddress': shippingAddress,
        'invoiceAddress': get_address(Partner) if Partner else [],
        'only_services': order and order.only_services or False,
        'express': False
    }]
    return values

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
                message = {"result": 0, "status": 200}
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
            website = request.env['website'].sudo().browse(1)
            warehouse = request.env['stock.warehouse'].sudo().search(
                [('company_id', '=', website.company_id.id)], limit=1)
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
                                 # "stock": i.qty_available,
                                 "stock": i.with_context(warehouse=warehouse.id).virtual_available if i.with_context(
                                     warehouse=warehouse.id).virtual_available > 0 else 0.0,
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

    @validate_token
    @http.route(['/api/v1/apk/get_address_apk','/api/v1/apk/get_address_apk/<id>'], type='http', auth='public', methods=['GET'], csrf=False, cors='*',
                website=True)
    def get_address_apk(self, id, **params):
        model = 'res.partner'
        temp = []
        try:
            if not id:
                error = {"message": "Partner id is not present in the request", "status": 400}
                return return_Response_error(error)
            model = 'res.partner'
            records = request.env[model].sudo().search([('id', '=', id)])
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        try:
            res_id = request.env['ir.attachment'].sudo()
            res_id = res_id.sudo().search([('res_model', '=', 'res.partner'),
                                           ('res_field', '=', 'image_1920'),
                                           ('res_id', 'in', [id])])
            res_id.sudo().write({"public": True})

            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            for i in records:
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
                             "image": base_url.value + '/web/image/' + str(res_id.id),
                             "type": i.type,
                             "website": i.website if i.website != False else ""})
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "result": temp
        }
        return return_Response(res)


    @validate_token
    @http.route('/api/v1/c/comfirm_order_apk', type='http', auth='public', methods=['GET'], csrf=False, cors='*',
                website=True)
    def confirm_order_apk(self, **params):
        try:
            redirectUrl = ''
            transactionId = False
            result = {}
            website = request.env['website'].sudo().browse(1)
            partner = request.env.user.partner_id
            order = request.env['sale.order'].sudo().search([('state', '=', 'draft'),
                                                             ('partner_id', '=', partner.id),
                                                             ('website_id', '=', website.id)],
                                                            order='write_date DESC', limit=1)
            redirectUrl = checkout_redirection(order, request.env.context.get(
                'website_sale_transaction')) or checkout_check_address(order)
            paymentAcquirer = request.env['payment.acquirer'].sudo().search([('state', 'in', ['enabled', 'test'])], limit=1)
            if not redirectUrl:
                order.onchange_partner_shipping_id()
                order.order_line._compute_tax_id()
                request.session['sale_last_order_id'] = order.id
                pricelist_id = request.session.get('website_sale_current_pl') or website.get_current_pricelist().id
                updatePriceListAPK(pricelist_id, order)
                if paymentAcquirer:
                    payTransferData = create_transaction(paymentAcquirer.id)
                    if payTransferData:
                        if 'message' in payTransferData and payTransferData.get('message'):
                            msg = {"message": payTransferData.get('message'), "status_code": 400}
                            return return_Response_error(msg)
                        if 'id' in payTransferData and payTransferData.get('id'):
                            res = {
                                "transactionId": payTransferData.get('id'),
                                "redirect": 'success', "status": 200
                            }
                            return return_Response(res)
                        else:
                            res = {
                                "message": "Something Went Wrong. Transaction is not created", "status": 400
                            }
                            return return_Response_error(res)
                    else:
                        res = {
                            "message": "Something Went Wrong. Transaction is not created", "status": 400
                        }
                        return return_Response_error(res)
                else:
                    res = {
                        "message": "Payment Method is missing", "status": 400
                    }
                    return return_Response_error(res)
            else:
                res = {
                    "message": f"Something Went Wrong. Please Go To {redirectUrl} ","status":400
                }
                return return_Response_error(res)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)

