from odoo import models, fields, api

class registryname(models.Model):
    _name = 'registryname'

    name = fields.Char()


    # @api.onchange('location')
    # def code_(self):

