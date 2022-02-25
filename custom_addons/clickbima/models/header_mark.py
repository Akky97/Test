from odoo import models, fields, api

class headermark(models.Model):
    _name = 'headermark'
    _sql_constraints = [('name_uniq', 'unique(name)', 'Name must be unique!'),]

    name = fields.Char()
    remark = fields.Char()