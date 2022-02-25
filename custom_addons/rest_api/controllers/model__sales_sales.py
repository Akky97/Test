# -*- coding: utf-8 -*-
from .main import *

_logger = logging.getLogger(__name__)


# List of REST resources in current file:
#   (url prefix)                    (method)     (action)
# /api/sales.sales                GET     - Read all (with optional filters, offset, limit, order)
# /api/sales.sales/<id>           GET     - Read one
# /api/sales.sales                POST    - Create one
# /api/sales.sales/<id>           PUT     - Update one
# /api/sales.sales/<id>           DELETE  - Delete one
# /api/sales.sales/<id>/<method>  PUT     - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/sales.sales  GET  - Read all (with optional filters, offset, limit, order)
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
OUT__sales_sales__read_all__SUCCESS_CODE = 200  # editable
#   JSON:
#       {
#           "count":   XXX,     # number of returned records
#           "results": [
OUT__sales_sales__read_all__JSON = (
    'dealer_code',
    'customer_name',
    'date',
    'vin_no',
    'mobile_no',
    'email_id',
    'attachment',
    'product_type',
    'name',
    'location_id',
    'product_uom',
    'product_id',
    'location_dest_id',

    ('motor_s_no', (
        'id',
        'name',
    )),
    ('vin_no', (
        'id',
        'name',
    )),
    
    ('product_type', (
        'id',
        'name',
    )),

            # editable
    

)
#           ]
#       }

# /api/sales.sales/<id>  GET  - Read one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional parameter 'search_field' for search object not by 'id' field)
#           {"search_field": "some_field_name"}     # editable
# OUT data:
OUT__sales_sales__read_one__SUCCESS_CODE = 200  # editable
OUT__sales_sales__read_one__JSON = (            # editable
    # (The order of fields of different types maybe arbitrary)
    # simple fields (non relational):
    'dealer_code',
    'customer_name',
    'date',
    'vin_no',
    'mobile_no',
    'email_id',
    'attachment',
    'product_type',
    'name',
    'location_id',
    'product_uom',
    'product_id',
    'location_dest_id',

    ('motor_s_no', (
        'id',
        'name',
    )),

    ('product_type', (
        'id',
        'name',
    )),

    ('vin_no', (
        'id',
        'name',
    )),

)

# /api/sales.sales  POST  - Create one
# IN data:
#   HEADERS:
#       'access_token'
#   DEFAULTS:
#       (optional default values of fields)
DEFAULTS__sales_sales__create_one__JSON = {     # editable
            #"some_field_1": some_value_1,
            #"some_field_2": some_value_2,
            #...
}
#   JSON:
#       (fields and its values of created object;
#        don't forget about model's mandatory fields!)
#           ...                                     # editable
# OUT data:
OUT__sales_sales__create_one__SUCCESS_CODE = 200  # editable
OUT__sales_sales__create_one__JSON = (          # editable
    'id',
)

# /api/sales.sales/<id>  PUT  - Update one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (fields and new values of updated object)   # editable
#           ...
# OUT data:
OUT__sales_sales__update_one__SUCCESS_CODE = 200  # editable

# /api/sales.sales/<id>  DELETE  - Delete one
# IN data:
#   HEADERS:
#       'access_token'
# OUT data:
OUT__sales_sales__delete_one__SUCCESS_CODE = 200  # editable

# /api/sales.sales/<id>/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__sales_sales__call_method__SUCCESS_CODE = 200  # editable


# HTTP controller of REST resources:

class ControllerREST(http.Controller):
    
    # Read all (with optional filters, offset, limit, order):
    @http.route('/api/sales.sales', methods=['GET'], type='http', auth='none', cors='*')
    @check_permissions
    def api__sales_sales__GET(self, **kw):
        return wrap__resource__read_all(
            modelname = 'sales.sales',
            default_domain = [],
            success_code = OUT__sales_sales__read_all__SUCCESS_CODE,
            OUT_fields = OUT__sales_sales__read_all__JSON
        )
    
    # Read one:
    @http.route('/api/sales.sales/<id>', methods=['GET'], type='http', auth='none', cors='*')
    @check_permissions
    def api__sales_sales__id_GET(self, id, **kw):
        return wrap__resource__read_one(
            modelname = 'sales.sales',
            id = id,
            success_code = OUT__sales_sales__read_one__SUCCESS_CODE,
            OUT_fields = OUT__sales_sales__read_one__JSON
        )
    
    # Create one:
    @http.route('/api/sales.sales', methods=['POST'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__sales_sales__POST(self):
        return wrap__resource__create_one(
            modelname = 'sales.sales',
            default_vals = DEFAULTS__sales_sales__create_one__JSON,
            success_code = OUT__sales_sales__create_one__SUCCESS_CODE,
            OUT_fields = OUT__sales_sales__create_one__JSON
        )
    
    # Update one:
    @http.route('/api/sales.sales/<id>', methods=['PUT'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__sales_sales__id_PUT(self, id):
        return wrap__resource__update_one(
            modelname = 'sales.sales',
            id = id,
            success_code = OUT__sales_sales__update_one__SUCCESS_CODE
        )
    
    # Delete one:
    @http.route('/api/sales.sales/<id>', methods=['DELETE'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__sales_sales__id_DELETE(self, id):
        return wrap__resource__delete_one(
            modelname = 'sales.sales',
            id = id,
            success_code = OUT__sales_sales__delete_one__SUCCESS_CODE
        )
    
    # Call method (with optional parameters):
    @http.route('/api/sales.sales/<id>/<method>', methods=['PUT'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__sales_sales__id__method_PUT(self, id, method):
        return wrap__resource__call_method(
            modelname = 'sales.sales',
            id = id,
            method = method,
            success_code = OUT__sales_sales__call_method__SUCCESS_CODE
        )
