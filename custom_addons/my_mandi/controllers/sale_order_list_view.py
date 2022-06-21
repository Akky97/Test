import logging
import uuid
import phonenumbers
from odoo import http, _, exceptions, SUPERUSER_ID
from odoo.http import request
from .exceptions import QueryFormatError
from .error_or_response_parser import *
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)


def check_product_availablity(order, product_id, qty, temp):
    avQty = 0
    message = False
    orderLine = request.env['sale.order.line'].sudo().search([('product_id', '=', int(product_id)), ('order_id', '=', order.id)])
    if orderLine and orderLine.product_id.type == 'product' and not temp:
        cart_qty = int(orderLine.product_uom_qty) + int(qty)
        avl_qty = orderLine.product_id.with_context(warehouse=order.warehouse_id.id).virtual_available
        if cart_qty > avl_qty:
            available_qty = avl_qty if avl_qty > 0 else 0
            message = f'You ask for {cart_qty} products but only {available_qty} is available'
    else:
        product_id = request.env['product.product'].sudo().search([('id', '=', int(product_id))])
        if product_id.type == 'product':
            virtual_qty = product_id.with_context(warehouse=order.warehouse_id.id).virtual_available
            if qty > virtual_qty:
                avQty = virtual_qty - qty
            if avQty < 0:
                message = f'You ask for {qty} products but only {virtual_qty} is available'
    return message


def get_sale_order_line(order_id=None):
    s3_image = request.env['ir.config_parameter'].sudo().search([('key', '=', 'product_image')], limit=1)
    saleOrderLine = []
    count = 0
    solObject = request.env['sale.order.line'].sudo()
    if order_id:
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
                variant_name = ''
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
                            variant_name += '(' + b.name + ')'
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
                'product_name': rec.product_id.name+variant_name if rec.product_id.name != False else "",
                'price_unit': rec.price_unit if rec.price_unit != False else 0.0,
                'price_subtotal': rec.price_subtotal if rec.price_subtotal != False else 0.0,
                'price_tax': rec.price_tax if rec.price_tax != False else 0.0,
                'price_total': rec.price_total if rec.price_total != False else 0.0,
                'tax_id': [{i.id:i.name} for i in rec.tax_id],
                'quantity': rec.product_uom_qty if rec.product_uom_qty != False else 0.0,
                'qty_delivered': rec.qty_delivered if rec.qty_delivered != False else 0.0,
                'qty_invoiced': rec.qty_invoiced if rec.qty_invoiced != False else 0.0,
                # "image": base_url.value + '/web/image/product.product/' + str(rec.product_id.id) + "/image_1920",
                'image': base_image.get('image_url') if 'image_url' in base_image else s3_image.value,
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
                "shipping_status": rec.shipping_Details if rec.shipping_Details else '',
                "return_state": rec.return_state if rec.return_state else ''
            })
            count += rec.product_uom_qty
        request.session['count'] = count
    return saleOrderLine



def get_address(id):
    address ={}
    if id:
        base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
        if id.is_image_remove:
            image = 'https://pandomall.s3.ap-southeast-1.amazonaws.com/1654085542image_1920.png'
        else:
            image = base_url.value + '/web/image/res.partner/' + str(id.id) + "/image_1920"

        res_id = request.env['ir.attachment'].sudo()
        res_id = res_id.sudo().search([('res_model', '=', 'res.partner'),
                                       ('res_field', '=', 'image_1920'),
                                       ('res_id', 'in', [id])])
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
                          "image": image,

                   }
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
        order = request.env['sale.order'].sudo().search([('in_process', '=', False), ('state', '=', 'draft'),
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


class WebsiteSale(WebsiteSale):
    @validate_token
    @http.route('/api/v1/c/get_cart', type='http', auth='public', methods=['GET'], csrf=False, cors='*',
                website=True)
    def get_cart(self, **params):
        try:
            sale_order = []
            website = request.website
            partner = request.env.user.partner_id
            order = request.env['sale.order'].sudo().search([('in_process', '=', False),('state', '=', 'draft'),
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
        res = {"isSucess": True,"result": sale_order}
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/cart_update', type='http', auth='public', methods=['POST'], csrf=False, cors='*', website=True)
    def cart_update(self, **params):
        try:
            website = request.env['website'].sudo().browse(1)
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
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
                if product_id:
                    if set_qty > 0:
                        qty = set_qty
                        temp = True
                    else:
                        qty = add_qty
                        temp = False
                    if qty and set_qty != -1:
                        stockMessage = check_product_availablity(sale_order, product_id, qty, temp)
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
        except Exception as e:
            msg = {"message": "Something Went Wrong.", "status_code": 400}
            return return_Response_error(msg)

        res = {"isSucess": True, "message": 'Updated Cart Successfully', "status": 200}
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/partially_confirm_sale_order', type='http', auth='public', methods=['POST'], csrf=False, cors='*', website=True)
    def partially_confirm_sale_order(self, **params):
        try:
            website = request.website
            partner = request.env.user.partner_id
            order = request.env['sale.order'].sudo().search([('in_process', '=', False), ('state', '=', 'draft'),
                                                             ('partner_id', '=', partner.id),
                                                             ('website_id', '=', website.id)],
                                                            order='write_date DESC', limit=1)
            if order and order.order_line:
                order.sudo().write({
                    'in_process': True
                })
        except Exception as e:
            msg = {"message": "Something Went Wrong.", "status_code": 400}
            return return_Response_error(msg)
        res = {"isSucess": True, "message": 'Order Locked Successfully', "status": 200}
        return return_Response(res)

    @http.route('/api/update_procurement_data', type='http', auth='public', methods=['GET'], csrf=False,
                cors='*')
    def update_procurement_data(self, **params):
        try:
            date = datetime.now().date()
            procurementId = request.env['procurement.table'].sudo().search([('date', '=', date)], limit=1)
            if not procurementId:
                procurementId = request.env['procurement.table'].sudo().create({'date': date})
            else:
                procurementId.procurementTableLine.sudo().unlink()
            request.cr.execute(f"insert into procurement_order_line_table (product_id, procurement_table_id, date, product_uom_qty) select product_id, {procurementId}, '{date}', sum(product_uom_qty) as qty from sale_order_line where create_date between '{date} 00:00:00' and '{date} 23:59:59' group by product_id order by qty desc")
            res = {"isSucess": True, "message": 'Success', "status": 200}
            return return_Response(res)
        except Exception as e:
            msg = {"message": "Something Went Wrong.", "status_code": 400}
            return return_Response_error(msg)



