# -*- coding: utf-8 -*-
from .main import *
from odoo import models, fields, api


_logger = logging.getLogger(__name__)

# List of REST resources in current file:
#   (url prefix)                (method)     (action)
# /api/res.partner                GET     - Read all (with optional filters, offset, limit, order)
# /api/res.partner/<id>           GET     - Read one
# /api/res.partner                POST    - Create one
# /api/res.partner/<id>           PUT     - Update one
# /api/res.partner/<id>           DELETE  - Delete one
# /api/res.partner/<id>/<method>  PUT     - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/res.partner  GET  - Read all (with optional filters, offset, limit, order)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional filters (Odoo domain), offset, limit, order)
#           {                                       # editable
#               "filters": "[('some_field_1', '=', some_value_1), ('some_field_2', '!=', some_value_2), ...]",
#               "offset":  XXX,
#               "limit":   XXX,
#               "order":   "list_of_fields"  # default 'name asc'
#           }
# OUT data:
OUT__res_partner__read_all__SUCCESS_CODE = 200  # editable
#   JSON:
#       {
#           "count":   XXX,     # number of returned records
#           "results": [
OUT__res_partner__read_all__JSON = (  # editable
    'id',
    'image',
    'company_type',
    'name',
    'street',
    'street2',
    'city',
    'zip',
    'website',
    'function',
    'phone',
    'mobile',
    'fax',
    'email',
    'lang',
    'customer',
    'supplier',
    'partner_latitude',
    'partner_longitude',
    'x_client',
    'create_date',
    'write_date',
    'x_pan',
    'x_dob',
    'x_gstin',

    # many2one fields:
    ('parent_id', (
        'id',
        'name',
    )),

    ('user_id', (
        'id',
        'name',
    )),
    ('state_id', (
        'id',
        'name',
    )),
    ('title', (
        'id',
        'name',
    )),
    ('country_id', (
        'id',
        'name',
        'code',
    )),
    ('x_category', [(
        'id',
        'name',
    )]),
    ('category_id', [(
        'id',
        'name',
    )]),
    # one2many fields:
    # ('bank_ids', [(
    #     'id',
    #     'acc_number',
    #     'bank_bic',
    # )]),
    # many2many fields:
    # ('category_id', [(
    #     'id',
    #     'name',
    # )]),
    # ('x_subcategory', [(
    #     'id',
    #     'name',
    # )]),
    # ('x_category', [(
    #     'id',
    #     'name',
    # )]),
)
#           ]
#       }

# /api/res.partner/<id>  GET  - Read one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional parameter 'search_field' for search object not by 'id' field)
#           {"search_field": "some_field_name"}     # editable
# OUT data:
OUT__res_partner__read_one__SUCCESS_CODE = 200  # editable
OUT__res_partner__read_one__JSON = (  # editable
    # (The order of fields of different types maybe arbitrary)
    # simple fields (non relational):
    'id',
    'image',
    'company_type',
    'name',
    'street',
    'street2',
    'city',
    'zip',
    'website',
    'function',
    'phone',
    'mobile',
    'fax',
    'email',
    'lang',
    'customer',
    'supplier',
    'partner_latitude',
    'partner_longitude',
    'x_client',
    'create_date',
    'write_date',
    'x_pan',
    'x_dob',
    'x_gstin',

    # many2one fields:
    ('parent_id', (
        'id',
        'name',
    )),
    # ('x_category', (
    #     'id',
    #     'name',
    # )),
    # ('x_category', (
    #     'id',
    #     'name',
    # )),
    ('user_id', (
        'id',
        'name',
    )),
    ('state_id', (
        'id',
        'name',
    )),
    ('title', (
        'id',
        'name',
    )),
    ('country_id', (
        'id',
        'name',
        'code',
    )),
    # one2many fields:
    # ('bank_ids', [(
    #     'id',
    #     'acc_number',
    #     'bank_bic',
    # )]),
    # many2many fields:
    ('x_category', [(
        'id',
        'name',
    )]),
    # ('x_subcategory', [(
    #     'id',
    #     'name',
    # )]),
    ('category_id', [(
        'id',
        'name',
    )]),
)

# /api/res.partner  POST  - Create one
# IN data:
#   HEADERS:
#       'access_token'
#   DEFAULTS:
#       (optional default values of fields)
DEFAULTS__res_partner__create_one__JSON = {  # editable
    # "some_field_1": some_value_1,
    # "some_field_2": some_value_2,
    # ...
}
#   JSON:
#       (fields and its values of created object;
#        don't forget about model's mandatory fields!)
#           ...                                     # editable
# OUT data:
OUT__res_partner__create_one__SUCCESS_CODE = 200  # editable
OUT__res_partner__create_one__JSON = (  # editable
    'id',
)

# /api/res.partner/<id>  PUT  - Update one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (fields and new values of updated object)   # editable
#           ...
# OUT data:
OUT__res_partner__update_one__SUCCESS_CODE = 200  # editable

# /api/res.partner/<id>  DELETE  - Delete one
# IN data:
#   HEADERS:
#       'access_token'
# OUT data:
OUT__res_partner__delete_one__SUCCESS_CODE = 200  # editable

# /api/res.partner/<id>/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__res_partner__call_method__SUCCESS_CODE = 200  # editable


# HTTP controller of REST resources:

class ControllerREST(http.Controller):

    # Read all (with optional filters, offset, limit, order):
    @http.route('/api/bimabachat/res.partner1', methods=['GET'], type='http', auth='none', cors='*')
    @check_permissions
    def api__res_partner__GET(self, **kw):
        return wrap__resource__read_all(
            modelname='res.partner',
            default_domain=[],
            success_code=OUT__res_partner__read_all__SUCCESS_CODE,
            OUT_fields=OUT__res_partner__read_all__JSON
        )

    # Read one:
    @http.route('/api/bimabachat/res.partner1/<id>', methods=['GET'], type='http', auth='none', cors='*')
    @check_permissions
    def api__res_partner__id_GET(self, id, **kw):
        return wrap__resource__read_one(
            modelname='res.partner',
            id=id,
            success_code=OUT__res_partner__read_one__SUCCESS_CODE,
            OUT_fields=OUT__res_partner__read_one__JSON
        )

    # Create one:
    @http.route('/api/bimabachat/res.partner1', methods=['POST'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__res_partner__POST(self):
        return wrap__resource__create_one(
            modelname='res.partner',
            default_vals=DEFAULTS__res_partner__create_one__JSON,
            success_code=OUT__res_partner__create_one__SUCCESS_CODE,
            OUT_fields=OUT__res_partner__create_one__JSON
        )

    # Update one:
    @http.route('/api/bimabachat/res.partner1/<id>', methods=['PUT'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__res_partner__id_PUT(self, id):
        return wrap__resource__update_one(
            modelname='res.partner',
            id=id,
            success_code=OUT__res_partner__update_one__SUCCESS_CODE
        )

    # Delete one:
    @http.route('/api/bimabachat/res.partner1/<id>', methods=['DELETE'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__res_partner__id_DELETE(self, id):
        return wrap__resource__delete_one(
            modelname='res.partner',
            id=id,
            success_code=OUT__res_partner__delete_one__SUCCESS_CODE
        )

    # Call method (with optional parameters):
    @http.route('/api/bimabachat/res.partner1/<id>/<method>', methods=['PUT'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__res_partner__id__method_PUT(self, id, method):
        return wrap__resource__call_method(
            modelname='res.partner',
            id=id,
            method=method,
            success_code=OUT__res_partner__call_method__SUCCESS_CODE
        )

    @http.route('/api/change_password', methods=['POST'],type='http', website=True, auth="public", csrf=False, cors="*")
    @check_permissions
    def app_change_password(self, **kw):
        old_password = kw['old_password']
        new_password = kw['new_password']
        confirm_password = kw['confirm_password']
        uid = request.session.uid
        db_name = odoo.tools.config.get('db_name')
        dbname = db_name
        if not old_password and new_password and confirm_password:
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps(
                    {'error': _('Mandatory Field is Required ,old_password,new_password,confirm_password'),
                     'title': _('Change Password'), "status_code": 400})
            )
        if new_password != confirm_password:
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({'error': _('The new password and its confirmation must be identical.'),
                                     'title': _('Change Password')
                                        , "status_code": 400})
            )
        try:
            if request.env['res.users'].change_passwords(uid, dbname, old_password, new_password):
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps(
                        {'new_password': new_password, "message": "Successfully Updated", "status_code": 200})
                )
        except Exception as e:
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps(
                    {'error': _('The old password you provided is incorrect, your password was not changed.'),
                     'title': _('Change Password'), "status_code": 400,"errors":str(e)})

            )

        return werkzeug.wrappers.Response(
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'),
                     ('Pragma', 'no-cache')],
            response=json.dumps(
                {'error': _('Error, password not changed !'), 'title': _('Change Password'), "status_code": 400})

        )


    @http.route('/api/bimabachat/res.partner2/<id>',  methods=['POST','GET'],type='http', website=True, auth="public", csrf=False, cors="*")
    @check_permissions
    def partner_get(self,id):
        data=request.env['res.partner'].sudo().search([('id','=',id)])
        if data:
            temp=[]
            for i in data:
                temp.append({
                    "id": i.id if i.id != False else '',
                    "name": i.name if i.name != False else '',
                    "parent_id": {"id": i.parent_id.id,
                                  "name": i.parent_id.name} if i.parent_id.id != False else '',
                    "user_id": {"id": i.user_id.id,
                                "name": i.user_id.name} if i.user_id.id != False else '',
                    "state_id": {"id": i.state_id.id, "name": i.state_id.name} if i.state_id.id != False else '',
                    "country_id": {"id": i.country_id.id,
                                   "name": i.country_id.name} if i.country_id.id != False else '',
                    "title": {"id": i.title.id, "name": i.title.name} if i.title.id != False else '',
                    "image": i.image if i.image != False else '',
                    "company_type": i.company_type if i.company_type != False else '',
                    "street": i.street if i.street != False else '',
                    "street2": i.street2 if i.street2 != False else '',
                    "city": i.city if i.city != False else '',
                    "zip": i.zip if i.zip != False else '',
                    "website": i.website if i.website != False else '',
                    "function": i.function if i.function != False else '',
                    "phone": i.phone if i.phone != False else '',
                    "mobile": i.mobile if i.mobile != False else '',
                    "fax": i.fax if i.fax != False else '',
                    "email": i.email if i.email != False else '',
                    "lang": i.lang if i.lang != False else '',
                    "customer": i.customer if i.customer != False else '',
                    "supplier": i.supplier if i.supplier != False else '',
                    "partner_latitude": i.partner_latitude if i.partner_latitude != False else '',
                    "partner_longitude": i.partner_longitude if i.partner_longitude != False else '',
                    "x_client": i.x_client if i.x_client != False else '',
                    "create_date": i.create_date if i.create_date != False else '',
                    "write_date": i.write_date if i.write_date != False else '',
                    "x_pan": i.x_pan if i.x_pan != False else '',
                    "x_dob": i.x_dob if i.x_dob != False else '',
                    "x_gstin": i.x_gstin if i.x_gstin != False else '',
                    "x_refer": i.x_refer if i.x_refer != False else '',


                })
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps(
                    {'data':temp, "status_code": 200,})

            )
        if not data:
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps(
                    {"status_code": 400,'data':"No record Found" })

            )

    @http.route('/api/bimabachat/customer',methods=['GET'],type='http', website=True, auth="public", csrf=False, cors="*")
    @check_permissions
    def partner_get_customer(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        uid = request.session.uid
        datas = request.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        datass = request.env['res.partner'].sudo().search([('x_client', '=', True)])
        data =datass.sudo().search(['|',('id', '=', datas.partner_id.id),('create_uid','=',uid)])
        if data:
            temp = []
            for i in data:
                q1 = http.request.env['ir.attachment'].sudo().search([('res_id', '=', i.id)])
                temps = []
                if q1:
                    for z in q1:
                        temps.append({"name": z.name,
                                      "url": 'https://bimabachat.in/web/content/' + str(z.id) + '?download=true'})
                temp.append({
                    "id": i.id if i.id != False else '',
                    "name": i.name if i.name != False else '',
                    "parent_id": {"id": i.parent_id.id,
                                  "name": i.parent_id.name} if i.parent_id.id != False else '',
                    "user_id": {"id": i.user_id.id,
                                "name": i.user_id.name} if i.user_id.id != False else '',
                    "state_id": {"id": i.state_id.id, "name": i.state_id.name} if i.state_id.id != False else '',
                    "country_id": {"id": i.country_id.id,
                                   "name": i.country_id.name} if i.country_id.id != False else '',
                    "title": {"id": i.title.id, "name": i.title.name} if i.title.id != False else '',
                    "image": i.image if i.image != False else '',
                    "company_type": i.company_type if i.company_type != False else '',
                    "street": i.street if i.street != False else '',
                    "street2": i.street2 if i.street2 != False else '',
                    "city": i.city if i.city != False else '',
                    "zip": i.zip if i.zip != False else '',
                    "website": i.website if i.website != False else '',
                    "function": i.function if i.function != False else '',
                    "phone": i.phone if i.phone != False else '',
                    "mobile": i.mobile if i.mobile != False else '',
                    "fax": i.fax if i.fax != False else '',
                    "email": i.email if i.email != False else '',
                    "lang": i.lang if i.lang != False else '',
                    "customer": i.customer if i.customer != False else '',
                    "supplier": i.supplier if i.supplier != False else '',
                    "partner_latitude": i.partner_latitude if i.partner_latitude != False else '',
                    "partner_longitude": i.partner_longitude if i.partner_longitude != False else '',
                    "x_client": i.x_client if i.x_client != False else '',
                    "create_date": i.create_date if i.create_date != False else '',
                    "write_date": i.write_date if i.write_date != False else '',
                    "x_pan": i.x_pan if i.x_pan != False else '',
                    "x_dob": i.x_dob if i.x_dob != False else '',
                    "x_gstin": i.x_gstin if i.x_gstin != False else '',
                    "x_refer": i.x_refer if i.x_refer != False else '',
                    "attachment_id":temps

                })

            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps(
                    {'data': temp, "status_code": 200, })

            )
        if not data:
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps(
                    {"status_code": 200, "data": []})
            )

    @http.route('/api/bimabachat/res.partner2', methods=['POST','GET'],type='http', auth='none',csrf=False, cors='*')
    @check_permissions
    def partner_get_id(self):

        print("CUSTOMER BLOCK")
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}

        uid = request.session.uid
        create_date =jdata.get('create_date')
        write_date =jdata.get('write_date')
        customer =jdata.get('customer')
        print(customer,write_date,create_date,uid,"DATA PRINTED VALUES")




        if create_date !=None or create_date ==False:
            print("1")
            data = request.env['res.partner'].sudo().search([('create_date','>=',create_date)])
            if data:
                temp = []
                for i in data:
                    q1 = http.request.env['ir.attachment'].sudo().search([('res_id', '=', i.id)])
                    temps = []
                    if q1:
                        for z in q1:
                            temps.append({"name": z.name,
                                          "url": 'https://bimabachat.in/web/content/' + str(z.id) + '?download=true'})

                    temp.append({
                        "id": i.id if i.id != False else '',
                        "name": i.name if i.name != False else '',
                        "parent_id": {"id": i.parent_id.id,
                                      "name": i.parent_id.name} if i.parent_id.id != False else {"name":"Group Head"},
                        "user_id": {"id": i.user_id.id,
                                    "name": i.user_id.name} if i.user_id.id != False else '',
                        "state_id": {"id": i.state_id.id, "name": i.state_id.name} if i.state_id.id != False else '',
                        "country_id": {"id": i.country_id.id, "name": i.country_id.name}  if i.country_id.id != False else '',
                        "title":{"id":i.title.id,"name":i.title.name} if i.title.id != False else '',
                        "image": i.image if i.image != False else '',
                        "company_type": i.company_type if i.company_type != False else '',
                        "street": i.street if i.street != False else '',
                        "street2": i.street2 if i.street2 != False else '',
                        "city": i.city if i.city != False else '',
                        "zip": i.zip if i.zip != False else '',
                        "website": i.website if i.website != False else '',
                        "function": i.function if i.function != False else '',
                        "phone": i.phone if i.phone != False else '',
                        "mobile": i.mobile if i.mobile != False else '',
                        "fax": i.fax if i.fax != False else '',
                        "email": i.email if i.email != False else '',
                        "lang": i.lang if i.lang != False else '',
                        "customer": i.customer if i.customer != False else '',
                        "supplier": i.supplier if i.supplier != False else '',
                        "partner_latitude": i.partner_latitude if i.partner_latitude != False else '',
                        "partner_longitude": i.partner_longitude if i.partner_longitude != False else '',
                        "x_client": i.x_client if i.x_client != False else '',
                        "create_date": i.create_date if i.create_date != False else '',
                        "write_date": i.write_date if i.write_date != False else '',
                        "x_pan": i.x_pan if i.x_pan != False else '',
                        "x_dob": i.x_dob if i.x_dob != False else '',
                        "x_gstin": i.x_gstin if i.x_gstin != False else '',
                        "x_refer": i.x_refer if i.x_refer != False else '',
                        "attachment_id":temps
                    })
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps(
                        {'data': temp, "status_code": 200, })

                )

            if not data:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps(
                        {"status_code": 200, "data":[]})

                )
        elif write_date !=None or write_date ==False:
            print("2")
            data = request.env['res.partner'].sudo().search([('write_date', '>=', write_date)])
            if data:
                temp = []
                for i in data:
                    # if i.parent_id.id ==False:
                    #     parent_id =''
                    q1 = http.request.env['ir.attachment'].sudo().search([('res_id', '=', i.id)])
                    temps = []
                    if q1:
                        for z in q1:
                            temps.append({"name": z.name,
                                          "url": 'https://bimabachat.in/web/content/' + str(z.id) + '?download=true'})

                    temp.append({
                        "id": i.id if i.id != False else '',
                        "name": i.name if i.name != False else '',
                        "parent_id": {"id": i.parent_id.id,
                                      "name": i.parent_id.name} if i.parent_id.id != False else {"name":"Group Head"},
                        "user_id": {"id": i.user_id.id,
                                    "name": i.user_id.name} if i.user_id.id != False else '',
                        "state_id": {"id": i.state_id.id, "name": i.state_id.name} if i.state_id.id != False else '',
                        "country_id": {"id": i.country_id.id,
                                       "name": i.country_id.name} if i.country_id.id != False else '',
                        "title": {"id": i.title.id, "name": i.title.name} if i.title.id != False else '',
                        "image": i.image if i.image != False else '',
                        "company_type": i.company_type if i.company_type != False else '',
                        "street": i.street if i.street != False else '',
                        "street2": i.street2 if i.street2 != False else '',
                        "city": i.city if i.city != False else '',
                        "zip": i.zip if i.zip != False else '',
                        "website": i.website if i.website != False else '',
                        "function": i.function if i.function != False else '',
                        "phone": i.phone if i.phone != False else '',
                        "mobile": i.mobile if i.mobile != False else '',
                        "fax": i.fax if i.fax != False else '',
                        "email": i.email if i.email != False else '',
                        "lang": i.lang if i.lang != False else '',
                        "customer": i.customer if i.customer != False else '',
                        "supplier": i.supplier if i.supplier != False else '',
                        "partner_latitude": i.partner_latitude if i.partner_latitude != False else '',
                        "partner_longitude": i.partner_longitude if i.partner_longitude != False else '',
                        "x_client": i.x_client if i.x_client != False else '',
                        "create_date": i.create_date if i.create_date != False else '',
                        "write_date": i.write_date if i.write_date != False else '',
                        "x_pan": i.x_pan if i.x_pan != False else '',
                        "x_dob": i.x_dob if i.x_dob != False else '',
                        "x_gstin": i.x_gstin if i.x_gstin != False else '',
                        "x_refer": i.x_refer if i.x_refer != False else '',
                        "attachment_id":temps

                    })

                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps(
                        {'data': temp, "status_code": 200, })

                )
            if not data:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps(
                        {"status_code": 200, "data":[]})
                )
        elif customer:
            print("3")
            datas = request.env['res.users'].sudo().search([('id', '!=',uid)],limit=1)
            print datas.partner_id.id,"DATAT"
            print customer,"CUSTOMER"
            # if customer == 'false':
            #     customer =True
            data = request.env['res.partner'].search([('x_client', '=', True)])
            if data:
                temp = []
                for i in data:
                    temp.append({
                        "id": i.id if i.id != False else '',
                        "name": i.name if i.name != False else '',
                    })

                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps(
                        {'data': temp, "status_code": 200, })

                )
            if not data:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps(
                        {"status_code": 200, "data": []})
                )

        else:
            uid=request.session.uid
            datas = request.env['res.users'].sudo().search([('id', '=',uid)],limit=1)
            data123 = request.env['res.partner'].sudo().search(['|',('id','=',datas.partner_id.id),('create_uid','=',uid)]).ids
            data12 = request.env['res.partner'].sudo().search([('id','=',datas.partner_id.id)]).child_ids.ids
            final=[]
            for x in data123 + data12:
                if x not in final:
                    final.append(x)

            data = request.env['res.partner'].sudo().search([('id','in',final)])

            if data:
                temp = []
                for i in data:
                    q1 = http.request.env['ir.attachment'].sudo().search([('res_id', '=', i.id)])
                    temps = []
                    if q1:
                        for z in q1:
                            temps.append({
                                          "id": z.id,
                                          "name": z.name,
                                          "url": 'https://bimabachat.in/web/content/' + str(z.id) + '?download=true'})
                    temp.append({
                        "id": i.id if i.id != False else '',
                        "name": i.name if i.name != False else '',
                        "parent_id": {"id": i.parent_id.id,
                                      "name": i.parent_id.name} if i.parent_id.id != False else {"name":"Group Head"},
                        "user_id": {"id": i.user_id.id,
                                    "name": i.user_id.name} if i.user_id.id != False else '',
                        "state_id": {"id": i.state_id.id, "name": i.state_id.name} if i.state_id.id != False else '',
                        "country_id": {"id": i.country_id.id,
                                       "name": i.country_id.name} if i.country_id.id != False else '',
                        "title": {"id": i.title.id, "name": i.title.name} if i.title.id != False else '',
                        "image": i.image if i.image != False else '',
                        "company_type": i.company_type if i.company_type != False else '',
                        "street": i.street if i.street != False else '',
                        "street2": i.street2 if i.street2 != False else '',
                        "city": i.city if i.city != False else '',
                        "zip": i.zip if i.zip != False else '',
                        "website": i.website if i.website != False else '',
                        "function": i.function if i.function != False else '',
                        "phone": i.phone if i.phone != False else '',
                        "mobile": i.mobile if i.mobile != False else '',
                        "fax": i.fax if i.fax != False else '',
                        "email": i.email if i.email != False else '',
                        "lang": i.lang if i.lang != False else '',
                        "customer": i.customer if i.customer != False else '',
                        "supplier": i.supplier if i.supplier != False else '',
                        "partner_latitude": i.partner_latitude if i.partner_latitude != False else '',
                        "partner_longitude": i.partner_longitude if i.partner_longitude != False else '',
                        "x_client": i.x_client if i.x_client != False else '',
                        "create_date": i.create_date if i.create_date != False else '',
                        "write_date": i.write_date if i.write_date != False else '',
                        "x_pan": i.x_pan if i.x_pan != False else '',
                        "x_dob": i.x_dob if i.x_dob != False else '',
                        "x_gstin": i.x_gstin if i.x_gstin != False else '',
                        "x_refer": i.x_refer if i.x_refer != False else '',
                        "attachment_id":temps
                    })


                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps(
                        {"status_code": 200, "data":temp})

                )



            if not data:
                return werkzeug.wrappers.Response(
                   content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps(
                        {"status_code": 200, "data":[]})

                )

    # @http.route('/api/bimabachat/createcontact', type='http', methods=['POST'], auth='auth',cors='*')
    # @http.route('/api/bimabachat/createcontact', methods=['POST'], type='http', auth='none', csrf=False, cors='*')
    # @check_permissions
    # def respartnercreate(self):
    #     try:
    #         try:
    #             jdata = json.loads(request.httprequest.stream.read())
    #         except:
    #             jdata = {}
    #         # uid = jdata.get('uid')
    #         name = jdata.get('name')
    #         x_client = jdata.get('x_client')
    #         parent_id = jdata.get('parent_id')
    #         user_id = jdata.get('user_id')
    #         partner_latitude = jdata.get('partner_latitude')
    #         partner_longitude = jdata.get('partner_longitude')
    #         attachment_id = jdata.get('attachment_id')
    #         email = jdata.get('email')
    #         company_type = jdata.get('company_type')
    #         mobile = jdata.get('mobile')
    #         x_pan = jdata.get('x_pan')
    #         website = jdata.get('website')
    #         function = jdata.get('function')
    #         title = jdata.get('title')
    #         x_gstin = jdata.get('x_gstin')
    #         x_dob = jdata.get('x_dob')
    #         street = jdata.get('street')
    #         street2 = jdata.get('street2')
    #         city = jdata.get('city')
    #         state_id = jdata.get('state_id')
    #         zip = jdata.get('zip')
    #         country_id = jdata.get('country_id')
    #         phone = jdata.get('phone')
    #         fax = jdata.get('fax')
    #         category_id = jdata.get('category_id')
    #         child_ids = jdata.get('child_ids')
    #         partner_id = jdata.get('partner_id')
    #
    #         category = []
    #         print jdata, "jdta"
    #         if category_id != None:
    #             for x in category_id:
    #                 category.append(x['id'])
    #
    #         vals = {
    #             # "create_uid": uid,
    #             # "write_uid": uid,
    #             "name": name,
    #             "company_type": company_type,
    #             "parent_id": parent_id,
    #             "x_client": x_client,
    #             "user_id": user_id,
    #             "partner_longitude": partner_longitude,
    #             "partner_latitude": partner_latitude,
    #             "email": email,
    #             "mobile": mobile,
    #             "function": function,
    #             "x_pan": x_pan,
    #             "website": website,
    #             "title": title,
    #             "x_gstin": x_gstin,
    #             "x_dob": x_dob,
    #             "street": street,
    #             "street2": street2,
    #             "city": city,
    #             "state_id": state_id,
    #             "zip": zip,
    #             "country_id": country_id,
    #             "phone": phone,
    #             "fax": fax,
    #             "category_id": [[6, False, category]]
    #
    #         }
    #         cr, uid = registry.cursor(), request.session.uid
    #         cr._cnx.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
    #         Model = request.env(cr, uid)['res.partner']
    #         q1 = Model.create(vals)
    #         cr.commit()
    #         cr.close()
    #         if q1:
    #             for k in attachment_id:
    #                 attach_update = http.request.env['ir.attachment'].sudo().search([('id', '=', k)])
    #                 attach_update.write({"res_id": q1.id})
    #         return werkzeug.wrappers.Response(
    #             content_type='application/json; charset=utf-8',
    #             headers=[('Cache-Control', 'no-store'),
    #                      ('Pragma', 'no-cache')],
    #             response=json.dumps({
    #                 'id': q1.id,
    #                 "status": 200,
    #                 "message": "created successfully"
    #             }),
    #         )
    #
    #     except Exception as e:
    #         return werkzeug.wrappers.Response(
    #             content_type='application/json; charset=utf-8',
    #             headers=[('Cache-Control', 'no-store'),
    #                      ('Pragma', 'no-cache')],
    #             response=json.dumps({
    #                 'error': e,
    #                 "status": 400,
    #                 "message": "not created"
    #             }),
    #         )

    @http.route('/api/bimabachat/createcontact', methods=['POST'], type='http',auth="public", csrf=False, cors='*')
    @check_permissions
    def respartnercreate(self):
        # try:
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        partner_id = jdata.get('partner_id')
        if not partner_id:
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    "status": 400,
                    "message": "Partner_id is Required"
                }),
            )
        x_client = jdata.get('x_client')
        name = jdata.get('name')
        parent_id = jdata.get('parent_id')
        user_id = jdata.get('user_id')
        partner_latitude = jdata.get('partner_latitude')
        partner_longitude = jdata.get('partner_longitude')
        attachment_id = jdata.get('attachment_id')
        email = jdata.get('email')
        image = jdata.get('image')
        company_type = jdata.get('company_type')
        mobile = jdata.get('mobile')
        x_pan = jdata.get('x_pan')
        website = jdata.get('website')
        function = jdata.get('function')
        title = jdata.get('title')
        x_gstin = jdata.get('x_gstin')
        x_dob = jdata.get('x_dob')
        street = jdata.get('street')
        street2 = jdata.get('street2')
        city = jdata.get('city')
        state_id = jdata.get('state_id')
        zip = jdata.get('zip')
        country_id = jdata.get('country_id')
        phone = jdata.get('phone')
        fax = jdata.get('fax')
        category_id = jdata.get('category_id')
        category_id = jdata.get('category_id')

        category = []
        print jdata, "jdta"
        if category_id != None:
            for x in category_id:
                category.append(x['id'])

        data = http.request.env['res.partner'].search([('id', '=', partner_id)])
        vals = {"name": name,
                "image": image,
                "phone": data.phone,
                "type": "private",
                "street": data.street,
                "street2": data.street2,
                "state_id": data.state_id.id,
                "city": data.city,
                "country_id": data.country_id.id,
                "zip": data.zip,
                "company_type": company_type,
                "parent_id": parent_id,
                "x_client": True,
                "user_id": data.user_id.id,
                "partner_longitude": partner_longitude,
                "partner_latitude": partner_latitude,
                "email": email,
                "mobile": mobile,
                "function": function,
                "x_pan": x_pan,
                "website": website,
                "title": title,
                "x_gstin": x_gstin,
                "x_dob": x_dob,
                "fax": fax,
                "category_id": [[6, False, category]]

                }
        cr, uid = registry.cursor(), request.session.uid
        cr._cnx.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        Model = request.env(cr, uid)['res.partner']
        q1 = Model.create(vals)
        print(q1, "SSSSSSS")
        cr.commit()
        cr.close()
        print(partner_id, q1.id, "print q1")
        cr, uid = registry.cursor(), request.session.uid
        cr._cnx.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        Model = request.env(cr, uid)['res.partner']
        q2 = Model.search([('id', '=', partner_id)])
        q2.sudo().write({"child_ids": [(4, q1.id)]})
        cr.commit()
        cr.close()
        if q1:
            if attachment_id == None:
                pass
            else:
                for k in attachment_id:
                    cr, uid = registry.cursor(), request.session.uid
                    cr._cnx.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
                    Model = request.env(cr, uid)['ir.attachment']
                    q3 = Model.search([('id', '=',  int(k))])
                    q3.sudo().write({"res_id": q1.id})
                    cr.commit()
                    cr.close()
                    # attach_update = http.request.env['ir.attachment'].sudo().search([('id', '=', int(k))])
                    # print(attach_update,"ATC")
                    # attach_update.sudo().write({"res_id": q1.id})

        return werkzeug.wrappers.Response(
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'),
                     ('Pragma', 'no-cache')],
            response=json.dumps({
                "id": q1.id,
                "status": 200,
                "message": "created successfully"
            }),
        )

        # except Exception as e:
        #     return werkzeug.wrappers.Response(
        #         content_type='application/json; charset=utf-8',
        #         headers=[('Cache-Control', 'no-store'),
        #                  ('Pragma', 'no-cache')],
        #         response=json.dumps({
        #             'error': e,
        #             "status": 400,
        #             "message": "not created"
        #         }),
        #     )

    @http.route('/api/bimabachat/editcontact/<id>/', methods=['POST','PUT'], type='http', auth="public", csrf=False, cors='*')
    @check_permissions
    def respartneredit(self,id):
        try:
            partner_id = id
            print(partner_id,"IDD")
            if not partner_id:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        "status": 400,
                        "message": "Partner_id is Required"
                    }),
                )
            data = http.request.env['res.partner'].search([('id', '=', partner_id)])
            print(data,"DATA")
            if not data:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        "status": 400,
                        "message": "no data found"
                    }),
                )
            else:
                try:
                    jdata = json.loads(request.httprequest.stream.read())
                except:
                    jdata = {}
                x_client = jdata.get('x_client')
                name = jdata.get('name')
                image = jdata.get('image')
                parent_id = jdata.get('parent_id')
                user_id = jdata.get('user_id')
                partner_latitude = jdata.get('partner_latitude')
                partner_longitude = jdata.get('partner_longitude')
                attachment_id = jdata.get('attachment_id')
                email = jdata.get('email')
                company_type = jdata.get('company_type')
                mobile = jdata.get('mobile')
                x_pan = jdata.get('x_pan')
                website = jdata.get('website')
                function = jdata.get('function')
                title = jdata.get('title')
                x_gstin = jdata.get('x_gstin')
                x_dob = jdata.get('x_dob')
                street = jdata.get('street')
                street2 = jdata.get('street2')
                city = jdata.get('city')
                state_id = jdata.get('state_id')
                zip = jdata.get('zip')
                country_id = jdata.get('country_id')
                phone = jdata.get('phone')
                fax = jdata.get('fax')
                category_id = jdata.get('category_id')
                category = []
                print jdata, "jdta"
                if category_id != None:
                    for x in category_id:
                        category.append(x['id'])
                # data = http.request.env['res.partner'].search([('id', '=', partner_id)])
                vals = {"name": name,
                        "phone":phone,
                        "type": "private",
                        "street": street,
                        "street2": street2,
                        "state_id": state_id,
                        "city": city,
                        "country_id": country_id,
                        "zip": zip,
                        "company_type": company_type,
                        "parent_id": parent_id,
                        "x_client": True,
                        "user_id": user_id,
                        "partner_longitude": partner_longitude,
                        "partner_latitude": partner_latitude,
                        "email": email,
                        "mobile": mobile,
                        "function": function,
                        "x_pan": x_pan,
                        "website": website,
                        "title": title,
                        "x_gstin": x_gstin,
                        "x_dob": x_dob,
                        "fax": fax,
                        "image":image,
                        "category_id": [[6, False, category]]
                        }
                data.write(vals)
                if data:
                    if attachment_id == None:
                        pass
                    else:
                        for k in attachment_id:
                            attach_update = http.request.env['ir.attachment'].sudo().search([('id', '=', k)])
                            if attach_update:
                                attach_update.write({"res_id": data.id})
                            else:
                                pass
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        "id": data.id,
                        "status": 200,
                        "message": "Updated successfully"
                    }),
                )

        except Exception as e:
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    'error': e,
                    "status": 400,
                    "message": "not created"
                }),
            )

    @http.route('/api/bimabachat/attach_delete', methods=['POST', 'PUT'], type='http', auth="public", csrf=False,
                cors='*')
    @check_permissions
    def attach_delete(self):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            attach =jdata.get('attachment_id')
            attach_link = http.request.env['ir.attachment'].sudo().search([('id', 'in', attach)])
            attach_link.unlink()
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    "status": 200,
                    "message": "Successfully deleted"
                }),
            )
        except Exception as e:
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    'error': e,
                    "status": 400,
                }),
            )

    # @http.route('/api/bimabachat/instagram/route', methods=['POST', 'PUT'], type='http', auth="public", csrf=False,
    #             cors='*')
    # @check_permissions
    # def instagram_route(self,**post):
    #     print(post,"POST")


