
import logging
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError
from odoo.modules.registry import Registry
import requests
import json
import odoo
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class policytrans(models.Model):
    _name = 'policytransaction'

    name = fields.Char(index=True, copy=False, default="NEW")
    company_id = fields.Many2one('res.company',string="Broker Name", help="Broker Name", default=lambda self: self.env.user.company_id.id)
    location = fields.Many2one('clickbima.clickbima',string="Location", default=lambda self: self.env['clickbima.clickbima'].search([('start_active', '=',True)],limit=1).id)
    # fy = fields.Many2one('fyyear',domain="[('ex_active','=',True)]")
    fy = fields.Many2one('fyyear',string="Financial Year", default=lambda self: self.env['fyyear'].search([('ex_active', '=',True)],limit=1).id)
    # financial = fields.Many2one('date.range')
    # endate=fields.Date()
    # registername = fields.Many2one('infotype.infotype',readonly=True)
    registername1 = fields.Many2one('subdata.subdata', required=True,string="Register Name")
    # regsitersrno = fields.Char(string="Register Sr.No.",index=True, copy=False,readonly=True)
    regsitersrno = fields.Char(string="Sr.No.",index=True)
    registersubno = fields.Char(string="Sub.Sr.No.",size=2, required=True,default="1")
    proposaldate = fields.Date(string="Proposal Date")
    date2 = fields.Date(string="Date", default=datetime.today())
    user_id =fields.Many2one('res.users',default=lambda  self:self.env.user.id)
    trnstype = fields.Many2one('infotype.infotype', string="Trans Type No.", readonly=True, default=lambda self: self.env['infotype.infotype'].search([('name', '=', 'Transaction Type')]))
    # register = fields.Many2one('infotype.infotype',string="Register")
    type = fields.Many2one('subdata.subdata',string="Type",domain=[('id','in',[172,173,175,712,713,714])])
    no = fields.Many2one('policytransaction',string="Policy Primary Id")
    saleorder = fields.Many2one('sale.order',string="Sale Order")
    clientname = fields.Many2one('res.partner',string="Client Name", required=True)
    group = fields.Char(string="Group Name")
    # pos = fields.Char(string="POS")

    segment = fields.Many2one('category.category', string="Category ", required=True)
    name1 = fields.Many2one('subcategory.subcategory', required=True, string="Sub-Category")
    insurername123 = fields.Many2one('res.partner',string="Insurance Name", required=True,domain=[('customer','=',True),('is_company','=',True)])
    insurerbranch = fields.Many2one('insurerbranch',string="Insurance Branch", required=True)
    pre_insurername = fields.Many2one('res.partner', string="Prev Insurer Name", domain=[('customer', '=', True), ('is_company', '=', True)])
    pre_insurerbranch = fields.Many2one('insurerbranch', string="Prev Insurer Branch")
    group_email=fields.Char(string="Email ID",readonly=True)
    group_phone=fields.Char(string="Mobile",readonly=True)
    group_mobile=fields.Char(string="Client Phone",readonly=True)
    group_tag_ids =fields.Many2many('res.partner.category',string="Tags",readonly=True)
    prevdocket = fields.Char(string="Prev Docket No.")
    prev_policy_date = fields.Date(string="Prev Policy Start Date")
    prev_policy_expiry = fields.Date(string="Prev Policy Expiry Date")
    prev_policy_no = fields.Char(string="Prev Policy No")
    date1 = fields.Date(string="Prev Docket Date")
    policyno = fields.Char(string="No.")
    issuedate = fields.Date(string="Issue")
    startfrom = fields.Date(string="From")
    expiry = fields.Date(string="To")
    suminsured = fields.Float(string="Sum Insured")
    coins = fields.Selection([('Yes','Yes'),('No','No')],string="Co-Insurance Selection", default="No")
    prev_pol = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Prev-Policy Selection", default="No")
    claims = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Claim Selection", default="No")
    brokerage_opt = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Brokerage Selection", default="No")
    pol_stat = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Policy Status Selection", default="No")
    endo_ins = fields.Selection([('Yes','Yes'),('No','No')],string="Endorsement Selection", default="No")
    renewal_opt = fields.Selection([('YES', 'YES'), ('NO', 'NO')], string="Renewal", default="NO")
    declare_opt = fields.Selection([('YES', 'YES'), ('NO', 'NO')], string="Declaration", default="NO")
    date_opt = fields.Selection([('yearly', 'Yearly'), ('nonyearly', 'Non Yearly')], string="Yearly", default="yearly")
    round_off =fields.Float(string="Round Off")
    rm = fields.Many2one('res.users',string="Sales Person", required=True)
    ref = fields.Char(string="Referred By", required=True)
    tc = fields.Many2one('utm.campaign',string="Campaign", required=True)
    csc = fields.Many2one('utm.medium',string="Medium", required=True)
    event = fields.Many2one('utm.source', string="Source", required=True)
    brokerageprem = fields.Float(string="Brokerage  Premium", required=True)
    tppremium = fields.Float(string="TP Premium")
    terrprem = fields.Float(string="Terr Premium")
    stamprem = fields.Float(string="Stamp Duty")
    netprem = fields.Float(string="Net Premium")
    servicetax = fields.Many2one('gsttax',string="GST Rate", required=True)
    servicetaxamt = fields.Float(string="GST Amount" )
    grossprem = fields.Float(string="Gross Premium")
    difference = fields.Float(string="Difference")
    paymenttotal = fields.Float(string="Payment Total")
    transaction = fields.One2many('ptransaction1','name',ondelete='cascade')
    segement = fields.Char(string="Segment")
    brokerage = fields.Float(string="Brokerage Details Premium(IRDA)")
    rate = fields.Float(string="Rate(IRDA)")
    commssionamt = fields.Float(string="Commission Amount(IRDA)")
    servicetax1 = fields.Float(string="GST (IRDA)")
    sertaxamt = fields.Float(string="GST Amt(IRDA)")
    netcomm = fields.Float(string="Net Commission(IRDA)")
    tp_brokerage = fields.Float(string="Brokerage Details Premium(TP)")
    tp_rate = fields.Float(string="Rate(TP)")
    tp_commssionamt = fields.Float(string="Commission Amount(TP)")
    tp_servicetax1 = fields.Float(string="GST (TP)")
    tp_sertaxamt = fields.Float(string="GST Amt(TP)")
    tp_netcomm = fields.Float(string="Net Commission(TP)")
    terr_brokerage = fields.Float(string="Brokerage Details Premium(Terr)")
    terr_rate = fields.Float(string="Rate(Terr)")
    terr_commssionamt = fields.Float(string="Commission Amount(Terr)")
    terr_servicetax1 = fields.Float(string="GST (Terr)")
    terr_sertaxamt = fields.Float(string="GST Amt(Terr)")
    terr_netcomm = fields.Float(string="Net Commission(Terr)")
    broprem = fields.Float(string="Brokerage Details Premium(Reward)")
    rate1 = fields.Float(string="Rate(Reward Rate)")
    commamt = fields.Float(string="Commission Amount(Reward Rate)")
    sertaxrate = fields.Float(string="Service Tax Rate(Reward Rate)")
    sertaxamount = fields.Float(string="Ser. Tax Amt(Reward Rate)")
    netcommission = fields.Float(string="Net Commission(Reward Rate)")
    nameco = fields.Selection([('no', 'No'), ('yes', 'Yes')], default="no",  string="Commission For Lead Insurer")
    rewardco = fields.Selection([('no', 'No'), ('yes', 'Yes')], default="no",string="Reward For Lead Insurer")
    co_insurer_id =fields.One2many('co_insurer_policy','co_insurer_id',ondelete='cascade')
    coinsurance_save= fields.Integer()
    endorsement_id =fields.One2many('endos_policy','endo_id')
    claim_id =fields.One2many('claim_policy','claim_id')
    pipeline_id=fields.Char(string="RFQ/Pipeline")
    sale_order_id=fields.Char(string="RFQ ID SHOW")

    sale_order_store=fields.Many2one('sale.order',string="RFQ ID" ,readonly=True)
    pipeline_store=fields.Many2one('crm.lead',string="Pipeline",readonly=True)
    product_id =fields.Many2one(comodel_name="product.product",string="Scheme",domain=[('x_is_scheme','=',True)])
    team_id = fields.Many2one('crm.team', string="Sales Team")
    data_check = fields.Boolean(compute="_compute_values_form")
    check_policy_expiry = fields.Boolean()
    remark = fields.Text(string="Remark")
    alternate_mobile = fields.Char(string="Alternate No.")
    check_gst_rate =fields.Boolean('Enable GST')
    partner_internal =fields.Char(string="Internal Ref.")
    partner_type= fields.Selection([('company', 'Company'), ('person', 'Individual')])



    @api.onchange('date_opt','startfrom','expiry')
    def check_yearly(self):
        if self.date_opt == 'yearly':
            if self.startfrom:
                date_1 = (datetime.strptime(self.startfrom, '%Y-%m-%d') + relativedelta(days=+ 364))
                self.expiry = date_1.date()
            if self.expiry:
                date_1 = (datetime.strptime(self.expiry, '%Y-%m-%d') + relativedelta(days=- 364))
                self.startfrom = date_1.date()
        elif self.date_opt == 'nonyearly':
            pass

    # @api.onchange('startfrom')
    # def _check_change(self):
    #     if self.startfrom:
    #         date_1 = (datetime.strptime(self.startfrom, '%Y-%m-%d') + relativedelta(days=+ 364))
    #         self.expiry = date_1.date()
    #
    # @api.onchange('expiry')
    # def _check_change_expiry(self):
    #     if self.expiry:
    #         date_1 = (datetime.strptime(self.expiry, '%Y-%m-%d') + relativedelta(days=-364))
    #         self.startfrom = date_1.date()

    @api.onchange('rm')
    def rm_changes(self):
        self.team_id =self.rm.sale_team_id.id

    @api.onchange('brokerageprem','tppremium','terrprem')
    def brokerageprem_changes(self):
        self.brokerage = self.brokerageprem
        self.broprem = self.brokerageprem
        self.tp_brokerage = self.tppremium
        self.terr_brokerage = self.terrprem

    @api.onchange('brokerage','sertaxamt','netcomm','servicetax1','rate')
    def brokerage_changes(self):
        self.commssionamt = (self.brokerage * self.rate)/100
        self.sertaxamt = (((self.brokerage * self.rate)/100) * self.servicetax1)/100
        self.netcomm = self.sertaxamt + self.commssionamt

    @api.onchange('broprem','commamt','sertaxamount','netcommission','rate1','sertaxrate')
    def brokerage_changesss(self):
        self.commamt = (self.broprem * self.rate1) / 100
        self.sertaxamount = (((self.broprem * self.rate1) / 100) * self.sertaxrate) / 100
        self.netcommission = self.commamt + self.sertaxamount

    @api.onchange('tp_brokerage', 'tp_sertaxamt', 'tp_netcomm', 'tp_servicetax1', 'tp_rate', 'tp_commssionamt')
    def tp_brokerage_change(self):
        self.tp_commssionamt = (self.tp_brokerage * self.tp_rate) / 100
        self.tp_sertaxamt = (((self.tp_brokerage * self.tp_rate) / 100) * self.tp_servicetax1) / 100
        self.tp_netcomm = self.tp_commssionamt + self.tp_sertaxamt

    @api.onchange('terr_brokerage', 'terr_sertaxamt', 'terr_netcomm', 'terr_servicetax1', 'terr_rate', 'terr_commssionamt')
    def terr_brokerage_change(self):
        self.terr_commssionamt = (self.terr_brokerage * self.terr_rate) / 100
        self.terr_sertaxamt = (((self.terr_brokerage * self.terr_rate) / 100) * self.terr_servicetax1) / 100
        self.terr_netcomm = self.terr_commssionamt + self.terr_sertaxamt


    @api.depends('name')
    def _compute_values_form(self):
        for i in self:
            self._compute_register_name()
            self._compute_type_name()

    @api.onchange('product_id','segment','insurername123','insurerbranch')
    def product_id_onchange(self):
        if self.product_id:
            data =self.env['product.product'].search([('id','=',self.product_id.id)])
            data_id =self.env['product.template'].search([('id','=',data.product_tmpl_id.id)])
            self.segment =data_id.x_category.id
            self.name1 =data_id.x_subcategory.id
            # self.insurername123 = data_id.x_ins_name.id
            # self.insurerbranch = data_id.x_ins_branch.id

            idra_rate = self.env['idra'].search([('category', '=',data_id.x_category.id), ('subcategory', '=',data_id.x_subcategory.id)], limit=1)
            if idra_rate:
                self.rate =idra_rate.name
                self.servicetax1 =18

            else:
                self.rate1 = 0
                self.sertaxrate = 0
            orc_rate = self.env['orc'].search(
                [('insurername', '=', data_id.x_ins_name.id), ('category', '=', data_id.x_category.id),
                 ('subcategory', '=', data_id.x_subcategory.id)], limit=1)
            if orc_rate:
                self.rate1=orc_rate.rate
                self.sertaxrate =18
                print("DARAT", self.sertaxrate )
            else:
                self.rate1 = 0
                self.sertaxrate = 0
            self.brokerage_opt ='Yes'
            if self.name1:
                self.renewal_opt=self.name1.renewal
                self.declare_opt=self.name1.declaration

            terrpremium_rate = self.env['terrpremium'].search(
                [('insurername', '=', self.insurername123.id), ('category', '=', self.segment.id),
                 ('subcategory', '=', self.name1.id)], limit=1)
            print(terrpremium_rate,"wertyuio")
            if terrpremium_rate:
                self.terr_rate =terrpremium_rate.rate
                self.terr_servicetax1=18
            else:
                self.terr_rate = 0
                self.terr_servicetax1 = 0


            tppremium_rate = self.env['tppremium'].search(
                [('insurername', '=', self.insurername123.id), ('category', '=', self.segment.id),
                 ('subcategory', '=', self.name1.id)], limit=1)
            if tppremium_rate:
                self.tp_rate = tppremium_rate.rate
                self.tp_servicetax1 = 18
            else:
                self.tp_rate = 0
                self.tp_servicetax1 = 0


    @api.onchange('proposaldate')
    def name_proposaldate(self):
        self.issuedate =self.proposaldate

    @api.onchange('saleorder')
    def name_saleorder(self):
        self.clientname = self.saleorder.partner_id.id
        self.tc = self.saleorder.x_campaign_id.id
        self.csc = self.saleorder.x_medium_id.id
        self.event = self.saleorder.x_source_id.id
        self.rm = self.saleorder.user_id.id

    # @api.multi
    # @api.onchange('register')
    # def _register_onchange(self):
    #     res = {}
    #     infoname = self.register.name
    #     locations = self.env['infodata'].search([('name', '=', infoname)])
    #     temp = []
    #     for i in locations:
    #         temp.append(i.infosubdata.name)
    #     res['domain'] = ({'type': [('name', 'in', temp)]})
    #     return res

    @api.multi
    @api.onchange('insurername123')
    def _compute_info_insurerbranch(self):
        res = {}
        locations = self.env['insurer'].search([('name', '=', self.insurername123.id)])
        temp = []
        for i in locations:
            temp.append(i.branch.id)
        res['domain'] = ({'insurerbranch': [('id', 'in', temp)]})
        return res

    @api.multi
    @api.onchange('pre_insurername')
    def _compute_info_pre_insurerbranch(self):
        res = {}
        locations = self.env['insurer'].search([('name', '=', self.pre_insurername.id)])
        temp = []
        for i in locations:
            temp.append(i.branch.id)
        res['domain'] = ({'pre_insurerbranch': [('id', 'in', temp)]})
        return res

    @api.onchange('transaction')
    def name_calculation_debit(self):
        sum = 0
        for i in self.transaction:
            sum = sum + i.amountpy
            self.paymenttotal = sum

    @api.onchange('no')
    def _onchange_partner_id_doc(self):
        if self.type.name =='Renewal':
            renewal_number = self.no
            self.prev_pol = 'Yes'
            self.pre_insurername    = renewal_number.insurername123.id
            self.pre_insurerbranch  = renewal_number.insurerbranch.id
            self.prev_policy_date   = renewal_number.issuedate
            self.prev_policy_no     = renewal_number.policyno
            self.prevdocket         = renewal_number.name
            self.date1              = renewal_number.proposaldate
            self.prev_policy_expiry = renewal_number.expiry
            if renewal_number.expiry:
                date_1                  = (datetime.strptime(renewal_number.expiry,'%Y-%m-%d') + relativedelta(days=+1))
                self.startfrom          = date_1.date()
        # else:
        #     client = self.no
        #     self.clientname = client.clientname.id
        #     self.segment = client.segment.id
        #     self.name1 = client.name1.id
        #     self.group = client.group
        #     self.insurername123 = client.insurername123.id
        #     self.insurerbranch = client.insurerbranch.id
        #     self.ref = client.ref
        #     self.tc = client.tc.id
        #     self.rm = client.rm
        #     self.csc = client.csc.id
        #     self.event = client.event
        #     self.startfrom = client.startfrom
        #     self.expiry = client.expiry
        #     self.brokerageprem = client.brokerageprem
        #     self.tppremium = client.tppremium
        #     self.terrprem = client.terrprem
        #     self.stamprem = client.stamprem
        #     self.netprem = client.netprem
        #     self.difference = client.difference
        #     self.paymenttotal = client.paymenttotal
        #     self.registername1 =client.registername1
        #     self.product_id =client.product_id.id
        #     self.regsitersrno =client.regsitersrno
        #     self.registersubno =client.registersubno
        #     self.location =client.location.id
        #     self.fy =client.fy.id
        #     self.suminsured =client.suminsured
        #     self.brokerageprem=client.brokerageprem
        #     self.tppremium=client.tppremium
        #     self.terrprem =client.terrprem
        #     self.stamprem =client.stamprem
        #     self.netprem=client.netprem
        #     self.servicetax=client.servicetax
        #     self.servicetaxamt =client.servicetaxamt
        #     self.grossprem =client.grossprem
        #     self.difference =client.difference
        #     self.paymenttotal =client.paymenttotal
        #     self.policyno1 =client.policyno1
        #     self.startdate =client.startdate
        #     self.expiry =client.expiry
        #     self.issuedate =client.issuedate
        #     self.proposaldate =client.proposaldate
        #     self.team_id =client.team_id.id
        #     self.remark1 =client.remark1
        #     self.remark2 =client.remark2
        #     for x in self.no:
        #         for i in x.co_insurer_id:
        #             lines = [(5,0,0)]
        #             vals = {'co_share': i.co_share,
        #                                'co_insurer_name': i.co_insurer_name.id,
        #                                'co_insurer_branch': i.co_insurer_branch.id,
        #                                'co_type': i.co_type,
        #                                'co_commission': i.co_commission,
        #                                'co_sum_insured': i.co_sum_insured,
        #                                'co_brokerage_pre': i.co_brokerage_pre,
        #                                'co_commission_amount':i.co_commission_amount,
        #                                'co_remark':i.co_remark}
        #             lines.append((0, 0, vals))
        #             print (lines,"LINESSS")
        #             self.co_insurer_id=lines
        #
        #     for m in self.no:
        #         for z in m.endorsement_id:
        #             linesz=[(5,0,0)]
        #             vals = {"endos_manual" :z.endos_manual,
        #                     "endos_type" :z.endos_type.id,
        #                     "endos_suminsured" :z.endos_suminsured,
        #                     "endos_brokerage_premium" :z.endos_brokerage_premium,
        #                     "endo_tp" :z.endo_tp,
        #                     "endo_terr" : z.endo_terr,
        #                     "endo_stamp" :z.endo_stamp,
        #                     "endo_net" :z.endo_net,
        #                     "endo_gst" :z.endo_gst,
        #                     "endo_gst_amount" :z.endo_gst_amount,
        #                     "endo_gst_gross" :z.endo_gst_gross,
        #                     "endo_difference" :z.endo_difference}
        #             linesz.append((0, 0, vals))
        #             self.endorsement_id=linesz

            # if client.coins =='Yes':
            #     self.write({'coins':'Yes'})
            # elif client.coins =='No':
            #     self.write({'coins':'No'})
        
    @api.onchange('fy')
    def _onchange_partner_id_(self):
        client = self.fy
        self.startdate = client.date_start
        self.endate = client.date_end

    from datetime import date
    def date_checker(self, date_value):
        d1 = self.fy.date_start
        d2 = date_value
        d3 = self.fy.date_end
        if d1 <= d2 <= d3:
            print "true date"
            return True
        else:
           return  False

    @api.multi
    @api.constrains('proposaldate')
    def date_constrains(self):
        for rec in self:
            data = self.date_checker(rec.proposaldate)
            if data is not True:
                raise ValidationError(_('Sorry, Proposal Date Must be between Financial Year...'))

    # @api.multi
    # @api.constrains('startdate', 'endate', 'Date1')
    # def date_constrains2(self):
    #     for rec in self:
    #         if rec.date1 < rec.startdate:
    #             raise ValidationError(_('Sorry, Insurer Detail Date Must be between Financial Year...'))
    #         elif rec.date1 > rec.endate:
    #             raise ValidationError(_('Sorry, Insurer Detail Date Must be between Financial Year...'))
    @api.onchange('proposaldate')
    def _onchange_partner_id_(self):
        client = self.proposaldate
    def issuedate_checker(self, date_value):
        d1 = self.proposaldate
        d2 = date_value
        if d1 <= d2 :
            return True
        else:
            return False
    @api.multi
    @api.constrains('issuedate')
    def date_constrains3(self):
        for rec in self:
            data = self.issuedate_checker(rec.issuedate)
            if data is not True:
                raise ValidationError(_('Sorry, Issue Date Must be greater than Proposal Date...'))

    # @api.multi
    # @api.constrains('startfrom')
    # def date_constrains4(self):
    #     for rec in self:
    #         data = self.date_checker(rec.startfrom)
    #         if data is not True:
    #             raise ValidationError(_('Sorry, Start From Date Must be between Financial Year...'))


    @api.onchange('startfrom')
    def _onchange_partner_id_startfrom(self):
        client = self.startfrom




    @api.onchange('prev_policy_date')
    def _check_prev_policy_date(self):
        if self.prev_policy_date:
            date_1 = (datetime.strptime(self.prev_policy_date, '%Y-%m-%d') + relativedelta(days=+ 364))
            self.prev_policy_expiry = date_1.date()

    # payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms', default=get_default)
    # @api.multi
    # @api.onchange('proposaldate', 'date2')
    # def _date_validation(self):
    #         if self.proposaldate < self.date2:
    #             raise ValidationError(_('Sorry, Proposal Date Must be greater Than Create Date...'))


    @api.onchange('clientname')
    def _onchange_partner_id_values(self):
        """ returns the new values when partner_id has changed """
        client =self.clientname
        if client.parent_id:
            self.group = client.parent_id.name
            self.rm = client.user_id.id
            self.group_email = client.email
            self.group_phone = client.phone
            self.partner_internal = client.ref
            self.partner_type = client.company_type
            tags = []
            for i in client.category_id:
                tags.append(i.id)
            self.group_tag_ids = tags
            res = {}
            locations = self.env['cdac'].search([('clientname12', '=', self.clientname.id)])
            temp = []
            for i in locations:
                temp.append(i.name)
            res['domain'] = ({'cdno': [('name', 'in', temp)]})
            return res
        elif client.company_name:
            self.group = client.company_name
            self.rm = client.user_id.id
            self.group_email = client.email
            self.group_phone = client.phone
            self.partner_internal = client.ref
            self.partner_type = client.company_type
            tags = []
            for i in client.category_id:
                tags.append(i.id)
            self.group_tag_ids = tags
            res = {}
            locations = self.env['cdac'].search([('clientname12', '=', self.clientname.id)])
            temp = []
            for i in locations:
                temp.append(i.name)
            res['domain'] = ({'cdno': [('name', 'in', temp)]})
            return res
        else:
            self.group = ''
            self.rm = client.user_id.id
            self.group_email = client.email
            self.group_phone = client.phone
            self.partner_internal = client.ref
            self.partner_type = client.company_type
            tags = []
            for i in client.category_id:
                tags.append(i.id)
            self.group_tag_ids = tags
            res = {}
            locations = self.env['cdac'].search([('clientname12', '=', self.clientname.id)])
            temp = []
            for i in locations:
                temp.append(i.name)
            res['domain'] = ({'cdno': [('name', 'in', temp)]})
            return res






    # @api.onchange('insurername123')
    # def _onchange_partner_id_values12(self):
    #     """ returns the new values when partner_id has changed """
    #     client12 = self.insurername123
    #     # print('client', client12.name, client12.branch)
    #     self.insurerbranch = client12.branch

    # @api.depends('grossprem','brokerageprem','tppremium','terrprem','stamprem','netprem','servicetax','servicetaxamt','subtotal')
    # def _compute_display_name(self):
    #     netprem = self.brokerageprem + self.tppremium + self.terrprem + self.stamprem
    #     self.netprem = netprem
    #     print(netprem, "netprem")
        # self.servicetaxamt = float(self.netprem) * float(self.servicetax/100)
        # print (self.servicetaxamt,"Ser")
        # self.grossprem = self.servicetaxamt + self.netprem
        # print (self.grossprem,'grossprem')

    @api.onchange('grossprem','brokerageprem','check_gst_rate','tppremium','terrprem','stamprem','netprem','servicetax','servicetaxamt','subtotal','round_off',)
    def _onchange_calculate(self):
        netprem = self.brokerageprem + self.tppremium + self.terrprem + self.stamprem
        self.netprem = netprem
        gstamount = self.servicetax
        if self.check_gst_rate== True:
            self.servicetaxamt
        else:
            self.servicetaxamt = float(self.netprem - self.stamprem) * float(gstamount.tax / 100)
        self.grossprem = self.servicetaxamt + self.netprem + self.round_off
        print(self.grossprem,"GROSS")

    @api.onchange('csc')
    def csc_change(self):
        if self.csc.id == 14:
            pass
        else:
            if self.csc.id is not  False:
                if self.event is not 29:
                    self.event =29

    @api.onchange('event')
    def csc_changess(self):
        if self.event.id ==29:
            pass
        else:
            if self.event.id is not  False:
                if self.csc is not 14:
                    self.csc =14


    @api.onchange('difference','grossprem','paymenttotal','round_off')
    def _onchange_calculate_diff(self):
        # self.grossprem = self.servicetaxamt + self.round_off
        if self.round_off:
            diff = self.grossprem - self.paymenttotal
            self.difference = diff
        else:
            diff = self.grossprem - self.paymenttotal
            self.difference = diff


    # @api.onchange('paymenttotal')
    # def paymenttotal_calculate(self):
    #     self.paymenttotal =self.grossprem +





    def aman(self):
        return { 'name': 'Endorsement',
                 'domain': [],
                 'res_model': 'endorsement',
                 'type': 'ir.actions.act_window',
                 'view_mode': 'tree',
                 'view_type': 'tree',
                 'context': {},
                 'target': 'new',
        }


    def coninsu(self):
        return { 'name': 'Coinsurance',
                 'domain': [],
                 'res_model': 'coinsurance',
                 'type': 'ir.actions.act_window',
                 'view_mode': 'tree',
                 'view_type': 'tree',
                 'context': {},
                 'target': 'new',
        }

    # @api.onchange('insurername123','insurerbranch','suminsured','brokerageprem')
    # def onchange_co_insurer(self):
    #     if self.insurername123:
    #         for i in self:
    #             lines =[(5,0,0)]
    #             vals = {"co_insurer_name": self.insurername123.id,
    #                     "co_insurer_branch": self.insurerbranch.id,
    #                     }
    #             lines.append((0, 0, vals))
    #         i.co_insurer_id=lines

    # @api.multi
    # @api.onchange('co_insurer_id')
    # @api.depends('co_insurer_id.co_sum_insured','co_insurer_id.co_brokerage_pre','co_insurer_id.co_commission_amount')
    # def _compute_co_insuress(self):
    #     print("inside11111")
    #     value = {}
    #     if self.co_insurer_id:
    #         sum_value =self.suminsured
    #         sum_broker = self.brokerageprem
    #         list_of_dict = []
    #         for i in self:
    #             for line in self.co_insurer_id:
    #                 list_of_dict.append((0, 0, {"co_sum_insured":(line.co_share * sum_value) / 100,
    #                                             "co_brokerage_pre":(line.co_commission * sum_broker) / 100,
    #                                             "co_commission_amount":((line.co_commission * sum_broker) / 100) * line.co_commission / 100,
    #                                             }))
    #             print (list_of_dict,"dfghjk")
    #             value.update(co_insurer_id=list_of_dict)
    #             return value
                # print (value,"value")
                # return {'value': value}
    @api.model
    def create(self, vals):
        print (vals,"VAlues")
        if vals.get('name', 'NEW') == 'NEW':
            vals['name'] = self.env['ir.sequence'].next_by_code('policytransaction') or '/'
        co_insurer =vals.get('co_insurer_id')
        endorsement_id =vals.get('endorsement_id')
        sum_value = vals.get('suminsured')
        sum_broker = vals.get('brokerageprem')
        data = super(policytrans, self).create(vals)
        if vals.get('endo_ins') =='Yes':
            eo =[]
            for j in endorsement_id:
                eo.append([0, 0, {'endos_manual': j[2]['endos_manual'],
                                  'endos_type': j[2]['endos_type'],
                                  'endos_reason': j[2]['endos_reason'],
                                  'endos_suminsured': j[2]['endos_suminsured'],
                                  'endos_brokerage_premium': j[2]['endos_brokerage_premium'],
                                  'endo_tp': j[2]['endo_tp'],
                                  'endo_terr': j[2]['endo_terr'],
                                  'endo_net': j[2]['endos_brokerage_premium'] + j[2]['endo_tp'] + j[2]['endo_terr'] + j[2]['endo_stamp'],
                                  'endo_gst':j[2]['endo_gst'],
                                  'endo_gst_amount': j[2]['endo_gst_gross'],
                                  'endo_gst_gross':j[2]['endo_gst_gross'],
                                  'endo_difference': j[2]['endo_difference'],
                                  'endos_date':j[2]['endos_date'],
                                  'endo_remark':j[2]['endo_remark']}])

            endoserment_create = self.env['endorsement'].create({"endo_insurer_id": eo,
                                                                "name": vals.get('insurername123'),
                                                                "endo_insurer_branch": vals.get("insurerbranch"),
                                                                "endo_client": vals.get('clientname')})
            vals['endorsement_save'] =endoserment_create.id

        if vals.get('coins') =='Yes':
            co = []
            co_share_value = 0
            for i in co_insurer:
                co_share_value += i[2]['co_share']
                co_com =(i[2]['co_share'] * sum_value) / 100
                co.append([0, 0, {'co_share': i[2]['co_share'],
                                  'co_insurer_name': i[2]['co_insurer_name'],
                                  'co_insurer_branch': i[2]['co_insurer_branch'],
                                  'co_type': i[2]['co_type'],
                                  'co_broker': i[2]['co_broker'],
                                  'co_commission':i[2]['co_commission'],
                                  'co_sum_insured': co_com,
                                  'co_brokerage_pre': (i[2]['co_commission'] * sum_broker) / 100,
                                  'co_commission_amount': (((i[2]['co_commission'] * sum_broker) / 100) * i[2]['co_commission']) / 100 ,
                                  'co_remark': i[2]['co_remark'],
                                  'co_rate':i[2]['co_rate'],
                                  'co_reward_amount':i[2]['co_reward_amount']}])
            co_insurer_create=self.env['coinsurance'].create({"co_insurer_id":co,
                                                              "name":vals.get('insurername123'),
                                                              "co_insurer_branch":vals.get("insurerbranch"),
                                                              "co_client":vals.get('clientname')})
            co_insurer_save_id =co_insurer_create.id
            vals['coinsurance_save'] =co_insurer_save_id
            co_share_value =0
            cs=[]
            for c in co_insurer:
                co_shares =c[2]['co_share']
                co_share_value +=co_shares
                co_com = (c[2]['co_share'] * sum_value) / 100
                cs.append([0, 0, {'co_share': c[2]['co_share'],
                                  'co_insurer_name': c[2]['co_insurer_name'],
                                  'co_insurer_branch': c[2]['co_insurer_branch'],
                                  'co_type': c[2]['co_type'],
                                  'co_broker': c[2]['co_broker'],
                                  'co_commission':c[2]['co_commission'],
                                  'co_sum_insured': co_com,
                                  'co_brokerage_pre': (c[2]['co_commission'] * sum_broker) / 100,
                                  'co_commission_amount': (((c[2]['co_commission'] * sum_broker) / 100) * c[2]['co_commission']) / 100 ,
                                  'co_remark': c[2]['co_remark'],
                                  'co_rate': c[2]['co_rate'],
                                  'co_reward_amount': c[2]['co_reward_amount']
                                  }])
            vals['co_insurer_id'] =cs
            if co_share_value ==100:
                print(co_insurer_save_id,"PCCCCCCC")
                # var_rid = self.env['generate_register_sno'].create({'generate_id': data.id})
                # data.write({'regsitersrno': var_rid.name})
                return data
            elif co_share_value < 100:
                raise ValidationError(_('Share is less then the 100 percent'))
            elif co_share_value > 100:
                raise ValidationError(_('Share is not greater then 100 percent'))
        else:
            cdno = vals.get('transaction')
            if cdno == None:
                pass
            else:
                for c in cdno:
                    cdac = self.env['cdac'].search([('id', '=', c[2]['cdno'])])
                    cdac.write({"baldate":c[2]['datepy'],
                                "totaldr":cdac.totaldr - c[2]['amountpy'],
                                "adddetails":[[0,0,{"mode1":c[2]['mode1'],
                                                    "amount":-c[2]['amountpy'],
                                                    "date":c[2]['datepy'],
                                                    "remarks": c[2]['remark'],
                                                    "rectno": self.name,
                                                    "rectdate": self.proposaldate
                                                    }]] })

            # var_rid = self.env['generate_register_sno'].create({'generate_id': data.id})
            # data.write({'regsitersrno': var_rid.name})
            return data

    @api.multi
    def write(self,vals):
        print(vals,"VLAS")
        data = super(policytrans, self).write(vals)
        co_share_value = 0
        co_insurer = vals.get('co_insurer_id')
        cdno = vals.get('transaction')
        cos=[]
        co_share=[]
        # if self.coins =='Yes':
        #     print("1")
        if co_insurer:
            for c in co_insurer:
                if c[0] != 4:
                    if c[2] is False:
                        pass
                    elif 'co_share' in c[2].keys():
                        if c[1] != False:
                            cos.append(c[1])
                            co_share.append(c[2]['co_share'])
            check = self.env['policytransaction'].search([('id', '=', self.id)]).co_insurer_id
            # check_data_nots =check.ids
            # print check_data_nots,"CHECK NOTsssss"
            check_data_not = check.search([('id', 'not in', cos), ('co_insurer_id', '=', self.id)])
            # print (co_share,"CO_SGARE")
            # print(cos,"IN ID")
            # print(check,"CHECK")
            # print (check_data_not,"NOT ID")
            for s in check_data_not:
                co_share.append(s.co_share)
            # print(co_share,"SHARE")
            for k in co_share:
                co_share_value += k
            if co_share_value == 100:
                if cdno:
                    for c in cdno:
                        if c[0] != 4:
                            if c[2] is False:
                                pass
                            else:
                                print(c[2]['cdno'], "CDNOOSOSOS")
                                if 'cdno' in c[2].keys():
                                    cdac = self.env['cdac'].search([('id', '=', c[2]['cdno'])])
                                    cdac.write({"baldate":c[2]['datepy'],
                                                "totaldr": cdac.totaldr - c[2]['amountpy'],
                                                "adddetails": [[0, 0, {"mode1": c[2]['mode1'],
                                                                       "amount": -c[2]['amountpy'],
                                                                       "date": c[2]['datepy'],
                                                                       "remarks": c[2]['remark'],
                                                                       "rectno": self.name,
                                                                       "rectdate": self.proposaldate
                                                                       }]]})
                                else:
                                    raise ValidationError(_('You are not allow to edit Record ! Create New Entry to Update the Record'))
                else:
                    pass
                return data
            elif co_share_value < 100:
                raise ValidationError(_('Share is less then the 100 percent'))
            elif co_share_value > 100:
                raise ValidationError(_('Share is not greater then 100 percent'))
        elif cdno:
            print("1")
            for c in cdno:
                print(c,"cccccccccccccccccccccccc")
                if c[0] != 4:
                    print("1")
                    if c[2] is False:
                        pass
                    else:
                        print("2")
                        if 'cdno' in c[2].keys():
                            cdac = self.env['cdac'].search([('id', '=', c[2]['cdno'])],limit=1)
                            print(cdac,"csdsc")
                            print("3")
                            if 'amountpy' and 'mode1' and 'datepy' in c[2].keys():
                                print("4")
                                cdac.write({"baldate":c[2]['datepy'],
                                            "totaldr": cdac.totaldr - c[2]['amountpy'],
                                            "adddetails": [[0, 0, {"mode1": c[2]['mode1'],
                                                                   "amount": -c[2]['amountpy'],
                                                                   "date": c[2]['datepy'],
                                                                   "remarks":c[2]['remark'],
                                                                   "rectno":self.name,
                                                                   "rectdate":self.proposaldate}]]})
                            else:
                                print("5")
                                if ['amountpy'] in c[2].keys():
                                    cdac.write({"baldate": c[2]['datepy'],
                                                "totaldr": cdac.totaldr - c[2]['amountpy'],
                                                "adddetails": c[2],
                                                "remarks": c[2]['remark'],
                                                "rectno": self.name,
                                                "rectdate": self.proposaldate
                                                })
                        else:
                            raise ValidationError( _('You are not allow to edit Record ! Create New Entry to Update the Record'))

            return data
        else:
            return data
        # else:
        #     return data


        # for i in co_insurer:
        #     if i[0] == 1 :
        #         if i[2]['co_share']:
        #             co_share_value += i[2]['co_share']
        #         # co.append([1,i[1],i[2]])
        #     if i[0] ==0 or i[0] == False:
        #         co_share_value += i[2]['co_share']
        #         # co_com = (i[2]['co_share'] * self.suminsured) / 100
        #         # co.append([1, i[1], {'co_share': i[2]['co_share'],
        #         #                    'co_insurer_name': i[2]['co_insurer_name'],
        #         #                    'co_insurer_branch': i[2]['co_insurer_branch'],
        #         #                    'co_type': i[2]['co_type'],
        #         #                    'co_commission': i[2]['co_commission'],
        #         #                    'co_sum_insured': co_com,
        #         #                    'co_brokerage_pre': (i[2]['co_commission'] * sum_broker) / 100,
        #         #                    'co_commission_amount': (i[2]['co_brokerage_pre'] * i[2]['co_commission']) / 100,
        #         #                    'co_remark': i[2]['co_remark']}
        #         #            ])
        #     if i[0]==4:
        #         lines = self.env['co_insurer_policy'].search([('id', '=',i[1])])
        #         co_share_value += lines.co_share
        #         co_com = (lines.co_share * self.suminsured) / 100
        #         # co.append((4, i[1],{'co_share': lines.co_share,
        #         #                     'co_insurer_name': lines.co_insurer_name.id,
        #         #                     'co_insurer_branch': lines.co_insurer_branch.id,
        #         #                     'co_type': lines.co_type,
        #         #                     'co_broker': lines.co_broker,
        #         #                     'co_commission':lines.co_commission,
        #         #                     'co_sum_insured':co_com,
        #         #                     'co_brokerage_pre':(co_com * sum_broker) * 100,
        #         #                     'co_commission_amount': (lines.co_brokerage_pre * lines.co_commission)/100,
        #         #                     'co_remark': lines.co_remark}))
        # print (co,"CO-inSURED")
        # vals['co_insurer_id'] =co

        # data = super(policytrans, self).write(vals)

        # print co_share_value ,"PRINT"
        # if co_share_value == 100:
        # return data
        # elif co_share_value < 100:
        #     raise ValidationError(_('Share is less then the 100 percent'))
        # elif co_share_value > 100:
        #     raise ValidationError(_('Share is not greater then 100 percent'))

    @api.depends('segment','name1')
    def _compute_first(self):
        for record in self:
            if record.segment.name =='' or record.name1.name =='' :
                record.segment.name = False
                record.name1.name = False
            else:
                self.policydetail = str(record.segment.name) +str("/")  +str(record.name1.name)

    @api.multi
    @api.onchange('company_id')
    def _compute_type_name(self):
        res = {}
        locations = self.env['infodata'].search([('name', '=', 27)])
        temp = []

        for i in locations:
            temp.append(i.infosubdata.name)
        res['domain'] = ({'type': [('name', 'in', temp)]})
        return res


    @api.multi
    @api.onchange('fy')
    def _compute_register_name(self):
        res = {}
        fiscalyear =self.env['registryentry'].search([('financial','=',self.fy.id)])
        print(fiscalyear,"FISCAL YEAR")
        register=[]
        if fiscalyear:
            for x in fiscalyear:
                register.append(x.register_name.id)
            locations = self.env['infodata'].search([('name', '=', 57),('infosubdata', 'in',register)])
            temp = []
            for i in locations:
                temp.append(i.infosubdata.name)
            res['domain'] = ({'registername1': [('name', 'in', temp)]})
            return res
            # locations = self.env['infodata'].search([('name', '=',57)])
            # temp = []
            # for i in fiscalyear:
            #     temp.append(i.id)

        else:
            pass


    # @api.multi
    # @api.onchange('trnstype')
    # def _compute_info_name123(self):
    #     # print ('aman')
    #     res = {}
    #     infoname = self.trnstype.name
    #     locations = self.env['infodata'].search([('name', '=', infoname)])
    #     # print (locations.name)
    #     temp = []
    #     for i in locations:
    #         temp.append(i.infosubdata.name)
    #
    #     res['domain'] = ({'type': [('name', '=', temp)]})
    #     return res

    @api.multi
    @api.onchange('type')
    def _compute_info_name12367(self):
        type = self.type.name
        if type == 'New':
            self.checking = True
        elif type == 'Renewal':
            self.checking = False
        else:
            self.checking = False


    @api.multi
    @api.onchange('segment')
    def _compute_info_name12345(self):
        res = {}
        temp1 = []
        for i in self.segment:
            temp1.append(i.name)
        locations = self.env['subcategory.subcategory'].search([('x_category', '=', temp1)])
        temp = []
        for i in locations:
            temp.append(i.id)
        res['domain'] = ({'name1': [('id', 'in', temp)]})
        return res
    # @api.onchange('co_insurer_id')
    # @api.depends('co_insurer_id','co_insurer_id.co_sum_insured', 'co_insurer_id.co_commission', 'co_insurer_id.co_sum_insured', 'co_insurer_id.co_brokerage_pre')
    # def _compute_amount(self):
    #     sum_value = self.suminsured
    #     sum_broker = self.brokerageprem
    #     list_of_dict = []
    #     print ("GOUTAMMAMA")
    #     for i in self:
    #          for line in i.co_insurer_id:
    #               print ((line.co_share * sum_value) / 100,"QEWRTYujkl")
    #               line.co_sum_insured=(line.co_share * sum_value) / 100
    #               line.co_brokerage_pre=(line.co_commission * sum_broker) / 100
    #               line.co_commission_amount=((line.co_commission * sum_broker) / 100) * line.co_commission / 100

# class payment(models.Model):
#     _name = 'sequence'


class Co_insurer(models.Model):
    _name='co_insurer_policy'

    co_insurer_id =fields.Many2one('policytransaction',ondelete='cascade', index=True)
    co_insurer_name = fields.Many2one('res.partner', string="Insurer Name", required=True,domain=[('customer', '=', True), ('is_company', '=', True)])
    co_broker = fields.Many2one('res.partner', string="Broker Name", domain=[('x_cobroker', '=', True)])
    co_insurer_branch = fields.Many2one('insurerbranch', string="Insurer Branch", required=True)
    co_type =fields.Selection([('self','Self'),('others','Others')],string="Type", default="self",required=True)
    co_share =fields.Float(string="Share",required=True )
    co_commission =fields.Float(string="Rate",required=True)
    co_sum_insured =fields.Float(string="Sum Insured")
    co_brokerage_pre =fields.Float(string="Brokerage Permium")
    co_net_premium =fields.Float(string="Net Permium")
    co_net_gross_pre =fields.Float(string="Gross Premium")
    co_commission_amount =fields.Float(string="Commission Amount")
    co_rate =fields.Float(string="Reward Rate")
    co_reward_amount =fields.Float(string="Reward Rate Amount")
    co_remark = fields.Text(string="Remark")
    line_no = fields.Integer(compute='_compute_lines',string="Sr.No")
    co_gst_amount =fields.Float('GST Amount')
    co_gst_tax = fields.Many2one('gsttax', string="GST Rate", required=True)

    def _compute_lines(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])
            for line_rec in first_line_rec.co_insurer_id.co_insurer_id:
                line_rec.line_no = line_num
                line_num += 1


    @api.onchange('co_insurer_id','co_share','co_rate','co_net_premium','co_gst_tax')
    @api.depends('co_insurer_id','co_insurer_id.rewardco','co_net_premium','co_gst_tax','co_insurer_id.nameco','co_share','co_rate','co_sum_insured', 'co_commission','co_sum_insured','co_brokerage_pre')
    def _compute_amount(self):
        # list_of_dict = []
        for line in self:
            sum_broker = line.co_insurer_id.brokerageprem
            sum_value = line.co_insurer_id.suminsured
            sum_broker = line.co_insurer_id.brokerageprem
            net_broker = line.co_insurer_id.netprem
            gross_broker = line.co_insurer_id.grossprem
            line.co_net_premium= (line.co_share * net_broker) / 100
            line.co_sum_insured = (line.co_share * sum_value) / 100
            line.co_brokerage_pre = (line.co_share * sum_broker) / 100
            line.co_net_gross_pre = (line.co_share * gross_broker) / 100
            if line.co_insurer_id.nameco =='yes':
                line.co_commission_amount = ((line.co_commission * ((100 * sum_broker) / 100)) / 100)
                line.co_gst_amount =(line.co_net_premium * line.co_gst_tax.tax)/100
                line.co_net_gross_pre = ((line.co_net_premium * line.co_gst_tax.tax)/100)+line.co_net_premium
            elif line.co_insurer_id.nameco == 'no':
                line.co_commission_amount = ((line.co_commission * ((line.co_share * sum_broker) / 100)) / 100)
                line.co_gst_amount = (line.co_net_premium * line.co_gst_tax.tax) / 100
                line.co_net_gross_pre = ((line.co_net_premium * line.co_gst_tax.tax) / 100) + line.co_net_premium
            if  line.co_insurer_id.rewardco =='no':
                line.co_reward_amount =(line.co_rate * ((line.co_share * sum_broker) / 100))/100
            elif line.co_insurer_id.rewardco =='yes':
                line.co_gst_amount = (line.co_net_premium * line.co_gst_tax.tax) / 100
                line.co_reward_amount = (line.co_rate * sum_broker) / 100
                line.co_net_gross_pre = ((line.co_net_premium * line.co_gst_tax.tax) / 100) + line.co_net_premium





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
        data =super(Co_insurer, self).create(vals)
        return data

    # @api.model
    # def write(self, vals):
    #     print (vals, "VALSSS")
    #     co_value=0
    #     for i in self:
    #         co_shares =i.co_share
    #         co_value +=co_shares
    #     print co_value,"VALUESS"
    #
    #     data = super(Co_insurer, self).write(vals)
    #     return data


    # @api.onchange('co_share')
    # def onchange_share(self):
    #     if self.co_share:
    #         co_share_value = 0
    #         for i in self:
    #             co_share_value += i.co_share
    #             print (co_share_value,"COO")
    #             if co_share_value == 100:
    #                 pass
    #             elif co_share_value < 100:
    #                 raise ValidationError(_('Share is less then the 100 percent'))
    #             elif co_share_value > 100:
    #                 raise ValidationError(_('Share is not greater then 100 percent'))


class Endosorment(models.Model):
    _name = 'endos_policy'

    endo_id =fields.Many2one('policytransaction',ondelete='cascade', index=True)
    name = fields.Char(string="Endosement Generated",default="NEW")
    endos_manual = fields.Char(string="Endosement Manual Generated")
    endos_type = fields.Many2one('subdata.subdata',string="Endosement Type")
    endos_reason = fields.Many2one('subdata.subdata',string="Endosement Reason")
    endos_suminsured = fields.Float(string="Endosement Suminsured")
    endos_brokerage_premium = fields.Float(string="Endosement Brokerage Premium")
    endo_tp = fields.Float(string="TP")
    endo_terr = fields.Float(string="Terr Permium")
    endo_stamp = fields.Float(string="Stamp")
    endo_net = fields.Float(string="Net Premium")
    endo_net_comp = fields.Float(string="Net Premium",compute="_onchange_endo_netss")
    endo_gst = fields.Many2one('gsttax',string="Service Tax Rate", required=True)
    endo_gst_amount = fields.Float(string="GST Amount")
    endo_gst_gross = fields.Float(string="GST Gross")
    endo_difference = fields.Float(string="Difference")
    endos_date =fields.Date(string='Effective Date')
    endo_payment =fields.Float(string="Endosement Payment")
    endo_commission =fields.Float(string="Endosement Commission")
    endo_round_off =fields.Float(string="Endosement Round Off")
    endo_remark =fields.Text(string="Endosement Remark")
    line_no = fields.Integer(compute='_compute_lines',string="Sr.No")



    def _compute_lines(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])
            for line_rec in first_line_rec.endo_id.endorsement_id:
                line_rec.line_no = line_num
                line_num += 1

    @api.multi
    @api.depends('endos_type','endo_payment','endo_round_off','endos_suminsured', 'endos_brokerage_premium', 'endo_tp', 'endo_terr', 'endo_stamp', 'endo_net',
                  'endo_gst', 'endo_gst_amount','endo_gst_gross','endo_difference')
    @api.onchange('endos_type','endo_payment','endo_round_off','endos_suminsured', 'endos_brokerage_premium', 'endo_tp', 'endo_terr', 'endo_stamp', 'endo_net',
                  'endo_gst', 'endo_gst_amount','endo_gst_gross','endo_difference')
    def _onchange_endo_netss(self):
        for i in self:
            netprem = i.endos_brokerage_premium + i.endo_tp + i.endo_terr  + i.endo_stamp
            i.endo_net = netprem
            i.endo_gst_amount = float(i.endo_net) * float(i.endo_gst.tax / 100)
            i.endo_gst_gross = i.endo_gst_amount + i.endo_net
            i.endo_commission = (i.endo_id.rate * i.endo_net)/100
            # i.endo_gst_gross = i.endo_gst_amount
            i.endo_difference =i.endo_gst_gross - (i.endo_payment) + (i.endo_round_off)

    @api.model
    def create(self, vals):
        if vals.get('name', 'NEW') == 'NEW':
            vals['name'] = self.env['ir.sequence'].next_by_code('endos_policy') or '/'
        data = super(Endosorment, self).create(vals)
        return data

    @api.multi
    @api.onchange('name')
    def _compute_endos_type(self):
        res = {}
        locations = self.env['infodata'].search([('name', '=',71)])
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
            trans =self.endo_id
            if trans.startfrom <= self.endos_date and  trans.expiry >= self.endos_date :
                pass
            else:
                raise ValidationError('Please choose the effective date between Start date/Expiry Date')






class payment(models.Model):
    _name = 'ptransaction1'


    name = fields.Many2one('policytransaction',ondelete='cascade', index=True)
    mode = fields.Many2one('infotype.infotype',string="Mode" ,  default=lambda self: self.env['infotype.infotype'].search([('name','=','Mode of Payment')]))
    mode1 = fields.Many2one('subdata.subdata',domain=[('id','in',[145,146,147,148,150,149,109])],required=True)
    chdd = fields.Char(string="Ch/DD No")
    cdno = fields.Many2one('cdac')
    others_mode_payment = fields.Many2one('subdata.subdata', string="Other Mode")
    amountpy = fields.Float(string="Amount",required=True)
    bankpy = fields.Many2one('infotype.infotype',default=lambda self: self.env['infotype.infotype'].search([('name','=',47)]).id)
    bankpy1 = fields.Many2one('subdata.subdata')
    bankbranch = fields.Char(string="Bank Branch")
    datepy = fields.Date(string="Dated", default=datetime.today(),required=True)
    accountcd = fields.Boolean()
    pay_of_id = fields.Selection([('policy','Policy'),('endo','Endos')],string="Payment Of",default="policy",required=True)
    # check=fields.Boolean(compute="_compute_check")
    endo_pay_no = fields.Char(string="Endos.No.")
    insurername = fields.Many2one('res.partner', string="Insurer Name",
                                     domain=[('customer', '=', True), ('is_company', '=', True)])
    insurerbranch = fields.Many2one('insurerbranch', string="Insurer Branch")
    location = fields.Many2one('clickbima.clickbima', string="Location",default=lambda self: self.env['clickbima.clickbima'].search([('start_active', '=', True)], limit=1).id)
    segment = fields.Many2many('category.category')
    # clientname = fields.Many2one('res.partner', string="Client Name")
    clientname = fields.Many2one('res.partner', string="Client Name", domain="[('x_client','=',True)]")
    remark = fields.Text()




    @api.onchange('pay_of_id')
    def endo_change(self):
        if self.pay_of_id == 'endo':
            res = {}
            for i in self:
                for j in i:
                    data = j.name.endorsement_id.ids
                    if not data:
                        raise ValidationError('Please Fill Endorsement Details and save the record firstly for further payment process/No Endorsement available')
                    if data:
                        for res in data:
                            endo_pay_id = self.env['endos_policy'].search([('id', '=', res)])
                        self.endo_pay_no=endo_pay_id.endos_manual
                        self.amountpy=endo_pay_id.endo_gst_gross
                        different_amount=endo_pay_id.endo_difference-self.amountpy
                        endo_pay_id.write({'endo_payment':self.amountpy,'endo_difference':different_amount})





    @api.onchange('mode1')
    def mode_change(self):
        if self.mode1.id == 109:
            res = {}
            locations = self.env['infodata'].search([('name', '=', 88)])
            temp = []
            for i in locations:
                temp.append(i.infosubdata.id)
            res['domain'] = ({'others_mode_payment': [('id', 'in', temp)]})
            return res
        else:
            pass

    @api.onchange('pay_of_id')
    def difference_value(self):
        for i in self:
            self.amountpy =i.name.grossprem

    @api.multi
    @api.onchange('bankpy1')
    def compute_bankpy1(self):
        res = {}
        locations = self.env['infodata'].search([('name', '=',47)])
        temp = []
        for i in locations:
            temp.append(i.infosubdata.id)
        res['domain'] = ({'bankpy1': [('id', 'in', temp)]})
        return res

    @api.multi
    @api.onchange('insurername')
    def compute_ptransaction1(self):
        res = {}
        locations = self.env['insurer'].search([('name', '=', self.insurername.id)])
        temp = []
        for i in locations:
            temp.append(i.branch.id)
        res['domain'] = ({'insurerbranch': [('id', 'in', temp)]})
        return res

    @api.multi
    @api.onchange('segment','location','insurerbranch','insurername','clientname')
    def onchange_account(self):
        res={}
        temp = []

        for z in self:
            self.insurerbranch =z.name.insurerbranch.id,
            self.insurername =z.name.insurername123.id,
            self.clientname =z.name.clientname.id,
            locations = self.env['cdac'].search([('insurername121', '=', z.name.insurername123.id),('insurerbranch22','=',z.name.insurerbranch.id),('clientname12','=',z.name.clientname.id)])
            for i in locations:
                temp.append(i.id)
        res['domain'] = ({'cdno': [('id', 'in', temp)]})
        return res

    # @api.multi
    # @api.onchange('clientname')
    # def _compute_cdno(self):
    #     print("gyi")
    #     res = {}
    #     locations = self.env['cdac'].search([('name', '=', self.clientname.id)])
    #     print (locations,"locations")
    #     temp = []
    #     for i in locations:
    #         temp.append(i.name.id)
    #     print (temp,"temp")
    #     res['domain'] = ({'cdno': [('name', 'in', temp)]})
    #     return res
    # def _compute_check(self):
    #     res = {}
    #     locations = self.env['infodata'].search([('name', '=', 89)])
    #     temp = []
    #     for i in locations:
    #         temp.append(i.infosubdata.name)
    #     res['domain'] = ({'endos_reason': [('name', 'in', temp)]})
    #     return res


    # @api.onchange('cdno')
    # def _onchange_partner_cdnumber(self):
    #     """ returns the new values when partner_id has changed """
    #     account = self.cdno
    #     print('account',account.name,account.accno)
    #     self.accno = account.accno

    @api.multi
    @api.onchange('mode1')
    def _compute_info_mode123(self):
        type = self.mode1.name
        if type == 'CD A/c':
            self.accountcd = True
        else:
            self.accountcd = False


    @api.multi
    @api.onchange('mode')
    def _compute_info_name_mode(self):
        res = {}
        infoname = self.mode.name
        locations = self.env['infodata'].search([('name', '=', infoname)])
        temp = []
        for i in locations:
            temp.append(i.infosubdata.name)

        res['domain'] = ({'mode1': [('name', '=', temp)]})
        return res

    @api.multi
    @api.onchange('bankpy')
    def _compute_info_name_bank_type(self):
        res = {}
        infoname = self.bankpy.name
        locations = self.env['infodata'].search([('name', '=', infoname)])
        temp = []
        for i in locations:
            temp.append(i.infosubdata.name)
        res['domain'] = ({'bankpy1': [('name', '=', temp)]})
        return res

    @api.model
    def create(self,vals):
        return super(payment, self).create(vals)


class claim(models.Model):
    _name = 'claim_policy'

    claim_id =fields.Many2one('policytransaction',ondelete='cascade', index=True)
    name = fields.Char(string="Claim Generated",default="1")
    claim_manual = fields.Char(string="Claim Manual Generated")
    claim_type = fields.Many2one('subdata.subdata',string="Claim Type",ondelete='cascade',required=True,domain=[('id','in',[547,548])])
    location = fields.Char(string="Location")
    claim_ticket =fields.Many2one('project.issue',string="Ticket Number",required=True,readonly=True)
    claim_date_int = fields.Datetime(string="Ticket Date",required=True,readonly=True)
    claim_of_admiss= fields.Date(string="Date of Admission/Loss",required=True)
    claim_date = fields.Date(required=True)
    claim_of_cause= fields.Text(string="Cause/Type of Claim",required=True)
    claim_of_est_cause= fields.Float(string="Estimated Claim/Loss",required=True)
    claim_brief= fields.Text(string="Brief Description of Case",required=True)
    claim_other_det= fields.Text(string="Other Details")
    claim_contact_insured = fields.Many2one('res.partner', ondelete='cascade', string="Contact Person of Insured",domain=[('x_client', '=', True)])
    claim_contact_person = fields.Many2one('res.partner',ondelete='cascade',string="Contact Person of Insurer",domain=[('customer','=',True)])
    policy_insurer_name = fields.Many2one('res.partner',ondelete='cascade',string="Insurer Name",domain=[('customer','=',True),('is_company','=',True)])
    policy_contact_person = fields.Many2one('res.partner',ondelete='cascade',string="Contact Person" )
    policy_mobile = fields.Char(string="Phone/Mobile" )
    policy_email = fields.Char(string="Email ID" )
    policy_pol_no = fields.Char(string="Policy No." )
    policy_scheme = fields.Many2one(comodel_name="product.product",ondelete='cascade',string="Scheme",domain=[('x_is_scheme','=',True)])
    policy_startfrom = fields.Date(string="Start From")
    policy_expiry = fields.Date(string="Expiry Date")
    policy_insured_name = fields.Many2one('res.partner', ondelete='cascade', string="Insured Name")
    policy_claimant = fields.Many2one('res.partner', ondelete='cascade', string="Insured/Claimant",domain=['|',('x_client', '=', True),('x_claimant', '=', True)])
    policy_contact_person2 = fields.Many2one('res.partner',ondelete='cascade',string="Contact Person" )
    policy_mobile2 = fields.Char(string="Phone/Mobile")
    policy_email2 = fields.Char(string="Email ID")
    policy_tpa = fields.Many2one('res.partner',ondelete='cascade',string="TPA Name",domain=[('x_tpa','=',True)])
    policy_contact_person3 = fields.Many2one('res.partner',ondelete='cascade',string="Contact Person" )
    policy_mobile3 = fields.Char(string="Phone/Mobile")
    policy_email3 = fields.Char(string="Email ID")

    policy_surveyer_name = fields.Many2one('res.partner',string="Surveyer Name",domain=[('x_surveyver','=',True)])
    policy_contact_person4 = fields.Many2one('res.partner',ondelete='cascade',string="Contact Person" )
    policy_mobile4 = fields.Char(string="Phone/Mobile")
    policy_email4 = fields.Char(string="Email ID")
    policy_patient_name = fields.Many2one('res.partner',ondelete='cascade',string="Patient Name" )
    policy_relationship = fields.Char(string="Relationship")
    policy_health_card = fields.Char(string="Health Card No")
    contact_insured_name = fields.Many2one('res.partner', ondelete='cascade', string="Insured Contact")
    contact_mobile = fields.Char(string="Contact Mobile")
    contact_email = fields.Char(string="Contact Email")
    claim_is_tpa = fields.Many2one('res.partner',ondelete='cascade',string="Contact Person of TPA",domain=[('x_tpa','=',True)])
    claim_is_survey = fields.Many2one('res.partner',ondelete='cascade',string="Surveyer Name",domain=[('x_surveyver','=',True)])
    claim_status = fields.Many2one('subdata.subdata',ondelete='cascade',string="Claim Status")
    claim_sub_status = fields.Many2one('infosubdatadropdown',ondelete='cascade',string="Claim Sub-Status")
    claim_remark = fields.Text(string="Claim Remark")
    claim_status_update_rate = fields.Float(string="Status Update Rate")
    claim_pri_diagnosis =fields.Char()
    line_no = fields.Integer(compute='_compute_lines',string="Sr.No")
    claim_onemany_id = fields.One2many('claim_history', 'claim_onemany_id')
    lor_one2many_id = fields.One2many('claim_lor', 'lor_onemany_id')

    settle_type = fields.Many2one('subdata.subdata',string="Settle Type", ondelete='cascade',domain=[('id','in',[644,650,651])])
    settle_amount = fields.Float(string="Settlement Amount")
    settle_deduction = fields.Float(string="Deductions/Excess")
    settle_details = fields.Text(string="Details")
    settle_date = fields.Date(string="Date of Settlement")
    settle_remark = fields.Text(string="Remark on Settlement")
    settle_reputation = fields.Text(string="Repudiation Reason")
    settle_reputation_date = fields.Date(string="Repudiation Date")
    check_company = fields.Boolean()
    state =fields.Selection([('notget','Not Get'),('get','Get')],string="State", default="notget")
    check_claim=fields.Boolean(default=False)
    check_claim_intimation = fields.Boolean(default=False,compute='_compute_claim_selection')
    claim_amount = fields.Float(string="Claim Amount",required=True)

    @api.one
    @api.constrains('claim_amount')
    def claim_amount_check(self):
        # if self.claim_amount:
            if self.claim_amount == 0.0 or self.claim_amount == 0.00  or self.claim_amount ==0:
                raise Warning(_('Values should not be zero in claim amount'))


    @api.onchange('claim_amount')
    def claim_amount_check_onchange(self):
        # if self.claim_amount:
            if self.claim_amount == 0.0 or self.claim_amount == 0.00 or self.claim_amount ==0:
                raise ValidationError(_('Values should not be zero in claim amount'))

    @api.one
    @api.constrains('settle_amount')
    def settle_amount_constr(self):
        # if self.settle_amount:
            if self.settle_amount == 0.0 or self.settle_amount == 0.00 or self.settle_amount == 0:
                raise Warning(_('Values should not be zero in settle amount'))

    @api.onchange('settle_amount')
    def settle_amount_onchange(self):
        # if self.settle_amount:
            if self.settle_amount == 0.0 or self.settle_amount == 0.00 or self.settle_amount == 0:
                raise ValidationError(_('Values should not be zero in settle amount'))

    @api.one
    @api.constrains('claim_of_est_cause')
    def claim_of_est_cause_contr(self):
        # if self.claim_of_est_cause:
            if self.claim_of_est_cause == 0.0 or self.claim_of_est_cause == 0.00 or self.claim_of_est_cause == 0:
                raise Warning(_('Values should not be zero in claim estimated amount'))

    @api.onchange('claim_of_est_cause')
    def claim_of_est_cause_onchange(self):
        # if self.claim_of_est_cause:
            if self.claim_of_est_cause == 0.0 or self.claim_of_est_cause == 0.00 or self.claim_of_est_cause == 0:
                raise ValidationError(_('Values should not be zero in claim estimated amount'))

    def _compute_claim_selection(self):
        for i in self:
            if i.claim_id.claims == 'Yes':
                i.check_claim_intimation = True


    def fetch_button(self):
        for i in self:
            for j in i.claim_id:
                try:
                    data = self.env['tempmaster'].search([('category', '=', j.segment.id),('subcategory','=', j.name1.id)])
                    if not data:
                        raise ValidationError(_('Please add Category/Sub-Category'))
                    if data:
                        for k in data.tempremark:
                            self.env['claim_lor'].create({"header": k.header,"lor_onemany_id":self.id})
                            self.write({"state":'get'})
                except Exception as e:
                    raise ValidationError(_(e))

    @api.onchange('contact_insured_name')
    def contact_insured_name_change1(self):
        if self.contact_insured_name:
            contact = self.contact_insured_name
            self.contact_email = contact.email
            self.contact_mobile = contact.mobile

    @api.onchange('policy_insured_name')
    def policy_insurer_name_change1(self):
        if self.policy_insured_name:
            res = {}
            insurer_id = self.policy_insured_name
            if insurer_id.company_type =='person':
                self.check_company =True
            else:
                self.check_company=False
            insurer_id = self.policy_insured_name.id
            data = self.env['res.partner'].search([('id', '=', insurer_id)]).child_ids
            temp = []
            for i in data:
                temp.append(i.id)
            temp.append(insurer_id)
            res['domain'] = ({'contact_insured_name': [('id', 'in', temp)]})
            return res

    @api.onchange('policy_surveyer_name')
    def policy_surveyer_name_chnage(self):
        if self.policy_surveyer_name:
            res = {}
            insurer_id = self.policy_surveyer_name.id
            data = self.env['res.partner'].search([('id', '=', insurer_id)]).child_ids
            temp = []
            for i in data:
                temp.append(i.id)
            temp.append(insurer_id)
            res['domain'] = ({'policy_contact_person4': [('id', 'in', temp)]})
            return res

    @api.onchange('policy_contact_person4')
    def onchange_policy_contact44(self):
        if self.policy_contact_person4:
            contact = self.policy_contact_person4
            self.policy_email4 = contact.email
            self.policy_mobile4 = contact.mobile

    def _compute_lines(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])
            for line_rec in first_line_rec.claim_id.claim_id:
                line_rec.line_no = line_num
                line_num += 1

    @api.depends('policy_insurer_name')
    @api.onchange('policy_insurer_name')
    def onchange_policy_insurer(self):
        if self.policy_insurer_name:
            res = {}
            insurer_id = self.policy_insurer_name.id
            data = self.env['res.partner'].search([('id', '=', insurer_id)]).child_ids
            temp = []
            for i in data:
                temp.append(i.id)
            temp.append(insurer_id)
            res['domain'] = ({'policy_contact_person': [('id', 'in', temp)]})
            return res

    @api.onchange('policy_contact_person')
    def onchange_policy_contact(self):
        if self.policy_contact_person:
            contact = self.policy_contact_person
            self.policy_email = contact.email
            self.policy_mobile = contact.mobile

    @api.onchange('policy_insured_name')
    def onchange_policy_insured(self):
        if self.policy_insured_name:
            res = {}
            insured_id = self.policy_insured_name.id
            data = self.env['res.partner'].search([('id', '=', insured_id)]).child_ids
            temp = []
            for i in data:
                temp.append(i.id)
            temp.append(insured_id)
            res['domain'] = ({'policy_claimant': [('id', 'in', temp)]})
            return res

    @api.onchange('policy_claimant')
    def policy_onchange_claimant2(self):
        if self.policy_claimant:
            insurer_id = self.policy_claimant
            if insurer_id.company_type == 'person':
                res1 = {}
                claimant_id = self.policy_claimant.id
                data = self.env['res.partner'].search([('id', '=', claimant_id)]).child_ids
                temp = []
                for i in data:
                    temp.append(i.id)
                temp.append(claimant_id)
                res1['domain'] = ({'policy_contact_person2': [('id', 'in', temp)]})
                return res1
            else:
                res1 = {}
                insured_id = self.policy_insured_name.id
                data = self.env['res.partner'].search([('id', '=', insured_id)]).child_ids
                temp = []
                for i in data:
                    temp.append(i.id)
                temp.append(insurer_id)
                res1['domain'] = ({'policy_contact_person2': [('id', 'in', temp)]})
                return res1



    @api.onchange('policy_contact_person2')
    def onchange_policy_contact_person2(self):
        if self.policy_contact_person2:
            contact2 = self.policy_contact_person2
            self.policy_email2 = contact2.email
            self.policy_mobile2 = contact2.mobile

    @api.onchange('policy_tpa')
    def onchange_policy_tpa1(self):
        if self.policy_tpa:
            res1 = {}
            insured_id = self.policy_tpa.id
            data = self.env['res.partner'].search([('id', '=', insured_id)]).child_ids
            temp = []
            for i in data:
                temp.append(i.id)
            temp.append(insured_id)
            res1['domain'] = ({'policy_contact_person3': [('id', 'in', temp)]})
            return res1

    @api.onchange('policy_claimant')
    def policy_claimant_patient(self):
        print("INISDE SCLAI")
        if self.policy_claimant:
            insurer_id = self.policy_claimant
            if insurer_id.company_type == 'person':
                res1 = {}
                claimant_id = self.policy_claimant.id
                data = self.env['res.partner'].search([('id', '=', claimant_id)]).child_ids
                temp = []
                for i in data:
                    temp.append(i.id)
                temp.append(claimant_id)
                res1['domain'] = ({'policy_patient_name': [('id', 'in', temp)]})
                return res1
            else:
                res1 = {}
                insured_id = self.policy_insured_name.id
                data = self.env['res.partner'].search([('id', '=', insured_id)]).child_ids
                temp = []
                for i in data:
                    temp.append(i.id)
                temp.append(insurer_id)
                res1['domain'] = ({'policy_patient_name': [('id', 'in', temp)]})
                return res1

    @api.onchange('policy_contact_person3')
    def onchange_policy_contact_person3(self):
        if self.policy_contact_person3:
            contact3 = self.policy_contact_person3
            self.policy_email3 = contact3.email
            self.policy_mobile3 = contact3.mobile

    @api.onchange('policy_patient_name')
    def onchange_policy_patient_name(self):
        if self.policy_patient_name:
            contact4 = self.policy_patient_name
            self.policy_relationship = contact4.function
            self.policy_health_card = contact4.comment



    @api.onchange('claim_type')
    def onchange_type(self):
        if self.claim_type:
            for i in self:
                self.claim_status = ""
                if i.claim_type.id == 547:
                    res = {}
                    locations = self.env['infodata'].search([('name', '=', 97)])
                    self.policy_pol_no = i.claim_id.policyno
                    self.policy_scheme = i.claim_id.product_id.id
                    self.policy_startfrom = i.claim_id.startfrom
                    self.policy_expiry = i.claim_id.expiry
                    self.policy_insurer_name = i.claim_id.insurername123.id
                    temp = []
                    for i in locations:
                        temp.append(i.infosubdata.name)
                    res['domain'] = ({'claim_status': [('name', 'in', temp)]})
                    return res
                elif i.claim_type.id == 548:
                    res1 = {}
                    locations = self.env['infodata'].search([('name', '=', 62)])
                    self.policy_pol_no = i.claim_id.policyno
                    self.policy_scheme = i.claim_id.product_id.id
                    self.policy_startfrom = i.claim_id.startfrom
                    self.policy_expiry = i.claim_id.expiry
                    self.policy_insurer_name = i.claim_id.insurername123.id
                    tempx = []
                    for i in locations:
                        tempx.append(i.infosubdata.name)
                    res1['domain'] = ({'claim_status': [('name', 'in', tempx)]})
                    return res1
                else:
                    res1 = {}
                    res1['domain'] = ({'claim_status': [('name', 'in', [])]})
                    return res1



    @api.onchange('claim_status')
    def onchange_claim_status(self):
        if self.claim_status:
            res = {}
            locations = self.env['infosubdata'].search([('infoname', '=', self.claim_status.id)])
            temps = []
            for i in locations:
                temps.append(i.infosub1.name)
            res['domain'] = ({'claim_sub_status': [('name', 'in', temps)]})
            return res

    @api.model
    def create(self, vals):
        data = super(claim, self).create(vals)
        return data

class Claim_Lor(models.Model):
    _name='claim_lor'

    name = fields.Char(string="LOR")
    lor_onemany_id =fields.Many2one('claim_policy',ondelete='cascade', index=True)
    header=fields.Char(string="Header")
    lor_date_receipt = fields.Date(string="Date of Receipt")
    lor_doc_date = fields.Date(string="LOR Date")
    lor_remark = fields.Text(string="LOR Remark")
    lor_many_remark = fields.Many2one('subdata.subdata',string="Remark",domain=[('id','in',[657,661])])




class Claim_history(models.Model):
    _name='claim_history'


    name = fields.Char(string="Claim Generated")
    claim_onemany_id =fields.Many2one('claim_policy',ondelete='cascade', index=True)
    claim_type = fields.Many2one('subdata.subdata', string="Claim Type", ondelete='cascade',
                                 domain=[('id', 'in', [547, 548])])
    claim_status1 = fields.Many2one('subdata.subdata',string="Claim Status", ondelete='cascade', readonly=True,store=False)
    claim_sub_status = fields.Many2one('infosubdatadropdown',string="Claim Sub-Status",ondelete='cascade')
    # claim_check = fields.Boolean(compute='_get_education_domain',store=True)
    claim_remark = fields.Text(string="Claim Remark")
    line_no = fields.Integer(compute='_compute_lines', string="Sr.No")
    reply = fields.Text(string="Reply")
    reply_date = fields.Date(string="Reply Date")
    next_activity_date = fields.Date(string="Next Activity Date")
    next_activity = fields.Text(string="Next Activity")

    # def _default_validity_date(self):
        # self._compute_amount()
    claim_status = fields.Many2one('subdata.subdata', string="Claim Status", ondelete='cascade')

    @api.multi
    def send_update(self):
        try:
            if self.claim_onemany_id.claim_ticket:
                self.write({"check_claim":True})
                claim_reply_id = self.env['project.issue'].sudo().search([('id', '=', self.claim_onemany_id.claim_ticket.id)], limit=1)
                if self.claim_onemany_id.claim_manual:
                    claim_reply_id.write({"x_reply":self.reply,"x_reply_date":self.reply_date,"x_claim_status":self.claim_status.id,
                                          "x_claim_sub_status":self.claim_sub_status.id,"x_claim_amount":self.claim_onemany_id.claim_amount,
                                          "x_settlement_amount":self.claim_onemany_id.settle_amount})
                    message_id = self.env['message.wizard'].sudo().create({'text':"Updated Successfully"})
                    return {
                        'name': 'Message',
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'message.wizard',
                        # pass the id
                        'res_id': message_id.id,
                        'target': 'new'
                    }
                else:
                    raise ValidationError(_('Please Enter the claim number'))

        except Exception as e:
            raise ValidationError("Error: %s" % str(e))



    def send_whatsapp(self):
        try:
            db_name = odoo.tools.config.get('db_name')
            if not db_name:
                _logger.error(
                    "ERROR: To proper setup OAuth2 and Redis - it's necessary to set the parameter 'db_name' in Odoo config file!")
                print(
                    "ERROR: To proper setup OAuth2 and Token Store - it's necessary to set the parameter 'db_name' in Odoo config file!")
            else:
                # Read system parameters...
                registry = Registry(db_name)
                with registry.cursor() as cr:
                    # ... of OAuth2 tokens
                    cr.execute("SELECT value FROM ir_config_parameter \
                                   WHERE key = 'whatsapp.whatsapp.token'")
                    res = cr.fetchone()
                    token = res and str(res[0])
                    phone = self.claim_onemany_id.claim_ticket.x_mobile
                    print(phone,"PPPPPHHHOOONNNEEE")
                    url = token
                    print(url, "URLLLLL")
                    if (len(phone)) == 12 or len(phone) == 13 or len(phone) == 11 :
                        vals = {"phone": phone,
                                "body": self.reply
                                }
                        print("111111111111111")
                    elif  len(phone) == 10:
                        vals = {"phone":str('91')+phone,
                                "body": self.reply
                                }
                        print(vals,"22222222222")
                    r = requests.post(url, data=vals, verify=False)
                    print(r, "RESQ")
                    auth = json.dumps(r.json())
                    all = json.loads(auth)
                    print(all.keys(), "ALLLLLLLLLLLLLLLLLl")
                    if 'id' in all.keys():
                        data = all['sent']
                        message = all['message']
                        idss = all['id']
                        if data == True:
                            self.write({'status': 'sendsuccessfully'})
                            valss = {"messageid": message, "status": data, "chat_id": idss,
                                     "message": self.reply}
                            data = self.env['whatsapp.log'].create(valss)
                            message_id = self.env['message.wizard'].sudo().create({'text': "Sent Successfully"})
                            return {
                                'name': 'Message',
                                'type': 'ir.actions.act_window',
                                'view_mode': 'form',
                                'res_model': 'message.wizard',
                                # pass the id
                                'res_id': message_id.id,
                                'target': 'new'
                            }


                        else:
                            self.write({'status': 'unsend'})
                            raise ValidationError("Message: %s" % str(all['message']))

                    else:
                        valss = {"messageid": "Not Provided",
                                 "status": "Incorrect Mobile number '" + str(phone) + "'",
                                 "chat_id": "Not Provided", "message": self.reply}
                        data = self.env['whatsapp.log'].create(valss)
                        message_id = self.env['message.wizard'].sudo().create({'text': "Not Sent"})
                        return {
                            'name': 'Message',
                            'type': 'ir.actions.act_window',
                            'view_mode': 'form',
                            'res_model': 'message.wizard',
                            # pass the id
                            'res_id': message_id.id,
                            'target': 'new'
                        }


        except Exception as e:
            raise ValidationError("Error: %s" % str(e))

    def send_notification(self):
        user_ids = self.env['res.partner'].sudo().search([('id', '=', self.claim_onemany_id.claim_id.clientname.id)], limit=1)
        print(user_ids,"GGGGGGGGGGGGG")
        datas = self.env['res.users'].sudo().search([('partner_id', '=', int(user_ids.id))], limit=1)
        if datas.id is False:
            raise UserError(_('Please create the User."'+str(self.claim_onemany_id.claim_id.clientname.name)+'"'))
        else:
            data_message="Dear "+str(self.claim_onemany_id.claim_id.clientname.name)+", your  "+str(self.claim_onemany_id.claim_ticket.name1)+"  is due for renewal on "+str(self.claim_onemany_id.claim_id.expiry)+". We have forwarded you the reminder at the registered email id, our RM will get in touch with you soon Regards Team Bimabachat"
            header = {"Content-Type": "application/json; charset=utf-8",
                      "Authorization": "Basic AAAA2F4_NL4:APA91bFEyx8QEcQLuwPe7r_sv6jp4P1dvhb77Ze0iLFy-daFT9-FzH3ifc8uCAZauREMpjFbDTPEpm2-vTpu-6EqaPV_BBVkv_AlOu-KMUe72MtIfKAWMqEUXYQ3G0ccSgca9sh59PVB"}

            payload = {"app_id": "902d04d1-7157-48a9-8be5-81c0cfcee73e",
                       "include_player_ids": [datas.x_gcm_id],
                       "contents": {"en": data_message},
                       "headings": {"en":self.claim_onemany_id.claim_ticket.name1}
                       }
            req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
            db_name = odoo.tools.config.get('db_name')
            registry = Registry(db_name)
            if not db_name:
                _logger.error(
                    "ERROR: To proper setup OAuth2 and Redis - it's necessary to set the parameter 'db_name' in Odoo config file!")
                print(
                    "ERROR: To proper setup OAuth2 and Token Store - it's necessary to set the parameter 'db_name' in Odoo config file!")
            else:
                # Read system parameters...
                registry = Registry(db_name)
                with registry.cursor() as cr:
                    cr.execute("Insert into apinotification_apinotification (user_id,model_name,model_id,create_date,message,image,title,due_date) values('" + str(
                            datas.id) + "','project.issue','" + str(self.id) + "','" + str(self.create_date) + "','" + str(data_message) + "','https://bimabachat.in/web/static/src/img/logo-bima-bachat.png','"+str(self.claim_onemany_id.claim_ticket.name1)+"','"+str(self.claim_onemany_id.claim_id.expiry)+"')")
                    message_id = self.env['message.wizard'].sudo().create({'text': "Sent Successfully"})
                    return {
                        'name': 'Message',
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'message.wizard',
                        # pass the id
                        'res_id': message_id.id,
                        'target': 'new'
                    }

    def _compute_lines(self):
        print("LINESS")
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])
            for line_rec in first_line_rec.claim_onemany_id.claim_onemany_id:
                line_rec.line_no = line_num
                line_num += 1

    @api.onchange('claim_type','claim_status')
    @api.depends('claim_onemany_id.claim_type','claim_status')
    def _compute_amount(self):
        print("TESSaaaaaaaaaaaaaaaaaaaaaTTSS")
        for i in self:
            print (i.claim_onemany_id.claim_type.id,"IDDDD")
            if i.claim_type.id == 547:
                res = {}
                locations = self.env['infodata'].search([('name', '=', 97)])
                temp = []
                for i in locations:
                    temp.append(i.infosubdata.name)
                res['domain'] = ({'claim_status': [('name', 'in', temp)]})
                return res
            elif i.claim_type.id == 548:
                res1 = {}
                locations = self.env['infodata'].search([('name', '=', 62)])
                tempx = []
                for i in locations:
                    tempx.append(i.infosubdata.name)
                res1['domain'] = ({'claim_status': [('name', 'in', tempx)]})
                return res1
            else:
                res1={}
                res1['domain'] = ({'claim_status': [('name', 'in', [])]})
                return res1

    @api.onchange('claim_status')
    def _compute_amountss(self):
        if self.claim_status:
            res = {}
            locations = self.env['infosubdatadropdown'].search([('info_sub_name', '=', self.claim_status.id)])
            temps = []
            for i in locations:
                temps.append(i.id)
            res['domain'] = ({'claim_sub_status': [('id', 'in', temps)]})
            return res

class Generate_register_sno(models.Model):
    _name='generate_register_sno'

    generate_id =fields.Many2one('policytransaction',ondelete='cascade', index=True)
    name = fields.Char(default="NEW")

    @api.model
    def create(self, vals):
        if vals.get('name', 'NEW') == 'NEW':
            vals['name'] = self.env['ir.sequence'].next_by_code('generate_register_sno') or '/'
        data = super(Generate_register_sno, self).create(vals)
        return data
    



