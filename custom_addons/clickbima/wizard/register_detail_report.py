from odoo import api, fields, models, _
import odoo
from odoo.http import request, content_disposition
from odoo.service import model
# from odoo.tools.misc import xlwt
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
import xlwt
# from pandas.tests.groupby.conftest import ts
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, StringIO, cStringIO


class Registerdetailreport(models.TransientModel):
    _name = "registerdetail.report"
    _description = "Register Detail Report"

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    monthly = fields.Selection([('monthly', 'Monthly'), ('quatar', 'Quarterly'), ('yearly', 'Yearly')],
                               default='monthly',string="Period Type")
    quarter = fields.Selection([('q1', 'Quarter 1'), ('q2', 'Quarter 2'), ('q3', 'Quarter 3'), ('q4', 'Quarter 4')],
                               string='Quarter')
    groupby = fields.Selection([('create_date', 'Docket Date'), ('proposaldate', 'Proposal Date'),('startdate', 'Start Date')], default='create_date',
                               string="Group BY")
    filterby = fields.Selection([('registername', 'Register Name'),('all','All')],default='all', string="Filter BY")
    location = fields.Selection([('9', 'Chandigarh'),('8','Ludhiana'),('7','New Delhi'),('all','All')],default='all', string="Location")
    fiscal_year = fields.Many2one('fyyear', string="Financial Year",
                                  default=lambda self: self.env['fyyear'].search([('ex_active', '=', True)],limit=1).id)
    months = fields.Selection(
        [('01-01', 'January'), ('01-02', 'February'), ('01-03', 'March'), ('01-04', 'April'), ('01-05', 'May'),('01-06', 'June'),
         ('01-07', 'July'), ('01-08', 'August'), ('01-09', 'September'), ('01-10', 'October'), ('01-11', 'November'),
         ('01-12', 'December')])
    policy_status = fields.Many2one('subdata.subdata', string="Policy Status")
    payment_type = fields.Many2one('subdata.subdata', string="Payment Type")
    referred_by = fields.Char(string="Referred By")
    sales_person = fields.Many2one('res.users', string="Sales Person")
    medium = fields.Many2one('utm.medium', string="Medium")
    source = fields.Many2one('utm.source', string="Source")
    register_name = fields.Many2one('subdata.subdata', string="Register Name")
    start_year = fields.Char()
    end_year = fields.Char()



    @api.multi
    @api.onchange('filterby')
    def _compute_info_name_mode(self):
        if self.filterby == "paymenttype":
            res = {}
            locations = self.env['infodata'].search([('name', '=', 17)])
            temp = []
            for i in locations:
                temp.append(i.infosubdata.id)
            res['domain'] = ({'payment_type': [('id', 'in', temp)]})
            return res
        elif self.filterby == "policystatus":
            res11 = {}
            locations1 = self.env['infodata'].search([('name', '=', 27)])
            temp1 = []
            for i in locations1:
                temp1.append(i.infosubdata.id)
            res11['domain'] = ({'policy_status': [('id', 'in', temp1)]})
            return res11
        elif self.filterby == "registername":
            res12 = {}
            locations2 = self.env['infodata'].search([('name', '=', 57)])
            temp = []

            for i in locations2:
                temp.append(i.infosubdata.name)
            res12['domain'] = ({'register_name': [('name', 'in', temp)]})
            return res12


    import datetime
    now1 = datetime.datetime.now()

    @api.onchange('monthly', 'months', 'fiscal_year')
    def onchange_monthly(self):
        import odoo
        import datetime
        if self.monthly and self.fiscal_year:
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
        return self.env['report'].get_action(self, report_name='clickbima.res_partner.xlsx', data=data)


from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
class PartnerXlsx(ReportXlsx):
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





            report_name = "sheet 1"
            report_head = 'Security Insurance Brokers (India) Private Limited'
            # report_head1 = 'New Delhi - Nehru Place'
            report_head2 = 'Register Details for the period of Created Start Date : ' + str(
                lines.date_from) + '  to End Date : ' + str(lines.date_to)

            filtname = ''
            if lines.filterby == 'medium':
                filtname = 'Medium'
            elif lines.filterby == 'salesperson':
                filtname = 'Sales Person'
            elif lines.filterby == 'paymenttype':
                filtname = 'Payment Type'
            elif lines.filterby == 'referredby':
                filtname = 'Referred By'
            elif lines.filterby == 'source':
                filtname = 'Source'
            elif lines.filterby == 'policystatus':
                filtname = 'Policy Status'
            elif lines.filterby == 'registername':
                filtname = 'Register Name'
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

            regis_name = ''
            if lines.filterby == 'registername':
                regis_name = lines.register_name.name
            else:
                regis_name = 'All'
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
            sheet = workbook.add_worksheet(report_name[:31])

            merge_format = workbook.add_format(
                {'bold': 1, 'align': 'center', 'valign': 'vcenter', 'font_color': 'black'})
            merge_format1 = workbook.add_format(
                {'bold': 1, 'align': 'left', 'valign': 'vleft', 'font_color': 'black'})
            bold = workbook.add_format({'border': 1, 'bold': True, 'align': 'left'})
            bold1 = workbook.add_format({'bold': True, 'border': 1, 'align': 'right'})
            bold2 = workbook.add_format({'bold': True, 'border': 1, 'align': 'center'})
            bold3 = workbook.add_format({'bold': True, 'align': 'right'})
            borderdate = workbook.add_format({'border': 1, 'align': 'center'})
            numbersformat = workbook.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'right'})
            numbersformat1 = workbook.add_format(
                {'num_format': '#,##0.00', 'bold': True, 'border': 1, 'align': 'right'})
            bordernum = workbook.add_format({'border': 1, 'align': 'right'})
            borderalpha = workbook.add_format({'border': 1, 'align': 'left'})
            align_left = workbook.add_format({'align': 'left'})

            # sheet.write(5, 6, ('Start Date : ' + str(lines.date_from) + '  to End Date : ' + str(lines.date_to)),
            #             bold1)
            report_head3 = 'Grouped By : ' + str(groupname) + '   Filtered By : ' + str(filtname)
            report_head4 = 'Printed On  ' + str(x.strftime("%x"))
            report_head5 = str(loc)
            # sheet.write(0, 17, ('Printed On  ' + str(x.strftime("%x"))), bold3)
            # sheet.write(1, 0, ('New Delhi-Nehru Place'), merge_format1)
            sheet.write(1, 18, ('Page:1'), bold3)
            # sheet.write(8, 0, ('Financial Year'), bold1)
            sheet.write(5, 1, (regis_name), borderalpha)
            # sheet.write(8, 2, (' '), bold)
            # sheet.write(8, 3, ('Period Type'), bold1)
            # sheet.write(8, 4, (quat), bold)
            sheet.write(5, 0, ('Register Name'), bold2)
            sheet.write(6, 0, ('No./Sr.No.'), bold2)
            sheet.write(6, 1, ('Pipeline/RFQ No.'), bold2)
            # sheet.write(6, 2, ('Quotation/Proposal No.'), bold)
            sheet.write(6, 2, ('Proposal Date'), bold2)
            sheet.write(6, 3, ('Docket No.'), bold2)
            sheet.write(6, 4, ('Policy Status'), bold)
            sheet.write(6, 5, ('Sub Category'), bold)
            sheet.write(6, 6, ('Insured Name'), bold)
            sheet.write(6, 7, ('Insurer Name/Branch Name'), bold)
            # sheet.write(6, 9, ('Branch Name'), bold)
            sheet.write(6, 8, ('Payment Type/No'), bold)
            sheet.write(6, 9, ('Co-Share'), bold1)
            sheet.write(6, 10, ('Sum Insured'), bold1)
            sheet.write(6, 11, ('Brok. Premium'), bold1)
            sheet.write(6, 12, ('Other Premium'), bold1)
            sheet.write(6, 13, ('Net Premium'), bold1)
            sheet.write(6, 14, ('Gross Premium'), bold1)
            # sheet.write(6, 11, ('Gross Premium'), bold1)
            # sheet.write(6, 12, ('Net Premium'), bold1)
            # sheet.write(6, 13, ('Other Premium'), bold1)
            # sheet.write(6,413, ('Covernote No./Date'), bold1)
            sheet.write(6, 15, ('Ends No./Date'), bold1)
            sheet.write(6, 16, ('Start Date'), bold2)
            sheet.write(6, 17, ('Expiry Date'), bold2)
            sheet.write(6, 18, ('Refer By/Sales Person'), bold)
            sheet.write(6, 19, ('Source(Employee)/Medium(POS)'), bold)

            # increasing width of column
            sheet.set_column('A:A', 15)
            sheet.set_column('B:B', 20)
            sheet.set_column('C:C', 20)
            sheet.set_column('D:D', 20)
            sheet.set_column('E:E', 15)
            sheet.set_column('F:F', 30)
            sheet.set_column('G:G', 40)
            sheet.set_column('H:H', 80)
            sheet.set_column('I:I', 20)
            sheet.set_column('J:J', 20)
            sheet.set_column('K:K', 20)
            sheet.set_column('L:L', 20)
            sheet.set_column('M:M', 20)
            sheet.set_column('N:N', 20)
            sheet.set_column('O:O', 20)
            sheet.set_column('P:P', 20)
            sheet.set_column('Q:Q', 20)
            sheet.set_column('R:R', 20)
            sheet.set_column('S:S', 30)
            sheet.set_column('T:T', 30)
            sheet.merge_range('A1:O1', report_head, merge_format1)
            sheet.merge_range('A4:T4', report_head2, merge_format)
            sheet.merge_range('A5:T5', report_head3, merge_format)
            sheet.merge_range('R1:T1', report_head4, bold3)
            sheet.merge_range('A2:C2', report_head5, merge_format1)

            row = 7
            s_no = 1


            usr_detail = []
            usr_details = self.querys(workbook, data, lines,start_date,start_year,start_year1,end_date,end_year1,end_year)
            endo_date =self.endos(workbook, data, lines,start_date,start_year,start_year1,end_date,end_year1,end_year)
            for j in endo_date:
                usr_detail.append(j)
            for i in usr_details:


                # if str(i['endo_ins']) == 'Yes':
                #     usr_details1 = self.querys(workbook, data, lines, start_date, start_year,
                #                                start_year1, end_date, end_year1,end_year,i['id'], 'Table1')
                #     print(len(usr_details1), "2")
                #     for j in usr_details1:
                #         usr_detail.append(j)

                if str(i['coins']) == 'Yes':
                    usr_details2 = self.querys(workbook, data, lines, start_date, start_year,
                                               start_year1, end_date, end_year1,end_year,i['id'], 'Table2')

                    for k in usr_details2:
                        usr_detail.append(k)
                else:
                    usr_detail.append(i)



            if lines.groupby == 'create_date':
                temp = []
                totalsuminsuredcount1 = 0
                totalgrosspremcount1 = 0
                totalbrokpremcount1 = 0
                totalnetpremcount1 = 0
                totalotherpremcount1 = 0
                an_iterator = itertools.groupby(usr_detail, key=operator.itemgetter('registername'))
                for key, group in an_iterator:
                    key_and_group = {key: list(group)}
                    for j in key_and_group.iteritems():
                         an_iterator12 = sorted(j[1], key=operator.itemgetter('docketdate'))
                         new_lst = itertools.groupby(an_iterator12, key=operator.itemgetter('docketdate'))
                         totalsuminsuredcount = 0
                         totalgrosspremcount = 0
                         totalbrokpremcount = 0
                         totalnetpremcount = 0
                         totalotherpremcount = 0
                         for key, group in new_lst:

                             key_and_group = {key: list(group)}
                             for i in key_and_group.iteritems():
                                # sheet.write(row, 0, i[0], border2)
                                # sheet.write(row, 2,  i[0], borderdate)
                                row += 1
                                suminsur_null = 0
                                gross_null = 0
                                netprem_null = 0
                                brokprem_null = 0
                                otherprem_null = 0
                                endos= 0
                                totalsuminsured = 0
                                totalgrossprem = 0
                                totalbrokprem = 0
                                totalnetprem = 0
                                totalotherprem = 0
                                tr=0
                                ts=0
                                tp=0
                                for res in i[1]:
                                    if res['suminsured'] == None or res['suminsured'] == False:
                                        suminsur_null = 0
                                    else:
                                        suminsur_null = res['suminsured']
                                    if res['brokprem'] == None or res['brokprem'] == False:
                                        brokprem_null = 0
                                    else:
                                        brokprem_null = res['brokprem']
                                    if res['grossprem'] == None or res['grossprem'] == False:
                                        gross_null = 0
                                    else:
                                        gross_null = res['grossprem']
                                    if res['netprem'] == None or res['netprem'] == False:
                                        netprem_null = 0
                                    else:
                                        netprem_null = res['netprem']
                                    # if res['otherprem'] == None or res['otherprem'] == False:
                                    #     otherprem_null = 0
                                    # else:
                                    #     otherprem_null = res['otherprem']
                                    if res['share'] == None or res['share'] == False:
                                        share = 100
                                    else:
                                        share = res['share']

                                    if res['tr'] == None or res['tr'] == False:
                                        tr = 0
                                    else:
                                        tr = res['tr']

                                    if res['tp'] == None or res['tp'] == False:
                                        tp = 0
                                    else:
                                        tp= res['tp']

                                    if res['ts'] == None or res['ts'] == False:
                                        ts = 0
                                    else:
                                        ts= res['ts']
                                    # print(tr,tp,ts,"PPPPPPPPPPPPPPpp")
                                    totalsuminsured += (suminsur_null)
                                    totalotherprem += float(tr)+float(tp)+float(ts)
                                    totalgrossprem += (gross_null)
                                    totalbrokprem += (brokprem_null)
                                    totalnetprem += (netprem_null)
                                    # sheet.write(row, 0, ' ', border1)
                                    sheet.write(row, 0, str(res['srno']) + str(' / ') + str(res['registersubno']),borderdate)
                                    sheet.write(row, 1, res['pipelineno'], borderdate)
                                    sheet.write(row, 2, res['proposaldate'], borderdate)
                                    sheet.write(row, 3, res['docketno'], borderdate)
                                    sheet.write(row, 4, res['type'], borderalpha)
                                    sheet.write(row, 5, res['subcategory'], borderalpha)
                                    sheet.write(row, 6, res['clientname'], borderalpha)
                                    sheet.write(row, 7, str(res['insurername']) + str(',  ') + str(res['insurerbranch']), borderalpha)
                                    sheet.write(row, 8, res['mode1'], borderalpha)
                                    sheet.write(row, 9, share, bordernum)
                                    sheet.write(row, 10, suminsur_null, numbersformat)
                                    sheet.write(row, 11, brokprem_null, numbersformat)
                                    sheet.write(row, 12, float(tr)+float(tp)+float(ts), numbersformat)
                                    sheet.write(row, 13, netprem_null, numbersformat)
                                    sheet.write(row, 14, gross_null, numbersformat)
                                    # sheet.write(row, 13, res['policyno'], bordernum)
                                    sheet.write(row, 15, str(res['endos_no']) + str(',   ') + str(res['endos_date']), bordernum)
                                    sheet.write(row, 16, res['startdate'], borderdate)
                                    sheet.write(row, 17, res['enddate'], borderdate)
                                    sheet.write(row, 18, str(res['referby']) + str(',   ') + str(res['salesperson']), borderalpha)
                                    sheet.write(row, 19, str(res['event']) + str(',    ') + str(res['csc']), borderalpha)

                                    row = row + 1
                                    s_no = s_no + 1
                                sheet.write(row, 7, ('Created Date Total ') + str(i[0]) , bold2)
                                sheet.write(row, 8 ,(' '), bold1)
                                sheet.write(row, 9 ,(' '), bold1)
                                sheet.write(row, 10, totalsuminsured, numbersformat1)
                                sheet.write(row, 11, totalbrokprem, numbersformat1)
                                sheet.write(row, 12, totalotherprem, numbersformat1)
                                sheet.write(row, 13, totalnetprem, numbersformat1)
                                sheet.write(row, 14, totalgrossprem, numbersformat1)
                                row += 1
                                totalsuminsuredcount += totalsuminsured
                                totalgrosspremcount += totalgrossprem
                                totalbrokpremcount += totalbrokprem
                                totalnetpremcount += totalnetprem
                                totalotherpremcount += totalotherprem

                                totalsuminsuredcount1 += totalsuminsured
                                totalgrosspremcount1 += totalgrossprem
                                totalbrokpremcount1 += totalbrokprem
                                totalnetpremcount1 += totalnetprem
                                totalotherpremcount1 += totalotherprem

                    sheet.write(row, 7, j[0] + str(' Total'), bold2)
                    sheet.write(row, 8, (' '), bold1)
                    sheet.write(row, 9, (' '), bold1)
                    sheet.write(row, 10, totalsuminsuredcount, numbersformat1)
                    sheet.write(row, 11, totalbrokpremcount, numbersformat1)
                    sheet.write(row, 12, totalotherpremcount, numbersformat1)
                    sheet.write(row, 13, totalnetpremcount, numbersformat1)
                    sheet.write(row, 14, totalgrosspremcount, numbersformat1)
                    row += 1
                sheet.write(row, 7,str('Register Total'), bold2)
                sheet.write(row, 8, (' '), bold1)
                sheet.write(row, 9, (' '), bold1)
                sheet.write(row, 10, totalsuminsuredcount1, numbersformat1)
                sheet.write(row, 11, totalbrokpremcount1, numbersformat1)
                sheet.write(row, 12, totalotherpremcount1, numbersformat1)
                sheet.write(row, 13, totalnetpremcount1, numbersformat1)
                sheet.write(row, 14, totalgrosspremcount1, numbersformat1)



            elif lines.groupby == 'proposaldate':
                temp = []
                totalsuminsuredcount1 = 0
                totalgrosspremcount1 = 0
                totalbrokpremcount1 = 0
                totalnetpremcount1 = 0
                totalotherpremcount1 = 0

                an_iterator = itertools.groupby(usr_detail, key=operator.itemgetter('registername'))
                for key, group in an_iterator:
                    key_and_group = {key: list(group)}
                    for j in key_and_group.iteritems():
                        an_iterator12 = sorted(j[1], key=operator.itemgetter('proposaldate'))
                        new_lst = itertools.groupby(an_iterator12, key=operator.itemgetter('proposaldate'))
                        totalsuminsuredcount = 0
                        totalgrosspremcount = 0
                        totalbrokpremcount = 0
                        totalnetpremcount = 0
                        totalotherpremcount = 0
                        for key, group in new_lst:

                            key_and_group = {key: list(group)}
                            for i in key_and_group.iteritems():
                                # sheet.write(row, 0, i[0], border2)
                                # sheet.write(row, 2,  i[0], borderdate)
                                row += 1
                                suminsur_null = 0
                                brokprem_null = 0
                                gross_null = 0
                                netprem_null = 0
                                otherprem_null = 0
                                endos = 0
                                totalsuminsured = 0
                                totalbrokprem = 0
                                totalgrossprem = 0
                                totalnetprem = 0
                                totalotherprem = 0
                                tr=0
                                ts=0
                                tp=0
                                for res in i[1]:
                                    if res['suminsured'] == None or res['suminsured'] == False:
                                        suminsur_null = 0
                                    else:
                                        suminsur_null = res['suminsured']
                                    if res['brokprem'] == None or res['brokprem'] == False:
                                        brokprem_null = 0
                                    else:
                                        brokprem_null = res['brokprem']
                                    if res['grossprem'] == None or res['grossprem'] == False:
                                        gross_null = 0
                                    else:
                                        gross_null = res['grossprem']
                                    if res['netprem'] == None or res['netprem'] == False:
                                        netprem_null = 0
                                    else:
                                        netprem_null = res['netprem']
                                    # if res['otherprem'] == None or res['otherprem'] == False:
                                    #     otherprem_null = 0
                                    # else:
                                    #     otherprem_null = res['otherprem']
                                    if res['share'] == None or res['share'] == False:
                                        share = 100
                                    else:
                                        share = res['share']

                                    if res['tr'] == None or res['tr'] == False:
                                        tr = 0
                                    else:
                                        tr = res['tr']

                                    if res['tp'] == None or res['tp'] == False:
                                        tp = 0
                                    else:
                                        tp = res['tp']

                                    if res['ts'] == None or res['ts'] == False:
                                        ts = 0
                                    else:
                                        ts = res['ts']

                                    totalsuminsured += (suminsur_null)
                                    totalotherprem += float(tr)+float(tp)+float(ts)
                                    totalbrokprem += (brokprem_null)
                                    totalgrossprem += (gross_null)
                                    totalnetprem += (netprem_null)
                                    # sheet.write(row, 0, ' ', border1)
                                    sheet.write(row, 0, str(res['srno']) + str(' / ') + str(res['registersubno']),
                                                borderdate)
                                    sheet.write(row, 1, res['pipelineno'], borderdate)
                                    sheet.write(row, 2, res['proposaldate'], borderdate)
                                    sheet.write(row, 3, res['docketno'], borderdate)
                                    sheet.write(row, 4, res['type'], borderalpha)
                                    sheet.write(row, 5, res['subcategory'], borderalpha)
                                    sheet.write(row, 6, res['clientname'], borderalpha)
                                    sheet.write(row, 7,
                                                str(res['insurername']) + str(',  ') + str(res['insurerbranch']),
                                                borderalpha)
                                    sheet.write(row, 8, res['mode1'], borderalpha)
                                    sheet.write(row, 9, share, bordernum)
                                    sheet.write(row, 10, suminsur_null, numbersformat)
                                    sheet.write(row, 11, brokprem_null, numbersformat)
                                    sheet.write(row, 12, float(tr)+float(tp)+float(ts), numbersformat)
                                    sheet.write(row, 13, netprem_null, numbersformat)
                                    sheet.write(row, 14, gross_null, numbersformat)
                                    # sheet.write(row, 13, res['policyno'], bordernum)
                                    sheet.write(row, 15, str(res['endos_no']) + str(',   ') + str(res['endos_date']),
                                                bordernum)
                                    sheet.write(row, 16, res['startdate'], borderdate)
                                    sheet.write(row, 17, res['enddate'], borderdate)
                                    sheet.write(row, 18, str(res['referby']) + str(',   ') + str(res['salesperson']),
                                                borderalpha)
                                    sheet.write(row, 19, str(res['event']) + str(',    ') + str(res['csc']),
                                                borderalpha)

                                    row = row + 1
                                    s_no = s_no + 1
                                sheet.write(row, 7, ('Proposal Date Total ') + str(i[0]), bold2)
                                sheet.write(row, 8, (' '), bold1)
                                sheet.write(row, 9, (' '), bold1)
                                sheet.write(row, 10, totalsuminsured, numbersformat1)
                                sheet.write(row, 11, totalbrokprem, numbersformat1)
                                sheet.write(row, 12, totalotherprem, numbersformat1)
                                sheet.write(row, 13, totalnetprem, numbersformat1)
                                sheet.write(row, 14, totalgrossprem, numbersformat1)
                                row += 1
                                totalsuminsuredcount += totalsuminsured
                                totalbrokpremcount += totalbrokprem
                                totalgrosspremcount += totalgrossprem
                                totalnetpremcount += totalnetprem
                                totalotherpremcount += totalotherprem
                                totalsuminsuredcount1 += totalsuminsured
                                totalbrokpremcount1 += totalbrokprem
                                totalgrosspremcount1 += totalgrossprem
                                totalnetpremcount1 += totalnetprem
                                totalotherpremcount1 += totalotherprem
                    sheet.write(row, 7, j[0] + str(' Total'), bold2)
                    sheet.write(row, 8, (' '), bold1)
                    sheet.write(row, 9, (' '), bold1)
                    sheet.write(row, 10, totalsuminsuredcount, numbersformat1)
                    sheet.write(row, 11, totalbrokpremcount, numbersformat1)
                    sheet.write(row, 12, totalotherpremcount, numbersformat1)
                    sheet.write(row, 13, totalnetpremcount, numbersformat1)
                    sheet.write(row, 14, totalgrosspremcount, numbersformat1)
                    row += 1
                sheet.write(row, 7, str('Register Total'), bold2)
                sheet.write(row, 8, (' '), bold1)
                sheet.write(row, 9, (' '), bold1)
                sheet.write(row, 10, totalsuminsuredcount1, numbersformat1)
                sheet.write(row, 11, totalbrokpremcount1, numbersformat1)
                sheet.write(row, 12, totalotherpremcount1, numbersformat1)
                sheet.write(row, 13, totalnetpremcount1, numbersformat1)
                sheet.write(row, 14, totalgrosspremcount1, numbersformat1)


            elif lines.groupby == 'startdate':
                temp = []
                totalsuminsuredcount1 = 0
                totalgrosspremcount1 = 0
                totalbrokpremcount1 = 0
                totalnetpremcount1 = 0
                totalotherpremcount1 = 0

                an_iterator = itertools.groupby(usr_detail, key=operator.itemgetter('registername'))
                for key, group in an_iterator:
                    key_and_group = {key: list(group)}
                    for j in key_and_group.iteritems():
                        an_iterator12 = sorted(j[1], key=operator.itemgetter('startdate'))
                        new_lst = itertools.groupby(an_iterator12, key=operator.itemgetter('startdate'))
                        totalsuminsuredcount = 0
                        totalgrosspremcount = 0
                        totalbrokpremcount = 0
                        totalnetpremcount = 0
                        totalotherpremcount = 0
                        for key, group in new_lst:

                            key_and_group = {key: list(group)}
                            for i in key_and_group.iteritems():
                                # sheet.write(row, 0, i[0], border2)
                                # sheet.write(row, 2,  i[0], borderdate)
                                row += 1
                                suminsur_null = 0
                                gross_null = 0
                                netprem_null = 0
                                brokprem_null = 0
                                otherprem_null = 0
                                endos = 0
                                totalsuminsured = 0
                                totalgrossprem = 0
                                totalnetprem = 0
                                totalbrokprem = 0
                                totalotherprem = 0
                                tr=0
                                tp=0
                                ts=0
                                for res in i[1]:
                                    if res['suminsured'] == None or res['suminsured'] == False:
                                        suminsur_null = 0
                                    else:
                                        suminsur_null = res['suminsured']
                                    if res['brokprem'] == None or res['brokprem'] == False:
                                        brokprem_null = 0
                                    else:
                                        brokprem_null = res['brokprem']
                                    if res['grossprem'] == None or res['grossprem'] == False:
                                        gross_null = 0
                                    else:
                                        gross_null = res['grossprem']
                                    if res['netprem'] == None or res['netprem'] == False:
                                        netprem_null = 0
                                    else:
                                        netprem_null = res['netprem']
                                    # if res['otherprem'] == None or res['otherprem'] == False:
                                    #     otherprem_null = 0
                                    # else:
                                    #     otherprem_null = res['otherprem']
                                    if res['share'] == None or res['share'] == False:
                                        share=100
                                    else:
                                        share =res['share']

                                    if res['tr'] == None or res['tr'] == False:
                                        tr = 0
                                    else:
                                        tr = res['tr']

                                    if res['tp'] == None or res['tp'] == False:
                                        tp = 0
                                    else:
                                        tp = res['tp']

                                    if res['ts'] == None or res['ts'] == False:
                                        ts = 0
                                    else:
                                        ts = res['ts']

                                    totalsuminsured += (suminsur_null)
                                    totalotherprem += (float(tr)+float(tp)+float(ts))
                                    totalgrossprem += (gross_null)
                                    totalnetprem += (netprem_null)
                                    totalbrokprem += (brokprem_null)
                                    # sheet.write(row, 0, ' ', border1)
                                    sheet.write(row, 0, str(res['srno']) + str(' / ') + str(res['registersubno']),
                                                borderdate)
                                    sheet.write(row, 1, res['pipelineno'], borderdate)
                                    sheet.write(row, 2, res['proposaldate'], borderdate)
                                    sheet.write(row, 3, res['docketno'], borderdate)
                                    sheet.write(row, 4, res['type'], borderalpha)
                                    sheet.write(row, 5, res['subcategory'], borderalpha)
                                    sheet.write(row, 6, res['clientname'], borderalpha)
                                    sheet.write(row, 7, str(res['insurername']) + str(',  ') + str(res['insurerbranch']),borderalpha)
                                    sheet.write(row, 8, res['mode1'], borderalpha)
                                    sheet.write(row, 9, share, bordernum)
                                    sheet.write(row, 10, suminsur_null, numbersformat)
                                    sheet.write(row, 11, brokprem_null, numbersformat)
                                    sheet.write(row, 12, float(tr)+float(tp)+float(ts),numbersformat)
                                    sheet.write(row, 13, netprem_null, numbersformat)
                                    sheet.write(row, 14, gross_null, numbersformat)
                                    # sheet.write(row, 13, res['policyno'], bordernum)
                                    sheet.write(row, 15, str(res['endos_no']) + str(',   ') + str(res['endos_date']),
                                                bordernum)
                                    sheet.write(row, 16, res['startdate'], borderdate)
                                    sheet.write(row, 17, res['enddate'], borderdate)
                                    sheet.write(row, 18, str(res['referby']) + str(',   ') + str(res['salesperson']),
                                                borderalpha)
                                    sheet.write(row, 19, str(res['event']) + str(',    ') + str(res['csc']),
                                                borderalpha)
                                    row = row + 1
                                    s_no = s_no + 1
                                sheet.write(row, 7, ('Start Date Total ') + str(i[0]), bold2)
                                sheet.write(row, 8, (' '), bold1)
                                sheet.write(row, 9, (' '), bold1)
                                sheet.write(row, 10, totalsuminsured, numbersformat1)
                                sheet.write(row, 11, totalbrokprem, numbersformat1)
                                sheet.write(row, 12, totalotherprem, numbersformat1)
                                sheet.write(row, 13, totalnetprem, numbersformat1)
                                sheet.write(row, 14, totalgrossprem, numbersformat1)
                                row += 1
                                totalsuminsuredcount += totalsuminsured
                                totalgrosspremcount += totalgrossprem
                                totalbrokpremcount += totalbrokprem
                                totalnetpremcount += totalnetprem
                                totalotherpremcount += totalotherprem

                                totalsuminsuredcount1 += totalsuminsured
                                totalgrosspremcount1 += totalgrossprem
                                totalbrokpremcount1 += totalbrokprem
                                totalnetpremcount1 += totalnetprem
                                totalotherpremcount1 += totalotherprem

                    sheet.write(row, 7, j[0] + str(' Total'), bold2)
                    sheet.write(row, 8, (' '), bold1)
                    sheet.write(row, 9, (' '), bold1)
                    sheet.write(row, 10, totalsuminsuredcount, numbersformat1)
                    sheet.write(row, 11, totalbrokpremcount, numbersformat1)
                    sheet.write(row, 12, totalotherpremcount, numbersformat1)
                    sheet.write(row, 13, totalnetpremcount, numbersformat1)
                    sheet.write(row, 14, totalgrosspremcount, numbersformat1)
                    row += 1
                sheet.write(row, 7, ('Register Total'), bold2)
                sheet.write(row, 8, (' '), bold1)
                sheet.write(row, 9, (' '), bold1)
                sheet.write(row, 10, totalsuminsuredcount1, numbersformat1)
                sheet.write(row, 11, totalbrokpremcount1, numbersformat1)
                sheet.write(row, 12, totalotherpremcount1, numbersformat1)
                sheet.write(row, 13, totalnetpremcount1, numbersformat1)
                sheet.write(row, 14, totalgrosspremcount1, numbersformat1)



            else:
                temp = []
                totalsuminsuredcount1 = 0
                totalgrosspremcount1 = 0
                totalbrokpremcount1 = 0
                totalnetpremcount1 = 0
                totalotherpremcount1 = 0
                an_iterator = itertools.groupby(usr_detail, key=operator.itemgetter('registername'))
                for key, group in an_iterator:
                    key_and_group = {key: list(group)}
                    for j in key_and_group.iteritems():
                        an_iterator12 = sorted(j[1], key=operator.itemgetter('docketdate'))
                        new_lst = itertools.groupby(an_iterator12, key=operator.itemgetter('docketdate'))
                        totalsuminsuredcount = 0
                        totalgrosspremcount = 0
                        totalbrokpremcount = 0
                        totalnetpremcount = 0
                        totalotherpremcount = 0
                        for key, group in new_lst:
                            key_and_group = {key: list(group)}
                            for i in key_and_group.iteritems():
                                # sheet.write(row, 0, i[0], border2)
                                row += 1
                                suminsur_null = 0
                                gross_null = 0
                                netprem_null = 0
                                brokprem_null = 0
                                otherprem_null = 0
                                endos = 0
                                totalsuminsured = 0
                                totalgrossprem = 0
                                totalbrokprem = 0
                                totalnetprem = 0
                                totalotherprem = 0
                                tr=0
                                ts=0
                                tp=0
                                for res in i[1]:
                                    if res['suminsured'] == None or res['suminsured'] == False:
                                        suminsur_null = 0
                                    else:
                                        suminsur_null = res['suminsured']
                                    if res['brokprem'] == None or res['brokprem'] == False:
                                        brokprem_null = 0
                                    else:
                                        brokprem_null = res['brokprem']
                                    if res['grossprem'] == None or res['grossprem'] == False:
                                        gross_null = 0
                                    else:
                                        gross_null = res['grossprem']
                                    if res['netprem'] == None or res['netprem'] == False:
                                        netprem_null = 0
                                    else:
                                        netprem_null = res['netprem']
                                    if res['otherprem'] == None or res['otherprem'] == False:
                                        otherprem_null = 0
                                    else:
                                        otherprem_null = res['otherprem']
                                    if res['share'] == None or res['share'] == False:
                                        share = 100
                                    else:
                                        share = res['share']

                                    if res['tr'] == None or res['tr'] == False:
                                        tr = 0
                                    else:
                                        tr = res['tr']

                                    if res['tp'] == None or res['tp'] == False:
                                        tp = 0
                                    else:
                                        tp = res['tp']

                                    if res['ts'] == None or res['ts'] == False:
                                        ts = 0
                                    else:
                                        ts = res['ts']

                                    totalsuminsured += (suminsur_null)
                                    totalotherprem += (float(tr)+float(tp)+float(ts))
                                    totalgrossprem += (gross_null)
                                    totalnetprem += (netprem_null)
                                    totalbrokprem += (brokprem_null)
                                    # sheet.write(row, 0, ' ', border1)
                                    sheet.write(row, 0, str(res['srno']) + str(' / ') + str(res['registersubno']),
                                                borderdate)
                                    sheet.write(row, 1, res['pipelineno'], borderdate)
                                    sheet.write(row, 2, res['proposaldate'], borderdate)
                                    sheet.write(row, 3, res['docketno'], borderdate)
                                    sheet.write(row, 4, res['type'], borderalpha)
                                    sheet.write(row, 5, res['subcategory'], borderalpha)
                                    sheet.write(row, 6, res['clientname'], borderalpha)
                                    sheet.write(row, 7,
                                                str(res['insurername']) + str(',  ') + str(res['insurerbranch']),
                                                borderalpha)
                                    sheet.write(row, 8, res['mode1'], borderalpha)
                                    sheet.write(row, 9, share, bordernum)
                                    sheet.write(row, 10, suminsur_null, numbersformat)
                                    sheet.write(row, 11, brokprem_null, numbersformat)
                                    sheet.write(row, 12, (float(tr)+float(tp)+float(ts)), numbersformat)
                                    sheet.write(row, 13, netprem_null, numbersformat)
                                    sheet.write(row, 14, gross_null, numbersformat)
                                    # sheet.write(row, 13, res['policyno'], bordernum)
                                    sheet.write(row, 15, str(res['endos_no']) + str(',   ') + str(res['endos_date']),
                                                bordernum)
                                    sheet.write(row, 16, res['startdate'], borderdate)
                                    sheet.write(row, 17, res['enddate'], borderdate)
                                    sheet.write(row, 18, str(res['referby']) + str(',   ') + str(res['salesperson']),
                                                borderalpha)
                                    sheet.write(row, 19, str(res['event']) + str(',    ') + str(res['csc']),
                                                borderalpha)

                                row = row + 1
                                s_no = s_no + 1
                                sheet.write(row, 7, ('Created Date Total ') + str(i[0]), bold2)
                                sheet.write(row, 8, (' '), bold1)
                                sheet.write(row, 9, (' '), bold1)
                                sheet.write(row, 10, totalsuminsured, numbersformat1)
                                sheet.write(row, 11, totalbrokprem, numbersformat1)
                                sheet.write(row, 12, totalotherprem, numbersformat1)
                                sheet.write(row, 13, totalnetprem, numbersformat1)
                                sheet.write(row, 14, totalgrossprem, numbersformat1)
                                row += 1
                                totalsuminsuredcount += totalsuminsured
                                totalgrosspremcount += totalgrossprem
                                totalbrokpremcount += totalbrokprem
                                totalnetpremcount += totalnetprem
                                totalotherpremcount += totalotherprem

                                totalsuminsuredcount1 += totalsuminsured
                                totalgrosspremcount1 += totalgrossprem
                                totalbrokpremcount1 += totalbrokprem
                                totalnetpremcount1 += totalnetprem
                                totalotherpremcount1 += totalotherprem

                    sheet.write(row, 7, j[0] + str(' Total'), bold2)
                    sheet.write(row, 8, (' '), bold1)
                    sheet.write(row, 9, (' '), bold1)
                    sheet.write(row, 10, totalsuminsuredcount, numbersformat1)
                    sheet.write(row, 11, totalbrokpremcount, numbersformat1)
                    sheet.write(row, 12, totalotherpremcount, numbersformat1)
                    sheet.write(row, 13, totalnetpremcount, numbersformat1)
                    sheet.write(row, 14, totalgrosspremcount, numbersformat1)
                    row += 1
                sheet.write(row, 7, ('Register Total'), bold2)
                sheet.write(row, 8, (' '), bold1)
                sheet.write(row, 9, (' '), bold1)
                sheet.write(row, 10, totalsuminsuredcount1, numbersformat1)
                sheet.write(row, 11, totalbrokpremcount1, numbersformat1)
                sheet.write(row, 12, totalotherpremcount1, numbersformat1)
                sheet.write(row, 13, totalnetpremcount1, numbersformat1)
                sheet.write(row, 14, totalgrosspremcount1, numbersformat1)


        def querys(self, workbook, data, lines,start_date,start_year,start_year1,end_date,end_year1,end_year,id=None,endo=None):
                db_name = odoo.tools.config.get('db_name')
                registry = Registry(db_name)
                with registry.cursor() as cr:
                    query = "select t1.tppremium AS tp,t1.terrprem AS tr,t1.stamprem AS ts ,t1.date2 as docketdate," \
                            " t1.registersubno as registersubno, t1.regsitersrno as srno,t1.name as docketno," \
                            " t1.pipeline_id as pipelineno,t1.sale_order_id as quotationno," \
                            " t1.proposaldate as proposaldate,t17.name as salesperson," \
                            " t1.ref as referby, " \
                            " t1.startfrom as startdate,t1.expiry as enddate," \
                            " t8.name as location,t3.name as registername," \
                            " t11.name as clientname,t12.name as type,t1.policyno ,t13.name as mode1," \
                            " t4.name as insurerbranch,t5.name as subcategory,t6.name as csc,t7.name as event,t1.registername1,t1.endo_ins,t1.coins,t1.id"

                    if id != None and endo =='Table1' and id is not False:
                        query+="  ,t9.endos_date,t9.name as endos_no,'' as share,t9.endos_brokerage_premium as brokprem,t9.endo_net as netprem ,t9.endo_gst_gross as grossprem,t9.endos_suminsured as suminsured"
                    elif id != None and endo =='Table2' and id is not False:
                        query+= " ,'' as endos_date ,'' as endos_no,t21.name as insurername,t20.co_share as share,t20.co_brokerage_pre as brokprem,t20.co_sum_insured as suminsured ,t20.co_net_gross_pre as grossprem,t20.co_net_premium as netprem"
                    else:
                        query+= " ,'' as endos_date ,'' as endos_no,'' as share, t1.grossprem as grossprem,t1.brokerageprem as brokprem,t10.name as insurername,t1.suminsured as suminsured,t1.netprem as netprem"
                        # query += " ,'' as endos_date ,'' as endos_no,'' as share, case when t20.co_insurer_id then t20.co_net_gross_pre else sum(t1.grossprem)  end as grossprem," \
                                 # "  case when t20.co_insurer_id then t20.co_sum_insured else sum(t1.suminsured) as suminsured,sum(t1.netprem) as netprem "

                    query+= " from policytransaction as t1 left join res_partner as t10 on t10.id=t1.insurername123" \
                            " left join res_partner as t11 on t11.id=t1.clientname" \
                            " left join subdata_subdata as t3 on t3.id=t1.registername1" \
                            " left join subdata_subdata as t12 on t12.id=t1.type" \
                            " left join ptransaction1 as t15 on t15.name =t1.id  and t15.pay_of_id='policy' and t15.amountpy > 0" \
                            " left join subdata_subdata as t13 on t13.id=t15.mode1" \
                            " left join res_users as t16 on t1.rm =t16.id" \
                            " left join res_partner as t17 on t16.partner_id=t17.id" \
                            " left join insurerbranch as t4 on t4.id=t1.insurerbranch" \
                            " left join subcategory_subcategory as t5 on t5.id=t1.name1" \
                            " left join utm_medium as t6 on t6.id=t1.csc" \
                            " left join utm_source as t7 on t7.id=t1.event " \
                            " left join clickbima_clickbima as t8 on t8.id=t1.location "

                    if id != None and endo == 'Table1' and  id is not False:
                            query += " left join endos_policy as t9 on t9.endo_id=t1.id "
                    elif id != None and endo == 'Table2'  and  id is not False:
                            query += " left join co_insurer_policy as t20 on t20.co_insurer_id=t1.id AND t20.co_type='self'" \
                                     " left join res_partner as t21 on t21.id=t20.co_insurer_name"

                    dy_date = ''
                    if lines.groupby == 'create_date':
                        dy_date = 't1.date2'
                    elif lines.groupby == 'proposaldate':
                        dy_date = 't1.proposaldate'
                    elif lines.groupby == 'startdate':
                        dy_date = 't1.startfrom'
                    else:
                        dy_date = 't1.date2'

                    # if lines.filterby == "medium":
                    #     if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    #         query += " where " + str(dy_date) + "  BETWEEN '" + str(
                    #             lines.fiscal_year.date_start) + "' AND '" + str(
                    #             lines.fiscal_year.date_end) + "' AND t6.name = '" + str(lines.medium.name) + "'  group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                           "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno ,t1.registername1 order by t3.name,t1.regsitersrno"
                    #
                    #     if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    #         if lines.months == '01-01':
                    #
                    #             jan_start = str(end_year) + str(start_date)
                    #             jan_end = str(end_year) + str(end_date)
                    #
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(jan_start) + "' AND '" + str(
                    #                 jan_end) + "'  AND t6.name = '" + str(lines.medium.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno ,t1.registername1 order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-02':
                    #             feb_start = str(end_year) + str(start_date)
                    #             feb_end = str(end_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(feb_start) + "' AND '" + str(
                    #                 feb_end) + "' AND t6.name = '" + str(lines.medium.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno ,t1.registername1 order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-03':
                    #             mar_start = str(end_year) + str(start_date)
                    #             mar_end = str(end_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(mar_start) + "' AND '" + str(
                    #                 mar_end) + "' AND t6.name = '" + str(lines.medium.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno ,t1.registername1 order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-04':
                    #             apr_start = str(start_year) + str(start_date)
                    #             apr_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(apr_start) + "' AND '" + str(
                    #                 apr_end) + "' AND t6.name = '" + str(lines.medium.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno ,t1.registername1 order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-05':
                    #             may_start = str(start_year) + str(start_date)
                    #             may_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(may_start) + "' AND '" + str(
                    #                 may_end) + "' AND t6.name = '" + str(lines.medium.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno ,t1.registername1 order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-06':
                    #             june_start = str(start_year) + str(start_date)
                    #             june_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(june_start) + "' AND '" + str(
                    #                 june_end) + "' AND t6.name = '" + str(lines.medium.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                             "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno ,t1.registername1 order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-07':
                    #             jul_start = str(start_year) + str(start_date)
                    #             jul_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(jul_start) + "' AND '" + str(
                    #                 jul_end) + "' AND t6.name = '" + str(lines.medium.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno ,t1.registername1 order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-08':
                    #             aug_start = str(start_year) + str(start_date)
                    #             aug_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(aug_start) + "' AND '" + str(
                    #                 aug_end) + "' AND t6.name = '" + str(lines.medium.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno ,t1.registername1 order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-09':
                    #             sep_start = str(start_year) + str(start_date)
                    #             sep_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(sep_start) + "' AND '" + str(
                    #                 sep_end) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno ,t1.registername1 order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-10':
                    #             oct_start = str(start_year) + str(start_date)
                    #             oct_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(oct_start) + "' AND '" + str(
                    #                 oct_end) + "' AND t6.name = '" + str(lines.medium.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno ,t1.registername1 order by t3.name,t1.regsitersrno"
                    #         if lines.months == '01-11':
                    #             nov_start = str(start_year) + str(start_date)
                    #             nov_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(nov_start) + "' AND '" + str(
                    #                 nov_end) + "' AND t6.name = '" + str(lines.medium.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno ,t1.registername1 order by t3.name,t1.regsitersrno"
                    #         if lines.months == '01-12':
                    #             dec_start = str(start_year) + str(start_date)
                    #             dec_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(dec_start) + "' AND '" + str(
                    #                 dec_end) + "' AND t6.name = '" + str(lines.medium.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno ,t1.registername1 order by t3.name,t1.regsitersrno"
                    #
                    #     if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    #         query += " where " + str(dy_date) + "  BETWEEN '" + str(
                    #             lines.date_from + ' 00:00:00') + "' AND '" + str(
                    #             lines.date_to + ' 23:59:59') + "' AND t6.name = '" + str(lines.medium.name) + "' group by t1.pipeline_id,t1.sale_order_id," \
                    #             "t1.date2,t3.name,t10.name,t4.name,t5.name,t6.name,t7.name,t8.name,t13.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate," \
                    #             "t1.suminsured,t17.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno ,t1.registername1"
                    #
                    #     cr.execute(query)
                    #     usr_detail = cr.dictfetchall()
                    #
                    # elif lines.filterby == "referredby":
                    #     if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    #         query += " where " + str(dy_date) + "  BETWEEN '" + str(
                    #             lines.fiscal_year.date_start) + "' AND '" + str(
                    #             lines.fiscal_year.date_end) + "' AND t1.ref = '" + str(lines.referred_by) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                           "t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #     if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    #         year = lines.fiscal_year.name
                    #         if lines.months == '01-01':
                    #             jan_start = str(end_year) + str(start_date)
                    #             jan_end = str(end_year) + str(end_date)
                    #
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(jan_start) + "' AND '" + str(
                    #                 jan_end) + "' AND t1.ref = '" + str(lines.referred_by) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-02':
                    #             feb_start = str(end_year) + str(start_date)
                    #             feb_end = str(end_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(feb_start) + "' AND '" + str(
                    #                 feb_end) + "' AND t1.ref = '" + str(lines.referred_by) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-03':
                    #             mar_start = str(end_year) + str(start_date)
                    #             mar_end = str(end_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(mar_start) + "' AND '" + str(
                    #                 mar_end) + "' AND t1.ref = '" + str(lines.referred_by) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-04':
                    #             apr_start = str(start_year) + str(start_date)
                    #             apr_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(apr_start) + "' AND '" + str(
                    #                 apr_end) + "' AND t1.ref = '" + str(lines.referred_by) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-05':
                    #             may_start = str(start_year) + str(start_date)
                    #             may_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(may_start) + "' AND '" + str(
                    #                 may_end) + "' AND t1.ref = '" + str(lines.referred_by) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-06':
                    #             june_start = str(start_year) + str(start_date)
                    #             june_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(june_start) + "' AND '" + str(
                    #                 june_end) + "' AND t1.ref = '" + str(lines.referred_by) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                             "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-07':
                    #             jul_start = str(start_year) + str(start_date)
                    #             jul_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(jul_start) + "' AND '" + str(
                    #                 jul_end) + "' AND t1.ref = '" + str(lines.referred_by) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-08':
                    #             aug_start = str(start_year) + str(start_date)
                    #             aug_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(aug_start) + "' AND '" + str(
                    #                 aug_end) + "' AND t1.ref = '" + str(lines.referred_by) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-09':
                    #             sep_start = str(start_year) + str(start_date)
                    #             sep_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(sep_start) + "' AND '" + str(
                    #                 sep_end) + "' AND t1.ref = '" + str(lines.referred_by) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-10':
                    #             oct_start = str(start_year) + str(start_date)
                    #             oct_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(oct_start) + "' AND '" + str(
                    #                 oct_end) + "' AND t1.ref = '" + str(lines.referred_by) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #         if lines.months == '01-11':
                    #             nov_start = str(start_year) + str(start_date)
                    #             nov_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(nov_start) + "' AND '" + str(
                    #                 nov_end) + "' AND t1.ref = '" + str(lines.referred_by) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #         if lines.months == '01-12':
                    #             dec_start = str(start_year) + str(start_date)
                    #             dec_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(dec_start) + "' AND '" + str(
                    #                 dec_end) + "' AND t1.ref = '" + str(lines.referred_by) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                            "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #     if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    #         query += " where " + str(dy_date) + "  BETWEEN '" + str(
                    #             lines.date_from + ' 00:00:00') + "' AND '" + str(
                    #             lines.date_to + ' 23:59:59') + "' AND t1.ref = '" + str(lines.referred_by) + "' group by t1.pipeline_id,t1.date2,t1.registername1,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t7.name,t8.name,t13.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #     cr.execute(query)
                    #     usr_detail = cr.dictfetchall()


                    if lines.filterby == "registername":

                        if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                            if id != None and endo == 'Table1' and id is not False:
                                query += " where t9.endos_date BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                                lines.fiscal_year.date_end) + "' AND t3.name = '" + str(lines.register_name.name) + "' "
                            else:
                                query += " where " + str(dy_date) + "  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                                            lines.fiscal_year.date_end) + "' AND t3.name = '" + str(lines.register_name.name) + "' "

                        if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                            year = lines.fiscal_year.name
                            if lines.months == '01-01':
                                jan_start = str(end_year) + str(start_date)
                                jan_end = str(end_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date  BETWEEN '" + str(jan_start) + "' AND '" + str(
                                        jan_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(jan_start) + "' AND '" + str(
                                        jan_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "

                            if lines.months == '01-02':
                                feb_start = str(end_year) + str(start_date)
                                feb_end = str(end_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(feb_start) + "' AND '" + str(
                                        feb_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(feb_start) + "' AND '" + str(
                                        feb_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                            if lines.months == '01-03':
                                mar_start = str(end_year) + str(start_date)
                                mar_end = str(end_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(mar_start) + "' AND '" + str(
                                        mar_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(mar_start) + "' AND '" + str(
                                        mar_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "

                            if lines.months == '01-04':
                                apr_start = str(start_year) + str(start_date)
                                apr_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(apr_start) + "' AND '" + str(
                                        apr_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(apr_start) + "' AND '" + str(
                                        apr_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "

                            if lines.months == '01-05':
                                may_start = str(start_year) + str(start_date)
                                may_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(may_start) + "' AND '" + str(
                                        may_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        may_start) + "' AND '" + str(
                                        may_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "

                            if lines.months == '01-06':
                                june_start = str(start_year) + str(start_date)
                                june_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(june_start) + "' AND '" + str(
                                        june_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        june_start) + "' AND '" + str(
                                        june_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "

                            if lines.months == '01-07':
                                jul_start = str(start_year) + str(start_date)
                                jul_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(jul_start) + "' AND '" + str(
                                        jul_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        jul_start) + "' AND '" + str(
                                        jul_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                            if lines.months == '01-08':
                                aug_start = str(start_year) + str(start_date)
                                aug_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(aug_start) + "' AND '" + str(
                                        aug_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        aug_start) + "' AND '" + str(
                                        aug_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "

                            if lines.months == '01-09':
                                sep_start = str(start_year) + str(start_date)
                                sep_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(sep_start) + "' AND '" + str(
                                        sep_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        sep_start) + "' AND '" + str(
                                        sep_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                            if lines.months == '01-10':
                                oct_start = str(start_year) + str(start_date)
                                oct_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(oct_start) + "' AND '" + str(
                                        oct_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        oct_start) + "' AND '" + str(
                                        oct_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                            if lines.months == '01-11':
                                nov_start = str(start_year) + str(start_date)
                                nov_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(nov_start) + "' AND '" + str(
                                        nov_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(nov_start) + "' AND '" + str(
                                        nov_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                            if lines.months == '01-12':
                                dec_start = str(start_year) + str(start_date)
                                dec_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(dec_start) + "' AND '" + str(
                                        dec_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        dec_start) + "' AND '" + str(
                                        dec_end) + "' AND t3.name = '" + str(
                                        lines.register_name.name) + "' "
                        if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                            if id != None and endo == 'Table1' and id is not False:
                                query += " where t9.endos_date BETWEEN '" + str(
                                    lines.date_from + ' 00:00:00') + "' AND '" + str(
                                    lines.date_to + ' 23:59:59') + "' AND t3.name = '" + str(
                                    lines.register_name.name) + "'"
                            else:
                                query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                    lines.date_from + ' 00:00:00') + "' AND '" + str(
                                    lines.date_to + ' 23:59:59') + "' AND t3.name = '" + str(
                                    lines.register_name.name) + "'"

                        if id != None and endo == 'Table1'  and  id is not False:
                            query += " and t9.endo_id= '" + str(id) + "'"
                        elif id != None and endo == 'Table2'  and  id is not False:
                            query += " and t20.co_insurer_id= '" + str(id) + "' "

                        if id != None and endo == 'Table1'  and  id is not False:
                            if lines.location != 'all':
                                query += " and t1.location = '" + str(lines.location) +  "' group by t9.name,t9.endos_date,t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name," \
                                     " t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno,t1.endo_ins,t1.coins,t1.id,t9.name,t9.endos_brokerage_premium,t9.endo_net,t9.endos_suminsured ,t9.endo_gst_gross,t1.tppremium,t1.terrprem,t1.stamprem  order by t3.name,t1.regsitersrno"
                            else:
                                query += " group by t9.name,t9.endos_date,t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name," \
                                         " t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno,t1.endo_ins,t1.coins,t1.id,t9.name,t9.endos_brokerage_premium,t9.endo_net,t9.endos_suminsured ,t9.endo_gst_gross,t1.tppremium,t1.terrprem,t1.stamprem  order by t3.name,t1.regsitersrno"

                        elif id != None and endo == 'Table2'  and  id is not False:
                            if lines.location != 'all':
                                query += " and t1.location = '" + str(lines.location) + "' group by t20.co_net_gross_pre,t20.co_net_premium,t20.co_sum_insured,t20.co_brokerage_pre,t21.name,t20.co_share,t1.pipeline_id,t1.sale_order_id,t3.name,t4.name,t5.name,t6.name,t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name," \
                                     " t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno,t1.endo_ins,t1.coins,t1.id,t1.tppremium,t1.terrprem,t1.stamprem order by t3.name,t1.regsitersrno"
                            else:
                                query += " group by t20.co_net_gross_pre,t20.co_net_premium,t20.co_sum_insured,t20.co_brokerage_pre,t21.name,t20.co_share,t1.pipeline_id,t1.sale_order_id,t3.name,t4.name,t5.name,t6.name,t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name," \
                                     " t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno,t1.endo_ins,t1.coins,t1.id,t1.tppremium,t1.terrprem,t1.stamprem order by t3.name,t1.regsitersrno"
                        else:
                            if lines.location != 'all':
                                query += " and t1.location = '" + str(lines.location) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name," \
                                     " t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno,t1.grossprem,t1,brokerageprem,t1.netprem,t1.endo_ins,t1.coins,t1.id,t1.tppremium,t1.terrprem,t1.stamprem order by t3.name,t1.regsitersrno"
                            else:
                                query += " group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name," \
                                     " t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno,t1.grossprem,t1,brokerageprem,t1.netprem,t1.endo_ins,t1.coins,t1.id,t1.tppremium,t1.terrprem,t1.stamprem order by t3.name,t1.regsitersrno"

                        print(query,"QUERY")
                        cr.execute(query)

                        usr_detail = cr.dictfetchall()
                        return usr_detail
                    # elif lines.filterby == "source":
                    #     if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    #         query += " where " + str(dy_date) + "  BETWEEN '" + str(
                    #             lines.fiscal_year.date_start) + "' AND '" + str(
                    #             lines.fiscal_year.date_end) + "' AND t7.name = '" + str(
                    #             lines.source.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                  "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.registername1,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #     if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    #         year = lines.fiscal_year.name
                    #         if lines.months == '01-01':
                    #             jan_start = str(end_year) + str(start_date)
                    #             jan_end = str(end_year) + str(end_date)
                    #
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(jan_start) + "' AND '" + str(
                    #                 jan_end) + "' AND t7.name = '" + str(
                    #                 lines.source.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                      "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-02':
                    #             feb_start = str(end_year) + str(start_date)
                    #             feb_end = str(end_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(feb_start) + "' AND '" + str(
                    #                 feb_end) + "' AND t7.name = '" + str(
                    #                 lines.source.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                      "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-03':
                    #             mar_start = str(end_year) + str(start_date)
                    #             mar_end = str(end_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(mar_start) + "' AND '" + str(
                    #                 mar_end) + "' AND t7.name = '" + str(
                    #                 lines.source.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                      "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-04':
                    #             apr_start = str(start_year) + str(start_date)
                    #             apr_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(apr_start) + "' AND '" + str(
                    #                 apr_end) + "' AND t7.name = '" + str(
                    #                 lines.source.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                      "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-05':
                    #             may_start = str(start_year) + str(start_date)
                    #             may_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(may_start) + "' AND '" + str(
                    #                 may_end) + "' AND t7.name = '" + str(
                    #                 lines.source.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                      "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-06':
                    #             june_start = str(start_year) + str(start_date)
                    #             june_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(june_start) + "' AND '" + str(
                    #                 june_end) + "' AND t7.name = '" + str(
                    #                 lines.source.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                      "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-07':
                    #             jul_start = str(start_year) + str(start_date)
                    #             jul_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(jul_start) + "' AND '" + str(
                    #                 jul_end) + "' AND t7.name = '" + str(
                    #                 lines.source.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                      "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-08':
                    #             aug_start = str(start_year) + str(start_date)
                    #             aug_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(aug_start) + "' AND '" + str(
                    #                 aug_end) + "' AND t7.name = '" + str(
                    #                 lines.source.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                      "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-09':
                    #             sep_start = str(start_year) + str(start_date)
                    #             sep_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(sep_start) + "' AND '" + str(
                    #                 sep_end) + "' AND t7.name = '" + str(
                    #                 lines.source.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                      "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-10':
                    #             oct_start = str(start_year) + str(start_date)
                    #             oct_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(oct_start) + "' AND '" + str(
                    #                 oct_end) + "' AND t7.name = '" + str(
                    #                 lines.source.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                      "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #         if lines.months == '01-11':
                    #             nov_start = str(start_year) + str(start_date)
                    #             nov_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(nov_start) + "' AND '" + str(
                    #                 nov_end) + "' AND t7.name = '" + str(
                    #                 lines.source.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                      "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #         if lines.months == '01-12':
                    #             dec_start = str(start_year) + str(start_date)
                    #             dec_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(dec_start) + "' AND '" + str(
                    #                 dec_end) + "' AND t7.name = '" + str(
                    #                 lines.source.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                             "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #     if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    #         query += " where " + str(dy_date) + "  BETWEEN '" + str(
                    #             lines.date_from + ' 00:00:00') + "' AND '" + str(
                    #             lines.date_to + ' 23:59:59') + "' AND t7.name = '" + str(
                    #             lines.source.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                  "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #     cr.execute(query)
                    #     usr_detail = cr.dictfetchall()
                    #
                    # elif lines.filterby == "policystatus":
                    #     if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    #         query += " where " + str(dy_date) + "  BETWEEN '" + str(
                    #             lines.fiscal_year.date_start) + "' AND '" + str(
                    #             lines.fiscal_year.date_end) + "' AND t12.name = '" + str(
                    #             lines.policy_status.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                         "t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #     if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    #         year = lines.fiscal_year.name
                    #         if lines.months == '01-01':
                    #             jan_start = str(end_year) + str(start_date)
                    #             jan_end = str(end_year) + str(end_date)
                    #
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(jan_start) + "' AND '" + str(
                    #                 jan_end) + "' AND t12.name = '" + str(
                    #                 lines.policy_status.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                             "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-02':
                    #             feb_start = str(end_year) + str(start_date)
                    #             feb_end = str(end_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(feb_start) + "' AND '" + str(
                    #                 feb_end) + "' AND t12.name = '" + str(
                    #                 lines.policy_status.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                             "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-03':
                    #             mar_start = str(end_year) + str(start_date)
                    #             mar_end = str(end_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(mar_start) + "' AND '" + str(
                    #                 mar_end) + "' AND t12.name = '" + str(
                    #                 lines.policy_status.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                             "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-04':
                    #             apr_start = str(start_year) + str(start_date)
                    #             apr_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(apr_start) + "' AND '" + str(
                    #                 apr_end) + "' AND t12.name = '" + str(
                    #                 lines.policy_status.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                             "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-05':
                    #             may_start = str(start_year) + str(start_date)
                    #             may_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(may_start) + "' AND '" + str(
                    #                 may_end) + "' AND t12.name = '" + str(
                    #                 lines.policy_status.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                             "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-06':
                    #             june_start = str(start_year) + str(start_date)
                    #             june_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(june_start) + "' AND '" + str(
                    #                 june_end) + "' AND t12.name = '" + str(
                    #                 lines.policy_status.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                             "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-07':
                    #             jul_start = str(start_year) + str(start_date)
                    #             jul_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(jul_start) + "' AND '" + str(
                    #                 jul_end) + "' AND t12.name = '" + str(
                    #                 lines.policy_status.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                             "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-08':
                    #             aug_start = str(start_year) + str(start_date)
                    #             aug_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(aug_start) + "' AND '" + str(
                    #                 aug_end) + "' AND t12.name = '" + str(
                    #                 lines.policy_status.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                             "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-09':
                    #             sep_start = str(start_year) + str(start_date)
                    #             sep_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(sep_start) + "' AND '" + str(
                    #                 sep_end) + "' AND t12.name = '" + str(
                    #                 lines.policy_status.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                             "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-10':
                    #             oct_start = str(start_year) + str(start_date)
                    #             oct_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(oct_start) + "' AND '" + str(
                    #                 oct_end) + "' AND t12.name = '" + str(
                    #                 lines.policy_status.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                             "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #         if lines.months == '01-11':
                    #             nov_start = str(start_year) + str(start_date)
                    #             nov_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(nov_start) + "' AND '" + str(
                    #                 nov_end) + "' AND t12.name = '" + str(
                    #                 lines.policy_status.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                             "t1.date2,t7.name,t8.name,t1.registername1,1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #         if lines.months == '01-12':
                    #             dec_start = str(start_year) + str(start_date)
                    #             dec_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(dec_start) + "' AND '" + str(
                    #                 dec_end) + "' AND t12.name = '" + str(
                    #                 lines.policy_status.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                      "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #     if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    #         query += " where " + str(dy_date) + "  BETWEEN '" + str(
                    #             lines.date_from + ' 00:00:00') + "' AND '" + str(
                    #             lines.date_to + ' 23:59:59') + "' AND t12.name = '" + str(
                    #             lines.policy_status.name) + "' group by t1.pipeline_id,t1.date2,t1.registername1,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t7.name,t8.name,t13.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #     cr.execute(query)
                    #     usr_detail = cr.dictfetchall()
                    # elif lines.filterby == "paymenttype":
                    #     if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    #         query += " where " + str(dy_date) + "  BETWEEN '" + str(
                    #             lines.fiscal_year.date_start) + "' AND '" + str(
                    #             lines.fiscal_year.date_end) + "' AND t13.name = '" + str(
                    #             lines.payment_type.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                        "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #     if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    #         year = lines.fiscal_year.name
                    #         if lines.months == '01-01':
                    #             jan_start = str(end_year) + str(start_date)
                    #             jan_end = str(end_year) + str(end_date)
                    #
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(jan_start) + "' AND '" + str(
                    #                 jan_end) + "' AND t13.name = '" + str(
                    #                 lines.payment_type.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-02':
                    #             feb_start = str(end_year) + str(start_date)
                    #             feb_end = str(end_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(feb_start) + "' AND '" + str(
                    #                 feb_end) + "' AND t13.name = '" + str(
                    #                 lines.payment_type.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-03':
                    #             mar_start = str(end_year) + str(start_date)
                    #             mar_end = str(end_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(mar_start) + "' AND '" + str(
                    #                 mar_end) + "' AND t13.name = '" + str(
                    #                 lines.payment_type.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-04':
                    #             apr_start = str(start_year) + str(start_date)
                    #             apr_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(apr_start) + "' AND '" + str(
                    #                 apr_end) + "' AND t13.name = '" + str(
                    #                 lines.payment_type.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-05':
                    #             may_start = str(start_year) + str(start_date)
                    #             may_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(may_start) + "' AND '" + str(
                    #                 may_end) + "' AND t13.name = '" + str(
                    #                 lines.payment_type.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-06':
                    #             june_start = str(start_year) + str(start_date)
                    #             june_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(june_start) + "' AND '" + str(
                    #                 june_end) + "' AND t13.name = '" + str(
                    #                 lines.payment_type.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-07':
                    #             jul_start = str(start_year) + str(start_date)
                    #             jul_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(jul_start) + "' AND '" + str(
                    #                 jul_end) + "' AND t13.name = '" + str(
                    #                 lines.payment_type.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-08':
                    #             aug_start = str(start_year) + str(start_date)
                    #             aug_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(aug_start) + "' AND '" + str(
                    #                 aug_end) + "' AND t13.name = '" + str(
                    #                 lines.payment_type.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-09':
                    #             sep_start = str(start_year) + str(start_date)
                    #             sep_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(sep_start) + "' AND '" + str(
                    #                 sep_end) + "' AND t13.name = '" + str(
                    #                 lines.payment_type.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-10':
                    #             oct_start = str(start_year) + str(start_date)
                    #             oct_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(oct_start) + "' AND '" + str(
                    #                 oct_end) + "' AND t13.name = '" + str(
                    #                 lines.payment_type.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #         if lines.months == '01-11':
                    #             nov_start = str(start_year) + str(start_date)
                    #             nov_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(nov_start) + "' AND '" + str(
                    #                 nov_end) + "' AND t13.name = '" + str(
                    #                 lines.payment_type.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #         if lines.months == '01-12':
                    #             dec_start = str(start_year) + str(start_date)
                    #             dec_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(dec_start) + "' AND '" + str(
                    #                 dec_end) + "' AND t13.name = '" + str(
                    #                 lines.payment_type.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                             "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #     if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    #         query += " where " + str(dy_date) + "  BETWEEN '" + str(
                    #             lines.date_from + ' 00:00:00') + "' AND '" + str(
                    #             lines.date_to + ' 23:59:59') + "' AND t13.name = '" + str(
                    #             lines.payment_type.name) + "' group by t1.pipeline_id,t1.date2,t1.registername1,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t7.name,t8.name,t13.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #     cr.execute(query)
                    #     usr_detail = cr.dictfetchall()
                    # elif lines.filterby == "salesperson":
                    #     if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    #         query += " where " + str(dy_date) + "  BETWEEN '" + str(
                    #             lines.fiscal_year.date_start) + "' AND '" + str(
                    #             lines.fiscal_year.date_end) + "' AND t17.name = '" + str(
                    #             lines.sales_person.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                        "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #     if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    #         year = lines.fiscal_year.name
                    #         if lines.months == '01-01':
                    #             jan_start = str(end_year) + str(start_date)
                    #             jan_end = str(end_year) + str(end_date)
                    #
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(jan_start) + "' AND '" + str(
                    #                 jan_end) + "' AND t17.name = '" + str(
                    #                 lines.sales_person.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-02':
                    #             feb_start = str(end_year) + str(start_date)
                    #             feb_end = str(end_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(feb_start) + "' AND '" + str(
                    #                 feb_end) + "' AND t17.name = '" + str(
                    #                 lines.sales_person.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-03':
                    #             mar_start = str(end_year) + str(start_date)
                    #             mar_end = str(end_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(mar_start) + "' AND '" + str(
                    #                 mar_end) + "' AND t17.name = '" + str(
                    #                 lines.sales_person.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-04':
                    #             apr_start = str(start_year) + str(start_date)
                    #             apr_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(apr_start) + "' AND '" + str(
                    #                 apr_end) + "' AND t17.name = '" + str(
                    #                 lines.sales_person.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-05':
                    #             may_start = str(start_year) + str(start_date)
                    #             may_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(may_start) + "' AND '" + str(
                    #                 may_end) + "' AND t17.name = '" + str(
                    #                 lines.sales_person.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-06':
                    #             june_start = str(start_year) + str(start_date)
                    #             june_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(june_start) + "' AND '" + str(
                    #                 june_end) + "' AND t17.name = '" + str(
                    #                 lines.sales_person.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-07':
                    #             jul_start = str(start_year) + str(start_date)
                    #             jul_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(jul_start) + "' AND '" + str(
                    #                 jul_end) + "' AND t17.name = '" + str(
                    #                 lines.sales_person.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-08':
                    #             aug_start = str(start_year) + str(start_date)
                    #             aug_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(aug_start) + "' AND '" + str(
                    #                 aug_end) + "' AND t17.name = '" + str(
                    #                 lines.sales_person.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-09':
                    #             sep_start = str(start_year) + str(start_date)
                    #             sep_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(sep_start) + "' AND '" + str(
                    #                 sep_end) + "' AND t17.name = '" + str(
                    #                 lines.sales_person.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #         if lines.months == '01-10':
                    #             oct_start = str(start_year) + str(start_date)
                    #             oct_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(oct_start) + "' AND '" + str(
                    #                 oct_end) + "' AND t17.name = '" + str(
                    #                 lines.sales_person.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #         if lines.months == '01-11':
                    #             nov_start = str(start_year) + str(start_date)
                    #             nov_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(nov_start) + "' AND '" + str(
                    #                 nov_end) + "' AND t17.name = '" + str(
                    #                 lines.sales_person.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.regsitersrno,t1.registersubno,t1.registername1,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #         if lines.months == '01-12':
                    #             dec_start = str(start_year) + str(start_date)
                    #             dec_end = str(start_year) + str(end_date)
                    #             query += " where " + str(dy_date) + "  BETWEEN '" + str(dec_start) + "' AND '" + str(
                    #                 dec_end) + "' AND t13.name = '" + str(
                    #                 lines.sales_person.name) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
                    #                                            "t1.date2,t7.name,t8.name,t1.registername1,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t13.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #     if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    #         query += " where " + str(dy_date) + "  BETWEEN '" + str(
                    #             lines.date_from + ' 00:00:00') + "' AND '" + str(
                    #             lines.date_to + ' 23:59:59') + "' AND t17.name = '" + str(
                    #             lines.sales_person.name) + "' group by t1.pipeline_id,t1.date2,t1.registername1,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t7.name,t8.name,t13.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno order by t3.name,t1.regsitersrno"
                    #
                    #     cr.execute(query)
                    #     usr_detail = cr.dictfetchall()
                    else:
                        if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                            if id != None and endo == 'Table1' and id is not False:
                                query += " where t9.endos_date BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' "
                            else:
                                query += " where " + str(dy_date) + "  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' "

                        if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                            year = lines.fiscal_year.name
                            if lines.months == '01-01':
                                jan_start = str(end_year) + str(start_date)
                                jan_end = str(end_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "' "

                            if lines.months == '01-02':
                                feb_start = str(end_year) + str(start_date)
                                feb_end = str(end_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(feb_start) + "' AND '" + str(
                                        feb_end) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        feb_start) + "' AND '" + str(feb_end) + "' "

                            if lines.months == '01-03':
                                mar_start = str(end_year) + str(start_date)
                                mar_end = str(end_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(mar_start) + "' AND '" + str(
                                        mar_end) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        mar_start) + "' AND '" + str(mar_end) + "' "
                            if lines.months == '01-04':
                                apr_start = str(start_year) + str(start_date)
                                apr_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(apr_start) + "' AND '" + str(
                                        apr_end) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        apr_start) + "' AND '" + str(apr_end) + "' "
                            if lines.months == '01-05':
                                may_start = str(start_year) + str(start_date)
                                may_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(may_start) + "' AND '" + str(
                                        may_end) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        may_start) + "' AND '" + str(may_end) + "' "
                            if lines.months == '01-06':
                                june_start = str(start_year) + str(start_date)
                                june_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(june_start) + "' AND '" + str(
                                        june_end) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        june_start) + "' AND '" + str(june_end) + "' "

                            if lines.months == '01-07':
                                jul_start = str(start_year) + str(start_date)
                                jul_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(jul_start) + "' AND '" + str(
                                        jul_end) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        jul_start) + "' AND '" + str(jul_end) + "' "

                            if lines.months == '01-08':
                                aug_start = str(start_year) + str(start_date)
                                aug_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(aug_start) + "' AND '" + str(
                                        aug_end) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        aug_start) + "' AND '" + str(aug_end) + "' "

                            if lines.months == '01-09':
                                sep_start = str(start_year) + str(start_date)
                                sep_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(sep_start) + "' AND '" + str(
                                        sep_end) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        sep_start) + "' AND '" + str(sep_end) + "' "
                            if lines.months == '01-10':
                                oct_start = str(start_year) + str(start_date)
                                oct_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(oct_start) + "' AND '" + str(
                                        oct_end) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        oct_start) + "' AND '" + str(oct_end) + "' "

                            if lines.months == '01-11':
                                nov_start = str(start_year) + str(start_date)
                                nov_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(nov_start) + "' AND '" + str(
                                        nov_end) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        nov_start) + "' AND '" + str(nov_end) + "' "

                            if lines.months == '01-12':
                                dec_start = str(start_year) + str(start_date)
                                dec_end = str(start_year) + str(end_date)
                                if id != None and endo == 'Table1' and id is not False:
                                    query += " where t9.endos_date BETWEEN '" + str(dec_start) + "' AND '" + str(
                                        dec_end) + "' "
                                else:
                                    query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                        dec_start) + "' AND '" + str(dec_end) + "' "

                        if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                            if id != None and endo == 'Table1' and id is not False:
                                query += " where t9.endos_date BETWEEN '" + str(
                                    lines.date_from + ' 00:00:00') + "' AND '" + str(
                                    lines.date_to + ' 23:59:59') + "'"
                            else:
                                query += " where " + str(dy_date) + "  BETWEEN '" + str(
                                    lines.date_from + ' 00:00:00') + "' AND '" + str(
                                    lines.date_to + ' 23:59:59') + "'"

                        if id != None and endo == 'Table1'  and  id is not False:
                            query += " and t9.endo_id= '" + str(id) + "' "
                        elif id != None and endo == 'Table2'  and  id is not False:
                            query += " and t20.co_insurer_id='" + str(id) + "' "


                        if id != None and endo == 'Table1'  and  id is not False:
                            if lines.location != 'all':
                                query+=" and t1.location = '" +str(lines.location)+"' group by t9.name,t9.endos_date,t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name," \
                                                               "t1.startfrom,t1.expiry,t11.name,t12.name,t9.endos_brokerage_premium,t1.policyno,t1.endo_ins,t1.coins,t1.id,t9.endos_date,t9.name,t9.endo_net,t9.endo_gst_gross,t9.endos_suminsured  order by t3.name,t1.regsitersrno"
                            else:
                                query += " group by t9.name,t9.endos_date,t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name," \
                                         "t1.startfrom,t1.expiry,t11.name,t12.name,t9.endos_brokerage_premium,t1.policyno,t1.endo_ins,t1.coins,t1.id,t9.endos_date,t9.name,t9.endo_net,t9.endo_gst_gross,t9.endos_suminsured  order by t3.name,t1.regsitersrno"

                        elif id != None and endo == 'Table2'  and  id is not False:
                            if lines.location != 'all':
                                query += " and t1.location = '" + str(lines.location) + "' group by t20.co_net_gross_pre,t20.co_net_premium,t20.co_sum_insured,t20.co_brokerage_pre,t20.co_share,t21.name,t1.pipeline_id,t1.sale_order_id,t3.name,t4.name,t5.name,t6.name,t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name," \
                                     "t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno,t1.endo_ins,t1.coins,t1.id,t1.tppremium,t1.terrprem,t1.stamprem order by t3.name,t1.regsitersrno"
                            else:
                                query+=" group by t20.co_net_gross_pre,t20.co_net_premium,t20.co_sum_insured,t20.co_brokerage_pre,t20.co_share,t21.name,t1.pipeline_id,t1.sale_order_id,t3.name,t4.name,t5.name,t6.name,t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name," \
                                     "t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno,t1.endo_ins,t1.coins,t1.id,t1.tppremium,t1.terrprem,t1.stamprem order by t3.name,t1.regsitersrno"
                        else:
                            if lines.location != 'all':
                                query += " and t1.location = '" + str(lines.location) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name," \
                                     " t1.startfrom,t1.expiry,t11.name,t12.name,t1.grossprem,t1.netprem,t1.brokerageprem,t1.policyno,t1.endo_ins,t1.coins,t1.id,t1.tppremium,t1.terrprem,t1.stamprem order by t3.name,t1.regsitersrno"
                            else:
                                query += " group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref,t13.name," \
                                     " t1.startfrom,t1.expiry,t11.name,t12.name,t1.grossprem,t1.netprem,t1.brokerageprem,t1.policyno,t1.endo_ins,t1.coins,t1.id,t1.tppremium,t1.terrprem,t1.stamprem order by t3.name,t1.regsitersrno"

                        print(query, "QUERY")
                        cr.execute(query)
                        
                        usr_detail = cr.dictfetchall()
                        return usr_detail



        def endos(self, workbook, data, lines,start_date,start_year,start_year1,end_date,end_year1,end_year):
            db_name = odoo.tools.config.get('db_name')
            registry = Registry(db_name)
            with registry.cursor() as cr:
                dy_date = ''
                if lines.groupby == 'create_date':
                    dy_date = 't1.date2'
                elif lines.groupby == 'proposaldate':
                    dy_date = 't1.proposaldate'
                elif lines.groupby == 'startdate':
                    dy_date = 't1.startfrom'
                else:
                    dy_date = 't1.date2'
                query ="select t9.endo_gst_amount as servicetaxamt,t9.endo_tp AS tp,t9.endo_terr AS tr,t9.endo_stamp AS ts," \
                       " t1.date2 as docketdate, t1.registersubno as registersubno," \
                       " t1.regsitersrno as srno,t1.name as docketno, t1.pipeline_id as pipelineno,t1.sale_order_id as quotationno," \
                       " t1.proposaldate as proposaldate,t17.name as salesperson, t1.ref as referby,  t1.startfrom as startdate,t1.expiry as enddate," \
                       " t8.name as location,t10.name as insurername,t3.name as registername, t11.name as clientname,t12.name as type, " \
                       " t1.policyno ,'' as mode1, t4.name as insurerbranch,t5.name as subcategory,t6.name as csc,t7.name as event, " \
                       " t1.registername1,t1.endo_ins,t1.coins,t1.id," \
                       " t9.endos_date,t9.endos_manual as endos_no,'' as share,t9.endo_net as netprem ," \
                       " t9.endo_gst_gross as grossprem,t9.endos_brokerage_premium as brokprem,t9.endos_suminsured as suminsured  from policytransaction as t1 " \
                       " left join res_partner as t10 on t10.id=t1.insurername123 " \
                       " left join res_partner as t11 on t11.id=t1.clientname " \
                       " left join subdata_subdata as t3 on t3.id=t1.registername1 " \
                       " left join subdata_subdata as t12 on t12.id=t1.type " \
                       " left join ptransaction1 as t15 on t15.name =t1.id and t15.pay_of_id='endo'" \
                       " left join subdata_subdata as t13 on t13.id=t15.mode1 " \
                       " left join res_users as t16 on t1.rm =t16.id " \
                       " left join res_partner as t17 on t16.partner_id=t17.id " \
                       " left join insurerbranch as t4 on t4.id=t1.insurerbranch " \
                       " left join subcategory_subcategory as t5 on t5.id=t1.name1 " \
                       " left join utm_medium as t6 on t6.id=t1.csc left join utm_source as t7 on t7.id=t1.event " \
                       " left join clickbima_clickbima as t8 on t8.id=t1.location " \
                       " left join endos_policy as t9  on t9.endo_id =t1.id "
                if lines.filterby == "registername":
                    if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                        query += " where t9.endos_date BETWEEN '" + str(
                            lines.fiscal_year.date_start) + "' AND '" + str(
                            lines.fiscal_year.date_end) + "' AND t3.name = '" + str(
                            lines.register_name.name) + "' "

                    if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                        year = lines.fiscal_year.name
                        if lines.months == '01-01':
                            jan_start = str(end_year) + str(start_date)
                            jan_end = str(end_year) + str(end_date)
                            query += " where t9.endos_date  BETWEEN '" + str(jan_start) + "' AND '" + str(
                                jan_end) + "' AND t3.name = '" + str(
                                lines.register_name.name) + "' "

                        if lines.months == '01-02':
                            feb_start = str(end_year) + str(start_date)
                            feb_end = str(end_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(feb_start) + "' AND '" + str(
                                feb_end) + "' AND t3.name = '" + str(
                                lines.register_name.name) + "' "


                        if lines.months == '01-03':
                            mar_start = str(end_year) + str(start_date)
                            mar_end = str(end_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(mar_start) + "' AND '" + str(
                                mar_end) + "' AND t3.name = '" + str(
                                lines.register_name.name) + "' "


                        if lines.months == '01-04':
                            apr_start = str(start_year) + str(start_date)
                            apr_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(apr_start) + "' AND '" + str(
                                apr_end) + "' AND t3.name = '" + str(
                                lines.register_name.name) + "' "


                        if lines.months == '01-05':
                            may_start = str(start_year) + str(start_date)
                            may_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(may_start) + "' AND '" + str(
                                may_end) + "' AND t3.name = '" + str(
                                lines.register_name.name) + "' "


                        if lines.months == '01-06':
                            june_start = str(start_year) + str(start_date)
                            june_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(june_start) + "' AND '" + str(
                                june_end) + "' AND t3.name = '" + str(
                                lines.register_name.name) + "' "



                        if lines.months == '01-07':
                            jul_start = str(start_year) + str(start_date)
                            jul_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(jul_start) + "' AND '" + str(
                                jul_end) + "' AND t3.name = '" + str(
                                lines.register_name.name) + "' "


                        if lines.months == '01-08':
                            aug_start = str(start_year) + str(start_date)
                            aug_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(aug_start) + "' AND '" + str(
                                aug_end) + "' AND t3.name = '" + str(
                                lines.register_name.name) + "' "

                        if lines.months == '01-09':
                            sep_start = str(start_year) + str(start_date)
                            sep_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(sep_start) + "' AND '" + str(
                                sep_end) + "' AND t3.name = '" + str(
                                lines.register_name.name) + "' "


                        if lines.months == '01-10':
                            oct_start = str(start_year) + str(start_date)
                            oct_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(oct_start) + "' AND '" + str(
                                oct_end) + "' AND t3.name = '" + str(
                                lines.register_name.name) + "' "


                        if lines.months == '01-11':
                            nov_start = str(start_year) + str(start_date)
                            nov_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(nov_start) + "' AND '" + str(
                                nov_end) + "' AND t3.name = '" + str(
                                lines.register_name.name) + "' "


                        if lines.months == '01-12':
                            dec_start = str(start_year) + str(start_date)
                            dec_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(dec_start) + "' AND '" + str(
                                dec_end) + "' AND t3.name = '" + str(
                                lines.register_name.name) + "' "


                    if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                        query += " where t9.endos_date BETWEEN '" + str(
                            lines.date_from + ' 00:00:00') + "' AND '" + str(
                            lines.date_to + ' 23:59:59') + "' AND t3.name = '" + str(
                            lines.register_name.name) + "'"


                    if lines.location != 'all':
                        query += " and t1.location = '" + str(lines.location) + "' group by t9.endo_gst_amount,t9.name,t9.endos_date,t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref," \
                                 " t1.startfrom,t1.expiry,t11.name,t12.name,t9.endos_brokerage_premium,t1.policyno,t1.endo_ins,t1.coins,t1.id,t9.endos_manual,t9.endo_net,t9.endos_suminsured ,t9.endo_gst_gross,t9.endo_tp,t9.endo_terr,t9.endo_stamp  order by t3.name,t1.regsitersrno"

                    else:
                        query += " group by t9.endo_gst_amount,t9.name,t9.endos_date,t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref," \
                                 " t1.startfrom,t1.expiry,t11.name,t12.name,t9.endos_brokerage_premium,t1.policyno,t1.endo_ins,t1.coins,t1.id,t9.endos_manual,t9.endo_net,t9.endos_suminsured ,t9.endo_gst_gross ,t9.endo_tp,t9.endo_terr,t9.endo_stamp order by t3.name,t1.regsitersrno"

                    cr.execute(query)
                    usr_detail = cr.dictfetchall()
                    
                    return usr_detail

                else:
                    if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                        query += " where t9.endos_date BETWEEN '" + str(
                            lines.fiscal_year.date_start) + "' AND '" + str(
                            lines.fiscal_year.date_end) + "'"

                    if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                        year = lines.fiscal_year.name
                        if lines.months == '01-01':
                            jan_start = str(end_year) + str(start_date)
                            jan_end = str(end_year) + str(end_date)
                            query += " where t9.endos_date  BETWEEN '" + str(jan_start) + "' AND '" + str(
                                jan_end) + "' "
                        if lines.months == '01-02':
                            feb_start = str(end_year) + str(start_date)
                            feb_end = str(end_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(feb_start) + "' AND '" + str(
                                feb_end) + "' "

                        if lines.months == '01-03':
                            mar_start = str(end_year) + str(start_date)
                            mar_end = str(end_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(mar_start) + "' AND '" + str(
                                mar_end) + "' "

                        if lines.months == '01-04':
                            apr_start = str(start_year) + str(start_date)
                            apr_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(apr_start) + "' AND '" + str(
                                apr_end) + "' "

                        if lines.months == '01-05':
                            may_start = str(start_year) + str(start_date)
                            may_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(may_start) + "' AND '" + str(
                                may_end) + "' "

                        if lines.months == '01-06':
                            june_start = str(start_year) + str(start_date)
                            june_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(june_start) + "' AND '" + str(
                                june_end) + "' "

                        if lines.months == '01-07':
                            jul_start = str(start_year) + str(start_date)
                            jul_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(jul_start) + "' AND '" + str(
                                jul_end) + "' "

                        if lines.months == '01-08':
                            aug_start = str(start_year) + str(start_date)
                            aug_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(aug_start) + "' AND '" + str(
                                aug_end) + "' "

                        if lines.months == '01-09':
                            sep_start = str(start_year) + str(start_date)
                            sep_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(sep_start) + "' AND '" + str(
                                sep_end) + "' "

                        if lines.months == '01-10':
                            oct_start = str(start_year) + str(start_date)
                            oct_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(oct_start) + "' AND '" + str(
                                oct_end) + "' "

                        if lines.months == '01-11':
                            nov_start = str(start_year) + str(start_date)
                            nov_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(nov_start) + "' AND '" + str(
                                nov_end) + "' "

                        if lines.months == '01-12':
                            dec_start = str(start_year) + str(start_date)
                            dec_end = str(start_year) + str(end_date)
                            query += " where t9.endos_date BETWEEN '" + str(dec_start) + "' AND '" + str(
                                dec_end) + "' "

                    if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                        query += " where t9.endos_date BETWEEN '" + str(
                            lines.date_from + ' 00:00:00') + "' AND '" + str(
                            lines.date_to + ' 23:59:59') + "' "

                    if lines.location != 'all':
                        query += " and t1.location = '" + str(lines.location) + "' group by t9.endo_gst_amount,t9.name,t9.endos_date,t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref," \
                             " t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno,t9.endos_brokerage_premium,t1.endo_ins,t1.coins,t1.id,t9.endos_manual,t9.endo_net,t9.endos_suminsured ,t9.endo_gst_gross,t9.endo_gst_gross ,t9.endo_tp,t9.endo_terr,t9.endo_stamp  order by t3.name,t1.regsitersrno"

                    else:
                        query += " group by t9.endo_gst_amount,t9.name,t9.endos_date,t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t1.date2,t7.name,t1.registername1,t8.name,t1.regsitersrno,t1.registersubno,t1.name,t1.proposaldate,t1.suminsured,t17.name,t1.ref," \
                             " t1.startfrom,t1.expiry,t11.name,t12.name,t1.policyno,t9.endos_brokerage_premium,t1.endo_ins,t1.coins,t1.id,t9.endos_manual,t9.endo_net,t9.endos_suminsured ,t9.endo_gst_gross,t9.endo_gst_gross ,t9.endo_tp,t9.endo_terr,t9.endo_stamp  order by t3.name,t1.regsitersrno"


                    cr.execute(query)
                    usr_detail = cr.dictfetchall()
                    return usr_detail












PartnerXlsx('report.clickbima.res_partner.xlsx', 'registerdetail.report')


