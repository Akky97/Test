from odoo import models, fields, api

class policys(models.Model):
    _name = 'policystatus'

    name = fields.Char(string="Broker Name",required=True)
    insuername = fields.Char(string="Insurer Name",required=True)
    policydept = fields.Char(string="Policy Dept",required=True)
    regdate = fields.Date(string="Reg. Date - From",required=True)
    location = fields.Char(string="Location",required=True)
    insurer = fields.Char(string="Insurer Branch",required=True)
    policystatus = fields.Selection([('all','All'),('pending','Pending'),('rece','Received'),('inprogres','In Progress')],string="Policy Status",required=True)
    insurerbranch = fields.Date(string="Date To",required=True)