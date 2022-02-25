# -*- coding: utf-8 -*-
from .main import *

_logger = logging.getLogger(__name__)


# List of REST resources in current file:
#   (url prefix)                (method)     (action)
# /api/res.country.state                GET     - Read all (with optional filters, offset, limit, order)
# /api/res.country.state/<id>           GET     - Read one
# /api/res.country.state                POST    - Create one
# /api/res.country.state/<id>           PUT     - Update one
# /api/res.country.state/<id>           DELETE  - Delete one
# /api/res.country.state/<id>/<method>  PUT     - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/res.country.state  GET  - Read all (with optional filters, offset, limit, order)
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
OUT__res_country_state__read_all__SUCCESS_CODE = 200      # editable
#   JSON:
#       {
#           "count":   XXX,     # number of returned records
#           "results": [
OUT__res_country_state__read_all__JSON = (                # editable
    'id',
    'display_name',

    ('country_id',(
        'id',
        'name',
    )),
    
    
   
    # one2many fields:
    
    # many2many fields:
    
)

#           ]
#       }

# /api/res.country.state/<id>  GET  - Read one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional parameter 'search_field' for search object not by 'id' field)
#           {"search_field": "some_field_name"}     # editable
# OUT data:
OUT__res_country_state__read_one__SUCCESS_CODE = 200      # editable
OUT__res_country_state__read_one__JSON = (                # editable
    # (The order of fields of different types maybe arbitrary)
    # simple fields (non relational):
    'id',
    'display_name',
)

# /api/res.country.state  POST  - Create one
# IN data:
#   HEADERS:
#       'access_token'
#   DEFAULTS:
#       (optional default values of fields)
DEFAULTS__res_country_state__create_one__JSON = (
	'id',
    'name',
)

#   JSON:
#       (fields and its values of created object;
#        don't forget about model's mandatory fields!)
#           ...                                     # editable
# OUT data:
OUT__res_country_state__create_one__SUCCESS_CODE = 200    # editable
OUT__res_country_state__create_one__JSON = (              # editable
    'id',
)

# /api/res.country.state/<id>  PUT  - Update one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (fields and new values of updated object)   # editable
#           ...
# OUT data:
OUT__res_country_state__update_one__SUCCESS_CODE = 200    # editable

# /api/res.country.state/<id>  DELETE  - Delete one
# IN data:
#   HEADERS:
#       'access_token'
# OUT data:
OUT__res_country_state__delete_one__SUCCESS_CODE = 200    # editable

# /api/res.country.state/<id>/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__res_country_state__call_method__SUCCESS_CODE = 200   # editable


# HTTP controller of REST resources:

class ControllerREST(http.Controller):
    
    # Read all (with optional filters, offset, limit, order):
    @http.route('/api/res.country.state', methods=['GET'], type='http', auth='none', cors='*')
    @check_permissions
    def api__res_country_state__GET(self, **kw):
        return wrap__resource__read_all(
            modelname = 'res.country.state',
            default_domain = [],
            success_code = OUT__res_country_state__read_all__SUCCESS_CODE,
            OUT_fields = OUT__res_country_state__read_all__JSON
        )
    
    # Read one:
    @http.route('/api/res.country.state/<id>', methods=['GET'], type='http', auth='none', cors='*')
    @check_permissions
    def api__res_country_state__id_GET(self, id, **kw):
        return wrap__resource__read_one(
            modelname = 'res.country.state',
            id = id,
            success_code = OUT__res_country_state__read_one__SUCCESS_CODE,
            OUT_fields = OUT__res_country_state__read_one__JSON
        )
    
    # Create one:
    @http.route('/api/res.country.state', methods=['POST'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__res_country_state__POST(self):
        return wrap__resource__create_one(
            modelname = 'res.country.state',
            default_vals = DEFAULTS__res_country_state__create_one__JSON,
            success_code = OUT__res_country_state__create_one__SUCCESS_CODE,
            OUT_fields = OUT__res_country_state__create_one__JSON
        )
    
    # Update one:
    @http.route('/api/res.country.state/<id>', methods=['PUT'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__res_country_state__id_PUT(self, id):
        return wrap__resource__update_one(
            modelname = 'res.country.state',
            id = id,
            success_code = OUT__res_country_state__update_one__SUCCESS_CODE
        )
    
    # Delete one:
    @http.route('/api/res.country.state/<id>', methods=['DELETE'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__res_country_state__id_DELETE(self, id):
        return wrap__resource__delete_one(
            modelname = 'res.country.state',
            id = id,
            success_code = OUT__res_country_state__delete_one__SUCCESS_CODE
        )
    
    # Call method (with optional parameters):
    @http.route('/api/res.country.state/<id>/<method>', methods=['PUT'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__res_country_state__id__method_PUT(self, id, method):
        return wrap__resource__call_method(
            modelname = 'res.country.state',
            id = id,
            method = method,
            success_code = OUT__res_country_state__call_method__SUCCESS_CODE
        )
