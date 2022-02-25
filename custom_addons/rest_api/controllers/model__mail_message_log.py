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

    @http.route('/api/mail_message_get', method=['POST'], type='http', auth='none', csrf=False ,cors='*')
    @check_permissions
    def api_top_count(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        date = jdata.get('date')
        offset = jdata.get('offset')
        channel_id = jdata.get('channel_id')
        
        print (channel_id)


        # if not user_id:
        #     error_descrip = "No create_uid was provided in request!"
        #     error = 'no_user_id'
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
                # aman =cr.execute("select * from mail_message where model='mail.channel' and res_id = " + str(channel_id)+ " ORDER BY create_date Desc limit " + str(limit)+ " ")
                if date == None:
                    aman =cr.execute("select * from mail_message where model='mail.channel' and res_id = " + str(channel_id)+ "  ORDER BY create_date Desc limit 10  offset " + str(offset)+ "")
                    r = (cr.dictfetchall())
                    temp = []
                    auth = json.dumps(r)
                    all = json.loads(auth)
                    for id in all:
                        if id['id'] == None:
                            error = {
                                "message": "No Message Found",
                                "status_code": 0
                            }
                            return error
                        else:
                            cr.execute(
                                "select * from mail_tracking_value where mail_message_id ='" + str(id['id']) + "'")
                            r1 = (cr.dictfetchall())
                            mail_tracking_value = []
                            for row in r1:
                                mail_tracking_value.append(row)
                            obj = {"mail_message": id, "mail_tracking_value": mail_tracking_value}
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
                else:
                    aman = cr.execute("select * from mail_message where model='mail.channel' and (res_id = " + str(channel_id) + " and create_date > '" + str(date) + "') ORDER BY create_date Desc limit 10 ")
                    r = (cr.dictfetchall())
                    temp = []
                    auth = json.dumps(r)
                    all = json.loads(auth)
                    for id in all:
                        if id['id'] == None:
                            error = {
                                "message": "No Message Found",
                                "status_code": 0
                            }
                            return error
                        else:
                            cr.execute(
                                "select * from mail_tracking_value where mail_message_id ='" + str(id['id']) + "'")
                            r1 = (cr.dictfetchall())
                            mail_tracking_value = []
                            for row in r1:
                                mail_tracking_value.append(row)
                            obj = {"mail_message": id, "mail_tracking_value": mail_tracking_value}
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


