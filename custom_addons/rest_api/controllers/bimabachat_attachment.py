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
    @http.route('/api/bimabachat/attachment', method=['POST'], type='http', auth='none', csrf=False ,cors='*')
    @check_permissions
    def api_attachment(self,**kw):
        try:
            file = kw['file']
            model= kw['model']
            if not file:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        "message": "File is Required",
                        "error": 400,
                        "status":False
                    }),)
            if not model:
                return werkzeug.wrappers.Response(
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        "message": "Model name is Required",
                        "error": 400,
                        "status": False
                    }), )


            if file:
                data = file.read()
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': file.filename,
                    'res_model':model,
                    'type': 'binary',
                    'datas_fname': file.filename,
                    'datas': data.encode('base64'),
                    # 'create_uid':request.session.uid
                })

        except Exception as e:
            return werkzeug.wrappers.Response(
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    'error':(e),
                    'status':400
                }),
            )
        return werkzeug.wrappers.Response(
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'),
                     ('Pragma', 'no-cache')],
            response=json.dumps({
                'attachment_id': attachment.id,
                'attachment_name':attachment.name,
                'message':True,
                'status':200
            }),
        )


