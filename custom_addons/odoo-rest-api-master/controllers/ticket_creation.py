import logging
import boto3
from botocore.exceptions import ClientError
import os
import json
import math
import logging
import requests
import ast
import base64
from odoo import http, _, exceptions, fields
from datetime import timedelta, time
from odoo.tools.float_utils import float_round
from odoo.http import request
from .serializers import Serializer
from .exceptions import QueryFormatError
from .error_or_response_parser import *
from werkzeug.utils import secure_filename
from datetime import date

_logger = logging.getLogger(__name__)
import calendar;
import time;

ts = calendar.timegm(time.gmtime())


class ControllerREST(http.Controller):

    @http.route('/api/v1/c/createticket', methods=['POST'], type='http', auth="public", csrf=False, cors='*')
    @validate_token
    def ticketcreate_method(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        uid = request.env.user.id
        partner_id = request.env.user.partner_id.id
        issue_name = jdata.get('issue_name')
        description = jdata.get('description')
        sale_line_id = jdata.get('sale_line_id')

        if not jdata.get('description') or not jdata.get('issue_name') or not jdata.get('sale_line_id'):
            msg = {"message": "Something Went Wrong", "status_code": 400}
            return return_Response_error(msg)
        stage_id = request.env['project.task.type'].sudo().search([('name', '=', 'New')], limit=1).id
        project_id = request.env['project.project'].sudo().search([('name', '=', 'Pando-Stores Issues')], limit=1).id
        tag_id = request.env['project.tags'].sudo().search([('name', '=', 'Issue')], limit=1).id
        tag = [tag_id]
        from datetime import datetime, timedelta
        deadline_date = datetime.now() + timedelta(1)
        # if tag_ids != None:
        #     for x in tag_ids:
        #         tag.append(x['id'])
        assert isinstance(uid, object)
        vals = dict(name=issue_name, tag_ids=[[6, False, tag]], partner_id=int(partner_id), description=description,
                    stage_id=stage_id, user_id=uid, project_id=project_id, sale_line_id_pando=int(sale_line_id),
                    date_deadline=deadline_date)
        try:
            ticket_id = request.env['project.task'].sudo().create(vals)
            if ticket_id:
                res = {
                    'message': "Ticket created Successfully",
                    'status': 200
                }
                return return_Response(res)
            else:
                res = {
                    'message': "Something Went Wrong",
                    'status': 200
                }
                return return_Response(res)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)

    @http.route('/api/v1/c/getticket', methods=['GET'], type='http', auth="public",cors='*')
    @validate_token
    def getticket(self):
        try:
            temp = []
            uid = request.env.user.id
            partner_id = request.env.user.partner_id
            tasks = http.request.env['project.task'].sudo().search([('partner_id', '=', int(partner_id.id))])
            for i in tasks:
                tags = []
                for z in i.tag_ids:
                    tags.append({"id": z.id, "name": z.name})
                vals = {"id": i.id,
                        "name": i.name if i.name != False else '',
                        "user_id": i.user_id.id if i.user_id.id != False else '',
                        "user_name": i.user_id.name if i.user_id.name != False else '',
                        "stage_id": i.stage_id.id if i.stage_id.id != False else '',
                        "stage_name": i.stage_id.name if i.stage_id.name != False else '',
                        "tag_ids": tags,
                        "partner_id": i.partner_id.id if i.partner_id.id != False else '',
                        "partner_name": i.partner_id.name if i.partner_id.name != False else '',
                        "create_date": str(i.create_date),
                        "ticket_number": i.ticket_number
                        }
                temp.append(vals)
            res = {
                'data':temp,
                'message': "Get Successfully ",
                'status': 200
            }
            return return_Response(res)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
