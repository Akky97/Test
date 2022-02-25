# -*- coding: utf-8 -*-
from .main import *
import xmlrpclib
import calendar;
import time;
import base64, os
import json
from odoo.modules.registry import Registry
import odoo
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED
import requests
from instagram_private_api import Client, ClientCompatPatch

_logger = logging.getLogger(__name__)

# List of REST resources in current file:
#   (url prefix)        (method)        (action)
# /api/report/<method>  PUT         - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/report/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__report__call_method__SUCCESS_CODE = 200  # editable


#   Possible ERROR CODES:
#       501 'report_method_not_implemented'
#       409 'not_called_method_in_odoo'


# HTTP controller of REST resources:


class ControllerREST(http.Controller):

    # @http.route('/api/bimabachat/createpipelines',methods=['POST'],type='http',cors='*')
    @http.route('/api/bimabachat/createpipeline', methods=['POST'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def crmleadcreatedata(self):
        print("inside Routess")
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            datas = request.env['res.users'].sudo().search([('id', '=', request.session.uid)], limit=1)
            user_ids = request.env['res.partner'].sudo().search([('id', '=', datas.partner_id.id)], limit=1)
            name = jdata.get('name')
            attachment_id = jdata.get('attachment_id')
            partner_id = jdata.get('partner_id')
            planned_revenue = jdata.get('planned_revenue')
            partner_name = jdata.get('partner_name')
            email_from = jdata.get('email_from')
            mobile = jdata.get('mobile')
            panno = jdata.get('panno')
            assigned_to = user_ids.user_id.id
            referred = jdata.get('referred')
            stage_id = jdata.get('stage_id')
            x_categoryone = jdata.get('x_categoryone')
            x_subcategoryone = jdata.get('x_subcategoryone')
            next_activity_id = jdata.get('next_activity_id')
            date_deadline = jdata.get('date_deadline')
            campaign_id = jdata.get('campaign_id')
            source_id = jdata.get('source_id')
            medium_id = jdata.get('medium_id')
            contact_name = jdata.get('contact_name')
            title = jdata.get('title')
            x_gender = jdata.get('x_gender')
            x_dob = jdata.get('x_dob')
            x_sum_insured = jdata.get('x_sum_insured')
            x_self_dob = jdata.get('x_self_dob')
            x_spouce_dob = jdata.get('x_spouce_dob')
            x_child_one_dob = jdata.get('x_child_one_dob')
            x_child_two_dob = jdata.get('x_child_two_dob')
            x_adult_child_one_dob = jdata.get('x_adult_child_one_dob')
            x_adult_child_two_dob = jdata.get('x_adult_child_two_dob')
            x_other_detail = jdata.get('x_other_detail')
            x_pre_medical = jdata.get('x_pre_medical')
            street = jdata.get('street')
            street2 = jdata.get('street2')
            city = jdata.get('city')
            state_id = jdata.get('state_id')
            zip = jdata.get('zip')
            country_id = jdata.get('country_id')
            x_upload_condition = jdata.get('x_upload_condition')
            x_details_condition = jdata.get('x_details_condition')
            phone = jdata.get('phone')
            fax = jdata.get('fax')
            day_open = jdata.get('day_open')
            day_close = jdata.get('day_close')
            tag_ids = jdata.get('tag_ids')
            description=jdata.get('description')
            title_action =jdata.get('title_action')
            date_action =jdata.get('date_action')
            tag = []
            print jdata,"jdta"
            if  tag_ids !=None:
                for x in tag_ids:
                    print(x['id'],"xxxx")
                    tag.append(x['id'])
            vals = {
                "name": name,
                "partner_id": partner_id,
                "partner_name": partner_name,
                "email_from": email_from,
                "mobile": mobile,
                "function": panno,
                "user_id": user_ids.user_id.id,
                "referred": referred,
                "planned_revenue": planned_revenue,
                "stage_id": 9,
                "x_categoryone": x_categoryone,
                "x_subcategoryone": x_subcategoryone,
                "next_activity_id": next_activity_id,
                "date_deadline": date_deadline,
                "campaign_id": campaign_id,
                "medium_id": medium_id,
                "source_id": source_id,
                "contact_name": contact_name,
                "title": title,
                "x_gender": x_gender,
                "x_dob": x_dob,
                "x_sum_insured": x_sum_insured,
                "x_self_dob": x_self_dob,
                "x_spouce_dob": x_spouce_dob,
                "x_child_one_dob": x_child_one_dob,
                "x_child_two_dob": x_child_two_dob,
                "x_adult_child_one_dob": x_adult_child_one_dob,
                "x_adult_child_two_dob": x_adult_child_two_dob,
                "x_other_detail": x_other_detail,
                "x_pre_medical": x_pre_medical,
                "street": street,
                "street2": street2,
                "city": city,
                "state_id": state_id,
                "zip": zip,
                "country_id": country_id,
                "x_upload_condition": x_upload_condition,
                "x_details_condition": x_details_condition,
                "phone": phone,
                "fax": fax,
                "day_open": day_open,
                "day_close": day_close,
                "tag_ids": [[6, False, tag]],
                "date_action":date_action,
                "description":description,
                "title_action":title_action

            }
            # if not db_name:
            #     _logger.error(
            #         "ERROR: To proper setup OAuth2 and Redis - it's necessary to set the parameter 'db_name' in Odoo config file!")
            #     print(
            #         "ERROR: To proper setup OAuth2 and Token Store - it's necessary to set the parameter 'db_name' in Odoo config file!")
            # else:
            #     # Read system parameters...
            #     registry = Registry(db_name)
            #     with registry.cursor() as cr:
            #         aman = cr.execute("INSERT INTO crm_lead (name, address) VALUES ")
            #         r = (cr.dictfetchall())
            #         temp = []
            #         auth = json.dumps(r)
            #         all = json.loads(auth)
            cr, uid = registry.cursor(), request.session.uid
            cr._cnx.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
            Model = request.env(cr, uid)['crm.lead']
            q1 = Model.sudo().create(vals)
            cr.execute("UPDATE crm_lead SET create_uid =" + str(request.session.uid) +" WHERE id =" + str(q1.id) + "")
            gcm_id = datas.x_gcm_id
            message = "You have Got the New Pipeline"
            assign_message = "You have Got the New Pipeline"
            title = "Pipeline is Created"
            cr.execute("Insert into apinotification_apinotification(user_id,model_name,model_id,create_date,message,image,title) values('" + str(datas.id) + "','crm.lead','" + str(q1.id) + "','" + str(q1.create_date) + "','" + str(
                    message) + "','https://bimabachat.in/web/static/src/img/logo-bima-bachat.png','Pipeline')")

            self.noti_send(gcm_id, assign_message, title)
            if q1:
                if attachment_id:
                    for k in attachment_id:
                        print(k,"KKS")
                        cr.execute("UPDATE ir_attachment SET res_id =" + str(q1.id) + " WHERE id =" +str(k) + "")

            cr.commit()
            cr.close()


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
        except Exception as e:
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    "error":str(e),
                    "status": 400,
                    "message": " not created "
                }),
            )

    @http.route('/api/bimabachat/getpipelines1', methods=['POST'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def crmleadcreatedata11(self):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            partner_id = jdata.get('partner_id')
            create_uid = jdata.get('create_uid')
            print (partner_id,create_uid,"qwertyuio")
            if not partner_id:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        "status": 400,
                        "message": "Partner_id is Required"
                    }),
                )
            if not create_uid:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        "status": 400,
                        "message": "Create_uid is Required"
                    }),
                )
            tempq3 = []
            child_ids = http.request.env['res.partner'].search([('id', '=', partner_id)]).child_ids.ids
            q3 = http.request.env['policytransaction'].sudo().search(['|',('clientname','in',child_ids),('clientname', '=', int(partner_id))])
            for j in q3:
                tags = []
                for i in j.group_tag_ids:
                    tags.append({"id": i.id, "name": i.name})
                vals_q3 = {

                    "id": j.id,
                    "clientname": {"id": j.clientname.id,
                                   "name": j.clientname.name} if j.clientname.id != False else [],
                    'group': j.group if j.group != False else '',
                    "product_id": {"id": j.product_id.id,
                                   "name": j.product_id.name} if j.product_id.id != False else [],
                    'policyno': j.policyno if j.policyno != False else '',
                    'group_phone': j.group_phone if j.group_phone != False else '',
                    'group_email': j.group_email if j.group_email != False else '',
                    "rm": {"id": j.rm.id, "name": j.rm.name} if j.rm.id != False else [],
                    "insurername123": {"id": j.insurername123.id,
                                       "name": j.insurername123.name} if j.insurername123.id != False else [],
                    'startfrom': j.startfrom if j.startfrom != False else '',
                    'expiry': j.expiry if j.expiry != False else '',
                    'suminsured': j.suminsured if j.suminsured != False else '',
                    'grossprem': j.grossprem if j.grossprem != False else '',
                    'renewal_opt': j.renewal_opt if j.renewal_opt != False else '',
                    'remark': j.remark if j.remark != False else '',
                }
                tempq3.append(vals_q3)
            # child_ids =http.request.env['res.partner'].search([('id', '=', partner_id)]).child_ids.ids
            # print child_ids,"CHILDSS"
            # cr, uid = registry.cursor(), request.session.uid
            # cr._cnx.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
            # Model = request.env(cr, uid)['crm.lead']
            # q2 =http.request.env['crm.lead'].sudo().search(['|','|',('create_uid', '=', create_uid), ('partner_id', '=', partner_id),('partner_id','in',child_ids),('stage_id', '=', 4)])

            # for i in q2:

            # temp = []
            # for c in q2:
            #     tags = []
            #
            #     for i in c.tag_ids:
            #         tags.append({"id": i.id, "name": i.name})
            #     vals = {'id': c.id,
            #             'name': c.name if c.name != False else '',
            #             'planned_revenue': c.planned_revenue if c.planned_revenue != False else '',
            #             'probability': c.probability if c.probability != False else '',
            #             'email_from': c.email_from if c.email_from != False else '',
            #             'phone': c.phone if c.phone != False else '',
            #             'mobile': c.mobile if c.mobile != False else '',
            #             'city': c.city if c.city != False else '',
            #             'x_priority': c.x_priority if c.x_priority != False else '',
            #             'street': c.street if c.street != False else '',
            #             'street2': c.street2 if c.street2 != False else '',
            #             'description': c.description if c.description != False else '',
            #             'zip': c.zip if c.zip != False else '',
            #             'partner_name': c.partner_name if c.partner_name != False else '',
            #             'function': c.function if c.function != False else '',
            #             'referred': c.referred if c.referred != False else '',
            #             'title_action': c.title_action if c.title_action != False else '',
            #             'create_date': c.create_date if c.create_date != False else '',
            #             'write_date': c.write_date if c.write_date != False else '',
            #             'date_action': c.date_action if c.date_action != False else '',
            #             'date_deadline': c.date_deadline if c.date_deadline != False else '',
            #             'contact_name': c.contact_name if c.contact_name != False else '',
            #             'fax': c.fax if c.fax != False else '',
            #             'opt_out': c.opt_out if c.opt_out != False else '',
            #             'create_uid': c.create_uid.id if c.create_uid.id != False else '',
            #             'write_uid': c.write_uid.id if c.write_uid.id != False else '',
            #             "user_id": {"id": c.user_id.id, "name": c.user_id.name} if c.user_id.id != False else [],
            #             # "sale_team_id": {"id":c.sale_team_id.id, "name": c.sale_team_id.name} if c.sale_team_id.id != False else [],
            #             "partner_id": {"id": c.partner_id.id,
            #                            "name": c.partner_id.name} if c.partner_id.id != False else [],
            #             "title": {"id": c.title.id, "name": c.partner_id.name} if c.title.id != False else [],
            #             "country_id": {"id": c.country_id.id,
            #                            "name": c.partner_id.name} if c.country_id.id != False else [],
            #             "team_id": {"id": c.team_id.id, "name": c.team_id.name} if c.team_id.id != False else [],
            #             "stage_id": {"id": c.stage_id.id, "name": c.stage_id.name} if c.stage_id.id != False else [],
            #             "campaign_id": {"id": c.campaign_id.id,
            #                             "name": c.campaign_id.name} if c.campaign_id.id != False else [],
            #             "medium_id": {"id": c.medium_id.id,
            #                           "name": c.medium_id.name} if c.medium_id.id != False else [],
            #             "source_id": {"id": c.source_id.id,
            #                           "name": c.source_id.name} if c.source_id.id != False else [],
            #             "x_categoryone": [{"id": c.x_categoryone.id,
            #                                "name": c.x_categoryone.name}] if c.x_categoryone.id != False else [],
            #             "tag_ids": tags,
            #             "next_activity_id": {"id": c.next_activity_id.id,
            #                                  "name": c.next_activity_id.name} if c.next_activity_id.id != False else [],
            #             'x_subcategoryone': {"id": c.x_subcategoryone.id,
            #                                  "name": c.x_subcategoryone.name} if c.x_subcategoryone.id != False else [],
            #             }
            #     temp.append(vals)
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    "data": tempq3,
                    "status": 200,
                    "message": "created successfully"
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
                    "message": " not created "
                }),
            )

    @http.route('/api/bimabachat/crm_lead_count', methods=['GET','POST'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def crm_lead_counts(self):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            partner_id = jdata.get('partner_id')
            create_uid = jdata.get('create_uid')
            print (partner_id, create_uid, "qwertyuio")
            if not partner_id:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        "status": 400,
                        "message": "Partner_id is Required"
                    }),
                )
            if not create_uid:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        "status": 400,
                        "message": "Create_uid is Required"
                    }),
                )
            child_ids = http.request.env['res.partner'].search([('id', '=', partner_id)]).child_ids.ids
            stage_close = http.request.env['crm.lead'].sudo().search([])
            policy_trans = http.request.env['policytransaction'].sudo().search([])
            total_count_4 =stage_close.search(['|','|',('create_uid', '=', create_uid), ('partner_id', '=', partner_id),('partner_id','=',child_ids),('stage_id', '!=', 4)])
            total_count_all =policy_trans.search(['|',('clientname','in',child_ids),('clientname', '=', partner_id)])
            # total_count_all =total_count_alll.search(['stage_id','not in',[4]])
            print(len(total_count_4),"RRRRRRRRRRRRRRRRRRRRRR")
            print(len(total_count_all),"PPPPPPPPPPPPPPPPPPPPp")
            total = len(total_count_4) + len(total_count_all)
            print(total,"TTTTTTTTTTTTTTTTTTTTTTTTTttt")
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    "data":total,
                    "status": 200,
                    "message": "created successfully"
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
                    "message": " not created "
                }),
            )




    @http.route('/api/bimabachat/getpipelines', methods=['POST'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def crmleadcreatedata1(self):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            partner_id = jdata.get('partner_id')
            create_uid = jdata.get('create_uid')
            print (partner_id,create_uid,"qwertyuio")
            if not partner_id:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        "status": 400,
                        "message": "Partner_id is Required"
                    }),
                )
            if not create_uid:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        "status": 400,
                        "message": "Create_uid is Required"
                    }),
                )
            child_ids =http.request.env['res.partner'].search([('id', '=', partner_id)]).child_ids.ids
            q1 = http.request.env['crm.lead'].sudo().search([])
            q2 = q1.search(['|','|',('create_uid', '=', create_uid), ('partner_id', '=', partner_id),('partner_id','in',child_ids),('stage_id', '!=', 4)])
            print(q2,"hhjjsbfbrfbf")
            temp = []
            # tempq3 = []
            # for i in q2:
            #     if i.stage_id.id is not 4:
            #         q3 = http.request.env['policytransaction'].sudo().search([('pipeline_store','=', int(i.id))])
            #         for j in q3:
            #             tags = []
            #             for i in j.group_tag_ids:
            #                 tags.append({"id": i.id, "name": i.name})
            #             vals_q3 = { "clientname": {"id": j.clientname.id, "name": j.clientname.name} if j.clientname.id != False else [],
            #                         'group': j.group if j.group != False else '',
            #                         "product_id": {"id": j.product_id.id, "name": j.product_id.name} if j.product_id.id != False else [],
            #                         'policyno': j.policyno if j.policyno != False else '',
            #                         'group_phone': j.group_phone if j.group_phone != False else '',
            #                         'group_email': j.group_email if j.group_email != False else '',
            #                         "rm": {"id": j.rm.id,"name": j.rm.name} if j.rm.id != False else [],
            #                         "insurername123": {"id": j.insurername123.id,"name": j.insurername123.name} if j.insurername123.id != False else [],
            #                         'startfrom': j.startfrom if j.startfrom != False else '',
            #                         'expiry': j.expiry if j.expiry != False else '',
            #                         'suminsured': j.suminsured if j.suminsured != False else '',
            #                         'grossprem': j.grossprem if j.grossprem != False else '',
            #                         'renewal_opt': j.renewal_opt if j.renewal_opt != False else '',
            #                         'remark': j.remark if j.remark != False else '',
            #                     }
            #             tempq3.append(vals_q3)
            for c in q2:
                if c.stage_id.id is not 4:
                    print(c.stage_id.id,"IDDDDDDDDDDDDssssssssss")
                    tags = []
                    for i in c.tag_ids:
                        tags.append({"id": i.id, "name": i.name})
                    vals = {'id': c.id,
                            'name': c.name if c.name != False else '',
                            'planned_revenue': c.planned_revenue if c.planned_revenue != False else '',
                            'probability': c.probability if c.probability != False else '',
                            'email_from': c.email_from if c.email_from != False else '',
                            'phone': c.phone if c.phone != False else '',
                            'mobile': c.mobile if c.mobile != False else '',
                            'city': c.city if c.city != False else '',
                            'x_priority': c.x_priority if c.x_priority != False else '',
                            'street': c.street if c.street != False else '',
                            'street2': c.street2 if c.street2 != False else '',
                            'description': c.description if c.description != False else '',
                            'zip': c.zip if c.zip != False else '',
                            'partner_name': c.partner_name if c.partner_name != False else '',
                            'function': c.function if c.function != False else '',
                            'referred': c.referred if c.referred != False else '',
                            'title_action': c.title_action if c.title_action != False else '',
                            'create_date': c.create_date if c.create_date != False else '',
                            'write_date': c.write_date if c.write_date != False else '',
                            'date_action': c.date_action if c.date_action != False else '',
                            'date_deadline': c.date_deadline if c.date_deadline != False else '',
                            'contact_name': c.contact_name if c.contact_name != False else '',
                            'fax': c.fax if c.fax != False else '',
                            'opt_out': c.opt_out if c.opt_out != False else '',
                            'create_uid': c.create_uid.id if c.create_uid.id != False else '',
                            'write_uid': c.write_uid.id if c.write_uid.id != False else '',
                            "user_id": {"id": c.user_id.id, "name": c.user_id.name} if c.user_id.id != False else [],
                            # "sale_team_id": {"id":c.sale_team_id.id, "name": c.sale_team_id.name} if c.sale_team_id.id != False else [],
                            "partner_id": {"id": c.partner_id.id,
                                           "name": c.partner_id.name} if c.partner_id.id != False else [],
                            "title": {"id": c.title.id, "name": c.partner_id.name} if c.title.id != False else [],
                            "country_id": {"id": c.country_id.id,
                                           "name": c.partner_id.name} if c.country_id.id != False else [],
                            "team_id": {"id": c.team_id.id, "name": c.team_id.name} if c.team_id.id != False else [],
                            "stage_id": {"id": c.stage_id.id, "name": c.stage_id.name} if c.stage_id.id != False else [],
                            "campaign_id": {"id": c.campaign_id.id,
                                            "name": c.campaign_id.name} if c.campaign_id.id != False else [],
                            "medium_id": {"id": c.medium_id.id, "name": c.medium_id.name} if c.medium_id.id != False else [],
                            "source_id": {"id": c.source_id.id, "name": c.source_id.name} if c.source_id.id != False else [],
                            "x_categoryone": [{"id": c.x_categoryone.id,
                                              "name": c.x_categoryone.name}]if c.x_categoryone.id != False else [],
                            "tag_ids": tags,
                            "next_activity_id": {"id": c.next_activity_id.id,
                                                 "name": c.next_activity_id.name} if c.next_activity_id.id != False else [],
                            'x_subcategoryone': {"id": c.x_subcategoryone.id,
                                                 "name": c.x_subcategoryone.name} if c.x_subcategoryone.id != False else [],
                            }
                    temp.append(vals)
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    "data": temp,
                    "status": 200,
                    "message": "created successfully"
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
                    "message": " not created "
                }),
            )


    @http.route('/api/bimabachat/editpipeline/<id>/', methods=['POST','PUT'], type='http', auth='none', csrf=False, cors='*')
    @check_permissions
    def crmleadupdatedata(self,id):
        print("inside Routess")
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if not id:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        "error": "Update ID not in Request",
                        "status": 400,
                    }),
                )
            data = http.request.env['crm.lead'].sudo().search([('id', '=',int(id))])
            print(data, "DATA")
            if not data:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        "status": 400,
                        "message": "no data found"
                    }),
                )
            else:
                datas = request.env['res.users'].sudo().search([('id', '=', request.session.uid)], limit=1)
                user_ids = request.env['res.partner'].sudo().search([('id', '=',datas.partner_id.id)],limit=1)
                name = jdata.get('name')
                attachment_id = jdata.get('attachment_id')
                partner_id = jdata.get('partner_id')
                planned_revenue = jdata.get('planned_revenue')
                partner_name = jdata.get('partner_name')
                email_from = jdata.get('email_from')
                mobile = jdata.get('mobile')
                panno = jdata.get('panno')
                # assigned_to = jdata.get('assigned_to')
                assigned_to = user_ids.user_id.id
                referred = jdata.get('referred')
                stage_id = jdata.get('stage_id')
                x_categoryone = jdata.get('x_categoryone')
                x_subcategoryone = jdata.get('x_subcategoryone')
                next_activity_id = jdata.get('next_activity_id')
                date_deadline = jdata.get('date_deadline')
                campaign_id = jdata.get('campaign_id')
                source_id = jdata.get('source_id')
                medium_id = jdata.get('medium_id')
                contact_name = jdata.get('contact_name')
                title = jdata.get('title')
                x_gender = jdata.get('x_gender')
                x_dob = jdata.get('x_dob')
                x_sum_insured = jdata.get('x_sum_insured')
                x_self_dob = jdata.get('x_self_dob')
                x_spouce_dob = jdata.get('x_spouce_dob')
                x_child_one_dob = jdata.get('x_child_one_dob')
                x_child_two_dob = jdata.get('x_child_two_dob')
                x_adult_child_one_dob = jdata.get('x_adult_child_one_dob')
                x_adult_child_two_dob = jdata.get('x_adult_child_two_dob')
                x_other_detail = jdata.get('x_other_detail')
                x_pre_medical = jdata.get('x_pre_medical')
                street = jdata.get('street')
                street2 = jdata.get('street2')
                city = jdata.get('city')
                state_id = jdata.get('state_id')
                zip = jdata.get('zip')
                country_id = jdata.get('country_id')
                x_upload_condition = jdata.get('x_upload_condition')
                x_details_condition = jdata.get('x_details_condition')
                phone = jdata.get('phone')
                fax = jdata.get('fax')
                day_open = jdata.get('day_open')
                day_close = jdata.get('day_close')
                tag_ids = jdata.get('tag_ids')
                description = jdata.get('description')
                title_action = jdata.get('title_action')
                date_action = jdata.get('date_action')

                tag = []

                print jdata, "jdta"
                if tag_ids != None:
                    for x in tag_ids:
                        print(x['id'], "xxxx")
                        tag.append(x['id'])
                vals = {
                    "name": name,
                    "partner_id": partner_id,
                    "partner_name": partner_name,
                    "email_from": email_from,
                    "mobile": mobile,
                    "function": panno,
                    "user_id": assigned_to,
                    "referred": referred,
                    "planned_revenue": planned_revenue,
                    "stage_id": stage_id,
                    "x_categoryone": x_categoryone,
                    "x_subcategoryone": x_subcategoryone,
                    "next_activity_id": next_activity_id,
                    "date_deadline": date_deadline,
                    "campaign_id": campaign_id,
                    "medium_id": medium_id,
                    "source_id": source_id,
                    "contact_name": contact_name,
                    "title": title,
                    "x_gender": x_gender,
                    "x_dob": x_dob,
                    "x_sum_insured": x_sum_insured,
                    "x_self_dob": x_self_dob,
                    "x_spouce_dob": x_spouce_dob,
                    "x_child_one_dob": x_child_one_dob,
                    "x_child_two_dob": x_child_two_dob,
                    "x_adult_child_one_dob": x_adult_child_one_dob,
                    "x_adult_child_two_dob": x_adult_child_two_dob,
                    "x_other_detail": x_other_detail,
                    "x_pre_medical": x_pre_medical,
                    "street": street,
                    "street2": street2,
                    "city": city,
                    "state_id": state_id,
                    "zip": zip,
                    "country_id": country_id,
                    "x_upload_condition": x_upload_condition,
                    "x_details_condition": x_details_condition,
                    "phone": phone,
                    "fax": fax,
                    "day_open": day_open,
                    "day_close": day_close,
                    "tag_ids": [[6, False, tag]],
                    "date_action": date_action,
                    "description": description,
                    "title_action": title_action

                }
            data.sudo().write(vals)
            data.sudo().write({"write_uid":request.session.uid})
            if attachment_id:
                for i in attachment_id:
                    attach = http.request.env['ir.attachment'].sudo().search([("id",'=',i)])
                    attach.sudo().write({"res_id":data.id})
            # with registry.cursor() as cr:
            #     print("UPDATE crm_lead SET create_uid =" + str(request.session.uid) + " WHERE id =" + str(data.id) + "")
            #     cr.execute("UPDATE crm_lead SET create_uid ='" + str(request.session.uid) + "' WHERE id ='" + str(data.id) + "'")

            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    "id": data.id,
                    "status": 200,
                    "message": "successfully Updated"
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
                    "message": "not created"
                }),
            )

    def noti_send(self,gcm_id,assign_message,title):
        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": "Basic AAAA2F4_NL4:APA91bFEyx8QEcQLuwPe7r_sv6jp4P1dvhb77Ze0iLFy-daFT9-FzH3ifc8uCAZauREMpjFbDTPEpm2-vTpu-6EqaPV_BBVkv_AlOu-KMUe72MtIfKAWMqEUXYQ3G0ccSgca9sh59PVB"}

        payload = {"app_id": "df4580a8-0f6e-4a5a-b95d-1d6f8bcfcb6a",
                   "include_player_ids": [gcm_id],
                   "contents": {"en": assign_message,
                                "headings": title
                                }
                   }
        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
        print(req.status_code, req.reason)

    @http.route('/instagram/user_info', auth='public', cors='*', csrf=False)
    def index(self, **post):
        try:
            username = post.get('username')
            password = post.get('password')
            api = Client(username, password)
            results = api.username_feed(username)
            if results:
                user_info = api.user_detail_info(results['items'][0]['user']['pk'])
                if user_info:
                    return json.dumps({"media_count": user_info['user_detail']['user']['media_count'],
                                       "follower": user_info['user_detail']['user']['follower_count'],
                                       "following": user_info['user_detail']['user']['following_count'],
                                       "profile_pic": user_info['user_detail']['user']['profile_pic_url']})

        except Exception as e:
            return json.dumps({"error": str(e)})
