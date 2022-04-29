from odoo import http, _, exceptions
from odoo.http import request
import logging
from .exceptions import QueryFormatError
from .error_or_response_parser import *
_logger = logging.getLogger(__name__)


class PandoBanner(http.Controller):

    @http.route('/api/v1/c/pando.banner/', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_pando_banner(self, **params):
        try:
            model = 'pando.banner'
            records = request.env[model].sudo().search([])
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            bannerList = []
            for rec in records:
                value = {
                    'id': rec.id,
                    'name': rec.name,
                    'drop_down': rec.drop_down,
                    'image': base_url.value + '/web/image/pando.banner/' + str(rec.id) + '/image/' +rec.name
                }
                bannerList.append(value)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            "count": len(bannerList),
            "result": bannerList
        }
        return return_Response(res)

