# -*- coding: utf-8 -*-
from .main import *

_logger = logging.getLogger(__name__)

# List of REST resources in current file:
#   (url prefix)               (method)     (action)
# /api/project.tags                GET     - Read all (with optional filters, offset, limit, order)
# /api/project.tags/<id>           GET     - Read one
# /api/project.tags                POST    - Create one
# /api/project.tags/<id>           PUT     - Update one
# /api/project.tags/<id>           DELETE  - Delete one
# /api/project.tags/<id>/<method>  PUT     - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/project.tags  GET  - Read all (with optional filters, offset, limit, order)
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
OUT__project_tags__read_all__SUCCESS_CODE = 200  # editable
#   JSON:
#       {
#           "count":   XXX,     # number of returned records
#           "results": [
OUT__project_tags__read_all__JSON = (  # editable
    # simple fields (non relational):
    'id',
    'name',
    
    # ('project_id', (
    #     'id',
    #     'name',
    # )),
    
)
#           ]
#       }

# /api/project.tags/<id>  GET  - Read one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional parameter 'search_field' for search object not by 'id' field)
#           {"search_field": "some_field_name"}     # editable
# OUT data:
OUT__project_tags__read_one__SUCCESS_CODE = 200  # editable
OUT__project_tags__read_one__JSON = (  # editable
     'id',
     'name',
    
    # ('project_id', (
    #     'id',
    #     'name',
    # )),
    
)

# /api/project.tags  POST  - Create one
# IN data:
#   HEADERS:
#       'access_token'
#   DEFAULTS:
#       (optional default values of fields)
DEFAULTS__project_tags__create_one__JSON = {  # editable
    # "some_field_1": some_value_1,
    # "some_field_2": some_value_2,
    # ...
}
#   JSON:
#       (fields and its values of created object;
#        don't forget about model's mandatory fields!)
#           ...                                     # editable
# OUT data:
OUT__project_tags__create_one__SUCCESS_CODE = 200  # editable
OUT__project_tags__create_one__JSON = (  # editable
    'id',
)

# /api/project.tags/<id>  PUT  - Update one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (fields and new values of updated object)   # editable
#           ...
# OUT data:
OUT__project_tags__update_one__SUCCESS_CODE = 200  # editable

# /api/project.tags/<id>  DELETE  - Delete one
# IN data:
#   HEADERS:
#       'access_token'
# OUT data:
OUT__project_tags__delete_one__SUCCESS_CODE = 200  # editable

# /api/project.tags/<id>/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__project_tags__call_method__SUCCESS_CODE = 200  # editable


# HTTP controller of REST resources:

class ControllerREST(http.Controller):

    # Read all (with optional filters, offset, limit, order):
    @http.route('/api/project.tags', methods=['GET'], type='http', auth='none', cors='*')
    @check_permissions
    def api__project_tags__GET(self, **kw):
        return wrap__resource__read_all(
            modelname='project.tags',
            default_domain=[],
            success_code=OUT__project_tags__read_all__SUCCESS_CODE,
            OUT_fields=OUT__project_tags__read_all__JSON
        )

    # Read one:
    @http.route('/api/project.tags/<id>', methods=['GET'], type='http', auth='none', cors='*')
    @check_permissions
    def api__project_tags__id_GET(self, id, **kw):
        return wrap__resource__read_one(
            modelname='project.tags',
            id=id,
            success_code=OUT__project_tags__read_one__SUCCESS_CODE,
            OUT_fields=OUT__project_tags__read_one__JSON
        )

    # Create one:
    @http.route('/api/project.tags', methods=['POST'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__project_tags__POST(self):
        return wrap__resource__create_one(
            modelname='project.tags',
            default_vals=DEFAULTS__project_tags__create_one__JSON,
            success_code=OUT__project_tags__create_one__SUCCESS_CODE,
            OUT_fields=OUT__project_tags__create_one__JSON
        )

    # Update one:
    @http.route('/api/project.tags/<id>', methods=['PUT'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__project_tags__id_PUT(self, id):
        return wrap__resource__update_one(
            modelname='project.tags',
            id=id,
            success_code=OUT__project_tags__update_one__SUCCESS_CODE
        )

    # Delete one:
    @http.route('/api/project.tags/<id>', methods=['DELETE'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__project_tags__id_DELETE(self, id):
        return wrap__resource__delete_one(
            modelname='project.tags',
            id=id,
            success_code=OUT__project_tags__delete_one__SUCCESS_CODE
        )

    # Call method (with optional parameters):
    @http.route('/api/project.tags/<id>/<method>', methods=['PUT'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__project_tags__id__method_PUT(self, id, method):
        return wrap__resource__call_method(
            modelname='project.tags',
            id=id,
            method=method,
            success_code=OUT__project_tags__call_method__SUCCESS_CODE
        )
