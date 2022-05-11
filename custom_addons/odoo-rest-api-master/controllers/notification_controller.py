from odoo import http, _, exceptions, fields
from odoo.http import request
import requests
from .exceptions import QueryFormatError
from .error_or_response_parser import *


def send_notification(title, message, user, deviceToken, image=None):
    serverToken = request.env['ir.config_parameter'].sudo().search([('key', '=', 'firebase_credentials')],
                                                                   limit=1).value
    if not image:
        res_id = request.env['ir.attachment'].sudo()
        res_id = res_id.sudo().search([('res_model', '=', 'res.partner'),
                                       ('res_field', '=', 'image_1920'),
                                       ('res_id', 'in', [user.partner_id.id])], limit=1)
        base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
        image = base_url.value + '/web/image/' + str(res_id.id)
    if deviceToken:
        for device in deviceToken:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'key=' + serverToken,
            }
            body = {
                'notification': {'title': title or '',
                                 'body': message or '',
                                 'image': image
                                 },
                'to': device.token,
                'priority': 'high',
                #   'data': dataPayLoad,
            }
            response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))


class OdooAPI(http.Controller):

    @validate_token
    @http.route('/api/v1/c/product.notifications', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def product_notification_view(self, **params):
        try:
            user = request.env.user.partner_id.id
            domain = [('is_read', '=', False), ('seller_id', '=', user)]
            if "SeeAll" in params:
                domain = [('seller_id', '=', user)]
            model = 'notification.center'
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        limit = 0
        offset = 0
        if "page" in params:
            limit = 12
            page = int(params["page"])
            offset = (page - 1) * 12
        try:
            record_count = request.env[model].sudo().search_count(domain)
            records = request.env[model].sudo().search(domain, limit=limit, offset=offset, order='id DESC')
            temp = []
            for i in records:
                temp.append({"id": i.id,
                             "product_id": i.product_id.id if i.product_id.id != False else '',
                             "product_name": i.product_id.name if i.product_id.name != False else '',
                             'image': i.image_data if i.image_data != False else 'https://pandomall.s3.ap-southeast-1.amazonaws.com/1652177979bell.png',
                             'seller_id': i.seller_id.id, 'seller_name': i.seller_id.name,
                             'vendor_message': i.vendor_message if i.vendor_message != False else '',
                             'approve_by': i.approve_by.id if i.approve_by.id != False else '',
                             'approve_by_name': i.approve_by.name if i.approve_by.name != False else '',
                             "title": i.title if i.title != False else '',
                             "model": i.model if i.model != False else ''})
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "total_count": record_count,
            "count": len(temp),
            "notifications": temp
        }

        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/product.notifications/<id>', type='http', auth='public', methods=['GET'], csrf=False,
                cors='*')
    def single_product_notification_view(self, id=None, **params):
        model = 'notification.center'
        try:
            if not id:
                error = {"message": "id is not present in the request", "status": 400}
                return return_Response_error(error)
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        try:
            record = request.env[model].sudo().search([('id', '=', int(id))])
            vals = {}
            if record:
                vals = {
                    "id": record.id,
                    "product_id": record.product_id.id if record.product_id.id != False else '',
                    "product_name": record.product_id.name if record.product_id.name != False else '',
                    'image': record.image_data,
                    'seller_id': record.seller_id.id,
                    'seller_name': record.seller_id.name,
                    'vendor_message': record.vendor_message if record.vendor_message != False else '',
                    'approve_by': record.approve_by.id if record.approve_by.id != False else '',
                    'approve_by_name': record.approve_by.name if record.approve_by.name != False else '',
                    "title": record.title if record.title != False else '',
                    "model": record.model if record.model != False else ''}
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "notifications": vals,
            'status': 200
        }

        return return_Response(res)

    @validate_token
    @http.route(['/api/v1/c/product.notifications.update', '/api/v1/c/product.notifications.update/<id>'],
                type='http', auth='public', methods=['PUT'], csrf=False, cors='*')
    def product_notification_update(self, id=None, **params):
        model = 'notification.center'
        try:
            if not id:
                error = {"message": "id is not present in the request", "status": 400}
                return return_Response_error(error)
            records = request.env[model].sudo().search([('id', '=', id)])
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        try:
            for i in records:
                i.sudo().write({"is_read": True})

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "result": "Record Updated Successfully", "status": 200
        }
        return return_Response(res)
