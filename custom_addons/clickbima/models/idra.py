from odoo.exceptions import ValidationError
from odoo import exceptions
from odoo import models, fields, api,_
from odoo.modules.registry import Registry
import odoo
import logging
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import datetime
import calendar
import json
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class idra1(models.Model):
    _name = 'idra'
    _order = 'category asc'

    category = fields.Many2one('category.category',required=True)
    subcategory = fields.Many2one('subcategory.subcategory',required=True)
    fdate = fields.Date(string="From Date",required=True)
    tdate = fields.Date(string="To Date",required=True)
    name = fields.Float(string="Rate (%)",required=True)
    check_edit=fields.Boolean(string='Edit Check',compute='_compute_data')

    # @api.model
    # def create(self, vals):
    #     db_name = odoo.tools.config.get('db_name')
    #     registry = Registry(db_name)
    #     category = vals.get('category')
    #     subcategory = vals.get('subcategory')
    #     fdate = vals.get('fdate')
    #     tdate = vals.get('tdate')
    #     datas = self.env['idra'].search([('tdate', '=', tdate), ('fdate', '=', fdate), ('subcategory', '=', subcategory), (' category', '=',  category)])
    #     print(datas, "DATAs")
    #     result = super(idra1, self).create(vals)
    #     if datas:
    #         print("qwertyui")
    #         raise UserError(_("Record Already Exist"))
    #     else:
    #         return result

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
            iname = self.env['idra'].search([('category', '=', self.category.id),
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
            data = self.env['idra'].search([('category', '=', i.category.id),
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
                            data = self.env['idra'].search([('id','=',k)])
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
                iname = self.env['idra'].search([('category', '=', self.category.id),
                         ('subcategory', '=', self.subcategory.id)], order='create_date desc', limit=1)
                if iname:

                    # vals['tdate'] = self.tdate
                    vals['fdate'] = self.fdate
                    vals['category'] = self.category.id
                    vals['subcategory'] = self.subcategory.id
                    vals['name'] = self.name


        # temp = []
        # iname = self.env['idra'].search([('category', '=', self.category.id),
        #                                  ('subcategory', '=', self.subcategory.id)], order='create_date desc', limit=1)
        # if iname:
            # print (iname,"iname>>>>>>>>>>>...")
            # for i in iname:
            #     temp.append(i.tdate)
            # if len(temp) != 0:
            #     from datetime import datetime
            #     from dateutil.relativedelta import relativedelta
            #     date_format = "%Y-%m-%d"
            #     current_date = datetime.strptime(str(temp[0]), date_format)
                # expiry_date = current_date + timedelta(days=+1)
                # fdate = expiry_date
                # vals['fdate'] = self.fdate
                # category = self.category.id
                # subcategory = self.subcategory.id
                # tdate = self.tdate
                # name = self.name

                # print vals, "VLAUESS"
            # else:
            #     fdate = self.fdate
            #     category = self.category.id
            #     subcategory = self.subcategory.id
            #     # tdate = self.tdate
            #     name = self.name
            #     vals = {"fdate": fdate,
            #             "category": category,
            #             "subcategory": subcategory,
            #             # "tdate": tdate,
            #             "name": name}
            #     # print vals, "VLAUESS"
        return super(idra1, self).write(vals)



    @api.model
    def create(self, vals):
        temp = []
        iname = self.env['idra'].search([('category', '=', vals.get('category')),
                                        ('subcategory', '=', vals.get('subcategory'))],
                                       order='create_date desc', limit=1)
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
                subcategory = vals.get('subcategory')
                tdate = vals.get('tdate')
                name = vals.get('name')
                vals = {"fdate": fdate,
                        "category": category,
                        "subcategory": subcategory,
                        "tdate": tdate,
                        "name": name}
                print vals, "VLAUESS"
            else:
                fdate = vals.get('fdate')
                category = vals.get('category')
                subcategory = vals.get('subcategory')
                tdate = vals.get('tdate')
                name = vals.get('name')
                vals = {"fdate": fdate,
                        "category": category,
                        "subcategory": subcategory,
                        "tdate": tdate,
                        "name": name}
                print vals, "VLAUESS"



        return super(idra1, self).create(vals)

    #
    #
    # @api.onchange('subcategory')
    # def subcategory_change(self):
    #     self.check_edit = False
    #     if self.subcategory:
    #         data = self.env['idra'].search([('category', '=', self.category.id),
    #                                        ('subcategory', '=', self.subcategory.id)],
    #                                       order='create_date desc', limit=1)
    #         print data, "DATA"
    #         if data:
    #             self.check_edit = True
    #         if not data:
    #             self.check_edit = False





