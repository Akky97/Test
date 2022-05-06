import logging
import uuid
import phonenumbers
from odoo import http, _, exceptions, SUPERUSER_ID
from odoo.http import request
from .exceptions import QueryFormatError
from .error_or_response_parser import *
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal

from .notification_controller import *
_logger = logging.getLogger(__name__)

def check_product_availablity(order, product_id, qty):
    avQty = 0
    message = False
    orderLine = request.env['sale.order.line'].sudo().search([('product_id','=',int(product_id)),('order_id','=',order.id)])
    if orderLine and orderLine.product_id.type == 'product':
        cart_qty = int(orderLine.product_uom_qty) + int(qty)
        avl_qty = orderLine.product_id.with_context(warehouse=order.warehouse_id.id).virtual_available
        if cart_qty > avl_qty:
            available_qty = avl_qty if avl_qty > 0 else 0
            message = f'You ask for {cart_qty} products but only {available_qty} is available'
    else:
        product_id = request.env['product.product'].sudo().search([('id','=',int(product_id))])

        if product_id.type == 'product':
            virtual_qty = product_id.with_context(warehouse=order.warehouse_id.id).virtual_available
            if qty > virtual_qty:
                avQty = virtual_qty - qty
            if avQty < 0:
                message = f'You ask for {qty} products but only {virtual_qty} is available'
    return message

def get_sale_order_line(order_id=None, order_line_id = None):
    saleOrderLine = []
    count = 0
    solObject = request.env['sale.order.line'].sudo()
    if order_id:
        solObject = solObject.search([('order_id','=',order_id)])
    if order_line_id:
        solObject = solObject.search([('order_id','=',order_id)])
    if solObject:
        base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
        website = request.env['website'].sudo().browse(1)
        warehouse = request.env['stock.warehouse'].sudo().search(
            [('company_id', '=', website.company_id.id)], limit=1)
        for rec in solObject:
            image = []
            category = []
            variant = []
            sellers = []
            imagerec = request.env['pando.images'].sudo().search([('product_id', '=', rec.product_id.id)])
            if not imagerec:
                imagerec = request.env['pando.images'].sudo().search(
                    [('product_id.product_tmpl_id', '=', rec.product_id.product_tmpl_id.id)])
            base_image = {}
            for j in imagerec:
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

            for z in rec.product_id.public_categ_ids:
                category.append({"id": z.id, "name": z.name, "slug": z.name.lower().replace(" ", "-"),
                                 "image": base_url.value + '/web/image/product.public.category/' + str(
                                     z.id) + "/image_1920", })
            product_var = request.env['product.product'].sudo().search([('id', '=', int(rec.product_id.id))])
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
                            "pivot": {"product_id": rec.id, "component_id": k.id}}

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

            for n in rec.product_id.seller_ids:
                sellers.append({"id": n.id, "vendor": n.name.name, "vendor_id": n.name.id})
            saleOrderLine.append({
                'id': rec.id if rec.id != False else "",
                'name': rec.name if rec.name != False else "",
                'product_id': rec.product_id.id if rec.product_id.id != False else "",
                'product_name': rec.product_id.name if rec.product_id.name != False else "",
                'price_unit': rec.price_unit if rec.price_unit != False else 0.0,
                'price_subtotal': rec.price_subtotal if rec.price_subtotal != False else 0.0,
                'price_tax': rec.price_tax if rec.price_tax != False else 0.0,
                'price_total': rec.price_total if rec.price_total != False else 0.0,
                'tax_id': [{i.id:i.name} for i in rec.tax_id],
                'quantity': rec.product_uom_qty if rec.product_uom_qty != False else 0.0,
                'qty_delivered': rec.qty_delivered if rec.qty_delivered != False else 0.0,
                'qty_invoiced': rec.qty_invoiced if rec.qty_invoiced != False else 0.0,
                # "image": base_url.value + '/web/image/product.product/' + str(rec.product_id.id) + "/image_1920",
                'image': base_image.get('image_url') if 'image_url' in base_image else "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/330px-No-Image-Placeholder.svg.png?20200912122019",
                "sm_pictures": image,
                "featured": rec.product_id.website_ribbon_id.html if rec.product_id.website_ribbon_id.html != False else '',
                "seller_ids": sellers,
                "slug": rec.id,
                "top": True if rec.product_id.website_ribbon_id.html == 'Trending' else False,
                "new": True if rec.product_id.website_ribbon_id.html == 'New' else False,
                "author": "Pando-Stores",
                "sold": rec.product_id.sales_count,
                "category": category,
                "create_uid": rec.create_uid.id if rec.create_uid.id != False else '',
                "create_name": rec.create_uid.name if rec.create_uid.name != False else '',
                "write_uid": rec.write_uid.id if rec.write_uid.id != False else '',
                "write_name": rec.write_uid.name if rec.write_uid.name != False else '',
                "variants": variant,
                # "stock": rec.product_id.qty_available,
                "stock": rec.product_id.with_context(warehouse=warehouse.id).virtual_available if rec.product_id.with_context(
                    warehouse=warehouse.id).virtual_available > 0 else 0.0,
                'type': rec.product_id.type, 'sale_price': rec.product_id.list_price, "price": rec.product_id.standard_price,
                'description': rec.product_id.description if rec.product_id.description != False else '',
                'short_desc': rec.product_id.description_sale if rec.product_id.description_sale != False else '',
                'categ_id': rec.product_id.categ_id.id if rec.product_id.categ_id.id != False else '',
                'categ_name':rec.product_id.categ_id.name if rec.product_id.categ_id.name != False else '',
                "additional_info": rec.product_id.additional_info if rec.product_id.additional_info else '',
                "shipping_return": rec.product_id.shipping_return if rec.product_id.shipping_return else '',
            })
            count += rec.product_uom_qty
        request.session['count'] = count
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


def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False, partner_id=False, website=False):
        """ Return the current sales order after mofications specified by params.
        :param bool force_create: Create sales order if not already existing
        :param str code: Code to force a pricelist (promo code)
                         If empty, it's a special case to reset the pricelist with the first available else the default.
        :param bool update_pricelist: Force to recompute all the lines from sales order to adapt the price with the current pricelist.
        :param int force_pricelist: pricelist_id - if set,  we change the pricelist with this one
        :returns: browse record for the current sales order
        """
        # self.ensure_one()
        # partner = self.env.user.partner_id
        partner = request.env['res.partner'].sudo().search([('id', '=', partner_id)])
        order = request.env['sale.order'].sudo().search([('state', '=', 'draft'),
                                                         ('partner_id', '=', partner.id),
                                                         ('website_id', '=', website)],
                                                        order='write_date DESC', limit=1)
        request.session['sale_order_id'] = order.id
        sale_order_id = request.session.get('sale_order_id')
        check_fpos = False
        if not sale_order_id and not self.env.user._is_public():
            last_order = partner.last_website_so_id
            if last_order:
                available_pricelists = self.get_pricelist_available()
                # Do not reload the cart of this user last visit if the cart uses a pricelist no longer available.
                sale_order_id = last_order.pricelist_id in available_pricelists and last_order.id
                check_fpos = True

        # Test validity of the sale_order_id
        sale_order = self.env['sale.order'].with_company(request.website.company_id.id).sudo().browse(sale_order_id).exists() if sale_order_id else None

        # Do not reload the cart of this user last visit if the Fiscal Position has changed.
        if check_fpos and sale_order:
            fpos_id = (
                self.env['account.fiscal.position'].sudo()
                .with_company(sale_order.company_id.id)
                .get_fiscal_position(sale_order.partner_id.id, delivery_id=sale_order.partner_shipping_id.id)
            ).id
            if sale_order.fiscal_position_id.id != fpos_id:
                sale_order = None

        if not (sale_order or force_create or code):
            if request.session.get('sale_order_id'):
                request.session['sale_order_id'] = None
            return self.env['sale.order']

        if self.env['product.pricelist'].browse(force_pricelist).exists():
            pricelist_id = force_pricelist
            request.session['website_sale_current_pl'] = pricelist_id
            update_pricelist = True
        else:
            pricelist_id = request.session.get('website_sale_current_pl') or self.get_current_pricelist().id

        if not self._context.get('pricelist'):
            self = self.with_context(pricelist=pricelist_id)

        # cart creation was requested (either explicitly or to configure a promo code)
        if not sale_order:
            # TODO cache partner_id session
            pricelist = self.env['product.pricelist'].browse(pricelist_id).sudo()
            so_data = self._prepare_sale_order_values(partner, pricelist)
            sale_order = self.env['sale.order'].with_company(request.website.company_id.id).with_user(SUPERUSER_ID).create(so_data)

            # set fiscal position
            if request.website.partner_id.id != partner.id:
                sale_order.onchange_partner_shipping_id()
            else: # For public user, fiscal position based on geolocation
                country_code = request.session['geoip'].get('country_code')
                if country_code:
                    country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1).id
                    sale_order.fiscal_position_id = request.env['account.fiscal.position'].sudo().with_company(request.website.company_id.id)._get_fpos_by_region(country_id)
                else:
                    # if no geolocation, use the public user fp
                    sale_order.onchange_partner_shipping_id()

            request.session['sale_order_id'] = sale_order.id

        # case when user emptied the cart
        if not request.session.get('sale_order_id'):
            request.session['sale_order_id'] = sale_order.id

        # check for change of pricelist with a coupon
        pricelist_id = pricelist_id or partner.property_product_pricelist.id

        # check for change of partner_id ie after signup
        if sale_order.partner_id.id != partner.id and request.website.partner_id.id != partner.id:
            flag_pricelist = False
            if pricelist_id != sale_order.pricelist_id.id:
                flag_pricelist = True
            fiscal_position = sale_order.fiscal_position_id.id

            # change the partner, and trigger the onchange
            sale_order.write({'partner_id': partner.id})
            sale_order.with_context(not_self_saleperson=True).onchange_partner_id()
            sale_order.write({'partner_invoice_id': partner.id})
            sale_order.onchange_partner_shipping_id() # fiscal position
            sale_order['payment_term_id'] = self.sale_get_payment_term(partner)

            # check the pricelist : update it if the pricelist is not the 'forced' one
            values = {}
            if sale_order.pricelist_id:
                if sale_order.pricelist_id.id != pricelist_id:
                    values['pricelist_id'] = pricelist_id
                    update_pricelist = True

            # if fiscal position, update the order lines taxes
            if sale_order.fiscal_position_id:
                sale_order._compute_tax_id()

            # if values, then make the SO update
            if values:
                sale_order.write(values)

            # check if the fiscal position has changed with the partner_id update
            recent_fiscal_position = sale_order.fiscal_position_id.id
            # when buying a free product with public user and trying to log in, SO state is not draft
            if (flag_pricelist or recent_fiscal_position != fiscal_position) and sale_order.state == 'draft':
                update_pricelist = True

        if code and code != sale_order.pricelist_id.code:
            code_pricelist = self.env['product.pricelist'].sudo().search([('code', '=', code)], limit=1)
            if code_pricelist:
                pricelist_id = code_pricelist.id
                update_pricelist = True
        elif code is not None and sale_order.pricelist_id.code and code != sale_order.pricelist_id.code:
            # code is not None when user removes code and click on "Apply"
            pricelist_id = partner.property_product_pricelist.id
            update_pricelist = True

        # update the pricelist
        if update_pricelist:
            request.session['website_sale_current_pl'] = pricelist_id
            values = {'pricelist_id': pricelist_id}
            sale_order.write(values)
            for line in sale_order.order_line:
                if line.exists():
                    sale_order._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=0)

        return sale_order


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


class SaleOrderController(http.Controller):

    @validate_token
    @http.route('/api/v1/c/sale_order_details/<order_id>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def sale_order_details(self, order_id=None, **params):
        model = 'sale.order'
        value = {}
        try:
            if not order_id:
                error = {"message": "order id is not present in the request", "status": 400}
                return return_Response_error(error)
            records = request.env[model].sudo().search([('id', '=', int(order_id))], limit=1)
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        try:
            if records:
                base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
                url =''
                if records.invoice_ids:
                    if not records.invoice_ids[0].access_token:
                        records.invoice_ids[0].sudo().write({'access_token': str(uuid.uuid4())})
                    url = base_url.value +'/my/invoices/'+str(records.invoice_ids[0].id)+'?access_token='+records.invoice_ids[0].access_token+'&report_type=pdf&download=true'

                value = {
                    'id': records.id,
                    'name': records.name if records.name != False else "",
                    'order_line': get_sale_order_line(order_id=records.id),
                    'partner_id': get_address(records.partner_id),
                    'partner_shipping_id': get_address(records.partner_shipping_id),
                    'date_order': str(records.date_order) if str(records.date_order) != False else "",
                    'state': records.state if records.state != False else "",
                    'amount_untaxed': records.amount_untaxed if records.amount_untaxed != False else 0.0,
                    'amount_tax': records.amount_tax if records.amount_tax != False else 0.0,
                    'amount_total': records.amount_total if records.amount_total != False else 0.0,
                    'invoice_status': records.invoice_status if records.invoice_status != False else "",
                    'url': url,
                    'symbol': records.currency_id.symbol if records.currency_id.symbol != False else "",
                }
            else:
                error = {"message": "Order List Is Empty", "status": 400}
                return return_Response_error(error)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "result": value,
            "status":200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/sale_orders/<partner_id>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def sale_order_list_view(self, partner_id=None, **params):
        model = 'sale.order'
        try:
            if not partner_id:
                error = {"message": "Partner id is not present in the request", "status": 400}
                return return_Response_error(error)
            records = request.env[model].sudo().search([('partner_id', '=', int(partner_id))])
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        try:
            sale_order_data = []
            for i in records:
                base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
                url = ''
                if i.invoice_ids:
                    if not i.invoice_ids[0].access_token:
                        i.invoice_ids[0].sudo().write({'access_token': str(uuid.uuid4())})
                    url = base_url.value + '/my/invoices/' + str(i.invoice_ids[0].id) + '?access_token=' + \
                      i.invoice_ids[0].access_token + '&report_type=pdf&download=true'
                from datetime import datetime, timedelta
                complaint_date_validity = i.date_order.date() + timedelta(7)
                check_date = True if complaint_date_validity >= datetime.now().date() else False
                value = {
                    'id': i.id,
                    'name': i.name if i.name != False else "",
                    'date_order': str(i.date_order) if str(i.date_order) != False else "",
                    'state': i.state if i.state != False else "",
                    'amount_total': i.amount_total if i.amount_total != False else 0.0,
                    'invoice_status': i.invoice_status if i.invoice_status != False else "",
                    'url': url,
                    'symbol': i.currency_id.symbol if i.currency_id.symbol != False else "",
                    'complaint_date_validity': str(complaint_date_validity),
                    'check_validity': check_date
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
    @http.route('/api/v1/c/get_cart', type='http', auth='public', methods=['GET'], csrf=False, cors='*',
                website=True)
    def get_cart(self, **params):
        try:
            sale_order = []
            website = request.website
            partner = request.env.user.partner_id
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
                    'count': request.session.get('count') or 0
                })
            else:
                message = {"message": "Cart is Empty", "status": 200}
                return return_Response(message)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {"result": sale_order}
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/cart_update', type='http', auth='public', methods=['POST'], csrf=False, cors='*', website=True)
    def cart_update(self, **params):
        try:
            website = request.env['website'].sudo().browse(1)
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata={}
            if jdata:
                if not jdata.get('product_id') or not jdata.get('add_qty'):
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)
                product_id = int(jdata.get('product_id')) or False
                set_qty = int(jdata.get('set_qty')) if jdata.get('set_qty') else 0
                add_qty = int(jdata.get('add_qty')) if jdata.get('add_qty') else 1
                sale_order = sale_get_order(self=website, partner_id=request.env.user.partner_id.id, website=website.id)
                if sale_order.state != 'draft':
                    request.session['sale_order_id'] = None
                    sale_order = sale_get_order(self=website, partner_id=request.env.user.partner_id.id, force_create=True, website=website.id)
                    vals = {
                        "seller_id": request.env.user.partner_id.id,
                        "vendor_message": f"""Customer Place an Order""",
                        "model": "sale.order",
                        "title": "Sale Order Created"
                    }
                    request.env['notification.center'].sudo().create(vals)
                    user = request.env.user
                    deviceToken = user.deviceToken
                    if deviceToken:
                        deviceToken = user.deviceToken.split()
                        deviceToken = set(deviceToken)
                        send_notification(vals['title'], vals['vendor_message'], user, deviceToken, None)

                if product_id:
                    if set_qty > 0:
                        qty = set_qty
                    else:
                        qty = add_qty
                    if qty and set_qty != -1:
                        stockMessage = check_product_availablity(sale_order,product_id,qty)
                        if stockMessage:
                            error = {"message": stockMessage, "status": 400}
                            return return_Response_error(error)

                    sale_order._cart_update(
                        product_id=int(product_id),
                        add_qty=add_qty,
                        set_qty=set_qty,
                        product_custom_attribute_values=None,
                        no_variant_attribute_values=None
                    )
            else:
                error = {"message": "Parameters Should not Empty", "status": 400}
                return return_Response_error(error)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {"result": 'Updated Cart Successfully', "status": 200}
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
            count = 0
            if not records:
                values = {
                    'partner_id': partner_id,
                    'product_id': product_id.id,
                    'pricelist_id': pricelist_id.id,
                    'price': product_id.product_tmpl_id.list_price,
                    'website_id': website_id.id
                }
                request.env['product.wishlist'].sudo().create(values)
                count = request.env['product.wishlist'].sudo().search_count([('partner_id', '=', partner_id)])
            else:
                error = {"message": "The Selected Product is in wishlist", "status": 200}
                return return_Response(error)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "message": 'Product Added Successfully', 'count': count, 'status': 200
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
            if records:
                for rec in records:
                    i = request.env['product.product'].sudo().search([('id', '=', rec.product_id.id)])
                    image = []
                    category = []
                    variant = []
                    sellers = []
                    imagerec = request.env['pando.images'].sudo().search([('product_id', '=', i.id)])
                    if not imagerec:
                        imagerec = request.env['pando.images'].sudo().search(
                            [('product_id.product_tmpl_id', '=', i.product_tmpl_id.id)])
                    base_image = {}
                    for j in imagerec:
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
                                 "write_uid": i.write_uid.id if i.write_uid.id != False else '',
                                 "write_name": i.write_uid.name if i.write_uid.name != False else '',
                                 "variants": variant,
                                 # "stock": i.qty_available,
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
                                 "pictures": [{
                                    'url': base_image.get('image_url') if 'image_url' in base_image else "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/330px-No-Image-Placeholder.svg.png?20200912122019" ,
                                    'image': base_image.get('image_url') if 'image_url' in base_image else "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/330px-No-Image-Placeholder.svg.png?20200912122019" }]
                                })

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "result": temp
        }
        return return_Response(res)

    @validate_token
    @http.route(['/api/v1/c/add_shipping_address'], type='http', auth='public', methods=['POST'], csrf=False, cors='*',
                website=True)
    def add_shipping_address(self, **params):
        try:
            dict = {}
            website = request.website
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
                if not jdata.get('name') or not jdata.get('street') or not jdata.get('city') or not jdata.get(
                        'country_id') or not jdata.get('state_id') or not jdata.get('zip'):
                    msg = {"message": "Some Required Fields are Empty.", "status_code": 200}
                    return return_Response(msg)
                dict['name'] = jdata.get('name') or ''
                dict['email'] = jdata.get('email') or ''
                dict['mobile'] = jdata.get('mobile') or ''
                dict['street'] = jdata.get('street') or ''
                dict['street2'] = jdata.get('street2') or ''
                dict['city'] = jdata.get('city') or ''
                if 'state_id' in jdata and jdata.get('state_id'):
                    dict['state_id'] = int(jdata.get('state_id'))
                if 'country_id' in jdata and jdata.get('country_id'):
                    dict['country_id'] = int(jdata.get('country_id'))
                dict['zip'] = jdata.get('zip')
                dict['type'] = jdata.get('type') or 'delivery'
            else:
                res = {
                    "message": "Parameter's are Empty.", "status": 400
                }
                return return_Response_error(res)

            if order:
                if order.partner_id.id != request.website.user_id.sudo().partner_id.id:
                    dict['parent_id'] = order.partner_id.id
                    rec = create_new_address(dict)
                    if 'id' in rec:
                        order.sudo().write({'partner_shipping_id': rec['id']})
                    if 'message' in rec:
                        vals = {
                            "seller_id": request.env.user.partner_id.id,
                            "vendor_message": """Your Address Created Successfully""",
                            "model": "res.partner",
                            "title": "Address"
                        }
                        request.env['notification.center'].sudo().create(vals)
                        message = {"message": rec['message'], "status": 200}
                        return return_Response(message)
                else:
                    res = {
                        "message": "Please Login First.", "status": 400
                    }
                    return return_Response_error(res)

            else:
                res = {
                    "message": "something Went Wrong.", "status": 400
                }
                return return_Response_error(res)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "message": 'New Address Created Successfully', 'status': 200
        }
        return return_Response(res)

    @validate_token
    @http.route(['/api/v1/c/add_address'], type='http', auth='public', methods=['POST'], csrf=False, cors='*',
                website=True)
    def add_address(self, **params):
        try:
            dict = {}
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                if not jdata.get('name') or not jdata.get('street') or not jdata.get('city') or not jdata.get(
                        'country_id') or not jdata.get('state_id') or not jdata.get('zip'):
                    msg = {"message": "Some Required Fields are Empty.", "status_code": 200}
                    return return_Response(msg)
                dict['name'] = jdata.get('name') or ''
                dict['email'] = jdata.get('email') or ''
                dict['mobile'] = jdata.get('mobile') or ''
                dict['street'] = jdata.get('street') or ''
                dict['street2'] = jdata.get('street2') or ''
                dict['city'] = jdata.get('city') or ''
                if 'state_id' in jdata and jdata.get('state_id'):
                    dict['state_id'] = int(jdata.get('state_id'))
                if 'country_id' in jdata and jdata.get('country_id'):
                    dict['country_id'] = int(jdata.get('country_id'))
                dict['zip'] = jdata.get('zip')
                dict['type'] = jdata.get('type') or 'delivery'

                if request.env.user.partner_id.id != request.website.user_id.sudo().partner_id.id:
                    dict['parent_id'] = request.env.user.partner_id.id
                    rec = create_new_address(dict)
                    if 'message' in rec:
                        vals = {
                            "seller_id": request.env.user.partner_id.id,
                            "vendor_message": """Your Address Created Successfully""",
                            "model": "res.partner",
                            "title": "Address"
                        }
                        request.env['notification.center'].sudo().create(vals)
                        message = {"message": rec['message'], "status": 200}
                        return return_Response(message)
                else:
                    res = {
                        "message": "Please Login First.", "status": 400
                    }
                    return return_Response_error(res)

            else:
                res = {
                    "message": "Parameter's are Empty.", "status": 400
                }
                return return_Response_error(res)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "message": 'New Address Created Successfully', 'status': 200
        }
        return return_Response(res)


class CustomerPortal(CustomerPortal):
    @validate_token
    @http.route('/api/v1/c/print_invoice_report/<id>', type='http', auth='public', methods=['GET'], csrf=False, cors='*',
                website=True)
    def print_invoice_report(self, id=None, **params):
        try:
            if not id:
                error = {"message": "Order id is not present in the request", "status": 400}
                return return_Response_error(error)
            order = request.env['sale.order'].sudo().browse(int(id))
            if order and order.invoice_ids:
                return self._show_report(model=order.invoice_ids[0], report_type='pdf', report_ref='account.account_invoices',
                                     download=True)
            else:
                res = {
                    "message": "No Data Found.", "status": 400
                }
                return return_Response_error(res)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)

