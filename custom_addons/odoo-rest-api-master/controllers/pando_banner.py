from odoo import http, _, exceptions
from odoo.http import request
from .sale_order_list_view import *
_logger = logging.getLogger(__name__)

def get_order_lines(order_id,seller_id):
    sol = request.env['sale.order.line'].sudo().search([('order_id', '=', order_id), ('product_id.marketplace_seller_id', '=', seller_id)])
    temp = []
    for line in sol:
        result = request.env['pando.images'].sudo().search([('product_id', '=', line.product_id.id)])
        if not result:
            result = request.env['pando.images'].sudo().search(
                [('product_id.product_tmpl_id', '=', line.product_id.product_tmpl_id.id)])
        base_image = {}
        for j in result:
            if j.type == 'multi_image':
                base_image = {
                    "id": j.product_id.id,
                    "image_url": j.image_url,
                    'image_name': j.image_name
                }
                if j.file_hash:
                    base_image['file_url'] = 'https://cloud.pandoproject.org/ipfs/' + j.file_hash

        id = []
        for c in line.product_id.product_template_attribute_value_ids:
            id.append(c.attribute_id.id)
        variant_name = ''
        for attr_id in list(set(id)):
            for b in line.product_id.product_template_attribute_value_ids:
                if attr_id == b.attribute_id.id:
                    variant_name += '(' + b.name + ')'

        val = {
            'name': line.product_id.name + variant_name,
            'url': base_image.get(
                'image_url') if 'image_url' in base_image else "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/330px-No-Image-Placeholder.svg.png?20200912122019",
            'image': base_image.get(
                'image_url') if 'image_url' in base_image else "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/330px-No-Image-Placeholder.svg.png?20200912122019",
            'image_name': base_image.get('image_name') if 'image_name' in base_image else '',
            'file_url': base_image.get('file_url'),
            'price_unit': line.price_unit if line.price_unit != False else 0.0,
            'price_subtotal': line.price_subtotal if line.price_subtotal != False else 0.0,
            'price_tax': line.price_tax if line.price_tax != False else 0.0,
            'price_total': line.price_total if line.price_total != False else 0.0,
            'tax_id': [{i.id:i.name} for i in line.tax_id],
            'quantity': line.product_uom_qty if line.product_uom_qty != False else 0.0,
            'qty_delivered': line.qty_delivered if line.qty_delivered != False else 0.0,
            'qty_invoiced': line.qty_invoiced if line.qty_invoiced != False else 0.0,
            "marketplace_seller_id": line.marketplace_seller_id.id,
            "marketplace_seller_name": line.marketplace_seller_id.name
        }
        temp.append(val)
    return temp
def deliveryLine(line):
    temp = []
    line = request.env['delivery.address'].sudo().search([('id', 'in', line.ids)], order='id desc')
    for l in line:
        temp.append({
            'date_time': str(l.date_time),
            'location': l.location,
            'to_location': l.to_location,
            'event': l.event,
            'is_dispatch': l.is_dispatch,
            'is_received': l.is_received,
            'tracking_location': l.tracking_location
        })
    return temp


class PandoBanner(http.Controller):

    @http.route('/api/v1/c/pando.banner', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_pando_banner(self, **params):
        try:
            model = 'pando.banner'
            domain = []
            if "type" in params and params.get('type'):
                domain = [('drop_down', '=', params.get('type'))]
            records = request.env[model].sudo().search(domain)
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            bannerList = []
            for rec in records:
                value = {
                    'id': rec.id,
                    'name': rec.name,
                    'drop_down': rec.drop_down,
                    'image': base_url.value + '/web/image/pando.banner/' + str(rec.id) + '/image/' +rec.name
                }
                bannerList.append(value)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(bannerList),
            "result": bannerList
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/create.delivery.tracking', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def create_delivery_tracking(self, **params):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        try:
            seller = request.env.user.partner_id.id
            if not jdata.get('order_id') or not jdata.get('from_location') or not jdata.get('to_location') or not jdata.get('event') or not jdata.get('trackingLocation'):
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
            order = request.env['sale.order'].sudo().search([('id', '=', int(jdata.get('order_id')))])
            if order:
                for picking in order.picking_ids:
                    if picking.marketplace_seller_id.id == seller:
                        vals = {
                            'seller_id': seller,
                            'dispatch_date': datetime.datetime.now(),
                            'source_address': seller,
                            'destination_address': order.partner_shipping_id.id,
                            'picking_id': picking.id,
                            'customer_id': order.partner_id.id,
                            'order_id': order.id,
                            'is_dispatch': True,
                            'tracking_location': jdata.get('trackingLocation'),
                            'deliveryLine': [(0, 0, {
                                'date_time': datetime.datetime.now(),
                                'location': jdata.get('from_location'),
                                'to_location': jdata.get('to_location'),
                                'event': jdata.get('event'),
                                'is_dispatch': True,
                                'tracking_location': jdata.get('trackingLocation')
                            })]
                        }
                        check = request.env['delivery.tracking'].sudo().search([('seller_id', '=', seller), ('order_id', '=', order.id)])
                        if check:
                            msg = {"message": "You Can't Create Multiple Tracking For a Single Order", "status_code": 400}
                            return return_Response_error(msg)
                        result = request.env['delivery.tracking'].sudo().create(vals)
                        if result:
                            resultlist = request.env['sale.order.line'].sudo().search([('product_id.marketplace_seller_id', '=', seller), ('order_id', '=', order.id)])
                            for i in resultlist:
                                i.sudo().write({'shipping_Details': 'shipped'})
                            res = {
                                "result": 'Delivery Created Successfully', 'status': 200
                            }
                            return return_Response(res)
                        else:
                            msg = {"message": "Something Went Wrong.", "status_code": 400}
                            return return_Response_error(msg)
                else:
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)

    @validate_token
    @http.route('/api/v1/c/get.delivery.tracking/<order_id>', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def get_delivery_tracking(self, order_id=None, **params):
        try:
            temp = []
            if not order_id:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)

            if order_id:
                order = request.env['sale.order'].sudo().search([('id','=', int(order_id))])
                domain = [('order_id', '=', int(order_id))]
                if "user" in params:
                    seller = request.env.user.partner_id.id
                    domain.append(('seller_id', '=', seller))
                else:
                    customer = request.env.user.partner_id.id
                    domain.append(('customer_id', '=', customer))

                if "id" in params and params.get('id'):
                    domain.append(('id', '=', int(params.get('id'))))
                tracking = request.env['delivery.tracking'].sudo().search(domain, order='id desc')
                if tracking:
                    for track in tracking:
                        vals = {
                            'id': track.id,
                            'seller_name': track.seller_id.name,
                            'dispatch_date': str(track.dispatch_date),
                            'source_address': get_address(track.source_address),
                            'destination_address': get_address(track.destination_address),
                            'customer_id': get_address(track.customer_id),
                            'order_name': order.name,
                            'is_dispatch': track.is_dispatch,
                            'is_received': track.is_received,
                            'trackingLocation': track.tracking_location,
                            'orderline': get_order_lines(track.order_id.id,track.seller_id.id),
                            'deliveryLine': deliveryLine(track.deliveryLine)
                        }
                        temp.append(vals)
                else:
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "result": temp,
            'status': 200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/add.delivery.line/<deliveryid>', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def add_delivery_line(self, deliveryid=None, **params):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if not jdata.get('from_location') or not jdata.get('to_location') or not jdata.get('event') or not jdata.get('trackingLocation'):
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
            tracking = request.env['delivery.tracking'].sudo().search([('id', '=', int(deliveryid))])
            if tracking:
                delVals = {
                    'delivery_id': tracking.id,
                    'date_time': datetime.datetime.now(),
                    'location': jdata.get('from_location'),
                    'to_location': jdata.get('to_location'),
                    'event': jdata.get('event'),
                    'is_received': True if jdata.get('is_received') else False,
                    'tracking_location': jdata.get('trackingLocation')
                }
                rec = request.env['delivery.address'].sudo().create(delVals)
                if rec:
                    if rec.is_received:
                        vals = {'is_received': True, 'tracking_location': jdata.get('trackingLocation')}
                        resultlist = request.env['sale.order.line'].sudo().search(
                            [('product_id.marketplace_seller_id', '=', tracking.seller_id.id), ('order_id', '=', tracking.order_id.id)])
                        for i in resultlist:
                            i.sudo().write({'shipping_Details': 'delivered'})
                    else:
                        vals = {'tracking_location': jdata.get('trackingLocation')}
                    tracking.sudo().write(vals)
                    res = {"message": "Delivery Status Updated", "status_code": 200}
                    return return_Response(res)
                else:
                    msg = {"message": "Something Went Wrong", "status_code": 400}
                    return return_Response_error(msg)
            else:
                msg = {"message": "No Result Found", "status_code": 400}
                return return_Response_error(msg)
        except Exception as e:
            msg = {"message": "Something Went Wrong", "status_code": 400}
            return return_Response_error(msg)
