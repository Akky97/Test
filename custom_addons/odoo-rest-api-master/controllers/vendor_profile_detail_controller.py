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
from odoo import http, _, exceptions, fields
from datetime import timedelta, time
from odoo.tools.float_utils import float_round
import werkzeug
_logger = logging.getLogger(__name__)


def _compute_sales_count(self):
    r = {}
    self.sales_count = 0
    date_from = fields.Datetime.to_string(fields.datetime.combine(fields.datetime.now() - timedelta(days=365),
                                                                  time.min))

    done_states = self.env['sale.report']._get_done_states()

    domain = [
        ('state', 'in', done_states),
        ('product_id', 'in', self.ids),
        ('date', '>=', date_from),
    ]
    for group in self.env['sale.report'].read_group(domain, ['product_id', 'product_uom_qty'], ['product_id']):
        r[group['product_id'][0]] = group['product_uom_qty']
    for product in self:
        if not product.id:
            product.sales_count = 0.0
            continue
        product.sales_count = float_round(r.get(product.id, 0), precision_rounding=product.uom_id.rounding)
    return r


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
    @validate_token
    @http.route('/api/v1/v/get_product_category', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def get_product_category_list(self, **params):
        model = 'product.category'
        records = request.env[model].sudo()
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
                        'id': rec.id,
                        'name': rec.name
                    })
            else:
                msg = {"message": "No result Found.", "status_code": 400}
                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "record": temp,
            "status": 200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/v/product_category', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def get_category_list(self, **params):
        model = 'product.public.category'
        records = request.env[model].sudo()
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
                        'id': rec.id,
                        'name': rec.name
                    })
            else:
                msg = {"message": "No result Found.", "status_code": 400}
                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "record": temp,
            "status": 200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/v/get_uom_list', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def get_uom_list(self, **params):
        model = 'uom.uom'
        records = request.env[model].sudo()
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

    @validate_token
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

    @validate_token
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
                    msg = {"message": "No Data Found.", "status_code": 400}
                    return return_Response_error(msg)
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            'message': "Product created Successfully",
            'status': 200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/v/product.template.view', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def product_template_view(self, **params):
        try:
            domain = [('is_published', '=', True),('type','=','product'),('marketplace_seller_id','=', request.env.user.partner_id.id)]
            model = 'product.product'
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)

        if "query" in params:
            query = params["query"]
        else:
            query = "{*}"
        search = ''
        if "orderBy" in params:
            orders = params["orderBy"]
            if orders == 'rating':
                pass
            elif orders == 'new':
                search = 'create_date DESC'
            elif orders == 'featured':
                search = 'sale_count_pando DESC'
            elif orders == 'sale':
                search = 'sale_count_pando DESC'
                domain.append(('website_ribbon_id.html', '=', 'Sale'))
        limit = 0
        offset = 0
        if "page" in params:
            limit = 12
            page = int(params["page"])
            offset = (page - 1) * 12
        record_count = request.env[model].sudo().search_count(domain)
        records = request.env[model].sudo().search(domain, order=search, limit=limit, offset=offset)
        if ("orderBy" in params and params['orderBy'] == 'featured') or ("orderBy" in params and params['orderBy'] == 'sale'):
            for res in records:
                _compute_sales_count(self=res)
                res.sale_count_pando = res.sales_count
            records = request.env[model].sudo().search(domain, order=search, limit=limit, offset=offset)
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1
        website = request.env['website'].sudo().browse(1)
        try:
            warehouse = request.env['stock.warehouse'].sudo().search(
                [('company_id', '=', website.company_id.id)], limit=1)

            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            temp = []
            for i in records:
                image = []
                category=[]
                variant=[]
                sellers=[]
                for j in i.product_template_image_ids:
                    image.append({"id": j.id, "name": j.name,
                                  "image": base_url.value + '/web/image/product.image/' + str(j.id) + "/image_1920",
                                  'url': base_url.value + '/web/image/product.image/' + str(j.id) + "/image_1920",
                                  })
                for z in i.public_categ_ids:
                    category.append({"id": z.id, "name": z.name,"slug":z.name.lower().replace(" ","-"),
                             "image": base_url.value + '/web/image/product.public.category/' + str(z.id) + "/image_1920",})
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
                    sellers.append({"id": n.id, "vendor": n.name.name,"vendor_id": n.name.id})

                temp.append({"id": i.id, "name": i.name,
                             'url': base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920",
                             'image': base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920",
                             'type': i.type, 'sale_price': i.list_price, "price": i.standard_price,
                             'description': i.description if i.description != False else '',
                             'short_desc': i.description_sale if i.description_sale != False else '',
                             'categ_id': i.categ_id.id if i.categ_id.id != False else '',
                             'categ_name': i.categ_id.name if i.categ_id.name != False else '',
                             "category":category,
                             "create_uid":i.create_uid.id if i.create_uid.id != False else '',
                             "create_name":i.create_uid.name if i.create_uid.name != False else '',
                             "write_uid":i.write_uid.id if i.write_uid.id != False else '',
                             "write_name":i.write_uid.name if i.write_uid.name != False else '',
                             "variants":variant,
                             "stock": i.with_context(warehouse=warehouse.id).virtual_available if i.with_context(warehouse=warehouse.id).virtual_available>0 else 0.0,
                             "sm_pictures": image,
                             "featured":i.website_ribbon_id.html if i.website_ribbon_id.html != False else '',
                             "seller_ids":sellers,
                             "slug":i.id,
                             "top": True if i.website_ribbon_id.html == 'Trending' else None,
                             "new": True if i.website_ribbon_id.html == 'New' else None,
                             "author":"Pando-Stores",
                             "sold":i.sales_count,
                             "review":2,
                             "rating":3,
                             "additional_info": i.additional_info if i.additional_info else '',
                             "shipping_return": i.shipping_return if i.shipping_return else '',
                             "pictures": [{'url': base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920","image": base_url.value + '/web/image/product.product/' + str(i.id) + "/image_1920"}]
                             })
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "total_count": record_count,
            "count": len(temp),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "products": temp,
            'symbol': website.company_id.currency_id.symbol if website.company_id.currency_id.symbol != False else ""
        }

        return return_Response(res)
