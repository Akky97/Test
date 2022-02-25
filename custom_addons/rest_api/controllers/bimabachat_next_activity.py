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

    @http.route('/api/bimabachat/next_activity_cron_job', method=['POST'], type='http', auth='none', csrf=False,
                cors='*')
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
            query = "select distinct(t2.id),t3.name as name,t2.login from crm_lead as t1  \
                           left join res_users as t2  on t1.user_id =t2.id  \
                           left join res_partner as t3 on t2.partner_id =t3.id \
                           where to_char(t1.date_action,'yyyy-mm-dd') = to_char(NOW()+interval '1 day','yyyy-mm-dd') and not (t1.stage_id =27 or t1.stage_id =4) and t2.login is not null \
                           and t1.active =True and t1.date_action is not null group by t2.id,t3.name,t2.login  order by t3.name,t2.login "
            with registry.cursor() as cr:
                cr.execute(query)
                r = (cr.dictfetchall())
                temp = []
                auth = json.dumps(r)
                all = json.loads(auth)
                for id in all:
                    cr.execute("select t2.id,t3.name as salesperson,t2.login,t1.partner_name,t1.date_action,t1.name,t5.name as companyname, \
                         t1.id  as pipelineid,t4.name as subcategory ,t7.name as nextactivity,t8.name as stage,t1.date_deadline as deadline,t1.planned_revenue as plannedrevenue \
                         from crm_lead as t1 \
                         left join res_users as t2  on t1.user_id =t2.id \
                         left join res_partner as t3 on t2.partner_id =t3.id \
                         left join subcategory_subcategory as t4 on t1.x_subcategoryone =t4.id \
                         left join res_partner as t5 on t1.partner_id =t5.id \
                         left join crm_activity as t6 on t1.next_activity_id = t6.id \
                         left join mail_message_subtype as t7 on t6.subtype_id=t7.id \
                         left join crm_stage as t8 on t1.stage_id = t8.id \
                         where to_char(t1.date_action,'yyyy-mm-dd') = to_char(NOW()+interval '1 day','yyyy-mm-dd') \
                         and not (t1.stage_id =27 or t1.stage_id =4) and t1.date_action is not null and t1.user_id = '" + str(id['id']) + "' \
                         group by t2.login, t3.name,t1.partner_name, t1.date_action, t1.name, t2.id, t1.id, t4.name, t5.name, t7.name, t8.name, t1.date_deadline, t1.planned_revenue \
                         order  by  t3.name ")
                    r1 = (cr.dictfetchall())
                    auth = json.dumps(r1)
                    alldata = json.loads(auth)
                    tbl = "<table style='border: 1px solid black'>" \
                          "<tr><td style='border: 1px solid black'>PipelineId:</td>" \
                          "<td style='border: 1px solid black'>Next Activity Date</td>" \
                          "<td style='border: 1px solid black'>Opportunity</td>" \
                          "<td style='border: 1px solid black'>Customer</td>" \
                          "<td style='border: 1px solid black'>Company Name</td>" \
                          "<td style='border: 1px solid black'>Sub-Category</td>" \
                          "<td style='border: 1px solid black'>Sales Person</td>" \
                          "<td style='border: 1px solid black'>Next Activity</td>" \
                          "<td style='border: 1px solid black'>Stage</td>" \
                          "<td style='border: 1px solid black'>Expected Closing Date</td>" \
                          "<td style='border: 1px solid black'>Expected Revenue</td>" \
                          "</tr>"
                    for id1 in alldata:
                        next_activity = id1['date_action']
                        tbl += "<tr><td style='border: 1px solid black'>" + str(id1['pipelineid']) + "</td>" \
                                    "<td style='border: 1px solid black'>" + str(id1['date_action']) + "</td>" \
                                    "<td style='border: 1px solid black'>" + str(id1['name']) + "</td>" \
                                    "<td style='border: 1px solid black'>" + str(id1['companyname']) + "</td>" \
                                    "<td style='border: 1px solid black'>" + str(id1['partner_name']) + "</td>" \
                                    "<td style='border: 1px solid black'>" + str(id1['subcategory']) + "</td>" \
                                    "<td style='border: 1px solid black'>" + str(id1['salesperson']) + "</td>" \
                                    "<td style='border: 1px solid black'>" + str(id1['nextactivity']) + "</td>" \
                                    "<td style='border: 1px solid black'>" + str(id1['stage']) + "</td>" \
                                    "<td style='border: 1px solid black'>" + str(id1['deadline']) + "</td>" \
                                    "<td style='border: 1px solid black'>" + str(id1['plannedrevenue']) + "</td></tr>"
                    tbl += "</table>"
                    username = 'info@bimabachat.in'
                    password = 'info@2020'
                    s = smtplib.SMTP('mail.mykumpany.com', 587)
                    s.starttls()
                    s.login(username, password)
                    li = str(id['login'])
                    # li = "aman@vartulz.com"
                    # cc = "md@bimabachat.in"
                    msg = MIMEMultipart('alternative')
                    msg['from'] = "info@bimabachat.in(Team SIL)"
                    msg['To'] = li
                    # msg['cc'] = cc
                    print (msg['To'], "TO_msg")
                    msg['Subject'] = "NEXT ACTIVITIES NOTIFICATION"
                    rcpt = [li]
                    # rcpt = li + ',' + cc
                    print (msg, "msg")
                    body = """ <html>
                                                                                                                                                                                                                            <head></head>
                                                                                                                                                                                                                                                                    <body>

                                                                                                                                                                                                                                                                    <p>Hi """ + str(
                        id['name']) + """</p>
                                                                                                                                                                                                                                                                    <br>
                                                                                                                                                                                                                                                                    <p>Please find the attachment at your Today activity </p>
                                                                                                                                                                                                                                                                    <br>
                                                                                                                                                                                                                                                                    <br>
                                                                                                                                                                                                                                                                    <p>Please login into your bimabachat.in account to check the Pipeline Today Activity's details.</p>
                                                                                                                                                                                                                                                                    <br>
                                                                                                                                                                                                                                                                    """ + tbl + """
                                                                                                                                                                                                                                                                    <br>
                                                                                                                                                                                                                                                                    <br>

                                                                                                                                                                                                                                                                    <p>Best Regards,</p>
                                                                                                                                                                                                                                                                    <p>SECURITY INSURANCE BROKERS(INDIA) PVT.LTD.</p>
                                                                                                                                                                                                                                                                    <p>607,Skylark Buliding,60,Nehru Place,New Delhi-110019</p>
                                                                                                                                                                                                                                                                    <p><b>Tel:</b>46631111 <b>FAX:</b>41513257</p>
                                                                                                                                                                                                                                                                    <p><b>Mobile:</b>9312832371,8851109491</p>
                                                                                                                                                                                                                                                                    <p><b>E-mail:</b>info@bimabachat.in</p>
                                                                                                                                                                                                                                                                    <p><b>Web:</b>www.bimabachat.in<p>
                                                                                                                                                                                                                                                                    <p><b>IRDA Licence No.:</b>348,<b>CIN:</b>U67120DL2005PTC142231</p>

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
                        'next_activities': "Successfully",
                        'Response': 200,

                    }),
                )












