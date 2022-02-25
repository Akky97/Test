from odoo import models, fields, api

class company1(models.Model):
    _name = 'scheme'

    name = fields.Char()
    branch = fields.Many2one('res.partner',string="Insurer Name")
    type = fields.Selection([('nonlifeinsurance','Non Life Insurance'),('lifeinsurance','Life Insurance')], placeholder="Select Insurer Type")

    subcategory = fields.Many2many('subcategory.subcategory')
