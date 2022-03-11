from odoo import http, _, exceptions
from odoo.http import request
from .serializers import Serializer
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

    @http.route('/api/v1/c/email.verification', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def get_email_verification(self, **params):
        try:
            if 'email' in params and 'send_otp' in params:
                result = request.env['email.verification'].sudo().create(params)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "result": 'Success'
        }
        return return_Response(res)
