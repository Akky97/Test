from odoo import models, fields, api

class tpa(models.Model):
    _name = 'tpamaster'

    name = fields.Char(string="Type")
    name1 = fields.Char(string="Name")
    address = fields.Text(string="Address")
    emailid = fields.Char(string="Email ID")
    website = fields.Char(string="Website")
    city = fields.Char(string="City")
    state = fields.Char(string="State")
    country = fields.Char(string="Country")
    faxno = fields.Char(string="Fax No.")
    no1 = fields.Char(string="No 1")
    no2 = fields.Char(string="No 2")
    text1 = fields.Char(string="Text 1")
    text2 = fields.Char(string="Text 2")
    name2 = fields.Char(string="Name")
    mobile = fields.Char(string="Mobile")
    email = fields.Char(string="Email")
    remark = fields.Char(string="Remarks")
    name3 = fields.Char(string="Name")
    mobile1 = fields.Char(string="Mobile")
    email1 = fields.Char(string="Email")
    remark1 = fields.Char(string="Remarks")
