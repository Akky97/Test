import re

import phonenumbers
from odoo import http, _, exceptions
from odoo.http import request
from .serializers import Serializer
from .exceptions import QueryFormatError
from .error_or_response_parser import *
from odoo.addons.website.controllers.main import Website
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError
import werkzeug
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




class AuthSignupHome(Website):
    @http.route('/api/v1/v/vendor_signup', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def vendor_signup(self):
        try:
            qcontext = self.get_auth_signup_qcontext()
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if not jdata.get('email') or not jdata.get('name') or not jdata.get('password') or not jdata.get('otp'):
                msg = {"message": "Something Went Wrong", "status_code": 400}
                return return_Response_error(msg)

            if not jdata.get('account_number') or not jdata.get('account_name') or not jdata.get('ifsc_code'):
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)

            if not jdata.get('owner_name') or not jdata.get('business_name') or not jdata.get(
                    'supplier_country_id') or not jdata.get('supplier_address') or not jdata.get(
                    'supplier_city') or not jdata.get('supplier_state_id') or not jdata.get('supplier_phone'):
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)

            if not jdata.get('country_id') or not jdata.get('state_id') or not jdata.get('city') or not jdata.get(
                    'address') or not jdata.get('email'):
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)

            email = jdata.get('email')
            name = jdata.get('name')
            password = jdata.get('password')
            otp = jdata.get('otp')
            confirm_password = jdata.get('confirm_password')
            qcontext.update({"login": email, "name": name, "password": password,
                             "confirm_password": confirm_password})
            email_veri = request.env['email.verification'].sudo().search([('email', '=', email)], limit=1,
                                                                         order='create_date desc')
            if email_veri and int(email_veri.otp) == int(otp):
                pass
            else:
                msg = {"message": "OTP not verified", "status_code": 400}
                return return_Response_error(msg)

            if not qcontext.get('token') and not qcontext.get('signup_enabled'):
                raise werkzeug.exceptions.NotFound()

            if 'error' not in qcontext and request.httprequest.method == 'POST':
                try:
                    self.do_signup(qcontext)
                    if qcontext.get('token'):
                        User = request.env['res.users']
                        user_sudo = User.sudo().search(
                            User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                        )
                        template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                                   raise_if_not_found=False)
                        if user_sudo and template:
                            template.sudo().send_mail(user_sudo.id, force_send=True)

                    user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
                    if user:
                        website = request.env['website'].sudo().browse(1)
                        warehouse = request.env['stock.warehouse'].sudo().search(
                            [('company_id', '=', website.company_id.id)], limit=1)
                        grp_internal = request.env.ref('base.group_user').id
                        grp_stock_user = request.env.ref('stock.group_stock_user').id
                        grp_marketplace = request.env.ref('odoo_marketplace.marketplace_draft_seller_group').id

                        userVals = {
                            'account_number': jdata.get('account_number'),
                            'account_name': jdata.get('account_name'),
                            'ifsc_code': jdata.get('ifsc_code'),
                            'owner_name': jdata.get('owner_name'),
                            'business_name': jdata.get('business_name'),
                            'supplier_country_id': int(jdata.get('supplier_country_id')),
                            'supplier_state_id': jdata.get('supplier_state_id'),
                            'supplier_phone': jdata.get('supplier_phone'),
                            'supplier_city': jdata.get('supplier_city'),
                            'supplier_address': jdata.get('supplier_address'),
                            'user_type': 'vendor',
                            'groups_id': [(6, 0, [grp_internal, grp_stock_user, grp_marketplace])],
                            'pickup_address_line': [(0, 0, {
                                'country_id': jdata.get('country_id'),
                                'address': jdata.get('address'),
                                'city': jdata.get('city'),
                                'state_id': jdata.get('state_id')
                            })]
                        }
                        gst_number = jdata.get('gst_number')
                        if gst_number:
                            rec = check_gst_number(gst_number, jdata.get('supplier_state_id'))
                            if 'message' not in rec:
                                userVals['gst_number'] = jdata.get('gst_number')
                            else:
                                msg = {"message": rec['message'], "status_code": 400}
                                return return_Response_error(msg)

                        partnerVals ={
                            'supplier_rank': 1,
                            'country_id':int(jdata.get('supplier_country_id')),
                            'customer_rank': 0,
                            'url_handler': user.partner_id.name,
                            'seller':True,
                            'warehouse_id':warehouse.id,
                            'location_id':warehouse.lot_stock_id.id,
                            'state_id': int(jdata.get('supplier_state_id')),
                            'phone': jdata.get('supplier_phone'),
                            'mobile': jdata.get('supplier_phone'),
                            'city': jdata.get('supplier_city'),
                            'street': jdata.get('supplier_address')
                        }
                        user.sudo().write(userVals)
                        user.partner_id.sudo().write(partnerVals)
                        user.partner_id.set_to_pending()
                        res = {"message": "Account Successfully Created", "status_code": 200}
                        email_get = request.env['email.verification'].sudo().search([('email', '=', email)], order='create_date desc', limit=1)
                        email_get.sudo().unlink()
                        return return_Response(res)
                except UserError as e:
                    qcontext['error'] = e.name or e.value
                    return error_response(e)
                except (SignupError, AssertionError) as e:
                    user = request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))])
                    if user:
                        msg = {"message": "Another user is already registered using this email address",
                               "status_code": 400}
                        return return_Response_error(msg)
                    else:
                        msg = {"message": "Could not create a new account", "status_code": 400}
                        return return_Response_error(msg)
        except Exception as e:
            msg = {"message": "Something Went Wrong", "status_code": 400}
            return return_Response_error(msg)


class OdooAPI(http.Controller):
    @http.route('/api/v1/v/product_category', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def get_category_list(self, **params):
        model = 'product.category'
        records=request.env[model].sudo()
        try:
            records = request.env[model].sudo().search([])
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        try:
            temp = []
            if records:
                for rec in records:
                    temp.append({
                        'id':rec.id,
                        'name':rec.name,
                        'complete_name': rec.complete_name
                    })

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count":len(temp),
            "record":temp,
            "status": 200
        }
        return return_Response(res)

    @http.route('/api/v1/v/get_uom_list', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def get_uom_list(self, **params):
        model = 'uom.uom'
        records = request.env[model].sudo()
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                records = request.env[model].sudo().search([])
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        try:
            temp = []
            if records:
                for rec in records:
                    temp.append({
                        'id': rec.id,
                        'name': rec.name,
                        'factor': rec.factor,
                        'uom_type': rec.uom_type,
                        'category_id': rec.category_id.id,
                        'category_name': rec.category_id.name
                    })

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "record": temp,
            "status": 200
        }
        return return_Response(res)

    @http.route(['/api/v1/v/attribute_value','/api/v1/v/attribute_value/<id>'], type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_attribute_value(self, id=None,**params):
        try:
            temp = []
            if id:
                record = request.env['product.attribute.value'].sudo().search([('attribute_id', '=', int(id))])
            else:
                record = request.env['product.attribute'].sudo().search([])
            if record:
                for i in record:
                    vals = {
                        'id': i.id,
                        'name': i.name
                    }
                    temp.append(vals)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "result": temp
        }
        return return_Response(res)


    @http.route('/api/v1/v/product_product', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def create_product(self, **params):
        try:
            resId = request.env['product.template'].sudo()
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                website = request.env['website'].sudo().browse(1)

                if not jdata.get('name') or not jdata.get('type') or not jdata.get('categ_id')or not jdata.get('list_price') or not jdata.get('tracking') or not jdata.get('country_id'):
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)
                dict = {
                    "name": jdata.get('name'),
                    "sequence": 1,
                    "type": jdata.get('type'),
                    "categ_id": jdata.get('categ_id'),
                    "list_price": jdata.get('list_price'),
                    "sale_ok": True,
                    "purchase_ok": False,
                    "uom_id": jdata.get('uom') or 1,
                    "uom_po_id": jdata.get('uom_po_id') or 1,
                    "company_id": website.company_id.id,
                    "active": True,
                    "invoice_policy": "order",
                    "tracking": jdata.get('tracking') or 'none',
                    "is_published": False,
                    "country_id": int(jdata.get('country_id')),
                    "public_categ_ids":[[6, False,[int(jdata.get('public_categ_ids'))]]]
                }
                if 'variant' in jdata:
                    lst=[]
                    for i in jdata.get('variant').keys():
                        if i:
                            value = [[6, False,jdata.get('variant')[i]]]
                            lst.append([0, 0,{'attribute_id':int(i),'value_ids':value}])
                    dict["attribute_line_ids"]= lst
                resId = request.env['product.template'].sudo().create(dict)
                resId.set_pending()
                if resId:
                    res = {
                        'message': "Product created Successfully",
                        'productId': resId.id,
                        'status': 200
                    }
                    return return_Response(res)
                else:
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
