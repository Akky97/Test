from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class conins(models.Model):
    _name = 'coinsurance'

    name = fields.Many2one('res.partner', string="Insurer Name", required=True,
                                      domain=[('customer', '=', True), ('is_company', '=', True)])
    co_insurer_id = fields.One2many('co_insurer_unq', 'co_insurer_id')
    co_insurer_branch = fields.Many2one('insurerbranch', string="Insurer Branch", required=True)
    co_client = fields.Many2one('res.partner', string="Client Name", required=True,domain=[('x_client', '=', True)])

    @api.model
    def create(self, vals):
        data = super(conins, self).create(vals)
        co_insurer = vals.get('co_insurer_id')
        co_share_value = 0
        for c in co_insurer:
            co_shares = c[2]['co_share']
            co_share_value += co_shares
        if co_share_value == 100:
            return data
        elif co_share_value < 100:
            raise ValidationError(_('Share is less then the 100 percent'))
        elif co_share_value > 100:
            raise ValidationError(_('Share is not greater then 100 percent'))

    @api.multi
    @api.onchange('name')
    def insurerbranch_change(self):
        res = {}
        locations = self.env['insurer'].search([('name', '=', self.name.id)])
        temp = []
        for i in locations:
            temp.append(i.branch.id)
        res['domain'] = ({'co_insurer_branch': [('id', 'in', temp)]})
        return res



class Co_insurer(models.Model):
    _name='co_insurer_unq'

    co_insurer_id =fields.Integer()
    co_insurer_name = fields.Many2one('res.partner', string="Insurer Name", required=True,
                                     domain=[('customer', '=', True), ('is_company', '=', True)])
    co_insurer_branch = fields.Many2one('insurerbranch', string="Insurer Branch", required=True)
    co_type =fields.Selection([('self','Self'),('others','Others')],string="Type", default="self")
    co_broker =fields.Float(string="Broker")
    co_share =fields.Float(string="Share")
    co_commission =fields.Float(string="Commission")
    co_sum_insured =fields.Float(string="Sum Insured")
    co_brokerage_pre =fields.Float(string="Brokerage Permium")
    co_commission_amount =fields.Float(string="Commission Amount")
    co_rate = fields.Float(string="Reward Rate")
    co_reward_amount = fields.Float(string="Reward Rate Amount")
    co_remark = fields.Text(string="Remark")

    @api.multi
    @api.onchange('co_insurer_name')
    def change_co_insurer_name(self):
        res = {}
        locations = self.env['insurer'].search([('name', '=', self.co_insurer_name.id)])
        temp = []
        for i in locations:
            temp.append(i.branch.id)
        res['domain'] = ({'co_insurer_branch': [('id', 'in', temp)]})
        return res

    @api.model
    def create(self,vals):
        print (vals,"VALSSS")
        data =super(Co_insurer, self).create(vals)
        return data

