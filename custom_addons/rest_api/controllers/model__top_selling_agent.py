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

    @http.route('/api/topsellingagent', method=['GET'], type='http', auth='none', csrf=False ,cors='*')
    @check_permissions
    def api_top_agent(self):
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
                # cr.execute("select partner_id,res_partner.name from  sale_order left join res_partner on sale_order.partner_id = res_partner.id")
                # cr.execute("select count(sale_order.id),sale_order.partner_id from  sale_order left join res_partner on sale_order.partner_id = res_partner.id GROUP BY sale_order.partner_id ORDER BY count(sale_order.id) DESC")
                # cr.execute("select count(sale_order.id),sale_order.partner_id ,res_partner.name from  sale_order left join res_partner on sale_order.partner_id = res_partner.id GROUP BY sale_order.partner_id,res_partner.name ORDER BY count(sale_order.id) DESC")
                cr.excute("select count(sale_order.id),sale_order.x_agent_1 ,res_partner.name from  sale_order left join res_partner on sale_order.x_agent_1 = res_partner.id GROUP BY sale_order.x_agent_1,res_partner.name ORDER BY count(sale_order.id) DESC;")
                _logger.info("RUNNING")
                temp = []
                rows = cr.fetchall()
                print('Total Row(s):', rows)
                for row in rows:
                    obj = {"count": row[0], "id": row[1],"agent name":row[2] }
                    temp.append(obj)  # making array to append
                    temp.append(obj)  # making array to append
                    print(row)



                # l = len(temp) #calculate the lenght
                # count = 0
                # res = temp[0]
                # for i in range(l):
                #     print ("i", i)
                #
                #     cur_count = 1
                #     for j in range(i + 1, l):
                #         print("j", j)
                #
                #         if (temp[i] != temp[j]):
                #             break
                #         cur_count += 1
                #         if cur_count > count:
                #             count = cur_count
                #             res = temp[i]
                    # return '{"response": "OK"}'
            return werkzeug.wrappers.Response(

                status=OUT__report__call_method__SUCCESS_CODE,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    'DATA': temp,

                    # 'To FROM': rows,
                    'MESSAGE': 'RESPONSE OK',

                }),
            )






