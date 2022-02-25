# -*- coding: utf-8 -*-
from .main import *
import xmlrpclib
import calendar;
import time;
import base64, os
import json
from odoo.modules.registry import Registry
import odoo
import xmlrpc.client
# import xmlrpc
import logging
import datetime

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

    @http.route('/api/chatmessage', method=['POST'], csrf=False ,type='http', auth='none',cors='*')
    @check_permissions
    def postProcessing(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        print ('JDATA', jdata)
        model = jdata.get('model')
        res_id = jdata.get('res_id')
        body = jdata.get('body')
        channel_ids = jdata.get('channel_ids')
        author_id = jdata.get('author_id')
        # author_avatar = jdata.get('author_avatar')
        message_type = jdata.get('message_type')
        subtype_id = jdata.get('subtype_id')
        now = datetime.datetime.now()
        create_uid =jdata.get('create_uid')
        record_name =jdata.get('record_name')
        email_from =jdata.get('email_from')
        app_password =jdata.get('app_password')
        app_username=jdata.get('app_username')
        print (now)


        # db_name = odoo.tools.config.get('db_name')
        # if not db_name:
        #     _logger.error(
        #         "ERROR: To proper setup OAuth2 and Redis - it's necessary to set the parameter 'db_name' in Odoo config file!")
        #     print(
        #         "ERROR: To proper setup OAuth2 and Token Store - it's necessary to set the parameter 'db_name' in Odoo config file!")
        # else:
        #     # Read system parameters...
        #     registry = Registry(db_name)
        #     with registry.cursor() as cr:
        #      cr.execute("Insert into mail_message (model,res_id,body,author_id,message_type,subtype_id,create_date,create_uid,record_name,email_from,channel_ids) values('" + str(model) + "','" + str(res_id) + "','" + str(body) + "','" + str(author_id) + "','" + str(message_type) + "','" + str(subtype_id) + "','" + str(now) + "','" + str(create_uid) + "','" + str(record_name) + "','" + str(email_from) + "','" + str(channel_ids) + "')")
        #
        print(channel_ids,model,res_id,body,channel_ids,author_id,message_type,subtype_id,app_password,app_username)
        url = "https://sowtex.mykumpany.com"
        db = "database_sowtex"
        print(app_username,app_username,"-->>>>>>>>")
        username = app_username
        password = app_password
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        common.version()
        {
            "server_version": "8.0",
            "server_version_info": [8, 0, 0, "final", 0],
            "server_serie": "8.0",
            "protocol_version": 1,
        }
        uid = common.authenticate(db, username, password, {})
        print(uid)
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        id = models.execute_kw(db, uid, password, 'mail.message', 'create', [{
            'model': model,
            'res_id': res_id,  # from/reference channel
            'body': body,  # here add the message bodyapp_usapp_usernameapp_usernameername
            'channel_ids': [channel_ids],  # channel ID to post to
            'author_id': author_id,
            # 'author_avatar': author_avatar,
            'message_type': message_type,
            'subtype_id': subtype_id
        }])

        return werkzeug.wrappers.Response(
            status=OUT__report__call_method__SUCCESS_CODE,
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'),
                     ('Pragma', 'no-cache')],
            response=json.dumps({
                "response": 200,
                "message": "Message Successfully Sent",
                'id': id

            }),
        )





