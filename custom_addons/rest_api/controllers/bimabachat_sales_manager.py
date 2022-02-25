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

    @http.route('/api/bimabachat/overdue_report_sales_manager', method=['POST'], type='http', auth='none', csrf=False, cors='*')
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
                cr.execute("Select t1.name,t3.name,t2.sale_team_id,t2.login"
                           " from crm_team as t1 left join res_users as t2 on t1.user_id = t2.id"
                           " left join res_partner as t3 on t2.partner_id = t3.id and t1.active =True")
                r = (cr.dictfetchall())
                temp = []
                auth = json.dumps(r)
                all = json.loads(auth)
                for id in all:
                    if id['login'] == None:
                        error = {
                            "message": "No login id Found",
                            "status_code": 0
                        }
                        return error
                    else:
                        cr.execute("select t1.id as pipelineid,t2.id,t3.name,t2.login ,t1.date_action,t1.name \
                                    from crm_lead as t1 \
                                    left join res_users as t2  on t1.user_id =t2.id \
                                    left join res_partner as t3 on t2.partner_id =t3.id \
                                    where t1.date_action < NOW() and t1.team_id ='" + str(id['sale_team_id']) + "' \
                                    group by t2.login,t3.name , t1.date_action,t1.name,t2.id,t1.id order by t3.name ")
                        r1 = (cr.dictfetchall())
                        auth = json.dumps(r1)
                        all = json.loads(auth)
                        tbl = "<table style='border: 1px solid black'><tr ><td style='border: 1px solid black'>Pipeline ID</td><td style='border: 1px solid black'>Overdue Date</td><td style='border: 1px solid black'>TASK</td></tr>"
                        for id1 in all:
                            overdue_date = id1['date_action']
                            tbl += "<tr><td style='border: 1px solid black'>" + str(
                                id1['pipelineid']) + "</td><td style='border: 1px solid black'>" + id1[
                                       'date_action'] + "</td><td style='border: 1px solid black'>" + id1[
                                       'name'] + "</td></tr>"
                        tbl += "</table>"

                    username = 'info@bimabachat.in'
                    password = 'info@2020'
                    try:
                        s = smtplib.SMTP('mail.mykumpany.com', 587)
                        s.starttls()
                        s.login(username, password)
                        li = id['login']

                        cc = "info@bimabachat.in"
                        msg = MIMEMultipart('alternative')
                        msg['from'] = "info@bimabachat.in(Team SIL)"
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
                                                                                                                                                 <p>Please login into your bimabachat.in account to check the Pipeline Overdue's Activity's details.</p>
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
                    except Exception as e:
                        pass
                    except smtplib.SMTPRecipientsRefused as e:
                        pass
                    #     return werkzeug.wrappers.Response(
                    #     status=OUT__report__call_method__SUCCESS_CODE,
                    #     content_type='application/json; charset=utf-8',
                    #     headers=[('Cache-Control', 'no-store'),
                    #              ('Pragma', 'no-cache')],
                    #     response=json.dumps({
                    #         'Send_overdues': "Successfully",
                    #         'Response': 200,
                    #         'error_msg': e
                    #
                    #     }),
                    # )
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















