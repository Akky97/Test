from odoo import models, fields, api

class pstatus(models.Model):
    _name = 'pstate1'

    dockno = fields.Char()
    serialno = fields.Char()
    policyno = fields.Char()
    disdate = fields.Date()
    disdetail = fields.Date()
    courierdet = fields.Char()
    statustype = fields.Char()
    recdtype = fields.Char()
    sendtype = fields.Char()