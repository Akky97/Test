from odoo import http, _, exceptions, SUPERUSER_ID, registry
from odoo.http import request
import datetime
import base64
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED
import odoo
import psycopg2
from .sale_order_list_view import *
_logger = logging.getLogger(__name__)
from .notification_controller import *
import stripe

from web3 import Web3

w = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/fe062e39f4fa40f581182b1de50ad71e'))


def refund_payment_by_metamask(acc1, acc2, pkey, tnx_amount, chain_id):
    res = False
    try:
        if chain_id == '0x3':
            w = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/fe062e39f4fa40f581182b1de50ad71e'))
        #     polygon test net
        if chain_id == '0x13881':
            w = Web3(Web3.HTTPProvider('https://rpc-mumbai.matic.today'))
        #     Main net
        if chain_id == '0x1':
            w = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/fe062e39f4fa40f581182b1de50ad71e'))

        web3 = Web3(Web3.HTTPProvider(w))
        account_1 = acc1
        private_key1 = pkey
        account_2 = acc2
        # get the nonce.  Prevents one from sending the transaction twice
        nonce = web3.eth.getTransactionCount(account_1)
        print(nonce)
        # build a transaction in a dictionary
        tx = {
            'nonce': nonce,
            'to': account_2,
            'value': web3.toWei(tnx_amount, 'ether'),
            'gas': 2000000,
            'gasPrice': web3.toWei('50', 'gwei')
        }
        # sign the transaction
        signed_tx = web3.eth.account.sign_transaction(tx, private_key1)
        # send transaction
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        res = web3.toHex(tx_hash)
        # get transaction hash
        print(res)
    except:
        return res
    return res
def refund_payment(transaction_id, amount):
    stripe_key = request.env['ir.config_parameter'].sudo().search([('key', '=', 'strip_key')], limit=1)
    stripe.api_key = stripe_key.value
    transaction = request.env['payment.transaction'].sudo().search([('id', '=', transaction_id)])
    res = {}
    if transaction:
        res = stripe.PaymentIntent.retrieve(
            transaction.payment_intent,
        )
        if res.status == 'succeeded':
            if not amount:
                amount = int(transaction.amount) * 100
            res = stripe.Refund.create(payment_intent=transaction.payment_intent, amount=amount)
            # res = stripe.Refund.create(payment_intent=transaction.payment_intent)
            print(res)
    return res


def update_transaction_data(transaction_id, from_address, to_address, hash_data, mode, chain_id, usd_price):
    transaction = request.env['payment.transaction'].sudo().search([('id', '=', transaction_id)])
    try:
        wallet = ''
        # Test net
        if chain_id == '0x3':
            wallet = 'Test Net'
            w = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/fe062e39f4fa40f581182b1de50ad71e'))
        #     polygon test net
        if chain_id == '0x13881':
            wallet = 'Polygon'
            w = Web3(Web3.HTTPProvider('https://rpc-mumbai.matic.today'))
        #     Main net
        if chain_id == '0x1':
            wallet = 'Main Net'
            w = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/fe062e39f4fa40f581182b1de50ad71e'))

        if transaction:
            transaction.sudo().write({
                'from_address': from_address,
                'to_address': to_address,
                'hash_data': hash_data,
                'mode': mode,
                'chain_id': chain_id,
                'usd_price': usd_price,
                'wallet': wallet
            })

            txns = w.eth.get_transaction(hash_data)
            if not txns:
                return False
            if txns['value'] == 0:
                return False
            if txns['blockHash'] is None:
                return True
            else:
                data = w.eth.wait_for_transaction_receipt(hash_data)
                if data['status'] == 1:
                    return True
                else:
                    return False
    except Exception as e:
        return False
    return True


def check_transaction_status(transaction_id, device_name=None, mode=None):
    stripe_key = request.env['ir.config_parameter'].sudo().search([('key', '=', 'strip_key')], limit=1)
    stripe.api_key = stripe_key.value
    transaction = request.env['payment.transaction'].sudo().search([('id', '=', transaction_id)])
    if transaction and transaction.payment_intent:
        res = stripe.PaymentIntent.retrieve(
            transaction.payment_intent,
        )
        vals ={'payment_data': res, 'mode': mode}
        if device_name:
            vals['device_name'] = device_name
        transaction.sudo().write(vals)
        if res.status == 'succeeded':
            return True
        else:
            stripe.Refund.create(payment_intent=transaction.payment_intent)
            return False
    return False


def create_checkout_session(jdata):
    stripe_key = request.env['ir.config_parameter'].sudo().search([('key', '=', 'strip_key')], limit=1)
    stripe.api_key = stripe_key.value

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
                customer_email=request.env.user.login,
                mode='payment',
                success_url='https://pandostores.com/shop/success',
                cancel_url='https://pandostores.com/shop/cart',
            )
            if checkout_session and checkout_session.payment_intent and jdata.get('id'):
                transaction = request.env['payment.transaction'].sudo().search([('id', '=', int(jdata.get('id')))])
                transaction.write({
                    'payment_intent':checkout_session.payment_intent
                })

    return checkout_session


def payment_validate(transaction_id,order):
    res = False
    transaction = request.env['payment.transaction'].sudo().search([('id','=',transaction_id)])
    if transaction:
        res = transaction.sudo().write({
            'state': 'done',
            'date': datetime.datetime.now()
        })
        if res:
            res = order.action_confirm()
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
    order = request.env['sale.order'].sudo().search([('in_process', '=', False), ('state', '=', 'draft'),
                                                     ('partner_id', '=', partner.id),
                                                     ('website_id', '=', website.id)],
                                                    order='write_date DESC', limit=1)

    # Ensure there is something to proceed
    if not order or (order and not order.order_line):
        return False
    # Check Product Quantity
    values = {}
    for line in order.order_line:
        if line.product_id.type == 'product':
            cart_qty = sum(
                order.order_line.filtered(lambda p: p.product_id.id == line.product_id.id).mapped('product_uom_qty'))
            avl_qty = line.product_id.with_context(warehouse=order.warehouse_id.id).virtual_available
            if cart_qty > avl_qty:
                available_qty = avl_qty if avl_qty > 0 else 0
                message = f'You ask for {cart_qty} products but only {available_qty} is available'
                values['message'] = message
                return values
    # # Delivery Method Check
    # if not order.is_all_service and not order.delivery_set:
    #     message = 'There is an issue with your delivery method. Please refresh the page and try again.'
    #     values['message'] = message
    #     return message

    assert order.partner_id.id != website.partner_id.id

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


def dispatch_order(order):
    stockPicking = request.env['stock.picking'].sudo().search([('sale_id', '=', order.id)])
    for rec in stockPicking:
        stockMoveLine = request.env['stock.move.line'].sudo().search([('picking_id', '=', rec.id)])
        for res in stockMoveLine:
            res.sudo().write({'qty_done': res.product_uom_qty})
        rec.button_validate()


def create_invoice(transaction_id, order):
    res = payment_validate(transaction_id, order)
    result = dispatch_order(order)
    for line in order.order_line:
        line.sudo().write({'shipping_Details': 'ordered'})
    if res:
        invoice = order._create_invoices(final=True)
        if invoice:
            res = invoice.action_post()
            template = request.env.ref('account.email_template_edi_invoice')
            outgoing_server_name = request.env['ir.mail_server'].sudo().search([], limit=1).name
            template.email_from = outgoing_server_name
            template.sudo().send_mail(invoice.id, force_send=True)



def updatePriceList(pricelist, order):
    msg={}
    if order and pricelist:
        request.session['website_sale_current_pl'] = pricelist
        values = {'pricelist_id': pricelist}
        order.write(values)
        for line in order.order_line:
            if line.exists():
                if line.product_id.is_product_publish and line.product_id.is_published and line.product_id.marketplace_status == 'approved' and line.product_id.type == 'product':
                    order._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=0)
                else:
                    if line.product_id.type == 'product':
                        msg = {"message": f"Product {line.product_id.name} is not Publish or Approve."}
                        return msg
                    else:
                        order._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=0)
    return msg


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


def get_shipping_method():
    result = request.env['delivery.carrier'].sudo().search([('is_published', '=', True)])
    deliveryMethod=[]
    for res in result:
        vals={
            'id':res.id,
            'name':res.name
        }
        deliveryMethod.append(vals)
    return deliveryMethod


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
    sale_order = {
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
        'shipping_method': get_shipping_method(),
        'express': False
    }]
    return values


def create_new_address(params):
    value = {}
    partnerObj = request.env['res.partner'].sudo()
    if all(item in params.keys() for item in ["name", "street", "city", "country_id", "state_id", "zip"]):
        country_id = request.env['res.country'].sudo().search([('id', '=', int(params['country_id']))])
        if country_id:
            if "mobile" in params and "email" in params:
                res = partnerObj.search([('mobile', '=', params['mobile']), ('email', '=', params['email'])])
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
    @http.route('/api/v1/c/update_shipping_method', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def update_shipping_method(self, **params):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                if not jdata.get('delivery_id'):
                    res = {"message": "Something Went Wrong.", "status": 400}
                    return return_Response_error(res)
                website = request.env['website'].sudo().browse(1)
                partner = request.env.user.partner_id
                order_id = request.env['sale.order'].sudo().search([('in_process', '=', False), ('state', '=', 'draft'), ('partner_id', '=', partner.id), ('website_id', '=', website.id)], order='write_date DESC', limit=1)
                if jdata.get('delivery_id'):
                    SaleOrderLine = request.env['sale.order.line']
                    delivery_lines = request.env['sale.order.line'].sudo().search([('order_id', 'in', order_id.ids), ('is_delivery', '=', True)])
                    if delivery_lines:
                        to_delete = delivery_lines.filtered(lambda x: x.qty_invoiced == 0)
                        if not to_delete:
                            res = {"message": ('You can not update the shipping costs on an order where it was already invoiced!\n\nThe following delivery lines (product, invoiced quantity and price) have already been processed:\n\n')
                                + '\n'.join(['- %s: %s x %s' % (
                                line.product_id.with_context(display_default_code=False).display_name, line.qty_invoiced,
                                line.price_unit) for line in delivery_lines]), "status": 400}
                            return return_Response_error(res)
                        to_delete.unlink()

                    delivery_id = request.env['delivery.carrier'].sudo().search([('id', '=', int(jdata.get('delivery_id')))])
                    values = {
                        'order_id': order_id.id,
                        'name': 'Delivery Charges',
                        'product_uom_qty': 1,
                        'product_uom': delivery_id.product_id.uom_id.id,
                        'product_id': delivery_id.product_id.id,
                        # 'tax_id': [(6, 0, taxes_ids)],
                        'is_delivery': True,
                        'price_unit': delivery_id.product_id.list_price
                    }
                    sol = SaleOrderLine.sudo().create(values)
                    r = order_id.sudo().write({
                        'recompute_delivery_price': False,
                        'delivery_message': delivery_id.fixed_price})
                    if r:
                        res = {
                            "message": 'Shipping Method Updated Successfully',
                            "status": 200
                        }
                        return return_Response(res)
            else:
                res = {"message": "Something Went Wrong.", "status": 400}
                return return_Response_error(res)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)

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
            order = request.env['sale.order'].sudo().search([('in_process', '=', False),('state', '=', 'draft'),
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
            "status": 200
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
            order = request.env['sale.order'].sudo().search([('in_process', '=', False),('state', '=', 'draft'),
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
                msg = updatePriceList(pricelist_id, order)
                if msg and 'message' in msg:
                    res = {
                        "message": msg.get('message'), "status": 400
                    }
                    return return_Response_error(res)

            else:
                res = {
                    "message": f"Something Went Wrong. Please Go To {redirectUrl} ","status":400
                }
                return return_Response_error(res)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "redirect": 'success', "status": 200
        }
        return return_Response(res)

    @validate_token
    @http.route(['/api/v1/c/update_shipping_address', '/api/v1/c/update_shipping_address/<id>'], type='http',
                auth='none', methods=['POST'], csrf=False, cors='*')
    def update_shipping_address(self, id=None, **params):
        try:
            if not id:
                error = {"message": "id is not present in the request", "status": 400}
                return return_Response_error(error)
            website = request.env['website'].sudo().browse(1)
            partner = request.env.user.partner_id
            order = request.env['sale.order'].sudo().search([('in_process', '=', False), ('state', '=', 'draft'),
                                                             ('partner_id', '=', partner.id),
                                                             ('website_id', '=', website.id)],
                                                            order='write_date DESC', limit=1)

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
            order = request.env['sale.order'].sudo().search([('in_process', '=', False),('state', '=', 'draft'),
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
                    stripe = []
                    for pa in paymentAcquirer:
                        # if pa.name == 'Stripe':
                        #     val = {
                        #         'id': pa.id,
                        #         'name': pa.name
                        #     }
                        #     stripe.append(val)
                        # else:
                        val = {
                            'id': pa.id,
                            'name': pa.name
                        }
                        payAcquirer.append(val)
                    # if stripe:
                    #     payAcquirer = stripe

                    # End Here
                    # Sale Order Details
                    sale_order = {
                        'id': order.id,
                        'name': order.name if order.name != False else "",
                        'order_line': get_sale_order_line(order_id=order.id),
                        'amount_untaxed': order.amount_untaxed if order.amount_untaxed != False else 0.0,
                        'amount_tax': order.amount_tax if order.amount_tax != False else 0.0,
                        'amount_total': order.amount_total if order.amount_total != False else 0.0,
                        'symbol': order.currency_id.symbol if order.currency_id.symbol != False else ""
                    }
                    # End Here
                    # User Shipping and Billing Details
                    values = {
                        'order': sale_order,
                        'shippingAddress': get_address(order.partner_shipping_id),
                        'invoiceAddress': get_address(order.partner_invoice_id),
                        'payAcquirer': payAcquirer
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
    @http.route('/api/v1/c/pay_now', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def pay_now(self, **params):
        try:
            result={}
            finalResult = {}
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                if not jdata.get('acquirer_id') or not jdata.get('mode'):
                    msg = {"message": "Something Went Wrong", "status_code": 400}
                    return return_Response_error(msg)
                acquirer_id = jdata.get('acquirer_id')
                if acquirer_id:
                    payTransferData = create_transaction(acquirer_id)
                    finalResult['transactionId'] = payTransferData['id']
                    if payTransferData:
                        if 'message' in payTransferData and payTransferData.get('message'):
                            msg = {"message": payTransferData.get('message'), "status_code": 400}
                            return return_Response_error(msg)
                        finalResult['transactionId'] = payTransferData.get('id')
                        if jdata.get('mode') == 'Stripe':
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

    @validate_token
    @http.route('/api/v1/get_transaction_details', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def get_transaction_details(self, **params):
        transaction_id = False
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        try:
            if jdata:
                if not jdata.get('hash_data') or not jdata.get('transaction_id') or not jdata.get('chain_id'):
                    msg = {"message": "Hash is missing from the parameter.", "status_code": 400}
                    return return_Response_error(msg)
            transaction_id = request.env['payment.transaction'].sudo().search([('id', '=', int(jdata.get('transaction_id')))])
            # Test net
            if jdata.get('chain_id') == '0x3':
                w = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/fe062e39f4fa40f581182b1de50ad71e'))
            #     polygon test net
            if jdata.get('chain_id') == '0x13881':
                w = Web3(Web3.HTTPProvider('https://rpc-mumbai.matic.today'))
            #     Main net
            if jdata.get('chain_id') == '0x1':
                w = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/fe062e39f4fa40f581182b1de50ad71e'))

            txns = w.eth.get_transaction(jdata.get('hash_data'))
            if not txns:
                for rec in transaction_id.sale_order_ids:
                    rec.action_cancel()
                msg = {"message": "Transaction Canceled", "status_code": 300}
                return return_Response(msg)
            if txns['value'] == 0:
                for rec in transaction_id.sale_order_ids:
                    rec.action_cancel()
                msg = {"message": "Transaction Canceled", "status_code": 300}
                return return_Response(msg)
            if txns['blockHash'] is None:
                if not transaction_id.state == 'pending':
                    transaction_id.sudo().write({
                        'state': 'pending'
                    })
                msg = {"message": "Pending-Transaction not Confirmed", "status_code": 400}
                return return_Response(msg)
            else:
                data = w.eth.wait_for_transaction_receipt(jdata.get('hash_data'))
                if data['status'] == 1:
                    transaction_id.sudo().write({
                        'state': 'done'
                    })
                    msg = {"message": "Transaction Confirmed", "status_code": 200}
                    return return_Response(msg)
                else:
                    for rec in transaction_id.sale_order_ids:
                        rec.action_cancel()
                    msg = {"message": "Transaction not Confirmed", "status_code": 400}
                    return return_Response(msg)
        except Exception as e:
            if transaction_id:
                for rec in transaction_id.sale_order_ids:
                    rec.action_cancel()
            msg = {"message": "Transaction Canceled", "status_code": 300}
            return return_Response(msg)



    @validate_token
    @http.route('/api/v1/c/confirm_order', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def confirm_order_send_mail(self, **params):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        order = request.env['sale.order'].sudo()
        try:
            check = False
            website = request.env['website'].sudo().browse(1)
            if 'partner_id' in jdata:
                partner = request.env['res.partner'].sudo().search([('id', '=', int(jdata.get('partner_id')))])
            else:
                partner = request.env.user.partner_id
            order = request.env['sale.order'].sudo().search([('in_process', '=', False),('state', '=', 'draft'),
                                                             ('partner_id', '=', partner.id),
                                                             ('website_id', '=', website.id)],
                                                            order='write_date DESC', limit=1)
            if jdata and order:
                if 'transaction_id' in jdata and jdata.get('transaction_id'):
                    device_name = None
                    transaction = request.env['payment.transaction'].sudo().search(
                        [('id', '=', int(jdata.get('transaction_id')))])
                    if 'device_name' in jdata and jdata.get('device_name'):
                        device_name = jdata.get('device_name')
                    if 'mode' in jdata and jdata.get('mode'):
                        if jdata.get('mode') == 'Stripe':
                            check = check_transaction_status(int(jdata.get('transaction_id')),device_name, mode=jdata.get('mode'))
                        if jdata.get('mode') == 'Meta Mask':
                            if not jdata.get('from_address') or not jdata.get('to_address') or not jdata.get('hash_data') or not jdata.get('chain_id') and jdata.get('usd_price'):
                                msg = {"message": "From Add, To Add and hash is missing.", "status_code": 400}
                                return return_Response_error(msg)
                            check = update_transaction_data(int(jdata.get('transaction_id')),jdata.get('from_address'), jdata.get('to_address'), jdata.get('hash_data'), jdata.get('mode'), jdata.get('chain_id'), jdata.get('usd_price'))
                            if transaction.state == 'pending' and check:
                                order.sudo().write({
                                    'in_process': True
                                })
                                res = {"message": 'Success', 'status': 200}
                                return return_Response(res)
                            
                    if check:
                        invoice = create_invoice(int(jdata.get('transaction_id')), order)
                        vendor_message = f"""{order.name} Order Confirmed Successfully"""
                        generate_notification(seller_id=partner.id, vendor_message=vendor_message,
                                              model="sale.order", title="Sale Order Confirmed")

                        user = request.env.user
                        tokenObject = request.env['device.token'].sudo()
                        tokens = tokenObject.search([('user_id', '=', user.id)])
                        if tokens:
                            send_notification("Sale Order Confirmed", vendor_message, user, tokens, None)
                        res = {"payment_method":transaction.acquirer_id.name,"payment_intent": transaction.payment_intent,"message": 'Success', 'status': 200}
                        return return_Response(res)
                    else:
                        msg = {"message": "Something Went Wrong.", "status_code": 400}
                        return return_Response_error(msg)
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        # except (SyntaxError, QueryFormatError) as e:
        #     return error_response(e, e.msg)
        except Exception as e:
            # This is for strip payment only
            res = {}
            if jdata and order:
                if 'transaction_id' in jdata and jdata.get('transaction_id') and order.state == 'draft':
                    res = refund_payment(jdata.get('transaction_id'), amount=None)
            return return_Response_error(res)

    @validate_token
    @http.route('/api/v1/c/return_order', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def return_order(self, **params):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        order = request.env['sale.order'].sudo()
        try:
            if not jdata.get('order_line') or not jdata.get('reason') or not jdata.get('product_uom_qty'):
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
            res = request.env['return.policy'].sudo().search([('order_line', '=', int(jdata.get('order_line'))), ('state', 'in', ['draft', 'picked', 'in-stock'])], limit=1)
            if res:
                msg = {"message": f"One Return Order Is being Process and It's in {res.state} State", "status_code": 400}
                return return_Response_error(msg)

            line = request.env['sale.order.line'].sudo().search([('id', '=', int(jdata.get('order_line')))])
            if line:
                vals = {
                    'order_line': line.id,
                    'order_id': line.order_id.id,
                    'product_id': line.product_id.id,
                    'seller_id': line.product_id.marketplace_seller_id.id,
                    'partner_id': line.order_id.partner_id.id,
                    'reason': jdata.get('reason')
                }
                if int(jdata.get('product_uom_qty')) <= (line.qty_delivered - line.return_qty):
                    vals['product_uom_qty'] = int(jdata.get('product_uom_qty'))
                else:
                    msg = {"message": "Return Qty Must be less then or equal to the dispatched qty", "status_code": 400}
                    return return_Response_error(msg)
                for rec in line.order_id.transaction_ids:
                    if rec.state == 'done':
                        vals['payment_intent'] = rec.payment_intent
                result = request.env['return.policy'].sudo().create(vals)
                if result:
                    res = {
                        "result": 'Return Order Created Successfully', 'status': 200
                    }
                    return return_Response(res)
                else:
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)


    @validate_token
    @http.route('/api/v1/v/update_return_order', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def update_return_order(self, **params):
        stripe_key = request.env['ir.config_parameter'].sudo().search([('key', '=', 'strip_key')], limit=1)
        stripe.api_key = stripe_key.value

        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        try:
            if not jdata.get('return_id') or not jdata.get('state'):
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
            return_order = request.env['return.policy'].sudo().search([('id', '=', int(jdata.get('return_id')))])
            if return_order:
                if jdata.get('state') == 'picking':
                    return_order.confirm()
                if jdata.get('state') == 'cancel':
                    return_order.cancel()
                if jdata.get('state') == 'in-stock':
                    return_order.update_stock()
                if jdata.get('state') == 'refund':
                    if return_order.order_id.transaction_ids and not return_order.payment_intent:
                        for rec in return_order.order_id.transaction_ids:
                            if not jdata.get('pkey'):
                                msg = {"message": "Need Primary Key For Transaction", "status_code": 400}
                                return return_Response_error(msg)
                            pkey = jdata.get('pkey')
                            acc1 = rec.to_address
                            acc2 = rec.from_address
                            if rec.acquirer_id.name == 'Meta Mask':
                                tnx_amount = (1/rec.usd_price)*(return_order.product_uom_qty * return_order.order_line.price_unit)
                                tnx_amount = tnx_amount * 1000000000000000000
                                data = refund_payment_by_metamask(acc1, acc2, pkey, tnx_amount, rec.chain_id)
                                if data:
                                    return_order.refund()
                                    return_order.payment_info = data
                                    res = {
                                        "result": 'Refund Successfully Created', 'status': 200
                                    }
                                    return return_Response(res)
                                else:
                                    msg = {"message": "Something Went Wrong", "status_code": 400}
                                    return return_Response_error(msg)
                    if return_order.payment_intent:
                        res = stripe.PaymentIntent.retrieve(
                            return_order.payment_intent,
                        )
                        if res.status == 'succeeded':
                            amount = int(return_order.order_line.price_unit * return_order.product_uom_qty) * 100
                            result = stripe.Refund.create(payment_intent=return_order.payment_intent, amount=amount)
                            if result.status == 'succeeded':
                                return_order.refund()
                                return_order.payment_info = result
                                res = {
                                    "result": 'Refund Successfully Created', 'status': 200
                                }
                                return return_Response(res)
                            else:
                                msg = {"message": "Something Went Wrong", "status_code": 400}
                                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "result": 'Success', 'status': 200
        }
        return return_Response(res)

    @validate_token
    @http.route(['/api/v1/v/get_return_order', '/api/v1/v/get_return_order/<id>'], type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def get_return_order(self, id=None, **params):
        temp = []
        try:
            domain = [('seller_id', '=', request.env.user.partner_id.id)]
            if id:
                domain.append(('id', '=', int(id)))
            if "state" in params and params.get('state'):
                domain.append(('state', '=', params.get('state')))
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata and jdata.get('from_date') and jdata.get('to_date'):
                domain.append(('create_date', '>=', jdata.get('from_date')))
                domain.append(('create_date', '<=', jdata.get('to_date')))

            limit = 0
            offset = 0
            if "page" in params and params.get('page'):
                limit = 5
                page = int(params["page"])
                offset = (page - 1) * 5

            record_count = request.env['return.policy'].sudo().search_count(domain)
            return_order = request.env['return.policy'].sudo().search(domain, order='id DESC', limit=limit, offset=offset)
            if return_order:
                for rec in return_order:
                    result = request.env['pando.images'].sudo().search([('product_id', '=', rec.product_id.id)])
                    if not result:
                        result = request.env['pando.images'].sudo().search(
                            [('product_id.product_tmpl_id', '=', rec.product_id.product_tmpl_id.id)])
                    base_image = ''
                    for j in result:
                        if j.type != 'multi_image':
                            base_image = j.image_url
                    temp.append({
                        'id': rec.id,
                        'order_line': rec.order_line.id,
                        'order_line_name': rec.order_line.name,
                        'order_id': rec.order_id.id,
                        'order_name': rec.order_id.name,
                        'product_id': rec.product_id.id,
                        'product_name': rec.product_id.name,
                        'product_image': base_image,
                        'partner_id': rec.partner_id.id,
                        'partner_name': rec.partner_id.name,
                        'reason': rec.reason,
                        'qty': rec.product_uom_qty,
                        'status': rec.state
                    })
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "isSuccess": True,
            "total_count": record_count,
            "record": temp, "count": len(temp), 'status': 200
        }
        return return_Response(res)

    @validate_token
    @http.route(['/api/v1/c/get_return_order', '/api/v1/c/get_return_order/<id>'], type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_own_return_order(self, id=None, **params):
        temp = []
        try:
            domain = [('partner_id', '=', request.env.user.partner_id.id)]
            if id:
                domain = [('id', '=', int(id))]
            limit = 0
            offset = 0
            if "page" in params and params.get('page'):
                limit = 5
                page = int(params["page"])
                offset = (page - 1) * 5
            record_count = request.env['return.policy'].sudo().search_count(domain)
            return_order = request.env['return.policy'].sudo().search(domain, order='id DESC', limit=limit, offset=offset)
            if return_order:
                for rec in return_order:
                    result = request.env['pando.images'].sudo().search([('product_id', '=', rec.product_id.id)])
                    if not result:
                        result = request.env['pando.images'].sudo().search(
                            [('product_id.product_tmpl_id', '=', rec.product_id.product_tmpl_id.id)])
                    base_image = ''
                    for j in result:
                        if j.type != 'multi_image':
                            base_image = j.image_url
                    temp.append({
                        'id': rec.id,
                        'order_line': rec.order_line.id,
                        'order_line_name': rec.order_line.name,
                        'order_id': rec.order_id.id,
                        'order_name': rec.order_id.name,
                        'product_id': rec.product_id.id,
                        'product_name': rec.product_id.name,
                        'product_image': base_image,
                        'partner_id': rec.partner_id.id,
                        'partner_name': rec.partner_id.name,
                        'reason': rec.reason,
                        'qty': rec.product_uom_qty,
                        'status': rec.state
                    })
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "isSuccess": True,
            "total_count": record_count,
            "record": temp, "count": len(temp), 'status': 200
        }
        return return_Response(res)

    @validate_token
    @http.route(['/api/v1/c/transaction_list/<order_id>'], type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def transaction_list(self, order_id=None, **params):
        temp = []
        try:
            if not id:
                msg = {"message": "OrderId is missing from parameter", "status_code": 400}
                return return_Response_error(msg)
            domain = [('sale_order_ids', '=', int(order_id))]
            return_order = request.env['payment.transaction'].sudo().search(domain, order='id DESC')
            if return_order:
                for rec in return_order:
                    temp.append({
                        'id': rec.id,
                        'amount': rec.amount,
                        'state': rec.state,
                        'payment_method_id': rec.acquirer_id.id,
                        'payment_mode': rec.acquirer_id.name,
                        'from_address': rec.from_address,
                        'to_address': rec.to_address,
                        'hash_data': rec.hash_data,
                        'payment_intent': rec.payment_intent
                    })
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "isSuccess": True,
            "record": temp, "count": len(temp), 'status': 200
        }
        return return_Response(res)
