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

    @http.route('/api/rescompany', method=['POST'], type='http', auth='none', csrf=False ,cors='*')
    def api_top_count(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        print ('JDATA', jdata)
        name = jdata.get('name')
        gstnumber = jdata.get('gstnumber')
        street = jdata.get('street')
        street2 = jdata.get('street2')
        city = jdata.get('city')
        website = jdata.get('website')
        phone = jdata.get('phone')
        fax = jdata.get('fax')
        email = jdata.get('email')
        x_acc = jdata.get('x_acc')
        x_bank = jdata.get('x_bank')
        x_ifsc = jdata.get('x_ifsc')
        x_pan = jdata.get('x_pan')

        if not name:
            error_descrip = "No Company Name was provided in request!"
            error = 'no_company_id'
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
                cr.execute("Insert into res_company (name,vat,street,street2,city,website,phone,fax,email,x_acc,x_bank,x_ifsc,x_pan) values('" + str(name) + "','" + str(gstnumber) + "','" + str(street) + "','" + str(street2) + "','" + str(city) + "','" + str(website) + "','" + str(phone) + "','" + str(fax) + "','" + str(email) + "','" + str(x_acc) + "','" + str(x_bank) + "','" + str(x_ifsc) + "','" + str(x_pan) + "')")

                return werkzeug.wrappers.Response(
                    status=OUT__report__call_method__SUCCESS_CODE,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        'Response': 200,
                    }),
                )


