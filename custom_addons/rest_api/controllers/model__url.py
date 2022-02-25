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

    @http.route('/api/urlmatched', method=['POST'], auth='none', csrf=False ,cors='*')
    def api_top_count(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        url = jdata.get('url')
        # type = jdata.get('type')
        # user_id = jdata.get('user_id')
        # if not user_id:
        #     error_descrip = "No create_uid was provided in request!"
        #     error = 'no_user_id'
        #     _logger.error(error_descrip)
        #     return error_response(400, error, error_descrip)
        if not url:
            error_descrip = "No url was provided in request!"
            error = 'no url is Provided in the Request'
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
                cr.execute("select url,db,image,country_id,country_name from urlmatch_urlmatch where url = '"+str(url)+"' ")
                rows = cr.fetchone()
                print(rows)
                print(rows,"Rows")
                if rows == None:
                    error = {
                        'status_code': 400,
                        'data': "Unmatched Url or Bad Request"
                    }
                    return werkzeug.wrappers.Response(
                        status=OUT__report__call_method__SUCCESS_CODE,
                        content_type='application/json; charset=utf-8',
                        headers=[('Cache-Control', 'no-store'),
                                 ('Pragma', 'no-cache')],
                        response=json.dumps({
                            "error": error

                        }),
                    )

                else:
                    return werkzeug.wrappers.Response(
                    status=OUT__report__call_method__SUCCESS_CODE,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                        response=json.dumps({
                            "Url": url,
                            "db":rows[1],
                            "image":rows[2],
                            "country_id": rows[3],
                            "country_name": rows[4],
                            'status_code': 200,
                            'data': "Matched Successfully",

                        }),
                    )


