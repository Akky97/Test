from odoo import models, fields, api

class policy1(models.Model):
    _name = 'policy'

    name = fields.Many2one('policyseg',string="Policy Segment" )
    pname = fields.Many2one('pname')
    isre = fields.Selection([('yes','Yes'),('no','No')], string="Is Renewable")
    isde = fields.Selection([('yes','Yes'),('no','No')], string="Is Declaration Policy" , default="no")
    declare = fields.Selection([('upfront','Upfront Commission'),('asper','As Per Certificate')], string="Declaration Type")


