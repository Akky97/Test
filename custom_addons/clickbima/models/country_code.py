from odoo import models, fields, api
from datetime import datetime



class country_code(models.Model):
    _name = 'country.code'


    name = fields.Char(string="Country Code")
    country_name = fields.Char(string="Country Name")
    