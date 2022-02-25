from odoo import models, fields, api

class clientgroupcreation1(models.Model):
    _name = 'clientgroupcreation'

    name = fields.Many2one('res.better.zip', string="Location")
    clienttype = fields.Selection([('pos','POS Client'),('direct','Direct Client')], string="Client Type")
    rm = fields.Char(string="RM")
    sm = fields.Char(string="SM")
    customertype = fields.Selection([('corporate','Corporate'),('retail','Retail'),('retailin','Retail In Corporate')],string="Customer Type")
    clientgroupname = fields.Char(string="Client Group Name")