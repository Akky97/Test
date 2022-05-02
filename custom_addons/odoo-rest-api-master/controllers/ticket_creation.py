import logging
from odoo import http, _, exceptions, fields
from odoo.http import request
from .exceptions import QueryFormatError
from .error_or_response_parser import *

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
        if not jdata.get('description') or not jdata.get('issue_name') or not jdata.get('priority') or not \
                jdata.get('assignTo') or not jdata.get('tag_id'):
            msg = {"message": "Something Went Wrong", "status_code": 400}
            return return_Response_error(msg)
        uid = request.env.user.id
        partner_id = request.env.user.partner_id.id
        issue_name = jdata.get('issue_name')
        description = jdata.get('description')
        product_id = False if not jdata.get('product_id') else jdata.get('product_id')
        priority = jdata.get('priority')
        assignTo = jdata.get('assignTo')
        tag_id = jdata.get('tag_id')
        stage_id = request.env['project.task.type'].sudo().search([('name', '=', 'New')], limit=1).id
        project_id = request.env['project.project'].sudo().search([('name', '=', 'Pando-Stores Issues')], limit=1).id
        tag = [tag_id]
        from datetime import datetime, timedelta
        deadline_date = datetime.now() + timedelta(1)
        assert isinstance(uid, object)
        vals = dict(name=issue_name, tag_ids=[[6, False, tag]], partner_id=int(partner_id),
                    description=description, stage_id=stage_id, user_id=int(assignTo), product_id=int(product_id),
                    project_id=project_id, date_deadline=deadline_date, priority=str(priority))
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
                        "deadline_date": str(i.date_deadline),
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

    @http.route('/api/v1/c/getticket/<id>', methods=['GET'], type='http', auth="public", cors='*')
    @validate_token
    def get_single_ticket(self, id=None):
        try:
            temp = []
            task = http.request.env['project.task'].sudo().search([('id', '=', int(id))])
            for i in task:
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
                        "deadline_date": str(i.date_deadline),
                        "description": i.description,
                        "product_id": i.product_id.id if i.product_id.id != False else '',
                        "product_name": i.product_id.name if i.product_id.name != False else '',
                        "ticket_number": i.ticket_number,
                        "sale_order_line_id": i.sale_line_id_pando.id if i.sale_line_id_pando.id != False else '',
                        "sale_order_line_name": i.sale_line_id_pando.name if i.sale_line_id_pando.name != False else ''
                        }
                temp.append(vals)
            res = {
                'data': temp,
                'message': "Get Successfully ",
                'status': 200
            }
            return return_Response(res)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)

    @http.route('/api/v1/c/getAssignedTo', methods=['GET'], type='http', auth="public", cors='*')
    def getAssignedTo(self):
        try:
            temp = []
            user = request.env['res.users'].sudo().search([('name', '=', 'Pando Admin')])
            for i in user:
                vals = {"user_id": i.id if i.id != False else '',
                        "user_name": i.name if i.name != False else ''
                        }
                temp.append(vals)
            res = {
                'data': temp,
                'message': "Assigned To Data",
                'status': 200
            }
            return return_Response(res)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)

    @http.route('/api/v1/c/getTicketType', methods=['GET'], type='http', auth="public", cors='*')
    def getTicketType(self):
        try:
            temp = []
            tags = request.env['project.tags'].sudo().search([('name', 'in',
                                                               ['Product Issue', 'Invoice Issue', 'Other'])])
            for i in tags:
                vals = {"tag_id": i.id if i.id != False else '',
                        "tag_name": i.name if i.name != False else ''
                        }
                temp.append(vals)
            res = {
                'data': temp,
                'message': "Ticket Type Data",
                'status': 200
            }
            return return_Response(res)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)

    @http.route('/api/v1/c/customer/createticket', methods=['POST'], type='http', auth="public", csrf=False, cors='*')
    @validate_token
    def ticketcreate_customer_method(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        if not jdata.get('description') or not jdata.get('issue_name') or not jdata.get('priority') or not \
                jdata.get('assignTo') or not jdata.get('tag_id') or not \
                jdata.get('sale_order_line_id'):
            msg = {"message": "Something Went Wrong", "status_code": 400}
            return return_Response_error(msg)
        uid = request.env.user.id
        partner_id = request.env.user.partner_id.id
        issue_name = jdata.get('issue_name')
        description = jdata.get('description')
        priority = jdata.get('priority')
        assignTo = jdata.get('assignTo')
        tag_id = jdata.get('tag_id')
        sale_line_id_pando = jdata.get('sale_order_line_id')
        stage_id = request.env['project.task.type'].sudo().search([('name', '=', 'New')], limit=1).id
        project_id = request.env['project.project'].sudo().search([('name', '=', 'Pando-Stores Issues')], limit=1).id
        tag = [tag_id]
        sale_order_line = request.env['sale.order.line'].sudo().search([('id', '=', int(sale_line_id_pando))])
        product_id = sale_order_line.product_id.id
        from datetime import datetime, timedelta
        deadline_date = datetime.now() + timedelta(1)
        assert isinstance(uid, object)

        vals = dict(name=issue_name, tag_ids=[[6, False, tag]], partner_id=int(partner_id),
                    description=description, stage_id=stage_id, user_id=int(assignTo), product_id=int(product_id),
                    project_id=project_id, date_deadline=deadline_date, priority=str(priority),
                    sale_line_id_pando=int(sale_line_id_pando))
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

    @http.route('/api/v1/c/customer/getSaleOrderLines/<id>', methods=['GET'], type='http', auth="public", cors='*')
    def getSaleOrderLines(self, id=None):
        try:
            temp = []
            sale_order_lines = request.env['sale.order.line'].sudo().search([('order_id', '=', int(id))])
            for i in sale_order_lines:
                vals = {"sale_order_line_id": i.id if i.id != False else '',
                        "sale_order_line_name": i.name if i.name != False else '',
                        "product_id": i.product_id.id if i.product_id.id != False else '',
                        "product_name": i.product_id.name if i.product_id.name != False else ''
                        }
                temp.append(vals)
            res = {
                'data': temp,
                'message': "Sale Order Line Data",
                'status': 200
            }
            return return_Response(res)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)

    # @http.route('/api/v1/c/customer/getProductId/<id>', methods=['GET'], type='http', auth="public", cors='*')
    # def getProductId(self, id=None):
    #     try:
    #         temp = []
    #         sale_order_line = request.env['sale.order.line'].sudo().search([('id', '=', int(id))])
    #         for i in sale_order_line:
    #             vals = {"product_id": i.product_id.id if i.product_id.id != False else '',
    #                     "product_name": i.product_id.name if i.product_id.name != False else ''
    #                     }
    #             temp.append(vals)
    #         res = {
    #             'data': temp,
    #             'message': "Product Data",
    #             'status': 200
    #         }
    #         return return_Response(res)
    #     except (SyntaxError, QueryFormatError) as e:
    #         return error_response(e, e.msg)
