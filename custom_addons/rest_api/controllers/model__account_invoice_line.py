# -*- coding: utf-8 -*-
from .main import *

_logger = logging.getLogger(__name__)


# List of REST resources in current file:
#   (url prefix)                         (method)     (action)
# /api/account.invoice.line                GET     - Read all (with optional filters, offset, limit, order)
# /api/account.invoice.line/<id>           GET     - Read one
# /api/account.invoice.line                POST    - Create one
# /api/account.invoice.line/<id>           PUT     - Update one
# /api/account.invoice.line/<id>           DELETE  - Delete one
# /api/account.invoice.line/<id>/<method>  PUT     - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/account.invoice.line  GET  - Read all (with optional filters, offset, limit, order)
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
OUT__account_invoice_line__read_all__SUCCESS_CODE = 200  # editable
#   JSON:
#       {
#           "count":   XXX,     # number of returned records
#           "results": [
OUT__account_invoice_line__read_all__JSON = (       # editable
    'id',
    'invoice_id',
    ('product_id', (  # many2one
        'id',
        'name',
    )),
    'name',
    'price_subtotal',
)
#           ]
#       }

# /api/account.invoice.line/<id>  GET  - Read one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional parameter 'search_field' for search object not by 'id' field)
#           {"search_field": "some_field_name"}     # editable
# OUT data:
OUT__account_invoice_line__read_one__SUCCESS_CODE = 200  # editable
OUT__account_invoice_line__read_one__JSON = (       # editable
    # (The order of fields of different types maybe arbitrary)
    # simple fields (non relational):
    'id',
    'name',
    'quantity',
    'price_unit',
    'price_subtotal',
    # many2one fields:
    ('invoice_id', (
        'id',
        'number',
    )),
    ('product_id', (
        'id',
        'name',
        'type',
        ('categ_id', (  # many2one
            'id',
            'name',
        )),
    )),
    ('account_id', (
        'id',
        'display_name',
    )),
    # many2many fields:
    ('invoice_line_tax_ids', [(
        'id',
        'name',
        'type',
        'amount',
        'price_include',
    )]),
)

# /api/account.invoice.line  POST  - Create one
# IN data:
#   HEADERS:
#       'access_token'
#   DEFAULTS:
#       (optional default values of fields)
DEFAULTS__account_invoice_line__create_one__JSON = {  # editable
            #"some_field_1": some_value_1,
            #"some_field_2": some_value_2,
            #...
}
#   JSON:
#       (fields and its values of created object;
#        don't forget about model's mandatory fields!)
#           ...                                     # editable
# OUT data:
OUT__account_invoice_line__create_one__SUCCESS_CODE = 200  # editable
OUT__account_invoice_line__create_one__JSON = (     # editable
    'id',
)

# /api/account.invoice.line/<id>  PUT  - Update one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (fields and new values of updated object)   # editable
#           ...
# OUT data:
OUT__account_invoice_line__update_one__SUCCESS_CODE = 200  # editable

# /api/account.invoice.line/<id>  DELETE  - Delete one
# IN data:
#   HEADERS:
#       'access_token'
# OUT data:
OUT__account_invoice_line__delete_one__SUCCESS_CODE = 200  # editable

# /api/account.invoice.line/<id>/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__account_invoice_line__call_method__SUCCESS_CODE = 200  # editable


# HTTP controller of REST resources:

class ControllerREST(http.Controller):
    
    # Read all (with optional filters, offset, limit, order):
    @http.route('/api/account.invoice.line', methods=['GET'], type='http', auth='none')
    @check_permissions
    def api__account_invoice_line__GET(self, **kw):
        return wrap__resource__read_all(
            modelname = 'account.invoice.line',
            default_domain = [],
            success_code = OUT__account_invoice_line__read_all__SUCCESS_CODE,
            OUT_fields = OUT__account_invoice_line__read_all__JSON
        )
    
    # Read one:
    @http.route('/api/account.invoice.line/<id>', methods=['GET'], type='http', auth='none')
    @check_permissions
    def api__account_invoice_line__id_GET(self, id, **kw):
        return wrap__resource__read_one(
            modelname = 'account.invoice.line',
            id = id,
            success_code = OUT__account_invoice_line__read_one__SUCCESS_CODE,
            OUT_fields = OUT__account_invoice_line__read_one__JSON
        )
    
    # Create one:
    @http.route('/api/account.invoice.line', methods=['POST'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__account_invoice_line__POST(self):
        return wrap__resource__create_one(
            modelname = 'account.invoice.line',
            default_vals = DEFAULTS__account_invoice_line__create_one__JSON,
            success_code = OUT__account_invoice_line__create_one__SUCCESS_CODE,
            OUT_fields = OUT__account_invoice_line__create_one__JSON
        )
    
    # Update one:
    @http.route('/api/account.invoice.line/<id>', methods=['PUT'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__account_invoice_line__id_PUT(self, id):
        return wrap__resource__update_one(
            modelname = 'account.invoice.line',
            id = id,
            success_code = OUT__account_invoice_line__update_one__SUCCESS_CODE
        )
    
    # Delete one:
    @http.route('/api/account.invoice.line/<id>', methods=['DELETE'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__account_invoice_line__id_DELETE(self, id):
        return wrap__resource__delete_one(
            modelname = 'account.invoice.line',
            id = id,
            success_code = OUT__account_invoice_line__delete_one__SUCCESS_CODE
        )
    
    # Call method (with optional parameters):
    @http.route('/api/account.invoice.line/<id>/<method>', methods=['PUT'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__account_invoice_line__id__method_PUT(self, id, method):
        return wrap__resource__call_method(
            modelname = 'account.invoice.line',
            id = id,
            method = method,
            success_code = OUT__account_invoice_line__call_method__SUCCESS_CODE
        )
