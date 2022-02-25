from odoo import models, fields, api,_
from datetime import datetime

from odoo.exceptions import ValidationError


class cdaccount1(models.Model):
    _name = 'cdac'

    brokername = fields.Many2one('res.company', string="Broker name", default=lambda self: self.env.user.company_id.id,required=True)
    location_id = fields.Many2one('clickbima.clickbima',string="Location",
                               default=lambda self: self.env['clickbima.clickbima'].search([('start_active', '=',True)],limit=1).id,required=True)
    # fy = fields.Many2one('fiscalyear', string="FY")
    fy = fields.Many2one('fyyear', string="F.Y", default=lambda self: self.env['fyyear'].search([('ex_active', '=',True)],limit=1).id)
    clientname12 = fields.Many2many('res.partner', string="Client Name",domain="[('x_cilent','=',True)]",required=True)
    groupname23 = fields.Char(string="Group Name")
    # pointofscale = fields.Char(string="Point Of Scale")
    insurername121 = fields.Many2one('res.partner',string="Insurer Name",required=True,domain=[('customer','=',True),('is_company','=',True)])
    insurerbranch22 = fields.Many2one('insurerbranch',string="Insurer Branch", required=True)
    segment = fields.Many2many('category.category',required=True)
    # name = fields.Char(string="Id", default="New")
    date = fields.Date(string="Date", default=datetime.today())
    name = fields.Char(string="CD A/C No.", size=25,required=True)
    baldate = fields.Date(string="Closing Balance Date",compute="closing_balance_date_date",store=True)
    openbaldate = fields.Date(string="Opening Balance Date")
    accbal = fields.Float(string="Opening Balance")
    closing_balance =fields.Float(string="Closing Balance",readonly=True,compute="_closing_balance_add")
    adddetails = fields.One2many('ads1.ads1', 'ads12')
    totalcr = fields.Float(string="Total Credit",readonly=True,compute='_name_calculation_credit',store=True)
    totaldr = fields.Float(string="Total Debit",readonly=True,compute='_name_calculation_credit',store=True)
    clbalance = fields.Float()
    startdate = fields.Date()
    endate = fields.Date()

    @api.depends('adddetails')
    def closing_balance_date_date(self):
        for i in self:
            for z in i.adddetails:
                i.baldate =z.date
    @api.multi
    @api.onchange('clientname12')
    def _onchange_partner_id_values(self):
        for i in self:
            client =i.clientname12
            for j in client:
                self.groupname23 = j.parent_id.name

    @api.depends('baldate', 'totalcr', 'totaldr','accbal')
    # @api.onchange('accbal','totalcr','totaldr','closing_balance')
    def _closing_balance_add(self):
        for i in self:
            i.closing_balance =i.accbal+i.totalcr+i.totaldr

    @api.depends('baldate','totalcr','totaldr')
    @api.onchange('adddetails')
    def _name_calculation_credit(self):
        sum = 0
        sum1=0
        for z  in self:
            for i in z.adddetails:
                if i.mode1.name !='CD A/c':
                    sum = sum + i.amount
                    z.totalcr = sum
                    print("1", i.amount)
                else:
                    print("2",i.amount)
                    sum1 = sum1 + i.amount
                    z.totaldr = sum1
    # @api.depends('baldate', 'totalcr', 'totaldr')
    # @api.onchange('adddetails')
    # def _name_calculation_debit(self):
    #     sum = 0
    #     for z in self:
    #         for i in z.adddetails:
    #
    #             else:
    #                 pass

    # @api.onchange('adddetails')
    # def _onchange_partner_id_amount(self):
    #     """ returns the new values when partner_id has changed """
    #     for i in self.adddetails:
    #         print (i, 'i')

    # @api.depends('accbal', 'totalcr', 'totaldr', 'clbalance')
    # def _compute_display_name12(self):
    #     clbalance = self.accbal + self.totalcr
    #     self.clbalance = clbalance - self.totaldr


    # @api.onchange('clientname12')
    # def _onchange_partner_id_values11(self):
    #     client22 = self.clientname12
    #     self.groupname23 = client22.company_name

    @api.multi
    @api.onchange('insurername121')
    def _compute_info_insurerbranch(self):
        res = {}
        temp1 = []
        locations = self.env['insurer'].search([('name', '=', self.insurername121.id)])
        temp = []
        for i in locations:
            temp.append(i.branch.id)
        res['domain'] = ({'insurerbranch22': [('id', 'in', temp)]})
        return res

    @api.model
    def create(self,vals):
        data=super(cdaccount1, self).create(vals)
        # if data.adddetails:
        #     for i in data.adddetails:
        #         data.write({"baldate": i.date})
        #     return data
        # else:
        return data

    @api.multi
    def write(self, vals):
        # print(vals,"ertyu")
        # date=''
        # if self.adddetails:
        #     for i in self.adddetails:
        #         date= i.date
        #     vals['baldate']=date
        #     return super(cdaccount1, self).write(vals)
        # else:
        return super(cdaccount1, self).write(vals)


class Res(models.Model):
    _name = 'ads1.ads1'

    name = fields.Many2one('cdac',index=True)
    ads12 = fields.Many2one('cdac',ondelete='cascade', index=True)
    mode = fields.Many2one('infotype.infotype', string="Mode",
                           default=lambda self: self.env['infotype.infotype'].search([('name', '=', 'Mode of Payment')]))
    mode1 = fields.Many2one('subdata.subdata')
    checkdd = fields.Char()
    amount = fields.Float()
    bankpy = fields.Many2one('infotype.infotype',default=lambda self: self.env['infotype.infotype'].search([('name', '=', 47)]).id)
    bankpy1 = fields.Many2one('subdata.subdata')
    bankbranch = fields.Char(string="Bank Branch")
    dated = fields.Date()
    others_mode_payment = fields.Many2one('subdata.subdata', string="Other Mode")
    pymtdesc = fields.Char()
    rectno = fields.Char()
    rectdate = fields.Date()
    remarks = fields.Char()
    name1 = fields.Char(string="Id", default="Credit")
    date = fields.Date(string="Date", default=datetime.today())
    line_no = fields.Integer(compute='_compute_lines')
    insurername = fields.Many2one('res.partner', string="Insurer Name",domain=[('customer', '=', True), ('is_company', '=', True)])
    insurerbranch = fields.Many2one('insurerbranch', string="Insurer Branch")
    location = fields.Many2one('clickbima.clickbima', string="Location",
                               default=lambda self: self.env['clickbima.clickbima'].search([('start_active', '=', True)], limit=1).id)
    # clientname = fields.Many2one('res.partner', string="Client Name")
    clientname = fields.Many2one('res.partner', string="Client Name", domain="[('x_client','=',True)]")



    @api.onchange('mode1')
    def mode_change(self):
        if self.mode1.id==109:
            print('aman')
            res = {}
            infoname = self.mode.name
            locations = self.env['infodata'].search([('name', '=', 88)])
            # print (locations.name)
            temp = []
            for i in locations:
                temp.append(i.infosubdata.id)

            res['domain'] = ({'others_mode_payment': [('id', 'in' , temp)]})
            return res
        else:
            pass

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
    @api.onchange ('location', 'insurerbranch', 'insurername', 'clientname')
    def onchange_account(self):
        res = {}
        temp = []
        for z in self:
            self.insurerbranch = z.ads12.insurerbranch22.id,
            self.insurername = z.ads12.insurername121.id,
            self.clientname = z.ads12.clientname12.id,
            locations = self.env['cdac'].search(
                [('insurername121', '=', z.ads12.insurername121.id), ('insurerbranch22', '=', z.ads12.insurerbranch22.id),
                 ('clientname12', '=', z.ads12.clientname12.id)])
            print(locations, "LOC")
            for i in locations:
                temp.append(i.id)
        res['domain'] = ({'name': [('id', 'in', temp)]})
        return res



    def _compute_lines(self):
        line_num = 1
        if self.ids:
            first_line_rec = self.browse(self.ids[0])
            for line_rec in first_line_rec.ads12.adddetails:
                line_rec.line_no = line_num
                line_num += 1
                first_line_rec.ads12.baldate=line_rec.date


    @api.model
    def create(self, vals):
        if vals.get('name1', 'Credit') == 'Credit':
            vals['name1'] = self.env['ir.sequence'].next_by_code('cdac') or '/'
        return super(Res, self).create(vals)

    @api.multi
    @api.onchange('mode')
    def _compute_info_name_mode_bank12(self):
        print ('aman')
        res = {}
        infoname = self.mode.name
        locations = self.env['infodata'].search([('name', '=', infoname)])
        # print (locations.name)
        temp = []
        for i in locations:
            temp.append(i.infosubdata.name)

        res['domain'] = ({'mode1': [('name', '=', temp)]})
        return res

    # @api.multi
    # @api.onchange('bankpy')
    # def _compute_info_name_bank32(self):
    #     print ('aman')
    #     res = {}
    #     infoname = self.bankpy.name
    #     locations = self.env['infodata'].search([('name', '=', infoname)])
    #     # print (locations.name)
    #     temp = []
    #     for i in locations:
    #         temp.append(i.infosubdata.name)
    #
    #     res['domain'] = ({'bankpy1': [('name', '=', temp)]})
    #     return res

    @api.multi
    @api.onchange('bankpy1')
    def compute_bankpy1(self):
        res = {}
        locations = self.env['infodata'].search([('name', '=', 47)])
        temp = []
        for i in locations:
            temp.append(i.infosubdata.id)
        res['domain'] = ({'bankpy1': [('id', 'in', temp)]})
        return res

    # @api.onchange('amount')
    # def _onchange_partner_id_amount(self):
    #     """ returns the new values when partner_id has changed """
    #
    #     for move in self:
    #         print(move,'move')
    #
    #         for i in move:
    #             print (i,'i')
    #             print(i.amount,'iname')
    #             # i.amount += i.amount
    #             print (i.amount)
    #             i.ads12.baldate = i.date
                # print(i.ads12.baldate,"iamount")


