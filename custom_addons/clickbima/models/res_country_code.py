from odoo import models, fields, api
from datetime import datetime



class rescountry_code(models.Model):
    _inherit = 'res.partner'

    country_code_symbol = fields.Many2one('country.code',string="Country code")



