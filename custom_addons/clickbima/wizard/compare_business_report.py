from odoo import api, fields, models, _
import odoo
from odoo.http import request, content_disposition
from odoo.service import model
from odoo.tools.misc import xlwt
from odoo.exceptions import UserError, AccessError
import io
import base64
import operator
import itertools
import time
from datetime import date
from odoo.modules.registry import Registry
from datetime import timedelta
import os
import pandas as pd
import numpy as np
# from pandas.tests.groupby.conftest import ts
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, StringIO, cStringIO


class Comparebusinessreport(models.TransientModel):
    _name = "comparebusiness.report"
    _description = "Business Comparison Report"

    date_from = fields.Date('From Date')
    pre_date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    pre_date_to = fields.Date('To Date')
    monthly = fields.Selection([('monthly', 'Monthly'), ('quatar', 'Quarterly'), ('yearly', 'Yearly')],
                               default='monthly',string="Period Type")
    quarter = fields.Selection([('q1', 'Quarter 1'), ('q2', 'Quarter 2'), ('q3', 'Quarter 3'), ('q4', 'Quarter 4')],
                               string='Quarter')
    groupby = fields.Selection([('create_date', 'All'), ('category', 'Category')], default='category',
                               string="Group BY")
    filterby = fields.Selection([('all', 'All'), ('category', 'Category')], default='all', string="Filter BY")
    location = fields.Selection([('9', 'Chandigarh'), ('8', 'Ludhiana'), ('7', 'New Delhi'), ('all', 'All')],
                                default='all', string="Location")
    fiscal_year = fields.Many2one('fyyear', string="Financial Year",
                                  default=lambda self: self.env['fyyear'].search([('ex_active', '=', True)],
                                                                                 limit=1).id)
    months = fields.Selection(
        [('01-01', 'January'), ('01-02', 'February'), ('01-03', 'March'), ('01-04', 'April'), ('01-05', 'May'),
         ('01-06', 'June'),
         ('01-07', 'July'), ('01-08', 'August'), ('01-09', 'September'), ('01-10', 'October'), ('01-11', 'November'),
         ('01-12', 'December')])
    category = fields.Many2one('category.category', string="Category")
    start_year = fields.Char()
    end_year = fields.Char()

    @api.multi
    @api.onchange('category')
    def _compute_category_id(self):
        cat_id = self.category.id

    import odoo
    import datetime
    now1 = datetime.datetime.now()

    @api.onchange('monthly', 'months', 'fiscal_year')
    def onchange_monthly(self):
        import datetime
        if self.monthly and self.fiscal_year:
            end_year1 = self.fiscal_year.date_end
            my_date1 = datetime.datetime.strptime(end_year1, "%Y-%m-%d")
            end_year = my_date1.year
            start_year1 = self.fiscal_year.date_start
            prev_date_start = datetime.datetime.strptime(start_year1, '%Y-%m-%d') - timedelta(365)
            # print(prev_date_start, "ssssssssssssssssss")
            prev_date_end = datetime.datetime.strptime(start_year1, '%Y-%m-%d') - timedelta(1)
            # print(prev_date_end, "eeeeeeeeeeeeeeeeee")
            my_date = datetime.datetime.strptime(start_year1, "%Y-%m-%d")
            start_year = my_date.year

            # prev_date_start = datetime.datetime.strptime(start_year1, '%Y-%m-%d') - timedelta(365)
            prev_start_year = prev_date_start.year
            # prev_date_end = datetime.datetime.strptime(start_year1, '%Y-%m-%d') - timedelta(1)
            prev_end_year = prev_date_end.year
            # predate = lines.date_from.split("-")
            # prev_sdate = '-' + date[1] + '-' + date[2]
            # prev_date1 = lines.date_to.split("-")
            # prev_edate = '-' + date1[1] + '-' + date1[2]
            # print(prev_start_year, prev_end_year, predate, prev_sdate, prev_date1, prev_edate, "valuess")

            if (self.monthly == 'yearly'):
                self.date_from = str(self.fiscal_year.date_start)
                self.date_to = str(self.fiscal_year.date_end)
            elif (self.monthly == 'monthly'):
                if self.months == '01-01':
                    print("INSIDE THE MONTHLY SECTORR")
                    self.start_year = start_year
                    self.end_year = end_year
                    jan_start = str(end_year) + str('-01-01')
                    prev_jan_start = str(prev_start_year) + str('-01-01')
                    jan_end = str(end_year) + str('-01-31')
                    prev_jan_end = str(prev_start_year) + str('-01-31')
                    self.date_from = str(jan_start)
                    self.pre_date_from = str(prev_jan_start)
                    self.date_to = str(jan_end)
                    self.pre_date_to = str(prev_jan_end)
                    print(self.date_to,self.pre_date_to,self.pre_date_from,prev_jan_end)

                if self.months == '01-02':
                    self.start_year = start_year
                    self.end_year = end_year
                    feb_start = str(end_year) + str('-02-01')
                    prev_feb_start = str(prev_start_year) + str('-02-01')
                    feb_end = str(prev_date_start) + str('-02-28')
                    prev_feb_end = str(prev_start_year) + str('-02-28')
                    self.date_from = str(feb_start)
                    self.pre_date_from = str(prev_feb_start)
                    self.date_to = str(feb_end)
                    self.pre_date_to = str(prev_feb_end)

                if self.months == '01-03':
                    self.start_year = start_year
                    self.end_year = end_year
                    mar_start = str(end_year) + str('-03-01')
                    prev_mar_start = str(prev_start_year) + str('-03-01')
                    mar_end = str(end_year) + str('-03-31')
                    prev_mar_end = str(prev_start_year) + str('-03-31')
                    self.date_from = str(mar_start)
                    self.pre_date_from = str(prev_mar_start)
                    self.date_to = str(mar_end)
                    self.pre_date_to = str(prev_mar_end)

                if self.months == '01-04':
                    self.start_year = start_year
                    self.end_year = end_year
                    apr_start = str(start_year) + str('-04-01')
                    prev_apr_start = str(prev_start_year) + str('-04-01')
                    apr_end = str(start_year) + str('-04-30')
                    prev_apr_end = str(prev_start_year) + str('-04-30')
                    self.date_from = str(apr_start)
                    self.pre_date_from = str(prev_apr_start)
                    self.pre_date_to = str(prev_apr_end)
                    self.date_to = str(apr_end)

                if self.months == '01-05':
                    self.start_year = start_year
                    self.end_year = end_year
                    may_start = str(start_year) + str('-05-01')
                    prev_may_start = str(prev_start_year) + str('-05-01')
                    may_end = str(start_year) + str('-05-31')
                    prev_may_end = str(prev_start_year) + str('-05-31')
                    self.date_from = str(may_start)
                    self.pre_date_from = str(prev_may_start)
                    self.date_to = str(may_end)
                    self.pre_date_to = str(prev_may_end)

                if self.months == '01-06':
                    self.start_year = start_year
                    self.end_year = end_year
                    june_start = str(start_year) + str('-06-01')
                    prev_june_start = str(prev_start_year) + str('-06-01')
                    june_end = str(start_year) + str('-06-30')
                    prev_june_end = str(prev_start_year) + str('-06-30')
                    self.date_from = str(june_start)
                    self.pre_date_from = str(prev_june_start)
                    self.pre_date_to = str(prev_june_end)
                    self.date_to = str(june_end)

                if self.months == '01-07':
                    self.start_year = start_year
                    self.end_year = end_year
                    jul_start = str(start_year) + str('-07-01')
                    prev_jul_start = str(prev_start_year) + str('-07-01')
                    jul_end = str(start_year) + str('-07-31')
                    prev_jul_end = str(prev_start_year) + str('-07-31')
                    self.date_from = str(jul_start)
                    self.pre_date_from = str(prev_jul_start)
                    self.date_to = str(jul_end)
                    self.pre_date_to = str(prev_jul_end)

                if self.months == '01-08':
                    self.start_year = start_year
                    self.end_year = end_year
                    aug_start = str(start_year) + str('-08-01')
                    prev_aug_start = str(prev_start_year) + str('-08-01')
                    aug_end = str(start_year) + str('-08-31')
                    prev_aug_end = str(prev_start_year) + str('-08-31')
                    self.date_from = str(aug_start)
                    self.pre_date_from = str(prev_aug_start)
                    self.date_to = str(aug_end)
                    self.pre_date_to = str(prev_aug_end)

                if self.months == '01-09':
                    self.start_year = start_year
                    self.end_year = end_year
                    sep_start = str(start_year) + str('-09-01')
                    prev_sep_start = str(prev_start_year) + str('-09-01')
                    sep_end = str(start_year) + str('-09-30')
                    prev_sep_end = str(prev_start_year) + str('-09-30')
                    self.date_from = str(sep_start)
                    self.pre_date_from = str(prev_sep_start)
                    self.date_to = str(sep_end)
                    self.pre_date_to = str(prev_sep_end)

                if self.months == '01-10':
                    self.start_year = start_year
                    self.end_year = end_year
                    oct_start = str(start_year) + str('-10-01')
                    prev_oct_start = str(prev_start_year) + str('-10-01')
                    oct_end = str(start_year) + str('-10-31')
                    prev_oct_end = str(prev_start_year) + str('-10-31')
                    self.date_from = str(oct_start)
                    self.pre_date_from = str(prev_oct_start)
                    self.date_to = str(oct_end)
                    self.pre_date_to = str(prev_oct_end)

                if self.months == '01-11':
                    self.start_year = start_year
                    self.end_year = end_year
                    nov_start = str(start_year) + str('-11-01')
                    prev_nov_start = str(prev_start_year) + str('-11-01')
                    nov_end = str(start_year) + str('-11-30')
                    prev_nov_end = str(prev_start_year) + str('-11-30')
                    self.date_from = str(nov_start)
                    self.pre_date_from = str(prev_nov_start)
                    self.pre_date_to = str(prev_nov_end)
                    self.date_to = str(nov_end)

                if self.months == '01-12':
                    self.start_year = start_year
                    self.end_year = end_year
                    dec_start = str(start_year) + str('-12-01')
                    prev_dec_start = str(prev_start_year) + str('-12-01')
                    dec_end = str(start_year) + str('-12-31')
                    prev_dec_end = str(prev_start_year) + str('-12-31')
                    self.date_from = str(dec_start)
                    self.pre_date_from = str(prev_dec_start)
                    self.date_to = str(dec_end)
                    self.pre_date_to = str(prev_dec_end)
        else:
            pass

    @api.onchange('quarter')
    def onchange_quarter(self):
        import datetime
        if self.quarter:
            end_year1 = self.fiscal_year.date_end
            my_date1 = datetime.datetime.strptime(end_year1, "%Y-%m-%d")
            end_year = my_date1.year
            start_year1 = self.fiscal_year.date_start
            my_date = datetime.datetime.strptime(start_year1, "%Y-%m-%d")
            start_year = my_date.year
            start_year1 = self.fiscal_year.date_start
            prev_date_start = datetime.datetime.strptime(start_year1, '%Y-%m-%d') - timedelta(365)
            prev_date_end = datetime.datetime.strptime(start_year1, '%Y-%m-%d') - timedelta(1)
            prev_start_year = prev_date_start.year
            prev_end_year = prev_date_end.year

            if (self.quarter == 'q1'):
                self.start_year = start_year
                self.end_year = end_year
                q1_start = str(start_year) + str('-04-01')
                pre_q1_start = str(prev_start_year) + str('-04-01')
                q1_end = str(start_year) + str('-06-30')
                pre_q1_end = str(prev_start_year) + str('-06-30')
                self.date_from = str(q1_start)
                self.pre_date_from = str(pre_q1_start)
                self.date_to = str(q1_end)
                self.pre_date_to = str(pre_q1_end)
                print(self.pre_date_to,self.pre_date_from,"TO from")

            elif (self.quarter == 'q2'):
                self.start_year = start_year
                self.end_year = end_year
                q2_start = str(start_year) + str('-07-01')
                pre_q2_start = str(prev_start_year) + str('-07-01')
                q2_end = str(start_year) + str('-09-30')
                pre_q2_end = str(prev_start_year) + str('-09-30')
                self.date_from = str(q2_start)
                self.pre_date_from = str(pre_q2_start)
                self.pre_date_to = str(pre_q2_end)
                self.date_to = str(q2_end)
            elif (self.quarter == 'q3'):
                self.start_year = start_year
                self.end_year = end_year
                q3_start = str(start_year) + str('-10-01')
                pre_q3_start = str(prev_start_year) + str('-10-01')
                q3_end = str(start_year) + str('-12-31')
                pre_q3_end = str(prev_start_year) + str('-12-31')
                self.date_from = str(q3_start)
                self.pre_date_from = str(pre_q3_start)
                self.date_to = str(q3_end)
                self.pre_date_to = str(pre_q3_end)
            elif (self.quarter == 'q4'):
                self.start_year = start_year
                self.end_year = end_year
                q4_start = str(end_year) + str('-01-01')
                pre_q4_start = str(prev_end_year) + str('-01-01')
                q4_end = str(end_year) + str('-03-31')
                pre_q4_end = str(prev_end_year) + str('-03-31')
                self.date_from = str(q4_start)
                self.pre_date_from = str(pre_q4_start)
                self.date_to = str(q4_end)
                self.pre_date_to = str(pre_q4_end)
            else:
                pass

    @api.multi
    def generate_xlsx_report(self):
        data = {}
        data['form'] = self.read([])[0]
        return self.env['report'].get_action(self, report_name='clickbima.compare_report_excel.xlsx', data=data)


from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class GeneralXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, lines):
        import datetime
        end_year1 = lines.fiscal_year.date_end
        my_date1 = datetime.datetime.strptime(end_year1, "%Y-%m-%d")
        end_year = my_date1.year
        start_year1 = lines.fiscal_year.date_start
        my_date = datetime.datetime.strptime(start_year1, "%Y-%m-%d")
        start_year = my_date.year
        date = lines.date_from.split("-")
        start_date = '-' + date[1] + '-' + date[2]
        date1 = lines.date_to.split("-")
        end_date = '-' + date1[1] + '-' + date1[2]
        prev_date_start = datetime.datetime.strptime(start_year1, '%Y-%m-%d') - timedelta(365)
        prev_start_year = prev_date_start.year
        prev_date_end = datetime.datetime.strptime(start_year1, '%Y-%m-%d') - timedelta(1)
        prev_end_year = prev_date_end.year
        predate = lines.date_from.split("-")
        prev_sdate = '-' + date[1] + '-' + date[2]
        prev_date1 = lines.date_to.split("-")
        prev_edate = '-' + date1[1] + '-' + date1[2]
        print(prev_start_year, prev_end_year, predate, prev_sdate, prev_date1, prev_edate, "valuess")


        filtname = ''
        if lines.filterby == 'all':
            filtname = 'All'
        elif lines.filterby == 'category':
            filtname = 'Category'

        loc = ''
        if lines.location == '9':
            loc = 'Chandigarh'
        elif lines.location == '8':
            loc = 'Ludhiana'
        elif lines.location == '7':
            loc = 'New Delhi'
        else:
            loc = 'All'

        quat = ''
        period = ''
        if lines.monthly == 'yearly':
            quat = '(' + str(lines.fiscal_year.date_start) + ' to ' + str(
                lines.fiscal_year.date_end) + ')'
            period = '  Yearly'
            per_date = '  From ' + str(lines.fiscal_year.date_start) + ' To ' + str(
                lines.fiscal_year.date_end)
        elif lines.monthly == 'quatar':
            if lines.quarter == 'q1':
                q1_start = str('01-04-') + str(start_year)
                pre_q1_start = str('01-04-') + str(prev_start_year)
                q1_end = str('30-06-') + str(start_year)
                pre_q1_end = str('30-06-') + str(prev_start_year)
                quat = '(' + str(q1_start) + ' to ' + str(q1_end) + ')'
                pre_quat = '(' + str(q1_start) + ' to ' + str(q1_end) + ')'
                period = '  Quarter (April-June)'
                per_date = '  From ' + str(q1_start) + ' To ' + str(q1_end)
                pre_per_date = '  From ' + str(q1_start) + ' To ' + str(q1_end)
            if lines.quarter == 'q2':
                q2_start = str('01-07-') + str(start_year)
                q2_end = str('30-09-') + str(start_year)
                quat = '(' + str(q2_start) + ' to ' + str(q2_end) + ')'
                period = '  Quarter  (July-September)'
                per_date = '  From ' + str(q2_start) + ' To ' + str(q2_end)
            if lines.quarter == 'q3':
                q3_start = str('01-10-') + str(start_year)
                q3_end = str('31-12-') + str(start_year)
                quat = '(' + str(q3_start) + ' to ' + str(q3_end) + ')'
                period = ' Quarter  (October-December)'
                per_date = ' From ' + str(q3_start) + ' To ' + str(q3_end)
            if lines.quarter == 'q4':
                q4_start = str('01-01-') + str(end_year)
                q4_end = str('31-03-') + str(end_year)
                quat = '(' + str(q4_start) + ' to ' + str(q4_end) + ')'
                period = ' Quarter  (January-March)'
                per_date = ' From ' + str(q4_start) + ' To ' + str(q4_end)
        elif lines.monthly == 'monthly':
            if lines.months == '01-01':
                jan_start = str('01-01-') + str(end_year)
                prev_jan_start = str('01-01-') + str(prev_start_year)
                jan_end = str('31-01-') + str(end_year)
                prev_jan_end = str('31-01-') + str(prev_start_year)
                period = '  Monthly  (January)'
                per_date = '  From ' + str(jan_start) + ' To ' + str(jan_end)
                quat = '(' + str(jan_start) + ' to ' + str(jan_end) + ')'

            if lines.months == '01-02':
                feb_start = str('01-02-') + str(end_year)
                prev_feb_start = str('01-02-') + str(prev_start_year)
                feb_end = str('28-02-') + str(end_year)
                prev_feb_end = str('28-02-') + str(prev_start_year)
                period = '  Monthly  (February)'
                per_date = '  From ' + str(feb_start) + ' To ' + str(feb_end)
                quat = '(' + str(feb_start) + ' to ' + str(feb_end) + ')'
            if lines.months == '01-03':
                mar_start = str('01-03-') + str(end_year)
                prev_mar_start = str('01-03-') + str(prev_start_year)
                mar_end = str('31-03-') + str(end_year)
                prev_mar_end = str('31-03-') + str(prev_start_year)
                period = '  Monthly  (March)'
                per_date = '  From ' + str(mar_start) + ' To ' + str(mar_end)
                quat = '(' + str(mar_start) + ' to ' + str(mar_end) + ')'
            if lines.months == '01-04':
                apr_start = str('01-04-') + str(start_year)
                prev_apr_start = str('01-04-') + str(prev_start_year)
                apr_end = str('30-04-') + str(start_year)
                prev_apr_end = str('30-04-') + str(prev_start_year)
                period = '  Monthly  (April)'
                per_date = '  From ' + str(apr_start) + ' To ' + str(apr_end)
                quat = '(' + str(apr_start) + ' to ' + str(apr_end) + ')'
            if lines.months == '01-05':
                may_start = str('01-05-') + str(start_year)
                prev_may_start = str('01-05-') + str(start_year)
                may_end = str('31-05-') + str(start_year)
                prev_may_end = str('31-05-') + str(start_year)
                period = '  Monthly  (May)'
                per_date = '  From ' + str(may_start) + ' To ' + str(may_end)
                quat = '(' + str(may_start) + ' to ' + str(may_end) + ')'
            if lines.months == '01-06':
                june_start = str('01-06-') + str(start_year)
                prev_june_start = str('01-06-') + str(prev_start_year)
                june_end = str('30-06-') + str(start_year)
                prev_june_end = str('30-06-') + str(prev_start_year)
                period = '  Monthly  (June)'
                per_date = '  From ' + str(june_start) + ' To ' + str(june_end)
                quat = '(' + str(june_start) + ' to ' + str(june_end) + ')'
            if lines.months == '01-07':
                jul_start = str('01-07-') + str(start_year)
                prev_jul_start = str('01-07-') + str(prev_start_year)
                jul_end = str('31-07-') + str(start_year)
                prev_jul_end = str('31-07-') + str(prev_start_year)
                period = '  Monthly  (July)'
                per_date = '  From ' + str(jul_start) + ' To ' + str(jul_end)
                quat = '(' + str(jul_start) + ' to ' + str(jul_end) + ')'
            if lines.months == '01-08':
                aug_start = str('01-08-') + str(start_year)
                prev_aug_start = str('01-08-') + str(prev_start_year)
                aug_end = str('31-08-') + str(start_year)
                prev_aug_end = str('31-08-') + str(prev_start_year)
                period = '  Monthly  (August)'
                per_date = '  From ' + str(aug_start) + ' To ' + str(aug_end)
                quat = '(' + str(aug_start) + ' to ' + str(aug_end) + ')'
            if lines.months == '01-09':
                sep_start = str('01-09-') + str(start_year)
                prev_sep_start = str('01-09-') + str(prev_start_year)
                sep_end = str('30-09-') + str(start_year)
                prev_sep_end = str('30-09-') + str(prev_start_year)
                period = '  Monthly  (September)'
                per_date = '  From ' + str(sep_start) + ' To ' + str(sep_end)
                quat = '(' + str(sep_start) + ' to ' + str(sep_end) + ')'
            if lines.months == '01-10':
                oct_start = str('01-10-') + str(start_year)
                prev_oct_start = str('01-10-') + str(prev_start_year)
                oct_end = str('31-10-') + str(start_year)
                prev_oct_end = str('31-10-') + str(prev_start_year)
                period = '  Monthly  (October)'
                per_date = '  From ' + str(oct_start) + ' To ' + str(oct_end)
                quat = '(' + str(oct_start) + ' to ' + str(oct_end) + ')'
            if lines.months == '01-11':
                nov_start = str('01-11-') + str(start_year)
                prev_nov_start = str('01-11-') + str(prev_start_year)
                nov_end = str('30-11-') + str(start_year)
                prev_nov_end = str('30-11-') + str(prev_start_year)
                period = '  Monthly  (November)'
                per_date = '  From ' + str(nov_start) + ' To ' + str(nov_end)
                quat = '(' + str(nov_start) + ' to ' + str(nov_end) + ')'
            if lines.months == '01-12':
                dec_start = str('01-12-') + str(start_year)
                prev_dec_start = str('01-12-') + str(prev_start_year)
                prev_dec_end = str('31-12-') + str(start_year)
                dec_end = str('31-12-') + str(prev_start_year)
                period = '  Monthly (December)'
                per_date = '  From ' + str(dec_start) + ' To ' + str(dec_end)
                quat = '(' + str(dec_start) + ' to ' + str(dec_end) + ')'
        else:
            pass

        import datetime
        x = datetime.datetime.now()

        # One sheet by partner
        report_name = "sheet 1"
        report_head = 'Security Insurance Brokers(India) Private Limited'
        sheet = workbook.add_worksheet(report_name[:31])

        merge_format = workbook.add_format(
            {'bold': 1, 'align': 'center', 'valign': 'vcenter', 'font_color': 'black'})
        merge_format33 = workbook.add_format(
            {'bold': 1, 'align': 'left', 'valign': 'vcenter', 'font_color': 'black'})
        merge_format2 = workbook.add_format(
            {'bold': 1, 'align': 'center', 'valign': 'vcenter', 'font_color': 'black', 'border': 1})
        merge_format1 = workbook.add_format(
            {'bold': 1, 'align': 'left', 'valign': 'vleft', 'font_color': 'black'})
        bold = workbook.add_format({'border': 1, 'bold': True, 'align': 'left'})
        bold1 = workbook.add_format({'bold': True, 'border': 1, 'align': 'right'})
        bold2 = workbook.add_format({'bold': True, 'border': 1, 'align': 'center'})
        bold3 = workbook.add_format({'bold': True, 'align': 'right'})
        border = workbook.add_format({'border': 1, 'align': 'center'})
        border2 = workbook.add_format({'border': 1, 'align': 'right'})
        border1 = workbook.add_format({'border': 1, 'align': 'left', 'border': 1, 'align': 'left'})
        align_left = workbook.add_format({'align': 'left'})
        numbersformat = workbook.add_format({'num_format': '#,##0.00', 'bold': True, 'border': 1, 'align': 'right'})
        numbersformat1 = workbook.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'right'})
        report_head2 = 'Business Comparison Report for the period of Start Date : ' + str(
            lines.date_from) + '  to End Date : ' + str(lines.date_to)
        report_head3 = 'Grouped By : Category     Filtered By : ' + str(filtname)
        report_head5 = ' Financial Year : ' + str(prev_date_start).split(" ")[0] +'-'+str(prev_date_end).split(" ")[0]
        report_head0 = ' Financial Year : ' + str(lines.fiscal_year.date_start)+'-'+str(lines.fiscal_year.date_end)
        report_head6 = ' Variance (%) '
        report_head7 = ' Variance Amount '
        report_head8 = ''
        report_head9 = str(period)
        report_head10 ='Printed On  ' + str(x.strftime("%x"))
        # sheet.write(0, 11, ('Printed On  ' + str(x.strftime("%x"))), merge_format)
        sheet.write(1, 0, (str(loc)), merge_format1)
        sheet.write(1, 11, ('Page:1'), bold3)
        sheet.write(8, 0, (' '), bold)
        sheet.write(9, 0, (' '), bold)
        sheet.write(10, 0, ('Line of Business'), bold)
        sheet.write(10, 1, ('No of policies'), bold2)
        sheet.write(10, 2, ('Net Premium'), bold1)
        sheet.write(10, 3, ('Brokg. Income'), bold1)
        sheet.write(10, 4, ('No of policies'), bold2)
        sheet.write(10, 5, ('Net Premium'), bold1)
        sheet.write(10, 6, ('Brokg. Income'), bold1)
        sheet.write(10, 7, ('No of policies'), bold2)
        sheet.write(10, 8, ('Net Premium'), bold1)
        sheet.write(10, 9, ('Brokg. Income'), bold1)
        sheet.write(10, 10, ('Net Premium'), bold1)
        sheet.write(10, 11, ('Brokg. Income'), bold1)

        # increasing width of column
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 20)
        sheet.set_column('J:J', 20)
        sheet.set_column('K:K', 20)
        sheet.set_column('L:L', 20)

        sheet.merge_range('A1:E1', report_head, merge_format33)
        sheet.merge_range('A4:L4', report_head2, merge_format)
        sheet.merge_range('A5:L5', report_head3, merge_format)
        # sheet.merge_range('A6:I6', report_head4, merge_format)
        sheet.merge_range('B9:D9', report_head5, merge_format2)
        sheet.merge_range('E9:G9', report_head0, merge_format2)
        sheet.merge_range('B10:D10', report_head9, merge_format2)
        sheet.merge_range('E10:G10', report_head9, merge_format2)
        sheet.merge_range('H10:J10', report_head7, merge_format2)
        sheet.merge_range('K10:L10', report_head6, merge_format2)
        # sheet.merge_range('B10:D10', report_head7, merge_format2)
        sheet.merge_range('H9:L9', report_head8, merge_format2)
        sheet.merge_range('K1:L1', report_head10, bold3)

        usr_detail = []
        usr_detail_previous = []
        usr_details = self.querys(workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1,
                                  end_year,prev_date_start,prev_date_end)

        endo_date = self.endos(workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1,
                               end_year,prev_date_start,prev_date_end)

        for j in endo_date[0]:
            usr_detail.append(j)

        for i in usr_details[0]:
            usr_detail.append(i)
        # print(len(usr_detail), "lens")

        for j in endo_date[1]:
            usr_detail_previous.append(j)

        for i in usr_details[1]:
            usr_detail_previous.append(i)
        # print(len(usr_detail_previous), "lens")

        temp = []
        temps = []
        an_iterator12 = sorted(usr_detail, key=operator.itemgetter('categoryname'))
        an_iterator = itertools.groupby(an_iterator12, key=operator.itemgetter('categoryname'))
        required_fields = ['Engineering', 'Fire', 'Health', 'Liability', 'Life', 'Marine Cargo', 'Motor', 'Others']
        cat=[]
        cats=[]
        an_iterator122 = sorted(usr_detail_previous, key=operator.itemgetter('categoryname'))
        an_iterator11 = itertools.groupby(an_iterator122, key=operator.itemgetter('categoryname'))

        for key, group in an_iterator:
            key_and_group = {key: list(group)}
            for i in key_and_group.iteritems():
                totalpol = 0
                totalprem = 0
                totalbrok = 0
                totalperc = 0
                brokeragepercent = 0
                commssionamt_null = 0
                netprem_null = 0
                for j in i[1]:
                    if j['netprem'] == None or j['netprem'] == False:
                        netprem_null = 0
                    else:
                        netprem_null = j['netprem']
                    if j['commssionamt'] == None or j['commssionamt'] == False:
                        commssionamt_null = 0
                    else:
                        commssionamt_null = j['commssionamt']

                    totalpol += j['total']
                    totalprem += netprem_null
                    totalbrok += commssionamt_null
                    brokeragepercent = round(((totalbrok / totalprem) * 100), 2)

                cat.append(i[0])
                temp.append({
                    "categoryname": i[0],
                    "total": totalpol,
                    "netprem": totalprem,
                    "commssionamt": totalbrok,
                    "brokeragepercent": brokeragepercent
                })

        a=set(required_fields)
        b =set(cat)
        z =a.difference(b)
        for i in z:
            temp.append({
                "categoryname": i,
                "total": 0,
                "netprem": 0,
                "commssionamt": 0,
                "brokeragepercent": 0
            })





        for key, group in an_iterator11:
            key_and_group = {key: list(group)}
            for i in key_and_group.iteritems():
                totalpol = 0
                totalprem = 0
                totalbrok = 0
                totalperc = 0
                brokeragepercent = 0
                commssionamt_null = 0
                netprem_null = 0
                for j in i[1]:
                    if j['netprem'] == None or j['netprem'] == False:
                        netprem_null = 0
                    else:
                        netprem_null = j['netprem']
                    if j['commssionamt'] == None or j['commssionamt'] == False:
                        commssionamt_null = 0
                    else:
                        commssionamt_null = j['commssionamt']

                    totalpol += j['total']
                    totalprem += netprem_null
                    totalbrok += commssionamt_null
                    brokeragepercent = round(((totalbrok / totalprem) * 100), 2)

                cats.append(i[0])
                temps.append({
                    "categoryname": i[0],
                    "total": totalpol,
                    "netprem": totalprem,
                    "commssionamt": totalbrok,
                    "brokeragepercent": brokeragepercent
                })
        a = set(required_fields)
        b = set(cats)
        z = a.difference(b)
        for i in z:
            temps.append({
                "categoryname": i,
                "total": 0,
                "netprem": 0,
                "commssionamt": 0,
                "brokeragepercent": 0
            })
        row = 11
        policy_countss = 0
        premium_totalss = 0
        brok_totalss = 0
        policy_counts = 0
        premium_total = 0
        brok_total = 0
        s_no = 1
        for res in temps:
            policy_countss += res['total']
            premium_totalss += res['netprem']
            brok_totalss += res['commssionamt']
            print(row,"rows")

            if res['categoryname'] =='Engineering':
                sheet.write(row, 0, res['categoryname'], border1)
                sheet.write(11, 1, res['total'], border)
                sheet.write(11, 2, round(res['netprem']), border2)
                sheet.write(11, 3, round(res['commssionamt']), border2)
                sheet.write(11, 4, res['brokeragepercent'], numbersformat)
            if res['categoryname'] =='Fire':
                sheet.write(12, 0, res['categoryname'], border1)
                sheet.write(12, 1, res['total'], border)
                sheet.write(12, 2, round(res['netprem']), border2)
                sheet.write(12, 3, round(res['commssionamt']), border2)
                sheet.write(12, 4, res['brokeragepercent'], numbersformat)
            if res['categoryname'] =='Health':
                sheet.write(13, 0, res['categoryname'], border1)
                sheet.write(13, 1, res['total'], border)
                sheet.write(13, 2, round(res['netprem']), border2)
                sheet.write(13, 3, round(res['commssionamt']), border2)
                sheet.write(13, 4, res['brokeragepercent'], numbersformat)
            if res['categoryname'] =='Marine Cargo':
                sheet.write(14, 0, res['categoryname'], border1)
                sheet.write(14, 1, res['total'], border)
                sheet.write(14, 2, round(res['netprem']), border2)
                sheet.write(14, 3, round(res['commssionamt']), border2)
                sheet.write(14, 4, res['brokeragepercent'], numbersformat)
            if res['categoryname'] =='Motor':
                sheet.write(15, 0, res['categoryname'], border1)
                sheet.write(15, 1, res['total'], border)
                sheet.write(15, 2, round(res['netprem']), border2)
                sheet.write(15, 3, round(res['commssionamt']), border2)
                sheet.write(15, 4, res['brokeragepercent'], numbersformat)
            if res['categoryname'] =='Others':
                sheet.write(16, 0, res['categoryname'], border1)
                sheet.write(16, 1, res['total'], border)
                sheet.write(16, 2, round(res['netprem']), border2)
                sheet.write(16, 3, round(res['commssionamt']), border2)
                sheet.write(16, 4, res['brokeragepercent'], numbersformat)
            if res['categoryname'] =='Liability':
                sheet.write(17, 0, res['categoryname'], border1)
                sheet.write(17, 1, res['total'], border)
                sheet.write(17, 2, round(res['netprem']), border2)
                sheet.write(17, 3, round(res['commssionamt']), border2)
                sheet.write(17, 4, res['brokeragepercent'], numbersformat)
            if res['categoryname'] =='Life':
                sheet.write(18, 0, res['categoryname'], border1)
                sheet.write(18, 1, res['total'], border)
                sheet.write(18, 2, round(res['netprem']), border2)
                sheet.write(18, 3, round(res['commssionamt']), border2)
                sheet.write(18, 4, res['brokeragepercent'], numbersformat)
            # sheet.write(row, 0, res['categoryname'], border1)
            # sheet.write(row, 1, res['total'], border)
            # sheet.write(row, 2, round(res['netprem']), border2)
            # sheet.write(row, 3, round(res['commssionamt']), border2)
            # sheet.write(row, 4, res['brokeragepercent'], numbersformat)

            row = row + 1
            s_no = s_no + 1
            # print("Array printed for s.no :", s_no - 1)
        sheet.write(row, 0, ('Total'), bold)
        sheet.write(row, 1, policy_countss, bold2)
        sheet.write(row, 2, round(premium_totalss), bold1)
        sheet.write(row, 3, round(brok_totalss), bold1)
        # sheet.write(row, 4, (' '), bold)
        row = 11
        for res in temp:
            policy_counts += res['total']
            premium_total += res['netprem']
            brok_total += res['commssionamt']
            # sheet.write(row, 3, res['categoryname'], border1)
            required_fields = ['Engineering', 'Fire', 'Health', 'Liability', 'Life', 'Marine Cargo', 'Motor', 'Others']
            if res['categoryname'] =='Engineering':
                sheet.write(11, 4, res['total'], border)
                sheet.write(11, 5, round(res['netprem']), border2)
                sheet.write(11, 6, round(res['commssionamt']), border2)
            if res['categoryname'] =='Fire':
                sheet.write(12, 4, res['total'], border)
                sheet.write(12, 5, round(res['netprem']), border2)
                sheet.write(12, 6, round(res['commssionamt']), border2)
            if res['categoryname'] =='Health':
                sheet.write(13, 4, res['total'], border)
                sheet.write(13, 5, round(res['netprem']), border2)
                sheet.write(13, 6, round(res['commssionamt']), border2)
            if res['categoryname'] =='Marine Cargo':
                # sheet.write(row, 3, res['categoryname'], border1)
                sheet.write(14, 4, res['total'], border)
                sheet.write(14, 5, round(res['netprem']), border2)
                sheet.write(14, 6, round(res['commssionamt']), border2)
            if res['categoryname'] =='Motor':
                sheet.write(15, 4, res['total'], border)
                sheet.write(15, 5, round(res['netprem']), border2)
                sheet.write(15, 6, round(res['commssionamt']), border2)
            if res['categoryname'] =='Others':
                sheet.write(16, 4, res['total'], border)
                sheet.write(16, 5, round(res['netprem']), border2)
                sheet.write(16, 6, round(res['commssionamt']), border2)
            if res['categoryname'] =='Liability':
                sheet.write(17, 4, res['total'], border)
                sheet.write(17, 5, round(res['netprem']), border2)
                sheet.write(17, 6, round(res['commssionamt']), border2)
            if res['categoryname'] =='Life':
                sheet.write(18, 4, res['total'], border)
                sheet.write(18, 5, round(res['netprem']), border2)
                sheet.write(18, 6, round(res['commssionamt']), border2)

            # sheet.write(row, 4, res['total'], border)
            # sheet.write(row, 5, round(res['netprem']), border2)
            # sheet.write(row, 6, round(res['commssionamt']), border2)
            # sheet.write(row, 8, res['brokeragepercent'], numbersformat)

            row = row + 1
            s_no = s_no + 1
            # print("Array printed for s.no :", s_no - 1)
        # sheet.write(row, 0, ('Total'), bold)
        sheet.write(row, 4, policy_counts, bold2)
        sheet.write(row, 5, round(premium_total), bold1)
        sheet.write(row, 6, round(brok_total), bold1)
        # sheet.write(row, 8, (' '), bold)

        varpol = 0
        varprem = 0
        varbrok = 0
        varnet_perto = 0
        varbrok_perto = 0
        var_total_pol = 0
        var_commssionamt_null = 0
        var_netprem_null = 0
        row=11
        varnet_per=0

        varbrok_per=0
        required_fields = ['Engineering', 'Fire', 'Health', 'Liability', 'Life', 'Marine Cargo', 'Motor', 'Others']
        # print(temp,temps)
        for j in temps:
            for i in temp:
                # if i['categoryname'] == j['categoryname']:
                #     # print(i['categoryname'],j['categoryname'],"CCCCCCCCCCCCCCCCCCCCCCCC")
                #     # print(i['total'] , j['total'],"CCCCCCCCCCCCCCCCCCCCCCCC")
                #     varpol = i['total'] - j['total']
                #     varprem = i['netprem'] - j['netprem']
                #     varbrok = i['commssionamt'] - j['commssionamt']
                #     var_total_pol+=varpol
                #     var_commssionamt_null+=varprem
                #     var_netprem_null+=varbrok
                #     if varprem !=0:
                #         varnet_per = varprem * 100 / i['netprem']
                #         varbrok_per = varbrok * 100 / i['commssionamt']
                #     varnet_perto += varnet_per
                #     varbrok_perto += varbrok_per
                #     sheet.write(row, 7, varpol, border)
                #     sheet.write(row, 8, round(varprem), border2)
                #     sheet.write(row, 9, round(varbrok), border2)
                #     sheet.write(row, 10, (varnet_per),  numbersformat1)
                #     sheet.write(row, 11, (varbrok_per), numbersformat1)
                #     row+=1
                if i['categoryname'] == j['categoryname']:
                    if i['categoryname'] and j['categoryname'] == 'Engineering':
                        varpol = i['total'] - j['total']
                        varprem = i['netprem'] - j['netprem']
                        varbrok = i['commssionamt'] - j['commssionamt']
                        var_total_pol+=varpol
                        var_commssionamt_null+=varprem
                        var_netprem_null+=varbrok
                        if varprem != 0 and i['netprem'] !=0:
                            varnet_per = varprem * 100 / i['netprem']
                            varnet_perto += varnet_per
                            varbrok_per = varbrok * 100 / i['commssionamt']
                            varbrok_perto += varbrok_per

                        sheet.write(11, 7, varpol, border)
                        sheet.write(11, 8, round(varprem), border2)
                        sheet.write(11, 9, round(varbrok), border2)
                        sheet.write(11, 10, (varnet_perto),  numbersformat1)
                        sheet.write(11, 11, (varbrok_perto), numbersformat1)
                    if i['categoryname'] and j['categoryname'] == 'Fire':
                        varpol = i['total'] - j['total']
                        varprem = i['netprem'] - j['netprem']
                        varbrok = i['commssionamt'] - j['commssionamt']
                        var_total_pol += varpol
                        var_commssionamt_null += varprem
                        var_netprem_null += varbrok
                        if varprem != 0 and i['netprem']:
                            varnet_per = varprem * 100 / i['netprem']
                        if varbrok !=0 and i['commssionamt']:
                            varbrok_per = varbrok * 100 / i['commssionamt']
                        varnet_perto += varnet_per
                        varbrok_perto += varbrok_per
                        sheet.write(12, 7, varpol, border)
                        sheet.write(12, 8, round(varprem), border2)
                        sheet.write(12, 9, round(varbrok), border2)
                        sheet.write(12, 10, (varnet_per), numbersformat1)
                        sheet.write(12, 11, (varbrok_per), numbersformat1)
                    if i['categoryname'] and j['categoryname'] == 'Health':
                        varpol = i['total'] - j['total']
                        varprem = i['netprem'] - j['netprem']
                        varbrok = i['commssionamt'] - j['commssionamt']
                        var_total_pol += varpol
                        var_commssionamt_null += varprem
                        var_netprem_null += varbrok
                        if varprem != 0:
                            varnet_per = varprem * 100 / i['netprem']
                            varbrok_per = varbrok * 100 / i['commssionamt']
                        varnet_perto += varnet_per
                        varbrok_perto += varbrok_per
                        sheet.write(13, 7, varpol, border)
                        sheet.write(13, 8, round(varprem), border2)
                        sheet.write(13, 9, round(varbrok), border2)
                        sheet.write(13, 10, (varnet_per), numbersformat1)
                        sheet.write(13, 11, (varbrok_per), numbersformat1)
                    if i['categoryname'] and j['categoryname'] == 'Marine Cargo':
                        varpol = i['total'] - j['total']
                        varprem = i['netprem'] - j['netprem']
                        varbrok = i['commssionamt'] - j['commssionamt']
                        var_total_pol += varpol
                        var_commssionamt_null += varprem
                        var_netprem_null += varbrok
                        if varprem != 0:
                            varnet_per = varprem * 100 / i['netprem']
                            varbrok_per = varbrok * 100 / i['commssionamt']
                        varnet_perto += varnet_per
                        varbrok_perto += varbrok_per
                        sheet.write(14, 7, varpol, border)
                        sheet.write(14, 8, round(varprem), border2)
                        sheet.write(14, 9, round(varbrok), border2)
                        sheet.write(14, 10, (varnet_per), numbersformat1)
                        sheet.write(14, 11, (varbrok_per), numbersformat1)
                    if i['categoryname'] and j['categoryname'] == 'Motor':
                        varpol = i['total'] - j['total']
                        varprem = i['netprem'] - j['netprem']
                        varbrok = i['commssionamt'] - j['commssionamt']
                        var_total_pol += varpol
                        var_commssionamt_null += varprem
                        var_netprem_null += varbrok
                        if varprem != 0:
                            varnet_per = varprem * 100 / i['netprem']
                            varbrok_per = varbrok * 100 / i['commssionamt']
                        varnet_perto += varnet_per
                        varbrok_perto += varbrok_per
                        sheet.write(15, 7, varpol, border)
                        sheet.write(15, 8, round(varprem), border2)
                        sheet.write(15, 9, round(varbrok), border2)
                        sheet.write(15, 10, (varnet_per), numbersformat1)
                        sheet.write(15, 11, (varbrok_per), numbersformat1)
                    if i['categoryname'] and j['categoryname'] == 'Others':
                        varpol = i['total'] - j['total']
                        varprem = i['netprem'] - j['netprem']
                        varbrok = i['commssionamt'] - j['commssionamt']
                        var_total_pol += varpol
                        var_commssionamt_null += varprem
                        var_netprem_null += varbrok
                        if varprem != 0:
                            varnet_per = varprem * 100 / i['netprem']
                            varbrok_per = varbrok * 100 / i['commssionamt']
                        varnet_perto += varnet_per
                        varbrok_perto += varbrok_per
                        sheet.write(16, 7, varpol, border)
                        sheet.write(16, 8, round(varprem), border2)
                        sheet.write(16, 9, round(varbrok), border2)
                        sheet.write(16, 10, (varnet_per), numbersformat1)
                        sheet.write(16, 11, (varbrok_per), numbersformat1)
                    if i['categoryname'] and j['categoryname'] == 'Liability':
                        varpol = i['total'] - j['total']
                        varprem = i['netprem'] - j['netprem']
                        varbrok = i['commssionamt'] - j['commssionamt']
                        var_total_pol += varpol
                        var_commssionamt_null += varprem
                        var_netprem_null += varbrok
                        if varprem != 0:
                            varnet_per = varprem * 100 / i['netprem']
                            varbrok_per = varbrok * 100 / i['commssionamt']
                        varnet_perto += varnet_per
                        varbrok_perto += varbrok_per
                        sheet.write(17, 7, varpol, border)
                        sheet.write(17, 8, round(varprem), border2)
                        sheet.write(17, 9, round(varbrok), border2)
                        sheet.write(17, 10, (varnet_per), numbersformat1)
                        sheet.write(17, 11, (varbrok_per), numbersformat1)
                    if i['categoryname'] and j['categoryname'] == 'Life':
                        varpol = i['total'] - j['total']
                        varprem = i['netprem'] - j['netprem']
                        varbrok = i['commssionamt'] - j['commssionamt']
                        var_total_pol += varpol
                        var_commssionamt_null += varprem
                        var_netprem_null += varbrok
                        if varprem != 0:
                            varnet_per = varprem * 100 / i['netprem']
                            varbrok_per = varbrok * 100 / i['commssionamt']
                        varnet_perto += varnet_per
                        varbrok_perto += varbrok_per
                        sheet.write(18, 7, varpol, border)
                        sheet.write(18, 8, round(varprem), border2)
                        sheet.write(18, 9, round(varbrok), border2)
                        sheet.write(18, 10, (varnet_per), numbersformat1)
                        sheet.write(18, 11, (varbrok_per), numbersformat1)

                sheet.write(19, 7, var_total_pol, bold2)
                sheet.write(19, 8, round(var_commssionamt_null), bold1)
                sheet.write(19, 9, round(var_netprem_null), bold1)
                if  var_commssionamt_null !=0:
                    sheet.write(19, 10, (var_commssionamt_null*100/premium_totalss), numbersformat)
                if var_netprem_null !=0:
                    sheet.write(19, 11, (var_netprem_null *100/brok_totalss), numbersformat)






    def querys(self, workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1, end_year
               ,prev_date_start,prev_date_end,id=None,
               endo=None):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        with registry.cursor() as cr:
            query = " select t1.id,t3.co_insurer_id,count(t1.segment) as total ,t4.irda_cat as categoryname ," \
                    " case when t3.co_insurer_id is not null then sum(t3.co_net_premium) else sum(t1.netprem)" \
                    " end as netprem," \
                    " case when t3.co_insurer_id is not null then sum(t3.co_commission_amount) else sum(t1.commssionamt)" \
                    " end as commssionamt" \
                    " from policytransaction as t1" \
                    " left join co_insurer_policy as t3 on t3.co_insurer_id =t1.id AND t3.co_type='self'" \
                    " left join category_category as t4 on t4.id = t1.segment"

            query1 = " select t1.id,t3.co_insurer_id,count(t1.segment) as total ,t4.irda_cat as categoryname ," \
                    " case when t3.co_insurer_id is not null then sum(t3.co_net_premium) else sum(t1.netprem)" \
                    " end as netprem," \
                    " case when t3.co_insurer_id is not null then sum(t3.co_commission_amount) else sum(t1.commssionamt)" \
                    " end as commssionamt" \
                    " from policytransaction as t1" \
                    " left join co_insurer_policy as t3 on t3.co_insurer_id =t1.id AND t3.co_type='self'" \
                    " left join category_category as t4 on t4.id = t1.segment"

            print(query,query1)
            if lines.filterby == 'all':
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t1.startfrom  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' "
                    query1 += " where t1.startfrom  BETWEEN '" + str(prev_date_start) + "' AND '" + str(prev_date_end) + "' "

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)

                        query += " where t1.startfrom  BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "'"
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                        lines.pre_date_to) + "'"

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(feb_start) + "' AND '" + str(feb_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"

                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(mar_start) + "' AND '" + str(mar_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(apr_start) + "' AND '" + str(apr_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(may_start) + "' AND '" + str(may_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(june_start) + "' AND '" + str(june_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(jul_start) + "' AND '" + str(jul_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(aug_start) + "' AND '" + str(aug_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(sep_start) + "' AND '" + str(sep_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(oct_start) + "' AND '" + str(oct_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(nov_start) + "' AND '" + str(nov_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(dec_start) + "' AND '" + str(dec_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t1.startfrom  BETWEEN '" + str(lines.date_from) + "' AND '" + str(lines.date_to) + "' "
                    query1 += " where t1.startfrom  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(lines.pre_date_to) + "' "

                if lines.location != 'all':
                    query += "and t1.location = '" + str(lines.location) + "' group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                    query1 += "and t1.location = '" + str(lines.location) + "' group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                else:
                    query += " group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                    query1 += " group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                cr.execute(query1)
                query1_exc = cr.dictfetchall()
                # print(query1_exc,"QWXSTERY")
                print(query, query1, "QQQQQWEEEEEEEEEEEEEEEE111")

                return [usr_detail,query1_exc]

            elif lines.filterby == 'category':

                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t1.startfrom  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "'  AND t4.name = '" + str(lines.category.name) + "' "
                    query1 += " where t1.startfrom  BETWEEN '" + str(prev_date_start) + "' AND '" + str(prev_date_end) + "'  AND t4.name = '" + str(lines.category.name) + "' "

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)

                        query += " where t1.startfrom  BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "'  AND t4.name = '" + str(lines.category.name) + "' "
                        query1 +=" where t1.startfrom BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "'   AND t4.name = '" + str(lines.category.name) + "' "
                        query1 += " where t1.startfrom BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "'"
                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"
                        query1 += " where t1.startfrom BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(apr_start) + "' AND '" + str(apr_end) + "'   AND t4.name = '" + str(lines.category.name) + "' "
                        query1 += " where t1.startfrom BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "'"
                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(may_start) + "' AND '" + str(may_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"
                        query1 += " where t1.startfrom BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "'"
                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(june_start) + "' AND '" + str(june_end) + "'   AND t4.name = '" + str(lines.category.name) + "' "
                        query1 += " where t1.startfrom BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                                    lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "'"
                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"
                        query1 += " where t1.startfrom BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "'"
                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"
                        query1 += " where t1.startfrom BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"
                        query1 += " where t1.startfrom BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"
                        query1 += " where t1.startfrom BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "'"
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"
                        query1 += " where t1.startfrom BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "'"
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"
                        query1 += " where t1.startfrom BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "'"

                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t1.startfrom  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "'  AND t4.name = '" + str(
                        lines.category.name) + "'"
                    query1 += " where t1.startfrom  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                        lines.pre_date_to) + "' "


                if lines.location != 'all':
                    query += " and t1.location = '" + str(
                            lines.location) + "'group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                    query1 += " and t1.location = '" + str(
                            lines.location) + "'group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                else:
                    query += " group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                    query1 += " group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                print(query,query1,"QQQQQWEEEEEEEEEEEEEEEE")
                cr.execute(query)
                usr_detail = cr.dictfetchall()
                cr.execute(query1)
                query1_exc = cr.dictfetchall()
                return [usr_detail, query1_exc]
            else:
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t1.startfrom  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' "
                    query1 += " where t1.startfrom  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                        lines.pre_date_to) + "' "

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)

                        query += " where t1.startfrom  BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(feb_start) + "' AND '" + str(feb_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(mar_start) + "' AND '" + str(mar_end) + "'"
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(apr_start) + "' AND '" + str(apr_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(may_start) + "' AND '" + str(may_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(june_start) + "' AND '" + str(june_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(jul_start) + "' AND '" + str(jul_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(aug_start) + "' AND '" + str(aug_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(sep_start) + "' AND '" + str(sep_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(oct_start) + "' AND '" + str(oct_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(nov_start) + "' AND '" + str(nov_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(dec_start) + "' AND '" + str(dec_end) + "' "
                        query1 += " where t1.startfrom   BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t1.startfrom  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(lines.date_to + ' 23:59:59') + "' "
                    query1 += " where t1.startfrom  BETWEEN '" + str(lines.pre_date_from + ' 00:00:00') + "' AND '" + str(lines.pre_date_to + ' 23:59:59') + "' "
                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "'group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                    query1 += " and t1.location = '" + str(lines.location) + "'group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                else:
                    query += " group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                    query1 += " group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"

                print(query, query1, "QQQQQWEEEEEEEEEEEEEEEE")
                cr.execute(query)
                usr_detail = cr.dictfetchall()
                cr.execute(query1)
                query1_exc = cr.dictfetchall()
                return [usr_detail, query1_exc]

    def endos(self, workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1, end_year,prev_date_start,prev_date_end,id=None,
              endo=None,):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        with registry.cursor() as cr:
            query = " select t1.id,t2.endo_id,count(t1.segment) as total,t4.irda_cat as categoryname,sum(t2.endo_net) as netprem," \
                    " sum(t2.endo_commission) as commssionamt" \
                    " from policytransaction as t1" \
                    " left join endos_policy as t2 on t2.endo_id =t1.id" \
                    " left join category_category as t4 on t4.id = t1.segment"
            query1 = " select t1.id,t2.endo_id,count(t1.segment) as total,t4.irda_cat as categoryname,sum(t2.endo_net) as netprem," \
                    " sum(t2.endo_commission) as commssionamt" \
                    " from policytransaction as t1" \
                    " left join endos_policy as t2 on t2.endo_id =t1.id" \
                    " left join category_category as t4 on t4.id = t1.segment"

            if lines.filterby == 'all':
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t2.endos_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' "

                    query1 += " where t2.endos_date  BETWEEN '" + str(prev_date_start) + "' AND '" + str(prev_date_end) + "' "

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)

                        query += " where t2.endos_date  BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "'"
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(feb_start) + "' AND '" + str(feb_end) + "' "
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(mar_start) + "' AND '" + str(mar_end) + "' "
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"

                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(apr_start) + "' AND '" + str(apr_end) + "' "
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"

                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(may_start) + "' AND '" + str(may_end) + "' "
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"

                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "' "
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"

                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(jul_start) + "' AND '" + str(jul_end) + "' "
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"

                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(aug_start) + "' AND '" + str(aug_end) + "' "
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"

                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(sep_start) + "' AND '" + str(sep_end) + "' "
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"

                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(oct_start) + "' AND '" + str(oct_end) + "' "
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(nov_start) + "' AND '" + str(nov_end) + "' "
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(dec_start) + "' AND '" + str(dec_end) + "' "
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'"
                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t2.endos_date  BETWEEN '" + str(lines.date_from) + "' AND '" + str(lines.date_to) + "' "
                    query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(lines.pre_date_to) + "' "

                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "' and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                    query1 += " and t1.location = '" + str(lines.location) + "' and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                else:
                    query += " and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                    query1 += " and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"

                # print(query, "QQQQQQQQQQQQQQQQQQQQQQ")
                cr.execute(query)
                usr_detail = cr.dictfetchall()
                cr.execute(query1)
                query1_exc = cr.dictfetchall()
                # print(query1_exc,"QWXSTERY")

                return [usr_detail, query1_exc]

            elif lines.filterby == 'category':

                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t2.endos_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "'  AND t4.name = '" + str(
                        lines.category.name) + "' "
                    query1 += " where t2.endos_date  BETWEEN '" + str(prev_date_start) + "' AND '" + str(
                        prev_date_end) + "' "

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)

                        query += " where t2.endos_date  BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "'  AND t4.name = '" + str(lines.category.name) + "' "
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "'   AND t4.name = '" + str(lines.category.name) + "' "
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"

                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "'   AND t4.name = '" + str(lines.category.name) + "' "
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"

                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "' "
                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "'   AND t4.name = '" + str(
                            lines.category.name) + "' "
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"

                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "' "
                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"

                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "' "
                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "' "
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "' "
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"
                        query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "'  AND t4.name = '" + str(lines.category.name) + "' "

                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t2.endos_date  BETWEEN '" + str(
                        lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "'  AND t4.name = '" + str(
                        lines.category.name) + "'"
                    query1 += " where t2.endos_date  BETWEEN '" + str(
                        lines.pre_date_from + ' 00:00:00') + "' AND '" + str(
                        lines.pre_date_to + ' 23:59:59') + "'  AND t4.name = '" + str(
                        lines.category.name) + "'"

                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "' and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                    query1 += " and t1.location = '" + str(lines.location) + "' and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                else:
                    query += " and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                    query1 += " and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"


                # print(query,"QQQQQQQQQQWWWEEEEEEEc")
                cr.execute(query)
                usr_detail = cr.dictfetchall()
                cr.execute(query1)
                query1_exc = cr.dictfetchall()
                # print(query1_exc,"QWXSTERY")

                return [usr_detail, query1_exc]

            else:
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t2.endos_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' "
                    query1 += " where t2.endos_date  BETWEEN '" + str(prev_date_start) + "' AND '" + str(
                        prev_date_end) + "' "
                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)

                        query += " where t2.endos_date  BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "' "

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(feb_start) + "' AND '" + str(feb_end) + "' "

                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(mar_start) + "' AND '" + str(mar_end) + "'"

                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(apr_start) + "' AND '" + str(apr_end) + "' "

                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(may_start) + "' AND '" + str(may_end) + "' "

                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "' "

                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(jul_start) + "' AND '" + str(jul_end) + "' "

                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(aug_start) + "' AND '" + str(aug_end) + "' "

                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(sep_start) + "' AND '" + str(sep_end) + "' "

                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(oct_start) + "' AND '" + str(oct_end) + "' "
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(nov_start) + "' AND '" + str(nov_end) + "' "
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(dec_start) + "' AND '" + str(dec_end) + "' "

                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t2.endos_date  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(lines.date_to + ' 23:59:59') + "' "
                    query1 += " where t2.endos_date  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(lines.pre_date_to) + "' "

                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "' and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                    query1 += " and t1.location = '" + str(lines.location) + "' and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                else:
                    query += " and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                    query1 += " and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                cr.execute(query1)
                query1_exc = cr.dictfetchall()
                # print(query1_exc,"QWXSTERY")

                return [usr_detail, query1_exc]


GeneralXlsx('report.clickbima.compare_report_excel.xlsx', 'comparebusiness.report')

