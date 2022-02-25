#-*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_terms_of_services = fields.Boolean(string='Show Term Of Service On Signup')
    show_terms_of_services_and_privacy = fields.Boolean(string='Show Term')



