# -*- coding: utf-8 -*-
from .main import *

_logger = logging.getLogger(__name__)

# List of REST resources in current file:
#   (url prefix)                    (method)     (action)
# /api/project.task                GET     - Read all (with optional filters, offset, limit, order)
# /api/project.task/<id>           GET     - Read one
# /api/project.task                POST    - Create one
# /api/project.task/<id>           PUT     - Update one
# /api/project.task/<id>           DELETE  - Delete one
# /api/project.task/<id>/<method>  PUT     - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/project.task  GET  - Read all (with optional filters, offset, limit, order)
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
OUT__project_defect__read_all__SUCCESS_CODE = 200  # editable
#   JSON:
#       {
#           "count":   XXX,     # number of returned records
#           "results": [
OUT__project_defect__read_all__JSON = (
    # editable
    'name',
    'id',
    'planned_hours',
    'date_deadline',
    'progress',
    'description',
    'sequence',
    'date_assign',
    'date_last_stage_update',
    'kanban_state',
    'create_uid',
    'create_date',
    'write_uid',
    'x_status',
    'x_priority',
    'x_planned_hours',

    ('partner_id', (
        'id',
        'name',
    )),

    ('procurement_id', (
        'id',
        'name',
    )),

    ('sale_line_id', (
        'id',
        'name',
    )),

    ('displayed_image_id', (
        'id',
        'name',
    )),
    ('stage_id', (
        'id',
        'name',
    )),

    ('project_id', (
        'id',
        'name',
    )),
    ('user_id', (
        'id',
        'name',
    )),

    ('tag_ids', [(
        'id',
        'name',
    )]),

    ('timesheet_ids', [(
        'id',
        'name',
        'unit_amount',
        'date',
        'scheduleto',
        'schedulefrom',
        ('user_id', (
        'id',
        'name',
        )),
    )]),

    ('x_attachment', [(
        'id',
        'name'
    )]),
)
#           ]
#       }

# /api/project.task/<id>  GET  - Read one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional parameter 'search_field' for search object not by 'id' field)
#           {"search_field": "some_field_name"}     # editable
# OUT data:
OUT__project_defect__read_one__SUCCESS_CODE = 200  # editable
OUT__project_defect__read_one__JSON = (  # editable
    # (The order of fields of different types maybe arbitrary)
    # simple fields (non relational):
    'name',
    'id',
    'planned_hours',
    'date_deadline',
    'progress',
    'description',
    'sequence',
    'date_assign',
    'date_last_stage_update',
    'kanban_state',
    'create_uid',
    'create_date',
    'write_uid',
    'x_status',
    'x_priority',
    'x_planned_hours',

    ('partner_id', (
        'id',
        'name',
    )),
    ('stage_id', (
        'id',
        'name',
    )),

    ('procurement_id', (
        'id',
        'name',
    )),

    ('sale_line_id', (
        'id',
        'name',
    )),

    ('displayed_image_id', (
        'id',
        'name',
    )),

    ('project_id', (
        'id',
        'name',
    )),
    ('user_id', (
        'id',
        'name',
    )),

    ('tag_ids', [(
        'id',
        'name',
    )]),

    ('timesheet_ids', [(
        'id',
        'name',
        'unit_amount',
        'date',
        'scheduleto',
        'schedulefrom',
        ('user_id', (
        'id',
        'name',
        )),
    )]),

    ('x_attachment', [(
        'id',
        'name'
    )]),
)

# /api/project.task  POST  - Create one
# IN data:
#   HEADERS:
#       'access_token'
#   DEFAULTS:
#       (optional default values of fields)
DEFAULTS__project_defect__create_one__JSON = {  # editable
    # "some_field_1": some_value_1,
    # "some_field_2": some_value_2,
    # ...
}
#   JSON:
#       (fields and its values of created object;
#        don't forget about model's mandatory fields!)
#           ...                                     # editable
# OUT data:
OUT__project_defect__create_one__SUCCESS_CODE = 200  # editable
OUT__project_defect__create_one__JSON = (  # editable
    'id',
)

# /api/project.task/<id>  PUT  - Update one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (fields and new values of updated object)   # editable
#           ...
# OUT data:
OUT__project_defect__update_one__SUCCESS_CODE = 200  # editable

# /api/project.task/<id>  DELETE  - Delete one
# IN data:
#   HEADERS:
#       'access_token'
# OUT data:
OUT__project_defect__delete_one__SUCCESS_CODE = 200  # editable

# /api/project.task/<id>/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__project_defect__call_method__SUCCESS_CODE = 200  # editable


# HTTP controller of REST resources:

class ControllerREST(http.Controller):

    # Read all (with optional filters, offset, limit, order):
    @http.route('/api/project.task.new', methods=['GET'], type='http', auth='none', cors='*')
    @check_permissions
    def api__project_defect__GET(self, **kw):
        return wrap__resource__read_all(
            modelname='project.task',
            default_domain=[],
            success_code=OUT__project_defect__read_all__SUCCESS_CODE,
            OUT_fields=OUT__project_defect__read_all__JSON
        )

    # Read one:
    @http.route('/api/project.task.new/<id>', methods=['GET'], type='http', auth='none', cors='*')
    @check_permissions
    def api__project_defect__id_GET(self, id, **kw):
        return wrap__resource__read_one(
            modelname='project.task',
            id=id,
            success_code=OUT__project_defect__read_one__SUCCESS_CODE,
            OUT_fields=OUT__project_defect__read_one__JSON
        )

    # Create one:
    @http.route('/api/project.task.new', methods=['POST'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__project_defect__POST(self):
        return wrap__resource__create_one(
            modelname='project.task',
            default_vals=DEFAULTS__project_defect__create_one__JSON,
            success_code=OUT__project_defect__create_one__SUCCESS_CODE,
            OUT_fields=OUT__project_defect__create_one__JSON
        )

    # Update one:
    @http.route('/api/project.task.new/<id>', methods=['PUT'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__project_defect__id_PUT(self, id):
        return wrap__resource__update_one(
            modelname='project.task',
            id=id,
            success_code=OUT__project_defect__update_one__SUCCESS_CODE
        )

    # Delete one:
    @http.route('/api/project.task.new/<id>', methods=['DELETE'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__project_defect__id_DELETE(self, id):
        return wrap__resource__delete_one(
            modelname='project.task',
            id=id,
            success_code=OUT__project_defect__delete_one__SUCCESS_CODE
        )

    # Call method (with optional parameters):
    @http.route('/api/project.task.new/<id>/<method>', methods=['PUT'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__project_defect__id__method_PUT(self, id, method):
        return wrap__resource__call_method(
            modelname='project.task',
            id=id,
            method=method,
            success_code=OUT__project_defect__call_method__SUCCESS_CODE
        )
