from odoo import models, fields, api

class poscreation1(models.Model):
    _name = 'poscreation'

    name = fields.Char(string="Role Type")
    category = fields.Char(string="Category")
    branch = fields.Char(string="Branch")
    title = fields.Selection([('mr','Mr'),('mrs','Mrs'),('dr','Dr'),('brig','Brig'),('ms','Ms'),('m/s','M/s'),('col','Col.'),('capt','Capt.')], string="Title")
    posname = fields.Char(string="POS Name(D)")
    beneficiary = fields.Char(string="Beneficiary")
    principle = fields.Selection([('yes','Yes'),('no','No')], string="Is Princial")
    rmname = fields.Char(string="RM Name")
    reference = fields.Char(string="Reference")
    telecaller = fields.Char(string="Telecaller")
    csc = fields.Char(string="CSC")
    accounttype = fields.Char(string="Account Type")
    acno = fields.Char(string="A/c No")
    bank = fields.Char(string="Bank")
    bankbranch = fields.Char(string="Bank Branch")
    bankaddress = fields.Char(string="Bank Address")
    ifsccode = fields.Char(string="IFSC Code")
    micr = fields.Char(string="MICR")
    dateofbday = fields.Date(string="Date of Birthday")
    anniversarydate = fields.Date(string="Anniversary Date")
    dateofjoin = fields.Date(string="Date of Joining")
    posnamep = fields.Char(string="POS Name(P)")