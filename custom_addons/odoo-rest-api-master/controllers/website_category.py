from odoo import http, _, exceptions
from odoo.http import request
import logging
from .exceptions import QueryFormatError
from .error_or_response_parser import *
_logger = logging.getLogger(__name__)

class WebsiteCategory(http.Controller):

    @http.route('/api/v1/c/product.public.category', type='http', auth='public', methods=['GET'], csrf=False, cors='*', website=True)
    def get_popular_category(self, **params):
        polularCategoryList = []
        try:
            model = 'product.public.category'
            records = request.env[model].sudo().search([('popular_category', '=', True)])
            if records:
                base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
                for rec in records:
                    value = {
                        'id': rec.id,
                        'name': rec.name,
                        'parent_id': rec.parent_id.id,
                        'sequence': rec.sequence,
                        'image': base_url.value + '/web/image/product.public.category/' + str(rec.id) + '/image_1920/' +rec.name
                    }
                    polularCategoryList.append(value)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(polularCategoryList),
            "result": polularCategoryList
        }
        return return_Response(res)

    @http.route('/api/v1/c/contact.us/<id>', type='http', auth='public', methods=['POST'], csrf=False, cors='*', website=True)
    def get_contact_us(self, id=None, **params):
        try:
            model = 'crm.lead'
            object = request.env[model].sudo()
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                if not jdata.get('name') or not jdata.get('email') or not jdata.get('phone') or not jdata.get('subject') or not jdata.get('message'):
                    error = {"message": "Something Went Wrong", "status": 400}
                    return return_Response_error(error)
                dict = {
                    'name': jdata.get('name'),
                    'email_from': jdata.get('email'),
                    'phone': jdata.get('phone'),
                    'mobile': jdata.get('phone'),
                    'description': jdata.get('subject')+' : '+jdata.get('message')
                }
                res = object.create(dict)
                if res:
                    template = request.env.ref('odoo-rest-api-master.send_otp_email_template',
                                               raise_if_not_found=False)
                    outgoing_server_name = request.env['ir.mail_server'].sudo().search([], limit=1).name
                    if outgoing_server_name:
                        email_check = request.env['res.users'].sudo().search([('id', '=', int(id))])
                        template.email_from = outgoing_server_name
                        template.email_to = email_check.email
                        template.subject = jdata.get('subject')
                        template.body_html = f"""<![CDATA[
                        <div class="container-fluid">
                            <div class="row" style="background: #5297f8; border-radius: 5px; margin: 0px; padding-left: 40px;"><a title="Pando Store" href="%20https://pandostores.com" target="_blank"><img src="https://stagingbackend.pandostores.com/odoo-rest-api-master/static/src/image/Pando_logo+1.png" width="278" height="59" /></a></div>
                            <div>
                            <p>Dear {email_check.name}</p>
                            <br />
                            <p>We have Received Your Request. And our concerned team will get back to you soon.</p>
                        </div>"""
                        template.sudo().send_mail(3, force_send=True)
            else:
                error = {"message": "Something Went Wrong", "status": 400}
                return return_Response_error(error)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "message": 'Record Created Successfully',
            "status": 200
        }
        return return_Response(res)
