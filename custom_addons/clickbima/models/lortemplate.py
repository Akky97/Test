from odoo import models, fields, api

class lor(models.Model):
    _name = 'lortemp'

    name = fields.Char(string="Type",required=True)
    segment = fields.Char(string="Segment",required=True)
    product = fields.Char(string="Product",required=True)
    lorcase = fields.Char(string="LOR Case Type",required=True)