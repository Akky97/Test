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

    @http.route('/api/bimabachat/stagecount', method=['POST'], type='http', auth='none', csrf=False ,cors='*')
    @check_permissions
    def api_top_count(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        sale_team_id = jdata.get('sale_team_id')
        user_id =jdata.get('user_id')
        type = jdata.get('type')
        if sale_team_id ==None or sale_team_id == False or sale_team_id =="":
            id =0
            sale_team_id =id
        if user_id == None or user_id == False or user_id == "":
            id = 0
            user_id = id

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
                cr.execute("select count(t2.name),t1.name as stagename \
                            from crm_stage as t1  left join crm_lead as t2 on t1.id = t2.stage_id \
                            where case when 'admin'='"+str(type)+"' then 1=1 \
                            when 'employee' ='"+str(type)+"'then t2.user_id='"+str(user_id)+"' \
                            when 'saleshead'='"+str(type)+"' then t2.team_id ='"+str(sale_team_id)+"'\
                            end \
                            group by t1.sequence,t1.name having count(t2.name) >0 order by t1.sequence asc")

                r = (cr.dictfetchall())

                return werkzeug.wrappers.Response(
                    status=OUT__report__call_method__SUCCESS_CODE,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        'slide_count': r,
                    }),
                )


