# -*- coding: utf-8 -*-
from .main import *

_logger = logging.getLogger(__name__)

# List of REST resources in current file:
#   (url prefix)               (method)     (action)
# /api/project.issue                GET     - Read all (with optional filters, offset, limit, order)
# /api/project.issue/<id>           GET     - Read one
# /api/project.issue           cr     POST    - Create one
# /api/project.issue/<id>           PUT     - Update one
# /api/project.issue/<id>           DELETE  - Delete one
# /api/project.issue/<id>/<method>  PUT     - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/project.issue  GET  - Read all (with optional filters, offset, limit, order)
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
OUT__project_issue__read_all__SUCCESS_CODE = 200  # editable
#   JSON:
#       {
#           "count":   XXX,     # number of returned records
#           "results": [
OUT__project_issue__read_all__JSON = (  # editable
    # simple fields (non relational):
    'id',
    'name',
    'name1',
    'status',
    'write_date',
    'description',
    'create_date',
    'email_from',
    # 'priority',

    ('user_id', (
        'id',
        'name',
    )),
    ('partner_id', (
        'id',
        'name',
    )),
    ('project_id', (
        'id',
        'name',
    )),
    ('task_id', (
        'id',
        'name',
    )),
    ('createdBy', (
        'id',
        'name',
    )),
    ('tag_ids', [(
        'id',
        'name',
    )]),
    # ('timesheet_ids', [(
    #     'id',
    #     'date',
    #     'unit_amount',
    #     ('user_id', (  # many2one
    #         'id',
    #         'name',
    #     )),
    # )]),

)
#           ]
#       }

# /api/project.issue/<id>  GET  - Read one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional parameter 'search_field' for search object not by 'id' field)
#           {"search_field": "some_field_name"}     # editable
# OUT data:
OUT__project_issue__read_one__SUCCESS_CODE = 200  # editable
OUT__project_issue__read_one__JSON = (  # editable
    # (The order of fields of different types maybe arbitrary)
    # simple fields (non relational):

    'id',
    'name',
    'name1',
    'write_date',
    'description',
    'create_date',
    'email_from',
    'status',
    'priority',

    ('user_id', (
        'id',
        'name',
    )),
    ('partner_id', (
        'id',
        'name',
    )),
    ('project_id', (
        'id',
        'name',
    )),
    ('task_id', (
        'id',
        'name',
    )),
    ('createdBy', (
        'id',
        'name',
    )),
    ('tag_ids', [(
        'id',
        'name',
    )]),
    # ('timesheet_ids', [(
    #     'id',
    #     'date',
    #     'unit_amount',
    #     ('user_id', (  # many2one
    #         'id',
    #         'name',
    #     )),
    # )]),

)
# /api/project.issue  POST  - Create one
# IN data:
#   HEADERS:
#       'access_token'
#   DEFAULTS:
#       (optional default values of fields)
DEFAULTS__project_issue__create_one__JSON = {  # editable
    # "some_field_1": some_value_1,
    # "some_field_2": some_value_2,
    # ...
}
#   JSON:
#       (fields and its values of created object;
#        don't forget about model's mandatory fields!)
#           ...                                     # editable
# OUT data:
OUT__project_issue__create_one__SUCCESS_CODE = 200  # editable
OUT__project_issue__create_one__JSON = (  # editable
    'id',
)

# /api/project.issue/<id>  PUT  - Update one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (fields and new values of updated object)   # editable
#           ...
# OUT data:
OUT__project_issue__update_one__SUCCESS_CODE = 200  # editable

# /api/project.issue/<id>  DELETE  - Delete one
# IN data:
#   HEADERS:
#       'access_token'
# OUT data:
OUT__project_issue__delete_one__SUCCESS_CODE = 200  # editable

# /api/project.issue/<id>/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__project_issue__call_method__SUCCESS_CODE = 200  # editable


# HTTP controller of REST resources:

class ControllerREST(http.Controller):

    # Read all (with optional filters, offset, limit, order):
    @http.route('/api/bimabachat/project.issue', methods=['GET'], type='http', auth='none', cors='*')
    @check_permissions
    def api__project_issue__GET(self, **kw):
        return wrap__resource__read_all(
            modelname='project.issue',
            default_domain=[],
            success_code=OUT__project_issue__read_all__SUCCESS_CODE,
            OUT_fields=OUT__project_issue__read_all__JSON
        )

    # Read one:
    @http.route('/api/bimabachat/project.issue/<id>', methods=['GET'], type='http', auth='none', cors='*')
    @check_permissions
    def api__project_issue__id_GET(self, id, **kw):
        return wrap__resource__read_one(
            modelname='project.issue',
            id=id,
            success_code=OUT__project_issue__read_one__SUCCESS_CODE,
            OUT_fields=OUT__project_issue__read_one__JSON
        )

    # Create one:
    @http.route('/api/bimabachat/project.issue', methods=['POST'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__project_issue__POST(self):
        return wrap__resource__create_one(
            modelname='project.issue',
            default_vals=DEFAULTS__project_issue__create_one__JSON,
            success_code=OUT__project_issue__create_one__SUCCESS_CODE,
            OUT_fields=OUT__project_issue__create_one__JSON
        )

    # Update one:
    @http.route('/api/bimabachat/project.issue/<id>', methods=['PUT'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__project_issue__id_PUT(self, id):
        return wrap__resource__update_one(
            modelname='project.issue',
            id=id,
            success_code=OUT__project_issue__update_one__SUCCESS_CODE
        )

    # Delete one:
    @http.route('/api/bimabachat/project.issue/<id>', methods=['DELETE'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__project_issue__id_DELETE(self, id):
        return wrap__resource__delete_one(
            modelname='project.issue',
            id=id,
            success_code=OUT__project_issue__delete_one__SUCCESS_CODE
        )

    # Call method (with optional parameters):
    @http.route('/api/bimabachat/project.issue/<id>/<method>', methods=['PUT'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def api__project_issue__id__method_PUT(self, id, method):
        return wrap__resource__call_method(
            modelname='project.issue',
            id=id,
            method=method,
            success_code=OUT__project_issue__call_method__SUCCESS_CODE
        )

    @http.route('/api/bimabachat/createticket', methods=['POST'], type='http', auth="public", csrf=False, cors='*')
    @check_permissions
    def ticketcreate_method(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        print(jdata)
        uid = request.session.uid
        name1 = jdata.get('name1')
        priority = jdata.get('priority')
        user_id = jdata.get('user_id')
        stage_id = jdata.get('stage_id')
        x_claim_type = jdata.get('x_claim_type')
        x_claim_status = jdata.get('x_claim_status')
        x_claim_sub_status = jdata.get('x_claim_sub_status')
        x_claim_policy = jdata.get('x_claim_policy')
        createdBy = jdata.get('createdBy')
        tag_ids = jdata.get('tag_ids')
        partner_id = jdata.get('partner_id')
        email_from = jdata.get('email_from')
        x_mobile = jdata.get('x_mobile')
        x_phone = jdata.get('x_phone')
        task_id = jdata.get('task_id')
        attachment_id = jdata.get('attachment_id')
        description = jdata.get('description')

        tag = []
        if tag_ids != None:
            for x in tag_ids:
                tag.append(x['id'])

        vals = {"name1": name1,
                "priority": priority,
                "user_id":22,
                "stage_id":28,
                "x_claim_type": 547,
                "x_claim_status": 568,
                "x_claim_sub_status": 231,
                "x_claim_policy": x_claim_policy,
                "createdBy": createdBy,
                "tag_ids": [[6, False, tag]],
                "partner_id": partner_id,
                "email_from": email_from,
                "x_mobile": x_mobile,
                "x_phone": x_phone,
                "task_id": task_id,
                "x_description":description
                }
        cr, uid = registry.cursor(), request.session.uid
        cr._cnx.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        Model = request.env(cr, uid)['project.issue']
        q11 = Model.create(vals)
        cr.commit()
        cr.close()
        if q11:
            if attachment_id == None:
                pass
            else:
                for k in attachment_id:
                    cr.execute("UPDATE ir_attachment SET res_id =" + str(q1.id) + " WHERE id =" + str(k) + "")

                    # cr, uid = registry.cursor(), request.session.uid
                    # cr._cnx.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
                    # Model = request.env(cr, uid)['ir.attachment']
                    # m=Model.sudo().search([('id', '=',id)], limit=1)
                    # m.write({"res_id": q11.id})
                    # cr.commit()
                    # cr.close()
        return werkzeug.wrappers.Response(
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'),
                     ('Pragma', 'no-cache')],
            response=json.dumps({
                "id": q11.id,
                "status": 200,
                "message": "created successfully"
            }),
        )

    @http.route('/api/bimabachat/getticket', methods=['GET'], type='http', auth="public", website=True, cors='*')
    @check_permissions
    def getticket(self):
        try:
            temp = []
            uid = request.session.uid
            users = http.request.env['project.issue'].sudo().search(['|',('create_uid','=',uid),('createdBy','=',uid)])
            for i in users:
                tags = []
                for z in i.tag_ids:
                    tags.append({"id":z.id,"name":z.name})
                q1 = http.request.env['ir.attachment'].sudo().search([('res_id', '=', i.id)])
                temps = []
                if q1:
                    for r in q1:
                        temps.append({"id":r.id,"name": i.name,"url": 'https://bimabachat.in/web/content/' + str(r.id) + '?download=true'})
                vals = {"id":i.id,
                        "name":i.name if i.name !=False else '',
                        "name1": i.name1 if i.name1 != False else '',
                        "priority": i.priority if i.priority != False else '',
                        "user_id":{"id":i.user_id.id,"name":i.user_id.name} if i.user_id.id != False else [],
                        "stage_id":{"id":i.stage_id.id,"name":i.stage_id.name} if i.stage_id.id != False else [],
                        "x_claim_type":{"id":i.x_claim_type.id,"name":i.x_claim_type.name} if i.x_claim_type.id != False else [],
                        "x_claim_status":{"id":i.x_claim_status.id,"name":i.x_claim_status.name}  if i.x_claim_status.id != False else [],
                        "x_claim_sub_status":{"id":i.x_claim_sub_status.id,"name":i.x_claim_sub_status.name} if i.x_claim_sub_status.id != False else [],
                        "x_claim_policy": {"id":i.x_claim_policy.id,"name":i.x_claim_policy.name} if i.x_claim_policy.id != False else [],
                        "createdBy":{"id":i.createdBy.id,"name":i.createdBy.name} if i.createdBy.id != False else [],
                        "tag_ids": tags,
                        "partner_id": {"id":i.partner_id.id,"name":i.partner_id.name} if i.partner_id.id != False else [],
                        "email_from": i.email_from if i.email_from != False else '',
                        "x_mobile": i.x_mobile if i.x_mobile != False else '',
                        "x_phone": i.x_phone if i.x_phone != False else '',
                        "task_id": {"id":i.task_id.id,"name":i.task_id.name} if i.task_id.id != False else [],
                        "create_date": i.create_date,
                        "attachment_id":temps,
                        "description":i.x_description if i.x_description != False else '',
                        "deadline":i.x_deadline,
                        "replay_date": i.x_reply_date if i.x_reply_date != False else '',
                        "reply_time": i.x_reply_time if i.x_reply_time != False else '',
                        "write_date": i.write_date,
                        "reply":i.x_reply if i.x_reply != False else ''

                        }
                temp.append(vals)
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    'data': temp,
                    'message': 200
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
                    "message": "no record"
                }),
            )

    @http.route('/api/bimabachat/countticket', methods=['GET'], type='http', auth="public", website=True, cors='*')
    @check_permissions
    def count_ticket(self):
        try:
            temp = []
            uid = request.session.uid
            count = http.request.env['project.issue'].sudo().search_count(['|',('create_uid', '=', uid),('createdBy', '=', uid)])
            count_count = http.request.env['asktheexpert.asktheexpert'].sudo().search_count(['|',('create_uid', '=', uid),('createdBy','=',uid)])
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    'data': count + count_count,
                    'message': 200
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
                    "message": "no record"
                }),
            )





    @http.route('/api/bimabachat/getclaimtype', methods=['GET','POST'], type='http', auth="public",cors='*')
    @check_permissions
    def getticketclaimtype(self):
        try:
            temp = []
            users = http.request.env['subdata.subdata'].sudo().search([('id','=',[547,548])])
            for i in users:
                vals = {"id":i.id,
                        "name": i.name,
                        }
                temp.append(vals)
            print(temp,"claim")
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    'data': temp,
                    'message': 200
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
                    "message": "no record"
                }),
            )
    @http.route('/api/bimabachat/getclaimstatus', methods=['POST'], type='http', auth="public", website=True, cors='*',csrf=False)
    @check_permissions
    def getticketclaimstatus(self, **jdata):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}

            claimtypeid = jdata.get('claimtypeid')
            temp = []
            temps=[]
            if claimtypeid == 547:
                locations = http.request.env['infodata'].search([('name', '=', 97)])
                print(locations, "LOCATIONS")
                for i in locations:
                    temp.append(i.infosubdata.id)
            elif claimtypeid == 548:
                locations = http.request.env['infodata'].search([('name', '=', 62)])
                for i in locations:
                    temp.append(i.infosubdata.id)
            print(temp, "TEMPSSS")
            users = http.request.env['subdata.subdata'].sudo().search([('id', '=', temp)])
            for i in users:
                vals = {"id": i.id,
                        "name": i.name,
                        }
                temps.append(vals)
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    'data': temps,
                    'message': 200
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
                    "message": "no record"
                }),
            )

    @http.route('/api/bimabachat/getclaimsubstatus', methods=['POST'], type='http', auth="public", website=True,
                cors='*', csrf=False)
    @check_permissions
    def getticketclaimsubstatus(self):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            subclaimtypeid = jdata.get('subclaimtypeid')
            temp = []
            locations =  http.request.env['infosubdata'].search([('infoname', '=',subclaimtypeid)])
            temps = []
            for i in locations:
                temps.append(i.infosub1.id)
            print(temps,"tempsss")
            users = http.request.env['infosubdatadropdown'].sudo().search([('id', 'in', temps)])
            for i in users:
                vals = {"id": i.id,
                        "name": i.name,
                        }
                temp.append(vals)

            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    'data': temp,
                    'message': 200
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
                    "message": "no record"
                }),
            )


    @http.route('/api/bimabachat/creategrievence', methods=['POST'], type='http', auth="public", csrf=False, cors='*')
    @check_permissions
    def create_grievence_method(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        print(jdata)
        name1 = jdata.get('name1')
        email = jdata.get('email')
        company = jdata.get('company')
        phone = jdata.get('phone')
        status = jdata.get('status')
        subcategory = jdata.get('subcategory')
        description = jdata.get('description')
        issue_summary = jdata.get('issue_summary')
        tags = jdata.get('tags')
        assigned_to = jdata.get('assigned_to')
        createdBy = jdata.get('createdBy')
        company_name = jdata.get('company_name')
        contact_person = jdata.get('contact_person')
        contact_email = jdata.get('contact_email')
        contact_phone = jdata.get('contact_phone')
        contact_mobile = jdata.get('contact_mobile')
        docket_number = jdata.get('docket_number')
        initial_plan_days = jdata.get('initial_plan_days')
        replay = jdata.get('replay')
        replay_date = jdata.get('replay_date')
        deadline = jdata.get('deadline')
        attachment_id = jdata.get('attachment_id')
        stage_id = jdata.get('stage_id')
        tag_id = []
        if tags != None:
            for x in tags:
                tag_id.append(x['id'])

        vals = {
                "status":'Open',
                "name1": '',
                "email": email,
                "company": company,
                "phone": phone,
                "subcategory": subcategory,
                "description": description,
                "issue_summary": name1,
                "gri_tags": [[6, False, tag_id]],
                "assigned_to": 99,
                "createdBy": createdBy,
                "company_name": company_name,
                "contact_person": contact_person,
                "contact_email": contact_email,
                "contact_phone": contact_phone,
                "contact_mobile": contact_mobile,
                "docket_number": docket_number,
                "initial_plan_days": initial_plan_days,
                "replay": replay,
                "replay_date": replay_date,
                "deadline": deadline,
                "stage_id": 1,
                "form_page": 7
                }
        cr, uid = registry.cursor(), request.session.uid
        cr._cnx.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        Model = request.env(cr, uid)['asktheexpert.asktheexpert']
        q1 = Model.create(vals)
        cr.commit()
        cr.close()
        if q1:
            if attachment_id == None:
                pass
            else:
                for k in attachment_id:
                    attach_update = http.request.env['ir.attachment'].sudo().search([('id', '=', k)])
                    if attach_update:
                        attach_update.write({"res_id": q1.id})
                    else:
                        pass
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


    @http.route('/api/bimabachat/getgrievence', methods=['GET'], type='http', auth="public", website=True, cors='*')
    @check_permissions
    def get_grievence(self):
        # try:
            temp = []
            uid = request.session.uid
            users = http.request.env['asktheexpert.asktheexpert'].sudo().search([('createdBy','=',uid),('create_uid','=',uid),('form_page','=',7)])

            for i in users:
                tag_id = []
                for z in i.gri_tags:
                    tag_id.append({"id":z.id,"name":z.name})
                q1 = http.request.env['ir.attachment'].sudo().search([('res_id', '=', i.id)])
                print(q1,"Q!")
                temps = []
                if q1:
                    for r in q1:
                        temps.append({"id":r.id,
                                      "name": r.name,
                                      "url": 'https://bimabachat.in/web/content/' + str(r.id) + '?download=true'})

                vals = {
                        "id": i.id,
                        "name1": i.name1 if i.name1 != False else '',
                        "name": i.name if i.name != False else '',
                        "email": i.email if i.email != False else '',
                        "company":i.company if i.company != False else '',
                        "phone":i.phone if i.phone != False else '',
                        "status":i.status if i.status != False else '',
                        "subcategory":i.subcategory  if i.subcategory != False else '',
                        "description":i.description if i.description != False else '',
                        "issue_summary":i.issue_summary if i.issue_summary != False else '',
                        "assigned_to":{"id":i.assigned_to.id,"name":i.assigned_to.name} if i.assigned_to.id != False else [],
                        "stage_id":{"id":i.stage_id.id,"name":i.stage_id.name} if i.stage_id.id != False else [],
                        "tags": tag_id,
                        "createdBy": {"id":i.createdBy.id,"name":i.createdBy.name} if i.createdBy.id != False else [],
                        "company_name": i.company_name if i.company_name!= False else [],
                        "contact_email": i.contact_email if i.contact_email != False else '',
                        "contact_phone": i.contact_phone if i.contact_phone != False else '',
                        "contact_mobile": i.contact_mobile if i.contact_mobile != False else '',
                        "docket_number":{"id":i.docket_number.id,"name":i.docket_number.name} if i.docket_number.id != False else [],
                        "initial_plan_days": i.initial_plan_days if i.initial_plan_days != False else '',
                        "deadline": i.deadline if i.deadline != False else '',
                        "contact_person": {"id":i.contact_person.id,"name":i.contact_person.name} if i.contact_person.id != False else [],
                        "attachment_id":temps,
                        "create_date":i.create_date,
                        "replay_date": i.replay_date if i.replay_date != False else '',
                        "replay": i.replay if i.replay != False else '',
                        "reply_time":i.reply_time,
                        "write_date":i.write_date
                        }
                temp.append(vals)
            print(temp)

            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    'data': temp,
                    'message': 200
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
        #             "message": "no record"
        #         }),
        #     )
    @http.route('/api/bimabachat/getsubcategory', methods=['GET','POST'], type='http', auth="public",cors='*')
    @check_permissions
    def getsubcategory(self):
        try:
            temp = [{"key":'endow',"value":'Endowment Plan'},
                    {"key":'termplan',"value":'Term Plan'},
                    {"key":'annuity',"value":'Annuity and Pension'},
                    {"key":'moneyback',"value":'Money Back Plan'},
                    {"key":'wholelife',"value":'Whole Life Plan'},
                    {"key":'unitlink',"value":'Unit Link Plan'},
                    {"key":'termlifeins',"value":'Term Life Insurance'},
                    {"key":'gratuity',"value":'Gratuity Scheme'},
                    {"key":'superannuation',"value":'Superannuation Scheme'},
                    {"key":'leavescheme',"value":'Leave Encashment Scheme'},
                    {"key":'group',"value":'Group(EDLI)'},
                    {"key":'mediclaim',"value":'Mediclaim'},
                    {"key":'Sr. Citizen Mediclaim',"value":'Sr. Citizen Mediclaim'},
                    {"key":'Super Top -Up',"value":'Super Top -Up'},
                    {"key":'New Gen. Super Top Up',"value":'New Gen. Super Top Up'},
                    {"key":'Critical Illness',"value":'Critical Illness'},
                    {"key":'Diabetes',"value":'Diabetes'},
                    {"key":'Hospital Cash',"value":'Hospital Cash'},
                    {"key":'Dengue',"value":'Dengue'}]
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    'data': temp,
                    'message': 200
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
                    "message": "no record"
                }),
            )

    @http.route('/api/bimabachat/getstage_id', methods=['GET'], type='http', auth="public", website=True, cors='*')
    @check_permissions
    def stage_id_get(self):
        try:
            temp = []
            uid = request.session.uid
            count = http.request.env['stage.stage'].sudo().search([])
            for i in count:
                temp.append({'id':i.id,
                             'name':i.name})
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    'data': temp,
                    'message': 200
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
                    "message": "no record"
                }),
            )
