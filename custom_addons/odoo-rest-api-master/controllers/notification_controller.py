from odoo import http, _, exceptions, fields
from odoo.http import request
from .exceptions import QueryFormatError
from .error_or_response_parser import *


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
            records = request.env[model].sudo().search(domain, limit=limit, offset=offset)
            temp = []
            for i in records:
                temp.append({"id": i.id,
                             "product_id": i.product_id.id if i.product_id.id != False else '',
                             "product_name": i.product_id.name if i.product_id.name != False else '',
                             'image': i.image_data,
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

    @validate_token
    @http.route(['/api/v1/c/res.partner.view/', '/api/v1/c/res.partner.view/<id>/'],
                type='http', auth='public', methods=['PUT'], csrf=False, cors='*')
    def profile_detail_update(self, id=None, **params):
        model = 'res.partner'
        try:
            if not id:
                error = {"message": "id is not present in the request", "status": 400}
                return return_Response_error(error)
            records = request.env[model].sudo().search([('id', '=', id)])

        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        try:
            dict = {}
            res_id = request.env['ir.attachment'].sudo()
            res_id = res_id.sudo().search([('res_model', '=', 'res.partner'),
                                           ('res_field', '=', 'image_1920'),
                                           ('res_id', 'in', [id])])
            res_id.sudo().write({"public": True})
            # if records:
            #     for rec in records:
            #         sale = request.env['sale.order'].sudo().search(['|', ('partner_id', '=', rec.id), '|', ('partner_invoice_id', '=', rec.id), ('partner_shipping_id', '=', rec.id)])
            #         if sale:
            #             msg = {"message": "Can not Update Your address Because it's in use.", "status_code": 400}
            #             return return_Response_error(msg)

            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                if 'image' in jdata:
                    image = jdata.get('image')
                    jdata.pop('image')
                    res_id.sudo().write({
                        'name': 'image_1920',
                        'checksum': image,
                        'datas': image,
                        'type': 'binary'
                    })
                dict['name'] = jdata.get('name') or records.name or ''
                dict['email'] = jdata.get('email') or records.email or ''
                dict['mobile'] = jdata.get('mobile') or records.mobile or ''
                dict['phone'] = jdata.get('phone') or records.phone or ''
                dict['street'] = jdata.get('street') or records.street or ''
                dict['street2'] = jdata.get('street2') or records.street2 or ''
                dict['city'] = jdata.get('city') or records.city or ''
                if jdata.get('state_id'):
                    dict['state_id'] = int(jdata.get('state_id'))
                if jdata.get('country_id'):
                    dict['country_id'] = int(jdata.get('country_id'))
                dict['zip'] = jdata.get('zip') or records.zip or ''
                for rec in records:
                    if jdata.get('country_id'):
                        country_id = request.env['res.country'].sudo().search(
                            [('id', '=', int(jdata.get('country_id')))])
                    else:
                        country_id = rec.country_id

                    if dict.get('mobile'):
                        my_number = phonenumbers.parse(str(dict.get('mobile')), country_id.code)
                        if not phonenumbers.is_valid_number(my_number):
                            error = {"message": "Please Enter Correct Mobile Number", "status": 400}
                            return return_Response_error(error)
                    if dict.get('phone'):
                        my_number = phonenumbers.parse(str(dict.get('phone')), country_id.code)
                        if not phonenumbers.is_valid_number(my_number):
                            error = {"message": "Please Enter Correct Phone Number", "status": 400}
                            return return_Response_error(error)

                    rec.sudo().write(dict)
            # End here

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "result": "Record Updated Successfully", "status": 200
        }
        return return_Response(res)
