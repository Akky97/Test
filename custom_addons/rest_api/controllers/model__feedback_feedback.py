# -*- coding: utf-8 -*-
from .main import *

_logger = logging.getLogger(__name__)


# List of REST resources in current file:
#   (url prefix)                    (method)     (action)
# /api/feedback.feedback                GET     - Read all (with optional filters, offset, limit, order)
# /api/feedback.feedback/<id>           GET     - Read one
# /api/feedback.feedback                POST    - Create one
# /api/feedback.feedback/<id>           PUT     - Update one
# /api/feedback.feedback/<id>           DELETE  - Delete one
# /api/feedback.feedback/<id>/<method>  PUT     - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/feedback.feedback  GET  - Read all (with optional filters, offset, limit, order)
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
OUT__feedback_feedback__read_all__SUCCESS_CODE = 200  # editable
#   JSON:
#       {
#           "count":   XXX,     # number of returned records
#           "results": [
OUT__feedback_feedback__read_all__JSON = (            # editable
    # simple fields (non relational):
    'description',
	'name',
	'x_date',
    'x_rating',
	
    # many2one fields:
    ('x_user1', (
        'id',
        'name',
    )),
  
)
#           ]
#       }

# /api/feedback.feedback/<id>  GET  - Read one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional parameter 'search_field' for search object not by 'id' field)
#           {"search_field": "some_field_name"}     # editable
# OUT data:
OUT__feedback_feedback__read_one__SUCCESS_CODE = 200  # editable
OUT__feedback_feedback__read_one__JSON = (            # editable
    # (The order of fields of different types maybe arbitrary)
    # simple fields (non relational):
	'description',
    'name',
    'x_date',
    'x_rating',
    
    # many2one fields:
    ('x_user1', (
        'id',
        'name',
    )),
  
)

# /api/feedback.feedback  POST  - Create one
# IN data:
#   HEADERS:
#       'access_token'
#   DEFAULTS:
#       (optional default values of fields)
DEFAULTS__feedback_feedback__create_one__JSON = {     # editable
            #"some_field_1": some_value_1,
            #"some_field_2": some_value_2,
            #...
}
#   JSON:
#       (fields and its values of created object;
#        don't forget about model's mandatory fields!)
#           ...                                     # editable
# OUT data:
OUT__feedback_feedback__create_one__SUCCESS_CODE = 200  # editable
OUT__feedback_feedback__create_one__JSON = (          # editable
    'id',
)

# /api/feedback.feedback/<id>  PUT  - Update one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (fields and new values of updated object)   # editable
#           ...
# OUT data:
OUT__feedback_feedback__update_one__SUCCESS_CODE = 200  # editable

# /api/feedback.feedback/<id>  DELETE  - Delete one
# IN data:
#   HEADERS:
#       'access_token'
# OUT data:
OUT__feedback_feedback__delete_one__SUCCESS_CODE = 200  # editable

# /api/feedback.feedback/<id>/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__feedback_feedback__call_method__SUCCESS_CODE = 200  # editable


# HTTP controller of REST resources:

class ControllerREST(http.Controller):
    
    # Read all (with optional filters, offset, limit, order):
    @http.route('/api/feedback.feedback', methods=['GET'], type='http', auth='none',cors='*')
    @check_permissions
    def api__feedback_feedback__GET(self, **kw):
        return wrap__resource__read_all(
            modelname = 'feedback.feedback',
            default_domain = [],
            success_code = OUT__feedback_feedback__read_all__SUCCESS_CODE,
            OUT_fields = OUT__feedback_feedback__read_all__JSON
        )
    
    # Read one:
    @http.route('/api/feedback.feedback/<id>', methods=['GET'], type='http', auth='none',cors='*')
    @check_permissions
    def api__feedback_feedback__id_GET(self, id, **kw):
        return wrap__resource__read_one(
            modelname = 'feedback.feedback',
            id = id,
            success_code = OUT__feedback_feedback__read_one__SUCCESS_CODE,
            OUT_fields = OUT__feedback_feedback__read_one__JSON
        )
    
    # Create one:
    @http.route('/api/feedback.feedback', methods=['POST'], type='http', auth='none', csrf=False,cors='*')
    @check_permissions
    def api__feedback_feedback__POST(self):
        return wrap__resource__create_one(
            modelname = 'feedback.feedback',
            default_vals = DEFAULTS__feedback_feedback__create_one__JSON,
            success_code = OUT__feedback_feedback__create_one__SUCCESS_CODE,
            OUT_fields = OUT__feedback_feedback__create_one__JSON
        )
    
    # Update one:
    @http.route('/api/feedback.feedback/<id>', methods=['PUT'], type='http', auth='none', csrf=False,cors='*')
    @check_permissions
    def api__feedback_feedback__id_PUT(self, id):
        return wrap__resource__update_one(
            modelname = 'feedback.feedback',
            id = id,
            success_code = OUT__feedback_feedback__update_one__SUCCESS_CODE
        )
    
    # Delete one:
    @http.route('/api/feedback.feedback/<id>', methods=['DELETE'], type='http', auth='none', csrf=False,cors='*')
    @check_permissions
    def api__feedback_feedback__id_DELETE(self, id):
        return wrap__resource__delete_one(
            modelname = 'feedback.feedback',
            id = id,
            success_code = OUT__feedback_feedback__delete_one__SUCCESS_CODE
        )
    
    # Call method (with optional parameters):
    @http.route('/api/feedback.feedback/<id>/<method>', methods=['PUT'], type='http', auth='none', csrf=False,cors='*')
    @check_permissions
    def api__feedback_feedback__id__method_PUT(self, id, method):
        return wrap__resource__call_method(
            modelname = 'feedback.feedback',
            id = id,
            method = method,
            success_code = OUT__feedback_feedback__call_method__SUCCESS_CODE
        )
