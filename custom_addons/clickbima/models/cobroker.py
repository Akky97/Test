from odoo import models, fields, api

class cobroker1(models.Model):
    _name = 'cobroker'

    name = fields.Many2one('res.company',string="Company")
    brokername = fields.Char(string="Broker Name")
    shortname = fields.Char(string="Short Name")
    address = fields.Text(string="Address")
    city = fields.Many2one('res.better.zip', string="City")
    state = fields.Char(string="State")
    country = fields.Char(string="Country")
    pincode = fields.Integer(string="Pin Code")
    contactperson = fields.Char(string="Contact Person")
    contactno = fields.Integer(string="Contact No.")
    stno = fields.Char(string="ST No.")
    panno = fields.Char(string="PAN No.")
    tanno = fields.Char(string="TAN No.")
    licneseno = fields.Char(string="License No")
    licnesedate = fields.Date(string="License Date")

    @api.onchange('city')
    def _onchange_city(self):
        self.state = self.city.state_id.name
        self.country = self.city.country_id.name
