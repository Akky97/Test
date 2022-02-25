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

    @http.route('/api/productsale', method=['POST'], type='http', auth='none', csrf=False ,cors='*')
    def api_top_count(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        print ('JDATA', jdata)
        company_id = jdata.get('company_id')
        # month = jdata.get('month')
        # year = jdata.get('year')
        # lastmonth = jdata.get('lastmonth')
        # lastyear = jdata.get('lastyear')
        # user_type_id = jdata.get('user_type_id')

        if not company_id:
            error_descrip = "No company_id was provided in request!"
            error = 'no_company_id'
            _logger.error(error_descrip)
            return error_response(400, error, error_descrip)
        # if not month:
        #     error_descrip = "No month was provided in request!"
        #     error = 'month'
        #     _logger.error(error_descrip)
        #     return error_response(400, error, error_descrip)
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
        # if not lastyear:
        #     error_descrip = "No lastyear was provided in request!"
        #     error = 'no_lastyear'
        #     _logger.error(error_descrip)
        #     return error_response(400, error, error_descrip)
        # if not user_type_id:
        #     error_descrip = "No user_type_id was provided in request!"
        #     error = 'no_user_type_id'
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
                cr.execute("SELECT  t1.create_date,t1.name,list_price,t1.company_id,pricelist_id,fixed_price,min_quantity,t3.description,t3.name as customertax, EXTRACT(MONTH FROM t1.create_date) FROM product_template as t1 LEFT join product_pricelist_item as t2 on t1.id = t2.id LEFT join account_tax as t3 on t1.id = t3.id WHERE t1.company_id = 1 AND ( EXTRACT(MONTH FROM t1.create_date) = 8 or EXTRACT(MONTH FROM t1.create_date) = 7)  ")
                temp = []
                rows = cr.fetchall()
                print('Total Row(s):', rows)
                for row in rows:
                    obj = {"create_id":row[0],"name":row[1],"list_price":row[2],"company_id":row[3],"pricelist_id":row[4],"fixed_price":row[5],"min_quantity":row[6],"description":row[7],"customertax":row[8],"month":row[9]}
                    temp.append(obj)
                return werkzeug.wrappers.Response(
                    status=OUT__report__call_method__SUCCESS_CODE,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        'productsale': temp,

                        # 'To FROM': rows

                    }),
                )


