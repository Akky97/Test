from odoo import models, fields, api

class dedetail(models.Model):
    _name = 'declarationdetails'

    name = fields.Char()