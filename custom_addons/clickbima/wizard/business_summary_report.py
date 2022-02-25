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

class Businesssummaryreport(models.TransientModel):
    _name = "businesssummary.report"
    _description = "Business Summary Report"

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    monthly = fields.Selection([('monthly', 'Monthly'), ('quatar', 'Quarterly'), ('yearly', 'Yearly')],
                               default='monthly',string="Period Type")
    quarter = fields.Selection([('q1', 'Quarter 1'), ('q2', 'Quarter 2'), ('q3', 'Quarter 3'), ('q4', 'Quarter 4')],
                               string='Quarter')
    groupby = fields.Selection([ ('create_date', 'Docket Date'), ('proposaldate', 'Proposal Date'),('startdate', 'Start Date')],
                               default='proposaldate', string="Group BY")
    filterby = fields.Selection([('insurername', 'Insurer Name'),('all','All')], default='all', string="Filter BY")
    location = fields.Selection([('9', 'Chandigarh'), ('8', 'Ludhiana'), ('7', 'New Delhi'), ('all', 'All')],
                                default='all', string="Location" )
    fiscal_year = fields.Many2one('fyyear', string="Financial Year",
                                  default=lambda self: self.env['fyyear'].search([('ex_active', '=', True)],
                                                                                 limit=1).id)
    months = fields.Selection(
        [('01-01', 'January'), ('01-02', 'February'), ('01-03', 'March'), ('01-04', 'April'), ('01-05', 'May'),
         ('01-06', 'June'),
         ('01-07', 'July'), ('01-08', 'August'), ('01-09', 'September'), ('01-10', 'October'), ('01-11', 'November'),
         ('01-12', 'December')])
    insurer_name = fields.Many2one('res.partner', string="Insurer Name", domain=[('customer','=',True),('is_company','=',True)])
    # insurer_branch = fields.Many2one('insurerbranch', string="Insurer Branch")
    start_year = fields.Char()
    end_year = fields.Char()

    @api.multi
    @api.onchange('category')
    def _compute_category_id(self):
        cat_id = self.category.id

    @api.multi
    @api.onchange('insurer_name')
    def compute_ptransaction1(self):
        res = {}
        locations = self.env['insurer'].search([('name', '=', self.insurer_name.id)])
        temp = []
        for i in locations:
            temp.append(i.branch.id)
        res['domain'] = ({'insurer_branch': [('id', 'in', temp)]})
        return res



    @api.onchange('monthly', 'months', 'fiscal_year')
    def onchange_monthly(self):
        import odoo
        import datetime
        if self.monthly  and self.fiscal_year:
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
        import odoo
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
    def generate_xlsx_report(self):
        data = {}
        data['form'] = self.read([])[0]
        return self.env['report'].get_action(self, report_name='clickbima.business_summary.xlsx', data=data)


from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
class BusinessSummary(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, lines):

        import odoo
        import datetime
        now = datetime.datetime.now()
        year = lines.fiscal_year.name
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
        if lines.filterby == 'insurername':
            filtname = 'Insurer Name'
        elif lines.filterby == 'insurerbranch':
            filtname = 'Insurer Branch'
        else:
            filtname = False
        groupname = ''
        if lines.groupby == 'create_date':
            groupname = 'Docket Date'
        elif lines.groupby == 'proposaldate':
            groupname = 'Proposal Date'
        elif lines.groupby == 'startdate':
            groupname = 'Start Date'
        else:
            groupname = 'All'
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

        import odoo
        import datetime
        x = datetime.datetime.now()

        # One sheet by partner
        report_name = "sheet 1"
        sheet = workbook.add_worksheet(report_name[:31])
        report_head = 'Security Insurance Brokers(India) Private Limited'

        merge_format = workbook.add_format(
            {'bold': 1, 'align': 'center', 'valign': 'vcenter', 'font_color': 'black'})
        merge_format1 = workbook.add_format(
            {'bold': 1, 'align': 'left', 'valign': 'vleft', 'font_color': 'black'})
        numbersformat = workbook.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'right'})
        numbersformat1 = workbook.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'right', 'bold': True})
        bold = workbook.add_format({'border': 1, 'bold': True, 'align': 'left'})
        bold1 = workbook.add_format({'bold': True, 'border': 1, 'align': 'right'})
        bold2 = workbook.add_format({'bold': True, 'border': 1, 'align': 'center'})
        bold3 = workbook.add_format({'bold': True, 'align': 'right'})
        border = workbook.add_format({'border': 1, 'align': 'center'})
        border2 = workbook.add_format({'border': 1, 'align': 'right'})
        border1 = workbook.add_format({'border': 1, 'align': 'left'})
        align_left = workbook.add_format({'align': 'left'})

        # report_head2 = 'Business Summary Report for the period of Proposal Start Date : ' + str(lines.date_from) + '  to End Date : ' + str(lines.date_to)
        report_head3 = 'Group by : ' + str(groupname) + '   Filter By : ' + str(filtname) + '   Start Date : ' + str(
            lines.date_from) + '  to End Date : ' + str(lines.date_to)
        report_head4 = str(loc)
        report_head5 = 'Business Summary'
        report_head6 = 'Printed On  ' + str(x.strftime("%x"))
        # sheet.write(0, 10, ('Printed On  ' + str(x.strftime("%x"))), merge_format)
        # sheet.write(1, 0, ('New Delhi-Nehru Place'), merge_format)
        # sheet.write(2, 0, ('Business Summary'), merge_format)
        sheet.write(10, 0, ('Sr. No.'), bold1)
        sheet.write(10, 1, ('Insurer Name'), bold)
        sheet.write(10, 2, ('Total No. of Policies'), bold2)
        sheet.write(10, 3, ('Sum Insured'), bold1)
        sheet.write(10, 4, ('Gross Premium'), bold1)
        sheet.write(10, 5, ('GST (Premium Amount)'), bold1)
        sheet.write(10, 6, ('Net Premium'), bold1)
        sheet.write(10, 7, ('Brokerage Premium'), bold1)
        sheet.write(10, 8, ('Third Party Premium'), bold1)
        sheet.write(10, 9, ('Brokerage Amount'), bold1)
        sheet.write(10, 10, ('GST(Brokerage) Amount'), bold1)
        # sheet.write(nrows + 11, 0, (' '), bold)
        # sheet.write(nrows + 11, 1, ('Total'), bold1)

        # increasing width of column
        sheet.set_column('A:A', 10)
        sheet.set_column('B:B', 80)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 15)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 20)
        sheet.set_column('J:J', 20)
        sheet.set_column('K:K', 20)
        sheet.set_column('L:L', 20)
        sheet.merge_range('A1:B1', report_head, merge_format1)
        sheet.merge_range('A2:B2', report_head4, merge_format1)
        sheet.merge_range('A3:B3', report_head5, merge_format1)
        sheet.merge_range('A5:L5', report_head3, merge_format)
        sheet.merge_range('J1:K1', report_head6, bold3)

        usr_detail = []
        usr_details = self.querys(workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1,
                                  end_year)

        endo_date = self.endos(workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1,
                               end_year)

        for j in endo_date:
            usr_detail.append(j)

        for i in usr_details:
            usr_detail.append(i)
        print(len(usr_detail), "lens")

        row = 11
        index = 0
        # s_no = 1

        if lines.groupby == 'create_date':
            temp = []
            s_no1 = 1
            totalsuminsuredcount = 0
            totalgrosspremcount = 0
            totalbrokpremcount = 0
            totalcommcount = 0
            totalnetpremcount = 0
            totaltppremcount = 0
            totalsertaxcount = 0
            totalservicetaxcount = 0
            totalpolcount = 0
            # an_iterator12 = sorted(usr_detail, key=operator.itemgetter('insurername'))
            an_iterator122 = sorted(usr_detail, key=operator.itemgetter('insurername'))
            new_lst = itertools.groupby(an_iterator122, key=operator.itemgetter('insurername'))
            for key, group in new_lst:
                key_and_group = {key: list(group)}
                for i in key_and_group.iteritems():
                    suminsur_null = 0
                    totalpol_null = 0
                    gross_null = 0
                    netprem_null = 0
                    brokprem_null = 0
                    comm_null = 0
                    sertaxamt_null = 0
                    totalpol = 0
                    totalnetprem = 0
                    totalgrossprem = 0
                    totaltpprem = 0
                    totalsuminsured = 0
                    totalservicetaxamt = 0
                    totalcommssionamt = 0
                    totalbrokprem = 0
                    totalsertaxamt = 0
                    for res in i[1]:
                        if res['total'] == None or res['total'] == False:
                            totalpol_null = 0
                        else:
                            totalpol_null = res['total']

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
                            servicetaxamt_null = 0
                        else:
                            servicetaxamt_null = res['servicetaxamt']
                        if res['servicetaxamt'] == None or res['servicetaxamt'] == False:
                            sertaxamt_null = 0
                        else:
                            sertaxamt_null = res['servicetaxamt']
                        if res['tppremium'] == None or res['tppremium'] == False:
                            tpprem_null = 0
                        else:
                            tpprem_null = res['tppremium']
                        totalpol += totalpol_null
                        totalnetprem += netprem_null
                        totalgrossprem += gross_null
                        totaltpprem += tpprem_null
                        totalbrokprem += brokprem_null
                        totalsuminsured += suminsur_null
                        totalservicetaxamt += servicetaxamt_null
                        totalcommssionamt += comm_null
                        totalsertaxamt += sertaxamt_null
                    sheet.write(row, 0, s_no1, border2)
                    sheet.write(row, 1, str(i[0]), border1)
                    sheet.write(row, 2, totalpol, border)
                    sheet.write(row, 3, totalsuminsured, numbersformat)
                    sheet.write(row, 4, totalgrossprem, numbersformat)
                    sheet.write(row, 5, totalservicetaxamt, numbersformat)
                    sheet.write(row, 6, totalnetprem, numbersformat)
                    sheet.write(row, 7, totalbrokprem, numbersformat)
                    sheet.write(row, 8, totaltpprem, numbersformat)
                    sheet.write(row, 9, totalcommssionamt, numbersformat)
                    sheet.write(row, 10, totalsertaxamt, numbersformat)
                    row = row + 1
                    index = index + 1
                    # sheet.write(row, 1, ('Start Date Total ') + i[0], bold2)
                    # sheet.write(row, 2, totalpol, bold2)
                    # sheet.write(row, 3, totalsuminsured, numbersformat1)
                    # sheet.write(row, 4, totalgrossprem, numbersformat1)
                    # sheet.write(row, 5, totalservicetaxamt, numbersformat1)
                    # sheet.write(row, 6, totalnetprem, numbersformat1)
                    # sheet.write(row, 7, totalbrokprem, numbersformat1)
                    # sheet.write(row, 8, totaltpprem, numbersformat1)
                    # sheet.write(row, 9, totalcommssionamt, numbersformat1)
                    # sheet.write(row, 10, totalsertaxamt, numbersformat1)
                    # row += 1
                totalpolcount += totalpol
                totalsuminsuredcount += totalsuminsured
                totalgrosspremcount += totalgrossprem
                totalbrokpremcount += totalbrokprem
                totalcommcount += totalcommssionamt
                totalnetpremcount += totalnetprem
                totalsertaxcount += totalsertaxamt
                totalservicetaxcount += totalservicetaxamt
                totaltppremcount += totaltpprem
                s_no1 = s_no1 + 1

            sheet.write(row, 1, str(' Total'), bold2)
            sheet.write(row, 2, totalpolcount, bold2)
            sheet.write(row, 3, totalsuminsuredcount, numbersformat1)
            sheet.write(row, 4, totalgrosspremcount, numbersformat1)
            sheet.write(row, 5, totalservicetaxcount, numbersformat1)
            sheet.write(row, 6, totalnetpremcount, numbersformat1)
            sheet.write(row, 7, totalbrokpremcount, numbersformat1)
            sheet.write(row, 8, totaltppremcount, numbersformat1)
            sheet.write(row, 9, totalcommcount, numbersformat1)
            sheet.write(row, 10, totalsertaxcount, numbersformat1)
            row += 1

        elif lines.groupby == 'proposaldate':
            temp = []
            s_no1 = 1
            totalsuminsuredcount = 0
            totalgrosspremcount = 0
            totalbrokpremcount = 0
            totalcommcount = 0
            totalnetpremcount = 0
            totaltppremcount = 0
            totalsertaxcount = 0
            totalservicetaxcount = 0
            totalpolcount = 0
            # an_iterator12 = sorted(usr_detail, key=operator.itemgetter('insurername'))
            an_iterator122 = sorted(usr_detail, key=operator.itemgetter('insurername'))
            new_lst = itertools.groupby(an_iterator122, key=operator.itemgetter('insurername'))
            for key, group in new_lst:
                key_and_group = {key: list(group)}
                for i in key_and_group.iteritems():
                    suminsur_null = 0
                    totalpol_null = 0
                    gross_null = 0
                    netprem_null = 0
                    brokprem_null = 0
                    comm_null = 0
                    sertaxamt_null = 0
                    totalpol = 0
                    totalnetprem = 0
                    totalgrossprem = 0
                    totaltpprem = 0
                    totalsuminsured = 0
                    totalservicetaxamt = 0
                    totalcommssionamt = 0
                    totalbrokprem = 0
                    totalsertaxamt = 0
                    for res in i[1]:
                        if res['total'] == None or res['total'] == False:
                            totalpol_null = 0
                        else:
                            totalpol_null = res['total']

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
                            servicetaxamt_null = 0
                        else:
                            servicetaxamt_null = res['servicetaxamt']
                        if res['servicetaxamt'] == None or res['servicetaxamt'] == False:
                            sertaxamt_null = 0
                        else:
                            sertaxamt_null = res['servicetaxamt']
                        if res['tppremium'] == None or res['tppremium'] == False:
                            tpprem_null = 0
                        else:
                            tpprem_null = res['tppremium']
                        totalpol += totalpol_null
                        totalnetprem += netprem_null
                        totalgrossprem += gross_null
                        totaltpprem += tpprem_null
                        totalbrokprem += brokprem_null
                        totalsuminsured += suminsur_null
                        totalservicetaxamt += servicetaxamt_null
                        totalcommssionamt += comm_null
                        totalsertaxamt += sertaxamt_null
                    sheet.write(row, 0, s_no1, border2)
                    sheet.write(row, 1, str(i[0]), border1)
                    sheet.write(row, 2, totalpol, border)
                    sheet.write(row, 3, totalsuminsured, numbersformat)
                    sheet.write(row, 4, totalgrossprem, numbersformat)
                    sheet.write(row, 5, totalservicetaxamt, numbersformat)
                    sheet.write(row, 6, totalnetprem, numbersformat)
                    sheet.write(row, 7, totalbrokprem, numbersformat)
                    sheet.write(row, 8, totaltpprem, numbersformat)
                    sheet.write(row, 9, totalcommssionamt, numbersformat)
                    sheet.write(row, 10, totalsertaxamt, numbersformat)
                    row = row + 1
                    index = index + 1
                    # sheet.write(row, 1, ('Start Date Total ') + i[0], bold2)
                    # sheet.write(row, 2, totalpol, bold2)
                    # sheet.write(row, 3, totalsuminsured, numbersformat1)
                    # sheet.write(row, 4, totalgrossprem, numbersformat1)
                    # sheet.write(row, 5, totalservicetaxamt, numbersformat1)
                    # sheet.write(row, 6, totalnetprem, numbersformat1)
                    # sheet.write(row, 7, totalbrokprem, numbersformat1)
                    # sheet.write(row, 8, totaltpprem, numbersformat1)
                    # sheet.write(row, 9, totalcommssionamt, numbersformat1)
                    # sheet.write(row, 10, totalsertaxamt, numbersformat1)
                    # row += 1
                totalpolcount += totalpol
                totalsuminsuredcount += totalsuminsured
                totalgrosspremcount += totalgrossprem
                totalbrokpremcount += totalbrokprem
                totalcommcount += totalcommssionamt
                totalnetpremcount += totalnetprem
                totalsertaxcount += totalsertaxamt
                totalservicetaxcount += totalservicetaxamt
                totaltppremcount += totaltpprem
                s_no1 = s_no1 + 1

            sheet.write(row, 1, str(' Total'), bold2)
            sheet.write(row, 2, totalpolcount, bold2)
            sheet.write(row, 3, totalsuminsuredcount, numbersformat1)
            sheet.write(row, 4, totalgrosspremcount, numbersformat1)
            sheet.write(row, 5, totalservicetaxcount, numbersformat1)
            sheet.write(row, 6, totalnetpremcount, numbersformat1)
            sheet.write(row, 7, totalbrokpremcount, numbersformat1)
            sheet.write(row, 8, totaltppremcount, numbersformat1)
            sheet.write(row, 9, totalcommcount, numbersformat1)
            sheet.write(row, 10, totalsertaxcount, numbersformat1)
            row += 1

        elif lines.groupby == 'startdate':
            s_no1 = 1
            totalsuminsuredcount = 0
            totalgrosspremcount = 0
            totalbrokpremcount = 0
            totalcommcount = 0
            totalnetpremcount = 0
            totaltppremcount = 0
            totalsertaxcount = 0
            totalservicetaxcount = 0
            totalpolcount = 0
            # import pandas as pd
            # df = pd.DataFrame(usr_detail)
            # df.groupby(['insurername'])['netprem','grossprem','suminsured',
            #                           'brokerageprem','commssionamt','servicetaxamt','tppremium','total'].sum()
            # print(df,"DATA")

            an_iterator12 = sorted(usr_detail, key=operator.itemgetter('insurername'))
            new_lst = itertools.groupby(an_iterator12, key=operator.itemgetter('insurername'))
            for key, group in new_lst:
                key_and_group = {key: list(group)}
                for i in key_and_group.iteritems():
                    print(i[0],"I")
                    suminsur_null = 0
                    totalpol_null = 0
                    gross_null = 0
                    netprem_null = 0
                    brokprem_null = 0
                    comm_null = 0
                    sertaxamt_null = 0
                    totalpol = 0
                    totalnetprem = 0
                    totalgrossprem = 0
                    totaltpprem = 0
                    totalsuminsured = 0
                    totalservicetaxamt = 0
                    totalcommssionamt = 0
                    totalbrokprem = 0
                    totalsertaxamt = 0
                    tpprem_null =0
                    servicetaxamt_null=0

                    for res in i[1]:
                        if res['total'] == None or res['total'] == False:
                            totalpol_null = 0
                        else:
                            totalpol_null = res['total']
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
                            servicetaxamt_null = 0
                        else:
                            servicetaxamt_null = res['servicetaxamt']
                        if res['servicetaxamt'] == None or res['servicetaxamt'] == False:
                            sertaxamt_null = 0
                        else:
                            sertaxamt_null = res['servicetaxamt']
                        if res['tppremium'] == None or res['tppremium'] == False:
                            tpprem_null = 0
                        else:
                            tpprem_null = res['tppremium']

                        totalpol += totalpol_null
                        totalnetprem += netprem_null
                        totalgrossprem += gross_null
                        totaltpprem += tpprem_null
                        totalbrokprem += brokprem_null
                        totalsuminsured += suminsur_null
                        totalservicetaxamt += servicetaxamt_null
                        totalcommssionamt += comm_null
                        totalsertaxamt += sertaxamt_null

                    sheet.write(row, 0, s_no1, border2)
                    sheet.write(row, 1, str(i[0]), border1)
                    sheet.write(row, 2, totalpol, border)
                    sheet.write(row, 3, totalsuminsured, numbersformat)
                    sheet.write(row, 4, totalgrossprem, numbersformat)
                    sheet.write(row, 5, totalservicetaxamt, numbersformat)
                    sheet.write(row, 6, totalnetprem, numbersformat)
                    sheet.write(row, 7, totalbrokprem, numbersformat)
                    sheet.write(row, 8, totaltpprem, numbersformat)
                    sheet.write(row, 9, totalcommssionamt, numbersformat)
                    sheet.write(row, 10, totalsertaxamt, numbersformat)
                    row = row + 1
                    index = index + 1
                        # sheet.write(row, 1, ('Start Date Total ') + i[0], bold2)
                        # sheet.write(row, 2, totalpol, bold2)
                        # sheet.write(row, 3, totalsuminsured, numbersformat1)
                        # sheet.write(row, 4, totalgrossprem, numbersformat1)
                        # sheet.write(row, 5, totalservicetaxamt, numbersformat1)
                        # sheet.write(row, 6, totalnetprem, numbersformat1)
                        # sheet.write(row, 7, totalbrokprem, numbersformat1)
                        # sheet.write(row, 8, totaltpprem, numbersformat1)
                        # sheet.write(row, 9, totalcommssionamt, numbersformat1)
                        # sheet.write(row, 10, totalsertaxamt, numbersformat1)
                        # row += 1
                    totalpolcount += totalpol
                    totalsuminsuredcount += totalsuminsured
                    totalgrosspremcount += totalgrossprem
                    totalbrokpremcount += totalbrokprem
                    totalcommcount += totalcommssionamt
                    totalnetpremcount += totalnetprem
                    totalsertaxcount += totalsertaxamt
                    totalservicetaxcount += totalservicetaxamt
                    totaltppremcount += totaltpprem
                    s_no1 = s_no1 + 1

            sheet.write(row, 1, str(' Total'), bold2)
            sheet.write(row, 2, totalpolcount, bold2)
            sheet.write(row, 3, totalsuminsuredcount, numbersformat1)
            sheet.write(row, 4, totalgrosspremcount, numbersformat1)
            sheet.write(row, 5, totalservicetaxcount, numbersformat1)
            sheet.write(row, 6, totalnetpremcount, numbersformat1)
            sheet.write(row, 7, totalbrokpremcount, numbersformat1)
            sheet.write(row, 8, totaltppremcount, numbersformat1)
            sheet.write(row, 9, totalcommcount, numbersformat1)
            sheet.write(row, 10, totalsertaxcount, numbersformat1)
            row += 1

        else:
            temp = []
            s_no1=1
            totalsuminsuredcount = 0
            totalgrosspremcount = 0
            totalbrokpremcount = 0
            totalcommcount = 0
            totalnetpremcount = 0
            totaltppremcount = 0
            totalsertaxcount = 0
            totalservicetaxcount = 0
            totalpolcount = 0
            # an_iterator12 = sorted(usr_detail, key=operator.itemgetter('docketdate'))
            new_lst = itertools.groupby(usr_detail, key=operator.itemgetter('insurername'))
            for key, group in new_lst:
                key_and_group = {key: list(group)}
                for i in key_and_group.iteritems():
                    suminsur_null = 0
                    totalpol_null = 0
                    gross_null = 0
                    netprem_null = 0
                    brokprem_null = 0
                    comm_null = 0
                    sertaxamt_null = 0
                    totalpol = 0
                    totalnetprem = 0
                    totalgrossprem = 0
                    totaltpprem = 0
                    totalsuminsured = 0
                    totalservicetaxamt = 0
                    totalcommssionamt = 0
                    totalbrokprem = 0
                    totalsertaxamt = 0
                    for res in i[1]:

                        if res['total'] == None or res['total'] == False:
                            totalpol_null = 0
                        else:
                            totalpol_null = res['total']
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
                            servicetaxamt_null = 0
                        else:
                            servicetaxamt_null = res['servicetaxamt']
                        if res['servicetaxamt'] == None or res['servicetaxamt'] == False:
                            sertaxamt_null = 0
                        else:
                            sertaxamt_null = res['servicetaxamt']
                        if res['tppremium'] == None or res['tppremium'] == False:
                            tpprem_null = 0
                        else:
                            tpprem_null = res['tppremium']
                        totalpol += totalpol_null
                        totalnetprem += netprem_null
                        totalgrossprem += gross_null
                        totaltpprem += tpprem_null
                        totalbrokprem += brokprem_null
                        totalsuminsured += suminsur_null
                        totalservicetaxamt += servicetaxamt_null
                        totalcommssionamt += comm_null
                        totalsertaxamt += sertaxamt_null
                    sheet.write(row, 0, s_no1, border2)
                    sheet.write(row, 1, str(i[0]), border1)
                    sheet.write(row, 2, totalpol, border)
                    sheet.write(row, 3, totalsuminsured, numbersformat)
                    sheet.write(row, 4, totalgrossprem, numbersformat)
                    sheet.write(row, 5, totalservicetaxamt, numbersformat)
                    sheet.write(row, 6, totalnetprem, numbersformat)
                    sheet.write(row, 7, totalbrokprem, numbersformat)
                    sheet.write(row, 8, totaltpprem, numbersformat)
                    sheet.write(row, 9, totalcommssionamt, numbersformat)
                    sheet.write(row, 10, totalsertaxamt, numbersformat)
                    row = row + 1
                    index = index + 1
                    # sheet.write(row, 1, ('Start Date Total ') + i[0], bold2)
                    # sheet.write(row, 2, totalpol, bold2)
                    # sheet.write(row, 3, totalsuminsured, numbersformat1)
                    # sheet.write(row, 4, totalgrossprem, numbersformat1)
                    # sheet.write(row, 5, totalservicetaxamt, numbersformat1)
                    # sheet.write(row, 6, totalnetprem, numbersformat1)
                    # sheet.write(row, 7, totalbrokprem, numbersformat1)
                    # sheet.write(row, 8, totaltpprem, numbersformat1)
                    # sheet.write(row, 9, totalcommssionamt, numbersformat1)
                    # sheet.write(row, 10, totalsertaxamt, numbersformat1)
                    # row += 1
                totalpolcount += totalpol
                totalsuminsuredcount += totalsuminsured
                totalgrosspremcount += totalgrossprem
                totalbrokpremcount += totalbrokprem
                totalcommcount += totalcommssionamt
                totalnetpremcount += totalnetprem
                totalsertaxcount += totalsertaxamt
                totalservicetaxcount += totalservicetaxamt
                totaltppremcount += totaltpprem
                s_no1 = s_no1 + 1

            sheet.write(row, 1, str(' Total'), bold2)
            sheet.write(row, 2, totalpolcount, bold2)
            sheet.write(row, 3, totalsuminsuredcount, numbersformat1)
            sheet.write(row, 4, totalgrosspremcount, numbersformat1)
            sheet.write(row, 5, totalservicetaxcount, numbersformat1)
            sheet.write(row, 6, totalnetpremcount, numbersformat1)
            sheet.write(row, 7, totalbrokpremcount, numbersformat1)
            sheet.write(row, 8, totaltppremcount, numbersformat1)
            sheet.write(row, 9, totalcommcount, numbersformat1)
            sheet.write(row, 10, totalsertaxcount, numbersformat1)
            row += 1

    def querys(self, workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1, end_year,id=None, endo=None):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        with registry.cursor() as cr:
            # query = "select case when t8.co_insurer_id is not null then t9.name else t3.name end as insurername," \
            #         " case when t8.co_insurer_id is not null then t10.name else t2.name end as insurerbranch," \
            #         " case when t8.co_insurer_id is not null then count(t9.name) else count(t3.name) end as total," \
            #         " case when t8.co_insurer_id is not null  then sum(t8.co_net_premium) else sum(t1.netprem)" \
            #         " end as netprem," \
            #         " case when t8.co_insurer_id is not null  then sum(t8.co_net_gross_pre) else sum(t1.grossprem)" \
            #         " end  as grossprem," \
            #         " case when t8.co_insurer_id is not null then sum(t8.co_sum_insured) else sum(t1.suminsured)" \
            #         " end as suminsured," \
            #         " case when t8.co_insurer_id is not null then sum(t8.co_brokerage_pre) else sum(t1.brokerageprem)" \
            #         " end  as brokerageprem," \
            #         " case when t8.co_insurer_id is not null then sum(t8.co_commission_amount) else sum(t1.commssionamt)" \
            #         " end as commssionamt," \
            #         " case when t8.co_insurer_id is not null then 0 else sum(t1.servicetaxamt)" \
            #         " end  as servicetaxamt," \
            #         " case when t8.co_insurer_id is not null then 0 else sum(t1.tppremium)" \
            #         " end  as tppremium" \
            #         " from policytransaction as t1 left join insurerbranch as t2 on t2.id = t1.insurerbranch" \
            #         " left join co_insurer_policy as t8 on t8.co_insurer_id = t1.id AND t8.co_type = 'self'" \
            #         " left join insurerbranch as t10 on t10.id=t8.co_insurer_branch" \
            #         " left join res_partner as t9 on t9.id=t8.co_insurer_name" \
            #         " left join res_partner as t3 on t3.id=t1.insurername123"

            query ="select insurername ,sum(a.total) as total,sum(a.netprem) as netprem," \
                   " sum(a.grossprem) as grossprem ," \
                   " sum(a.tppremium) as tppremium ," \
                   " sum(a.servicetaxamt) as servicetaxamt," \
                   " sum(a.commssionamt) as commssionamt,sum(a.brokerageprem) as brokerageprem," \
                   " sum(a.suminsured) as suminsured from (select " \
                   " case when t8.co_insurer_id is not null then t9.name else t3.name end as insurername, " \
                   " case when t8.co_insurer_id is not null then t10.name else t2.name end as insurerbranch, " \
                   " case when t8.co_insurer_id is not null then count(t9.name) else count(t3.name) end as total, " \
                   " case when t8.co_insurer_id is not null  then sum(t8.co_net_premium) else sum(t1.netprem) " \
                   " end as netprem, " \
                   " case when t8.co_insurer_id is not null  then sum(t8.co_net_gross_pre) else sum(t1.grossprem) " \
                   " end  as grossprem, " \
                   " case when t8.co_insurer_id is not null then sum(t8.co_sum_insured) else sum(t1.suminsured) " \
                   " end as suminsured, " \
                   " case when t8.co_insurer_id is not null then sum(t8.co_brokerage_pre) else sum(t1.brokerageprem) " \
                   " end  as brokerageprem, " \
                   " case when t8.co_insurer_id is not null then sum(t8.co_commission_amount) else sum(t1.commssionamt) " \
                   " end as commssionamt, " \
                   " case when t8.co_insurer_id is not null then 0 else sum(t1.servicetaxamt) " \
                   " end  as servicetaxamt, " \
                   " case when t8.co_insurer_id is not null then 0 else sum(t1.tppremium) " \
                   " end  as tppremium " \
                   " from policytransaction as t1 left join insurerbranch as t2 on t2.id = t1.insurerbranch " \
                   " left join co_insurer_policy as t8 on t8.co_insurer_id = t1.id AND t8.co_type = 'self' " \
                   " left join insurerbranch as t10 on t10.id=t8.co_insurer_branch " \
                   " left join res_partner as t9 on t9.id=t8.co_insurer_name " \
                   " left join res_partner as t3 on t3.id=t1.insurername123" \



        # with registry.cursor() as cr:
        #     query1 = "select t1.date2 as docketdate,t8.co_insurer_id, t1.proposaldate as proposaldate, t1.startfrom as startdate," \
        #             " case when t8.co_insurer_id is not null then t9.name else t3.name end as insurername," \
        #             " case when t8.co_insurer_id is not null then t10.name else t2.name end as insurerbranch," \
        #             " case when t8.co_insurer_id is not null then count(t9.name) else count(t3.name) end as total," \
        #             " case when t8.co_insurer_id is not null  then sum(t8.co_net_premium) else sum(t1.netprem)" \
        #             " end as netprem," \
        #             " case when t8.co_insurer_id is not null  then sum(t8.co_net_gross_pre) else sum(t1.grossprem)" \
        #             " end  as grossprem," \
        #             " case when t8.co_insurer_id is not null then sum(t8.co_sum_insured) else sum(t1.suminsured)" \
        #             " end as suminsured," \
        #             " case when t8.co_insurer_id is not null then sum(t8.co_brokerage_pre) else sum(t1.brokerageprem)" \
        #             " end  as brokerageprem," \
        #             " case when t8.co_insurer_id is not null then sum(t8.co_commission_amount) else sum(t1.commssionamt)" \
        #             " end as commssionamt," \
        #             " case when t8.co_insurer_id is not null then 0 else sum(t1.servicetaxamt)" \
        #             " end  as servicetaxamt," \
        #             " case when t8.co_insurer_id is not null then 0 else sum(t1.tppremium)" \
        #             " end  as tppremium" \
        #             " from policytransaction as t1 left join insurerbranch as t2 on t2.id = t1.insurerbranch" \
        #             " left join co_insurer_policy as t8 on t8.co_insurer_id = t1.id AND t8.co_type = 'self'" \
        #             " left join insurerbranch as t10 on t10.id=t8.co_insurer_branch" \
        #             " left join res_partner as t9 on t9.id=t8.co_insurer_name" \
        #             " left join res_partner as t3 on t3.id=t1.insurername123"


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
                        lines.fiscal_year.date_end) + "'"
                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
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
                            apr_end) + "'"
                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "' "
                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "' "
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
                            dec_end) + "'"
                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                        lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "'"

                if lines.location != 'all':
                    query += " and t1.location = '" +str(lines.location) + "' AND (t3.name = '" + str(lines.insurer_name.name) + "' or t9.name = '" + str(lines.insurer_name.name) + "')" \
                             " group by case when t8.co_insurer_id is not null then t9.name else t3.name end," \
                             " case when t8.co_insurer_id is not null then t10.name else t2.name end,t8.co_insurer_id order by insurername) as a  group by a.insurername"
                    # if lines.groupby == 'proposaldate':
                    #     query += " ,t8.co_insurer_id order by t3.name,t9.name"
                    # if lines.groupby == 'startdate':
                    #     query += " ,t8.co_insurer_id order by t3.name,t9.name"
                    # if lines.groupby == 'create_date':
                    #     query += " ,t8.co_insurer_id  order by t3.name,t9.name"

                else:
                    query += "  AND (t3.name = '" + str(lines.insurer_name.name) + "' or t9.name = '" + str(
                        lines.insurer_name.name) + "')" \
                        " group by case when t8.co_insurer_id is not null then t9.name else t3.name end," \
                        " case when t8.co_insurer_id is not null then t10.name else t2.name end,t8.co_insurer_id order by insurername) as a  group by a.insurername"

                    # if lines.groupby == 'proposaldate':
                    #     query += " ,t8.co_insurer_id order by t3.name,t9.name"
                    # if lines.groupby == 'startdate':
                    #     query += " ,t8.co_insurer_id order by t3.name,t9.name"
                    # if lines.groupby == 'create_date':
                    #     query += " ,t8.co_insurer_id order by t3.name,t9.name"

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                
                return usr_detail

            # elif lines.filterby == 'insurerbranch':
            #
            #     if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
            #         query1 += " where " + str(dy_date) + "  BETWEEN '" + str(
            #             lines.fiscal_year.date_start) + "' AND '" + str(
            #             lines.fiscal_year.date_end) + "' "
            #     if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
            #         year = lines.fiscal_year.name
            #         if lines.months == '01-01':
            #             jan_start = str(end_year) + str(start_date)
            #             jan_end = str(end_year) + str(end_date)
            #             query1 += " where " + str(dy_date) + "  BETWEEN '" + str(jan_start) + "' AND '" + str(
            #                 jan_end) + "' "
            #         if lines.months == '01-02':
            #             feb_start = str(end_year) + str(start_date)
            #             feb_end = str(end_year) + str(end_date)
            #             query1 += " where " + str(dy_date) + "  BETWEEN '" + str(feb_start) + "' AND '" + str(
            #                 feb_end) + "' "
            #         if lines.months == '01-03':
            #             mar_start = str(end_year) + str(start_date)
            #             mar_end = str(end_year) + str(end_date)
            #             query1 += " where " + str(dy_date) + "  BETWEEN '" + str(mar_start) + "' AND '" + str(
            #                 mar_end) + "' "
            #         if lines.months == '01-04':
            #             apr_start = str(start_year) + str(start_date)
            #             apr_end = str(start_year) + str(end_date)
            #             query1 += " where " + str(dy_date) + "  BETWEEN '" + str(apr_start) + "' AND '" + str(
            #                 apr_end) + "' "
            #         if lines.months == '01-05':
            #             may_start = str(start_year) + str(start_date)
            #             may_end = str(start_year) + str(end_date)
            #             query1 += " where " + str(dy_date) + "  BETWEEN '" + str(may_start) + "' AND '" + str(
            #                 may_end) + "' "
            #         if lines.months == '01-06':
            #             june_start = str(start_year) + str(start_date)
            #             june_end = str(start_year) + str(end_date)
            #             query1 += " where " + str(dy_date) + "  BETWEEN '" + str(june_start) + "' AND '" + str(
            #                 june_end) + "' "
            #         if lines.months == '01-07':
            #             jul_start = str(start_year) + str(start_date)
            #             jul_end = str(start_year) + str(end_date)
            #             query1 += " where " + str(dy_date) + "  BETWEEN '" + str(jul_start) + "' AND '" + str(
            #                 jul_end) + "' "
            #         if lines.months == '01-08':
            #             aug_start = str(start_year) + str(start_date)
            #             aug_end = str(start_year) + str(end_date)
            #             query1 += " where " + str(dy_date) + "  BETWEEN '" + str(aug_start) + "' AND '" + str(
            #                 aug_end) + "' "
            #         if lines.months == '01-09':
            #             sep_start = str(start_year) + str(start_date)
            #             sep_end = str(start_year) + str(end_date)
            #             query1 += " where " + str(dy_date) + "  BETWEEN '" + str(sep_start) + "' AND '" + str(
            #                 sep_end) + "' "
            #         if lines.months == '01-10':
            #             oct_start = str(start_year) + str(start_date)
            #             oct_end = str(start_year) + str(end_date)
            #             query1 += " where " + str(dy_date) + "  BETWEEN '" + str(oct_start) + "' AND '" + str(
            #                 oct_end) + "' "
            #         if lines.months == '01-11':
            #             nov_start = str(start_year) + str(start_date)
            #             nov_end = str(start_year) + str(end_date)
            #             query1 += " where " + str(dy_date) + "  BETWEEN '" + str(nov_start) + "' AND '" + str(
            #                 nov_end) + "' "
            #         if lines.months == '01-12':
            #             dec_start = str(start_year) + str(start_date)
            #             dec_end = str(start_year) + str(end_date)
            #             query1 += " where " + str(dy_date) + "  BETWEEN '" + str(dec_start) + "' AND '" + str(
            #                 dec_end) + "' "
            #     if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
            #         query1 += " where " + str(dy_date) + "  BETWEEN '" + str(
            #             lines.date_from + ' 00:00:00') + "' AND '" + str(
            #             lines.date_to + ' 23:59:59') + "' "
            #     query += "  AND (t3.name = '" + str(lines.insurer_name.name) + "' or t9.name = '" + str(lines.insurer_name.name) + "') AND (t2.name = '" + str(lines.insurer_branch.name) + "'" \
            #             "or t10.name = '" + str(lines.insurer_branch.name) + "') group by t8.co_insurer_id,t1.id,t1.date2,t1.startfrom," \
            #                                    " t1.proposaldate,t3.name,t9.name,t2.name,t10.name order by t3.name"
            #
            #     cr.execute(query)
            #     usr_detail = cr.dictfetchall()
            #     return usr_detail
            else:
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where " + str(dy_date) + "  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' "
                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start =str(end_year)+str(start_date)
                        jan_end =str(end_year)+str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "' "
                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(feb_start) + "' AND '" + str(feb_end) + "' "
                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(mar_start) + "' AND '" + str(mar_end) + "' "
                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(apr_start) + "' AND '" + str(apr_end) + "' "
                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(may_start) + "' AND '" + str(may_end) + "' "
                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(june_start) + "' AND '" + str(june_end) + "' "
                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(jul_start) + "' AND '" + str(jul_end) + "' "
                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(aug_start) + "' AND '" + str(aug_end) + "' "
                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(sep_start) + "' AND '" + str(sep_end) + "' "
                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(oct_start) + "' AND '" + str(oct_end) + "' "
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(nov_start) + "' AND '" + str(nov_end) + "' "
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(dec_start) + "' AND '" + str(dec_end) + "' "
                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where " + str(dy_date) + "  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(lines.date_to + ' 23:59:59') + "' "

                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "'  group by t2.name,t8.co_insurer_id,t9.name,t3.name,t10.name order by insurername) as a " \
                                                                            " group by a.insurername "
                    # if lines.groupby == 'proposaldate':
                    #     query += " ,t8.co_insurer_id by t3.name,t9.name"
                    # if lines.groupby == 'startdate':
                    #     query += " ,t8.co_insurer_id order by t3.name,t9.name"
                    # if lines.groupby == 'create_date':
                    #     query += " ,t8.co_insurer_id order by t3.name,t9.name"
                else:
                    query +=  " group by t2.name,t8.co_insurer_id,t9.name,t3.name,t10.name order by insurername) as a " \
                              " group by a.insurername "
                    # if lines.groupby == 'proposaldate':
                    #     query += " ,t8.co_insurer_id order by t3.name,t9.name"
                    # if lines.groupby == 'startdate':
                    #     query += " ,t8.co_insurer_id order by t3.name,t9.name"
                    # if lines.groupby == 'create_date':
                    #     query += " ,t8.co_insurer_id order by t3.name,t9.name"
                cr.execute(query)
                usr_detail = cr.dictfetchall()
                
                return usr_detail



    def endos(self, workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1, end_year, id=None,endo=None):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        with registry.cursor() as cr:
            # query = "select "\

            # if lines.groupby == 'proposaldate':
            #             query += " t1.proposaldate as proposaldate,"
            # if lines.groupby == 'startdate':
            #     query += " t1.startfrom as startdate,"
            # if lines.groupby == 'create_date':
            #     query += " t1.date2 as docketdate,"
            #
            # query = "select insurername,insurerbranch,sum(a.total) as total,sum(a.netprem) as netprem," \
            #         " sum(a.grossprem) as grossprem ," \
            #         " sum(a.tppremium) as tppremium ," \
            #         " sum(a.servicetaxamt) as servicetaxamt," \
            #         " sum(a.commssionamt) as commssionamt,sum(a.brokerageprem) as brokerageprem," \
            #         " sum(a.suminsured) as suminsured from (select t3.name as insurername,t2.name as insurerbranch, count(t3.name) as total, " \
            #         " case when t8.endo_id is not null  then sum(t8.endo_net) else 0 " \
            #         " end as netprem," \
            #         " case when t8.endo_id is not null  then sum(t8.endo_gst_gross) else 0 " \
            #         " end  as grossprem, " \
            #         " case when t8.endo_id is not null then sum(t8.endos_suminsured) else 0 " \
            #         " end as suminsured, " \
            #         " case when t8.endo_id is not null then sum(t8.endos_brokerage_premium) else 0 " \
            #         " end  as brokerageprem, " \
            #         " case when t8.endo_id is not null then sum(t8.endo_commission) else 0 " \
            #         " end as commssionamt, " \
            #         " case when t8.endo_id is not null then sum(t8.endo_gst_amount) else 0 " \
            #         " end  as servicetaxamt, " \
            #         " case when t8.endo_id is not null then sum(t8.endo_tp) else 0 " \
            #         " end  as tppremium " \
            #         " from policytransaction as t1 left join insurerbranch as t2 on t2.id = t1.insurerbranch " \
            #         " left join endos_policy as t8 on t8.endo_id =t1.id " \
            #         " left join res_partner as t3 on t3.id=t1.insurername123"


            query = " select t3.name as insurername," \
                    " count(t3.name) as total,sum(t8.endo_net) as netprem," \
                    " sum(t8.endo_gst_gross) as grossprem ," \
                    " sum(t8.endo_tp) as tppremium ," \
                    " sum(t8.endo_gst_amount) as servicetaxamt," \
                    " sum(t8.endo_commission) as commssionamt," \
                    " sum(t8.endos_brokerage_premium) as brokerageprem," \
                    " sum(t8.endos_suminsured) as suminsured " \
                    " from policytransaction as t1 " \
                    " left join insurerbranch as t2 on t2.id = t1.insurerbranch " \
                    " left join endos_policy as t8 on t8.endo_id =t1.id " \
                    " left join res_partner as t3 on t3.id=t1.insurername123"


                # with registry.cursor() as cr:
        #     query1 = "select t1.date2 as docketdate,t8.endo_id, t1.proposaldate as proposaldate, t1.startfrom as startdate," \
        #              " t3.name as insurername, count(t3.name) as total,t2.name as insurerbranch," \
        #               " case when t8.endo_id is not null  then sum(t8.co_net_premium) else 0" \
        #             " end as netprem," \
        #             " case when t8.endo_id is not null  then sum(t8.endo_gst_gross) else 0" \
        #             " end  as grossprem," \
        #             " case when t8.endo_id is not null then sum(t8.endos_suminsured) else 0" \
        #             " end as suminsured," \
        #             " case when t8.endo_id is not null then sum(t8.endos_brokerage_premium) else 0" \
        #             " end  as brokerageprem," \
        #             " case when t8.endo_id is not null then sum(t8.endo_commission) else 0" \
        #             " end as commssionamt," \
        #             " case when t8.endo_id is not null then sum(t8.endo_gst_amount) else 0" \
        #             " end  as servicetaxamt," \
        #             " case when t8.endo_id is not null then sum(t8.endo_tp) else 0" \
        #             " end  as tppremium" \
        #              " from policytransaction as t1 left join insurerbranch as t2 on t2.id = t1.insurerbranch" \
        #              " left join endos_policy as t8 on t8.endo_id =t1.id" \
        #              " left join res_partner as t3 on t3.id=t1.insurername123"

            golbal = []


            if lines.filterby == 'insurername':
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t8.endos_date  BETWEEN '" + str(
                        lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "'"
                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "' "
                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "' "
                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "' "
                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "'"
                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "' "
                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "' "
                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(jul_start) + "' AND '" + str(
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
                        query += " where t8.endos_date  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "' "
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "' "

                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "'"
                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t8.endos_date  BETWEEN '" + str(
                        lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "'"

                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "' AND t3.name = '" + str(lines.insurer_name.name) + "'  and t8.endo_id is not null group by t8.endo_id"
                    if lines.groupby == 'proposaldate':
                        query += " ,t3.name order by t3.name"
                    if lines.groupby == 'startdate':
                        query += " ,t3.name order by t3.name"
                    if lines.groupby == 'create_date':
                        query += " ,t8.endo_id,t3.name order by t3.name"
                else:
                    query += "  AND t3.name = '" + str(lines.insurer_name.name) + "' and t8.endo_id is not null group by t8.endo_id"
                    if lines.groupby == 'proposaldate':
                        query += " ,t3.name order by t3.name"
                    if lines.groupby == 'startdate':
                        query += " ,t3.name order by t3.name"
                    if lines.groupby == 'create_date':
                        query += " ,t3.name order by t3.name"

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                
                return usr_detail

            # elif lines.filterby == 'insurerbranch':
            #
            #     if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
            #         query1 += " where t8.endos_date  BETWEEN '" + str(
            #             lines.fiscal_year.date_start) + "' AND '" + str(
            #             lines.fiscal_year.date_end) + "' "
            #     if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
            #         year = lines.fiscal_year.name
            #         if lines.months == '01-01':
            #             jan_start = str(end_year) + str(start_date)
            #             jan_end = str(end_year) + str(end_date)
            #             query1 += " where t8.endos_date  BETWEEN '" + str(jan_start) + "' AND '" + str(
            #                 jan_end) + "' "
            #         if lines.months == '01-02':
            #             feb_start = str(end_year) + str(start_date)
            #             feb_end = str(end_year) + str(end_date)
            #             query1 += " where t8.endos_date  BETWEEN '" + str(feb_start) + "' AND '" + str(
            #                 feb_end) + "' "
            #         if lines.months == '01-03':
            #             mar_start = str(end_year) + str(start_date)
            #             mar_end = str(end_year) + str(end_date)
            #             query1 += " where t8.endos_date BETWEEN '" + str(mar_start) + "' AND '" + str(
            #                 mar_end) + "' "
            #         if lines.months == '01-04':
            #             apr_start = str(start_year) + str(start_date)
            #             apr_end = str(start_year) + str(end_date)
            #             query1 += " where t8.endos_date  BETWEEN '" + str(apr_start) + "' AND '" + str(
            #                 apr_end) + "' "
            #         if lines.months == '01-05':
            #             may_start = str(start_year) + str(start_date)
            #             may_end = str(start_year) + str(end_date)
            #             query1 += " where t8.endos_date BETWEEN '" + str(may_start) + "' AND '" + str(
            #                 may_end) + "' "
            #         if lines.months == '01-06':
            #             june_start = str(start_year) + str(start_date)
            #             june_end = str(start_year) + str(end_date)
            #             query1 += " where t8.endos_date  BETWEEN '" + str(june_start) + "' AND '" + str(
            #                 june_end) + "' "
            #         if lines.months == '01-07':
            #             jul_start = str(start_year) + str(start_date)
            #             jul_end = str(start_year) + str(end_date)
            #             query1 += " where t8.endos_date  BETWEEN '" + str(jul_start) + "' AND '" + str(
            #                 jul_end) + "' "
            #         if lines.months == '01-08':
            #             aug_start = str(start_year) + str(start_date)
            #             aug_end = str(start_year) + str(end_date)
            #             query1 += " where t8.endos_date  BETWEEN '" + str(aug_start) + "' AND '" + str(
            #                 aug_end) + "' "
            #         if lines.months == '01-09':
            #             sep_start = str(start_year) + str(start_date)
            #             sep_end = str(start_year) + str(end_date)
            #             query1 += " where t8.endos_date  BETWEEN '" + str(sep_start) + "' AND '" + str(
            #                 sep_end) + "' "
            #         if lines.months == '01-10':
            #             oct_start = str(start_year) + str(start_date)
            #             oct_end = str(start_year) + str(end_date)
            #             query1 += " where t8.endos_date  BETWEEN '" + str(oct_start) + "' AND '" + str(
            #                 oct_end) + "' "
            #         if lines.months == '01-11':
            #             nov_start = str(start_year) + str(start_date)
            #             nov_end = str(start_year) + str(end_date)
            #             query1 += " where t8.endos_date  BETWEEN '" + str(nov_start) + "' AND '" + str(
            #                 nov_end) + "' "
            #         if lines.months == '01-12':
            #             dec_start = str(start_year) + str(start_date)
            #             dec_end = str(start_year) + str(end_date)
            #             query1 += " where t8.endos_date  BETWEEN '" + str(dec_start) + "' AND '" + str(
            #                 dec_end) + "' "
            #     if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
            #         query1 += " where t8.endos_date  BETWEEN '" + str(
            #             lines.date_from + ' 00:00:00') + "' AND '" + str(
            #             lines.date_to + ' 23:59:59') + "' "
            #     query += "  AND (t3.name = '" + str(lines.insurer_name.name) + "' or t9.name = '" + str(
            #         lines.insurer_name.name) + "') AND (t2.name = '" + str(lines.insurer_branch.name) + "'" \
            #                                                                                             "or t10.name = '" + str(
            #         lines.insurer_branch.name) + "') and t8.endo_id is not null group by t8.endo_id,t1.id,t1.date2,t1.startfrom," \
            #                                      " t1.proposaldate,t3.name,t2.name order by t3.name"
            #
            #     cr.execute(query)
            #     usr_detail = cr.dictfetchall()
            #     return usr_detail
            else:
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t8.endos_date  BETWEEN '" + str(
                        lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' "
                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)

                        query += " where t8.endos_date BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "' "
                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "' "
                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "' "
                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "' "
                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "' "
                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "' "
                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "' "
                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(aug_start) + "' AND '" + str(
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
                        query += " where t8.endos_date  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "' "
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "' "
                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t8.endos_date  BETWEEN '" + str(
                        lines.date_from + ' 00:00:00') + "' AND '" + str(lines.date_to + ' 23:59:59') + "' "

                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "' and t8.endo_id is not null group by "
                    if lines.groupby == 'proposaldate':
                        query += " t3.name order by t3.name"
                    if lines.groupby == 'startdate':
                        query += " t3.name order by t3.name"
                    if lines.groupby == 'create_date':
                        query += " t3.name order by t3.name"

                else:
                    query += " and t8.endo_id is not null group by  "
                    if lines.groupby == 'proposaldate':
                        query += " t3.name order by t3.name"
                    if lines.groupby == 'startdate':
                        query += " t3.name order by t3.name"
                    if lines.groupby == 'create_date':
                        query += " t3.name order by t3.name"
                cr.execute(query)
                usr_detail = cr.dictfetchall()

                return usr_detail

        # row = 11
        # index = 0
        # s_no = 1
        # total_polcount = 0
        # total_netprem = 0
        # total_grossprem = 0
        # total_tppremium = 0
        # total_suminsured = 0
        # total_servicetaxamt = 0
        # total_commssionamt = 0
        # total_brokerageprem = 0
        # total_sertaxamt = 0
        # for index, i in enumerate(temp,0):
        #     if i['netprem'] == None or i['netprem'] == False:
        #         totalnetprem = 0
        #     else:
        #         totalnetprem = i['netprem']
        #     if i['grossprem'] == None or i['grossprem'] == False:
        #         totalgrossprem = 0
        #     else:
        #         totalgrossprem = i['grossprem']
        #     if i['tppremium'] == None or i['tppremium'] == False:
        #         totaltppremium  = 0
        #     else:
        #         totaltppremium  = i['tppremium']
        #     if i['brokerageprem'] == None or i['brokerageprem'] == False:
        #         totalbrokerageprem = 0
        #     else:
        #         totalbrokerageprem = i['brokerageprem']
        #     if i['suminsured'] == None or i['suminsured'] == False:
        #         totalsuminsured = 0
        #     else:
        #         totalsuminsured = i['suminsured']
        #     if i['commssionamt'] == None or i['commssionamt'] == False:
        #         totalcommssionamt = 0
        #     else:
        #         totalcommssionamt = i['commssionamt']
        #     if i['servicetaxamt'] == None or i['servicetaxamt'] == False:
        #         totalservicetaxamt = 0
        #     else:
        #         totalservicetaxamt = i['servicetaxamt']
        #     if i['sertaxamt'] == None or i['sertaxamt'] == False:
        #         totalsertaxamt = 0
        #     else:
        #         totalsertaxamt = i['sertaxamt']
        #     total_polcount += i['total']
        #     total_netprem += totalnetprem
        #     total_grossprem += totalgrossprem
        #     total_tppremium += totaltppremium
        #     total_brokerageprem += totalbrokerageprem
        #     total_suminsured += totalsuminsured
        #     total_servicetaxamt += totalservicetaxamt
        #     total_commssionamt += totalcommssionamt
        #     total_sertaxamt += totalsertaxamt
        #     sheet.write(row, 0, index +1 , border1)
        #     sheet.write(row, 1, i['insurername'], border)
        #     sheet.write(row, 2, i['total'], border2)
        #     sheet.write(row, 3, totalsuminsured, numbersformat)
        #     sheet.write(row, 4, totalgrossprem, numbersformat)
        #     sheet.write(row, 5, totalservicetaxamt, numbersformat)
        #     sheet.write(row, 6, totalnetprem, numbersformat)
        #     sheet.write(row, 7, totalbrokerageprem, numbersformat)
        #     sheet.write(row, 8, totaltppremium, numbersformat)
        #     sheet.write(row, 9, totalcommssionamt, numbersformat)
        #     sheet.write(row, 10, totalsertaxamt, numbersformat)
        #
        #     row = row + 1
        # sheet.write(row, 2, total_polcount, bold1)
        # sheet.write(row, 3, total_suminsured, numbersformat1)
        # sheet.write(row, 4, total_grossprem, numbersformat1)
        # sheet.write(row, 5, total_servicetaxamt, numbersformat1)
        # sheet.write(row, 6, total_netprem, numbersformat1)
        # sheet.write(row, 7, total_brokerageprem, numbersformat1)
        # sheet.write(row, 8, total_tppremium, numbersformat1)
        # sheet.write(row, 9, total_commssionamt, numbersformat1)
        # sheet.write(row, 10, total_sertaxamt, numbersformat1)

BusinessSummary('report.clickbima.business_summary.xlsx', 'businesssummary.report')



