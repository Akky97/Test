from odoo import models, fields, api

class renew(models.Model):
    _name = 'renewalcall'

    name = fields.Char(string="No.")