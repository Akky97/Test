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

class Idrageneralbusinessreport(models.TransientModel):
    _name = "idrageneralbusiness.report"
    _description = "IDRA General Business Report"

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    monthly = fields.Selection([ ('monthly', 'Monthly'), ('quatar', 'Quarterly'),('yearly', 'Yearly')], default='monthly',string="Period Type")
    quarter = fields.Selection([('q1', 'Quarter 1'), ('q2', 'Quarter 2'), ('q3', 'Quarter 3'), ('q4', 'Quarter 4')],
                               string='Quarter')
    groupby = fields.Selection([('create_date', 'All'), ('category', 'Category')],default='category', string="Group BY")
    filterby = fields.Selection([('all', 'All'),('category', 'Category')] , default='all', string="Filter BY")
    location = fields.Selection([('9', 'Chandigarh'), ('8', 'Ludhiana'), ('7', 'New Delhi'), ('all', 'All')],
                                default='all', string="Location")
    fiscal_year = fields.Many2one('fyyear',string="Financial Year", default=lambda self: self.env['fyyear'].search([('ex_active', '=',True)],limit=1).id)
    months = fields.Selection(
        [('01-01', 'January'), ('01-02', 'February'), ('01-03', 'March'), ('01-04', 'April'), ('01-05', 'May'),
         ('01-06', 'June'),
         ('01-07', 'July'), ('01-08', 'August'), ('01-09', 'September'), ('01-10', 'October'), ('01-11', 'November'),
         ('01-12', 'December')])
    category=fields.Many2one('category.category', string="Category")
    start_year = fields.Char()
    end_year = fields.Char()

    @api.multi
    @api.onchange('category')
    def _compute_category_id(self):
        cat_id = self.category.id



    import odoo
    import datetime
    now1 = datetime.datetime.now()

    @api.onchange('monthly','months','fiscal_year')
    def onchange_monthly(self):
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
        return self.env['report'].get_action(self, report_name='clickbima.general_report_excel.xlsx', data=data)


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




        filtname = ''
        if lines.filterby == 'all':
            filtname = 'All'
        elif lines.filterby == 'category':
            filtname = 'Category'
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
        report_head = 'Security Insurance Brokers(India) Private Limited'
        report_head1 = 'New Delhi-Nehru Place'
        sheet = workbook.add_worksheet(report_name[:31])


        merge_format = workbook.add_format(
            {'bold': 1, 'align': 'center', 'valign': 'vcenter', 'font_color': 'black'})
        merge_format1 = workbook.add_format(
            {'bold': 1, 'align': 'left', 'valign': 'vleft', 'border': 1, 'font_color': 'black'})
        bold = workbook.add_format({'border': 1, 'bold': True, 'align': 'left'})
        bold1 = workbook.add_format({'bold': True, 'border': 1, 'align': 'right'})
        bold2 = workbook.add_format({'bold': True, 'border': 1, 'align': 'center'})
        bold3 = workbook.add_format({'bold': True, 'align': 'right'})
        border = workbook.add_format({'border': 1, 'align': 'center'})
        border2 = workbook.add_format({'border': 1, 'align': 'right'})
        border1 = workbook.add_format({'border': 1, 'align': 'left', 'border': 1, 'align': 'left'})
        align_left = workbook.add_format({'align': 'left'})
        numbersformat = workbook.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'right'})
        report_head2 = 'General Business Report for the period of Proposal Start Date : ' + str(
            lines.date_from) + '  to End Date : ' + str(lines.date_to)
        report_head3 = 'Grouped By : Category     Filtered By : ' + str(filtname)
        sheet.write(0, 4, ('Printed On  ' + str(x.strftime("%x"))), merge_format)
        sheet.write(1, 0, (str(loc)), merge_format)
        sheet.write(1, 4, ('Page:1'), bold3)
        sheet.write(8, 0, ('Financial Year'), bold1)
        sheet.write(8, 1, (lines.fiscal_year.name), bold)
        sheet.write(8, 2, (' '), bold)
        sheet.write(8, 3, ('Period Type'), bold1)
        sheet.write(8, 4, (quat), bold)
        sheet.write(9, 0, (' '), bold)
        sheet.write(9, 1, (' '), bold)
        sheet.write(9, 2, (' '), bold)
        sheet.write(9, 3, (' '), bold)
        sheet.write(9, 4, (' '), bold)
        sheet.write(10, 0, ('Line of Business'), bold)
        sheet.write(10, 1, ('No of policies'), bold2)
        sheet.write(10, 2, ('Premium Amount'), bold1)
        sheet.write(10, 3, ('Brokerage Income'), bold1)
        sheet.write(10, 4, ('Brokerage %'), bold1)


        # increasing width of column
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)

        sheet.merge_range('A1:B1', report_head, merge_format)
        sheet.merge_range('A4:E4', report_head2, merge_format)
        sheet.merge_range('A5:E5', report_head3, merge_format)

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


        temp = []
        an_iterator12 = sorted(usr_detail, key=operator.itemgetter('categoryname'))
        an_iterator = itertools.groupby(an_iterator12, key=operator.itemgetter('categoryname'))

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
                    if totalprem !=0 and totalbrok !=0:
                        brokeragepercent = round(((totalbrok / totalprem) * 100), 2)
                    else:
                        pass

                temp.append({
                    "categoryname": i[0],
                    "total": totalpol,
                    "netprem": totalprem,
                    "commssionamt": totalbrok,
                    "brokeragepercent": brokeragepercent
                })



        row = 11
        policy_counts = 0
        premium_total = 0
        brok_total = 0
        s_no = 1
        for res in temp:
            policy_counts += res['total']
            premium_total += res['netprem']
            brok_total += res['commssionamt']
            sheet.write(row, 0, res['categoryname'], border1)
            sheet.write(row, 1, res['total'], border)
            sheet.write(row, 2, round(res['netprem']), border2)
            sheet.write(row, 3, round(res['commssionamt']), border2)
            sheet.write(row, 4, res['brokeragepercent'], numbersformat)

            row = row + 1
            s_no = s_no + 1
            print("Array printed for s.no :", s_no - 1)
        sheet.write(row, 0, ('Total'), bold)
        sheet.write(row, 1, policy_counts, bold2)
        sheet.write(row, 2, round(premium_total), bold1)
        sheet.write(row, 3, round(brok_total), bold1)
        sheet.write(row, 4, (' '), bold)

    # with registry.cursor() as cr:
            # query = " select t1.id,t2.endo_id,t3.co_insurer_id,count(t1.segment) as total ,t4.irda_cat as categoryname ," \
            #         " case when (t2.endo_id is not null and t3.co_insurer_id is null) then sum(t2.endo_net)" \
            #         " else case when (t3.co_insurer_id is not null and t2.endo_id is null) then sum(t3.co_brokerage_pre)" \
            #         " else case when (t3.co_insurer_id is null and t2.endo_id is null) then sum(t1.netprem)" \
            #         " else case when (t3.co_insurer_id is not null and t2.endo_id is not null) then sum(t2.endo_net + t3.co_brokerage_pre)" \
            #         " end end end end as netprem," \
            #         " case when (t2.endo_id is not null and t3.co_insurer_id is null) then sum(t2.endo_commission)" \
            #         " else case when (t3.co_insurer_id is not null and t2.endo_id is null) then sum(t3.co_commission_amount)" \
            #         " else case when (t3.co_insurer_id is null and t2.endo_id is null) then sum(t1.commssionamt)" \
            #         " else case when (t3.co_insurer_id is not null and t2.endo_id is not null) then sum(t2.endo_commission + t3.co_commission_amount)" \
            #         " end end end end as commssionamt" \
            #         " from policytransaction as t1 " \
            #         " left join co_insurer_policy as t3 on t3.co_insurer_id =t1.id AND t3.co_type='self'" \
            #         " left join endos_policy as t2 on t2.endo_id =t1.id " \
            #         " left join category_category as t4 on t4.id = t1.segment"


    def querys(self, workbook, data, lines,start_date,start_year,start_year1,end_date,end_year1,end_year,id=None,endo=None):
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

            if lines.filterby == 'all':
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t1.startfrom  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' "

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)

                        query += " where t1.startfrom  BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "'"

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(feb_start) + "' AND '" + str(feb_end) + "' "

                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(mar_start) + "' AND '" + str(mar_end) + "' "

                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(apr_start) + "' AND '" + str(apr_end) + "' "

                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(may_start) + "' AND '" + str(may_end) + "' "

                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(june_start) + "' AND '" + str(june_end) + "' "

                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(jul_start) + "' AND '" + str(jul_end) + "' "

                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(aug_start) + "' AND '" + str(aug_end) + "' "

                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(sep_start) + "' AND '" + str(sep_end) + "' "

                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(oct_start) + "' AND '" + str(oct_end) + "' "
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(nov_start) + "' AND '" + str(nov_end) + "' "
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(dec_start) + "' AND '" + str(dec_end) + "' "

                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t1.startfrom  BETWEEN '" + str(lines.date_from) + "' AND '" + str(
                        lines.date_to) + "' "

                if lines.location != 'all':
                    query += "and t1.location = '" +str(lines.location)+ "' group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                else:
                    query += " group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"

                print(query,"QQQQQQQQQQQQQQQQQQQQQQ")
                cr.execute(query)
                usr_detail = cr.dictfetchall()
                
                return usr_detail

            elif lines.filterby == 'category':

                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t1.startfrom  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "'  AND t4.name = '" + str(
                        lines.category.name) + "' "

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)

                        query += " where t1.startfrom  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "'  AND t4.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "'   AND t4.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "'   AND t4.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "'   AND t4.name = '" + str(
                            lines.category.name) + "' "

                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"

                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t1.startfrom  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "'  AND t4.name = '" + str(
                        lines.category.name) + "'"

                if lines.location != 'all':
                    query += " and t1.location = '"+str(lines.location)+ "' group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                else:
                    query += " group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                cr.execute(query)
                usr_detail = cr.dictfetchall()
                
                return usr_detail

            else:
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t1.startfrom  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' "

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)

                        query += " where t1.startfrom  BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "' "

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(feb_start) + "' AND '" + str(feb_end) + "' "

                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(mar_start) + "' AND '" + str(mar_end) + "'"

                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(apr_start) + "' AND '" + str(apr_end) + "' "

                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(may_start) + "' AND '" + str(may_end) + "' "

                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(june_start) + "' AND '" + str(june_end) + "' "

                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(jul_start) + "' AND '" + str(jul_end) + "' "

                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(aug_start) + "' AND '" + str(aug_end) + "' "

                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(sep_start) + "' AND '" + str(sep_end) + "' "

                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(oct_start) + "' AND '" + str(oct_end) + "' "
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(nov_start) + "' AND '" + str(nov_end) + "' "
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t1.startfrom  BETWEEN '" + str(dec_start) + "' AND '" + str(dec_end) + "' "

                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t1.startfrom  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "' "
                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "'group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                else:
                    query += " group by t3.co_insurer_id,t1.id,t3.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                
                return usr_detail

    def endos(self, workbook, data, lines, start_date, start_year, start_year1, end_date, end_year1, end_year, id=None,
              endo=None):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        with registry.cursor() as cr:
            query = " select t1.id,t2.endo_id,count(t1.segment) as total,t4.irda_cat as categoryname,sum(t2.endo_net) as netprem," \
                    " sum(t2.endo_commission) as commssionamt" \
                    " from policytransaction as t1" \
                    " left join endos_policy as t2 on t2.endo_id =t1.id" \
                    " left join category_category as t4 on t4.id = t1.segment"

            if lines.filterby == 'all':
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t2.endos_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' "

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)

                        query += " where t2.endos_date  BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "'"

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(feb_start) + "' AND '" + str(feb_end) + "' "

                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(mar_start) + "' AND '" + str(mar_end) + "' "

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
                        query += " where t1.startfrom  BETWEEN '" + str(jul_start) + "' AND '" + str(jul_end) + "' "

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
                    query += " where t2.endos_date  BETWEEN '" + str(lines.date_from) + "' AND '" + str(
                        lines.date_to) + "' "


                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "' and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                else:
                    query += " and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"

                print(query, "QQQQQQQQQQQQQQQQQQQQQQ")
                cr.execute(query)
                usr_detail = cr.dictfetchall()
                
                return usr_detail

            elif lines.filterby == 'category':

                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t2.endos_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "'  AND t4.name = '" + str(
                        lines.category.name) + "' "

                if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                    year = lines.fiscal_year.name
                    if lines.months == '01-01':
                        jan_start = str(end_year) + str(start_date)
                        jan_end = str(end_year) + str(end_date)

                        query += " where t2.endos_date  BETWEEN '" + str(jan_start) + "' AND '" + str(
                            jan_end) + "'  AND t4.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-02':
                        feb_start = str(end_year) + str(start_date)
                        feb_end = str(end_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(feb_start) + "' AND '" + str(
                            feb_end) + "'   AND t4.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-03':
                        mar_start = str(end_year) + str(start_date)
                        mar_end = str(end_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(mar_start) + "' AND '" + str(
                            mar_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-04':
                        apr_start = str(start_year) + str(start_date)
                        apr_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(apr_start) + "' AND '" + str(
                            apr_end) + "'   AND t4.name = '" + str(lines.category.name) + "' "

                    if lines.months == '01-05':
                        may_start = str(start_year) + str(start_date)
                        may_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(may_start) + "' AND '" + str(
                            may_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-06':
                        june_start = str(start_year) + str(start_date)
                        june_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(june_start) + "' AND '" + str(
                            june_end) + "'   AND t4.name = '" + str(
                            lines.category.name) + "' "

                    if lines.months == '01-07':
                        jul_start = str(start_year) + str(start_date)
                        jul_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(jul_start) + "' AND '" + str(
                            jul_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-08':
                        aug_start = str(start_year) + str(start_date)
                        aug_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(aug_start) + "' AND '" + str(
                            aug_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-09':
                        sep_start = str(start_year) + str(start_date)
                        sep_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(sep_start) + "' AND '" + str(
                            sep_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"

                    if lines.months == '01-10':
                        oct_start = str(start_year) + str(start_date)
                        oct_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(oct_start) + "' AND '" + str(
                            oct_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"
                    if lines.months == '01-11':
                        nov_start = str(start_year) + str(start_date)
                        nov_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(nov_start) + "' AND '" + str(
                            nov_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"
                    if lines.months == '01-12':
                        dec_start = str(start_year) + str(start_date)
                        dec_end = str(start_year) + str(end_date)
                        query += " where t2.endos_date  BETWEEN '" + str(dec_start) + "' AND '" + str(
                            dec_end) + "'   AND t4.name = '" + str(lines.category.name) + "'"

                if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                    query += " where t2.endos_date  BETWEEN '" + str(
                        lines.date_from + ' 00:00:00') + "' AND '" + str(
                        lines.date_to + ' 23:59:59') + "'  AND t4.name = '" + str(
                        lines.category.name) + "'"

                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "' and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                else:
                    query += " and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                
                return usr_detail

            else:
                if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                    query += " where t2.endos_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                        lines.fiscal_year.date_end) + "' "

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
                    query += " where t2.endos_date  BETWEEN '" + str(
                        lines.date_from + ' 00:00:00') + "' AND '" + str(lines.date_to + ' 23:59:59') + "' "

                if lines.location != 'all':
                    query += " and t1.location = '" + str(lines.location) + "' and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"
                else:
                    query += " and t2.endo_id is not null group by t2.endo_id,t1.id,t1.commssionamt,t1.netprem,t4.irda_cat order by t4.irda_cat desc"

                cr.execute(query)
                usr_detail = cr.dictfetchall()
                
                return usr_detail





GeneralXlsx('report.clickbima.general_report_excel.xlsx', 'idrageneralbusiness.report')

