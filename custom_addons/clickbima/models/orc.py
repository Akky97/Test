from odoo import models, fields, api,_
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from odoo.exceptions import ValidationError
import datetime
import calendar
from odoo import exceptions
from odoo.modules.registry import Registry
import odoo
import logging
import json
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class orc1(models.Model):
    _name = 'orc'
    _order = 'insurername asc'

    category = fields.Many2one('category.category',required=True)
    subcategory = fields.Many2one('subcategory.subcategory',required=True)
    insurername = fields.Many2one('res.partner', string="Insurer Name", required=True,domain=[('customer', '=', True),('is_company', '=', True)])
    fdate = fields.Date(string="From Date",required=True)
    tdate = fields.Date(string="To Date",required=True)
    rate = fields.Float(string="Rate (%)", required=True)
    remark = fields.Text(string="Remarks",required=True)
    check_edit = fields.Boolean(string='Edit Check', compute='_compute_data',default=False)



    @api.multi
    @api.constrains('fdate', 'tdate')
    def date_constrains(self):
        if self.fdate:
            if self.fdate >= self.tdate:
                raise ValidationError('Sorry, To Date Must be greater Than From Date...')
            else:
                pass

    @api.multi
    @api.onchange('category')
    def _compute_info_catidra(self):
        res = {}
        temp1 = []
        for i in self.category:
            temp1.append(i.name)
        locations = self.env['subcategory.subcategory'].search([('x_category', '=', temp1)])
        temp = []
        for i in locations:
            temp.append(i.id)
        res['domain'] = ({'subcategory': [('id', 'in', temp)]})
        return res

    @api.multi
    @api.onchange('subcategory')
    def _compute_date(self):
        if self.subcategory:
            date = {}
            temp=[]
            iname = self.env['orc'].search([('category', '=', self.category.id),
                                             ('subcategory','=',self.subcategory.id)],
                                             order='create_date desc',limit=1)
            if iname:
                for i in iname:
                    temp.append(i.tdate)
                if len(temp) != 0:
                    from datetime import datetime
                    from dateutil.relativedelta import relativedelta
                    date_format = "%Y-%m-%d"
                    current_date = datetime.strptime(str(temp[0]), date_format)
                    expiry_date = current_date + timedelta(days=+1)
                    self.fdate = expiry_date
                else:
                    self.fdate = ""
                date['domain'] = ({'fdate': [(temp)]})
                return date
            else:
                self.fdate = ""

    @api.depends('subcategory')
    def _compute_data(self):
        for i in self:
            data = self.env['orc'].search([('insurername','=',i.insurername.id),('category', '=', i.category.id),
                                            ('subcategory','=',i.subcategory.id)],order='create_date desc')
            ids=[]
            for i in data:
                ids.append(i.id)
            number = len(ids)
            if number >1:
                largestnumber = self.largest(ids,number)
                if len(ids) == 1:
                    i.check_edit = False
                else:
                    for k in ids:
                        if k < largestnumber:
                            data = self.env['orc'].search([('id','=',k)])
                            print ("2")
                            data.check_edit =True
                        else:
                            i.check_edit =False

    def largest(self,arr, n):
        # Initialize maximum element
        max = arr[0]
        # Traverse array elements from second
        # and compare every element with
        # current max
        for i in range(1, n):
            if arr[i] > max:
                max = arr[i]
        return max



    @api.multi
    @api.model
    def write(self, vals):
        if self.fdate:
            if self.fdate >= self.tdate:
                raise ValidationError('Sorry, To Date Must be greater Than From Date...')
            else:
                print (vals,"vals>>>>>>>>>>>>>>>>>>>>>>>.")
                iname = self.env['orc'].search([('category', '=', self.category.id),
                         ('subcategory', '=', self.subcategory.id),('insurername','=',self.insurername.id)], order='create_date desc', limit=1)
                if iname:
                    # vals['tdate'] = self.tdate
                    vals['fdate'] = self.fdate
                    vals['category'] = self.category.id
                    vals['subcategory'] = self.subcategory.id
                    vals['insurername'] = self.insurername.id
                    vals['rate'] = self.rate
        return super(orc1, self).write(vals)



    @api.model
    def create(self, vals):
        temp = []
        iname = self.env['orc'].search([('category', '=', vals.get('category')),
                                        ('subcategory', '=', vals.get('subcategory')),('insurername','=',vals.get('insurername'))],
                                       order='create_date desc', limit=1)
        print (iname,"iname")
        if iname:
            for i in iname:
                temp.append(i.tdate)
            if len(temp) != 0:
                from datetime import datetime
                from dateutil.relativedelta import relativedelta
                date_format = "%Y-%m-%d"
                current_date = datetime.strptime(str(temp[0]), date_format)
                expiry_date = current_date + timedelta(days=+1)
                fdate = expiry_date
                vals['fdate'] = fdate
                category = vals.get('category')
                insurername = vals.get('insurername')
                subcategory = vals.get('subcategory')
                tdate = vals.get('tdate')
                rate = vals.get('rate')
                vals = {"fdate": fdate,
                        "category": category,
                        "subcategory": subcategory,
                        "insurername":insurername,
                        "tdate": tdate,
                        "rate": rate}
                print vals, "VLAUESS"
            else:
                fdate = vals.get('fdate')
                category = vals.get('category')
                subcategory = vals.get('subcategory')
                tdate = vals.get('tdate')
                rate = vals.get('rate')
                insurername = vals.get('insurername')
                vals = {"fdate": fdate,
                        "category": category,
                        "subcategory": subcategory,
                        "tdate": tdate,
                        "insurername":insurername,
                        "rate": rate}
                print vals, "VLAUESS"



        return super(orc1, self).create(vals)







    #
    # @api.model
    # def create(self, vals):
    #     db_name = odoo.tools.config.get('db_name')
    #     registry = Registry(db_name)
    #     category = vals.get('category')
    #     insurername = vals.get('insurername')
    #     subcategory = vals.get('subcategory')
    #     fdate = vals.get('fdate')
    #     tdate = vals.get('tdate')
    #     datas = self.env['orc'].search([('subcategory', '=', subcategory),('category', '=', category), ('insurername', '=', insurername),('fdate', '=', fdate),('tdate', '=', tdate)])
    #     print(datas, "DATAs")
    #     result = super(orc1, self).create(vals)
    #     if datas:
    #         print("qwertyui")
    #         raise UserError(_("Record Already Exist"))
    #     else:
    #         return result
    #
    # @api.multi
    # @api.constrains('fdate', 'tdate')
    # def date_constrains(self):
    #
    #     for rec in self:
    #
    #         if rec.tdate <= rec.fdate:
    #             raise ValidationError(_('Sorry, To Date Must be greater Than From Date...'))
    #
    # @api.multi
    # @api.onchange('category')
    # def _compute_info_catidra(self):
    #     res = {}
    #     temp1 = []
    #     for i in self.category:
    #         temp1.append(i.name)
    #     locations = self.env['subcategory.subcategory'].search([('x_category', '=', temp1)])
    #     temp = []
    #     for i in locations:
    #         temp.append(i.id)
    #     res['domain'] = ({'subcategory': [('id', 'in', temp)]})
    #     return res
    #
    # @api.multi
    # @api.onchange('insurername')
    # def _compute_date(self):
    #     if self.insurername:
    #         date = {}
    #         temp = []
    #         iname = self.env['orc'].search([('category', '=', self.category.id),
    #                                          ('subcategory', '=', self.subcategory.id),
    #                                          ('insurername', '=', self.insurername.id)],
    #                                         order='create_date desc', limit=1)
    #         if iname:
    #             for i in iname:
    #                 temp.append(i.tdate)
    #             print (temp,"TEMPAAA")
    #             if len(temp) != 0:
    #                 from datetime import datetime
    #                 from dateutil.relativedelta import relativedelta
    #                 date_format = "%Y-%m-%d"
    #                 current_date = datetime.strptime(str(temp[0]), date_format)
    #                 expiry_date = current_date + timedelta(days=+1)
    #                 self.fdate=expiry_date
    #             else:
    #                 self.fdate = ""
    #             date['domain'] = ({'fdate': [(temp)]})
    #             return date
    #         else:
    #             self.fdate = ""
    #
    # # @api.multi
    # @api.depends('insurername','subcategory','category')
    # def _compute_data(self):
    #     self.check_edit=False
    #     for i in self:
    #         data = self.env['orc'].search([('category', '=', i.category.id),
    #                                         ('subcategory', '=', i.subcategory.id),
    #                                        ('insurername','=',i.insurername.id)],order='create_date desc')
    #         ids = []
    #         for i in data:
    #             ids.append(i.id)
    #         print (ids,"IDSS")
    #         number = len(ids)
    #         print (number,"NUMBHER")
    #         if number > 1:
    #             largestnumber = self.largest(ids, number)
    #             if len(ids) == 1:
    #                 i.check_edit = False
    #                 print ("1")
    #             else:
    #                 print("2")
    #                 for k in ids:
    #                     if k < largestnumber:
    #                         data = self.env['orc'].search([('id', '=', k)])
    #                         print ("2")
    #                         data.check_edit = True
    #                     else:
    #                         i.check_edit = False
    #
    # def largest(self, arr, n):
    #     max = arr[0]
    #     for i in range(1, n):
    #         if arr[i] > max:
    #             max = arr[i]
    #     return max
    #
    # @api.multi
    # def write(self, vals):
    #     temp = []
    #     iname = self.env['orc'].search([('category', '=', self.category.id),
    #                                     ('subcategory', '=', self.subcategory.id),
    #                                     ('insurername', '=', self.insurername.id)],
    #                                    order='create_date desc')
    #     if iname:
    #         for i in iname:
    #             temp.append(i.tdate)
    #         if len(temp) != 0:
    #             from datetime import datetime
    #             from dateutil.relativedelta import relativedelta
    #             date_format = "%Y-%m-%d"
    #             current_date = datetime.strptime(str(temp[0]), date_format)
    #             # expiry_date = current_date + timedelta(days=+1)
    #             # fdate = expiry_date
    #             vals['fdate'] = self.fdate
    #
    #             category = self.category.id
    #             subcategory = self.subcategory.id
    #             insurername = self.insurername.id
    #             vals['tdate'] = self.tdate
    #             # tdate = vals['tdate']
    #             rate = self.rate
    #             remark = self.remark
    #             vals = {"category": category,
    #                     "subcategory": subcategory,
    #                     "insurername": insurername,
    #                     # "tdate": self.tdate,
    #                     "rate": rate,
    #                     "remark": remark}
    #
    #             # print vals, "VLAUESS"
    #
    #     else:
    #         fdate = self.fdate
    #         category = self.category.id
    #         subcategory = self.subcategory.id
    #         insurername = self.insurername.id
    #         tdate = self.tdate
    #         rate = self.rate
    #         remark = self.remark
    #         vals = {"fdate": fdate, "category": category,
    #                 "subcategory": subcategory,
    #                 "insurername": insurername,
    #                 "tdate": tdate,
    #                 "rate": rate,
    #                 "remark": remark}
    #
    #         # print vals, "VLAUESS"
    #
    #     return super(orc1, self).write(vals)
    #
    #
    # @api.model
    # def create(self,vals):
    #     temp=[]
    #     iname = self.env['orc'].search([('category', '=', vals.get('category')),
    #                                     ('subcategory', '=', vals.get('subcategory.id')),
    #                                     ('insurername', '=', vals.get('insurername'))],
    #                                    order='create_date desc')
    #     if iname:
    #         for i in iname:
    #             temp.append(i.tdate)
    #         if len(temp) != 0:
    #             from datetime import datetime
    #             from dateutil.relativedelta import relativedelta
    #             date_format = "%Y-%m-%d"
    #             current_date = datetime.strptime(str(temp[0]), date_format)
    #             expiry_date = current_date + timedelta(days=+1)
    #             fdate = expiry_date
    #             vals['fdate'] = fdate
    #             category = vals.get('category')
    #             subcategory = vals.get('subcategory')
    #             insurername = vals.get('insurername')
    #             tdate = vals.get('tdate')
    #             rate = vals.get('rate')
    #             remark = vals.get('remark')
    #             vals = {"category": category,
    #                     "subcategory": subcategory,
    #                     "insurername": insurername,
    #                     "tdate": tdate,
    #                     "rate": rate,
    #                     "remark": remark}
    #
    #             print vals, "VLAUESS"
    #
    #     else:
    #         fdate=vals.get('fdate')
    #         category = vals.get('category')
    #         subcategory = vals.get('subcategory')
    #         insurername = vals.get('insurername')
    #         tdate = vals.get('tdate')
    #         rate = vals.get('rate')
    #         remark = vals.get('remark')
    #         vals = {"fdate": fdate, "category": category,
    #                 "subcategory": subcategory,
    #                 "insurername": insurername,
    #                 "tdate": tdate,
    #                 "rate": rate,
    #                 "remark": remark}
    #
    #         print vals, "VLAUESS"
    #
    #     return super(orc1, self).create(vals)
    #
    # # @api.onchange('insurername')
    # # def insurer_change(self):
    # #     self.check_edit = False
    # #     if self.insurername:
    # #         data = self.env['orc'].search([('category', '=', self.category.id),
    # #                                         ('subcategory', '=', self.subcategory.id),('insurername','=',self.insurername.id)],
    # #                                        order='create_date desc', limit=1)
    # #         print data, "DATA"
    # #         if data:
    # #             self.check_edit = True
    # #         if not data:
    # #             self.check_edit = False
    # #     if self.insurername == False:
    # #         self.check_edit = False
    #
