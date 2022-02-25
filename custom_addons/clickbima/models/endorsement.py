from odoo import models, fields, api

class endor(models.Model):
    _name = 'endorsement'

    name = fields.Many2one('res.partner', string="Insurer Name", required=True,
                           domain=[('customer', '=', True), ('is_company', '=', True)])
    endo_insurer_id = fields.One2many('endos_policy_unq', 'endo_id')
    endo_insurer_branch = fields.Many2one('insurerbranch', string="Insurer Branch", required=True)
    endo_client = fields.Many2one('res.partner', string="Client Name", required=True, domain=[('x_client', '=', True)])

class Endosorment(models.Model):
    _name = 'endos_policy_unq'

    endo_id = fields.Integer()
    name = fields.Char(string="Endosement Generated", default="NEW")
    endos_manual = fields.Char(string="Endosement Manual Generated")
    endos_type = fields.Many2one('subdata.subdata')
    endos_reason = fields.Many2one('subdata.subdata')
    endos_suminsured = fields.Float(string="Endosement Suminsured")
    endos_brokerage_premium = fields.Float(string="Endosement Brokerage Premium")
    endo_tp = fields.Float(string="Tp")
    endo_terr = fields.Float(string="Terr Permium")
    endo_stamp = fields.Float(string="Stamp")
    endo_net = fields.Float(string="Net Premium", compute="_onchange_endo_net")
    endo_gst = fields.Many2one('gsttax', string="Service Tax Rate", required=True)
    endo_gst_amount = fields.Float(string="Gst Amount")
    endo_gst_gross = fields.Float(string="Gst Gross")
    endo_difference = fields.Float(string="Difference")
    endos_date = fields.Date(string='Effective Date')
    endo_payment = fields.Float()
    endo_round_off = fields.Float()
    line_no = fields.Integer(compute='_compute_lines')

    def _compute_lines(self):
        print("NA NJKANAKJ")
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])
            for line_rec in first_line_rec.endo_id.endorsement_id:
                print(line_rec, "RECC")
                line_rec.line_no = line_num
                line_num += 1

    @api.multi
    @api.onchange('endos_type', 'endos_suminsured', 'endos_brokerage_premium', 'endo_tp', 'endo_terr', 'endo_stamp',
                  'endo_net',
                  'endo_gst', 'endo_gst_amount', 'endo_gst_gross', 'endo_difference')
    def _onchange_endo_net(self):
        for i in self:
            netprem = i.endos_brokerage_premium + i.endo_tp + i.endo_terr + i.endo_stamp
            i.endo_net = netprem
            i.endo_gst_amount = float(i.endo_net) * float(i.endo_gst.tax / 100)
            i.endo_gst_amount = i.endo_gst_amount + i.endo_net
            i.endo_gst_gross = i.endo_gst_amount

    @api.model
    def create(self, vals):
        # if vals.get('name', 'NEW') == 'NEW':
        #     vals['name'] = self.env['ir.sequence'].next_by_code('endos_policy') or '/'
        data = super(Endosorment, self).create(vals)
        return data

    @api.multi
    @api.onchange('name')
    def _compute_endos_type(self):
        res = {}
        locations = self.env['infodata'].search([('name', '=', 71)])
        temp = []

        for i in locations:
            temp.append(i.infosubdata.name)
        res['domain'] = ({'endos_type': [('name', 'in', temp)]})
        return res

    @api.multi
    @api.onchange('name')
    def _compute_endos_reason(self):
        res = {}
        locations = self.env['infodata'].search([('name', '=', 89)])
        temp = []
        for i in locations:
            temp.append(i.infosubdata.name)
        res['domain'] = ({'endos_reason': [('name', 'in', temp)]})
        return res

    @api.multi
    @api.onchange('endos_date')
    def endos_date_change(self):
        if self.endos_date:
            trans = self.endo_id
            print(trans.startfrom, "Start")
            if trans.startfrom <= self.endos_date and trans.expiry >= self.endos_date:
                pass
            else:
                raise ValidationError('Please choose the effective date between Start date/Expiry Date')

    # name = fields.Char(string="Docket No.")
    # clientname = fields.Many2one(string="Client Name")
    # group = fields.Char(string="Group Name")
    # segment = fields.Many2one(string="Segment")
    # policyno = fields.Char(string="Policy No.")
    # startfrom = fields.Date(string="Start From")
    # suminsured = fields.Char(string="Sum Insured")
    # date2 = fields.Date(string="Date")
    # insurername = fields.Many2one(string="Insurer Name")
    # insurerbranch = fields.Many2one(string="Insurer Branch")
    # policydetail = fields.Char(string="Type/Product")
    # issuedate = fields.Date(string="Issue Date")
    # expiry = fields.Date(string="Expiry")
    # sharein = fields.Float(string="Share in(%)")
    # fy = fields.Many2one(string="F.Y")
    # regsitersrno = fields.Char(string="Register Sr. No.")
    # endstype = fields.Char(string="Ends. Type.")
    # endsid = fields.Char(string="Ends-Id")
    # endstart = fields.Date(string="Start From")
    # endinsured = fields.Char(string="Sum Insured")
    # registername = fields.Many2one('registryentry', string="Register Name")
    # registerdate = fields.Date(string="Register Date")
    # endsdate = fields.Date(string="Ends.Date")
    # endsno = fields.Char(string="Ends No.")
    # endexp = fields.Date(string="Expiry")
    # sharein1 = fields.Char(string="Share in(%)")
    # brokerageprem = fields.Float(string="Brokerage Prem.")
    # tppremium = fields.Float(string="TP Premium")
    # terrprem = fields.Float(string="Terr Premium")
    # stamprem = fields.Float(string="Stamp Duty")
    # netprem = fields.Float(string="Net Premium")
    # servicetax = fields.Float(string="Service Tax Rate")
    # servicetaxamt = fields.Float(string="Service Tax Amt.", readonly=True)
    # grossprem = fields.Float(string="Gross Premium", readonly=True)
    # difference = fields.Float(string="Difference", readonly=True)
    # paymenttotal = fields.Float(string="Payment Total",readonly=True, store=True)
    # transaction = fields.One2many('ptransaction', 'mode')
    # remark1 = fields.Text(string="Remark 1")
    # remark2 = fields.Text(string="Remark 2")







# class payment(models.Model):
#     _name = 'ptransaction'
#
#     # name = fields.Integer()
#     mode = fields.Selection(
#         [('cash', 'Cash'), ('cd', 'CD A/C'), ('cheque', 'Cheque'), ('dd', 'DD'), ('etrans', 'e-Transfer'),
#          ('not', 'Not Applicable')],string="Mode")
#     chdd = fields.Char(string="Ch/DD No")
#     amountpy = fields.Float(string="Amount")
#     bankpy = fields.Many2one(string="Bank")
#     bankbranch = fields.Char(string="Bank Branch")
#     datepy = fields.Date(string="Dated")
