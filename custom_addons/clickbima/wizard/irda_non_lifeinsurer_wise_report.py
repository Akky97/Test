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

class Idranonlifereport(models.TransientModel):
    _name = "idranonlife.report"
    _description = "IDRA Non Life Insurerwise Report"

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    monthly = fields.Selection([('monthly', 'Monthly'), ('quatar', 'Quarterly'), ('yearly', 'Yearly')],
                               default='monthly',string="Period Type")
    quarter = fields.Selection([('q1', 'Quarter 1'), ('q2', 'Quarter 2'), ('q3', 'Quarter 3'), ('q4', 'Quarter 4')],
                               string='Quarter')
    groupby = fields.Selection([('create_date', 'All'), ('category', 'Category')], default='',
                               string="group by")
    filterby = fields.Selection([('all', 'All'), ('category', 'Category'),('insurername', 'Insurer Name')], default='all', string="Filter BY")
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
    insurer_name = fields.Many2one('res.partner', string="Insurer Name",
                                   domain=[('customer', '=', True), ('is_company', '=', True)])
    start_year = fields.Char()
    end_year = fields.Char()

    @api.onchange('monthly', 'fiscal_year')
    def onchange_monthly(self):
        if self.monthly:
            if (self.monthly == 'yearly'):
                self.date_from = str(self.fiscal_year.date_start)
                self.date_to = str(self.fiscal_year.date_end)
            else:
                pass

   

    @api.onchange('monthly', 'months', 'fiscal_year')
    def onchange_monthly(self):
        import datetime
        if self.monthly:
            end_year1 = self.fiscal_year.date_end
            my_date1 = datetime.datetime.strptime(end_year1, "%Y-%m-%d")
            end_year = my_date1.year
            start_year1 = self.fiscal_year.date_start
            my_date = datetime.datetime.strptime(start_year1, "%Y-%m-%d")
            start_year = my_date.year
            if (self.monthly == 'yearly'):
                self.date_from = str(self.fiscal_year.date_start)
                self.date_to = str(self.fiscal_year.date_end)
            elif (self.monthly == 'monthly'):
                if self.months == '01-01':
                    self.start_year = start_year
                    self.end_year = end_year
                    jan_start = str(end_year) + str('-01-01')
                    jan_end = str(end_year) + str('-01-31')
                    self.date_from = str(jan_start)
                    self.date_to = str(jan_end)

                if self.months == '01-02':
                    self.start_year = start_year
                    self.end_year = end_year
                    feb_start = str(end_year) + str('-02-01')
                    feb_end = str(end_year) + str('-02-28')
                    self.date_from = str(feb_start)
                    self.date_to = str(feb_end)

                if self.months == '01-03':
                    self.start_year = start_year
                    self.end_year = end_year
                    mar_start = str(end_year) + str('-03-01')
                    mar_end = str(end_year) + str('-03-31')
                    self.date_from = str(mar_start)
                    self.date_to = str(mar_end)

                if self.months == '01-04':
                    self.start_year = start_year
                    self.end_year = end_year
                    apr_start = str(start_year) + str('-04-01')
                    apr_end = str(start_year) + str('-04-30')
                    self.date_from = str(apr_start)
                    self.date_to = str(apr_end)

                if self.months == '01-05':
                    self.start_year = start_year
                    self.end_year = end_year
                    may_start = str(start_year) + str('-05-01')
                    may_end = str(start_year) + str('-05-31')
                    self.date_from = str(may_start)
                    self.date_to = str(may_end)

                if self.months == '01-06':
                    self.start_year = start_year
                    self.end_year = end_year
                    june_start = str(start_year) + str('-06-01')
                    june_end = str(start_year) + str('-06-30')
                    self.date_from = str(june_start)
                    self.date_to = str(june_end)

                if self.months == '01-07':
                    self.start_year = start_year
                    self.end_year = end_year
                    jul_start = str(start_year) + str('-07-01')
                    jul_end = str(start_year) + str('-07-31')
                    self.date_from = str(jul_start)
                    self.date_to = str(jul_end)

                if self.months == '01-08':
                    self.start_year = start_year
                    self.end_year = end_year
                    aug_start = str(start_year) + str('-08-01')
                    aug_end = str(start_year) + str('-08-31')
                    self.date_from = str(aug_start)
                    self.date_to = str(aug_end)

                if self.months == '01-09':
                    self.start_year = start_year
                    self.end_year = end_year
                    sep_start = str(start_year) + str('-09-01')
                    sep_end = str(start_year) + str('-09-30')
                    self.date_from = str(sep_start)
                    self.date_to = str(sep_end)

                if self.months == '01-10':
                    self.start_year = start_year
                    self.end_year = end_year
                    oct_start = str(start_year) + str('-10-01')
                    oct_end = str(start_year) + str('-10-31')
                    self.date_from = str(oct_start)
                    self.date_to = str(oct_end)

                if self.months == '01-11':
                    self.start_year = start_year
                    self.end_year = end_year
                    nov_start = str(start_year) + str('-11-01')
                    nov_end = str(start_year) + str('-11-30')
                    self.date_from = str(nov_start)
                    self.date_to = str(nov_end)

                if self.months == '01-12':
                    self.start_year = start_year
                    self.end_year = end_year
                    dec_start = str(start_year) + str('-12-01')
                    dec_end = str(start_year) + str('-12-31')
                    self.date_from = str(dec_start)
                    self.date_to = str(dec_end)
        else:
            pass

    @api.onchange('quarter', 'fiscal_year')
    def onchange_quarter(self):
        import datetime
        if self.quarter:
            end_year1 = self.fiscal_year.date_end
            my_date1 = datetime.datetime.strptime(end_year1, "%Y-%m-%d")
            end_year = my_date1.year
            start_year1 = self.fiscal_year.date_start
            my_date = datetime.datetime.strptime(start_year1, "%Y-%m-%d")
            start_year = my_date.year
            if (self.quarter == 'q1'):
                self.start_year = start_year
                self.end_year = end_year
                q1_start = str(start_year) + str('-04-01')
                q1_end = str(start_year) + str('-06-30')
                self.date_from = str(q1_start)
                self.date_to = str(q1_end)
            elif (self.quarter == 'q2'):
                self.start_year = start_year
                self.end_year = end_year
                q2_start = str(start_year) + str('-07-01')
                q2_end = str(start_year) + str('-09-30')
                self.date_from = str(q2_start)
                self.date_to = str(q2_end)
            elif (self.quarter == 'q3'):
                self.start_year = start_year
                self.end_year = end_year
                q3_start = str(start_year) + str('-10-01')
                q3_end = str(start_year) + str('-12-31')
                self.date_from = str(q3_start)
                self.date_to = str(q3_end)
            elif (self.quarter == 'q4'):
                self.start_year = start_year
                self.end_year = end_year
                q4_start = str(end_year) + str('-01-01')
                q4_end = str(end_year) + str('-03-31')
                self.date_from = str(q4_start)
                self.date_to = str(q4_end)
            else:
                pass


    @api.multi
    def test_report1(self):
        data = {}
        data['form'] = self.read([])[0]
        return self.env['report'].get_action(self, report_name='clickbima.non_life_insurer.xlsx', data=data)

from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
class NonLifeInsurerXlsx(ReportXlsx):
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

        filtname = ''
        if lines.filterby == 'all':
            filtname = 'All'
        elif lines.filterby == 'category':
            filtname = 'Category'
        elif lines.filterby == 'insurername':
            filtname = 'Insurer Name'
        quat = ''
        if lines.monthly == 'yearly':
            quat = 'Yearly'
        elif lines.monthly == 'monthly':
            if lines.months == '01-01':
                quat = 'January'
            if lines.months == '01-02':
                quat = 'February'
            if lines.months == '01-03':
                quat = 'March'
            if lines.months == '01-04':
                quat = 'April'
            if lines.months == '01-05':
                quat = 'May'
            if lines.months == '01-06':
                quat = 'June'
            if lines.months == '01-07':
                quat = 'July'
            if lines.months == '01-08':
                quat = 'August'
            if lines.months == '01-09':
                quat = 'September'
            if lines.months == '01-10':
                quat = 'October'
            if lines.months == '01-11':
                quat = 'November'
            if lines.months == '01-12':
                quat = 'December'
        elif lines.monthly == 'quatar':
            if lines.quarter == 'q1':
                quat = 'Quarter(April-June)'
            if lines.quarter == 'q2':
                quat = 'Quarter(July-Sept)'
            if lines.quarter == 'q3':
                quat = 'Quarter(Oct-Dec)'
            if lines.quarter == 'q4':
                quat = 'Quarter(Jan-Mar)'
        else:
            pass
        loc = ''
        if lines.location == '9':
            loc = 'Chandigarh'
        elif lines.location == '8':
            loc = 'Ludhiana'
        elif lines.location == '7':
            loc = 'New Delhi'
        else:
            loc = 'All'
        import datetime
        x = datetime.datetime.now()
        # One sheet by partner
        report_name = "sheet 1"
        sheet = workbook.add_worksheet(report_name[:31])
        report_head = 'Security Insurance Brokers (India) Private Limited'
        report_head4 = 'Engineering'
        report_head5 = 'Fire'
        report_head6 = 'Health'
        report_head7 = 'Liability'
        # report_head8 = 'Life'
        report_head12 = 'Marine Cargo'
        report_head9 = 'Marine Hull'
        report_head10 = 'Motor'
        report_head11 = 'Others'

        merge_format = workbook.add_format(
            {'bold': 1, 'align': 'center', 'valign': 'vcenter', 'font_color': 'black'})
        merge_format1 = workbook.add_format(
            {'bold': 1, 'align': 'left', 'valign': 'vleft', 'font_color': 'black'})
        merge_format2 = workbook.add_format(
            {'bold': 1, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'font_color': 'black'})
        bold = workbook.add_format({'border': 1, 'bold': True, 'align': 'left'})
        bold1 = workbook.add_format({'bold': True, 'border': 1, 'align': 'right'})
        bold2 = workbook.add_format({'border': 1, 'align': 'center'})
        count = workbook.add_format({'border': 1, 'align': 'center', 'bold': True, })
        bold3 = workbook.add_format({'bold': True, 'align': 'right'})
        right = workbook.add_format({'border': 1, 'align': 'right', 'bold': True})
        border = workbook.add_format({'border': 1, 'align': 'center', 'bold': True})
        border2 = workbook.add_format({'border': 1, 'align': 'left'})
        border1 = workbook.add_format({'border': 1, 'align': 'right'})
        border3 = workbook.add_format({'border': 1, 'align': 'right', 'bold': True})
        align_left = workbook.add_format({'align': 'left'})

        # sheet.write(5, 4, ('Start Date : ' + str(lines.date_from) + '  to End Date : ' + str(lines.date_to)), bold1)
        report_head2 = 'Non Life Insurer-wise Report for the period of Proposal Start Date : ' + str(
            lines.date_from) + '  to End Date : ' + str(lines.date_to)
        report_head3 = 'Grouped By : Category     Filtered By : ' + str(filtname)
        report_location = str(loc)
        report_printed = 'Printed On  ' + str(x.strftime("%x"))
        sheet.write(1, 18, ('Page:1'), bold3)
        sheet.write(8, 0, ('Financial Year'), bold1)
        sheet.write(8, 1, (lines.fiscal_year.name), bold)
        sheet.write(8, 2, (' '), bold)
        sheet.write(8, 3, ('Period Type'), bold1)
        sheet.write(8, 4, (quat), bold)
        sheet.write(9, 0, (' '), bold)
        sheet.write(10, 0, ('Name of Insurers'), bold)
        sheet.write(10, 17, ('Total No of Policy'), border)
        sheet.write(10, 18, ('Total Premium'), right)
        for i in range(0, 8):
            sheet.write(10, 2 * i + 1, ('No of Policies'), border)
            sheet.write(10, 2 * i + 2, ('Premium'), right)


        # increasing width of column
        sheet.set_column('A:A', 50)
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
        sheet.set_column('M:M', 20)
        sheet.set_column('N:N', 20)
        sheet.set_column('O:O', 20)
        sheet.set_column('P:P', 20)
        sheet.set_column('Q:Q', 20)
        sheet.set_column('R:R', 30)
        sheet.set_column('S:S', 30)
        sheet.set_column('T:T', 20)
        sheet.set_column('U:U', 20)

        sheet.merge_range('A1:F1', report_head, merge_format1)
        sheet.merge_range('A2:B2', report_location, merge_format1)
        sheet.merge_range('A4:Q4', report_head2, merge_format)
        sheet.merge_range('A5:Q5', report_head3, merge_format)
        sheet.merge_range('B10:C10', report_head4, merge_format2)
        sheet.merge_range('D10:E10', report_head5, merge_format2)
        sheet.merge_range('F10:G10', report_head6, merge_format2)
        sheet.merge_range('H10:I10', report_head7, merge_format2)
        sheet.merge_range('J10:K10', report_head12, merge_format2)
        sheet.merge_range('L10:M10', report_head9, merge_format2)
        sheet.merge_range('N10:O10', report_head10, merge_format2)
        sheet.merge_range('P10:Q10', report_head11, merge_format2)
        sheet.merge_range('R1:S1', report_printed, bold3)
        # sheet.merge_range('R9:S9', report_head12, merge_format)
        # sheet.merge_range('T9:U9', report_head13, merge_format)

        usr_detail = []
        usr_details = self.querys(workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1,
                                  end_year)
        endo_date = self.endos(workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1,
                               end_year)
        for j in endo_date:
            usr_detail.append(j)
        print(len(endo_date), "lens")
        for i in usr_details:
            usr_detail.append(i)
        print(len(usr_detail), "lens")

        temp = []
        an_iterator12 = sorted(usr_detail, key=operator.itemgetter('insurername'))
        an_iterator = itertools.groupby(an_iterator12, key=operator.itemgetter('insurername'))
        for key, group in an_iterator:
            key_and_group = {key: list(group)}
            for i in key_and_group.iteritems():
                health_count = 0
                health_premium = 0
                motor_count = 0
                motor_premium = 0
                liability_count = 0
                liability_premium = 0
                engineering_count = 0
                engineering_premium = 0
                fire_count = 0
                fire_premium = 0
                others_count = 0
                others_premium = 0
                life_count = 0
                life_premium = 0
                miscellaneous_count = 0
                miscellaneous_premium = 0
                marine_count = 0
                marine_premium = 0
                engineering_count_null = 0
                engineering_premium_null = 0
                motor_count_null = 0
                motor_premium_null = 0
                health_count_null = 0
                health_premium_null = 0
                marine_count_null = 0
                marine_premium_null = 0
                fire_count_null = 0
                fire_premium_null = 0
                liability_count_null = 0
                liability_premium_null = 0
                others_count_null = 0
                others_premium_null = 0
                miscellaneous_count_null = 0
                miscellaneous_premium_null = 0
                category = ''
                for j in i[1]:
                    if j['engineering_count'] == None or j['engineering_count'] == False:
                        engineering_count_null = 0
                    else:
                        engineering_count_null = j['engineering_count']
                    if j['engineering_premium'] == None or j['engineering_premium'] == False:
                        engineering_premium_null = 0
                    else:
                        engineering_premium_null = j['engineering_premium']
                    if j['motor_count'] == None or j['motor_count'] == False:
                        motor_count_null = 0
                    else:
                        motor_count_null = j['motor_count']
                    if j['motor_premium'] == None or j['motor_premium'] == False:
                        motor_premium_null = 0
                    else:
                        motor_premium_null = j['motor_premium']
                    if j['health_count'] == None or j['health_count'] == False:
                        health_count_null = 0
                    else:
                        health_count_null = j['health_count']
                    if j['health_premium'] == None or j['health_premium'] == False:
                        health_premium_null = 0
                    else:
                        health_premium_null = j['health_premium']
                    if j['marine_count'] == None or j['marine_count'] == False:
                        marine_count_null = 0
                    else:
                        marine_count_null = j['marine_count']
                    if j['marine_premium'] == None or j['marine_premium'] == False:
                        marine_premium_null = 0
                    else:
                        marine_premium_null = j['marine_premium']
                    if j['fire_count'] == None or j['fire_count'] == False:
                        fire_count_null = 0
                    else:
                        fire_count_null = j['fire_count']
                    if j['fire_premium'] == None or j['fire_premium'] == False:
                        fire_premium_null = 0
                    else:
                        fire_premium_null = j['fire_premium']
                    if j['liability_count'] == None or j['liability_count'] == False:
                        liability_count_null = 0
                    else:
                        liability_count_null = j['liability_count']
                    if j['liability_premium'] == None or j['liability_premium'] == False:
                        liability_premium_null = 0
                    else:
                        liability_premium_null = j['liability_premium']
                    if j['others_count'] == None or j['others_count'] == False:
                        others_count_null = 0
                    else:
                        others_count_null = j['others_count']
                    if j['others_premium'] == None or j['others_premium'] == False:
                        others_premium_null = 0
                    else:
                        others_premium_null = j['others_premium']
                    if j['miscellaneous_count'] == None or j['miscellaneous_count'] == False:
                        miscellaneous_count_null = 0
                    else:
                        miscellaneous_count_null = j['miscellaneous_count']
                    if j['miscellaneous_premium'] == None or j['miscellaneous_premium'] == False:
                        miscellaneous_premium_null = 0
                    else:
                        miscellaneous_premium_null = j['miscellaneous_premium']
                    health_count += health_count_null
                    health_premium += health_premium_null
                    motor_count += motor_count_null
                    motor_premium += motor_premium_null
                    liability_count += liability_count_null
                    liability_premium += liability_premium_null
                    engineering_count += engineering_count_null
                    engineering_premium += engineering_premium_null
                    fire_count += fire_count_null
                    fire_premium += fire_premium_null
                    others_count += others_count_null
                    others_premium += others_premium_null
                    # life_count += j['life_count']
                    # life_premium += j['life_premium']
                    miscellaneous_count += miscellaneous_count_null
                    miscellaneous_premium += miscellaneous_premium_null
                    marine_count += marine_count_null
                    marine_premium += marine_premium_null
                    category = j['category']
                temp.append({"insurer_name": i[0],
                             "category": category,
                             "health_count": health_count,
                             "health_premium": health_premium,
                             "motor_count": motor_count,
                             "motor_premium": motor_premium,
                             "liability_count": liability_count,
                             "liability_premium": liability_premium,
                             "engineering_count": engineering_count,
                             "engineering_premium": engineering_premium,
                             "fire_count": fire_count,
                             "fire_premium": fire_premium,
                             "others_count": others_count,
                             "others_premium": others_premium,
                             # "life_count": life_count,
                             # "life_premium": life_premium,
                             "miscellaneous_count": miscellaneous_count,
                             "miscellaneous_premium": miscellaneous_premium,
                             "marine_count": marine_count,
                             "marine_premium": marine_premium,
                             "total_policy": health_count + motor_count + liability_count + engineering_count + fire_count + others_count + miscellaneous_count + marine_count,
                             "total_premium": health_premium + motor_premium + liability_premium + engineering_premium + fire_premium + others_premium + miscellaneous_premium + marine_premium})

        row = 11
        s_no = 1
        engineering_counts = 0
        engineering_premiums = 0
        health_counts = 0
        health_premiums = 0
        # life_counts=0
        # life_premiums=0
        motor_counts = 0
        motor_premiums = 0
        marine_counts = 0
        marine_premiums = 0
        fire_counts = 0
        fire_premiums = 0
        liability_counts = 0
        liability_premiums = 0
        miscellaneous_counts = 0
        miscellaneous_premiums = 0
        others_counts = 0
        others_premiums = 0
        total_counts = 0
        total_premiums = 0
        for res in temp:
            engineering_counts += res['engineering_count']
            engineering_premiums += res['engineering_premium']
            health_counts += res['health_count']
            health_premiums += res['health_premium']
            # life_counts+=res['life_count']
            # life_premiums+=res['life_premium']
            motor_counts += res['motor_count']
            motor_premiums += res['motor_premium']
            marine_counts += res['marine_count']
            marine_premiums += res['marine_premium']
            fire_counts += res['fire_count']
            fire_premiums += res['fire_premium']
            liability_counts += res['liability_count']
            liability_premiums += res['liability_premium']
            miscellaneous_counts += res['miscellaneous_count']
            miscellaneous_premiums += res['miscellaneous_premium']
            others_counts += res['others_count']
            others_premiums += res['others_premium']
            total_counts += res['total_policy']
            total_premiums += res['total_premium']
            import math
            sheet.write(row, 0, res['insurer_name'], border2)
            sheet.write(row, 1, res['engineering_count'], bold2)
            sheet.write(row, 2, round(res['engineering_premium']), border1)
            sheet.write(row, 3, res['fire_count'], bold2)
            sheet.write(row, 4, round(res['fire_premium']), border1)
            sheet.write(row, 5, res['health_count'], bold2)
            sheet.write(row, 6, round(res['health_premium']), border1)
            sheet.write(row, 7, res['liability_count'], bold2)
            sheet.write(row, 8, round(res['liability_premium']), border1)
            # sheet.write(row, 9, res['life_count'], border1)
            # sheet.write(row, 10, res['life_premium'], border1)
            sheet.write(row, 9, res['marine_count'], bold2)
            sheet.write(row, 10, round(res['marine_premium']), border1)
            sheet.write(row, 11, res['miscellaneous_count'], bold2)
            sheet.write(row, 12, round(res['miscellaneous_premium']), border1)
            sheet.write(row, 13, res['motor_count'], bold2)
            sheet.write(row, 14, round(res['motor_premium']), border1)
            sheet.write(row, 15, res['others_count'], bold2)
            sheet.write(row, 16, round(res['others_premium']), border1)
            sheet.write(row, 17, res['total_policy'], bold2)
            sheet.write(row, 18, round(res['total_premium']), border1)

            row = row + 1
            s_no = s_no + 1
            print("Array printed for s.no :", s_no - 1)


        sheet.write(row, 0, ('Total'), border3)
        sheet.write(row, 1, engineering_counts, count)
        sheet.write(row, 2, round(engineering_premiums), border3)
        sheet.write(row, 3, fire_counts, count)
        sheet.write(row, 4, round(fire_premiums), border3)
        sheet.write(row, 5, health_counts, count)
        sheet.write(row, 6, round(health_premiums), border3)
        sheet.write(row, 7, liability_counts, count)
        sheet.write(row, 8, round(liability_premiums), border3)
        # sheet.write(row, 9, life_counts, border1)
        # sheet.write(row, 10, life_premiums, border1)
        sheet.write(row, 9, marine_counts, count)
        sheet.write(row, 10, round(marine_premiums), border3)
        sheet.write(row, 11, miscellaneous_counts, count)
        sheet.write(row, 12, round(miscellaneous_premiums), border3)
        sheet.write(row, 13, motor_counts, count)
        sheet.write(row, 14, round(motor_premiums), border3)
        sheet.write(row, 15, others_counts, count)
        sheet.write(row, 16, round(others_premiums), border3)
        sheet.write(row, 17, total_counts, count)
        sheet.write(row, 18, round(total_premiums), border3)

    def querys(self, workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1, end_year,id=None, endo=None):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        with registry.cursor() as cr:
            query = "select t1.name, t2.irda_cat, t2.name as category, t4.co_insurer_id," \
                    " case when 'Health' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then count(t2.irda_cat) else count(t2.irda_cat)" \
                    " end end as health_count," \
                    " case when 'Health' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then sum(t4.co_net_premium) else sum(t1.netprem)" \
                    " end end as health_premium," \
                    " case when 'Motor' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then count(t2.irda_cat) else count(t2.irda_cat)" \
                    " end end as motor_count," \
                    " case when 'Motor' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then sum(t4.co_net_premium) else sum(t1.netprem)" \
                    " end end as motor_premium," \
                    " case when 'Liability' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then count(t2.irda_cat) else count(t2.irda_cat)" \
                    " end end as liability_count," \
                    " case when 'Liability' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then sum(t4.co_net_premium) else sum(t1.netprem)" \
                    " end end as liability_premium," \
                    " case when 'Engineering' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then count(t2.irda_cat) else count(t2.irda_cat)" \
                    " end end as engineering_count," \
                    " case when 'Engineering' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then sum(t4.co_net_premium) else sum(t1.netprem)" \
                    " end end as engineering_premium," \
                    " case when 'Fire' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then count(t2.irda_cat) else count(t2.irda_cat)" \
                    " end end as fire_count," \
                    " case when 'Fire' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then sum(t4.co_net_premium) else sum(t1.netprem)" \
                    " end end as fire_premium," \
                    " case when 'Others' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then count(t2.irda_cat) else count(t2.irda_cat)" \
                    " end end as others_count," \
                    " case when 'Others' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then sum(t4.co_net_premium) else sum(t1.netprem)" \
                    " end end as others_premium," \
                    " case when 'Life' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then count(t2.irda_cat) else count(t2.irda_cat)" \
                    " end end as life_count," \
                    " case when 'Life' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then sum(t4.co_net_premium) else sum(t1.netprem)" \
                    " end end as life_premium," \
                    " case when 'Miscellaneous' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then count(t2.irda_cat) else count(t2.irda_cat)" \
                    " end end as miscellaneous_count," \
                    " case when 'Miscellaneous' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then sum(t4.co_net_premium) else sum(t1.netprem)" \
                    " end end as miscellaneous_premium," \
                    " case when 'Marine Cargo' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then count(t2.irda_cat) else count(t2.irda_cat)" \
                    " end end as marine_count," \
                    " case when 'Marine Cargo' = t2.irda_cat then" \
                    " case when t4.co_insurer_id is not null then sum(t4.co_net_premium) else sum(t1.netprem)" \
                    " end end as marine_premium," \
                    " case when t4.co_insurer_id is not null then t5.name else t3.name" \
                    " end as insurername" \
                    " from policytransaction as t1" \
                    " left join category_category as t2 on t2.id = t1.segment" \
                    " left join co_insurer_policy as t4 on t4.co_insurer_id = t1.id AND t4.co_type = 'self'" \
                    " left join res_partner as t3 on t1.insurername123 = t3.id" \
                    " left join res_partner as t5 on t5.id = t4.co_insurer_name"


        # query = " select t2.irda_cat,t5.endo_id,t2.name as category,t4.co_insurer_id,t3.name as insurername," \
        #             " case when 'Health'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then  count(t2.irda_cat)" \
        #             " end end end end end as health_count," \
        #             " case when 'Health'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then sum(t5.endo_net)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null) then sum(t4.co_brokerage_pre)" \
        #             " else case when (t4.co_insurer_id is null and t5.endo_id is null) then sum(t1.netprem)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then sum(t5.endo_net + t4.co_brokerage_pre)" \
        #             " end end end end end as health_premium," \
        #             " case when 'Motor'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then  count(t2.irda_cat)" \
        #             " end end end end end as motor_count," \
        #             " case when 'Motor'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then sum(t5.endo_net)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then sum(t4.co_brokerage_pre)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then sum(t1.netprem)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then sum(t5.endo_net + t4.co_brokerage_pre)" \
        #             " end end end end end as motor_premium," \
        #             " case when 'Liability'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then  count(t2.irda_cat)" \
        #             " end end end end end as liability_count," \
        #             " case when 'Liability'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then sum(t5.endo_net)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then sum(t4.co_brokerage_pre)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then sum(t1.netprem)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then sum(t5.endo_net + t4.co_brokerage_pre)" \
        #             " end end end end end as liability_premium," \
        #             " case when 'Engineering'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then  count(t2.irda_cat)" \
        #             " end end end end end as engineering_count," \
        #             " case when 'Engineering'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then sum(t5.endo_net)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then sum(t4.co_brokerage_pre)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then sum(t1.netprem)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then sum(t5.endo_net + t4.co_brokerage_pre)" \
        #             " end end end end end as engineering_premium," \
        #             " case when 'Fire'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then  count(t2.irda_cat)" \
        #             " end end end end end as fire_count," \
        #             " case when 'Fire'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then sum(t5.endo_net)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then sum(t4.co_brokerage_pre)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then sum(t1.netprem)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then sum(t5.endo_net + t4.co_brokerage_pre)" \
        #             " end end end end end as fire_premium," \
        #             " case when 'Others'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then  count(t2.irda_cat)" \
        #             " end end end end end as others_count," \
        #             " case when 'Others'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then sum(t5.endo_net)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then sum(t4.co_brokerage_pre)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then sum(t1.netprem)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then sum(t5.endo_net + t4.co_brokerage_pre)" \
        #             " end end end end end as others_premium," \
        #             " case when 'Life'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then  count(t2.irda_cat)" \
        #             " end end end end end as life_count," \
        #             " case when 'Life'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then sum(t5.endo_net)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then sum(t4.co_brokerage_pre)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then sum(t1.netprem)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then sum(t5.endo_net + t4.co_brokerage_pre)" \
        #             " end end end end end as life_premium," \
        #             " case when 'Miscellaneous'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then  count(t2.irda_cat)" \
        #             " end end end end end as miscellaneous_count," \
        #             " case when 'Miscellaneous'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then sum(t5.endo_net)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then sum(t4.co_brokerage_pre)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then sum(t1.netprem)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then sum(t5.endo_net + t4.co_brokerage_pre)" \
        #             " end end end end end as miscellaneous_premium," \
        #             " case when 'Marine Cargo'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then  count(t2.irda_cat)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then  count(t2.irda_cat)" \
        #             " end end end end end as marine_count," \
        #             " case when 'Marine Cargo'=t2.irda_cat then" \
        #             " case when (t5.endo_id is not null and t4.co_insurer_id is null) then sum(t5.endo_net)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is null)  then sum(t4.co_brokerage_pre)" \
        #             " else case when (t4.co_insurer_id is  null and t5.endo_id is null) then sum(t1.netprem)" \
        #             " else case when (t4.co_insurer_id is not null and t5.endo_id is not null) then sum(t5.endo_net + t4.co_brokerage_pre)" \
        #             " end end end end end as marine_premium" \
        #             " from policytransaction as t1" \
        #             " left join category_category as t2 on t2.id = t1.segment" \
        #             " left join  co_insurer_policy as t4 on t4.co_insurer_id =t1.id AND t4.co_type='self'" \
        #             " left join  endos_policy as t5 on t5.endo_id =t1.id" \
        #             " left join  res_partner as t3 on t1.insurername123 =t3.id"

                # query="select t1.insurername123,t2.name as category,t3.name as insurername,t2.irda_cat," \
            #       " case when 'Health'=t2.irda_cat then count(t2.irda_cat) else 0 end as health_count," \
            #       " case when 'Health'=t2.irda_cat then sum(t1.netprem) else 0 end as health_premium , " \
            #       " case when 'Motor'=t2.irda_cat then count(t2.irda_cat) else 0 end as motor_count, " \
            #       " case when 'Motor'=t2.irda_cat then sum(t1.netprem) else 0 end as motor_premium, " \
            #       " case when 'Liability'=t2.irda_cat then count(t2.irda_cat) else 0 end as liability_count," \
            #       " case when 'Liability'=t2.irda_cat then sum(t1.netprem) else 0 end as liability_premium, " \
            #       " case when 'Engineering'=t2.irda_cat then count(t2.irda_cat) else 0 end as engineering_count," \
            #       " case when 'Engineering'=t2.irda_cat then sum(t1.netprem) else 0 end as engineering_premium," \
            #       " case when 'Fire'=t2.irda_cat then count(t2.irda_cat) else 0 end as fire_count," \
            #       " case when 'Fire'=t2.irda_cat then sum(t1.netprem) else 0 end as fire_premium," \
            #       " case when 'Others'=t2.irda_cat then count(t2.irda_cat) else 0 end as others_count," \
            #       " case when 'Others'=t2.irda_cat then sum(t1.netprem) else 0 end as others_premium," \
            #       " case when 'Life'=t2.irda_cat then count(t2.irda_cat) else 0 end as life_count," \
            #       " case when 'Life'=t2.irda_cat then t1.netprem else 0 end as life_premium," \
            #       " case when 'Miscellaneous'=t2.irda_cat then count(t2.irda_cat) else 0 end as miscellaneous_count," \
            #       " case when 'Miscellaneous'=t2.irda_cat then sum(t1.netprem) else 0 end as miscellaneous_premium," \
            #       " case when 'Marine Cargo'=t2.irda_cat then count(t2.irda_cat) else 0 end as marine_count," \
            #       " case when 'Marine Cargo'=t2.irda_cat then sum(t1.netprem) else 0 end as marine_premium" \
            #       " from policytransaction as t1 " \
            #       " left join category_category as t2 on t2.id = t1.segment" \
            #       " left join  res_partner as t3 on t1.insurername123 =t3.id" \


                
         
            if lines.filterby == 'all':
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t1.startfrom  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "'"

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "'"

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "' "

                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "'"

                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "'"

                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "'"

                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "'"

                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "' "

                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "' "

                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "'"

                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "'"

                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "'"

                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "' "

                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t1.startfrom  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "'"
                if lines.location != 'all':
                    query += " and t1.location = '" +str(lines.location) +"' group by t2.irda_cat, t2.name, t4.co_insurer_id, t5.name, t3.name, t1.name order by t3.name,t2.irda_cat"
                else:
                    query += "  group by t2.irda_cat, t2.name, t4.co_insurer_id, t5.name, t3.name, t1.name order by t3.name,t2.irda_cat"
                cr.execute(query)
                usr_detail = cr.dictfetchall()
                
                return usr_detail

            elif lines.filterby == 'category':

                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where  t1.startfrom  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' AND t2.name = '" + str(
                        lines.category.name) + "'"

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "' AND t2.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where  t1.startfrom  BETWEEN '" + str(feb_start) + "' AND '" + str(feb_end) + "' AND t2.name = '" + str(
                            lines.category.name) + "'"

                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "' AND t2.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "' AND t2.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "' AND t2.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "' AND t2.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "' AND t2.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "' AND t2.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where  t1.startfrom  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "' AND t2.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "' AND t2.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "' AND t2.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "' AND t2.name = '" + str(lines.category.name) + "'"

                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t1.startfrom  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "' AND t2.name = '" + str(
                        lines.category.name) + "' "
                if lines.location != 'all':
                    query += " and t1.location = '" +str(lines.location) +"'group by t2.irda_cat, t2.name, t4.co_insurer_id, t5.name, t3.name, t1.name order by t3.name,t2.irda_cat"
                else:
                    query += "  group by t2.irda_cat, t2.name, t4.co_insurer_id, t5.name, t3.name, t1.name order by t3.name,t2.irda_cat"

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                
                return usr_detail
            elif lines.filterby == 'insurername':
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t1.startfrom  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' AND t3.name = '" + str(lines.insurer_name.name) + "' "

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "' "

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "' "

                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "' "

                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "' "

                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "'"

                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "'"

                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "' "

                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "'"

                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "' "

                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "'"

                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "' "

                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "'"

                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t1.startfrom  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "'"
                if lines.location != 'all':
                    query += " and t1.location = '" +str(lines.location) +"'  AND (t3.name = '" + str(lines.insurer_name.name) + "' or t5.name = '" + str(lines.insurer_name.name) + "') group by t2.irda_cat, t2.name, t4.co_insurer_id, t5.name, t3.name, t1.name order by t3.name,t2.irda_cat"
                else:
                    query += "  AND (t3.name = '" + str(lines.insurer_name.name) + "' or t5.name = '" + str(lines.insurer_name.name) + "') group by t2.irda_cat, t2.name, t4.co_insurer_id, t5.name, t3.name, t1.name order by t3.name,t2.irda_cat"

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                
                return usr_detail
            else:
                    if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                        query += " where t1.startfrom  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                            lines.fiscal_year.date_end) + "'"

                    if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                        year = lines.fiscal_year.name
                        if lines.months == '01-01':
                            jan_start = str(end_year) + str(start_date)
                            jan_end = str(end_year) + str(end_date)
                            query += " where t1.startfrom  BETWEEN '" + str(jan_start) + "' AND '" + str(
                                jan_end) + "'"

                        if lines.months == '01-02':
                            feb_start = str(end_year) + str(start_date)
                            feb_end = str(end_year) + str(end_date)
                            query += " where t1.startfrom  BETWEEN '" + str(feb_start) + "' AND '" + str(
                                feb_end) + "' "

                        if lines.months == '01-03':
                            mar_start = str(end_year) + str(start_date)
                            mar_end = str(end_year) + str(end_date)
                            query += " where t1.startfrom  BETWEEN '" + str(mar_start) + "' AND '" + str(
                                mar_end) + "'"

                        if lines.months == '01-04':
                            apr_start = str(start_year) + str(start_date)
                            apr_end = str(start_year) + str(end_date)
                            query += " where t1.startfrom  BETWEEN '" + str(apr_start) + "' AND '" + str(
                                apr_end) + "'"

                        if lines.months == '01-05':
                            may_start = str(start_year) + str(start_date)
                            may_end = str(start_year) + str(end_date)
                            query += " where t1.startfrom  BETWEEN '" + str(may_start) + "' AND '" + str(
                                may_end) + "'"

                        if lines.months == '01-06':
                            june_start = str(start_year) + str(start_date)
                            june_end = str(start_year) + str(end_date)
                            query += " where t1.startfrom  BETWEEN '" + str(june_start) + "' AND '" + str(
                                june_end) + "'"

                        if lines.months == '01-07':
                            jul_start = str(start_year) + str(start_date)
                            jul_end = str(start_year) + str(end_date)
                            query += " where t1.startfrom  BETWEEN '" + str(jul_start) + "' AND '" + str(
                                jul_end) + "' "

                        if lines.months == '01-08':
                            aug_start = str(start_year) + str(start_date)
                            aug_end = str(start_year) + str(end_date)
                            query += " where t1.startfrom  BETWEEN '" + str(aug_start) + "' AND '" + str(
                                aug_end) + "' "

                        if lines.months == '01-09':
                            sep_start = str(start_year) + str(start_date)
                            sep_end = str(start_year) + str(end_date)
                            query += " where t1.startfrom  BETWEEN '" + str(sep_start) + "' AND '" + str(
                                sep_end) + "'"

                        if lines.months == '01-10':
                            oct_start = str(start_year) + str(start_date)
                            oct_end = str(start_year) + str(end_date)
                            query += " where t1.startfrom  BETWEEN '" + str(oct_start) + "' AND '" + str(
                                oct_end) + "'"

                        if lines.months == '01-11':
                            nov_start = str(start_year) + str(start_date)
                            nov_end = str(start_year) + str(end_date)
                            query += " where t1.startfrom  BETWEEN '" + str(nov_start) + "' AND '" + str(
                                nov_end) + "'"

                        if lines.months == '01-12':
                            dec_start = str(start_year) + str(start_date)
                            dec_end = str(start_year) + str(end_date)
                            query += " where t1.startfrom  BETWEEN '" + str(dec_start) + "' AND '" + str(
                                dec_end) + "' "

                    if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                        query += " where t1.startfrom  BETWEEN '" + str(
                            lines.date_from + ' 00:00:00') + "' AND '" + str(
                            lines.date_to + ' 23:59:59') + "'"
                    if lines.location != 'all':
                        query += " and t1.location = '" + str(lines.location) + "'  group by t2.irda_cat, t2.name, t4.co_insurer_id, t5.name, t3.name, t1.name order by t3.name,t2.irda_cat"
                    else:
                        query += "  group by t2.irda_cat, t2.name, t4.co_insurer_id, t5.name, t3.name, t1.name order by t3.name,t2.irda_cat"

                    cr.execute(query)
                    usr_detail = cr.dictfetchall()
                    
                    return usr_detail

    def endos(self, workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1, end_year, id=None,endo=None):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        with registry.cursor() as cr:
            query = "select t1.name,t2.irda_cat,t2.name as category,t5.endo_id,t3.name as insurername," \
                    " case when 'Health'=t2.irda_cat" \
                    " then count(t2.irda_cat) else 0" \
                    " end as health_count," \
                    " case when 'Health'=t2.irda_cat then sum(t5.endo_net) else 0" \
                    " end  as health_premium," \
                    " case when 'Motor'=t2.irda_cat" \
                    " then count(t2.irda_cat) else 0" \
                    " end as motor_count," \
                    " case when 'Motor'=t2.irda_cat then sum(t5.endo_net) else 0" \
                    " end as motor_premium," \
                    " case when 'Liability'=t2.irda_cat" \
                    " then count(t2.irda_cat) else 0" \
                    " end as liability_count," \
                    " case when 'Liability'=t2.irda_cat then sum(t5.endo_net) else 0" \
                    " end as liability_premium," \
                    " case when 'Engineering'=t2.irda_cat" \
                    " then count(t2.irda_cat) else 0" \
                    " end as engineering_count," \
                    " case when 'Engineering'=t2.irda_cat then sum(t5.endo_net) else 0" \
                    " end as engineering_premium," \
                    " case when 'Fire'=t2.irda_cat" \
                    " then count(t2.irda_cat) else 0" \
                    " end as fire_count," \
                    " case when 'Fire'=t2.irda_cat then sum(t5.endo_net) else 0" \
                    " end as fire_premium," \
                    " case when 'Others'=t2.irda_cat" \
                    " then count(t2.irda_cat) else 0" \
                    " end as others_count," \
                    " case when 'Others'=t2.irda_cat then sum(t5.endo_net) else 0" \
                    " end as others_premium," \
                    " case when 'Life'=t2.irda_cat" \
                    " then count(t2.irda_cat) else 0" \
                    " end as life_count," \
                    " case when 'Life'=t2.irda_cat then sum(t5.endo_net) else 0" \
                    " end as life_premium," \
                    " case when 'Miscellaneous'=t2.irda_cat" \
                    " then count(t2.irda_cat) else 0" \
                    " end as miscellaneous_count," \
                    " case when 'Miscellaneous'=t2.irda_cat then sum(t5.endo_net) else 0 " \
                    " end as miscellaneous_premium," \
                    " case when 'Marine Cargo'=t2.irda_cat" \
                    " then count(t2.irda_cat) else 0" \
                    " end as marine_count," \
                    " case when 'Marine Cargo'=t2.irda_cat then sum(t5.endo_net) else 0 " \
                    " end as marine_premium" \
                    " from policytransaction as t1" \
                    " left join category_category as t2 on t2.id = t1.segment" \
                    " left join  endos_policy as t5 on t5.endo_id =t1.id" \
                    " left join  res_partner as t3 on t1.insurername123 =t3.id"





            if lines.filterby == 'all':
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t5.endos_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "'"

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "'"

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "' "

                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "'"

                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "'"

                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "'"

                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "'"

                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "' "

                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "' "

                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "'"

                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "'"

                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "'"

                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "' "

                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t5.endos_date  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "'"
                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "'  and t5.endo_id is not null group by t2.irda_cat,t2.name,t5.endo_id,t3.name,t1.name order by t3.name,t2.irda_cat"
                else:
                    query += " and t5.endo_id is not null group by t2.irda_cat,t2.name,t5.endo_id,t3.name,t1.name order by t3.name,t2.irda_cat"

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                
                return usr_detail

            elif lines.filterby == 'category':

                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where  t5.endos_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' AND t2.name = '" + str(
                        lines.category.name) + "'"

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "' AND t2.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where  t5.endos_date  BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "' AND t2.name = '" + str(
                            lines.category.name) + "'"

                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "' AND t2.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "' AND t2.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "' AND t2.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "' AND t2.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "' AND t2.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "' AND t2.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where  t5.endos_date  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "' AND t2.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "' AND t2.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "' AND t2.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "' AND t2.name = '" + str(lines.category.name) + "'"

                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t5.endos_date  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "' AND t2.name = '" + str(
                        lines.category.name) + "' "
                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "'and t5.endo_id is not null group by t2.irda_cat,t2.name,t5.endo_id,t3.name,t1.name order by t3.name,t2.irda_cat"
                else:
                    query += " and t5.endo_id is not null group by t2.irda_cat,t2.name,t5.endo_id,t3.name,t1.name order by t3.name,t2.irda_cat"

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                
                return usr_detail
            elif lines.filterby == 'insurername':
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t5.endos_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' AND t3.name = '" + str(lines.insurer_name.name) + "' "

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "' AND t3.name = '" + str(lines.insurer_name.name) + "'"

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "' AND t3.name = '" + str(lines.insurer_name.name) + "' "

                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "' AND t3.name = '" + str(lines.insurer_name.name) + "' "

                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "' AND t3.name = '" + str(lines.insurer_name.name) + "' "

                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "' AND t3.name = '" + str(lines.insurer_name.name) + "'"

                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "' AND t3.name = '" + str(lines.insurer_name.name) + "' "

                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "' AND t3.name = '" + str(lines.insurer_name.name) + "'"

                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "' AND t3.name = '" + str(lines.insurer_name.name) + "' "

                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "' AND t3.name = '" + str(lines.insurer_name.name) + "'"

                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "' AND t3.name = '" + str(lines.insurer_name.name) + "' "

                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "' AND t3.name = '" + str(lines.insurer_name.name) + "'"

                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "' AND t3.name = '" + str(lines.insurer_name.name) + "' "

                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t5.endos_date  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "' AND t3.name = '" + str(lines.insurer_name.name) + "'"

                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "'and t5.endo_id is not null group by t2.irda_cat,t2.name,t5.endo_id,t3.name,t1.name order by t3.name,t2.irda_cat"
                else:
                    query += " and t5.endo_id is not null group by t2.irda_cat,t2.name,t5.endo_id,t3.name,t1.name order by t3.name,t2.irda_cat"

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                
                return usr_detail
            else:
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t5.endos_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "'"

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "'"

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t5.endos_date BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "' "

                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "'"

                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "'"

                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "'"

                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "'"

                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "' "

                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "' "

                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "'"

                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "'"

                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "'"

                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t5.endos_date  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "' "

                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t5.endos_date  BETWEEN '" + str(
                        lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "'"
                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "'and t5.endo_id is not null group by t2.irda_cat,t2.name,t5.endo_id,t3.name,t1.name order by t3.name,t2.irda_cat"
                else:
                    query += " and t5.endo_id is not null group by t2.irda_cat,t2.name,t5.endo_id,t3.name,t1.name order by t3.name,t2.irda_cat"

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                
                return usr_detail




NonLifeInsurerXlsx('report.clickbima.non_life_insurer.xlsx', 'idranonlife.report')
