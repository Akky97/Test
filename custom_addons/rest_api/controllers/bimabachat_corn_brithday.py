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

    @http.route('/api/bimabachat/happy_birthday', method=['POST'], type='http', auth='none', csrf=False, cors='*')
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
                cr.execute("select name,email,to_char(x_dob, 'DD-MM') as dob from res_partner \
                            where to_char(NOW(), 'DD-MM') = to_char(x_dob, 'DD-MM')")
                r = (cr.dictfetchall())
                
                for i in r:
                    email=i['email']
                    name= i['name']
                    username = 'info@bimabachat.in'
                    password = 'info@2020'
                    s = smtplib.SMTP('mail.mykumpany.com', 587)
                    s.starttls()
                    s.login(username, password)
                    li = [email]
                    for i in range(len(li)):
                        print(i, "Email")
                        msg = MIMEMultipart('alternative')
                        msg['from'] = "info@bimabachat.in(Team SIL)"
                        msg['To'] = li[i]
                        print (msg['To'], "TO_msg")
                        msg['Subject'] = "Happy Birthday"
                        body = """ <html>
                                                                             <head></head>
                                                                                                                     <body>

                                                                                                                     <b><p>Dear """ + str(name) + """</p></b>
                                                                                                                     <br>
                                                                                                                     <b><p> Team SIB wishes you many happy returns of the day.</p><b>
            
                                                                                                                     <b><p>May the coming year be filled with peace,prosperity,good health and happiness.</p><b>
                                                                                                                    
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
                        s.sendmail(username, li[i], text)

                return werkzeug.wrappers.Response(
                    status=OUT__report__call_method__SUCCESS_CODE,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        'happy_birthday': "Successfully",
                        'Response': 200,
                    }),
                )











