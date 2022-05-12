import datetime
import re
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError
from odoo import http, _, exceptions, fields
from datetime import timedelta, time
from odoo.tools.float_utils import float_round
from .sale_order_list_view import *
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


def get_rating_avg(product):
    records = request.env['rating.rating'].sudo().search([('rating_product_id','=',product.id)])
    if records:
        rating_total = 0
        count = 0
        for rec in records:
            count += 1
            rating_total += rec.rating
        return (rating_total/count)
    else:
        return 0


def get_product_details(website, warehouse, base_url,records):
    temp = []
    for i in records:
        image = []
        category = []
        variant = []
        sellers = []
        result = request.env['pando.images'].sudo().search([('product_id', '=', i.id)])
        if not result:
            result = request.env['pando.images'].sudo().search(
                [('product_id.product_tmpl_id', '=', i.product_tmpl_id.id)])
        base_image = {}
        for j in result:
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

        for z in i.public_categ_ids:
            category.append({"id": z.id, "name": z.name, "slug": z.name.lower().replace(" ", "-"),
                             "image": base_url.value + '/web/image/product.public.category/' + str(
                                 z.id) + "/image_1920", })
        product_var = request.env['product.product'].sudo().search([('id', '=', int(i.id))])
        for k in product_var:
            values = []
            attribute_name = ''
            id = []
            data = []
            variant_name = ''
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
                        variant_name += '('+b.name + ')'

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
            sellers.append({"id": n.id, "vendor": n.name.name, "vendor_id": n.name.id})

        temp.append({"id": i.id, "name": i.product_tmpl_id.name+variant_name,
                     'url': base_image.get('image_url') if 'image_url' in base_image else "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/330px-No-Image-Placeholder.svg.png?20200912122019" ,
                     'image': base_image.get('image_url') if 'image_url' in base_image else "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/330px-No-Image-Placeholder.svg.png?20200912122019" ,
                     'image_name': base_image.get('image_name') if 'image_name' in base_image else '',
                     'type': i.type, 'sale_price': i.list_price, "price": i.standard_price,
                     'description': i.description if i.description != False else '',
                     'short_desc': i.description_sale if i.description_sale != False else '',
                     'categ_id': i.categ_id.id if i.categ_id.id != False else '',
                     'categ_name': i.categ_id.name if i.categ_id.name != False else '',
                     "category": category,
                     "create_uid": i.create_uid.id if i.create_uid.id != False else '',
                     "create_name": i.create_uid.name if i.create_uid.name != False else '',
                     "write_uid": i.write_uid.id if i.write_uid.id != False else '',
                     "write_name": i.write_uid.name if i.write_uid.name != False else '',
                     "variants": variant,
                     # "stock": i.qty_available,
                     "stock": i.with_context(warehouse=warehouse.id).virtual_available if i.with_context(
                         warehouse=warehouse.id).virtual_available > 0 else 0.0,
                     "sm_pictures": image,
                     "featured": i.website_ribbon_id.html if i.website_ribbon_id.html != False else '',
                     "seller_ids": sellers,
                     "slug": i.id,
                     "top": True if i.website_ribbon_id.html == 'Trending' else None,
                     "new": True if i.website_ribbon_id.html == 'New' else None,
                     "author": "Pando-Stores",
                     "sold": i.sales_count,
                     "review": 2,
                     "rating": get_rating_avg(i),
                     "is_product_publish": i.is_product_publish,
                     "additional_info": i.additional_info if i.additional_info else '',
                     "shipping_return": i.shipping_return if i.shipping_return else '',
                     "status":i.marketplace_status,
                     "pictures": [
                         {
                            'url': base_image.get('image_url') if 'image_url' in base_image else "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/330px-No-Image-Placeholder.svg.png?20200912122019" ,
                            'image': base_image.get('image_url') if 'image_url' in base_image else "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/330px-No-Image-Placeholder.svg.png?20200912122019" }]
                     })
    return temp


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
                    'address') or not jdata.get('email') or not jdata.get('zip'):
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
                                'state_id': jdata.get('state_id'),
                                'zip': jdata.get('zip')
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
                        vals = {
                            "seller_id":user.partner_id.id,
                            "vendor_message":f"""You are successfully Signed Up""",
                            "model":"res.partner",
                            "title":"Seller Signup"
                        }
                        request.env['notification.center'].sudo().create(vals)
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

    @http.route('/api/v1/v/vendor/forgot_password', type='http', auth='public', methods=['POST'], csrf=False,
                cors='*')
    def vendor_forgot_password(self):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata and jdata.get('email') and jdata.get('otp') and jdata.get('password'):
                email = jdata.get('email')
                otp = jdata.get('otp')
                psw = jdata.get('password')
                user = request.env['res.users'].sudo().search([('login', '=', email)])
                if not user:
                    msg = {"message": "User does not exist!!", "status_code": 400}
                    return return_Response_error(msg)
                # aakash vishwakarma
                if user.user_type != 'vendor':
                    error = {"message": "You are not authorized to Change Password from here", "status": 400}
                    return return_Response_error(error)
                # End here
                email_otp = request.env['forgot.password'].sudo().search([('email', '=', email)],
                                                                         order='create_date desc', limit=1)
                if not email_otp:
                    msg = {"message": "Please Resend OTP", "status_code": 400}
                    return return_Response_error(msg)
                if user and email_otp:
                    if int(otp) == int(email_otp.otp):
                        user.sudo().write({'password': psw})
                        msg = {"message": "Password has been changed successfully", "status_code": 200}
                        return return_Response(msg)
                    else:
                        msg = {"message": "OTP is Incorrect", "status_code": 400}
                        return return_Response(msg)
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except Exception as e:
            msg = {"message": str(e), "status_code": 400}
            return return_Response_error(msg)


class OdooAPI(http.Controller):

    @validate_token
    @http.route('/api/v1/v/vendor_profile_update', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def vendor_profile_update(self):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                user = request.env.user
                res_id = request.env['ir.attachment'].sudo()
                res_id = res_id.sudo().search([('res_model', '=', 'res.partner'),
                                               ('res_field', '=', 'image_1920'),
                                               ('res_id', 'in', [user.partner_id.id])])
                if 'image' in jdata:
                    image = jdata.get('image')
                    jdata.pop('image')
                    res_id.sudo().write({
                        'name': 'image_1920',
                        'checksum': image,
                        'datas': image,
                        'type': 'binary'
                    })

                userVals = {
                    'account_number': jdata.get('account_number') or user.account_number,
                    'account_name': jdata.get('account_name') or user.account_name,
                    'ifsc_code': jdata.get('ifsc_code') or user.ifsc_code,
                    'owner_name': jdata.get('owner_name') or user.owner_name,
                    'business_name': jdata.get('business_name') or user.business_name,
                    'supplier_country_id': jdata.get('supplier_country_id') or user.supplier_country_id.id,
                    'supplier_state_id': jdata.get('supplier_state_id') or user.supplier_state_id.id,
                    'supplier_phone': jdata.get('supplier_phone') or user.supplier_phone,
                    'supplier_city': jdata.get('supplier_city') or user.supplier_city,
                    'supplier_address': jdata.get('supplier_address') or user.supplier_address
                }
                gst_number = jdata.get('gst_number')
                if gst_number:
                    rec = check_gst_number(gst_number, userVals.get('supplier_state_id'))
                    if 'message' not in rec:
                        userVals['gst_number'] = jdata.get('gst_number')
                    else:
                        msg = {"message": rec['message'], "status_code": 400}
                        return return_Response_error(msg)

                partnerVals ={
                    'name': jdata.get('name') or user.partner_id.name,
                    'state_id': jdata.get('supplier_state_id') or user.partner_id.state_id.id,
                    'phone': jdata.get('supplier_phone') or user.partner_id.phone,
                    'mobile': jdata.get('supplier_phone') or user.partner_id.mobile,
                    'city': jdata.get('supplier_city') or user.partner_id.city,
                    'street': jdata.get('supplier_address') or user.partner_id.street,
                    'zip': jdata.get('zip') or user.partner_id.zip
                }
                user.sudo().write(userVals)
                user.partner_id.sudo().write(partnerVals)
                vals = {
                    "seller_id": user.partner_id.id,
                    "vendor_message": "Your Profile Is Successfully Updated",
                    "model": "res.partner",
                    "title": "Seller Record Update"
                }
                request.env['notification.center'].sudo().create(vals)
                res = {"message": "Record Successfully Updated", "status_code": 200}
                return return_Response(res)
            else:
                msg = {"message": "Something Went Wrong", "status_code": 400}
                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)


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
    @http.route('/api/v1/v/attribute_value_data', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def attribute_value_data(self, **params):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            res = {}
            if jdata:
                if not jdata.get('variant'):
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)

                for id in jdata.get('variant')[0].keys():
                    value = jdata.get('variant')[0][id]
                    pav = []
                    pAttr = request.env['product.attribute'].sudo().search([('id','=',int(id))])
                    pAttrValue = request.env['product.attribute.value'].sudo().search([('id', 'in', value)])
                    for r in pAttrValue:
                        pav.append(r.name)
                    if pAttr:
                        res[pAttr.name] = pav

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "result": res
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/v/account.tax', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_account_tax(self, **params):
        try:
            temp = []
            record = request.env['account.tax'].sudo().search([])
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
    @http.route('/api/v1/v/product.ribbon', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_product_ribbon(self, **params):
        try:
            temp = []
            record = request.env['product.ribbon'].sudo().search([])
            if record:
                for i in record:
                    vals = {
                        'id': i.id,
                        'name': i.html
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
        idList = []
        name = ''
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                website = request.env['website'].sudo().browse(1)

                if jdata.get('products'):
                    for rec in jdata.get('products'):
                        tax = [[6, False, []]]
                        name = rec.get('name')
                        dict = {
                            "name": rec.get('name'),
                            "sequence": 1,
                            "type": rec.get('type'),
                            "categ_id": rec.get('categ_id'),
                            "list_price": rec.get('list_price'),
                            "standard_price": rec.get('standard_price'),
                            "description": rec.get('description') or '',
                            "description_sale": rec.get('description_sale') or '',
                            "additional_info": rec.get('additional_info') or '',
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
                        if 'tax' in rec and rec.get('tax'):
                            dict['taxes_id'] = [[6, False,[int(rec.get('tax'))]]]
                            tax = dict['taxes_id']
                        if 'ribbon' in rec and rec.get('ribbon'):
                            dict['website_ribbon_id'] = int(rec.get('ribbon'))
                        if 'variant' in rec and rec.get('variant'):
                            lst=[]
                            for i in rec.get('variant').keys():
                                if i:
                                    value = [[6, False, rec.get('variant')[i]]]
                                    lst.append([0, 0, {'attribute_id': int(i), 'value_ids': value}])
                            dict["attribute_line_ids"] = lst
                        resId = request.env['product.template'].sudo().create(dict)
                        resId.sudo().write({"categ_id": rec.get('categ_id'), 'taxes_id': tax})
                        resId.set_pending()
                        if resId.product_variant_ids:
                            idList.append(resId.product_variant_ids[0].id)
                else:
                    msg = {"message": "No Data Found.", "status_code": 400}
                    return return_Response_error(msg)
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        if idList:
            vals = {
                'seller_id': request.env.user.partner_id.id,
                'vendor_message': f"{name} Created Successfully",
                'model': "product.template",
                'title': "Product Template"
            }
            request.env['notification.center'].sudo().create(vals)

        res = {
            'message': "Product created Successfully",
            'productList': idList,
            'status': 200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/v/product.template.view', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def vendor_product_template_view(self, **params):
        try:
            domain = [("marketplace_seller_id", "=", request.env.user.partner_id.id)]
            model = 'product.product'
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        search = ''

        if "search" in params:
            domain.append(('name', 'ilike', params['search']))

        if "orderBy" in params:
            orders = params["orderBy"]
            if orders == 'rating':
                pass
            elif orders == 'new':
                search = 'create_date DESC'
            elif orders == 'featured':
                search = 'sale_count_pando DESC'

        if "status" in params:
            domain.append(('marketplace_status', 'in', [params['status']]))


        limit = 0
        offset = 0
        if "page" in params:
            limit = 10
            page = int(params["page"])
            offset = (page - 1) * 10
        record_count = request.env[model].sudo().search_count(domain)
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
            if ("orderBy" in params and params['orderBy'] == 'featured') or (
                    "orderBy" in params and params['orderBy'] == 'sale'):
                for res in records:
                    _compute_sales_count(self=res)
                    res.sale_count_pando = res.sales_count
                records = request.env[model].sudo().search(domain, order=search, limit=limit, offset=offset)

            temp = get_product_details(website, warehouse, base_url, records)
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

    @validate_token
    @http.route('/api/v1/v/product.template.view/<id>', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def single_product_template_view(self, id=None, **params):
        try:
            model = 'product.product'
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)
        records = request.env[model].sudo().search([("id", "=", int(id))])
        website = request.env['website'].sudo().browse(1)
        try:
            warehouse = request.env['stock.warehouse'].sudo().search(
                [('company_id', '=', website.company_id.id)], limit=1)

            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            temp = get_product_details(website, warehouse, base_url, records)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "products": temp,
            'symbol': website.company_id.currency_id.symbol if website.company_id.currency_id.symbol != False else ""
        }

        return return_Response(res)

    @validate_token
    @http.route('/api/v1/v/vendor_dashboard', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def vendor_dashboard(self, **params):
        try:
            domain = [("marketplace_seller_id", "=", request.env.user.partner_id.id)]
            model = 'sale.order.line'
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata and jdata.get('from_date') and jdata.get('to_date'):
                domain.append(('order_id.date_order', '>=', jdata.get('from_date')))
                domain.append(('order_id.date_order', '<=', jdata.get('to_date')))
            records = request.env[model].sudo().search(domain)
            total_sales_unit = 0
            total_earning = 0
            total_count = 0
            total_return=0
            for rec in records:
                total_count +=1
                total_sales_unit += rec.product_uom_qty
                total_earning += rec.price_subtotal
            res={
                'total_count':total_count,
                'total_sales_unit':total_sales_unit,
                'total_earning':total_earning,
                'total_return':total_return
            }
            return return_Response(res)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)

    @validate_token
    @http.route('/api/v1/v/sale_order_list_view', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def sale_order_list_view(self, **params):
        try:
            domain = [("marketplace_seller_id", "=", request.env.user.partner_id.id)]
            model = 'sale.order.line'
        except KeyError as e:
            msg = "The model `%s` does not exist." % model
            return error_response(e, msg)

        limit = 0
        offset = 0
        if "search" in params:
            domain.append(('name', 'ilike', params['search']))
        if "page" in params:
            limit = 10
            page = int(params["page"])
            offset = (page - 1) * 10
        if "status" in params:
            domain.append(('marketplace_state', 'in', [params['status']]))
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        if jdata and jdata.get('from_date') and jdata.get('to_date'):
            domain.append(('order_id.date_order', '>=', jdata.get('from_date')))
            domain.append(('order_id.date_order', '<=', jdata.get('to_date')))
        if "quator" in params and params.get('quator'):
            from_date = datetime.datetime.now().date()
            if params.get('quator') == 'week':
                to_date = from_date - timedelta(days=7)
            if params.get('quator') == 'month':
                to_date = from_date - timedelta(days=30)
            if params.get('quator') == 'q1':
                to_date = from_date - timedelta(days=90)
            if params.get('quator') == 'q2':
                to_date = from_date - timedelta(days=180)
            if params.get('quator') == 'q3':
                to_date = from_date - timedelta(days=270)
            if params.get('quator') == 'q4':
                to_date = from_date - timedelta(days=365)
            if from_date and to_date:
                domain.append(('order_id.date_order', '<=', from_date))
                domain.append(('order_id.date_order', '>=', to_date))
        record_count = request.env[model].sudo().search_count(domain)
        records = request.env[model].sudo().search(domain, order='id desc', limit=limit, offset=offset)
        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1
        website = request.env['website'].sudo().browse(1)
        base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
        warehouse = request.env['stock.warehouse'].sudo().search(
            [('company_id', '=', website.company_id.id)], limit=1)
        try:
            temp=[]
            for rec in records:
                result = request.env['pando.images'].sudo().search([('product_id', '=', rec.product_id.id)])
                if not result:
                    result = request.env['pando.images'].sudo().search(
                        [('product_id.product_tmpl_id', '=', rec.product_id.product_tmpl_id.id)])
                base_image = {}
                image = []
                for j in result:
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

                vals={
                    "id":rec.id,
                    "order_id":rec.order_id.name,
                    "product_id":rec.product_id.id,
                    "product_name":rec.product_id.name,
                    "price_subtotal":rec.price_subtotal,
                    "date": str(rec.order_id.date_order),
                    "create_date": str(rec.order_id.create_date),
                    "quantity": rec.product_uom_qty if rec.product_uom_qty != False else 0.0,
                    "image": base_image.get('image_url') if 'image_url' in base_image else "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/330px-No-Image-Placeholder.svg.png?20200912122019" ,
                    "image_name": base_image.get('image_name') if 'image_name' in base_image else "",
                    "multi_image": image,
                    "stock": rec.product_id.with_context(warehouse=warehouse.id).virtual_available if rec.product_id.with_context(
                    warehouse=warehouse.id).virtual_available > 0 else 0.0,
                    "marketplace_state": rec.marketplace_state,
                    "shipping_status": rec.shipping_Details if rec.shipping_Details != False else ''
                }
                temp.append(vals)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "total_order": record_count,
            "count": len(temp),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "products": temp,
            'symbol': website.company_id.currency_id.symbol if website.company_id.currency_id.symbol != False else ""
        }

        return return_Response(res)

    @validate_token
    @http.route('/api/v1/v/sale_order_line_details/<id>', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def sale_order_line_details(self, id=None, **params):
        try:
            if not id:
                error = {"message": "id is not present in the request", "status": 400}
                return return_Response_error(error)
            record = request.env['sale.order.line'].sudo().search([('id','=',int(id))])
            website = request.env['website'].sudo().browse(1)
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            warehouse = request.env['stock.warehouse'].sudo().search(
                [('company_id', '=', website.company_id.id)], limit=1)
            vals = {}
            if record:
                vals = {
                    "id": record.id,
                    "order_id": record.order_id.name,
                    "product_id": record.product_id.id,
                    "product_name": record.product_id.name,
                    "price_subtotal": record.price_subtotal,
                    "date": str(record.order_id.date_order),
                    "create_date": str(record.order_id.create_date),
                    "quantity": record.product_uom_qty if record.product_uom_qty != False else 0.0,
                    "image": base_url.value + '/web/image/product.product/' + str(record.product_id.id) + "/image_1920",
                    "stock": record.product_id.with_context(
                        warehouse=warehouse.id).virtual_available if record.product_id.with_context(
                        warehouse=warehouse.id).virtual_available > 0 else 0.0,
                    "marketplace_state": record.marketplace_state,
                    "customer_detail": get_address(record.order_id.partner_id),
                    "shipping_status": record.shipping_Details if record.shipping_Details != False else ''
                }
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "products": vals,
            'symbol': website.company_id.currency_id.symbol if website.company_id.currency_id.symbol != False else ""
        }

        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/pando.images', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def pando_images(self, **kw):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                if not jdata.get('product_id') or not jdata.get('image') or not jdata.get('image_type'):
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)
                for image in jdata.get('image'):
                    dict = {
                        'image_url': image.get('url'),
                        'image_name':image.get('name'),
                        'product_id': int(jdata.get('product_id')),
                        'type': jdata.get('image_type'),
                    }
                    object = request.env['pando.images'].sudo().create(dict)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "message": "success",
            "status": 200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/pando.images.delete', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def pando_images_delete(self, **kw):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                if not jdata.get('product_id') or not jdata.get('image_name'):
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)
                object = request.env['pando.images'].sudo().search([('product_id','=',int(jdata.get('product_id'))),('image_name','in',jdata.get('image_name'))])
                for obj in object:
                    obj.sudo().unlink()
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "message": "success",
            "status": 200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/pando.images.update', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def pando_images_update(self, **kw):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                if not jdata.get('product_id') or not jdata.get('image_name') or jdata.get('image'):
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)

                object = request.env['pando.images'].sudo().search([('product_id','=',int(jdata.get('product_id'))),('image_name','=',jdata.get('image_name'))])
                for obj in object:
                    if jdata.get('image') and request.env.user.id != 4:
                        obj.sudo().write({'image_url': jdata.get('image').get('url'),
                        'image_name':jdata.get('image').get('name')
                        })
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "message": "Record Updated Successfully",
            "status": 200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/product_stock_update', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def product_stock_update(self, **kw):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                if not jdata.get('product_id') or not jdata.get('new_quantity'):
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)
                product = request.env['product.product'].sudo().search([('id','=',int(jdata.get('product_id')))])
                if product:
                    object = request.env['marketplace.stock'].sudo().create({
                        'product_id': product.id,
                        'new_quantity': int(jdata.get('new_quantity')),
                        'location_id': product.marketplace_seller_id.get_seller_global_fields('location_id')
                    })
                    if object:
                        object.request()
                        vals = {
                            "seller_id": request.env.user.partner_id.id,
                            "vendor_message": f"""Inventory Update Request For {product.name} Sent Successfully""",
                            "model": "marketplace.stock",
                            "title": "Requested For Inventory Update"
                        }
                        request.env['notification.center'].sudo().create(vals)

            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "message": "Request Send Successfully",
            "status": 200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/c/product_stock_list', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def product_stock_list(self, **kw):
        try:
            domain = [("marketplace_seller_id", "=", request.env.user.partner_id.id)]
            model = 'marketplace.stock'
            if "status" in kw:
                domain.append(('state','in',[kw.get('status')]))
            limit = 0
            offset = 0
            if "page" in kw:
                limit = 10
                page = int(kw["page"])
                offset = (page - 1) * 10
            record_count = request.env[model].sudo().search_count(domain)
            records = request.env[model].sudo().search(domain, order='id desc', limit=limit, offset=offset)
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            website = request.env['website'].sudo().browse(1)
            warehouse = request.env['stock.warehouse'].sudo().search(
                [('company_id', '=', website.company_id.id)], limit=1)
            temp=[]
            for rec in records:
                sol = request.env['sale.order.line'].sudo().search([('product_id', '=', rec.product_id.id)])
                count = 0
                total = 0
                for line in sol:
                    count += 1
                    total += line.price_total
                category = []
                for z in rec.product_id.public_categ_ids:
                    category.append({"id": z.id, "name": z.name, "slug": z.name.lower().replace(" ", "-"),
                                     "image": base_url.value + '/web/image/product.public.category/' + str(
                                         z.id) + "/image_1920", })

                vals = {
                    'id': rec.id,
                    'productId': rec.product_id.id,
                    'productName': rec.product_id.name,
                    'category': category,
                    'totalOrder': count,
                    'totalAmount': total,
                    "stock": rec.product_id.with_context(warehouse=warehouse.id).virtual_available if rec.product_id.with_context(warehouse=warehouse.id).virtual_available > 0 else 0.0,
                    "status": rec.state,
                    "requestQty": rec.new_quantity,
                    'write_date': str(rec.write_date),
                    'create_date': str(rec.create_date)
                }
                temp.append(vals)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "total_count": record_count,
            "count": len(temp),
            "products": temp,
            "status": 200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/v/product.product.list', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def product_product_list(self, **params):
        try:
            domain = [("marketplace_seller_id", "=", request.env.user.partner_id.id), ('type', '=', 'product'),
                      ('marketplace_status', 'in', ['approved'])]
            model = 'product.product'
            records = request.env[model].sudo().search(domain)
            temp = []
            for rec in records:
                id = []
                for c in rec.product_template_attribute_value_ids:
                    id.append(c.attribute_id.id)
                variant_name = ''
                for attr_id in list(set(id)):
                    for b in rec.product_template_attribute_value_ids:
                        if attr_id == b.attribute_id.id:
                            variant_name += '(' + b.name + ')'
                vals = {
                    'id': rec.id,
                    'name': rec.product_tmpl_id.name + variant_name
                }
                temp.append(vals)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(temp),
            "products": temp
        }
        return return_Response(res)

    @http.route('/api/v1/v/product.status', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def product_status(self, **params):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                if not jdata.get('product_id'):
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)
                product_id = jdata.get('product_id')
                product = request.env['product.product'].sudo().search([('id', '=', int(product_id))])
                publish_state = product.is_product_publish
                if publish_state:
                    product.is_product_publish = False
                else:
                    product.is_product_publish = True
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "message": 'success',
            "status": 200
        }
        return return_Response(res)

    @validate_token
    @http.route(['/api/v1/v/product_product_update','/api/v1/v/product_product_update/<id>'], type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def vendor_product_update(self, id=None, **params):
        try:
            if not id:
                error = {"message": "Id is not present in the request", "status": 400}
                return return_Response_error(error)
            record = request.env['product.product'].sudo().search([('id','=',int(id))])
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                website = request.env['website'].sudo().browse(1)
                if record:
                    dict = {
                        "name": jdata.get('name'),
                        "categ_id": jdata.get('categ_id'),
                        "list_price": jdata.get('list_price'),
                        "standard_price": jdata.get('standard_price'),
                        "description": jdata.get('description') or '',
                        "description_sale": jdata.get('description_sale') or '',
                        "additional_info": jdata.get('additional_info') or '',
                        "uom_id": jdata.get('uom') or 1,
                        "uom_po_id": jdata.get('uom_po_id') or 1,
                        "tracking": jdata.get('tracking') or 'none',
                        "country_id": int(jdata.get('country_id')),
                        "public_categ_ids":[[6, False,[int(jdata.get('public_categ_ids'))]]]
                    }
                    if 'tax' in jdata and jdata.get('tax'):
                        dict['taxes_id'] = [[6, False,[int(jdata.get('tax'))]]]
                    if 'ribbon' in jdata and jdata.get('ribbon'):
                        dict['website_ribbon_id'] = int(jdata.get('ribbon'))
                    # if 'variant' in jdata and jdata.get('variant'):
                    #     lst=[]
                    #     for i in jdata.get('variant').keys():
                    #         if i:
                    #             value = [[6, False,jdata.get('variant')[i]]]
                    #             lst.append([0, 0,{'attribute_id':int(i),'value_ids':value}])
                    #     dict["attribute_line_ids"]= lst
                    resId = record.product_tmpl_id.sudo().write(dict)
                    if resId:
                        vals = {
                            'seller_id': request.env.user.partner_id.id,
                            'vendor_message': f"""{record.name} Updated Successfully""",
                            'model': "product.template",
                            'title': "Product Template"
                        }
                        request.env['notification.center'].sudo().create(vals)
                        record.product_tmpl_id.reject()
                        record.product_tmpl_id.set_pending()
                else:
                    msg = {"message": "No Data Found.", "status_code": 400}
                    return return_Response_error(msg)
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)

        res = {
            'message': "Product updated Successfully",
            'status': 200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/v/picking_address_create', type='http',
                auth='public', methods=['POST'], csrf=False, cors='*')
    def picking_address_create(self, **params):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if not jdata.get('country_id') or not jdata.get('state_id') or not jdata.get('city') or not jdata.get(
                    'address') or not jdata.get('zip'):
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
            uid = request.env.user.id
            user = request.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
            if user:
                userVals = {
                    'pickup_address_line': [(0, 0, {
                        'country_id': int(jdata.get('country_id')),
                        'address': jdata.get('address'),
                        'city': jdata.get('city'),
                        'state_id': int(jdata.get('state_id')),
                        'zip': jdata.get('zip')
                    })]
                }
                user.sudo().write(userVals)
                # user.partner_id.set_to_pending()
                res = {"message": "Picking Address Created Successfully", "status_code": 200}
                vals = {
                    "seller_id": user.partner_id.id,
                    "vendor_message": f"""Picking Address Created Successfully""",
                    "model": "pickup.address",
                    "title": "Picking Address Create"
                }
                request.env['notification.center'].sudo().create(vals)
                return return_Response(res)
        except Exception as e:
            msg = {"message": "Something Went Wrong", "status_code": 400}
            return return_Response_error(msg)

    @validate_token
    @http.route('/api/v1/v/picking_address_update/<id>', type='http',
                auth='public', methods=['POST'], csrf=False, cors='*')
    def picking_address_update(self, id=None, **params):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                uid = request.env.user
                picking_address = request.env['pickup.address'].sudo().search([('id', '=', id)], limit=1)
                if picking_address:
                    pickingVals = {
                        'country_id': jdata.get('country_id') or picking_address.country_id.id,
                        'address': jdata.get('address') or picking_address.address,
                        'city': jdata.get('city') or picking_address.city,
                        'state_id': jdata.get('state_id') or picking_address.state_id.id,
                        'zip': jdata.get('zip') or picking_address.zip
                    }
                    picking_address.sudo().write(pickingVals)
                    # user.partner_id.set_to_pending()
                    res = {"message": "Picking Address Updated Successfully", "status_code": 200}
                    vals = {
                        "seller_id": uid.partner_id.id,
                        "vendor_message": f"""Picking Address Updated Successfully""",
                        "model": "pickup.address",
                        "title": "Picking Address Update"
                    }
                    request.env['notification.center'].sudo().create(vals)
                    return return_Response(res)
                else:
                    msg = {"message": "Picking Address Not Found", "status_code": 400}
                    return return_Response_error(msg)
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except Exception as e:
            msg = {"message": "Something Went Wrong", "status_code": 400}
            return return_Response_error(msg)

    @validate_token
    @http.route(['/api/v1/v/get_picking_address','/api/v1/v/get_picking_address/<id>'], type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_picking_address(self, id=None, **params):
        try:
            user = request.env.user
            if id:
                domain = [('id', '=', int(id))]
            else:
                domain = [('user_id', '=', user.id)]
            picking_address = request.env['pickup.address'].sudo().search(domain, order='id desc')
            temp = []
            for rec in picking_address:
                temp.append({
                    'id': rec.id,
                    'country_id': rec.country_id.id,
                    'country_name': rec.country_id.name,
                    'address': rec.address,
                    'city': rec.city,
                    'state_id': rec.state_id.id,
                    'state_name': rec.state_id.name,
                    'zip': rec.zip
                })
        except Exception as e:
            msg = {"message": "Something Went Wrong", "status_code": 400}
            return return_Response_error(msg)
        res = {
            'count': len(temp),
            'record': temp,
            'status': 200
        }
        return return_Response(res)

    @validate_token
    @http.route('/api/v1/v/get_vendor_address', type='http',
                auth='public', methods=['POST'], csrf=False, cors='*')
    def get_vendor_address(self, id=None, **params):
        try:
            user = request.env.user
            if user and user.id != 4:
                record = {
                    'account_number': user.account_number,
                    'account_name': user.account_name,
                    'ifsc_code': user.ifsc_code,
                    'owner_name': user.owner_name,
                    'business_name': user.business_name,
                    'supplier_country_id': user.supplier_country_id.id,
                    'supplier_country_name': user.supplier_country_id.name,
                    'supplier_state_id': user.supplier_state_id.id,
                    'supplier_state_name': user.supplier_state_id.name,
                    'supplier_phone': user.supplier_phone,
                    'supplier_city': user.supplier_city,
                    'supplier_address': user.supplier_address,
                    'partner_details': get_address(user.partner_id)
                }
                res = {
                    'record': record,
                    'status': 200
                }
                return return_Response(res)
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except Exception as e:
            msg = {"message": "Something Went Wrong", "status_code": 400}
            return return_Response_error(msg)

    @validate_token
    @http.route('/api/v1/v/generate_invoice_report', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def generate_invoice_report(self, **params):
        try:
            domain = [('product_id.marketplace_seller_id', '=', request.env.user.partner_id.id), ('move_id.payment_state', 'in', ['paid', 'not_paid'])]
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                domain.append(('date', '>=', jdata.get('from_date')))
                domain.append(('date', '<=', jdata.get('to_date')))

            if "quator" in params and params.get('quator'):
                from_date = datetime.datetime.now().date()
                if params.get('quator') == 'week':
                    to_date = from_date - timedelta(days=7)
                if params.get('quator') == 'month':
                    to_date = from_date - timedelta(days=30)
                if params.get('quator') == 'q1':
                    to_date = from_date - timedelta(days=90)
                if params.get('quator') == 'q2':
                    to_date = from_date - timedelta(days=180)
                if params.get('quator') == 'q3':
                    to_date = from_date - timedelta(days=270)
                if params.get('quator') == 'q4':
                    to_date = from_date - timedelta(days=365)
                if from_date and to_date:
                    domain.append(('date', '>=', from_date))
                    domain.append(('date', '<=', to_date))
            if domain:
                records = request.env['account.move.line'].sudo().search(domain, order='id desc')
                temp = []
                total = 0
                for rec in records:
                    if not rec.exclude_from_invoice_tab:
                        vals = {
                            'id': rec.id,
                            'name': rec.move_id.name,
                            'productName': rec.name,
                            'price_unit': rec.price_unit,
                            "qty": rec.quantity,
                            'price_subtotal': rec.price_subtotal,
                            'price_total': rec.price_total
                        }
                        tax = []
                        record = request.env['account.move.line'].sudo().search([('product_id', '=', rec.product_id.id), ('move_id', '=', rec.move_id.id)], order='id desc')
                        for r in record:
                            if r.exclude_from_invoice_tab:
                                v = {
                                    'name': r.name,
                                    'taxAmount': r.price_unit
                                }
                                tax.append(v)
                        vals['tax'] = tax
                        temp.append(vals)
                        total += rec.price_total
                res = {
                    'record': temp,
                    'totalAmount': round(total, 2),
                    'status': 200
                }
                return return_Response(res)
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except Exception as e:
            msg = {"message": "Something Went Wrong", "status_code": 400}
            return return_Response_error(msg)

