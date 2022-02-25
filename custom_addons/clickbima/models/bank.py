from odoo import models, fields, api

class bank1(models.Model):
    _name = 'bank'

    name = fields.Char()