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

    @http.route('/api/revenue', method=['POST'], type='http', auth='none', csrf=False ,cors='*')
    @check_permissions
    def api_revenue_report_POST(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        print ('JDATA', jdata)
        to_date = jdata.get('to_date')
        from_date = jdata.get('from_date')
        if not to_date:
            error_descrip = "No to date was provided in request!"
            error = 'no_to_date'
            _logger.error(error_descrip)
            return error_response(400, error, error_descrip)
        if not from_date:
            error_descrip = "No from date was provided in request!"
            error = 'no_from_date'
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
                cr.execute("SELECT date_order,amount_total FROM Sale_order WHERE date_order BETWEEN '" + str(to_date) + "' AND '" + str(from_date) + "'")
                temp = []
                rows = cr.fetchall()
                print('Total Row(s):', rows)
                for row in rows:
                    obj = {"DATE":row[0],"AMOUNT FOR REVENUE":row[1]}
                    temp.append(obj)
                    print(temp)
                # print ('RESULT', result)
                return werkzeug.wrappers.Response(
                    status=OUT__report__call_method__SUCCESS_CODE,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        'DATE AND REVENUE': temp,

                        # 'To FROM': rows,
                        'MESSAGE': 'RESPONSE OK',

                    }),
                )


