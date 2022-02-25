# -*- coding: utf-8 -*-
from odoo import http

# class Clickbima(http.Controller):
#     @http.route('/clickbima/clickbima/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/clickbima/clickbima/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('clickbima.listing', {
#             'root': '/clickbima/clickbima',
#             'objects': http.request.env['clickbima.clickbima'].search([]),
#         })

#     @http.route('/clickbima/clickbima/objects/<model("clickbima.clickbima"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('clickbima.object', {
#             'object': obj
#         })