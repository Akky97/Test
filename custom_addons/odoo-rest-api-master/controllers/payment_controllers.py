import phonenumbers
from odoo import http, _, exceptions, SUPERUSER_ID
from odoo.http import request
from .exceptions import QueryFormatError
from .error_or_response_parser import *
from odoo.addons.website_sale.controllers.main import WebsiteSale
import datetime
import base64
from .sale_order_list_view import *
_logger = logging.getLogger(__name__)
import stripe
SECRET_KEY = 'sk_test_51Kg63YHk8ErRzzRMjkcktAlL10lqxtkuAShLk09e0kD8iEE7aGCwoV8tHoDtKICnLlNEc6GEpGdXVFw3QBetvkGW00rsDPcDUV'
stripe.api_key = SECRET_KEY


def create_checkout_session(jdata):
    checkout_session = {}
    if jdata:
        base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
        if 'amount' in jdata and jdata.get('amount'):
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price_data': {
                            'currency': jdata.get('currency') or 'usd',
                            'product_data': {
                                'name': jdata.get('reference') or 'Test Product'
                            },
                            'unit_amount': int(jdata.get('amount')) * 100,
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=base_url.value + '/success.html',
                cancel_url=base_url.value + '/cancel.html',
            )
    return checkout_session


def payment_validate(transaction_id,order):
    res = False
    transaction = request.env['payment.transaction'].sudo().search([('id','=',transaction_id)])
    if transaction:
        res = transaction.sudo().write({
            'state':'done'
        })
        if res:
            res = order.with_context(send_email=True).action_confirm()
    return res


def create_transaction(acquirer_id):
    if not acquirer_id:
        return False

    try:
        acquirer_id = int(acquirer_id)
    except:
        return False
    # website = request.website
    website = request.env['website'].sudo().browse(1)
    partner = request.env.user.partner_id
    order = request.env['sale.order'].sudo().search([('state', '=', 'draft'),
                                                     ('partner_id', '=', partner.id),
                                                     ('website_id', '=', website.id)],
                                                    order='write_date DESC', limit=1)

    # Ensure there is something to proceed
    if not order or (order and not order.order_line):
        return False
    # Check Product Quantity
    values = {}
    for line in order.order_line:
        if line.product_id.type == 'product' and line.product_id.inventory_availability in ['always', 'threshold']:
            cart_qty = sum(
                order.order_line.filtered(lambda p: p.product_id.id == line.product_id.id).mapped('product_uom_qty'))
            avl_qty = line.product_id.with_context(warehouse=order.warehouse_id.id).virtual_available
            if cart_qty > avl_qty:
                available_qty = avl_qty if avl_qty > 0 else 0
                message = f'You ask for {cart_qty} products but only {available_qty} is available'
                values['message']=message
                return message
    # # Delivery Method Check
    # if not order.is_all_service and not order.delivery_set:
    #     message = 'There is an issue with your delivery method. Please refresh the page and try again.'
    #     values['message'] = message
    #     return message

    assert order.partner_id.id != request.website.partner_id.id

    # Create transaction
    vals = {'acquirer_id': acquirer_id,
            'return_url': '/shop/payment/validate'}

    transaction = order._create_payment_transaction(vals)
    if transaction:
        transaction._log_payment_transaction_sent()
    value = {
        'reference': transaction.reference,
        'amount': order.amount_total,
        'currency': order.pricelist_id.currency_id.name,
        'id': transaction.id
    }
    return value

def create_invoice(transaction_id, order):
    res = payment_validate(transaction_id, order)
    if res:
        invoice = order._create_invoices(final=True)
        if invoice:
            res = invoice.action_post()
            template = request.env.ref('odoo-rest-api-master.email_template_edi_invoice_extra')
            data, data_format = request.env.ref('account.account_invoices').sudo()._render_qweb_pdf([invoice.id])
            data_record = base64.b64encode(data)
            if template:
                ir_values = {
                    'name': "Invoice Report",
                    'type': 'binary',
                    'datas': data_record,
                    'store_fname': data_record,
                    'mimetype': 'application/pdf',
                    'res_model': 'account.move',
                    'res_id': invoice.id,
                }
                data_id = request.env['ir.attachment'].create(ir_values)
                template.attachment_ids = [(6,0, data_id.ids)]
                template.sudo().send_mail(invoice.id, force_send=True)

def updatePriceList(pricelist, order):
    if order and pricelist:
        request.session['website_sale_current_pl'] = pricelist
        values = {'pricelist_id': pricelist}
        order.write(values)
        for line in order.order_line:
            if line.exists():
                order._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=0)


def checkout_redirection(order, tx):
    redirectUrl = ''
    if not order or order.state != 'draft':
        redirectUrl = 'Home Page'
    if order and not order.order_line:
        redirectUrl = 'Home Page'

    # # if transaction pending / done: redirect to confirmation
    # if tx and tx.state != 'draft':
    #     redirectUrl = f'/shop/payment/confirmation/{order.id}'
    return redirectUrl

def _get_mandatory_billing_fields(country_id=False):
    fields = ["name", "email", "street", "city", "country_id"]
    if country_id:
        if country_id.state_required:
            fields += ['state_id']
        if country_id.zip_required:
            fields += ['zip']
    return fields

def _get_mandatory_shipping_fields(country_id=None):
    fields = ["name", "street", "city", "country_id"]
    if country_id:
        if country_id.state_required:
            fields += ['state_id']
        if country_id.zip_required:
            fields += ['zip']
    return fields

def checkout_check_address(order):
    redirectUrl = ''
    billing_fields_required = _get_mandatory_billing_fields(order.partner_id.country_id)
    if not all(order.partner_id.read(billing_fields_required)[0].values()):
        redirectUrl = f'Profile / Address Page'
    shipping_fields_required = _get_mandatory_shipping_fields(order.partner_shipping_id.country_id)
    if not all(order.partner_shipping_id.read(shipping_fields_required)[0].values()):
        redirectUrl = f'Profile / Address Page'
    return redirectUrl

def checkout_data(order):
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
        'amount_untaxed': order.amount_untaxed if order.amount_untaxed != False else "",
        'amount_tax': order.amount_tax if order.amount_tax != False else "",
        'amount_total': order.amount_total if order.amount_total != False else "",
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

def create_new_address(params):
    value = {}
    partnerObj = request.env['res.partner'].sudo()
    if all(item in params.keys() for item in ["name", "street", "city", "country_id", "state_id", "zip"]):
        country_id = request.env['res.country'].sudo().search([('id','=',int(params['country_id']))])
        if country_id:
            if "mobile" in params and "email" in params:
                res = partnerObj.search([('mobile', '=', params['mobile']),('email', '=', params['email'])])
                if res:
                    value["message"] = "Email Or Mobile Number Already Exists"
                else:
                    my_number = phonenumbers.parse(str(params['mobile']), country_id.code)
                    if not phonenumbers.is_valid_number(my_number):
                        value["message"] = "Please Enter Correct Mobile Number"
        if 'message' not in value:
            rec = partnerObj.create(params)
            if rec:
                value['id'] = rec.id
    else:
        value["message"] = "Some Required Fields Are Empty"
    return value



class WebsiteSale(WebsiteSale):

    @validate_token
    @http.route('/api/v1/c/process_checkout', type='http', auth='public', methods=['GET'], csrf=False, cors='*',
                website=True)
    def process_checkout_api(self, **params):
        try:
            redirectUrl = ""
            values = {}
            website = request.env['website'].sudo().browse(1)
            # website = request.website
            partner = request.env.user.partner_id
            order = request.env['sale.order'].sudo().search([('state', '=', 'draft'),
                                                             ('partner_id', '=', partner.id),
                                                             ('website_id', '=', website.id)],
                                                            order='write_date DESC', limit=1)

            # order = request.website.sale_get_order()
            redirectUrl = checkout_redirection(order, request.env.context.get('website_sale_transaction'))
            if not redirectUrl:
                if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
                    redirectUrl = 'Login Page'
                if not redirectUrl:
                    redirectUrl = checkout_check_address(order)
                    if not redirectUrl:
                        values = checkout_data(order)
            if redirectUrl:
                res = {
                    "message": f"Something Went Wrong. Please Go To {redirectUrl} ","status":400
                }
                return return_Response_error(res)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "result": values,
            "status":200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/comfirm_order_api', type='http', auth='public', methods=['GET'], csrf=False, cors='*',
                website=True)
    def confirm_order_api(self, **params):
        try:
            redirectUrl = ''
            website = request.env['website'].sudo().browse(1)
            # website = request.website
            partner = request.env.user.partner_id
            order = request.env['sale.order'].sudo().search([('state', '=', 'draft'),
                                                             ('partner_id', '=', partner.id),
                                                             ('website_id', '=', website.id)],
                                                            order='write_date DESC', limit=1)
            redirectUrl = checkout_redirection(order, request.env.context.get(
                'website_sale_transaction')) or checkout_check_address(order)
            if not redirectUrl:
                order.onchange_partner_shipping_id()
                order.order_line._compute_tax_id()
                request.session['sale_last_order_id'] = order.id
                pricelist_id = request.session.get('website_sale_current_pl') or website.get_current_pricelist().id
                updatePriceList(pricelist_id, order)
            else:
                res = {
                    "message": f"Something Went Wrong. Please Go To {redirectUrl} ","status":400
                }
                return return_Response_error(res)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "redirect": 'success',"status":200
        }
        return return_Response(res)

    @validate_token
    @http.route(['/api/v1/c/update_shipping_address', '/api/v1/c/update_shipping_address/<id>/'], type='http',
                auth='public', methods=['PUT'], csrf=False, cors='*',
                website=True)
    def update_shipping_address(self, id=None, **params):
        try:
            if not id:
                error = {"message": "id is not present in the request", "status": 400}
                return return_Response_error(error)
            website = request.env['website'].sudo().browse(1)
            # website = request.website
            partner = request.env.user.partner_id
            order = request.env['sale.order'].sudo().search([('state', '=', 'draft'),
                                                             ('partner_id', '=', partner.id),
                                                             ('website_id', '=', website.id)],
                                                            order='write_date DESC', limit=1)

            # order = request.website.sale_get_order()
            if order:
                order.sudo().write({'partner_shipping_id': int(id)})
            else:
                res = {
                    "message": "Something Went Wrong. Please Go To Home Page ", "status": 400
                }
                return return_Response_error(res)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "result": 'Shipping Address Updated Successfully','status':200,
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/payment_page', type='http', auth='public', methods=['GET'], csrf=False, cors='*',website=True)
    def payment_page(self, **params):
        try:
            redirectUrl = ''
            payAcquirer = []
            values = {}
            website = request.env['website'].sudo().browse(1)
            # website = request.website
            partner = request.env.user.partner_id
            order = request.env['sale.order'].sudo().search([('state', '=', 'draft'),
                                                             ('partner_id', '=', partner.id),
                                                             ('website_id', '=', website.id)],
                                                            order='write_date DESC', limit=1)

            # order = request.website.sale_get_order()
            paymentAcquirer = request.env['payment.acquirer'].sudo().search([('state','in',['enabled','test'])])
            if order:
                redirectUrl = checkout_redirection(order, request.env.context.get(
                    'website_sale_transaction')) or checkout_check_address(order)
                if not redirectUrl:
                    # Payment Acquirer List
                    for pa in paymentAcquirer:
                        val = {
                            'id': pa.id,
                            'name':pa.name
                        }
                        payAcquirer.append(val)
                    # End Here
                    # Sale Order Details
                    sale_order = {
                        'id': order.id,
                        'name': order.name if order.name != False else "",
                        'order_line': get_sale_order_line(order_id=order.id),
                        'amount_untaxed': order.amount_untaxed if order.amount_untaxed != False else "",
                        'amount_tax': order.amount_tax if order.amount_tax != False else "",
                        'amount_total': order.amount_total if order.amount_total != False else "",
                        'symbol': order.currency_id.symbol if order.currency_id.symbol != False else ""
                    }
                    # End Here
                    # User Shipping and Billing Details
                    values = {
                        'order': sale_order,
                        'shippingAddress': get_address(order.partner_shipping_id),
                        'invoiceAddress': get_address(order.partner_invoice_id),
                        'payAcquirer':payAcquirer
                    }
                    #         End hete
            else:
                redirectUrl = 'Home Page'
            if redirectUrl:
                res = {
                    "message": f"Something Went Wrong. Please Go To {redirectUrl} ", "status": 400
                }
                return return_Response_error(res)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "result": values
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/pay_now', type='http', auth='public', methods=['POST'], csrf=False, cors='*',
                website=True)
    def pay_now(self, **params):
        try:
            result={}
            finalResult = {}
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                acquirer_id = jdata.get('acquirer_id') or False
                if acquirer_id:
                    payTransferData = create_transaction(acquirer_id)
                    finalResult['transactionId'] = payTransferData['id']
                    if payTransferData:
                        finalResult['transactionId'] = payTransferData.get('id')
                        result = create_checkout_session(payTransferData)
                        if result:
                            finalResult['url'] = result.url
                else:
                    msg = {"message": "Payment Method Is Missing", "status_code": 400}
                    return return_Response_error(msg)
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "result": finalResult, 'status':200
        }
        return return_Response(res)

    # @validate_token
    # @http.route('/api/v1/c/create_checkout_session', type='http', auth='public', methods=['GET'], csrf=False, cors='*',
    #             website=True)
    # def create_checkout_session(self, **params):
    #     try:
    #         checkout_session = {}
    #         base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
    #         try:
    #             jdata = json.loads(request.httprequest.stream.read())
    #         except:
    #             jdata = {}
    #         if jdata:
    #             if 'amount' in jdata and jdata.get('amount'):
    #                 checkout_session = stripe.checkout.Session.create(
    #                     line_items=[
    #                         {
    #                             'price_data':{
    #                                 'currency': jdata.get('currency') or 'usd',
    #                                 'product_data':{
    #                                     'name': jdata.get('reference') or 'Test Product'
    #                                 },
    #                                 'unit_amount': int(jdata.get('amount'))*100,
    #                             },
    #                             'quantity': 1,
    #                         },
    #                     ],
    #                     mode='payment',
    #                     success_url=base_url.value + '/success.html',
    #                     cancel_url=base_url.value + '/cancel.html',
    #                 )
    #         else:
    #             msg = {"message": "Something Went Wrong.", "status_code": 400}
    #             return return_Response_error(msg)
    #         if checkout_session:
    #             res = {
    #                 "redirectUrl": checkout_session.url,"data": checkout_session, 'status': 200
    #             }
    #             return return_Response(res)
    #         else:
    #             msg = {"message": "Something Went Wrong.", "status_code": 400}
    #             return return_Response_error(msg)
    #
    #     except (SyntaxError, QueryFormatError) as e:
    #         return error_response(e, e.msg)
    #     # res = {
    #     #     "message": 'Success', 'status': 200
    #     # }
    #     # return return_Response(res)

    @http.route('/api/v1/c/confirm_order', type='http', auth='public', methods=['POST'], csrf=False, cors='*',
                website=True)
    def confirm_order(self, **params):
        try:
            website = request.env['website'].sudo().browse(1)
            # website = request.website
            partner = request.env.user.partner_id
            order = request.env['sale.order'].sudo().search([('state', '=', 'draft'),
                                                             ('partner_id', '=', partner.id),
                                                             ('website_id', '=', website.id)],
                                                            order='write_date DESC', limit=1)
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                if 'transaction_id' in jdata and jdata.get('transaction_id'):
                    create_invoice(jdata.get('transaction_id'), order)
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        # res = {
        #     "message": 'success', 'status':200
        # }
        # return return_Response(res)

