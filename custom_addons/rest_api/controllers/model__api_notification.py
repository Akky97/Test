# -*- coding: utf-8 -*-
from .main import *
import math

_logger = logging.getLogger(__name__)

# List of REST resources in current file:
#   (url prefix)               (method)     (action)
# /api/apinotification.apinotification                GET     - Read all (with optional filters, offset, limit, order)
# /api/apinotification.apinotification/<id>           GET     - Read one
# /api/apinotification.apinotification                POST    - Create one
# /api/apinotification.apinotification/<id>           PUT     - Update one
# /api/apinotification.apinotification/<id>           DELETE  - Delete one
# /api/apinotification.apinotification/<id>/<method>  PUT     - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/apinotification.apinotification  GET  - Read all (with optional filters, offset, limit, order)
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
OUT__apinotification__read_all__SUCCESS_CODE = 200  # editable
#   JSON:
#       {
#           "count":   XXX,     # number of returned records
#           "results": [
OUT__apinotification__read_all__JSON = (  # editable
    # simple fields (non relational):
    'id',
    'model_name',
    'model_id',
    'message',
    'create_date',
    'image',
    'title',
    'due_date',
    'premium',
    'company_name',
    'date',
    'heading',
    
    ('name', (
        'id',
        'name',
    )),

    ('user_id', (
        'id',
        'name',
    )),

)
#           ]
#       }

# /api/apinotification.apinotification/<id>  GET  - Read one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional parameter 'search_field' for search object not by 'id' field)
#           {"search_field": "some_field_name"}     # editable
# OUT data:
OUT__apinotification__read_one__SUCCESS_CODE = 200  # editable
OUT__apinotification__read_one__JSON = (  # editable
    'id',
    'model_name',
    'model_id',
    'message',
    'create_date',
    'image',
    'title',
    'due_date',
    'premium',
    'company_name',
    'date',
    'heading',

    ('name', (
        'id',
        'name',
    )),

    ('user_id', (
        'id',
        'name',
    )),

    # ('project_id', (
    #     'id',
    #     'name',
    # )),

)

# /api/apinotification.apinotification  POST  - Create one
# IN data:
#   HEADERS:
#       'access_token'
#   DEFAULTS:
#       (optional default values of fields)
DEFAULTS__apinotification__create_one__JSON = {  # editable
    # "some_field_1": some_value_1,
    # "some_field_2": some_value_2,
    # ...
}
#   JSON:
#       (fields and its values of created object;
#        don't forget about model's mandatory fields!)
#           ...                                     # editable
# OUT data:
OUT__apinotification__create_one__SUCCESS_CODE = 200  # editable
OUT__apinotification__create_one__JSON = (  # editable
    'id',
)

# /api/apinotification.apinotification/<id>  PUT  - Update one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (fields and new values of updated object)   # editable
#           ...
# OUT data:
OUT__apinotification__update_one__SUCCESS_CODE = 200  # editable

# /api/apinotification.apinotification/<id>  DELETE  - Delete one
# IN data:
#   HEADERS:
#       'access_token'
# OUT data:
OUT__apinotification__delete_one__SUCCESS_CODE = 200  # editable

# /api/apinotification.apinotification/<id>/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__apinotification__call_method__SUCCESS_CODE = 200  # editable


# HTTP controller of REST resources:

class ControllerREST(http.Controller):

    # Read all (with optional filters, offset, limit, order):
    @http.route('/api/apinotification', methods=['POST'], type='http', auth='none', cors='*',csrf=False)
    @check_permissions
    def api__apinotification__id__count12(self):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            user_id = jdata.get('user_id')
            if not user_id:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        "status": 400,
                        "message": "user_id is Required"
                    }),
                )
            user_ids = http.request.env['apinotification.apinotification'].sudo().search([('user_id', '=', int(user_id))],order='id desc')
            temp = []
            import math
            for i in user_ids:
                pre=0
                if i.premium == False or i.premium is None:
                    pre=0
                else:
                    pre=i.premium
                vals = {
                    'id': i.id,
                    'model_name': i.model_name,
                    'model_id': i.model_id,
                    'message': i.message,
                    'create_date': i.create_date,
                    'image': i.image,
                    'title': i.title,
                    'due_date': i.due_date,
                    'premium': math.trunc(pre),
                    'company_name': i.company_name,
                    'date': i.date,
                    'heading': i.heading,
                    'name': {"id": i.name.id, "name": i.name.name},
                    'user_id': {"id": i.user_id.id, "name": i.user_id.name},
                    'ticket_number':i.ticket_number
                }
                temp.append(vals)

            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    "data": temp,
                    "status": 200,
                    "message": "successful"
                }),
            )
        except Exception as e:
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    "error": str(e),
                    "status": 400,
                    "message": "Something Went Wrong !!!"
                }),
            )


    # def api__apinotification__GET(self, **kw):
    #     return wrap__resource__read_all(
    #         modelname='apinotification.apinotification',
    #         default_domain=[],
    #         success_code=OUT__apinotification__read_all__SUCCESS_CODE,
    #         OUT_fields=OUT__apinotification__read_all__JSON
    #     )

    # Read one:
    @http.route('/api/apinotification/<id>', methods=['GET'], type='http', auth='none', cors='*')
    @check_permissions
    def api__apinotification__id_GET(self, id, **kw):
        return wrap__resource__read_one(
            modelname='apinotification.apinotification',
            id=id,
            success_code=OUT__apinotification__read_one__SUCCESS_CODE,
            OUT_fields=OUT__apinotification__read_one__JSON
        )

    # Create one:
    # @http.route('/api/apinotification', methods=['POST'], type='http', auth='none', csrf=False, cors='*')
    # @check_permissions
    # def api__apinotification__POST(self):
    #     return wrap__resource__create_one(
    #         modelname='apinotification.apinotification',
    #         default_vals=DEFAULTS__apinotification__create_one__JSON,
    #         success_code=OUT__apinotification__create_one__SUCCESS_CODE,
    #         OUT_fields=OUT__apinotification__create_one__JSON
    #     )

    # Update one:
    @http.route('/api/apinotification/<id>', methods=['PUT'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__apinotification__id_PUT(self, id):
        return wrap__resource__update_one(
            modelname='apinotification.apinotification',
            id=id,
            success_code=OUT__apinotification__update_one__SUCCESS_CODE
        )

    # Delete one:
    @http.route('/api/apinotification/<id>', methods=['DELETE'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__apinotification__id_DELETE(self, id):
        return wrap__resource__delete_one(
            modelname='apinotification.apinotification',
            id=id,
            success_code=OUT__apinotification__delete_one__SUCCESS_CODE
        )

    # Call method (with optional parameters):
    @http.route('/api/apinotification/<id>/<method>', methods=['PUT'],auth='none', csrf=False, cors='*')
    @check_permissions
    def api__apinotification__id__method_PUT(self, id, method):
        return wrap__resource__call_method(
            modelname='apinotification.apinotification',
            id=id,
            method=method,
            success_code=OUT__apinotification__call_method__SUCCESS_CODE
        )

    @http.route('/api/apinotificationcount', methods=['POST'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__apinotification__id__count(self):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            user_id = jdata.get('user_id')
            if not user_id:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        "status": 400,
                        "message": "user_id is Required"
                    }),
                )
            user_ids = http.request.env['apinotification.apinotification'].sudo().search_count([('user_id', '=', int(user_id)),('noti_read','=',False)])
            count = http.request.env['apinotification.apinotification'].sudo().search([('user_id', '=', int(user_id)),('noti_read','=',False)])
            print(user_ids,"AAAAAAa")
            for i in count:
                i.write({"noti_read":True})
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    "count": user_ids,
                    "status": 200,
                    "message": "counted successfully"
                }),
             )
        except Exception as e:
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    "error": str(e),
                    "status": 400,
                    "message": " not counted "
                }),
            )

