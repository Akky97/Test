import re

import phonenumbers
from odoo import http, _, exceptions
from odoo.http import request
from .serializers import Serializer
from .exceptions import QueryFormatError
from .error_or_response_parser import *
_logger = logging.getLogger(__name__)




def check_gst_number(gst, state_id):
    state_id = request.env['res.country.state'].sudo().search([('id','=',int(state_id))])
    vals = {}
    if (len(gst) != 15):
        message = 'Invalid GSTIN. GSTIN number must be 15 digits. Please check.'
        vals['message'] = message
        return vals

    if not (re.match("\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d[Z]{1}[A-Z\d]{1}", gst.upper())):
        message = 'Invalid GSTIN format.\r\n. GSTIN must be in the format nnAAAAAnnnnA_Z_ where n=number, A= alphabet, _= digit'
        vals['message'] = message
        return vals

    if gst[0:2] != state_id.l10n_in_tin:
        message = 'Please Enter Correct GSTIN'
        vals['message'] = message
        return vals

    return vals


class OdooAPI(http.Controller):
    @http.route('/api/v1/v/res.users', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def vendor_profile_detail_view(self, **params):
        model = 'res.users'
        try:
            query = 'update res_users set'
            pickupQuery = ''
            website = request.env['website'].sudo().browse(1)
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                if not jdata.get('account_number') or not jdata.get('account_name') or not jdata.get('ifsc_code'):
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)

                if not jdata.get('owner_name') or not jdata.get('business_name') or not jdata.get('supplier_country_id') or not jdata.get('supplier_address') or not jdata.get('supplier_city') or not jdata.get('supplier_state_id') or not jdata.get('supplier_phone'):
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)

                if not jdata.get('country_id') or not jdata.get('state_id') or not jdata.get('city') or not jdata.get('address') or not jdata.get('email'):
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)
                # prepare data for supplier details
                gst_number = jdata.get('gst_number')
                if gst_number:
                    rec = check_gst_number(gst_number, jdata.get('supplier_state_id'))
                    if 'message' not in rec:
                        query += f" gst_number='{jdata.get('gst_number')}',"
                    else:
                        msg = {"message": rec['message'], "status_code": 400}
                        return return_Response_error(msg)
                query += f" account_name='{jdata.get('account_name')}', " \
                         f"account_number='{jdata.get('account_number')}', " \
                         f"ifsc_code='{jdata.get('ifsc_code')}', " \
                         f"owner_name='{jdata.get('owner_name')}', business_name='{jdata.get('business_name')}'," \
                         f" supplier_country_id='{jdata.get('supplier_country_id')}', supplier_state_id='{jdata.get('supplier_state_id')}'," \
                         f" supplier_address='{jdata.get('supplier_address')}', supplier_city='{jdata.get('supplier_city')}', " \
                         f"supplier_phone='{jdata.get('supplier_phone')}',"

                request.env.cr.execute(f"select * from res_users where login='{jdata.get('email')}'")
                result = request.env.cr.dictfetchall()
                if result and result[0]['id']:
                    # create pickup address
                    pickupQuery = f" INSERT INTO pickup_address(user_id,country_id,address,city,state_id) VALUES({result[0]['id']},{jdata.get('country_id')}, '{jdata.get('address')}', '{jdata.get('city')}', {jdata.get('state_id')})"
                    request.env.cr.execute(pickupQuery)
                    # update supplier address and bank details
                    query += f" active='f' where login='{jdata.get('email')}'"
                    request.env.cr.execute(query)
                else:
                    msg = {"message": "User Does not Exists", "status_code": 400}
                    return return_Response_error(msg)
            else:
                msg = {"message": "Parameter is Empty", "status_code": 400}
                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "message":"Profile Updated Successfully", "status":200
            }
        return return_Response(res)

