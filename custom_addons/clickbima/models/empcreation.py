from odoo import models, fields, api

class empcreation1(models.Model):
    _name = 'empcreation'


    name = fields.Char(string="RoleType")
    sm = fields.Boolean('SM')
    rm = fields.Boolean('RM', compute="_compute_rm")
    tl = fields.Boolean('TL')
    tc = fields.Boolean('TC', compute="_compute_tc")
    reference = fields.Boolean('Reference')
    csc = fields.Boolean('CSC')
    branch = fields.Char(string="Branch")
    title = fields.Selection(
        [('mr', 'Mr'), ('mrs', 'Mrs'), ('dr', 'Dr'), ('brig', 'Brig'), ('ms', 'Ms'), ('m/s', 'M/s'), ('col', 'Col.'),
         ('capt', 'Capt.')], string="Title")
    empname = fields.Char(string="Employee Name(D)")
    department = fields.Char(string="Department")
    designation = fields.Char(string="Designation")
    dateofjoin = fields.Date(string="Date of Joining")
    dateofbday = fields.Date(string="Date of Birthday")
    anniversarydate = fields.Date(string="Anniversary Date")
    accounttype = fields.Char(string="Account    Type")
    acno = fields.Char(string="A/c No")
    bank = fields.Char(string="Bank")
    bankbranch = fields.Char(string="Bank Branch")
    bankaddress = fields.Char(string="Bank Address")
    ifsccode = fields.Char(string="IFSC Code")
    micr = fields.Char(string="MICR")
    empp = fields.Char(string="Employee Name(P)")

    @api.depends('sm')
    def _compute_rm(self):
        if self.sm is True:
            self.rm = True

    @api.depends('tl')
    def _compute_tc(self):
        if self.tl is True:
            self.tc = True



