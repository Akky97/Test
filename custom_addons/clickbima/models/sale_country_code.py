from odoo import models, fields, api
from datetime import datetime



class salecountry_code(models.Model):
    _inherit = 'crm.lead'


    name = fields.Many2one('country.code', related='name.code',string="Country Code" )

