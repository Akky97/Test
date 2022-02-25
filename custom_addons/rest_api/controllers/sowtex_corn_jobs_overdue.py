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

    @http.route('/api/overdue_report', method=['POST'], type='http', auth='none', csrf=False ,cors='*')
    def api_top_count(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        # limit = jdata.get('limit')
        # model = jdata.get('model')
        # channel_id = jdata.get('channel_id')
        # if channel_id == '' or channel_id == None:
        #     channel_id = 0
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
                cr.execute("select t2.id,t3.name,t2.login from crm_lead as t1 left join res_users as t2  on t1.user_id =t2.id \
                                left join res_partner as t3 on t2.partner_id =t3.id \
                                where t1.date_action < NOW() \
                                group by t2.id,t3.name \
                                order by id")
                r = (cr.dictfetchall())
                temp =[]
                auth = json.dumps(r)
                all = json.loads(auth)
                for id in all:
                    print (id['id'])
                    print (id['login'])
                    if id['id'] == None:
                        error = {
                            "message": "No id Found",
                            "status_code": 0
                        }
                        return error
                    else:
                        cr.execute("select t2.id,t3.name,t2.login ,t1.date_action,t1.name \
                                    from crm_lead as t1 \
                                    left join res_users as t2  on t1.user_id =t2.id \
                                    left join res_partner as t3 on t2.partner_id =t3.id \
                                    where t1.date_action < NOW() and t1.user_id ='"+str(id['id'])+"' \
                                    group by t2.login,t3.name , t1.date_action,t1.name,t2.id order by t3.name ")
                        r1 = (cr.dictfetchall())
                        auth = json.dumps(r1)
                        all = json.loads(auth)
                        tbl = "<table style='border: 1px solid black'><tr ><td style='border: 1px solid black'>Overdue Date</td><td style='border: 1px solid black'>TASK</td></tr>"
                        for id1 in all:
                            overdue_date =id1['date_action']

                            print (overdue_date,"overdue_date")
                            tbl += "<tr><td style='border: 1px solid black'>"+id1['date_action']+"</td><td style='border: 1px solid black'>"+id1['name']+"</td></tr>"
                        tbl += "</table>"




                    username = 'sowtex@mykumpany.com'
                    password = 'sowtex@2020'
                    s = smtplib.SMTP('mail.mykumpany.com', 587)
                    s.starttls()
                    s.login(username, password)
                    li = [id['login']]
                    for i in range(len(li)):
                        print(i, "Email")
                        msg = MIMEMultipart('alternative')
                        msg['from'] = "sowtex@mykumpany.com(Team Sowtex)"
                        msg['To'] = li[i]
                        print (msg['To'], "TO_msg")
                        msg['Subject'] = "Pending Overdue's"
                        body = """ <html>
                                             <head></head>
                                                                                     <body>
    
                                                                                     <p>Hi """ + str(id['name']) + """</p>
                                                                                     <br>
                                                                                     <p> You have received your Overdue's Tickets.</p>
                                                                                     <br>
                                                                                     <br>
                                                                                     <p>Please login into your sowtex.mykumpany.com account to check the Pipeline Overdue's details.</p>
                                                                                     <br>
                                                                                     """+ tbl +"""
                                                                                     <br>
                                                                                     <br>
                                                                                     <p>Best Regards,</p>
                                                                                     <p>Team Sowtex</p>
                                                                                     """

                        msg.attach(MIMEText(body, 'html'))
                        text = msg.as_string()
                        s.sendmail(username, li[i], text)


                return werkzeug.wrappers.Response(
                    status=OUT__report__call_method__SUCCESS_CODE,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        'Send_overdues': "Successfully",
                        'Response':200,
                        'message':'Kripya Time pe kaam kiya karo'

                    }),
                )








