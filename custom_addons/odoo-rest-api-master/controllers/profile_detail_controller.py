import json
import math
import logging
import requests
import ast
import phonenumbers
from odoo import http, _, exceptions
from odoo.http import request
from .serializers import Serializer
from .exceptions import QueryFormatError
from .error_or_response_parser import *
_logger = logging.getLogger(__name__)

import base64


class OdooAPI(http.Controller):
    @validate_token
    @http.route(['/api/v1/c/res.partner.view/', '/api/v1/c/res.partner.view/<id>/'], type='http', auth='public',
                methods=['GET'], csrf=False, cors='*')
    def profile_detail_view(self, id=None, **params):
        model = 'res.partner'
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
            temp = []
            for i in records:
                other_addresses = []
                for j in i.child_ids:
                    if j.type == 'invoice' or j.type == 'delivery':
                        other_addresses.append(
                            {"id": j.id, "name": j.name, "phone": j.phone if j.phone != False else "",
                             "mobile": j.mobile if j.mobile != False else "",
                             "email": j.email if j.email != False else "",
                             "street": j.street if j.street != False else "",
                             "street2": j.street2 if j.street2 != False else "",
                             "city": j.city if j.city != False else "",
                             "state_id": j.state_id.id if j.state_id.id != False else "",
                             "state_name": j.state_id.name if j.state_id.name != False else "",
                             "zip": j.zip if j.zip != False else "",
                             "country_id": j.country_id.id if j.country_id.id != False else "",
                             "country_name": j.country_id.name if j.country_id.name != False else "",
                             "image": base_url.value + '/web/image/' + str(res_id.id),
                             "website": j.website if j.website != False else "",
                             "type": j.type})
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
                             "website": i.website if i.website != False else "", "other_addresses": other_addresses})
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "result": temp
        }
        return return_Response(res)

    @validate_token
    @http.route(['/api/v1/c/res.partner.view/', '/api/v1/c/res.partner.view/<id>/'], type='http', auth='public',
                methods=['PUT'], csrf=False, cors='*')
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
            if records:
                for rec in records:
                    sale = request.env['sale.order'].sudo().search(['|', ('partner_id', '=', rec.id), '|', ('partner_invoice_id', '=', rec.id), ('partner_shipping_id', '=', rec.id)])
                    if sale:
                        msg = {"message": "Can not Update Your address Because it's in use.", "status_code": 400}
                        return return_Response_error(msg)

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
                dict['name'] = jdata.get('name') or ''
                dict['email'] = jdata.get('email') or ''
                dict['mobile'] = jdata.get('mobile') or ''
                dict['phone'] = jdata.get('phone') or ''
                dict['street'] = jdata.get('street') or ''
                dict['street2'] = jdata.get('street2') or ''
                dict['city'] = jdata.get('city') or ''
                if jdata.get('state_id'):
                    dict['state_id'] = int(jdata.get('state_id'))
                if jdata.get('country_id'):
                    dict['country_id'] = int(jdata.get('country_id'))
                dict['zip'] = jdata.get('zip') or ''
                for rec in records:
                    if jdata.get('country_id'):
                        country_id = request.env['res.country'].sudo().search([('id', '=', int(jdata.get('country_id')))])
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

    @validate_token
    @http.route(['/api/v1/c/delete/res.partner.view/', '/api/v1/c/delete/res.partner.view/<id>/'], type='http', auth='public',
                methods=['GET'], csrf=False, cors='*')
    def profile_detail_delete(self, id=None, **params):
        model = 'res.partner'
        try:
            if not id:
                error = {"message": "id is not present in the request", "status": 400}
                return return_Response_error(error)
            records = request.env[model].sudo().search([('id', '=', int(id))])
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        try:
            if records:
                order = request.env['sale.order'].sudo().search(['|', '|', ('partner_id', '=', int(id)), ('partner_invoice_id', '=', int(id)), ('partner_shipping_id', '=', int(id))])
                if order:
                    error = {"message": "You cannot delete this address", "status": 400}
                    return return_Response_error(error)
                records.sudo().unlink()
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "result": "Record Deleted Successfully", "status": 200
        }
        return return_Response(res)

    # @validate_token
    @http.route('/api/v1/c/get_country_state', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_country_state(self, **params):
        try:
            if "country_id" in params:
                model = 'res.country.state'
                records = request.env[model].sudo().search([('country_id', '=', int(params["country_id"]))])
            else:
                model = 'res.country'
                records = request.env[model].sudo().search([])
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        try:
            temp = []
            for i in records:
                temp.append({"id": i.id, "name": i.name})
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "result": temp
        }
        return return_Response(res)
