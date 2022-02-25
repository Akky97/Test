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

    @http.route('/api/claimweb', method=['POST'], type='http', auth='none', csrf=False ,cors='*')
    def api_top_count(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        print ('JDATA', jdata)
        infodata = jdata.get('infodata')


        if not infodata:
            error_descrip = "No infodata was provided in request!"
            error = 'no_infodata'
            _logger.error(error_descrip)
            return error_response(400, error, error_descrip)


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

                cr.execute("select t2.name as infotype,t3.name as infodata,t4.name as infosubdata,t1.claim,t1.details,t1.sequence from claim_process_claim_process as t1 left join infotype_infotype as t2 on t1.infotype = t2.id left join infosubdatadropdown as t3 on t1.infodata = t3.id left join subdata_subdata as t4 on t1.infosubtype = t4.id where t3.name = '" + str(infodata) + "' order by t1.sequence")
                temp = []
                rows = cr.fetchall()
                print('Total Row(s):', rows)
                for row in rows:
                    obj = {"infotype":row[0],"infodata":row[1],"infosubdata":row[2],"claim":row[3],"details":row[4],"sequence":row[5]}
                    temp.append(obj)
                return werkzeug.wrappers.Response(
                    status=OUT__report__call_method__SUCCESS_CODE,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        'claim_bimabachat': temp,

                        # 'To FROM': rows

                    }),
                )


