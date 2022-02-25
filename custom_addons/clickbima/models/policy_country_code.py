from odoo import models, fields, api
from datetime import datetime



class policycountry_code(models.Model):
    _inherit = 'country.code'

    name = fields.Char(string="Country Name")
    code = fields.Char(string="Country Code")