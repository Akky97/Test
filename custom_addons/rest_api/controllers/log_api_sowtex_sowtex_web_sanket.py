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

    @http.route('/api/log_pipeline', method=['POST'], type='http', auth='none', csrf=False ,cors='*')
    @check_permissions
    def api_top_count(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        # limit = jdata.get('limit')
        # model = jdata.get('model')
        sowtex_user_id = jdata.get('sowtex_user_id')
        if sowtex_user_id == '' or sowtex_user_id == None:
            sowtex_user_id = 0
        # if not model:
        #     error_descrip = "No model was provided in request!"
        #     error = 'No model name'
        #     _logger.error(error_descrip)
        #     return error_response(400, error, error_descrip)
        # if not partner_id:
        #     error_descrip = "No user_id was provided in request!"
        #     error = 'no_partner_id'
        #     _logger.error(error_descrip)
        #     return error_response(400, error, error_descrip)

        db_name = odoo.tools.config.get('db_name')
        if not db_name:
            _logger.error(
                "ERROR: To proper setup OAuth2 and Redis - it's necessary to set the parameter 'db_name' in Odoo config file!")
            print(
                "ERROR: To proper setup OAuth2 and Token Store - it's necessary to set the parameter 'db_name' in Odoo config file!")
        else:
            # Read system parameters...
            registry = Registry(db_name)
            with registry.cursor() as cr:
                aman1 =cr.execute("select id,x_sowtex_user_id from crm_lead where x_sowtex_user_id ='"+str(sowtex_user_id)+"'")
                r3 = (cr.dictfetchall())
                authdata = json.dumps(r3)
                all_authdata = json.loads(authdata)
                print(all_authdata)
                print (all_authdata[0]['id'],"inside 1")
                sowtex_user_id_id =all_authdata[0]['id']
                print (sowtex_user_id_id,"printe 2")
                aman =cr.execute("select t1.body,t1.author_id,t2.name,t1.record_name,t1.message_type,t1.id,t1.reply_to,t1.email_from,t1.model,t1.res_id,t1.subject,t1.create_date,t1.write_date, t1.subtype_id,t3.name as subtype_name from mail_message as t1 left join res_partner as t2 on t1.author_id = t2.id left join mail_message_subtype as t3 on t1.subtype_id = t3.id  where model='crm.lead' and res_id ='" +str(sowtex_user_id_id)+"' ORDER BY t1.create_date Desc ")
                r = (cr.dictfetchall())
                temp =[]

                auth = json.dumps(r)
                all = json.loads(auth)
                print(all)
                for id in all:
                    if id['id'] == None:
                        error = {
                            "message": "No Message Found",
                            "status_code": 0
                        }
                        return error
                    else:
                        cr.execute("select create_date,mail_message_id, field,id,field_desc,new_value_char from mail_tracking_value  where mail_message_id ='" + str(id['id'])+ "'")
                        r1 = (cr.dictfetchall())
                        mail_tracking_value=[]
                        for row in r1:
                            mail_tracking_value.append(row)
                        obj ={"mail_message":id,"mail_tracking_value":mail_tracking_value}
                        temp.append(obj)
                return werkzeug.wrappers.Response(
                    status=OUT__report__call_method__SUCCESS_CODE,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        'mai_message': temp,

                    }),
                )



