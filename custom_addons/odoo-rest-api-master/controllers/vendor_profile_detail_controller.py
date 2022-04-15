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
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                website = request.env['website'].sudo().browse(1)

                if jdata.get('products'):
                    for rec in jdata.get('products'):
                        print(rec['name'])
                        dict = {
                            "name": rec.get('name'),
                            "sequence": 1,
                            "type": rec.get('type'),
                            "categ_id": rec.get('categ_id'),
                            "list_price": rec.get('list_price'),
                            "sale_ok": True,
                            "purchase_ok": False,
                            "uom_id": rec.get('uom') or 1,
                            "uom_po_id": rec.get('uom_po_id') or 1,
                            "company_id": website.company_id.id,
                            "active": True,
                            "invoice_policy": "order",
                            "tracking": rec.get('tracking') or 'none',
                            "is_published": False,
                            "country_id": int(rec.get('country_id')),
                            "public_categ_ids":[[6, False,[int(rec.get('public_categ_ids'))]]]
                        }
                        # dict['image_1920'] = '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'
                        if 'variant' in rec:
                            lst=[]
                            for i in rec.get('variant').keys():
                                if i:
                                    value = [[6, False,rec.get('variant')[i]]]
                                    lst.append([0, 0,{'attribute_id':int(i),'value_ids':value}])
                            dict["attribute_line_ids"]= lst
                        resId = request.env['product.template'].sudo().create(dict)
                        resId.set_pending()
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
