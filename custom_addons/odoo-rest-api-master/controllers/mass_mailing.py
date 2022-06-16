import datetime

from odoo import http, _, exceptions, fields
from odoo.http import request
import requests
from .exceptions import QueryFormatError
from .error_or_response_parser import *


class OdooAPI(http.Controller):

    @validate_token
    @http.route('/api/v1/c/pando.mass.mailing', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def pando_mass_mailing(self, **params):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if not jdata.get('email'):
                msg = {"message": "Email is not present", "status_code": 400}
                return return_Response_error(msg)
            mailing_list = request.env['mailing.list'].sudo().search([('name', '=', 'Pando Stores Mailing List')],
                                                                        limit=1)
            email = jdata.get('email')
            vals = {'email': email,
                    'subscription_list_ids': [(0, 0, {
                        'list_id': mailing_list.id
                    })]
                    }
            request.env['mailing.contact'].sudo().create(vals)
            res = {
                'message': 'Record Created Successfully',"isSucess": True,
                'status': 200
            }
            return return_Response(res)
        except Exception as e:
            msg = {"message": "Something Went Wrong", "status_code": 400}
            return return_Response_error(msg)
