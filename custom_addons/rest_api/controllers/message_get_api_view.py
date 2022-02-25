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

    @http.route('/api/message_channel_get', method=['POST'], type='http', auth='none', csrf=False ,cors='*')
    @check_permissions
    def api_top_count(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        channel_name = jdata.get('channel_name')
        channel_type =jdata.get('channel_type')
        partner_id=jdata.get('partner_id')
        type =jdata.get('type')
        if channel_name == '' or channel_name == None:
            channel_id = 0
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
                # aman =cr.execute("select body,t1.create_date,t1.res_id,t1.create_uid,t1.id,t3.id as imageId,t4.public,t4.channel_type from mail_message t1 join (select max(id) as id from mail_message group by create_uid) as t2 on t1.id = t2.id left join ir_attachment as t3 on t3.res_model = 'mail.channel' and t3.res_field = 'image' and t1.res_id = t3.res_id left join mail_channel as t4 on t1.res_id =t4.id where case when 'one' ='one' then t4.public ='" + str(channel_name) + "' or t4.channel_type='" + str(channel_type) + "' when 'all'='" + str(type) + "' then 1=1 end order by create_date desc")
                cr.execute("select t1.name,t1.public ,t2.body ,t3.id as imageid ,t1.create_date,t1.channel_type,t1.id as res_id ,t4.partner_id from mail_channel as t1 \
                            left join ( select body,t1.create_date,t1.res_id,t1.create_uid,t1.id from mail_message t1 \
                            join (select res_id,max(id) as id from mail_message group by res_id) as t2 on t1.id = t2.id \
                            order by create_date desc  \
                            ) as t2  on t2.res_id =t1.id \
                            left join ir_attachment as t3 on t3.res_model = 'mail.channel' and t3.res_field = 'image' and t1.id = t3.res_id \
                            left join mail_channel_partner as t4 on t4.channel_id =t1.id \
                            left join res_partner as t5 on t4.partner_id = t5.id \
                            where t1.public ='" + str(channel_name) + "' and t1.channel_type='" + str(channel_type) + "' and t4.partner_id ='" + str(partner_id) + "'")
                temp = []
                rows = cr.fetchall()
                print('Total Row(s):', rows)
                for row in rows:
                    obj = {"name":row[0],"public": row[1], "body": row[2], "imageid":"https://sowtex.mykumpany.com/web/image/"+str(row[3]),
                           "create_date": row[4], "channel_type": row[5],"res_id":row[6],"partner_id":row[7]}
                    temp.append(obj)
                # r = (cr.fetchall())
                # auth = json.dumps(r)
                # all = json.loads(auth)
                # for i in all:
                #     print(i['imageid'])
                return werkzeug.wrappers.Response(
                    status=OUT__report__call_method__SUCCESS_CODE,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        'mail_message': temp

                    }),
                )



