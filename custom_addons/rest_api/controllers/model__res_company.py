# -*- coding: utf-8 -*-
from .main import *

_logger = logging.getLogger(__name__)


# List of REST resources in current file:
#   (url prefix)                (method)     (action)
# /api/res.company                GET     - Read all (with optional filters, offset, limit, order)
# /api/res.company/<id>           GET     - Read one
# /api/res.company                POST    - Create one
# /api/res.company/<id>           PUT     - Update one
# /api/res.company/<id>           DELETE  - Delete one
# /api/res.company/<id>/<method>  PUT     - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/res.company  GET  - Read all (with optional filters, offset, limit, order)
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
OUT__res_company__read_all__SUCCESS_CODE = 200      # editable
#   JSON:
#       {
#           "count":   XXX,     # number of returned records
#           "results": [
OUT__res_company__read_all__JSON = (                # editable
    'id',
    'name',
    'street',
    'street2',
    'city',
    'zip',
    'display_name',
    'phone',
    'email',
    'logo',
    

    ('state_id', (
        'id',
        'name',
    )),

    ('country_id', (
        'id',
        'name',
    )),

    ('parent_id', (
        'id',
        'name',
    )),
    
    ('partner_id', (
        'id',
        'name',
    )),
    
   
    # one2many fields:
    
    # many2many fields:
    
)

#           ]
#       }

# /api/res.company/<id>  GET  - Read one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional parameter 'search_field' for search object not by 'id' field)
#           {"search_field": "some_field_name"}     # editable
# OUT data:
OUT__res_company__read_one__SUCCESS_CODE = 200      # editable
OUT__res_company__read_one__JSON = (                # editable
    # (The order of fields of different types maybe arbitrary)
    # simple fields (non relational):
    'id',
    'name',
    'street',
    'street2',
    'city',
    'zip',
    'display_name',
    'phone',
    'email',
    'logo',
    'vat',
    'website',
    'x_acc',
    'x_bank',
    'x_ifsc',
    'x_pan',
    'rml_header1',
    

    ('state_id', (
        'id',
        'name',
    )),

    ('country_id', (
        'id',
        'name',
    )),
    


    ('parent_id', (
        'id',
        'name',
    )),

    
    ('partner_id', (
        'id',
        'name',
    )),
)

# /api/res.company  POST  - Create one
# IN data:
#   HEADERS:
#       'access_token'
#   DEFAULTS:
#       (optional default values of fields)
DEFAULTS__res_company__create_one__JSON = {
    
}


#   JSON:
#       (fields and its values of created object;
#        don't forget about model's mandatory fields!)
#           ...                                     # editable
# OUT data:
OUT__res_company__create_one__SUCCESS_CODE = 200    # editable
OUT__res_company__create_one__JSON = (              # editable
    'id',
    'name',
    'street',
    'street2',
    'city',
    'zip',
    'display_name',
    'phone',
    'email',
    'logo',
    'vat',
    'website',
    'x_acc',
    'x_bank',
    'x_ifsc',
    'x_pan',
    'rml_header1',
)

# /api/res.company/<id>  PUT  - Update one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (fields and new values of updated object)   # editable
#           ...
# OUT data:
OUT__res_company__update_one__SUCCESS_CODE = 200    # editable

# /api/res.company/<id>  DELETE  - Delete one
# IN data:
#   HEADERS:
#       'access_token'
# OUT data:
OUT__res_company__delete_one__SUCCESS_CODE = 200    # editable

# /api/res.company/<id>/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__res_company__call_method__SUCCESS_CODE = 200   # editable


# HTTP controller of REST resources:

class ControllerREST(http.Controller):
    
    # Read all (with optional filters, offset, limit, order):
    @http.route('/api/res.company', methods=['GET'], type='http', auth='none', cors='*')
    @check_permissions
    def api__res_company__GET(self, **kw):
        return wrap__resource__read_all(
            modelname = 'res.company',
            default_domain = [],
            success_code = OUT__res_company__read_all__SUCCESS_CODE,
            OUT_fields = OUT__res_company__read_all__JSON
        )
    
    # Read one:
    @http.route('/api/res.company/<id>', methods=['GET'], type='http', auth='none', cors='*')
    @check_permissions
    def api__res_company__id_GET(self, id, **kw):
        return wrap__resource__read_one(
            modelname = 'res.company',
            id = id,
            success_code = OUT__res_company__read_one__SUCCESS_CODE,
            OUT_fields = OUT__res_company__read_one__JSON
        )
    
    # Create one:
    @http.route('/api/res.company', methods=['POST'], type='http', auth='none', csrf=False, cors='*')
    def api__res_company__POST(self):
        return wrap__resource__create_one(
            modelname = 'res.company',
            default_vals = DEFAULTS__res_company__create_one__JSON,
            success_code = OUT__res_company__create_one__SUCCESS_CODE,
            OUT_fields = OUT__res_company__create_one__JSON
        )
    
    # Update one:
    @http.route('/api/res.company/<id>', methods=['PUT'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__res_company__id_PUT(self, id):
        return wrap__resource__update_one(
            modelname = 'res.company',
            id = id,
            success_code = OUT__res_company__update_one__SUCCESS_CODE
        )
    
    # Delete one:
    @http.route('/api/res.company/<id>', methods=['DELETE'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__res_company__id_DELETE(self, id):
        return wrap__resource__delete_one(
            modelname = 'res.company',
            id = id,
            success_code = OUT__res_company__delete_one__SUCCESS_CODE
        )
    
    # Call method (with optional parameters):
    @http.route('/api/res.company/<id>/<method>', methods=['PUT'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__res_company__id__method_PUT(self, id, method):
        return wrap__resource__call_method(
            modelname = 'res.company',
            id = id,
            method = method,
            success_code = OUT__res_company__call_method__SUCCESS_CODE
        )
