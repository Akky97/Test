import base64
import io
import itertools
import numpy as np
import odoo
import operator
import os
import pandas as pd
import time
from datetime import date
from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.http import request, content_disposition
from odoo.modules.registry import Registry
from odoo.service import model
# from pandas.tests.groupby.conftest import ts
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, StringIO, cStringIO
from odoo.tools.misc import xlwt


class buscompdetailreport(models.TransientModel):
    _name = "buscompdetail.report"
    _description = "Business Comparison Detail Report"

    date_from = fields.Date('From Date')
    pre_date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    pre_date_to = fields.Date('To Date')
    monthly = fields.Selection([('monthly', 'Monthly'), ('quatar', 'Quarterly'), ('yearly', 'Yearly')],
                               default='monthly', string='Period Type')
    quarter = fields.Selection([('q1', 'Quarter 1'), ('q2', 'Quarter 2'), ('q3', 'Quarter 3'), ('q4', 'Quarter 4')],
                               string='Quarter')
    location = fields.Selection([('9', 'Chandigarh'), ('8', 'Ludhiana'), ('7', 'New Delhi'), ('all', 'All')],
                                default='all', string="Location")
    groupby = fields.Selection(
        [('create_date', 'Docket Date'), ('proposaldate', 'Proposal Date'), ('startdate', 'Start Date')],
        default='startdate', string="Group BY")
    filterby = fields.Selection([('all', 'All'), ('category', 'Category')], default='all', string="Filter BY")
    fiscal_year = fields.Many2one('fyyear', string="Financial Year",
                                  default=lambda self: self.env['fyyear'].search([('ex_active', '=', True)],
                                                                                 limit=1).id)
    months = fields.Selection(
        [('01-01', 'January'), ('01-02', 'February'), ('01-03', 'March'), ('01-04', 'April'), ('01-05', 'May'),
         ('01-06', 'June'),
         ('01-07', 'July'), ('01-08', 'August'), ('01-09', 'September'), ('01-10', 'October'), ('01-11', 'November'),
         ('01-12', 'December')])
    # category=fields.Many2one('category.category', string="Category")
    client_name = fields.Many2one('res.partner', string="Client Name")
    group_name = fields.Char(string="Group Name")
    start_year = fields.Char()
    end_year = fields.Char()

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
                previous_start_date =''
                previous_end_date =''
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
                    print(self.date_to, self.pre_date_to, self.pre_date_from, prev_jan_end)


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
                    print(prev_apr_start,prev_apr_end,"????????????>>>>>>>>>>>??????????????")

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
                print(self.pre_date_to, self.pre_date_from, "TO from")

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
        return self.env['report'].get_action(self, report_name='clickbima.bus_comp_detail.xlsx', data=data)


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
        report_name = "sheet 1"
        # One sheet by partner
        sheet = workbook.add_worksheet(report_name[:31])

        merge_format = workbook.add_format(
            {'bold': 1, 'align': 'center', 'valign': 'vcenter', 'font_color': 'black'})
        bold = workbook.add_format({'border': 1, 'bold': True, 'align': 'left'})
        bold_less = workbook.add_format({'bold': True, 'align': 'left'})
        bold1 = workbook.add_format({'bold': True, 'align': 'right'})
        bold2 = workbook.add_format({'bold': True, 'align': 'center'})
        bold3 = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
        bold_center = workbook.add_format({'align': 'center', 'border': 1})
        bold_right = workbook.add_format({'align': 'right', 'border': 1})
        bold_left = workbook.add_format({'align': 'left', 'border': 1})
        border = workbook.add_format({'border': 1, 'align': 'right', 'bold': True, })
        border2 = workbook.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'right'})
        border1 = workbook.add_format({'border': 1, 'align': 'left'})
        align_right = workbook.add_format({'border': 'right', 'border': 1, 'bold': True, })
        numbersformat = workbook.add_format({'num_format': '#,##0.00', 'bold': True, 'border': 1, 'align': 'right'})
        numbersformat1 = workbook.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'right'})
        report_head1 = 'Business Comparison Detail Report for the period of Start Date : ' + str(
            lines.date_from) + '  to End Date : ' + str(lines.date_to)
        report_head2 = 'Grouped By : Category     Filtered By : ' + str(filtname)
        report_head3 = 'Security Insurance Brokers (India) Private Limited'
        report_head4 = str(loc)
        report_head5 = ''
        report_head6 = 'Previous Period'
        report_head8 = 'Current Period'
        report_head7 = 'Printed On  ' + str(x.strftime("%x"))
        report_head9 = '( Financial Year : ' + str(prev_date_start).split(" ")[0] + '-' + str(prev_date_end).split(" ")[
            0] + ')' + str(period)
        report_head10 = '( Financial Year : ' + str(lines.fiscal_year.date_start) + '-' + str(
            lines.fiscal_year.date_end) + ')' + str(period)
        report_head11 = 'Current'
        report_head12 = 'New Business'
        sheet.write(6, 1, ('Sr.'), bold3)
        sheet.write(6, 2, ('Previous'), bold3)
        sheet.write(6, 3, ('New'), bold3)
        sheet.write(6, 4, (''), bold3)
        sheet.write(6, 7, (''), bold3)
        sheet.write(6, 8, (''), bold3)
        sheet.write(6, 9, (''), bold3)
        sheet.write(7, 1, ('No.'), bold3)
        sheet.write(7, 2, ('Docket No.'), bold3)
        sheet.write(7, 3, ('Docket No.'), bold3)
        sheet.write(7, 4, ('Policy Status'), bold)
        sheet.write(7, 5, ('Policy No.'), bold1)
        sheet.write(7, 6, ('Ends No.'), bold1)
        sheet.write(7, 7, ('Scheme'), bold)
        sheet.write(7, 8, ('Insured Name'), bold)
        sheet.write(7, 9, ('Insurer Name / Branch Name'), bold)
        sheet.write(7, 10, ('Share(%)'), border)
        sheet.write(7, 11, ('Net Premium'), border)
        sheet.write(7, 12, ('Brkg Amnt'), border)
        sheet.write(7, 13, ('Share(%)'), border)
        sheet.write(7, 14, ('Net Premium'), border)
        sheet.write(7, 15, ('Brkg Amnt'), border)

        # increasing width of column
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 10)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 40)
        sheet.set_column('I:I', 50)
        sheet.set_column('J:J', 70)
        sheet.set_column('K:K', 10)
        sheet.set_column('L:L', 20)
        sheet.set_column('M:M', 20)
        sheet.set_column('N:N', 10)
        sheet.set_column('O:O', 20)
        sheet.set_column('P:P', 20)

        sheet.merge_range('O1:P1', report_head7, bold1)
        sheet.merge_range('K6:M6', report_head6, bold3)
        sheet.merge_range('N6:P6', report_head8, bold3)
        sheet.merge_range('K7:M7', report_head9, bold3)
        sheet.merge_range('N7:P7', report_head10, bold3)
        sheet.merge_range('B6:J6', report_head5, bold3)
        sheet.merge_range('B3:P3', report_head1, bold2)
        sheet.merge_range('B4:P4', report_head2, bold2)
        sheet.merge_range('B2:F2', report_head4, bold_less)
        sheet.merge_range('B1:F1', report_head3, bold_less)
        sheet.merge_range('F7:G7', report_head11, bold3)
        sheet.merge_range('B9:G9', report_head12, bold)

        usr_detail = []  # current year new
        usr_detail_previous = []  # only renewal of current year
        usr_detail_lost = []  # previous year
        usr_lost_data =[]
        usr_details = self.querys(workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1,
                                  end_year, prev_date_start, prev_date_end)

        endo_date = self.endos(workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1,
                               end_year, prev_date_start, prev_date_end)

        for j in endo_date[0]:
            usr_detail.append(j)

        for i in usr_details[0]:
            usr_detail.append(i)


        #
        for j in endo_date[1]:
            usr_detail_previous.append(j)




        for i in usr_details[1]:
            usr_detail_previous.append(i)



        # >>>>>>>>>>LOST DATA ARRAY<<<<<<<<<
        # for j in endo_date[1]:
        #     usr_lost_data.append(j)
        for i in usr_details[1]:
            usr_lost_data.append(i)



        # for j in endo_date[2]:
        #     usr_detail_lost.append(j)

        for i in usr_details[2]:
            usr_detail_lost.append(i)

        # print(len(usr_detail), "new")
        # print(len(usr_detail_previous), "renewal")
        # print(len(usr_detail_lost), "lost")

        row = 8
        index = 1

        if lines.groupby == 'create_date':
            temp = []
            totalcommcount = 0
            totalnetprems = 0

            renewtotalcommcount = 0
            renewtotalnetprems = 0

            frenewtotalcommcount = 0
            frenewtotalnetprems = 0

            losttotalcommcount = 0
            losttotalnetprems = 0

            s_no_proposaldate = 0
            totalcomm_new = 0
            totalnetprem_new = 0

            for res in usr_detail:
                row += 1
                s_no_proposaldate += 1
                suminsur_null = 0
                gross_null = 0
                netprem_null_n = 0
                brokprem_null = 0
                comm_null_n = 0
                sertaxamt_null = 0
                brokeragepercent = 0
                totalsuminsured = 0
                totalgrossprem = 0
                totalcomm_n = 0
                totalnetprem_n = 0
                totalbrokprem = 0

                totalservicetxtamts = 0
                totalothersprems = 0
                if res['suminsured'] == None or res['suminsured'] == False:
                    suminsur_null = 0
                else:
                    suminsur_null = res['suminsured']
                if res['grossprem'] == None or res['grossprem'] == False:
                    gross_null = 0
                else:
                    gross_null = res['grossprem']
                if res['netprem'] == None or res['netprem'] == False:
                    netprem_null_n = 0
                else:
                    netprem_null_n = res['netprem']
                if res['brokerageprem'] == None or res['brokerageprem'] == False:
                    brokprem_null = 0
                else:
                    brokprem_null = res['brokerageprem']
                if res['commssionamt'] == None or res['commssionamt'] == False:
                    comm_null_n = 0
                else:
                    comm_null_n = res['commssionamt']
                if res['servicetaxamt'] == None or res['servicetaxamt'] == False:
                    sertaxamt_null = 0
                else:
                    sertaxamt_null = res['servicetaxamt']

                totalcommcount += comm_null_n
                totalsuminsured += (suminsur_null)
                totalbrokprem += (brokprem_null)
                totalgrossprem += (gross_null)
                totalnetprems += (netprem_null_n)

                totalservicetxtamts += (sertaxamt_null)
                totalothersprems += (res['tp'] + res['tr'] + res['ts'])

                sheet.write(row, 1, s_no_proposaldate, bold_right)
                sheet.write(row, 2, '', bold_center)
                sheet.write(row, 3, res['docketno'], bold_center)
                sheet.write(row, 4, res['policystatus'], border1)
                sheet.write(row, 5, res['policyno'], border1)
                sheet.write(row, 6, res['endos_no'], border2)
                sheet.write(row, 7, res['subcategory'], bold_left)
                sheet.write(row, 8, res['insuredname'], bold_left)
                sheet.write(row, 9, res['insurername'] + '/' + res['insurerbranch'], bold_left)
                sheet.write(row, 10, '', border)
                sheet.write(row, 11, '', border1)
                sheet.write(row, 12, '', border1)
                sheet.write(row, 13, res['co_share'], numbersformat1)
                sheet.write(row, 14, netprem_null_n, border2)
                sheet.write(row, 15, comm_null_n, border2)
                # totalcomm_new += comm_null_n
                # totalnetprem_new += netprem_null_n
            row += 1
            # sheet.write(row, 11, str('New '), border)
            sheet.write(row, 9, str('New Business Total '), bold)
            sheet.write(row, 10, ' ', numbersformat)
            sheet.write(row, 11, ' ', numbersformat)
            sheet.write(row, 12, ' ', numbersformat)
            sheet.write(row, 13, ' ', numbersformat)
            sheet.write(row, 14, totalnetprems, numbersformat)
            sheet.write(row, 15, totalcommcount, numbersformat)

            row += 3
            sheet.write(row, 1, 'Renewal', border)
            sheet.write(row, 2, ' Business', bold)
            # REnewal case
            for res in usr_detail_previous:  # cuurent renewal
                for f in usr_detail_lost:  # previous dockets
                    if res['prevdocket'] == f['docketno']:
                        row += 1
                        s_no_proposaldate += 1
                        suminsur_null = 0
                        gross_null = 0
                        netprem_null = 0
                        brokprem_null = 0
                        comm_null = 0
                        sertaxamt_null = 0
                        brokeragepercent = 0
                        totalsuminsured = 0
                        totalgrossprem = 0
                        totalnetprem = 0
                        totalbrokprem = 0
                        totalcomm = 0
                        totalservicetxtamts = 0
                        totalothersprems = 0

                        zsuminsur_null = 0
                        zgross_null = 0
                        znetprem_null = 0
                        zbrokprem_null = 0
                        zcomm_null = 0
                        zsertaxamt_null = 0
                        zbrokeragepercent = 0
                        ztotalsuminsured = 0
                        ztotalgrossprem = 0
                        ztotalnetprem = 0
                        ztotalbrokprem = 0
                        ztotalcomm = 0
                        ztotalservicetxtamts = 0
                        ztotalothersprems = 0

                        if res['suminsured'] == None or res['suminsured'] == False:
                            suminsur_null = 0
                        else:
                            suminsur_null = res['suminsured']
                        if res['grossprem'] == None or res['grossprem'] == False:
                            gross_null = 0
                        else:
                            gross_null = res['grossprem']
                        if res['netprem'] == None or res['netprem'] == False:
                            netprem_null = 0
                        else:
                            netprem_null = res['netprem']
                        if res['brokerageprem'] == None or res['brokerageprem'] == False:
                            brokprem_null = 0
                        else:
                            brokprem_null = res['brokerageprem']
                        if res['commssionamt'] == None or res['commssionamt'] == False:
                            comm_null = 0
                        else:
                            comm_null = res['commssionamt']
                        if res['servicetaxamt'] == None or res['servicetaxamt'] == False:
                            sertaxamt_null = 0
                        else:
                            sertaxamt_null = res['servicetaxamt']

                        if f['suminsured'] == None or f['suminsured'] == False:
                            zsuminsur_null = 0
                        else:
                            zsuminsur_null = f['suminsured']
                        if f['grossprem'] == None or f['grossprem'] == False:
                            zgross_null = 0
                        else:
                            zgross_null = f['grossprem']
                        if f['netprem'] == None or f['netprem'] == False:
                            znetprem_null = 0
                        else:
                            znetprem_null = f['netprem']
                        if f['brokerageprem'] == None or f['brokerageprem'] == False:
                            zbrokprem_null = 0
                        else:
                            zbrokprem_null = f['brokerageprem']
                        if f['commssionamt'] == None or f['commssionamt'] == False:
                            zcomm_null = 0
                        else:
                            zcomm_null = f['commssionamt']
                        if f['servicetaxamt'] == None or f['servicetaxamt'] == False:
                            zsertaxamt_null = 0
                        else:
                            zsertaxamt_null = f['servicetaxamt']
                        totalsuminsured += (suminsur_null)
                        totalbrokprem += (brokprem_null)
                        totalgrossprem += (gross_null)
                        totalnetprem += (netprem_null)
                        totalcomm += (comm_null)
                        totalservicetxtamts += (sertaxamt_null)
                        totalothersprems += (res['tp'] + res['tr'] + res['ts'])

                        ztotalsuminsured += (zsuminsur_null)
                        ztotalbrokprem += (zbrokprem_null)
                        ztotalgrossprem += (zgross_null)
                        ztotalnetprem += (znetprem_null)
                        ztotalcomm += (zcomm_null)
                        ztotalservicetxtamts += (zsertaxamt_null)
                        ztotalothersprems += (f['tp'] + f['tr'] + f['ts'])

                        sheet.write(row, 1, s_no_proposaldate, bold_right)
                        sheet.write(row, 2, f['docketno'], bold_center)
                        sheet.write(row, 3, res['docketno'], bold_center)
                        sheet.write(row, 4, res['policystatus'], border1)
                        sheet.write(row, 5, res['policyno'], border1)
                        sheet.write(row, 6, res['endos_no'], border2)
                        sheet.write(row, 7, res['subcategory'], bold_left)
                        sheet.write(row, 8, res['insuredname'], bold_left)
                        sheet.write(row, 9, res['insurername'] + '/' + res['insurerbranch'], bold_left)
                        sheet.write(row, 10, f['co_share'], border)
                        sheet.write(row, 11, znetprem_null, border2)
                        sheet.write(row, 12, zcomm_null, border2)
                        sheet.write(row, 13, res['co_share'], numbersformat1)
                        sheet.write(row, 14, netprem_null, border2)
                        sheet.write(row, 15, comm_null, border2)
                        renewtotalcommcount += totalcomm
                        renewtotalnetprems += totalnetprem
                        frenewtotalcommcount += ztotalcomm
                        frenewtotalnetprems +=  ztotalnetprem
                        break
            row += 1
            # sheet.write(row, 10, str('Renewal'), border)
            sheet.write(row, 9, str('Renewal Business Total'), bold)
            sheet.write(row, 10, ' ', bold)
            sheet.write(row, 11, frenewtotalnetprems, numbersformat)
            sheet.write(row, 12, frenewtotalcommcount, numbersformat)
            sheet.write(row, 13, ' ', numbersformat)
            sheet.write(row, 14, renewtotalnetprems, numbersformat)
            sheet.write(row, 15, renewtotalcommcount, numbersformat)

            # Lost case
            row += 3
            sheet.write(row, 1, 'Lost', border)
            sheet.write(row, 2, ' Business', bold)
            count = 0
            for res in usr_detail_previous:
                count = 0
                for z in usr_detail_lost:
                    if res['prevdocket'] == z['docketno']:
                        # print(res['prevdocket'], z['docketno'], "DATATA")
                        count += 1
                        break
                if count == 0:
                    row += 1
                    s_no_proposaldate += 1
                    suminsur_null = 0
                    gross_null = 0
                    netprem_null = 0
                    brokprem_null = 0
                    comm_null = 0
                    sertaxamt_null = 0
                    brokeragepercent = 0
                    totalsuminsured = 0
                    totalgrossprem = 0
                    totalnetprem = 0
                    totalbrokprem = 0
                    totalcomm = 0
                    totalservicetxtamts = 0
                    totalothersprems = 0

                    if res['suminsured'] == None or res['suminsured'] == False:
                        suminsur_null = 0
                    else:
                        suminsur_null = res['suminsured']
                    if res['grossprem'] == None or res['grossprem'] == False:
                        gross_null = 0
                    else:
                        gross_null = res['grossprem']
                    if res['netprem'] == None or res['netprem'] == False:
                        netprem_null = 0
                    else:
                        netprem_null = res['netprem']
                    if res['brokerageprem'] == None or res['brokerageprem'] == False:
                        brokprem_null = 0
                    else:
                        brokprem_null = res['brokerageprem']
                    if res['commssionamt'] == None or res['commssionamt'] == False:
                        comm_null = 0
                    else:
                        comm_null = res['commssionamt']
                    if res['servicetaxamt'] == None or res['servicetaxamt'] == False:
                        sertaxamt_null = 0
                    else:
                        sertaxamt_null = res['servicetaxamt']

                    totalsuminsured += (suminsur_null)
                    totalbrokprem += (brokprem_null)
                    totalgrossprem += (gross_null)
                    totalnetprem += (netprem_null)
                    totalcomm += (comm_null)
                    totalservicetxtamts += (sertaxamt_null)
                    totalothersprems += (res['tp'] + res['tr'] + res['ts'])

                    sheet.write(row, 1, s_no_proposaldate, bold_right)
                    sheet.write(row, 2, res['docketno'], bold_center)
                    sheet.write(row, 3, '', bold_center)
                    sheet.write(row, 4, res['policystatus'], border1)
                    sheet.write(row, 5, res['policyno'], border1)
                    sheet.write(row, 6, res['endos_no'], border2)
                    sheet.write(row, 7, res['subcategory'], bold_left)
                    sheet.write(row, 8, res['insuredname'], bold_left)
                    sheet.write(row, 9, res['insurername'] + '/' + res['insurerbranch'], bold_left)
                    sheet.write(row, 10, res['co_share'], numbersformat1)
                    sheet.write(row, 11, netprem_null, border2)
                    sheet.write(row, 12, comm_null, border2)
                    sheet.write(row, 13, ' ', numbersformat1)
                    sheet.write(row, 14, ' ', border2)
                    sheet.write(row, 15, ' ', border2)
                    losttotalcommcount += totalcomm
                    losttotalnetprems += totalnetprem
            row += 1
            # sheet.write(row, 10, str('Lost '), border)
            sheet.write(row, 9, str('Lost Business Total'), bold)
            sheet.write(row, 10, ' ', bold)
            sheet.write(row, 11, losttotalnetprems, numbersformat)
            sheet.write(row, 12, losttotalcommcount, numbersformat)
            sheet.write(row, 13, ' ', numbersformat)
            sheet.write(row, 14, ' ', numbersformat)
            sheet.write(row, 15, ' ', numbersformat)
            row += 3
            fgrandnettotal = frenewtotalnetprems + losttotalnetprems
            fgrandcommtotal = frenewtotalnetprems + losttotalnetprems
            grandnettotal = totalnetprems + renewtotalnetprems
            grandcommtotal = totalcommcount + renewtotalcommcount
            sheet.write(row, 9, str('Business Comparison Total'), border)
            sheet.write(row, 10, str(''), bold)
            sheet.write(row, 11, fgrandnettotal, numbersformat)
            sheet.write(row, 12, fgrandcommtotal, numbersformat)
            sheet.write(row, 13, ' ', numbersformat)
            sheet.write(row, 14, grandnettotal, numbersformat)
            sheet.write(row, 15, grandcommtotal, numbersformat)

        elif lines.groupby == 'proposaldate':
            temp = []
            totalcommcount = 0
            totalnetprems = 0

            renewtotalcommcount = 0
            renewtotalnetprems = 0

            frenewtotalcommcount = 0
            frenewtotalnetprems = 0

            losttotalcommcount = 0
            losttotalnetprems = 0

            s_no_proposaldate = 0
            totalcomm_new = 0
            totalnetprem_new = 0

            for res in usr_detail:
                row += 1
                s_no_proposaldate += 1
                suminsur_null = 0
                gross_null = 0
                netprem_null_n = 0
                brokprem_null = 0
                comm_null_n = 0
                sertaxamt_null = 0
                brokeragepercent = 0
                totalsuminsured = 0
                totalgrossprem = 0
                totalcomm_n = 0
                totalnetprem_n = 0
                totalbrokprem = 0

                totalservicetxtamts = 0
                totalothersprems = 0
                if res['suminsured'] == None or res['suminsured'] == False:
                    suminsur_null = 0
                else:
                    suminsur_null = res['suminsured']
                if res['grossprem'] == None or res['grossprem'] == False:
                    gross_null = 0
                else:
                    gross_null = res['grossprem']
                if res['netprem'] == None or res['netprem'] == False:
                    netprem_null_n = 0
                else:
                    netprem_null_n = res['netprem']
                if res['brokerageprem'] == None or res['brokerageprem'] == False:
                    brokprem_null = 0
                else:
                    brokprem_null = res['brokerageprem']
                if res['commssionamt'] == None or res['commssionamt'] == False:
                    comm_null_n = 0
                else:
                    comm_null_n = res['commssionamt']
                if res['servicetaxamt'] == None or res['servicetaxamt'] == False:
                    sertaxamt_null = 0
                else:
                    sertaxamt_null = res['servicetaxamt']

                totalcommcount += comm_null_n
                totalsuminsured += (suminsur_null)
                totalbrokprem += (brokprem_null)
                totalgrossprem += (gross_null)
                totalnetprems += (netprem_null_n)

                totalservicetxtamts += (sertaxamt_null)
                totalothersprems += (res['tp'] + res['tr'] + res['ts'])

                sheet.write(row, 1, s_no_proposaldate, bold_right)
                sheet.write(row, 2, '', bold_center)
                sheet.write(row, 3, res['docketno'], bold_center)
                sheet.write(row, 4, res['policystatus'], border1)
                sheet.write(row, 5, res['policyno'], border1)
                sheet.write(row, 6, res['endos_no'], border2)
                sheet.write(row, 7, res['subcategory'], bold_left)
                sheet.write(row, 8, res['insuredname'], bold_left)
                sheet.write(row, 9, res['insurername'] + '/' + res['insurerbranch'], bold_left)
                sheet.write(row, 10, '', border)
                sheet.write(row, 11, '', border1)
                sheet.write(row, 12, '', border1)
                sheet.write(row, 13, res['co_share'], numbersformat1)
                sheet.write(row, 14, netprem_null_n, border2)
                sheet.write(row, 15, comm_null_n, border2)
                # totalcommcount += comm_null_n
                # totalnet += netprem_null_n
            row += 1
            # sheet.write(row, 11, str('New '), border)
            sheet.write(row, 9, str('New Business Total '), bold)
            sheet.write(row, 10, ' ', numbersformat)
            sheet.write(row, 11, ' ', numbersformat)
            sheet.write(row, 12, ' ', numbersformat)
            sheet.write(row, 13, ' ', numbersformat)
            sheet.write(row, 14, totalnetprems, numbersformat)
            sheet.write(row, 15, totalcommcount, numbersformat)

            row += 3
            sheet.write(row, 1, 'Renewal', border)
            sheet.write(row, 2, ' Business', bold)
            # REnewal case
            for res in usr_detail_previous:  # cuurent renewal
                for f in usr_detail_lost:  # previous dockets
                    if res['prevdocket'] == f['docketno']:
                        row += 1
                        s_no_proposaldate += 1
                        suminsur_null = 0
                        gross_null = 0
                        netprem_null = 0
                        brokprem_null = 0
                        comm_null = 0
                        sertaxamt_null = 0
                        brokeragepercent = 0
                        totalsuminsured = 0
                        totalgrossprem = 0
                        totalnetprem = 0
                        totalbrokprem = 0
                        totalcomm = 0
                        totalservicetxtamts = 0
                        totalothersprems = 0

                        zsuminsur_null = 0
                        zgross_null = 0
                        znetprem_null = 0
                        zbrokprem_null = 0
                        zcomm_null = 0
                        zsertaxamt_null = 0
                        zbrokeragepercent = 0
                        ztotalsuminsured = 0
                        ztotalgrossprem = 0
                        ztotalnetprem = 0
                        ztotalbrokprem = 0
                        ztotalcomm = 0
                        ztotalservicetxtamts = 0
                        ztotalothersprems = 0

                        if res['suminsured'] == None or res['suminsured'] == False:
                            suminsur_null = 0
                        else:
                            suminsur_null = res['suminsured']
                        if res['grossprem'] == None or res['grossprem'] == False:
                            gross_null = 0
                        else:
                            gross_null = res['grossprem']
                        if res['netprem'] == None or res['netprem'] == False:
                            netprem_null = 0
                        else:
                            netprem_null = res['netprem']
                        if res['brokerageprem'] == None or res['brokerageprem'] == False:
                            brokprem_null = 0
                        else:
                            brokprem_null = res['brokerageprem']
                        if res['commssionamt'] == None or res['commssionamt'] == False:
                            comm_null = 0
                        else:
                            comm_null = res['commssionamt']
                        if res['servicetaxamt'] == None or res['servicetaxamt'] == False:
                            sertaxamt_null = 0
                        else:
                            sertaxamt_null = res['servicetaxamt']

                        if f['suminsured'] == None or f['suminsured'] == False:
                            zsuminsur_null = 0
                        else:
                            zsuminsur_null = f['suminsured']
                        if f['grossprem'] == None or f['grossprem'] == False:
                            zgross_null = 0
                        else:
                            zgross_null = f['grossprem']
                        if f['netprem'] == None or f['netprem'] == False:
                            znetprem_null = 0
                        else:
                            znetprem_null = f['netprem']
                        if f['brokerageprem'] == None or f['brokerageprem'] == False:
                            zbrokprem_null = 0
                        else:
                            zbrokprem_null = f['brokerageprem']
                        if f['commssionamt'] == None or f['commssionamt'] == False:
                            zcomm_null = 0
                        else:
                            zcomm_null = f['commssionamt']
                        if f['servicetaxamt'] == None or f['servicetaxamt'] == False:
                            zsertaxamt_null = 0
                        else:
                            zsertaxamt_null = f['servicetaxamt']
                        totalsuminsured += (suminsur_null)
                        totalbrokprem += (brokprem_null)
                        totalgrossprem += (gross_null)
                        totalnetprem += (netprem_null)
                        totalcomm += (comm_null)
                        totalservicetxtamts += (sertaxamt_null)
                        totalothersprems += (res['tp'] + res['tr'] + res['ts'])

                        ztotalsuminsured += (zsuminsur_null)
                        ztotalbrokprem += (zbrokprem_null)
                        ztotalgrossprem += (zgross_null)
                        ztotalnetprem += (znetprem_null)
                        ztotalcomm += (zcomm_null)
                        ztotalservicetxtamts += (zsertaxamt_null)
                        ztotalothersprems += (f['tp'] + f['tr'] + f['ts'])

                        sheet.write(row, 1, s_no_proposaldate, bold_right)
                        sheet.write(row, 2, f['docketno'], bold_center)
                        sheet.write(row, 3, res['docketno'], bold_center)
                        sheet.write(row, 4, res['policystatus'], border1)
                        sheet.write(row, 5, res['policyno'], border1)
                        sheet.write(row, 6, res['endos_no'], border2)
                        sheet.write(row, 7, res['subcategory'], bold_left)
                        sheet.write(row, 8, res['insuredname'], bold_left)
                        sheet.write(row, 9, res['insurername'] + '/' + res['insurerbranch'], bold_left)
                        sheet.write(row, 10, f['co_share'], border)
                        sheet.write(row, 11, znetprem_null, border2)
                        sheet.write(row, 12, zcomm_null, border2)
                        sheet.write(row, 13, res['co_share'], numbersformat1)
                        sheet.write(row, 14, netprem_null, border2)
                        sheet.write(row, 15, comm_null, border2)
                        renewtotalcommcount += totalcomm
                        renewtotalnetprems += totalnetprem
                        frenewtotalcommcount += ztotalcomm
                        frenewtotalnetprems +=  ztotalnetprem
                        break
            row += 1
            # sheet.write(row, 10, str('Renewal'), border)
            sheet.write(row, 9, str('Renewal Business Total'), bold)
            sheet.write(row, 10, ' ', bold)
            sheet.write(row, 11, frenewtotalnetprems, numbersformat)
            sheet.write(row, 12, frenewtotalcommcount, numbersformat)
            sheet.write(row, 13, ' ', numbersformat)
            sheet.write(row, 14, renewtotalnetprems, numbersformat)
            sheet.write(row, 15, renewtotalcommcount, numbersformat)

            # Lost case
            row += 3
            sheet.write(row, 1, 'Lost', border)
            sheet.write(row, 2, ' Business', bold)
            count = 0
            for res in usr_detail_previous:
                count = 0
                for z in usr_detail_lost:
                    if res['prevdocket'] == z['docketno']:
                        # print(res['prevdocket'], z['docketno'], "DATATA")
                        count += 1
                        break
                if count == 0:
                    row += 1
                    s_no_proposaldate += 1
                    suminsur_null = 0
                    gross_null = 0
                    netprem_null = 0
                    brokprem_null = 0
                    comm_null = 0
                    sertaxamt_null = 0
                    brokeragepercent = 0
                    totalsuminsured = 0
                    totalgrossprem = 0
                    totalnetprem = 0
                    totalbrokprem = 0
                    totalcomm = 0
                    totalservicetxtamts = 0
                    totalothersprems = 0

                    if res['suminsured'] == None or res['suminsured'] == False:
                        suminsur_null = 0
                    else:
                        suminsur_null = res['suminsured']
                    if res['grossprem'] == None or res['grossprem'] == False:
                        gross_null = 0
                    else:
                        gross_null = res['grossprem']
                    if res['netprem'] == None or res['netprem'] == False:
                        netprem_null = 0
                    else:
                        netprem_null = res['netprem']
                    if res['brokerageprem'] == None or res['brokerageprem'] == False:
                        brokprem_null = 0
                    else:
                        brokprem_null = res['brokerageprem']
                    if res['commssionamt'] == None or res['commssionamt'] == False:
                        comm_null = 0
                    else:
                        comm_null = res['commssionamt']
                    if res['servicetaxamt'] == None or res['servicetaxamt'] == False:
                        sertaxamt_null = 0
                    else:
                        sertaxamt_null = res['servicetaxamt']

                    totalsuminsured += (suminsur_null)
                    totalbrokprem += (brokprem_null)
                    totalgrossprem += (gross_null)
                    totalnetprem += (netprem_null)
                    totalcomm += (comm_null)
                    totalservicetxtamts += (sertaxamt_null)
                    totalothersprems += (res['tp'] + res['tr'] + res['ts'])

                    sheet.write(row, 1, s_no_proposaldate, bold_right)
                    sheet.write(row, 2, res['docketno'], bold_center)
                    sheet.write(row, 3, '', bold_center)
                    sheet.write(row, 4, res['policystatus'], border1)
                    sheet.write(row, 5, res['policyno'], border1)
                    sheet.write(row, 6, res['endos_no'], border2)
                    sheet.write(row, 7, res['subcategory'], bold_left)
                    sheet.write(row, 8, res['insuredname'], bold_left)
                    sheet.write(row, 9, res['insurername'] + '/' + res['insurerbranch'], bold_left)
                    sheet.write(row, 10, res['co_share'], numbersformat1)
                    sheet.write(row, 11, netprem_null, border2)
                    sheet.write(row, 12, comm_null, border2)
                    sheet.write(row, 13, ' ', numbersformat1)
                    sheet.write(row, 14, ' ', border2)
                    sheet.write(row, 15, ' ', border2)
                    losttotalcommcount += totalcomm
                    losttotalnetprems += totalnetprem
            row += 1
            # sheet.write(row, 10, str('Lost '), border)
            sheet.write(row, 9, str('Lost Business Total'), bold)
            sheet.write(row, 10, ' ', bold)
            sheet.write(row, 11, losttotalnetprems, numbersformat)
            sheet.write(row, 12, losttotalcommcount, numbersformat)
            sheet.write(row, 13, ' ', numbersformat)
            sheet.write(row, 14, ' ', numbersformat)
            sheet.write(row, 15, ' ', numbersformat)
            row += 3
            fgrandnettotal = frenewtotalnetprems + losttotalnetprems
            fgrandcommtotal = frenewtotalnetprems + losttotalnetprems
            grandnettotal = totalnetprems + renewtotalnetprems
            grandcommtotal = totalcommcount + renewtotalcommcount
            sheet.write(row, 9, str('Business Comparison Total'), border)
            sheet.write(row, 10, str(''), bold)
            sheet.write(row, 11, fgrandnettotal, numbersformat)
            sheet.write(row, 12, fgrandcommtotal, numbersformat)
            sheet.write(row, 13, ' ', numbersformat)
            sheet.write(row, 14, grandnettotal, numbersformat)
            sheet.write(row, 15, grandcommtotal, numbersformat)


        elif lines.groupby == 'startdate':
            temp = []
            totalcommcount = 0
            totalnetprems = 0

            renewtotalcommcount = 0
            renewtotalnetprems = 0

            frenewtotalcommcount = 0
            frenewtotalnetprems = 0

            losttotalcommcount = 0
            losttotalnetprems = 0

            s_no_proposaldate = 0
            totalcomm_new = 0
            totalnetprem_new = 0

            for res in usr_detail:
                row += 1
                s_no_proposaldate += 1
                suminsur_null = 0
                gross_null = 0
                netprem_null_n = 0
                brokprem_null = 0
                comm_null_n = 0
                sertaxamt_null = 0
                brokeragepercent = 0
                totalsuminsured = 0
                totalgrossprem = 0
                totalcomm_n = 0
                totalnetprem_n = 0
                totalbrokprem = 0

                totalservicetxtamts = 0
                totalothersprems = 0
                if res['suminsured'] == None or res['suminsured'] == False:
                    suminsur_null = 0
                else:
                    suminsur_null = res['suminsured']
                if res['grossprem'] == None or res['grossprem'] == False:
                    gross_null = 0
                else:
                    gross_null = res['grossprem']
                if res['netprem'] == None or res['netprem'] == False:
                    netprem_null_n = 0
                else:
                    netprem_null_n = res['netprem']
                if res['brokerageprem'] == None or res['brokerageprem'] == False:
                    brokprem_null = 0
                else:
                    brokprem_null = res['brokerageprem']
                if res['commssionamt'] == None or res['commssionamt'] == False:
                    comm_null_n = 0
                else:
                    comm_null_n = res['commssionamt']
                if res['servicetaxamt'] == None or res['servicetaxamt'] == False:
                    sertaxamt_null = 0
                else:
                    sertaxamt_null = res['servicetaxamt']

                totalcommcount += comm_null_n
                totalsuminsured += (suminsur_null)
                totalbrokprem += (brokprem_null)
                totalgrossprem += (gross_null)
                totalnetprems += (netprem_null_n)

                totalservicetxtamts += (sertaxamt_null)
                totalothersprems += (res['tp'] + res['tr'] + res['ts'])

                sheet.write(row, 1, s_no_proposaldate, bold_right)
                sheet.write(row, 2, '', bold_center)
                sheet.write(row, 3, res['docketno'], bold_center)
                sheet.write(row, 4, res['policystatus'], border1)
                sheet.write(row, 5, res['policyno'], border1)
                sheet.write(row, 6, res['endos_no'], border2)
                sheet.write(row, 7, res['subcategory'], bold_left)
                sheet.write(row, 8, res['insuredname'], bold_left)
                sheet.write(row, 9, res['insurername'] + '/' + res['insurerbranch'], bold_left)
                sheet.write(row, 10, '', border)
                sheet.write(row, 11, '', border1)
                sheet.write(row, 12, '', border1)
                sheet.write(row, 13, res['co_share'], numbersformat1)
                sheet.write(row, 14, netprem_null_n, border2)
                sheet.write(row, 15, comm_null_n, border2)
                # totalcomm_new += comm_null_n
                # totalnetprem_new += netprem_null_n
            row += 1
            # sheet.write(row, 11, str('New '), border)
            sheet.write(row, 9, str('New Business Total '), bold)
            sheet.write(row, 10, ' ', numbersformat)
            sheet.write(row, 11, ' ', numbersformat)
            sheet.write(row, 12, ' ', numbersformat)
            sheet.write(row, 13, ' ', numbersformat)
            sheet.write(row, 14, totalnetprems, numbersformat)
            sheet.write(row, 15, totalcommcount, numbersformat)

            row += 3
            sheet.write(row, 1, 'Renewal', border)
            sheet.write(row, 2, ' Business', bold)
            # REnewal case
            for res in usr_detail_previous:  # cuurent renewal
                # for f in usr_detail_lost:  # previous dockets
                #     if res['prevdocket'] == f['docketno']:
                        previous_year_data = self.env['policytransaction'].sudo().search([('name','=',res['prevdocket'])])
                        # print(previous_year_data,"DATAA")
                        row += 1
                        s_no_proposaldate += 1
                        suminsur_null = 0
                        gross_null = 0
                        netprem_null = 0
                        brokprem_null = 0
                        comm_null = 0
                        sertaxamt_null = 0
                        brokeragepercent = 0
                        totalsuminsured = 0
                        totalgrossprem = 0
                        totalnetprem = 0
                        totalbrokprem = 0
                        totalcomm = 0
                        totalservicetxtamts = 0
                        totalothersprems = 0

                        zsuminsur_null = 0
                        zgross_null = 0
                        znetprem_null = 0
                        zbrokprem_null = 0
                        zcomm_null = 0
                        zsertaxamt_null = 0
                        zbrokeragepercent = 0
                        ztotalsuminsured = 0
                        ztotalgrossprem = 0
                        ztotalnetprem = 0
                        ztotalbrokprem = 0
                        ztotalcomm = 0
                        ztotalservicetxtamts = 0
                        ztotalothersprems = 0

                        if res['suminsured'] == None or res['suminsured'] == False:
                            suminsur_null = 0
                        else:
                            suminsur_null = res['suminsured']
                        if res['grossprem'] == None or res['grossprem'] == False:
                            gross_null = 0
                        else:
                            gross_null = res['grossprem']
                        if res['netprem'] == None or res['netprem'] == False:
                            netprem_null = 0
                        else:
                            netprem_null = res['netprem']
                        if res['brokerageprem'] == None or res['brokerageprem'] == False:
                            brokprem_null = 0
                        else:
                            brokprem_null = res['brokerageprem']
                        if res['commssionamt'] == None or res['commssionamt'] == False:
                            comm_null = 0
                        else:
                            comm_null = res['commssionamt']
                        if res['servicetaxamt'] == None or res['servicetaxamt'] == False:
                            sertaxamt_null = 0
                        else:
                            sertaxamt_null = res['servicetaxamt']

                        if previous_year_data.suminsured == None or previous_year_data.suminsured == False:
                            zsuminsur_null = 0
                        else:
                            zsuminsur_null = previous_year_data.suminsured
                        if previous_year_data.grossprem == None or previous_year_data.grossprem == False:
                            zgross_null = 0
                        else:
                            zgross_null = previous_year_data.grossprem
                        if previous_year_data.netprem == None or previous_year_data.netprem == False:
                            znetprem_null = 0
                        else:
                            znetprem_null = previous_year_data.netprem
                        if previous_year_data.brokerageprem == None or previous_year_data.brokerageprem == False:
                            zbrokprem_null = 0
                        else:
                            zbrokprem_null = previous_year_data.brokerageprem
                        if previous_year_data.commssionamt == None or previous_year_data.commssionamt == False:
                            zcomm_null = 0
                        else:
                            zcomm_null = previous_year_data.commssionamt
                        if previous_year_data.servicetaxamt == None or previous_year_data.servicetaxamt == False:
                            zsertaxamt_null = 0
                        else:
                            zsertaxamt_null = previous_year_data.servicetaxamt
                        totalsuminsured += (suminsur_null)
                        totalbrokprem += (brokprem_null)
                        totalgrossprem += (gross_null)
                        totalnetprem += (netprem_null)
                        totalcomm += (comm_null)
                        totalservicetxtamts += (sertaxamt_null)
                        totalothersprems += (res['tp'] + res['tr'] + res['ts'])

                        ztotalsuminsured += (zsuminsur_null)
                        ztotalbrokprem += (zbrokprem_null)
                        ztotalgrossprem += (zgross_null)
                        ztotalnetprem += (znetprem_null)
                        ztotalcomm += (zcomm_null)
                        ztotalservicetxtamts += (zsertaxamt_null)
                        ztotalothersprems += (previous_year_data.tppremium + previous_year_data.terrprem + previous_year_data.stamprem)

                        sheet.write(row, 1, s_no_proposaldate, bold_right)
                        sheet.write(row, 2, res['prevdocket'], bold_center)
                        sheet.write(row, 3, res['docketno'], bold_center)
                        sheet.write(row, 4, res['policystatus'], border1)
                        sheet.write(row, 5, res['policyno'], border1)
                        sheet.write(row, 6, res['endos_no'], border2)
                        sheet.write(row, 7, res['subcategory'], bold_left)
                        sheet.write(row, 8, res['insuredname'], bold_left)
                        sheet.write(row, 9, res['insurername'] + '/' + res['insurerbranch'], bold_left)
                        sheet.write(row, 10, res['co_share'], border)
                        sheet.write(row, 11, znetprem_null, border2)
                        sheet.write(row, 12, zcomm_null, border2)
                        sheet.write(row, 13, res['co_share'], numbersformat1)
                        sheet.write(row, 14, netprem_null, border2)
                        sheet.write(row, 15, comm_null, border2)
                        renewtotalcommcount += totalcomm
                        renewtotalnetprems += totalnetprem
                        frenewtotalcommcount += ztotalcomm
                        frenewtotalnetprems +=  ztotalnetprem
                        # break
            row += 1
            # sheet.write(row, 10, str('Renewal'), border)
            sheet.write(row, 9, str('Renewal Business Total'), bold)
            sheet.write(row, 10, ' ', bold)
            sheet.write(row, 11, frenewtotalnetprems, numbersformat)
            sheet.write(row, 12, frenewtotalcommcount, numbersformat)
            sheet.write(row, 13, ' ', numbersformat)
            sheet.write(row, 14, renewtotalnetprems, numbersformat)
            sheet.write(row, 15, renewtotalcommcount, numbersformat)

            # Lost case
            row += 3
            sheet.write(row, 1, 'Lost', border)
            sheet.write(row, 2, ' Business', bold)
            print(len(usr_lost_data),len(usr_detail_lost),"DATATAT")
            for res in usr_detail_lost: #renewal data of the current year exclude endoserment data array
                count = 0
                for z in usr_lost_data:
                    if res['docketno'] == z['prevdocket']:
                        count += 1
                        break
                if count == 0:
                    row += 1
                    s_no_proposaldate += 1
                    suminsur_null = 0
                    gross_null = 0
                    netprem_null = 0
                    brokprem_null = 0
                    comm_null = 0
                    sertaxamt_null = 0
                    brokeragepercent = 0
                    totalsuminsured = 0
                    totalgrossprem = 0
                    totalnetprem = 0
                    totalbrokprem = 0
                    totalcomm = 0
                    totalservicetxtamts = 0
                    totalothersprems = 0

                    if res['suminsured'] == None or res['suminsured'] == False:
                        suminsur_null = 0
                    else:
                        suminsur_null = res['suminsured']
                    if res['grossprem'] == None or res['grossprem'] == False:
                        gross_null = 0
                    else:
                        gross_null = res['grossprem']
                    if res['netprem'] == None or res['netprem'] == False:
                        netprem_null = 0
                    else:
                        netprem_null = res['netprem']
                    if res['brokerageprem'] == None or res['brokerageprem'] == False:
                        brokprem_null = 0
                    else:
                        brokprem_null = res['brokerageprem']
                    if res['commssionamt'] == None or res['commssionamt'] == False:
                        comm_null = 0
                    else:
                        comm_null = res['commssionamt']
                    if res['servicetaxamt'] == None or res['servicetaxamt'] == False:
                        sertaxamt_null = 0
                    else:
                        sertaxamt_null = res['servicetaxamt']

                    totalsuminsured += (suminsur_null)
                    totalbrokprem += (brokprem_null)
                    totalgrossprem += (gross_null)
                    totalnetprem += (netprem_null)
                    totalcomm += (comm_null)
                    totalservicetxtamts += (sertaxamt_null)
                    totalothersprems += (res['tp'] + res['tr'] + res['ts'])

                    sheet.write(row, 1, s_no_proposaldate, bold_right)
                    sheet.write(row, 2, res['docketno'], bold_center)
                    sheet.write(row, 3, '', bold_center)
                    sheet.write(row, 4, res['policystatus'], border1)
                    sheet.write(row, 5, res['policyno'], border1)
                    sheet.write(row, 6, res['endos_no'], border2)
                    sheet.write(row, 7, res['subcategory'], bold_left)
                    sheet.write(row, 8, res['insuredname'], bold_left)
                    sheet.write(row, 9, res['insurername'] + '/' + res['insurerbranch'], bold_left)
                    sheet.write(row, 10, res['co_share'], numbersformat1)
                    sheet.write(row, 11, netprem_null, border2)
                    sheet.write(row, 12, comm_null, border2)
                    sheet.write(row, 13, ' ', numbersformat1)
                    sheet.write(row, 14, ' ', border2)
                    sheet.write(row, 15, ' ', border2)
                    losttotalcommcount += totalcomm
                    losttotalnetprems += totalnetprem
            row += 1
            # sheet.write(row, 10, str('Lost '), border)
            sheet.write(row, 9, str('Lost Business Total'), bold)
            sheet.write(row, 10, ' ', bold)
            sheet.write(row, 11, losttotalnetprems, numbersformat)
            sheet.write(row, 12, losttotalcommcount, numbersformat)
            sheet.write(row, 13, ' ', numbersformat)
            sheet.write(row, 14, ' ', numbersformat)
            sheet.write(row, 15, ' ', numbersformat)
            row += 3
            fgrandnettotal = frenewtotalnetprems + losttotalnetprems
            fgrandcommtotal = frenewtotalnetprems + losttotalnetprems
            grandnettotal = totalnetprems + renewtotalnetprems
            grandcommtotal = totalcommcount + renewtotalcommcount
            sheet.write(row, 9, str('Business Comparison Total'), border)
            sheet.write(row, 10, str(''), bold)
            sheet.write(row, 11, fgrandnettotal, numbersformat)
            sheet.write(row, 12, fgrandcommtotal, numbersformat)
            sheet.write(row, 13, ' ', numbersformat)
            sheet.write(row, 14, grandnettotal, numbersformat)
            sheet.write(row, 15, grandcommtotal, numbersformat)



        else:
            temp = []
            totalcommcount = 0
            totalnetprems = 0

            renewtotalcommcount = 0
            renewtotalnetprems = 0

            frenewtotalcommcount = 0
            frenewtotalnetprems = 0

            losttotalcommcount = 0
            losttotalnetprems = 0

            s_no_proposaldate = 0
            totalcomm_new = 0
            totalnetprem_new = 0

            for res in usr_detail:
                row += 1
                s_no_proposaldate += 1
                suminsur_null = 0
                gross_null = 0
                netprem_null_n = 0
                brokprem_null = 0
                comm_null_n = 0
                sertaxamt_null = 0
                brokeragepercent = 0
                totalsuminsured = 0
                totalgrossprem = 0
                totalcomm_n = 0
                totalnetprem_n = 0
                totalbrokprem = 0

                totalservicetxtamts = 0
                totalothersprems = 0
                if res['suminsured'] == None or res['suminsured'] == False:
                    suminsur_null = 0
                else:
                    suminsur_null = res['suminsured']
                if res['grossprem'] == None or res['grossprem'] == False:
                    gross_null = 0
                else:
                    gross_null = res['grossprem']
                if res['netprem'] == None or res['netprem'] == False:
                    netprem_null_n = 0
                else:
                    netprem_null_n = res['netprem']
                if res['brokerageprem'] == None or res['brokerageprem'] == False:
                    brokprem_null = 0
                else:
                    brokprem_null = res['brokerageprem']
                if res['commssionamt'] == None or res['commssionamt'] == False:
                    comm_null_n = 0
                else:
                    comm_null_n = res['commssionamt']
                if res['servicetaxamt'] == None or res['servicetaxamt'] == False:
                    sertaxamt_null = 0
                else:
                    sertaxamt_null = res['servicetaxamt']

                totalcommcount += comm_null_n
                totalsuminsured += (suminsur_null)
                totalbrokprem += (brokprem_null)
                totalgrossprem += (gross_null)
                totalnetprems += (netprem_null_n)

                totalservicetxtamts += (sertaxamt_null)
                totalothersprems += (res['tp'] + res['tr'] + res['ts'])

                sheet.write(row, 1, s_no_proposaldate, bold_right)
                sheet.write(row, 2, '', bold_center)
                sheet.write(row, 3, res['docketno'], bold_center)
                sheet.write(row, 4, res['policystatus'], border1)
                sheet.write(row, 5, res['policyno'], border1)
                sheet.write(row, 6, res['endos_no'], border2)
                sheet.write(row, 7, res['subcategory'], bold_left)
                sheet.write(row, 8, res['insuredname'], bold_left)
                sheet.write(row, 9, res['insurername'] + '/' + res['insurerbranch'], bold_left)
                sheet.write(row, 10, '', border)
                sheet.write(row, 11, '', border1)
                sheet.write(row, 12, '', border1)
                sheet.write(row, 13, res['co_share'], numbersformat1)
                sheet.write(row, 14, netprem_null_n, border2)
                sheet.write(row, 15, comm_null_n, border2)
                # totalcomm_new += comm_null_n
                # totalnetprem_new += netprem_null_n
            row += 1
            # sheet.write(row, 11, str('New '), border)
            sheet.write(row, 9, str('New Business Total '), bold)
            sheet.write(row, 10, ' ', numbersformat)
            sheet.write(row, 11, ' ', numbersformat)
            sheet.write(row, 12, ' ', numbersformat)
            sheet.write(row, 13, ' ', numbersformat)
            sheet.write(row, 14, totalnetprems, numbersformat)
            sheet.write(row, 15, totalcommcount, numbersformat)

            row += 3
            sheet.write(row, 1, 'Renewal', border)
            sheet.write(row, 2, ' Business', bold)
            # REnewal case
            for res in usr_detail_previous:  # cuurent renewal
                for f in usr_detail_lost:  # previous dockets
                    if res['prevdocket'] == f['docketno']:
                        row += 1
                        s_no_proposaldate += 1
                        suminsur_null = 0
                        gross_null = 0
                        netprem_null = 0
                        brokprem_null = 0
                        comm_null = 0
                        sertaxamt_null = 0
                        brokeragepercent = 0
                        totalsuminsured = 0
                        totalgrossprem = 0
                        totalnetprem = 0
                        totalbrokprem = 0
                        totalcomm = 0
                        totalservicetxtamts = 0
                        totalothersprems = 0

                        zsuminsur_null = 0
                        zgross_null = 0
                        znetprem_null = 0
                        zbrokprem_null = 0
                        zcomm_null = 0
                        zsertaxamt_null = 0
                        zbrokeragepercent = 0
                        ztotalsuminsured = 0
                        ztotalgrossprem = 0
                        ztotalnetprem = 0
                        ztotalbrokprem = 0
                        ztotalcomm = 0
                        ztotalservicetxtamts = 0
                        ztotalothersprems = 0

                        if res['suminsured'] == None or res['suminsured'] == False:
                            suminsur_null = 0
                        else:
                            suminsur_null = res['suminsured']
                        if res['grossprem'] == None or res['grossprem'] == False:
                            gross_null = 0
                        else:
                            gross_null = res['grossprem']
                        if res['netprem'] == None or res['netprem'] == False:
                            netprem_null = 0
                        else:
                            netprem_null = res['netprem']
                        if res['brokerageprem'] == None or res['brokerageprem'] == False:
                            brokprem_null = 0
                        else:
                            brokprem_null = res['brokerageprem']
                        if res['commssionamt'] == None or res['commssionamt'] == False:
                            comm_null = 0
                        else:
                            comm_null = res['commssionamt']
                        if res['servicetaxamt'] == None or res['servicetaxamt'] == False:
                            sertaxamt_null = 0
                        else:
                            sertaxamt_null = res['servicetaxamt']

                        if f['suminsured'] == None or f['suminsured'] == False:
                            zsuminsur_null = 0
                        else:
                            zsuminsur_null = f['suminsured']
                        if f['grossprem'] == None or f['grossprem'] == False:
                            zgross_null = 0
                        else:
                            zgross_null = f['grossprem']
                        if f['netprem'] == None or f['netprem'] == False:
                            znetprem_null = 0
                        else:
                            znetprem_null = f['netprem']
                        if f['brokerageprem'] == None or f['brokerageprem'] == False:
                            zbrokprem_null = 0
                        else:
                            zbrokprem_null = f['brokerageprem']
                        if f['commssionamt'] == None or f['commssionamt'] == False:
                            zcomm_null = 0
                        else:
                            zcomm_null = f['commssionamt']
                        if f['servicetaxamt'] == None or f['servicetaxamt'] == False:
                            zsertaxamt_null = 0
                        else:
                            zsertaxamt_null = f['servicetaxamt']
                        totalsuminsured += (suminsur_null)
                        totalbrokprem += (brokprem_null)
                        totalgrossprem += (gross_null)
                        totalnetprem += (netprem_null)
                        totalcomm += (comm_null)
                        totalservicetxtamts += (sertaxamt_null)
                        totalothersprems += (res['tp'] + res['tr'] + res['ts'])

                        ztotalsuminsured += (zsuminsur_null)
                        ztotalbrokprem += (zbrokprem_null)
                        ztotalgrossprem += (zgross_null)
                        ztotalnetprem += (znetprem_null)
                        ztotalcomm += (zcomm_null)
                        ztotalservicetxtamts += (zsertaxamt_null)
                        ztotalothersprems += (f['tp'] + f['tr'] + f['ts'])

                        sheet.write(row, 1, s_no_proposaldate, bold_right)
                        sheet.write(row, 2, f['docketno'], bold_center)
                        sheet.write(row, 3, res['docketno'], bold_center)
                        sheet.write(row, 4, res['policystatus'], border1)
                        sheet.write(row, 5, res['policyno'], border1)
                        sheet.write(row, 6, res['endos_no'], border2)
                        sheet.write(row, 7, res['subcategory'], bold_left)
                        sheet.write(row, 8, res['insuredname'], bold_left)
                        sheet.write(row, 9, res['insurername'] + '/' + res['insurerbranch'], bold_left)
                        sheet.write(row, 10, f['co_share'], border)
                        sheet.write(row, 11, znetprem_null, border2)
                        sheet.write(row, 12, zcomm_null, border2)
                        sheet.write(row, 13, res['co_share'], numbersformat1)
                        sheet.write(row, 14, netprem_null, border2)
                        sheet.write(row, 15, comm_null, border2)
                        renewtotalcommcount += totalcomm
                        renewtotalnetprems += totalnetprem
                        frenewtotalcommcount += ztotalcomm
                        frenewtotalnetprems +=  ztotalnetprem
                        break
            row += 1
            # sheet.write(row, 10, str('Renewal'), border)
            sheet.write(row, 9, str('Renewal Business Total'), bold)
            sheet.write(row, 10, ' ', bold)
            sheet.write(row, 11, frenewtotalnetprems, numbersformat)
            sheet.write(row, 12, frenewtotalcommcount, numbersformat)
            sheet.write(row, 13, ' ', numbersformat)
            sheet.write(row, 14, renewtotalnetprems, numbersformat)
            sheet.write(row, 15, renewtotalcommcount, numbersformat)

            # Lost case
            row += 3
            sheet.write(row, 1, 'Lost', border)
            sheet.write(row, 2, ' Business', bold)
            count = 0
            for res in usr_detail_previous:
                count = 0
                for z in usr_detail_lost:
                    if res['prevdocket'] == z['docketno']:
                        # print(res['prevdocket'], z['docketno'], "DATATA")
                        count += 1
                        break
                if count == 0:
                    row += 1
                    s_no_proposaldate += 1
                    suminsur_null = 0
                    gross_null = 0
                    netprem_null = 0
                    brokprem_null = 0
                    comm_null = 0
                    sertaxamt_null = 0
                    brokeragepercent = 0
                    totalsuminsured = 0
                    totalgrossprem = 0
                    totalnetprem = 0
                    totalbrokprem = 0
                    totalcomm = 0
                    totalservicetxtamts = 0
                    totalothersprems = 0

                    if res['suminsured'] == None or res['suminsured'] == False:
                        suminsur_null = 0
                    else:
                        suminsur_null = res['suminsured']
                    if res['grossprem'] == None or res['grossprem'] == False:
                        gross_null = 0
                    else:
                        gross_null = res['grossprem']
                    if res['netprem'] == None or res['netprem'] == False:
                        netprem_null = 0
                    else:
                        netprem_null = res['netprem']
                    if res['brokerageprem'] == None or res['brokerageprem'] == False:
                        brokprem_null = 0
                    else:
                        brokprem_null = res['brokerageprem']
                    if res['commssionamt'] == None or res['commssionamt'] == False:
                        comm_null = 0
                    else:
                        comm_null = res['commssionamt']
                    if res['servicetaxamt'] == None or res['servicetaxamt'] == False:
                        sertaxamt_null = 0
                    else:
                        sertaxamt_null = res['servicetaxamt']

                    totalsuminsured += (suminsur_null)
                    totalbrokprem += (brokprem_null)
                    totalgrossprem += (gross_null)
                    totalnetprem += (netprem_null)
                    totalcomm += (comm_null)
                    totalservicetxtamts += (sertaxamt_null)
                    totalothersprems += (res['tp'] + res['tr'] + res['ts'])

                    sheet.write(row, 1, s_no_proposaldate, bold_right)
                    sheet.write(row, 2, res['docketno'], bold_center)
                    sheet.write(row, 3, '', bold_center)
                    sheet.write(row, 4, res['policystatus'], border1)
                    sheet.write(row, 5, res['policyno'], border1)
                    sheet.write(row, 6, res['endos_no'], border2)
                    sheet.write(row, 7, res['subcategory'], bold_left)
                    sheet.write(row, 8, res['insuredname'], bold_left)
                    sheet.write(row, 9, res['insurername'] + '/' + res['insurerbranch'], bold_left)
                    sheet.write(row, 10, res['co_share'], numbersformat1)
                    sheet.write(row, 11, netprem_null, border2)
                    sheet.write(row, 12, comm_null, border2)
                    sheet.write(row, 13, ' ', numbersformat1)
                    sheet.write(row, 14, ' ', border2)
                    sheet.write(row, 15, ' ', border2)
                    losttotalcommcount += totalcomm
                    losttotalnetprems += totalnetprem
            row += 1
            # sheet.write(row, 10, str('Lost '), border)
            sheet.write(row, 9, str('Lost Business Total'), bold)
            sheet.write(row, 10, ' ', bold)
            sheet.write(row, 11, losttotalnetprems, numbersformat)
            sheet.write(row, 12, losttotalcommcount, numbersformat)
            sheet.write(row, 13, ' ', numbersformat)
            sheet.write(row, 14, ' ', numbersformat)
            sheet.write(row, 15, ' ', numbersformat)
            row += 3
            fgrandnettotal = frenewtotalnetprems + losttotalnetprems
            fgrandcommtotal = frenewtotalnetprems + losttotalnetprems
            grandnettotal = totalnetprems + renewtotalnetprems
            grandcommtotal = totalcommcount + renewtotalcommcount
            sheet.write(row, 9, str('Business Comparison Total'), border)
            sheet.write(row, 10, str(''), bold)
            sheet.write(row, 11, fgrandnettotal, numbersformat)
            sheet.write(row, 12, fgrandcommtotal, numbersformat)
            sheet.write(row, 13, ' ', numbersformat)
            sheet.write(row, 14, grandnettotal, numbersformat)
            sheet.write(row, 15, grandcommtotal, numbersformat)



    def querys(self, workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1, end_year,
               prev_date_start, prev_date_end, id=None,
               endo=None):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        with registry.cursor() as cr:
            query = "select t1.prevdocket,case when t8.co_insurer_id is not null then t8.co_share else 100 end as co_share," \
                    " case when t8.co_insurer_id is not null then t9.name else t3.name end as insurername," \
                    " case when t8.co_insurer_id is not null then t10.name else t2.name end as insurerbranch," \
                    " COALESCE(SUM(t1.tppremium),0) AS tp,COALESCE(SUM(t1.terrprem),0) AS tr,COALESCE(SUM(t1.stamprem),0) AS ts," \
                    " t4.name as insuredname, t1.name as docketno,t1.id,t11.name as policystatus,t7.name as subcategory,t1.policyno as policyno," \
                    " t1.date2 as docketdate,t8.co_insurer_id,t1.proposaldate as proposaldate,t1.startfrom as startdate,'' as endos_no,t1.expiry as enddate," \
                    " case when t8.co_insurer_id is not null  then sum(t8.co_net_premium) else sum(t1.netprem) end as netprem," \
                    " case when t8.co_insurer_id is not null  then sum(t8.co_net_gross_pre) else sum(t1.grossprem) end  as grossprem," \
                    " case when t8.co_insurer_id is not null then sum(t8.co_sum_insured) else sum(t1.suminsured) end  as suminsured," \
                    " case when t8.co_insurer_id is not null then sum(t8.co_brokerage_pre) else sum(t1.brokerageprem) end  as brokerageprem," \
                    " case when t8.co_insurer_id is not null then sum(t8.co_commission_amount) else  sum(t1.commssionamt) end  as commssionamt," \
                    " case when t8.co_insurer_id is not null then sum(t8.co_commission) else  sum(t1.rate) end  as rate," \
                    " case when t8.co_insurer_id is not null then sum(t8.co_gst_amount) else sum(t1.servicetaxamt) end  as servicetaxamt" \
                    " from policytransaction as t1 left join insurerbranch as t2 on t2.id = t1.insurerbranch" \
                    " left join res_partner as t3 on t3.id=t1.insurername123" \
                    " left join res_partner as t4 on t4.id=t1.clientname" \
                    " left join subdata_subdata as t5 on t5.id=t1.type" \
                    " left join product_product as t16 on t16.id=t1.product_id" \
                    " left join product_template as t7 on t16.product_tmpl_id =t7.id" \
                    " left join co_insurer_policy as t8 on t8.co_insurer_id=t1.id AND t8.co_type='self'" \
                    " left join res_partner as t9 on t9.id=t8.co_insurer_name " \
                    " left join insurerbranch as t10 on t10.id=t8.co_insurer_branch" \
                    " left join subdata_subdata as t11 on t11.id=t1.type"

            query1 = "select t1.prevdocket,case when t8.co_insurer_id is not null then t8.co_share else 100 end as co_share," \
                     " case when t8.co_insurer_id is not null then t9.name else t3.name end as insurername," \
                     " case when t8.co_insurer_id is not null then t10.name else t2.name end as insurerbranch," \
                     " COALESCE(SUM(t1.tppremium),0) AS tp,COALESCE(SUM(t1.terrprem),0) AS tr,COALESCE(SUM(t1.stamprem),0) AS ts," \
                     " t4.name as insuredname, t1.name as docketno,t1.id,t11.name as policystatus,t7.name as subcategory,t1.policyno as policyno," \
                     " t1.date2 as docketdate,t8.co_insurer_id,t1.proposaldate as proposaldate,t1.startfrom as startdate,'' as endos_no,t1.expiry as enddate," \
                     " case when t8.co_insurer_id is not null  then sum(t8.co_net_premium) else sum(t1.netprem) end as netprem," \
                     " case when t8.co_insurer_id is not null  then sum(t8.co_net_gross_pre) else sum(t1.grossprem) end  as grossprem," \
                     " case when t8.co_insurer_id is not null then sum(t8.co_sum_insured) else sum(t1.suminsured) end  as suminsured," \
                     " case when t8.co_insurer_id is not null then sum(t8.co_brokerage_pre) else sum(t1.brokerageprem) end  as brokerageprem," \
                     " case when t8.co_insurer_id is not null then sum(t8.co_commission_amount) else  sum(t1.commssionamt) end  as commssionamt," \
                     " case when t8.co_insurer_id is not null then sum(t8.co_commission) else  sum(t1.rate) end  as rate," \
                     " case when t8.co_insurer_id is not null then sum(t8.co_gst_amount) else sum(t1.servicetaxamt) end  as servicetaxamt" \
                     " from policytransaction as t1 left join insurerbranch as t2 on t2.id = t1.insurerbranch" \
                     " left join res_partner as t3 on t3.id=t1.insurername123" \
                     " left join res_partner as t4 on t4.id=t1.clientname" \
                     " left join subdata_subdata as t5 on t5.id=t1.type" \
                     " left join product_product as t16 on t16.id=t1.product_id" \
                     " left join product_template as t7 on t16.product_tmpl_id =t7.id" \
                     " left join co_insurer_policy as t8 on t8.co_insurer_id=t1.id AND t8.co_type='self'" \
                     " left join res_partner as t9 on t9.id=t8.co_insurer_name " \
                     " left join insurerbranch as t10 on t10.id=t8.co_insurer_branch" \
                     " left join subdata_subdata as t11 on t11.id=t1.type"

            query2 = "select t1.prevdocket, case when t8.co_insurer_id is not null then t8.co_share else 100 end as co_share," \
                     " case when t8.co_insurer_id is not null then t9.name else t3.name end as insurername," \
                     " case when t8.co_insurer_id is not null then t10.name else t2.name end as insurerbranch," \
                     " COALESCE(SUM(t1.tppremium),0) AS tp,COALESCE(SUM(t1.terrprem),0) AS tr,COALESCE(SUM(t1.stamprem),0) AS ts," \
                     " t4.name as insuredname, t1.name as docketno,t1.id,t11.name as policystatus,t7.name as subcategory,t1.policyno as policyno," \
                     " t1.date2 as docketdate,t8.co_insurer_id,t1.proposaldate as proposaldate,t1.startfrom as startdate,'' as endos_no,t1.expiry as enddate," \
                     " case when t8.co_insurer_id is not null  then sum(t8.co_net_premium) else sum(t1.netprem) end as netprem," \
                     " case when t8.co_insurer_id is not null  then sum(t8.co_net_gross_pre) else sum(t1.grossprem) end  as grossprem," \
                     " case when t8.co_insurer_id is not null then sum(t8.co_sum_insured) else sum(t1.suminsured) end  as suminsured," \
                     " case when t8.co_insurer_id is not null then sum(t8.co_brokerage_pre) else sum(t1.brokerageprem) end  as brokerageprem," \
                     " case when t8.co_insurer_id is not null then sum(t8.co_commission_amount) else  sum(t1.commssionamt) end  as commssionamt," \
                     " case when t8.co_insurer_id is not null then sum(t8.co_commission) else  sum(t1.rate) end  as rate," \
                     " case when t8.co_insurer_id is not null then sum(t8.co_gst_amount) else sum(t1.servicetaxamt) end  as servicetaxamt" \
                     " from policytransaction as t1 left join insurerbranch as t2 on t2.id = t1.insurerbranch" \
                     " left join res_partner as t3 on t3.id=t1.insurername123" \
                     " left join res_partner as t4 on t4.id=t1.clientname" \
                     " left join subdata_subdata as t5 on t5.id=t1.type" \
                     " left join product_product as t16 on t16.id=t1.product_id" \
                     " left join product_template as t7 on t16.product_tmpl_id =t7.id" \
                     " left join co_insurer_policy as t8 on t8.co_insurer_id=t1.id AND t8.co_type='self'" \
                     " left join res_partner as t9 on t9.id=t8.co_insurer_name " \
                     " left join insurerbranch as t10 on t10.id=t8.co_insurer_branch" \
                     " left join subdata_subdata as t11 on t11.id=t1.type"

            golbal = []
            dy_date = ''
            if lines.groupby == 'create_date':
                dy_date = 't1.date2'
            elif lines.groupby == 'proposaldate':
                dy_date = 't1.proposaldate'
            elif lines.groupby == 'startdate':
                dy_date = 't1.startfrom'
            else:
                dy_date = 't1.date2'
            if lines.filterby == 'insurername':
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                        lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' and t1.type=172  "  # new
                    query1 += " where " + str(dy_date) + "  BETWEEN '" + str(
                        lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' and (t1.type=173 or t1.type=175)  "  # renewal/roll-over
                    query2 += " where " + str(dy_date) + "  BETWEEN '" + str(prev_date_start) + "' AND '" + str(
                        prev_date_end) + "' "  # previuos year data
                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":

                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "' "
                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "' "
                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "' "
                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "' "
                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "' "
                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "'"
                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "' "
                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "' "
                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "' "
                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "' "
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "' "
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "' "
                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                        lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "' "

                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "' AND (t3.name = '" + str(
                        lines.insurer_name.name) + "' or t9.name = '" + str(
                        lines.insurer_name.name) + "')" \
                                                   " group by t1.prevdocket,t8.co_insurer_id,t1.id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                                   " t1.proposaldate,t8.co_share,t8.co_type,t2.name,t3.name,t9.name,t10.name,t4.name,t1.name," \
                                                   " t5.name,t4.name,t7.name,t1.tppremium,t1.terrprem,t1.stamprem,t1.rate"
                else:
                    query += "  AND (t3.name = '" + str(lines.insurer_name.name) + "' or t9.name = '" + str(
                        lines.insurer_name.name) + "')" \
                                                   " group by t1.prevdocket,t8.co_insurer_id,t1.id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                                   " t1.proposaldate,t8.co_share,t8.co_type,t2.name,t3.name,t9.name,t10.name,t4.name,t1.name," \
                                                   " t5.name,t4.name,t7.name,t1.tppremium,t1.terrprem,t1.stamprem,t1.rate"

                cr.execute(query)
                usr_detail = cr.dictfetchall()

                return usr_detail



            elif lines.filterby == 'insurerbranch':

                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                        lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "'"

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "'"
                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "'"
                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "'"
                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "' "
                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "' "
                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "'"
                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "' "
                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "'"
                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "'"
                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "' "
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "' "
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "' "
                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                        lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "'"

                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "' AND (t3.name = '" + str(
                        lines.insurer_name.name) + "' or t9.name = '" + str(
                        lines.insurer_name.name) + "') AND (t2.name = '" + str(lines.insurer_branch.name) + "'" \
                                                                                                            "or t10.name = '" + str(
                        lines.insurer_branch.name) + "') group by t1.prevdocket,t8.co_insurer_id,t1.id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                                     " t1.proposaldate,t8.co_share,t8.co_type,t2.name,t3.name,t9.name,t10.name,t4.name,t1.name," \
                                                     " t5.name,t4.name,t7.name,t1.tppremium , t1.terrprem , t1.stamprem,t1.rate"
                else:
                    query += " AND (t3.name = '" + str(lines.insurer_name.name) + "' or t9.name = '" + str(
                        lines.insurer_name.name) + "') AND (t2.name = '" + str(lines.insurer_branch.name) + "'" \
                                                                                                            "or t10.name = '" + str(
                        lines.insurer_branch.name) + "') group by t1.prevdocket,t8.co_insurer_id,t1.id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                                     " t1.proposaldate,t8.co_share,t8.co_type,t2.name,t3.name,t9.name,t10.name,t4.name,t1.name," \
                                                     " t5.name,t4.name,t7.name,t1.tppremium , t1.terrprem , t1.stamprem,t1.rate"

                cr.execute(query)
                usr_detail = cr.dictfetchall()

                return usr_detail
            else:

                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                        lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' and t1.type=172  "
                    query1 += " where " + str(dy_date) + "  BETWEEN '" + str(
                        lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' and (t1.type=173 or t1.type=175) "
                    query2 += " where " + str(dy_date) + "  BETWEEN '" + str(prev_date_start) + "' AND '" + str(prev_date_end) + "' "
                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(dec_start) + "' AND '" + str(dec_end) + "'" \
                            " and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where " + str(dy_date) + "  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "' and t1.type=172  "
                    query1 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.date_from) + "' " \
                              "AND '" + str(lines.date_to) + "' and (t1.type=173 or t1.type=175)"
                    query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' " \
                              " AND '" + str(lines.pre_date_to) + "' "

                if lines.location != 'all':
                    query += " and t1.location = '" + str(
                        lines.location) + "' group by t1.prevdocket,t8.co_insurer_id,t1.id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                          " t1.proposaldate,t8.co_share,t8.co_type,t2.name,t3.name,t9.name,t10.name,t4.name,t1.name," \
                                          " t5.name,t4.name,t7.name,t1.tppremium , t1.terrprem , t1.stamprem,t1.rate,t1.prevdocket"

                    query1 += " and t1.location = '" + str(
                        lines.location) + "' group by t1.prevdocket,t8.co_insurer_id,t1.id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                          " t1.proposaldate,t8.co_share,t8.co_type,t2.name,t3.name,t9.name,t10.name,t4.name,t1.name," \
                                          " t5.name,t4.name,t7.name,t1.tppremium , t1.terrprem , t1.stamprem,t1.rate,t1.prevdocket"
                    query2 += " and t1.location = '" + str(
                        lines.location) + "' group by t1.prevdocket,t8.co_insurer_id,t1.id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                          " t1.proposaldate,t8.co_share,t8.co_type,t2.name,t3.name,t9.name,t10.name,t4.name,t1.name," \
                                          " t5.name,t4.name,t7.name,t1.tppremium , t1.terrprem , t1.stamprem,t1.rate,t1.prevdocket"


                else:
                    query += " group by t1.prevdocket,t8.co_insurer_id,t1.id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                             " t1.proposaldate,t8.co_share,t8.co_type,t2.name,t3.name,t9.name,t10.name,t4.name,t1.name," \
                             " t5.name,t4.name,t7.name,t1.tppremium , t1.terrprem , t1.stamprem,t1.rate,t1.prevdocket"

                    query1 += " group by t1.prevdocket,t8.co_insurer_id,t1.id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                              " t1.proposaldate,t8.co_share,t8.co_type,t2.name,t3.name,t9.name,t10.name,t4.name,t1.name," \
                              " t5.name,t4.name,t7.name,t1.tppremium , t1.terrprem , t1.stamprem,t1.rate,t1.prevdocket"

                    query2 += " group by t1.prevdocket,t8.co_insurer_id,t1.id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                              " t1.proposaldate,t8.co_share,t8.co_type,t2.name,t3.name,t9.name,t10.name,t4.name,t1.name," \
                              " t5.name,t4.name,t7.name,t1.tppremium , t1.terrprem , t1.stamprem,t1.rate,t1.prevdocket"

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                cr.execute(query1)
                query1_exc = cr.dictfetchall()
                cr.execute(query2)
                query1_exc2 = cr.dictfetchall()
                return [usr_detail, query1_exc, query1_exc2]

    def endos(self, workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1, end_year,
              prev_date_start, prev_date_end, id=None,
              endo=None):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        with registry.cursor() as cr:
            query = " select t1.prevdocket, '' as co_share,t3.name as insurername,t2.name as insurerbranch,t4.name as insuredname,t1.name as docketno," \
                    " t11.name as policystatus,t7.name as subcategory,t1.policyno as policyno,t8.endo_id," \
                    " t1.date2  as docketdate,t1.proposaldate  as proposaldate,t1.startfrom  as startdate,t1.expiry  as enddate," \
                    " t8.endos_manual as endos_no,sum(t8.endo_net)  as netprem,sum(t8.endo_gst_gross)  as grossprem,sum(t8.endos_suminsured)  as suminsured," \
                    " sum(t8.endos_brokerage_premium)  as brokerageprem,sum(t8.endo_commission) as commssionamt," \
                    " sum(t8.endo_gst_amount) as servicetaxamt,COALESCE(SUM(t8.endo_tp),0) AS tp,COALESCE(SUM(t8.endo_terr),0) AS tr,COALESCE(SUM(t8.endo_stamp),0) AS ts," \
                    " t1.rate as rate from policytransaction as t1" \
                    " left join insurerbranch as t2 on t2.id = t1.insurerbranch" \
                    " left join res_partner as t3 on t3.id=t1.insurername123" \
                    " left join res_partner as t4 on t4.id=t1.clientname" \
                    " left join subdata_subdata as t5 on t5.id=t1.type" \
                    " left join product_product as t16 on t16.id=t1.product_id" \
                    " left join product_template as t7 on t16.product_tmpl_id =t7.id" \
                    " left join  endos_policy as t8 on t8.endo_id=t1.id" \
                    " left join subdata_subdata as t11 on t11.id=t1.type"

            query1 = " select t1.prevdocket, '' as co_share,t3.name as insurername,t2.name as insurerbranch,t4.name as insuredname,t1.name as docketno," \
                     " t11.name as policystatus,t7.name as subcategory,t1.policyno as policyno,t8.endo_id," \
                     " t1.date2  as docketdate,t1.proposaldate  as proposaldate,t1.startfrom  as startdate,t1.expiry  as enddate," \
                     " t8.endos_manual as endos_no,sum(t8.endo_net)  as netprem,sum(t8.endo_gst_gross)  as grossprem,sum(t8.endos_suminsured)  as suminsured," \
                     " sum(t8.endos_brokerage_premium)  as brokerageprem,sum(t8.endo_commission) as commssionamt," \
                     " sum(t8.endo_gst_amount) as servicetaxamt,COALESCE(SUM(t8.endo_tp),0) AS tp,COALESCE(SUM(t8.endo_terr),0) AS tr,COALESCE(SUM(t8.endo_stamp),0) AS ts," \
                     " t1.rate as rate from policytransaction as t1" \
                     " left join insurerbranch as t2 on t2.id = t1.insurerbranch" \
                     " left join res_partner as t3 on t3.id=t1.insurername123" \
                     " left join res_partner as t4 on t4.id=t1.clientname" \
                     " left join subdata_subdata as t5 on t5.id=t1.type" \
                     " left join product_product as t16 on t16.id=t1.product_id" \
                     " left join product_template as t7 on t16.product_tmpl_id =t7.id" \
                     " left join  endos_policy as t8 on t8.endo_id=t1.id" \
                     " left join subdata_subdata as t11 on t11.id=t1.type"

            query2 = " select t1.prevdocket, '' as co_share,t3.name as insurername,t2.name as insurerbranch,t4.name as insuredname,t1.name as docketno," \
                     " t11.name as policystatus,t7.name as subcategory,t1.policyno as policyno,t8.endo_id," \
                     " t1.date2  as docketdate,t1.proposaldate  as proposaldate,t1.startfrom  as startdate,t1.expiry  as enddate," \
                     " t8.endos_manual as endos_no,sum(t8.endo_net)  as netprem,sum(t8.endo_gst_gross)  as grossprem,sum(t8.endos_suminsured)  as suminsured," \
                     " sum(t8.endos_brokerage_premium)  as brokerageprem,sum(t8.endo_commission) as commssionamt," \
                     " sum(t8.endo_gst_amount) as servicetaxamt,COALESCE(SUM(t8.endo_tp),0) AS tp,COALESCE(SUM(t8.endo_terr),0) AS tr,COALESCE(SUM(t8.endo_stamp),0) AS ts," \
                     " t1.rate as rate from policytransaction as t1" \
                     " left join insurerbranch as t2 on t2.id = t1.insurerbranch" \
                     " left join res_partner as t3 on t3.id=t1.insurername123" \
                     " left join res_partner as t4 on t4.id=t1.clientname" \
                     " left join subdata_subdata as t5 on t5.id=t1.type" \
                     " left join product_product as t16 on t16.id=t1.product_id" \
                     " left join product_template as t7 on t16.product_tmpl_id =t7.id" \
                     " left join  endos_policy as t8 on t8.endo_id=t1.id" \
                     " left join subdata_subdata as t11 on t11.id=t1.type"

            golbal = []
            if lines.filterby == 'insurername':
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t8.endos_date  BETWEEN '" + str(
                        lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' and t1.type=172"

                    query1 += " where t8.endos_date BETWEEN '" + str(
                        lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' and (t1.type=173 or t1.type=175) "

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":

                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "' "
                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "' "
                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "' "
                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "' "
                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "' "
                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "'"
                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "' "
                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "' "
                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "' "
                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "' "
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "' "
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "' "
                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    dy_date="t8.endos_date"
                    query += " where t8.endos_date BETWEEN '" + str(
                        lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "' "
                    query1 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.date_from) + "' " \
                              " AND '" + str(lines.date_to) + "' and (t1.type=173 or t1.type=175)"
                    query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' " \
                              " AND '" + str(lines.pre_date_to) + "' "

                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "' AND t3.name = '" + str(
                        lines.insurer_name.name) + "' " \
                                                   " and t8.endo_id is not null group by t1.prevdocket,t8.name,t8.endo_id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                                   " t1.proposaldate,t2.name,t3.name,t4.name,t1.name,t5.name,t4.name,t7.name,t8.endo_tp,t8.endo_terr,t8.endo_stamp,t8.endos_manual,t1.rate "

                else:
                    query += "  AND t3.name = '" + str(lines.insurer_name.name) + "' " \
                                                                                  " and t8.endo_id is not null group by t1.prevdocket,t8.name,t8.endo_id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                                                                  " t1.proposaldate,t2.name,t3.name,t4.name,t1.name,t5.name,t4.name,t7.name,t8.endo_tp,t8.endo_terr,t8.endo_stamp,t8.endos_manual,t1.rate "

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                cr.execute(query1)
                query1_exc = cr.dictfetchall()
                return [usr_detail, query1_exc]



            elif lines.filterby == 'insurerbranch':

                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t8.endos_date BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "'"

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "'"
                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(feb_start) + "' AND '" + str(feb_end) + "'"
                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "'"
                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "' "
                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "' "
                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "'"
                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "' "
                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "'"
                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "'"
                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "' "
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "' "
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "' "
                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t8.endos_date BETWEEN '" + str(
                        lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "'"

                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "' AND t3.name = '" + str(
                        lines.insurer_name.name) + "'  AND t2.name = '" + str(
                        lines.insurer_branch.name) + "'and t8.endo_id is not null group by t1.prevdocket,t8.name,t8.endo_id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                                     " t1.proposaldate,t2.name,t3.name,t4.name,t1.name,t5.name,t4.name,t7.name,t8.endo_tp,t8.endo_terr,t8.endo_stamp,t1.rate,t8.endos_manual"
                else:
                    query += " AND t3.name = '" + str(lines.insurer_name.name) + "'  AND t2.name = '" + str(
                        lines.insurer_branch.name) + "' and t8.endo_id is not null group by t1.prevdocket,t8.name,t8.endo_id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                                     " t1.proposaldate,t2.name,t3.name,t4.name,t1.name,t5.name,t4.name,t7.name,t8.endo_tp,t8.endo_terr,t8.endo_stamp,t1.rate,t8.endos_manual"

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                return usr_detail
            else:

                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t8.endos_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' and t1.type=172 "

                    query1 += " where t8.endos_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' and (t1.type=173 or t1.type=175) "
                    query2 += " where t8.endos_date  BETWEEN '" + str(prev_date_start) + "' AND '" + str(
                        prev_date_end) + "' "
                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    dy_date="t8.endos_date"
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "' and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "' and t1.type=172  "
                        query1 += " where " + str(dy_date) + "  BETWEEN '" + str(dec_start) + "' AND '" + str(dec_end) + "'" \
                            " and (t1.type=173 or t1.type=175)"
                        query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' AND '" + str(
                            lines.pre_date_to) + "' "
                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    dy_date="t8.endos_date"
                    query += " where t8.endos_date  BETWEEN '" + str(
                        lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "'  and t1.type=172"
                    query1 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.date_from) + "' " \
                                                                                                " AND '" + str(
                        lines.date_to) + "' and (t1.type=173 or t1.type=175)"
                    query2 += " where " + str(dy_date) + "  BETWEEN '" + str(lines.pre_date_from) + "' " \
                                                                                                    " AND '" + str(
                        lines.pre_date_to) + "' "

                if lines.location != 'all':
                    query += " and t1.location = '" + str(
                        lines.location) + "' and t8.endo_id is not null group by t1.prevdocket,t8.name,t8.endo_id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom,t1.proposaldate,t2.name,t3.name," \
                                          "  t4.name,t1.name,t5.name,t4.name,t7.name,t8.endo_tp,t8.endo_terr,t8.endo_stamp,t1.rate,t8.endos_manual "

                    query1 += " and t1.location = '" + str(
                        lines.location) + "' and t8.endo_id is not null group by t1.prevdocket,t8.name,t8.endo_id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom,t1.proposaldate,t2.name,t3.name," \
                                          "  t4.name,t1.name,t5.name,t4.name,t7.name,t8.endo_tp,t8.endo_terr,t8.endo_stamp,t1." \
                                          "rate,t8.endos_manual,t1.prevdocket"
                    query2 += " and t1.location = '" + str(
                        lines.location) + "' and t8.endo_id is not null group by t1.prevdocket,t8.name,t8.endo_id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom,t1.proposaldate,t2.name,t3.name," \
                                          "  t4.name,t1.name,t5.name,t4.name,t7.name,t8.endo_tp,t8.endo_terr,t8.endo_stamp,t1." \
                                          "rate,t8.endos_manual,t1.prevdocket"
                else:
                    query += " and t8.endo_id is not null group by t1.prevdocket,t8.name,t8.endo_id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom,t1.proposaldate,t2.name,t3.name," \
                             " t4.name,t1.name,t5.name,t4.name,t7.name,t8.endo_tp,t8.endo_terr,t8.endo_stamp,t1.rate,t8.endos_manual,t1.prevdocket"

                    query1 += " and t8.endo_id is not null group by t1.prevdocket,t8.name,t8.endo_id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom,t1.proposaldate,t2.name,t3.name," \
                              " t4.name,t1.name,t5.name,t4.name,t7.name,t8.endo_tp,t8.endo_terr,t8.endo_stamp,t1.rate,t8.endos_manual,t1.prevdocket "

                    query2 += " and t8.endo_id is not null group by t1.prevdocket,t8.name,t8.endo_id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom,t1.proposaldate,t2.name,t3.name," \
                              " t4.name,t1.name,t5.name,t4.name,t7.name,t8.endo_tp,t8.endo_terr,t8.endo_stamp,t1.rate,t8.endos_manual,t1.prevdocket"

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                cr.execute(query1)
                query1_exc = cr.dictfetchall()
                cr.execute(query2)
                query2_exc = cr.dictfetchall()
                return [usr_detail, query1_exc, query2_exc]


GeneralXlsx('report.clickbima.bus_comp_detail.xlsx', 'buscompdetail.report')
