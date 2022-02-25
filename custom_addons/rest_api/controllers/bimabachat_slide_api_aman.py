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

    @http.route('/api/slideslidechannel1', method=['POST'], type='http', auth='none', csrf=False ,cors='*')
    @check_permissions
    def api_top_count(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        channel_id = jdata.get('channel_id')
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
                cr.execute("select t1.name,t1.description,t1.url as website_url,t1.channel_id ,t2.id,t1.id as slide_id from slide_slide as t1 \
                            left join ir_attachment as t2 on t1.id=t2.id and res_field ='image' \
                             where t1.channel_id ='"+str(channel_id)+"' and t1.active =true")
                r3 = (cr.dictfetchall())
                temp=[]
                for i in r3:
                    cr.execute("select id ,name from slide_channel where id =" + str(i['channel_id']) + "")
                    r4 = (cr.dictfetchall())
                    tag_ids=[]
                    channel_id=({'id':r4[0]['id'],'name':r4[0]['name']})
                    cr.execute("select t1.tag_id ,t2.name from rel_slide_tag as t1 \
                                left join slide_tag as t2 on t1.tag_id =t2.id \
                                where t1.slide_id ='" + str(i['slide_id']) + "'")
                    r5 = (cr.dictfetchall())
                    for k in r5:
                        tag_ids.append({'id':k['tag_id'],'name':k['name']})
                    obj = {'name': r3[0]['name'],
                           'description': r3[0]['description'],
                           'website_url': 'https://bimabachat.in/slides/slide/'+str(r3[0]['id']),
                           'channel_id': channel_id,
                           'tag_ids':tag_ids,
                           'id':'https://bimabachat.in/web/image/slide.slide/'+str(r3[0]['id'])+'/image'
                           }
                    temp.append(obj)

                return werkzeug.wrappers.Response(
                    status=OUT__report__call_method__SUCCESS_CODE,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        'slide_slide': temp,
                        'slide_url_pass_id':"https://bimabachat.in/web/image/slide.slide/"

                    }),
                )



