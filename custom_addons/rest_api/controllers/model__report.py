# -*- coding: utf-8 -*-
from .main import *
import xmlrpclib
import calendar;
import time;
import base64, os
from odoo.modules.registry import Registry
from odoo import http

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

    # Call method (with parameters):
    @http.route('/api/report/<vin_no>', methods=['GET'], type='http', auth='none', csrf=False, cors='*')
    def api__report__method_PUT(self, vin_no):
        print "inside report"
        url = 'http://grg.mykumpany.com'
        db = 'grg1'
        password = '123456'
        username = 'grg@grg.com'
        print(vin_no)
        vin = int(vin_no)
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        print ('PRINT', uid)
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        invoice_ids = models.execute_kw(
            db, uid, password, 'sales.sales', 'search',
            [[('vin_no', '=', vin)]])
        report = xmlrpclib.ServerProxy('{}/xmlrpc/2/report'.format(url))
        result = report.render_report(
            db, uid, password, 'sales.report_sales', invoice_ids)
        print (result, 'result')
        ts = calendar.timegm(time.gmtime())
        print http.request.env['ir.config_parameter'].get_param('web.base.url')  # BASE URL
        print http.request.httprequest
        print http.request.httprequest.full_path
        print(ts)
        with open(os.path.expanduser('/opt/odoo/odoo-10.0/addons/web/static/grgreports/' + str(ts) + '.pdf'), 'wb') as fout:
            fout.write(base64.decodestring(result['result']))
            print('PDF SUCCESSFULLY SAVED', str(ts) + '.pdf')
            return werkzeug.wrappers.Response(
                status=OUT__report__call_method__SUCCESS_CODE,
                content_type='application/json; charset=utf-8',
                # headers=[('Cache-Control', 'no-store'),
                         # ('Pragma', 'no-cache')],
                response=json.dumps({
                    'status': result['state'],
                    'report_format': result['format'],
                    'uid': uid,
                    'filename': 'File Successfully Saved With File Name ' + str(ts) + '.pdf',
                    'Downloadable_link': 'http://grg.mykumpany.com/web/static/grgreports/'+ str(ts) + '.pdf',
                }),
            )









