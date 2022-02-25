from odoo import models, fields

class insuran(models.Model):
    _name = 'detailinsurance1'

    nameco = fields.Selection([('no','No'),('yes','Yes')], default="no")
    commrate = fields.Float()

    insurername = fields.Char()
    insurerbranch = fields.Char()
    typeconins = fields.Char()
    cobroker = fields.Float()
    share = fields.Float()
    commrt = fields.Float()
    remark = fields.Text()