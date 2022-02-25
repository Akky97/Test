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

    @http.route('/api/lastmonth', method=['POST'], type='http', auth='none', csrf=False ,cors='*')
    def api_top_count(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        print ('JDATA', jdata)
        company_id = jdata.get('company_id')
        month = jdata.get('month')
        # year = jdata.get('year')
        # lastmonth = jdata.get('lastmonth')
        # lastmonth = jdata.get('lastmonth')


        if not company_id:
            error_descrip = "No company_id was provided in request!"
            error = 'no_company_id'
            _logger.error(error_descrip)
            return error_response(400, error, error_descrip)
        if not month:
            error_descrip = "No month was provided in request!"
            error = 'month'
            _logger.error(error_descrip)
            return error_response(400, error, error_descrip)
        # if not year:
        #     error_descrip = "No year was provided in request!"
        #     error = 'year'
        #     _logger.error(error_descrip)
        #     return error_response(400, error, error_descrip)
        # if not lastmonth:
        #     error_descrip = "No lastmonth was provided in request!"
        #     error = 'no_lastmonth'
        #     _logger.error(error_descrip)
        #     return error_response(400, error, error_descrip)
        # if not lastmonth:
        #     error_descrip = "No lastmonth was provided in request!"
        #     error = 'no_lastmonth'
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
                cr.execute("SELECT TO_CHAR(t1.create_date,'DD-MON') as day, t1.user_type_id,SUM(t1.debit) as debit,SUM(t1.credit) as credit FROM account_move_line AS t1 LEFT JOIN account_account AS t2 ON t1.account_id = t2.id WHERE t1.company_id = '" + str(company_id) + "' AND EXTRACT(MONTH FROM t1.create_date) = '" + str(month) + "' AND (t1.user_type_id = 16 OR t1.user_type_id = 14) GROUP BY TO_CHAR(t1.create_date,'DD-MON'),t1.user_type_id ORDER BY TO_CHAR(t1.create_date,'DD-MON')")
                temp = []
                rows = cr.fetchall()
                print('Total Row(s):', rows)
                for row in rows:
                    obj = {"month":row[0],"user_type_id":row[1],"debit":row[2],"credit":row[3]}
                    temp.append(obj)
                return werkzeug.wrappers.Response(
                    status=OUT__report__call_method__SUCCESS_CODE,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        'lastmonth': temp,

                        # 'To FROM': rows

                    }),
                )


