# -*- coding: utf-8 -*-
from .main import *

_logger = logging.getLogger(__name__)

# List of REST resources in current file:
#   (url prefix)                    (method)     (action)
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
    # simple fields (non relational):
    'id',
   'subject',
   'date',
   'email_from',
   'record_name',
   'model',
   'res_id',
   'message_type',
   'body',
   'reply_to',
   'create_date',

   ('author_id', (  # many2one
        'id',
        'name',
    )),
    ('subtype_id', (  # many2one
        'id',
        'name',
    )),



    ('tracking_value_ids', [(  # one2many
                'id',
            'field',
    'field_desc',
    'new_value_char',
    'mail_message_id',
    )]),
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
   'subject',
   'date',
   'email_from',
   'record_name',
   'model',
   'res_id',
   'message_type',
   'body',
   'reply_to',
   'create_date',

   ('author_id', (  # many2one
        'id',
        'name',
    )),
    ('subtype_id', (  # many2one
        'id',
        'name',
    )),



    ('tracking_value_ids', [(  # one2many
                'id',
            'field',
    'field_desc',
    'new_value_char',
    'mail_message_id',
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
    @http.route('/api/log1222', methods=['GET'], type='http', auth='none' ,cors='*')
    @check_permissions
    def api__res_partner__GET(self, **kw):
        return wrap__resource__read_all(
            modelname='mail.message',
            default_domain=[],
            success_code=OUT__res_partner__read_all__SUCCESS_CODE,
            OUT_fields=OUT__res_partner__read_all__JSON
        )

    # Read one:
    @http.route('/api/log/<id>', methods=['GET'], type='http', auth='none' ,cors='*')
    @check_permissions
    def api__res_partner__id_GET(self, id, **kw):
        return wrap__resource__read_one(
            modelname='mail.message',
            id=id,
            success_code=OUT__res_partner__read_one__SUCCESS_CODE,
            OUT_fields=OUT__res_partner__read_one__JSON
        )

    # Create one:
    @http.route('/api/log', methods=['POST'], type='http', auth='none', csrf=False ,cors='*')
    @check_permissions
    def api__res_partner__POST(self):
        return wrap__resource__create_one(
            modelname='mail.message',
            default_vals=DEFAULTS__res_partner__create_one__JSON,
            success_code=OUT__res_partner__create_one__SUCCESS_CODE,
            OUT_fields=OUT__res_partner__create_one__JSON
        )

    # Update one:
    @http.route('/api/log/<id>', methods=['PUT'], type='http', auth='none', csrf=False ,cors='*')
    @check_permissions
    def api__res_partner__id_PUT(self, id):
        return wrap__resource__update_one(
            modelname='mail.message',
            id=id,
            success_code=OUT__res_partner__update_one__SUCCESS_CODE
        )

    # Delete one:
    @http.route('/api/log/<id>', methods=['DELETE'], type='http', auth='none', csrf=False ,cors='*')
    @check_permissions
    def api__res_partner__id_DELETE(self, id):
        return wrap__resource__delete_one(
            modelname='mail.message',
            id=id,
            success_code=OUT__res_partner__delete_one__SUCCESS_CODE
        )

    # Call method (with optional parameters):
    @http.route('/api/log/<id>/<method>', methods=['PUT'], type='http', auth='none', csrf=False ,cors='*')
    @check_permissions
    def api__res_partner__id__method_PUT(self, id, method):
        return wrap__resource__call_method(
            modelname='mail.message',
            id=id,
            method=method,
            success_code=OUT__res_partner__call_method__SUCCESS_CODE
        )
