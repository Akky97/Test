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

    @http.route('/api/ticketdashboard', method=['POST'], type='http', auth='none', csrf=False ,cors='*')
    def api_top_count(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        # user_id = jdata.get('user_id')
        # type = jdata.get('type')
        # create_uid = jdata.get('user_id')
        # if not create_uid:
        #     error_descrip = "No create_uid was provided in request!"
        #     error = 'no_create_uid'
        #     _logger.error(error_descrip)
        #     return error_response(400, error, error_descrip)
        # if not user_id:
        #     error_descrip = "No user_id was provided in request!"
        #     error = 'no_user_id'
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
                # cr.execute("select count(t1.user_id),t1.user_id,t3.name from project_issue as t1 left join res_users as t2 on t2.id = t1.user_id left join res_partner as t3 on t2.partner_id = t3.id group by t1.user_id,t3.name ")
                # cr.execute("select count(t1.created_by),t1.created_by,t3.name from project_issue as t1 left join res_users as t2 on t2.id = t1.created_by left join res_partner as t3 on t2.partner_id = t3.id where case when 'admin' = '" + str(type) + "' or 'master agent' = '" + str(type) + "' then 1=1 when 'agent manager'='" + str(type) + "'  then t1.created_by ='" + str(user_id) + "' else  t1.created_by = '" + str(user_id) + "' end group by t1.created_by,t3.name ")
                cr.execute("select count(t1.user_id),t1.user_id,t3.name from project_issue as t1 left join res_users as t2 on t2.id=t1.user_id left join res_partner as t3 on t2.partner_id = t3.id group by t1.user_id,t3.name order by count(t1.user_id) desc")
                r = (cr.dictfetchall())
                auth = json.dumps(r)
                all = json.loads(auth)
                print(all)
                temp = []
                for row in all:

                    temp.append(row)
                # print ('RESULT', result)
                return werkzeug.wrappers.Response(
                    status=OUT__report__call_method__SUCCESS_CODE,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        'ticketdashboard': temp,

                        # 'To FROM': rows

                    }),
                )


