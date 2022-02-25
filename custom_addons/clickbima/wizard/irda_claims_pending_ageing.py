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

class Idrapendingreport(models.TransientModel):
    _name = "irdapending.report"
    _description = "IRDA Claims Pending Ageing Report"

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    monthly = fields.Selection([  ('quatar', 'Quarterly'),('yearly', 'Yearly')], default='yearly',string="Period Type")
    quarter = fields.Selection([('q1', 'Quarter 1'), ('q2', 'Quarter 2'), ('q3', 'Quarter 3'), ('q4', 'Quarter 4')],
                               string='Quarter')
    # groupby = fields.Selection([('create_date', 'All'), ('category', 'Category')],default='category', string="Group BY")
    # filterby = fields.Selection([('all', 'All'),('category', 'Category')] , default='all', string="Filter BY")
    fiscal_year = fields.Many2one('fyyear',string="Financial Year", default=lambda self: self.env['fyyear'].search([('ex_active', '=',True)],limit=1).id)
    months = fields.Selection(
        [('01-01', 'January'), ('01-02', 'February'), ('01-03', 'March'), ('01-04', 'April'), ('01-05', 'May'),
         ('01-06', 'June'),
         ('01-07', 'July'), ('01-08', 'August'), ('01-09', 'September'), ('01-10', 'October'), ('01-11', 'November'),
         ('01-12', 'December')])
    # category=fields.Many2one('category.category', string="Category")
    start_year = fields.Char()
    end_year = fields.Char()


    @api.onchange('fiscal_year')
    def onchange_monthly(self):
        import odoo
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
        else:
            pass

    @api.onchange('quarter', 'fiscal_year')
    def onchange_quarter(self):
        import odoo
        import datetime
        if self.quarter  and self.fiscal_year:
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
        return self.env['report'].get_action(self, report_name='clickbima.irda_claims_pending.xlsx', data=data)


from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
class GeneralXlsx(ReportXlsx):
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

        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)

        with registry.cursor() as cr:
            query = "select tab1.days,count(tab1.days) as num,sum(tab1.amount) as sum from ( " \

            if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar":
                query += " select DATE_PART('day','" + str(lines.fiscal_year.date_end) + "'::timestamp -  t2.claim_date::timestamp)," \
                         " case when DATE_PART('day','" + str(lines.fiscal_year.date_end) + "'::timestamp -  t2.claim_date::timestamp) <= 30 then 30 " \
                         " when DATE_PART('day','" + str(lines.fiscal_year.date_end) + "'::timestamp -  t2.claim_date::timestamp) between 31 and 90 then 90 " \
                         " when DATE_PART('day','" + str(lines.fiscal_year.date_end) + "'::timestamp -  t2.claim_date::timestamp) between 91 and 180 then 180 " \
                         " when DATE_PART('day','" + str(lines.fiscal_year.date_end) + "'::timestamp -  t2.claim_date::timestamp) between 181 and 365 then 365 " \
                         " when DATE_PART('day','" + str(lines.fiscal_year.date_end) + "'::timestamp -  t2.claim_date::timestamp) > 365 then 366 " \
                         " else 0 end as days, " \
                         " case when DATE_PART('day','" + str(lines.fiscal_year.date_end) + "'::timestamp -  t2.claim_date::timestamp) <= 30 then t2.claim_of_est_cause " \
                         " when DATE_PART('day','" + str(lines.fiscal_year.date_end) + "'::timestamp -  t2.claim_date::timestamp) between 31 and 90 then t2.claim_of_est_cause " \
                         " when DATE_PART('day','" + str(lines.fiscal_year.date_end) + "'::timestamp -  t2.claim_date::timestamp) between 91 and 180 then t2.claim_of_est_cause " \
                         " when DATE_PART('day','" + str(lines.fiscal_year.date_end) + "'::timestamp -  t2.claim_date::timestamp) between 181 and 365 then t2.claim_of_est_cause " \
                         " when DATE_PART('day','" + str(lines.fiscal_year.date_end) + "'::timestamp -  t2.claim_date::timestamp) > 365 then t2.claim_of_est_cause " \
                         " else 0 end as amount " \
                         " from policytransaction as t1 " \
                         " left join claim_policy as t2 on t2.claim_id =t1.id " \
                         " where  ('" + str(lines.fiscal_year.date_end) + "'  >=  t2.claim_date or '" + str(lines.fiscal_year.date_end) + "' >= t2.settle_date or '" + str(lines.fiscal_year.date_end) + "' >= t2.settle_reputation_date ) "

                query += " and t2.id not in (select t2.id from policytransaction as t1 " \
                         " left join claim_policy as t2 on   t2.claim_id=t1.id " \
                         " where t2.settle_date  <= '" + str(lines.fiscal_year.date_end) + "' AND  t1.id is  not null " \
                         " and (t2.settle_type = 651 or t2.settle_type = 650) " \
                         " or  (t2.settle_reputation_date < '" + str(lines.fiscal_year.date_end) + "' and (t2.settle_type =644 )" \
                         " ))) as tab1 group by tab1.days"
            if lines.quarter and not lines.monthly == 'yearly':
                if lines.quarter == "q2" or lines.quarter == "q3" or lines.quarter == "q4" or lines.quarter == "q1":
                    query += "select DATE_PART('day','" + str(lines.date_to) + "'::timestamp -  t2.claim_date::timestamp)," \
                             " case when DATE_PART('day','" + str(lines.date_to) + "'::timestamp -  t2.claim_date::timestamp) <= 30 then 30 " \
                             " when DATE_PART('day','" + str(lines.date_to) + "'::timestamp -  t2.claim_date::timestamp) between 31 and 90 then 90 " \
                             " when DATE_PART('day','" + str(lines.date_to) + "'::timestamp -  t2.claim_date::timestamp) between 91 and 180 then 180 " \
                             " when DATE_PART('day','" + str(lines.date_to) + "'::timestamp -  t2.claim_date::timestamp) between 181 and 365 then 365 " \
                             " when DATE_PART('day','" + str(lines.date_to) + "'::timestamp -  t2.claim_date::timestamp) > 365 then 366 " \
                             " else 0 end as days, " \
                             " case when DATE_PART('day','" + str(lines.date_to) + "'::timestamp -  t2.claim_date::timestamp) <= 30 then t2.claim_of_est_cause " \
                             " when DATE_PART('day','" + str(lines.date_to) + "'::timestamp -  t2.claim_date::timestamp) between 31 and 90 then t2.claim_of_est_cause " \
                             " when DATE_PART('day','" + str(lines.date_to) + "'::timestamp -  t2.claim_date::timestamp) between 91 and 180 then t2.claim_of_est_cause " \
                             " when DATE_PART('day','" + str(lines.date_to) + "'::timestamp -  t2.claim_date::timestamp) between 181 and 365 then t2.claim_of_est_cause " \
                             " when DATE_PART('day','" + str(lines.date_to) + "'::timestamp -  t2.claim_date::timestamp) < 365 then t2.claim_of_est_cause " \
                             " else 0 end as amount " \
                             " from policytransaction as t1 " \
                             " left join claim_policy as t2 on t2.claim_id =t1.id " \
                             " where  ('" + str(lines.date_to) + "'  >=  t2.claim_date or '" + str(lines.date_to) + "' >= t2.settle_date " \
                             " or '" + str(lines.date_to) + "' >= t2.settle_reputation_date ) "

                    query += " and t2.id not in (select t2.id from policytransaction as t1 " \
                             " left join claim_policy as t2 on   t2.claim_id=t1.id " \
                             " where t2.settle_date  <= '" + str(lines.date_to) + "' AND  t1.id is  not null " \
                             " and (t2.settle_type = 651 or t2.settle_type = 650) " \
                             " or  (t2.settle_reputation_date < '" + str(lines.date_to) + "' and (t2.settle_type =644 )" \
                             " ))) as tab1 group by tab1.days"
            cr.execute(query)
            print(query,"QQQQQQQQQQQQQQQQQQQQQQQQQQQ")
            usr_detail = cr.dictfetchall()
            

        temp = []
        l1 = [30, 90, 180, 365, 366]
        l3=[]
        for i in usr_detail:
            l3.append(i['days'])
            temp.append({"days":i['days'],"amount":i['sum'],"count":i['num']})
        res = [x for x in l1 + l3 if x not in l1 or x not in l3]
        for j in res:
            temp.append({"days":j, "amount":0, "count":0})

        quat = ''
        if lines.monthly == 'yearly':
            quat = 'Financial Year (' + str(lines.fiscal_year.date_start) + ' to ' + str(
                lines.fiscal_year.date_end) + ')'
        elif lines.monthly == 'quatar':
            if lines.quarter == 'q1':
                q1_start = str('01-04-') + str(start_year)
                q1_end = str('30-06-') + str(start_year)
                quat = 'Quarter-1 (' + str(q1_start) + ' to ' + str(q1_end) + ')'
            if lines.quarter == 'q2':
                q2_start = str('01-07-') + str(start_year)
                q2_end = str('30-09-') + str(start_year)
                quat = 'Quarter-2 (' + str(q2_start) + ' to ' + str(q2_end) + ')'
            if lines.quarter == 'q3':
                q3_start = str('01-10-') + str(start_year)
                q3_end = str('31-12-') + str(start_year)
                quat = 'Quarter-3 (' + str(q3_start) + ' to ' + str(q3_end) + ')'
            if lines.quarter == 'q4':
                q4_start = str('01-01-') + str(end_year)
                q4_end = str('31-03-') + str(end_year)
                quat = 'Quarter-4 (' + str(q4_start) + ' to ' + str(q4_end) + ')'
        else:
            pass

        import datetime
        x = datetime.datetime.now()
        report_name = "sheet 1"
        # One sheet by partner
        sheet = workbook.add_worksheet(report_name[:31])


        merge_format = workbook.add_format({'bold': 1, 'align': 'center', 'valign': 'vcenter', 'font_color': 'black'})
        bold = workbook.add_format({'border': 1, 'bold': True, 'align': 'left'})
        bold1 = workbook.add_format({'bold': True, 'align': 'right'})
        bold2 = workbook.add_format({'bold': True, 'align': 'center'})
        align_right = workbook.add_format({'align': 'right', 'bold': True, })
        bold_less = workbook.add_format({'bold': True, 'align': 'left'})
        bold3 = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
        border = workbook.add_format({'border': 1, 'align': 'right'})
        border2 = workbook.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'right'})
        border1 = workbook.add_format({'border': 1, 'align': 'left'})
        align_left = workbook.add_format({'align': 'left'})
        numbersformat = workbook.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'right', 'bold': True})
        report_head = 'Ageing of Pending claims (From Policy Holders And Customers)'
        report_head1 = 'for Financial Year ' + str(lines.fiscal_year.name)
        report_head2 = str(quat)
        report_head3 = 'Total'
        report_head4 = 'IRDA-Claims-Pending'
        report_head5 = 'Security Insurance Brokers (India) Private Limited'
        report_head6 = 'New Delhi-Nehru Place'
        sheet.write(1, 3, ('Printed On  ' + str(x.strftime("%x"))), align_right)
        sheet.write(9, 1, (' '), bold)
        sheet.write(10, 1, ('Pending claims ageing buckets'), bold)
        sheet.write(10, 2, ('Number Of Claims'), bold3)
        sheet.write(10, 3, ('Claims Amount'), bold3)
        sheet.write(11, 1, ('Pending for upto 1 month'), border1)
        sheet.write(12, 1, ('Pending for greater than 1 month and upto 3 months'), border1)
        sheet.write(13, 1, ('Pending for greater than 3 month and upto 6 months'), border1)
        sheet.write(14, 1, ('Pending for greater than 6 month and upto 12 months'), border1)
        sheet.write(15, 1, ('Pending for more than 1 year'), border1)
        sheet.write(16, 1, ('Total Pending As on '+ str(lines.fiscal_year.date_end)), bold)
        # increasing width of column
        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 80)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)

        sheet.merge_range('B3:D3', report_head4, bold1)
        sheet.merge_range('B4:D4', report_head, bold2)
        sheet.merge_range('B5:D5', report_head1, bold2)
        sheet.merge_range('B7:D7', report_head2, bold2)
        sheet.merge_range('C10:D10', report_head3, bold3)
        sheet.merge_range('B2:C2', report_head6, bold_less)
        sheet.merge_range('B1:C1', report_head5, bold_less)

        total_count = 0
        total_amount = 0
        amount=0
        for res in temp:
            if res['amount'] ==None or res['amount'] =='':
                amount=0
            else:
                amount=res['amount']
            if res['days'] ==30:
                total_count += res['count']
                total_amount += amount
                sheet.write(11, 2, res['count'], border)
                sheet.write(11, 3, amount, border2)
            if res['days'] ==90:
                total_count += res['count']
                total_amount += amount
                sheet.write(12, 2, res['count'], border)
                sheet.write(12, 3, amount, border2)
            if res['days'] ==180:
                total_count += res['count']
                total_amount += amount
                sheet.write(13, 2, res['count'], border)
                sheet.write(13, 3, amount, border2)
            if res['days'] ==365:
                total_count += res['count']
                total_amount += amount
                sheet.write(14, 2, res['count'], border)
                sheet.write(14, 3, amount, border2)
            if res['days'] ==366:
                total_count += res['count']
                total_amount += amount
                sheet.write(15, 2, res['count'], border)
                sheet.write(15, 3, amount, border2)

        sheet.write(16, 2, total_count, border)
        sheet.write(16, 3, total_amount, border2)



GeneralXlsx('report.clickbima.irda_claims_pending.xlsx', 'irdapending.report')

