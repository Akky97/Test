# -*- coding: utf-8 -*-
from .main import *
import xmlrpclib
# from flask import Flask, request, render_template
import calendar;
import time;
import base64, os
import requests
import json
from odoo.modules.registry import Registry
import odoo
import logging
import calendar
import time
from werkzeug.utils import secure_filename
ts=calendar.timegm(time.gmtime())


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

    @http.route('/api/contactgroup', method=['GET'], type='http', auth='none', csrf=False ,cors='*')
    @check_permissions
    def api_top_agent(self):
        print('SELF',self)
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
                cr.execute("select name, key from contactgroup_contactgroup")
                rows = cr.fetchall()
                company = []
                salesperson =[]
                country =[]
                for row in rows:
                    obj={
                        "name":row[0],
                        "key":row[1],
                    }
                    company.append(obj)  # making array to append
                    # salesperson.append(obj1)  # making array to append
                    # country.append(obj2)  # making array to append
            #             temp.append(obj)  # making array to append
            #             print(row)
        #         print('Total Row(s):', rows)'DATA': url,
        #

        return werkzeug.wrappers.Response(

            status=OUT__report__call_method__SUCCESS_CODE,
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'),
                     ('Pragma', 'no-cache')],
            response=json.dumps({
                # 'DATA': url,

                # 'To FROM': rows,
                'company':company,
                'response':200

            }),
        )






