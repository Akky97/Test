from odoo import models, fields, api

class taxgst(models.Model):
    _name = 'gsttax'

    name = fields.Char()
    tax = fields.Float()