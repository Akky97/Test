from odoo import models, fields, api

class upload(models.Model):
    _name = 'uploaddata'

    name = fields.Char(string="No.")