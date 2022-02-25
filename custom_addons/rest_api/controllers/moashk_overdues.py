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
from odoo.addons.base.ir.ir_mail_server import MailDeliveryException

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

    @http.route('/api/moashk/overdue_report', method=['POST'], type='http', auth='none', csrf=False, cors='*')
    def api_top_count(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
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
                                left join crm_stage as t4 on t1.stage_id =t4.id \
                                where t1.date_action < NOW() and t4.name NOT IN ('Close (Won)','Open (Lost)') and t2.login is not null \
                                group by t2.id,t3.name \
                                order by id")
                r = (cr.dictfetchall())
                temp = []
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
                        cr.execute("select t1.id as pipelineid,t2.id,t3.name,t2.login ,t1.date_action,t1.name \
                                    from crm_lead as t1 \
                                    left join res_users as t2  on t1.user_id =t2.id \
                                    left join res_partner as t3 on t2.partner_id =t3.id \
                                    left join crm_stage as t4 on t1.stage_id =t4.id \
                                    where t1.date_action < NOW() and t4.name NOT IN ('Close (Won)','Open (Lost)') and t1.user_id ='" + str(id['id']) + "' \
                                    group by t2.login,t3.name , t1.date_action,t1.name,t2.id,t1.id order by t3.name ")
                        r1 = (cr.dictfetchall())
                        auth = json.dumps(r1)
                        all = json.loads(auth)
                        tbl = "<table style='border: 1px solid black'><tr ><td style='border: 1px solid black'>Pipeline ID</td><td style='border: 1px solid black'>Overdue Date</td><td style='border: 1px solid black'>TASK</td></tr>"
                        for id1 in all:
                            overdue_date = id1['date_action']

                            print (overdue_date, "overdue_date")
                            tbl += "<tr><td style='border: 1px solid black'>" + str(
                                id1['pipelineid']) + "</td><td style='border: 1px solid black'>" + id1[
                                       'date_action'] + "</td><td style='border: 1px solid black'>" + id1[
                                       'name'] + "</td></tr>"
                        tbl += "</table>"
                        username = 'bharat@moashkinvestment.com'
                        password = 'Bharat@Moashk2020'
                        s = smtplib.SMTP_SSL('host.123servers.net', 465)
                        s.login(username, password)
                        s.login(username, password)
                        li = id['login']
                        # li = "aman@vartulz.com"
                        cc = "bharat@moashkinvest.com"
                        msg = MIMEMultipart('alternative')
                        msg['from'] = "bharat@moashkinvestment.com(Team Moashk)"
                        msg['To'] = li
                        msg['cc'] = cc
                        print (msg['To'], "TO_msg")
                        msg['Subject'] = "Pending Activity:" + str(id1['date_action']) + ""
                        rcpt = li + ',' + cc
                        body = """ <html>
                                                                   <head></head>
                                                                                                                                                                                            <body>

                                                                                                                                                                                            <p>Hi """ + str(
                            id['name']) + """</p>
                                                                                                                                                                                             <br>

                                                                                                                                                                                            <p>Please find the attachment at your Overdue's activity</p>
                                                                                                                                                                                            <br>
                                                                                                                                                                                            <br>
                                                                                                                                                                                            <p>Please login into your moashk.mykumpany.com account to check the Pipeline Overdue's Activity's details.</p>
                                                                                                                                                                                            <br>
                                                                                                                                                                                            """ + tbl + """
                                                                                                                                                                                            <br>
                                                                                                                                                                                            <br>
                                                                                                                                                                                            <p>Best Regards,</p>
                                                                                                                                                                                           <p>Team Moashk</p>



                                                                                                                                                                                            """

                        msg.attach(MIMEText(body, 'html'))
                        text = msg.as_string()
                        s.sendmail(username, rcpt, text)
                return werkzeug.wrappers.Response(
                        status=OUT__report__call_method__SUCCESS_CODE,
                        content_type='application/json; charset=utf-8',
                        headers=[('Cache-Control', 'no-store'),
                                 ('Pragma', 'no-cache')],
                        response=json.dumps({
                            'Send_overdues': "Successfully",
                            'Response': 200,
                            'message': 'Kripya Time pe kaam kiya karo'

                        }),
                    )

                    # except Exception as e:
                    #     pass
                    # except smtplib.SMTPRecipientsRefused as e:
                    #     pass
                    # #     return werkzeug.wrappers.Response(
                    # #     status=OUT__report__call_method__SUCCESS_CODE,
                    # #     content_type='application/json; charset=utf-8',
                    # #     headers=[('Cache-Control', 'no-store'),
                    # #              ('Pragma', 'no-cache')],
                    # #     response=json.dumps({
                    # #         'Send_overdues': "Successfully",
                    # #         'Response': 200,
                    # #         'error_msg': e
                    # #
                    # #     }),
                    # # )















