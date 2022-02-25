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


class Businessdetailreport(models.TransientModel):
    _name = "businessdetail.report"
    _description = "Business Detail Report"

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    monthly = fields.Selection([('monthly', 'Monthly'), ('quatar', 'Quarterly'), ('yearly', 'Yearly')],
                               default='monthly',string="Period Type")
    quarter = fields.Selection([('q1', 'Quarter 1'), ('q2', 'Quarter 2'), ('q3', 'Quarter 3'), ('q4', 'Quarter 4')],
                               string='Quarter')
    groupby = fields.Selection(
        [('create_date', 'Docket Date'), ('proposaldate', 'Proposal Date'), ('startdate', 'Start Date')],
        default='proposaldate', string="Group BY")
    location = fields.Selection([('9', 'Chandigarh'), ('8', 'Ludhiana'), ('7', 'New Delhi'), ('all', 'All')],
                                default='all', string="Location")
    filterby = fields.Selection([('insurername', 'Insurer Name'), ('insurerbranch', 'Insurer Branch'), ('all', 'All')],
                                default='all', string="Filter BY")
    fiscal_year = fields.Many2one('fyyear', string="Financial Year",
                                  default=lambda self: self.env['fyyear'].search([('ex_active', '=', True)],
                                                                                 limit=1).id)
    months = fields.Selection(
        [('01-01', 'January'), ('01-02', 'February'), ('01-03', 'March'), ('01-04', 'April'), ('01-05', 'May'),
         ('01-06', 'June'),
         ('01-07', 'July'), ('01-08', 'August'), ('01-09', 'September'), ('01-10', 'October'), ('01-11', 'November'),
         ('01-12', 'December')])
    insurer_name = fields.Many2one('res.partner', string="Insurer Name",
                                   domain=[('customer', '=', True), ('is_company', '=', True)])
    insurer_branch = fields.Many2one('insurerbranch', string="Insurer Branch")
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
        return self.env['report'].get_action(self, report_name='clickbima.business_detail.xlsx', data=data)


from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class BusinessDetail(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, lines):

        import odoo
        import datetime
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
            groupname = 'Created Date'
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

        import datetime
        x = datetime.datetime.now()

        # One sheet by partner
        report_name = "sheet 1"
        sheet = workbook.add_worksheet(report_name[:31])
        report_head = 'Security Insurance Brokers(India) Private Limited'
        report_head1 = str(loc)
        merge_format = workbook.add_format({'bold': 1, 'align': 'center', 'valign': 'vcenter', 'font_color': 'black'})
        merge_format1 = workbook.add_format({'bold': 1, 'align': 'left', 'valign': 'vleft', 'font_color': 'black'})
        bold = workbook.add_format({'border': 1, 'bold': True, 'align': 'left'})
        bold1 = workbook.add_format({'bold': True, 'border': 1, 'align': 'right'})
        bold2 = workbook.add_format({'bold': True, 'border': 1, 'align': 'center'})
        numbersformat = workbook.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'right'})
        bold3 = workbook.add_format({'bold': True, 'align': 'right'})
        border = workbook.add_format({'border': 1, 'align': 'center'})
        border2 = workbook.add_format({'border': 1, 'align': 'right'})
        border1 = workbook.add_format({'border': 1, 'align': 'left'})
        numbersformat1 = workbook.add_format({'num_format': '#,##0.00', 'bold': True, 'border': 1, 'align': 'right'})
        align_left = workbook.add_format({'align': 'left'})

        # report_head2 = 'Business Detail Report for the period of Proposal Start Date : ' + str(
        #     lines.date_from) + '  to End Date : ' + str(lines.date_to)
        report_head3 = 'Grouped By : ' + str(groupname) + '   Filter By : ' + str(filtname) + ' Start Date : ' + str(
            lines.date_from) + '  to End Date : ' + str(lines.date_to)
        # sheet.write(0, 10, ('Printed On  ' + str(x.strftime("%x"))), merge_format)
        # sheet.write(1, 0, ('New Delhi-Nehru Place'), merge_format1)
        sheet.write(2, 0, ('Business Report'), merge_format1)
        if lines.filterby == 'insurername':
            sheet.write(3, 0, str(lines.insurer_name.name), merge_format1)
        elif lines.filterby == 'insurerbranch':
            sheet.write(3, 0, str(lines.insurer_name) + ' , ' + str(lines.insurer_branch.name), merge_format1)

        # sheet.write(1, 10, ('Page:1'), bold3)
        # sheet.write(8, 0, ('Financial Year'), bold1)
        # sheet.write(8, 1, (lines.fiscal_year.name), bold)
        # sheet.write(8, 2, (' '), bold)
        # sheet.write(8, 3, ('Period Type'), bold1)
        # sheet.write(8, 4, (quat), bold)
        # sheet.write(9, 0, (' '), bold)
        # sheet.write(9, 1, (' '), bold)
        # sheet.write(9, 2, (' '), bold)
        # sheet.write(9, 3, (' '), bold)
        # sheet.write(9, 4, (' '), bold)
        # sheet.write(9, 5, (' '), bold)
        # sheet.write(9, 6, (' '), bold)
        # sheet.write(9, 7, (' '), bold)
        # sheet.write(9, 8, (' '), bold)
        # sheet.write(9, 9, (' '), bold)
        # sheet.write(9, 10, (' '), bold)
        sheet.write(7, 0, ('Sr. No.'), bold1)
        sheet.write(7, 1, ('Docket No.'), bold2)
        sheet.write(7, 2, ('Proposal Date'), bold2)
        sheet.write(7, 3, ('Policy Status'), bold)
        sheet.write(7, 4, ('Scheme'), bold)
        sheet.write(7, 5, ('Policy No'), bold1)
        sheet.write(7, 6, ('Ends No'), bold1)
        sheet.write(7, 7, ('Policy Date'), bold2)
        sheet.write(7, 8, ('Start Date'), bold2)
        sheet.write(7, 9, ('Expiry Date'), bold2)
        sheet.write(7, 10, ('Insured Name'), bold)
        sheet.write(7, 11, ('Insurer Name / Branch Name'), bold)
        sheet.write(7, 12, ('Sum Insured'), bold1)
        sheet.write(7, 13, ('Share(%)'), bold1)
        sheet.write(7, 14, ('Brkg Prem'), bold1)
        sheet.write(7, 15, ('Other Prem'), bold1)
        sheet.write(7, 16, ('Net Premium'), bold1)
        sheet.write(7, 17, ('GST Amt'), bold1)
        sheet.write(7, 18, ('Gross Prem'), bold1)
        sheet.write(7, 19, ('Brkg(%)'), bold1)
        sheet.write(7, 20, ('Brkg Amnt'), bold1)

        # increasing width of column
        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 36)
        sheet.set_column('F:F', 25)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 15)
        sheet.set_column('K:K', 30)
        sheet.set_column('L:L', 70)
        sheet.set_column('M:M', 20)
        sheet.set_column('N:N', 15)
        sheet.set_column('O:O', 15)
        sheet.set_column('P:P', 15)
        sheet.set_column('Q:Q', 15)
        sheet.set_column('R:R', 15)
        sheet.set_column('S:S', 15)
        sheet.set_column('T:T', 10)
        sheet.set_column('U:U', 15)
        sheet.merge_range('A1:D1', report_head, merge_format1)
        sheet.merge_range('A5:S5', report_head3, merge_format)
        sheet.merge_range('A2:C2', report_head1, merge_format1)

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
        row = 8
        index = 1
        s_no = 1
        if lines.groupby == 'create_date':
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            temp = []
            totalsuminsuredcount = 0
            totalgrosspremcount = 0
            totalbrokpremcount = 0
            totalcommcount = 0
            totalnetprems = 0
            totalservicetxtcount = 0
            totalotherscount = 0

            an_iterator12 = sorted(usr_detail, key=operator.itemgetter('docketdate'))
            new_lst = itertools.groupby(an_iterator12, key=operator.itemgetter('docketdate'))
            for key, group in new_lst:

                key_and_group = {key: list(group)}
                for i in key_and_group.iteritems():
                    # sheet.write(row, 0, i[0], border2)
                    row += 1
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
                    totalservicetxtamts=0
                    totalothersprems=0
                    for res in i[1]:
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
                        # brokeragepercent = round(((totalcomm / totalnetprem) * 100), 2)
                        sheet.write(row, 0, index, border2)
                        sheet.write(row, 1, res['docketno'], border)
                        sheet.write(row, 2, res['proposaldate'], border)
                        sheet.write(row, 3, res['policystatus'], border1)
                        sheet.write(row, 4, res['subcategory'], border1)
                        sheet.write(row, 5, res['policyno'], border2)
                        sheet.write(row, 6, res['endos_no'], border2)
                        sheet.write(row, 7, res['docketdate'], border)
                        sheet.write(row, 8, res['startdate'], border)
                        sheet.write(row, 9, res['enddate'], border)
                        sheet.write(row, 10, res['insuredname'], border1)
                        sheet.write(row, 11, res['insurername'] + '/' + res['insurerbranch'], border1)
                        sheet.write(row, 12, suminsur_null, numbersformat)
                        sheet.write(row, 13, res['co_share'], border2)
                        sheet.write(row, 14, brokprem_null, numbersformat)
                        sheet.write(row, 15, (res['tp'] + res['tr'] + res['ts']), numbersformat)
                        sheet.write(row, 16, netprem_null, numbersformat)
                        sheet.write(row, 17, sertaxamt_null, numbersformat)
                        sheet.write(row, 18, gross_null, numbersformat)
                        sheet.write(row, 19, res['rate'], numbersformat)
                        sheet.write(row, 20, comm_null, numbersformat)
                        row = row + 1
                        s_no = s_no + 1
                        index = index + 1
                    sheet.write(row, 11, ('Created Date Total ') + str(i[0]), bold2)
                    sheet.write(row, 12, totalsuminsured, numbersformat1)
                    sheet.write(row, 13, (' '), bold1)
                    sheet.write(row, 14, totalbrokprem, numbersformat1)
                    sheet.write(row, 15, totalothersprems, numbersformat1)
                    sheet.write(row, 16, totalnetprem, numbersformat1)
                    sheet.write(row, 17, totalservicetxtamts, numbersformat1)
                    sheet.write(row, 18, totalgrossprem, numbersformat1)
                    sheet.write(row, 19, (' '), bold1)
                    sheet.write(row, 20, totalcomm, numbersformat1)
                    row += 1

                    totalsuminsuredcount += totalsuminsured
                    totalgrosspremcount += totalgrossprem
                    totalbrokpremcount += totalbrokprem
                    totalcommcount += totalcomm
                    totalservicetxtcount += totalservicetxtamts
                    totalotherscount += totalothersprems
                    totalnetprems += totalnetprem

            sheet.write(row, 11, str(' Total'), bold2)
            sheet.write(row, 12, totalsuminsuredcount, numbersformat1)
            sheet.write(row, 13, (' '), bold1)
            sheet.write(row, 14, totalbrokpremcount, numbersformat1)
            sheet.write(row, 15, totalotherscount, numbersformat1)
            sheet.write(row, 16, totalnetprems, numbersformat1)
            sheet.write(row, 17, totalservicetxtcount, numbersformat1)
            sheet.write(row, 18, totalgrosspremcount, numbersformat1)
            sheet.write(row, 19, (' '), bold1)
            sheet.write(row, 20, totalcommcount, numbersformat1)
            row += 1
            print("Report Printed")

        elif lines.groupby == 'proposaldate':
            temp = []
            totalsuminsuredcount = 0
            totalgrosspremcount = 0
            totalbrokpremcount = 0
            totalcommcount = 0
            totalnetprems = 0
            totalservicetxtcount = 0
            totalotherscount = 0

            an_iterator12 = sorted(usr_detail, key=operator.itemgetter('proposaldate'))
            new_lst = itertools.groupby(an_iterator12, key=operator.itemgetter('proposaldate'))
            for key, group in new_lst:

                key_and_group = {key: list(group)}
                for i in key_and_group.iteritems():
                    # sheet.write(row, 0, i[0], border2)
                    row += 1
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
                    totalservicetxtamts=0
                    totalothersprems=0
                    for res in i[1]:
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
                        # brokeragepercent = round(((totalcomm / totalnetprem) * 100), 2)
                        sheet.write(row, 0, index, border2)
                        sheet.write(row, 1, res['docketno'], border)
                        sheet.write(row, 2, res['proposaldate'], border)
                        sheet.write(row, 3, res['policystatus'], border1)
                        sheet.write(row, 4, res['subcategory'], border1)
                        sheet.write(row, 5, res['policyno'], border2)
                        sheet.write(row, 6, res['endos_no'], border2)
                        sheet.write(row, 7, res['docketdate'], border)
                        sheet.write(row, 8, res['startdate'], border)
                        sheet.write(row, 9, res['enddate'], border)
                        sheet.write(row, 10, res['insuredname'], border1)
                        sheet.write(row, 11, res['insurername'] + '/' + res['insurerbranch'], border1)
                        sheet.write(row, 12, suminsur_null, numbersformat)
                        sheet.write(row, 13, res['co_share'], border2)
                        sheet.write(row, 14, brokprem_null, numbersformat)
                        sheet.write(row, 15, (res['tp'] + res['tr'] + res['ts']), numbersformat)
                        sheet.write(row, 16, netprem_null, numbersformat)
                        sheet.write(row, 17, sertaxamt_null, numbersformat)
                        sheet.write(row, 18, gross_null, numbersformat)
                        sheet.write(row, 19, res['rate'], numbersformat)
                        sheet.write(row, 20, comm_null, numbersformat)
                        row = row + 1
                        s_no = s_no + 1
                        index = index + 1
                    sheet.write(row, 11, ('Proposal Date Total ') + str(i[0]), bold2)
                    sheet.write(row, 12, totalsuminsured, numbersformat1)
                    sheet.write(row, 13, (' '), bold1)
                    sheet.write(row, 14, totalbrokprem, numbersformat1)
                    sheet.write(row, 15, totalothersprems, numbersformat1)
                    sheet.write(row, 16, totalnetprem, numbersformat1)
                    sheet.write(row, 17, totalservicetxtamts, numbersformat1)
                    sheet.write(row, 18, totalgrossprem, numbersformat1)
                    sheet.write(row, 19, (' '), bold1)
                    sheet.write(row, 20, totalcomm, numbersformat1)
                    row += 1

                    totalsuminsuredcount += totalsuminsured
                    totalgrosspremcount += totalgrossprem
                    totalbrokpremcount += totalbrokprem
                    totalcommcount += totalcomm
                    totalservicetxtcount += totalservicetxtamts
                    totalotherscount += totalothersprems
                    totalnetprems += totalnetprem

            sheet.write(row, 11, str(' Total'), bold2)
            sheet.write(row, 12, totalsuminsuredcount, numbersformat1)
            sheet.write(row, 13, (' '), bold1)
            sheet.write(row, 14, totalbrokpremcount, numbersformat1)
            sheet.write(row, 15, totalotherscount, numbersformat1)
            sheet.write(row, 16, totalnetprems, numbersformat1)
            sheet.write(row, 17, totalservicetxtcount, numbersformat1)
            sheet.write(row, 18, totalgrosspremcount, numbersformat1)
            sheet.write(row, 19, (' '), bold1)
            sheet.write(row, 20, totalcommcount, numbersformat1)
            row += 1
            print("Report Printed")

        elif lines.groupby == 'startdate':
            temp = []
            totalsuminsuredcount = 0
            totalgrosspremcount = 0
            totalbrokpremcount = 0
            totalcommcount = 0
            totalnetprems = 0
            totalservicetxtcount = 0
            totalotherscount = 0

            an_iterator12 = sorted(usr_detail, key=operator.itemgetter('startdate'))
            new_lst = itertools.groupby(an_iterator12, key=operator.itemgetter('startdate'))
            for key, group in new_lst:

                key_and_group = {key: list(group)}
                for i in key_and_group.iteritems():
                    # sheet.write(row, 0, i[0], border2)
                    row += 1
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
                    totalservicetxtamts=0
                    totalothersprems=0
                    for res in i[1]:
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
                        # brokeragepercent = round(((totalcomm / totalnetprem) * 100), 2)
                        sheet.write(row, 0, index, border2)
                        sheet.write(row, 1, res['docketno'], border)
                        sheet.write(row, 2, res['proposaldate'], border)
                        sheet.write(row, 3, res['policystatus'], border1)
                        sheet.write(row, 4, res['subcategory'], border1)
                        sheet.write(row, 5, res['policyno'], border2)
                        sheet.write(row, 6, res['endos_no'], border2)
                        sheet.write(row, 7, res['docketdate'], border)
                        sheet.write(row, 8, res['startdate'], border)
                        sheet.write(row, 9, res['enddate'], border)
                        sheet.write(row, 10, res['insuredname'], border1)
                        sheet.write(row, 11, res['insurername'] + '/' + res['insurerbranch'], border1)
                        sheet.write(row, 12, suminsur_null, numbersformat)
                        sheet.write(row, 13, res['co_share'], border2)
                        sheet.write(row, 14, brokprem_null, numbersformat)
                        sheet.write(row, 15, (res['tp'] + res['tr'] + res['ts']), numbersformat)
                        sheet.write(row, 16, netprem_null, numbersformat)
                        sheet.write(row, 17, sertaxamt_null, numbersformat)
                        sheet.write(row, 18, gross_null, numbersformat)
                        sheet.write(row, 19, res['rate'], numbersformat)
                        sheet.write(row, 20, comm_null, numbersformat)
                        row = row + 1
                        s_no = s_no + 1
                        index = index + 1
                    sheet.write(row, 11, ('Start Date Total ') + str(i[0]), bold2)
                    sheet.write(row, 12, totalsuminsured, numbersformat1)
                    sheet.write(row, 13, (' '), bold1)
                    sheet.write(row, 14, totalbrokprem, numbersformat1)
                    sheet.write(row, 15, totalothersprems, numbersformat1)
                    sheet.write(row, 16, totalnetprem, numbersformat1)
                    sheet.write(row, 17, totalservicetxtamts, numbersformat1)
                    sheet.write(row, 18, totalgrossprem, numbersformat1)
                    sheet.write(row, 19, (' '), bold1)
                    sheet.write(row, 20, totalcomm, numbersformat1)
                    row += 1

                    totalsuminsuredcount += totalsuminsured
                    totalgrosspremcount += totalgrossprem
                    totalbrokpremcount += totalbrokprem
                    totalcommcount += totalcomm
                    totalservicetxtcount += totalservicetxtamts
                    totalotherscount += totalothersprems
                    totalnetprems += totalnetprem
            #
            sheet.write(row, 11, str(' Total'), bold2)
            sheet.write(row, 12, totalsuminsuredcount, numbersformat1)
            sheet.write(row, 13, (' '), bold1)
            sheet.write(row, 14, totalbrokpremcount, numbersformat1)
            sheet.write(row, 15, totalotherscount, numbersformat1)
            sheet.write(row, 16, totalnetprems, numbersformat1)
            sheet.write(row, 17, totalservicetxtcount, numbersformat1)
            sheet.write(row, 18, totalgrosspremcount, numbersformat1)
            sheet.write(row, 19, (' '), bold1)
            sheet.write(row, 20, totalcommcount, numbersformat1)
            row += 1
            print("Report Printed")


        else:
            temp = []
            totalsuminsuredcount = 0
            totalgrosspremcount = 0
            totalbrokpremcount = 0
            totalcommcount = 0
            totalnetprems = 0
            totalservicetxtcount = 0
            totalotherscount = 0
            an_iterator12 = sorted(usr_detail, key=operator.itemgetter('docketdate'))
            new_lst = itertools.groupby(an_iterator12, key=operator.itemgetter('docketdate'))
            for key, group in new_lst:

                key_and_group = {key: list(group)}
                for i in key_and_group.iteritems():
                    # sheet.write(row, 0, i[0], border2)
                    row += 1
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
                    totalservicetxtamts=0
                    totalothersprems=0
                    for res in i[1]:
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
                        # brokeragepercent = round(((totalcomm / totalnetprem) * 100), 2)
                        sheet.write(row, 0, index, border2)
                        sheet.write(row, 1, res['docketno'], border)
                        sheet.write(row, 2, res['proposaldate'], border)
                        sheet.write(row, 3, res['policystatus'], border1)
                        sheet.write(row, 4, res['subcategory'], border1)
                        sheet.write(row, 5, res['policyno'], border2)
                        sheet.write(row, 6, res['endos_no'], border2)
                        sheet.write(row, 7, res['docketdate'], border)
                        sheet.write(row, 8, res['startdate'], border)
                        sheet.write(row, 9, res['enddate'], border)
                        sheet.write(row, 10, res['insuredname'], border1)
                        sheet.write(row, 11, res['insurername'] + '/' + res['insurerbranch'], border1)
                        sheet.write(row, 12, suminsur_null, numbersformat)
                        sheet.write(row, 13, res['co_share'], border2)
                        sheet.write(row, 14, brokprem_null, numbersformat)
                        sheet.write(row, 15, (res['tp'] + res['tr'] + res['ts']), numbersformat)
                        sheet.write(row, 16, netprem_null, numbersformat)
                        sheet.write(row, 17, sertaxamt_null, numbersformat)
                        sheet.write(row, 18, gross_null, numbersformat)
                        sheet.write(row, 19, res['rate'], numbersformat)
                        sheet.write(row, 20, comm_null, numbersformat)
                        row = row + 1
                        s_no = s_no + 1
                        index = index + 1
                    sheet.write(row, 11, ('Created Date Total ') + i[0], bold2)
                    sheet.write(row, 12, totalsuminsured, numbersformat1)
                    sheet.write(row, 13, (' '), bold1)
                    sheet.write(row, 14, totalbrokprem, numbersformat1)
                    sheet.write(row, 15, totalothersprems, numbersformat1)
                    sheet.write(row, 16, totalnetprem, numbersformat1)
                    sheet.write(row, 17, totalservicetxtamts, numbersformat1)
                    sheet.write(row, 18, totalgrossprem, numbersformat1)
                    sheet.write(row, 19, (' '), bold1)
                    sheet.write(row, 20, totalcomm, numbersformat1)
                    row += 1

                    totalsuminsuredcount += totalsuminsured
                    totalgrosspremcount += totalgrossprem
                    totalbrokpremcount += totalbrokprem
                    totalcommcount += totalcomm
                    totalservicetxtcount += totalservicetxtamts
                    totalotherscount += totalothersprems
                    totalnetprems += totalnetprem

            sheet.write(row, 11, str(' Total'), bold2)
            sheet.write(row, 12, totalsuminsuredcount, numbersformat1)
            sheet.write(row, 13, (' '), bold1)
            sheet.write(row, 14, totalbrokpremcount, numbersformat1)
            sheet.write(row, 15, totalotherscount, numbersformat1)
            sheet.write(row, 16, totalnetprems, numbersformat1)
            sheet.write(row, 17, totalservicetxtcount, numbersformat1)
            sheet.write(row, 18, totalgrosspremcount, numbersformat1)
            sheet.write(row, 19, (' '), bold1)
            sheet.write(row, 20, totalcommcount, numbersformat1)
            row += 1
            print("Report Printed")


    def querys(self, workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1, end_year, id=None,
               endo=None):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        with registry.cursor() as cr:
            query = "select case when t8.co_insurer_id is not null then t8.co_share else 100 end as co_share," \
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

            # query = " select case when 'self'=t8.co_type then t8.co_share else 100 end as co_share,"\
            #         " case when 'self'=t8.co_type then t9.name  else  t3.name end as insurername," \
            #         " case when 'self'=t8.co_type then t10.name else t2.name end as insurerbranch," \
            #         " case when 'self'=t8.co_type then t4.name  else t4.name  end as insuredname," \
            #         " case when 'self'=t8.co_type then t1.name  else t1.name end as docketno," \
            #         " case when 'self'=t8.co_type then t11.name  else t11.name end as policystatus," \
            #         " case when 'self'=t8.co_type then t6.name  else t6.name end as endos_no," \
            #         " case when 'self'=t8.co_type then t7.name  else t7.name end as subcategory," \
            #         " case when 'self'=t8.co_type then t1.policyno  else t1.policyno end as policyno," \
            #         " case when 'self'=t8.co_type then t1.date2  else t1.date2 end as docketdate," \
            #         " case when 'self'=t8.co_type then t1.proposaldate  else t1.proposaldate end as proposaldate," \
            #         " case when 'self'=t8.co_type then t1.startfrom  else t1.startfrom end as startdate," \
            #         " case when 'self'=t8.co_type then t1.expiry  else t1.expiry end as enddate," \
            #         " case when (t6.endo_id is not null and t8.co_insurer_id is null) then sum(t6.endo_net)" \
            #         " else case when(t8.co_insurer_id is not null and t6.endo_id is null) then sum(t8.co_net_premium)" \
            #         " else case when(t8.co_insurer_id is null and t6.endo_id is null) then sum(t1.netprem)" \
            #         " else case when(t8.co_insurer_id is not null and t6.endo_id is not null) then sum(t6.endo_net + t8.co_net_premium)" \
            #         " end end end end as netprem," \
            #         " case when(t6.endo_id is not null and t8.co_insurer_id is null) then sum(t6.endo_gst_gross)" \
            #         " else case when(t8.co_insurer_id is not null and t6.endo_id is null) then sum(t8.co_net_gross_pre)" \
            #         " else case when(t8.co_insurer_id is null and t6.endo_id is null) then sum(t1.grossprem)" \
            #         " else case when(t8.co_insurer_id is not null and t6.endo_id is not null) then sum(t6.endo_gst_gross + t8.co_net_gross_pre)" \
            #         " end end end end  as grossprem," \
            #         " case when(t6.endo_id is not null and t8.co_insurer_id is null) then sum(t6.endos_suminsured)" \
            #         " else case when(t8.co_insurer_id is not null and t6.endo_id is null) then sum(t8.co_sum_insured)" \
            #         " else case when(t8.co_insurer_id is null and t6.endo_id is null) then sum(t1.suminsured)" \
            #         " else case when(t8.co_insurer_id is not null and t6.endo_id is not null) then sum(t6.endos_suminsured + t8.co_sum_insured)" \
            #         " end end end end  as suminsured," \
            #         " case when(t6.endo_id is not null and t8.co_insurer_id is null) then sum(t6.endos_brokerage_premium)" \
            #         " else case when(t8.co_insurer_id is not null and t6.endo_id is null) then sum(t8.co_brokerage_pre)" \
            #         " else case when(t8.co_insurer_id is null and t6.endo_id is null) then sum(t1.brokerageprem)" \
            #         " else case when(t8.co_insurer_id is not null and t6.endo_id is not null) then sum(t6.endos_brokerage_premium + t8.co_brokerage_pre)" \
            #         " end end end end  as brokerageprem," \
            #         " case when(t6.endo_id is not null and t8.co_insurer_id is null) then sum(t6.endo_commission)" \
            #         " else case when(t8.co_insurer_id is not null and t6.endo_id is null) then sum(t8.co_commission_amount)" \
            #         " else case when(t8.co_insurer_id is null and t6.endo_id is null) then sum(t1.commssionamt)" \
            #         " else case when(t8.co_insurer_id is not null and t6.endo_id is not null) then sum(t6.endo_commission + t8.co_commission_amount)" \
            #         " end end end end  as commssionamt," \
            #         " case when(t6.endo_id is not null and t8.co_insurer_id is null) then sum(t6.endo_gst_amount)" \
            #         " else case when(t8.co_insurer_id is not null and t6.endo_id is null) then 0" \
            #         " else case when(t8.co_insurer_id is null and t6.endo_id is null) then sum(t1.servicetaxamt)" \
            #         " else case when(t8.co_insurer_id is not null and t6.endo_id is not null) then sum(t6.endo_gst_amount)" \
            #         " end end end end  as servicetaxamt" \
            #         " from policytransaction as t1 left join insurerbranch as t2 on t2.id = t1.insurerbranch" \
            #         " left join res_partner as t3 on t3.id=t1.insurername123" \
            #         " left join res_partner as t4 on t4.id=t1.clientname" \
            #         " left join subdata_subdata as t5 on t5.id=t1.type" \
            #         " left join endos_policy as t6 on t6.endo_id=t1.id" \
            #         " left join product_product as t16 on t16.id=t1.product_id" \
            #         " left join product_template as t7 on t16.product_tmpl_id =t7.id" \
            #         " left join co_insurer_policy as t8 on t8.co_insurer_id=t1.id AND t8.co_type='self'" \
            #         " left join res_partner as t9 on t9.id=t8.co_insurer_name left join insurerbranch as t10 on t10.id=t8.co_insurer_branch"\
            #         " left join subdata_subdata as t11 on t11.id=t1.type"

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
                        lines.fiscal_year.date_end) + "' "
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
                    query += " and t1.location = '" + str(lines.location) + "' AND (t3.name = '" + str(lines.insurer_name.name) + "' or t9.name = '" + str(
                    lines.insurer_name.name) + "')" \
                                               " group by t8.co_insurer_id,t1.id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                               " t1.proposaldate,t8.co_share,t8.co_type,t2.name,t3.name,t9.name,t10.name,t4.name,t1.name," \
                                               " t5.name,t4.name,t7.name,t1.tppremium,t1.terrprem,t1.stamprem,t1.rate"
                else:
                    query += "  AND (t3.name = '" + str(lines.insurer_name.name) + "' or t9.name = '" + str(
                        lines.insurer_name.name) + "')" \
                                                   " group by t8.co_insurer_id,t1.id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
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
                    query += " and t1.location = '" + str(lines.location) + "' AND (t3.name = '" + str(lines.insurer_name.name) + "' or t9.name = '" + str(
                        lines.insurer_name.name) + "') AND (t2.name = '" + str(lines.insurer_branch.name) + "'" \
                                                                                                            "or t10.name = '" + str(
                        lines.insurer_branch.name) + "') group by t8.co_insurer_id,t1.id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                                     " t1.proposaldate,t8.co_share,t8.co_type,t2.name,t3.name,t9.name,t10.name,t4.name,t1.name," \
                                                     " t5.name,t4.name,t7.name,t1.tppremium , t1.terrprem , t1.stamprem,t1.rate"
                else:
                    query += " AND (t3.name = '" + str(lines.insurer_name.name) + "' or t9.name = '" + str(
                        lines.insurer_name.name) + "') AND (t2.name = '" + str(lines.insurer_branch.name) + "'" \
                                                                                                            "or t10.name = '" + str(
                        lines.insurer_branch.name) + "') group by t8.co_insurer_id,t1.id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                                     " t1.proposaldate,t8.co_share,t8.co_type,t2.name,t3.name,t9.name,t10.name,t4.name,t1.name," \
                                                     " t5.name,t4.name,t7.name,t1.tppremium , t1.terrprem , t1.stamprem,t1.rate"

                cr.execute(query)
                usr_detail = cr.dictfetchall()

                return usr_detail
            else:

                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                        lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' "
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
                            dec_end) + "' "
                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                        lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "' "




                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "' group by t8.co_insurer_id,t1.id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                             " t1.proposaldate,t8.co_share,t8.co_type,t2.name,t3.name,t9.name,t10.name,t4.name,t1.name," \
                             " t5.name,t4.name,t7.name,t1.tppremium , t1.terrprem , t1.stamprem,t1.rate"
                else:
                    query += " group by t8.co_insurer_id,t1.id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                             " t1.proposaldate,t8.co_share,t8.co_type,t2.name,t3.name,t9.name,t10.name,t4.name,t1.name," \
                             " t5.name,t4.name,t7.name,t1.tppremium , t1.terrprem , t1.stamprem,t1.rate"

                cr.execute(query)
                usr_detail = cr.dictfetchall()

                return usr_detail

    def endos(self, workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1, end_year, id=None,
              endo=None):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        with registry.cursor() as cr:
            query = " select '' as co_share,t3.name as insurername,t2.name as insurerbranch,t4.name as insuredname,t1.name as docketno," \
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
                        lines.fiscal_year.date_end) + "' "
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
                    query += " where t8.endos_date BETWEEN '" + str(
                        lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "' "



                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "' AND t3.name = '" + str(lines.insurer_name.name) + "' " \
                                                                                  " and t8.endo_id is not null group by t8.name,t8.endo_id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                                                                  " t1.proposaldate,t2.name,t3.name,t4.name,t1.name,t5.name,t4.name,t7.name,t8.endo_tp,t8.endo_terr,t8.endo_stamp,t8.endos_manual,t1.rate "

                else:
                    query += "  AND t3.name = '" + str(lines.insurer_name.name) + "' " \
                                                                                  " and t8.endo_id is not null group by t8.name,t8.endo_id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                                                                  " t1.proposaldate,t2.name,t3.name,t4.name,t1.name,t5.name,t4.name,t7.name,t8.endo_tp,t8.endo_terr,t8.endo_stamp,t8.endos_manual,t1.rate "

                cr.execute(query)
                usr_detail = cr.dictfetchall()

                return usr_detail



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
                        query += " where " + str(dy_date) + "  BETWEEN '" + str(sep_start) + "' AND '" + str(
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
                    query += " and t1.location = '" + str(lines.location) + "' AND t3.name = '" + str(lines.insurer_name.name) + "'  AND t2.name = '" + str(
                    lines.insurer_branch.name) + "'and t8.endo_id is not null group by t8.name,t8.endo_id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                                 " t1.proposaldate,t2.name,t3.name,t4.name,t1.name,t5.name,t4.name,t7.name,t8.endo_tp,t8.endo_terr,t8.endo_stamp,t1.rate,t8.endos_manual"
                else:
                    query += " AND t3.name = '" + str(lines.insurer_name.name) + "'  AND t2.name = '" + str(
                        lines.insurer_branch.name) + "' and t8.endo_id is not null group by t8.name,t8.endo_id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom," \
                                                     " t1.proposaldate,t2.name,t3.name,t4.name,t1.name,t5.name,t4.name,t7.name,t8.endo_tp,t8.endo_terr,t8.endo_stamp,t1.rate,t8.endos_manual"

                cr.execute(query)
                usr_detail = cr.dictfetchall()

                return usr_detail
            else:

                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t8.endos_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' "
                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)
                        query += " where t8.endos_date  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "'"
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
                        query += " where t8.endos_date BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "' "
                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t8.endos_date BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "' "
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
                    query += " where t8.endos_date  BETWEEN '" + str(
                        lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "' "

                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "' and t8.endo_id is not null group by t8.name,t8.endo_id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom,t1.proposaldate,t2.name,t3.name," \
                         "  t4.name,t1.name,t5.name,t4.name,t7.name,t8.endo_tp,t8.endo_terr,t8.endo_stamp,t1.rate,t8.endos_manual "
                else:
                    query += " and t8.endo_id is not null group by t8.name,t8.endo_id,t1.policyno,t11.name,t1.date2,t1.expiry,t1.startfrom,t1.proposaldate,t2.name,t3.name," \
                             " t4.name,t1.name,t5.name,t4.name,t7.name,t8.endo_tp,t8.endo_terr,t8.endo_stamp,t1.rate,t8.endos_manual "

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                return usr_detail


BusinessDetail('report.clickbima.business_detail.xlsx', 'businessdetail.report')



