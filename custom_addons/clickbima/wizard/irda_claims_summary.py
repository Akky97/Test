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

class Idrasummaryreport(models.TransientModel):
    _name = "irdaclaimssummary.report"
    _description = "IRDA Claims Summary Report"

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    monthly = fields.Selection([ ('monthly', 'Monthly'), ('quatar', 'Quarterly'),('yearly', 'Yearly')], default='monthly',string="Period Type")
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
        return self.env['report'].get_action(self, report_name='clickbima.irda_claims_summary.xlsx', data=data)


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
            query = "select count(t2.id) as count,sum(t2.claim_of_est_cause) as claim_amount from policytransaction as t1 "\
                    " left join claim_policy as t2 on t2.claim_id=t1.id "
            query2 = "select count(t2.id) as count2,sum(t2.claim_of_est_cause) as claim_amount2 " \
                     " from policytransaction as t1 " \
                     " left join claim_policy as t2 on t2.claim_id=t1.id "
            query1 = "select count(t2.id) as count1,sum(t2.claim_of_est_cause) as claim_amount1 " \
                     " from policytransaction as t1 " \
                     " left join claim_policy as t2 on t2.claim_id=t1.id "
            query3 = "select count(t2.id) as count3,sum(t2.claim_of_est_cause) as claim_amount3 from policytransaction as t1 " \
                     " left join claim_policy as t2 on t2.claim_id=t1.id "
            query4 = "select count(t2.id) as count4,sum(t2.claim_of_est_cause) as claim_amount4 from policytransaction as t1 " \
                     " left join claim_policy as t2 on t2.claim_id=t1.id "

            if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                query4 += " where t2.claim_date <= '" + str(lines.fiscal_year.date_end) + "' and t2.id  " \
                          " not in (select t2.id from policytransaction as t1 " \
                          " left join claim_policy as t2 on t2.claim_id =t1.id " \
                          " where  (t2.settle_date <= '" + str(lines.fiscal_year.date_end) + "' and " \
                          " (t2.settle_type =650 or t2.settle_type =651)) or " \
                          " (t2.settle_reputation_date <= '" + str(lines.fiscal_year.date_end) + "' and (t2.settle_type =644)))"

            if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                year = lines.fiscal_year.name
                if lines.months == '01-01':
                    jan_start = str(end_year) + str('-01-01')
                    jan_end = str(end_year) + str('-01-31')

                    query4 += " where t2.claim_date  <= '" + str(jan_end) + "'  and t2.id  not in (select t2.id from policytransaction as t1 " \
                                   " left join claim_policy as t2 on t2.claim_id =t1.id " \
                                   " where  (t2.settle_date <= '" + str(jan_end) + "'  and (t2.settle_type =650 or t2.settle_type =651)) or " \
                                   " (t2.settle_reputation_date <=  '" + str(jan_end) + "'  and (t2.settle_type =644)))"

                if lines.months == '01-02':
                    feb_start = str(end_year) + str('-02-01')
                    feb_end = str(end_year) + str('-02-28')
                    query4 += " where t2.claim_date  <= '" + str(feb_end) + "'  and t2.id  not in (select t2.id from policytransaction as t1 " \
                                   " left join claim_policy as t2 on t2.claim_id =t1.id " \
                                   " where  (t2.settle_date <= '" + str(feb_end) + "'  and (t2.settle_type =650 or t2.settle_type =651)) or " \
                                   " (t2.settle_reputation_date <=  '" + str(feb_end) + "'  and (t2.settle_type =644)))"
                if lines.months == '01-03':
                    mar_start = str(end_year) + str('-03-01')
                    mar_end = str(end_year) + str('-03-31')
                    query4 += " where t2.claim_date  <= '" + str(
                        mar_end) + "'  and t2.id  not in (select t2.id from policytransaction as t1 " \
                                   " left join claim_policy as t2 on t2.claim_id =t1.id " \
                                   " where  (t2.settle_date <= '" + str(
                        mar_end) + "'  and (t2.settle_type =650 or t2.settle_type =651)) or " \
                                   " (t2.settle_reputation_date <=  '" + str(mar_end) + "'  and (t2.settle_type =644)))"
                if lines.months == '01-04':
                    apr_start = str(start_year) + str('-04-01')
                    apr_end = str(start_year) + str('-04-30')
                    query4 += " where t2.claim_date  <= '" + str(apr_end) + "'  and t2.id  not in (select t2.id from policytransaction as t1 " \
                                   " left join claim_policy as t2 on t2.claim_id =t1.id " \
                                   " where  (t2.settle_date <= '" + str(
                        apr_end) + "'  and (t2.settle_type =650 or t2.settle_type =651)) or " \
                                   " (t2.settle_reputation_date <=  '" + str(apr_end) + "'  and (t2.settle_type =644)))"
                if lines.months == '01-05':
                    may_start = str(start_year) + str('-05-01')
                    may_end = str(start_year) + str('-05-31')
                    query4 += " where t2.claim_date  <= '" + str(
                        may_end) + "'  and t2.id  not in (select t2.id from policytransaction as t1 " \
                                   " left join claim_policy as t2 on t2.claim_id =t1.id " \
                                   " where  (t2.settle_date <= '" + str(
                        may_end) + "'  and (t2.settle_type =650 or t2.settle_type =651)) or " \
                                   " (t2.settle_reputation_date <=  '" + str(may_end) + "'  and (t2.settle_type =644)))"
                if lines.months == '01-06':
                    june_start = str(start_year) + str('-06-01')
                    june_end = str(start_year) + str('-06-30')
                    query4 += " where t2.claim_date  <= '" + str(
                        june_end) + "'  and t2.id  not in (select t2.id from policytransaction as t1 " \
                                   " left join claim_policy as t2 on t2.claim_id =t1.id " \
                                   " where  (t2.settle_date <= '" + str(
                        june_end) + "'  and (t2.settle_type =650 or t2.settle_type =651)) or " \
                                   " (t2.settle_reputation_date <=  '" + str(june_end) + "'  and (t2.settle_type =644)))"

                if lines.months == '01-07':
                    jul_start = str(start_year) + str('-07-01')
                    jul_end = str(start_year) + str('-07-31')
                    query4 += " where t2.claim_date  <= '" + str(
                        jul_end) + "'  and t2.id  not in (select t2.id from policytransaction as t1 " \
                                   " left join claim_policy as t2 on t2.claim_id =t1.id " \
                                   " where  (t2.settle_date <= '" + str(
                        jul_end) + "'  and (t2.settle_type =650 or t2.settle_type =651)) or " \
                                   " (t2.settle_reputation_date <=  '" + str(jul_end) + "'  and (t2.settle_type =644)))"
                if lines.months == '01-08':
                    aug_start = str(start_year) + str('-08-01')
                    aug_end = str(start_year) + str('-08-31')
                    query4 += " where t2.claim_date  <= '" + str(
                        aug_end) + "'  and t2.id  not in (select t2.id from policytransaction as t1 " \
                                   " left join claim_policy as t2 on t2.claim_id =t1.id " \
                                   " where  (t2.settle_date <= '" + str(
                        aug_end) + "'  and (t2.settle_type =650 or t2.settle_type =651)) or " \
                                   " (t2.settle_reputation_date <=  '" + str(aug_end) + "'  and (t2.settle_type =644)))"

                if lines.months == '01-09':
                    sep_start = str(start_year) + str('-09-01')
                    sep_end = str(start_year) + str('-09-30')
                    query4 += " where t2.claim_date  <= '" + str(
                        sep_end) + "'  and t2.id  not in (select t2.id from policytransaction as t1 " \
                                   " left join claim_policy as t2 on t2.claim_id =t1.id " \
                                   " where  (t2.settle_date <= '" + str(
                        sep_end) + "'  and (t2.settle_type =650 or t2.settle_type =651)) or " \
                                   " (t2.settle_reputation_date <=  '" + str(sep_end) + "'  and (t2.settle_type =644)))"
                if lines.months == '01-10':
                    oct_start = str(start_year) + str('-10-01')
                    oct_end = str(start_year) + str('-10-31')
                    query4 += " where t2.claim_date  <= '" + str(
                        oct_end) + "'  and t2.id  not in (select t2.id from policytransaction as t1 " \
                                   " left join claim_policy as t2 on t2.claim_id =t1.id " \
                                   " where  (t2.settle_date <= '" + str(
                        oct_end) + "'  and (t2.settle_type =650 or t2.settle_type =651)) or " \
                                   " (t2.settle_reputation_date <=  '" + str(oct_end) + "'  and (t2.settle_type =644)))"
                if lines.months == '01-11':
                    nov_start = str(start_year) + str('-11-01')
                    nov_end = str(start_year) + str('-11-30')
                    query4 += " where t2.claim_date  <= '" + str(
                        nov_end) + "'  and t2.id  not in (select t2.id from policytransaction as t1 " \
                                   " left join claim_policy as t2 on t2.claim_id =t1.id " \
                                   " where  (t2.settle_date <= '" + str(
                        nov_end) + "'  and (t2.settle_type =650 or t2.settle_type =651)) or " \
                                   " (t2.settle_reputation_date <=  '" + str(nov_end) + "'  and (t2.settle_type =644)))"

                if lines.months == '01-12':
                    dec_start = str(start_year) + str('-12-01')
                    dec_end = str(start_year) + str('-12-31')
                    query4 += " where t2.claim_date  <= '" + str(dec_end) + "'  and t2.id  not in (select t2.id from policytransaction as t1 " \
                          " left join claim_policy as t2 on t2.claim_id =t1.id " \
                          " where  (t2.settle_date <= '" + str(dec_end) + "'  and (t2.settle_type =650 or t2.settle_type =651)) or " \
                          " (t2.settle_reputation_date <=  '" + str(dec_end) + "'  and (t2.settle_type =644)))"

            if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                if lines.quarter == "q2" or lines.quarter == "q3" or lines.quarter == "q4" or lines.quarter == "q1":
                    query4 += " where t2.claim_date  <= '"  + str(lines.date_to) + "'  and t2.id  not in (select t2.id from policytransaction as t1 " \
                              " left join claim_policy as t2 on t2.claim_id =t1.id " \
                              " where  (t2.settle_date <= '" + str(lines.date_to) + "'  and (t2.settle_type =650 or t2.settle_type =651)) or " \
                              " (t2.settle_reputation_date <=  '" + str(lines.date_to) + "'  and (t2.settle_type =644)))"

            print(query4,"CLOSING QUERY")
            cr.execute(query4)
            usr_detail4 = cr.dictfetchall()
            


            if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                query3 += " where (t2.claim_date < '" + str(lines.fiscal_year.date_start) + "') and t2.id " \
                          " not in (select t2.id from policytransaction as t1  left join claim_policy as t2 on t2.claim_id =t1.id  where ((t2.settle_date < '" + str(lines.fiscal_year.date_start) + "' and (t2.settle_type =650 or t2.settle_type =651))" \
                          "  or  (t2.settle_reputation_date < '" + str(lines.fiscal_year.date_start) + "' and (t2.settle_type =644 ))))"

            if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                year = lines.fiscal_year.name
                if lines.months == '01-01':
                    jan_start = str(end_year) + str('-01-01')
                    jan_end = str(end_year) + str('-01-31')
                    query3 += " where t2.claim_date  <  '" + str(jan_start) + "' and t2.id " \
                          " not in (select t2.id from policytransaction as t1  left join claim_policy as t2 on t2.claim_id =t1.id  where ((t2.settle_date < '" + str(jan_start) + "' and (t2.settle_type =650 or t2.settle_type =651))" \
                          "  or  (t2.settle_reputation_date < '" + str(jan_start) + "' and (t2.settle_type =644 ))))"


                if lines.months == '01-02':
                    feb_start = str(end_year) + str('-02-01')
                    feb_end = str(end_year) + str('-02-28')
                    query3 += " where t2.claim_date  < '" + str(feb_start) + "' and t2.id " \
                          " not in (select t2.id from policytransaction as t1  left join claim_policy as t2 on t2.claim_id =t1.id  where ((t2.settle_date < '" + str(feb_start) + "' and (t2.settle_type =650 or t2.settle_type =651))" \
                          "  or  (t2.settle_reputation_date < '" + str(feb_start) + "' and (t2.settle_type =644 ))))"

                if lines.months == '01-03':
                    mar_start = str(end_year) + str('-03-01')
                    mar_end = str(end_year) + str('-03-31')
                    query3 += " where t2.claim_date  < '" + str(mar_start) + "' and t2.id " \
                          " not in (select t2.id from policytransaction as t1  left join claim_policy as t2 on t2.claim_id =t1.id  where ((t2.settle_date < '" + str(mar_start) + "' and (t2.settle_type =650 or t2.settle_type =651))" \
                          "  or  (t2.settle_reputation_date < '" + str(mar_start) + "' and (t2.settle_type =644 ))))"

                if lines.months == '01-04':
                    apr_start = str(start_year) + str('-04-01')
                    apr_end = str(start_year) + str('-04-30')
                    query3 += " where t2.claim_date  < '" + str(apr_start) + "' and t2.id " \
                          " not in (select t2.id from policytransaction as t1  left join claim_policy as t2 on t2.claim_id =t1.id  where ((t2.settle_date < '" + str(apr_start) + "' and (t2.settle_type =650 or t2.settle_type =651))" \
                          "  or  (t2.settle_reputation_date < '" + str(apr_start) + "' and (t2.settle_type =644 ))))"

                if lines.months == '01-05':
                    may_start = str(start_year) + str('-05-01')
                    may_end = str(start_year) + str('-05-31')
                    query3 += " where t2.claim_date  < '" + str(may_start) + "'  and t2.id " \
                          " not in (select t2.id from policytransaction as t1  left join claim_policy as t2 on t2.claim_id =t1.id  where ((t2.settle_date < '" + str(may_start) + "' and (t2.settle_type =650 or t2.settle_type =651))" \
                          "  or  (t2.settle_reputation_date < '" + str(may_start) + "' and (t2.settle_type =644 ))))"

                if lines.months == '01-06':
                    june_start = str(start_year) + str('-06-01')
                    june_end = str(start_year) + str('-06-30')
                    query3 += " where t2.claim_date < '" + str(june_start) + "'  and t2.id " \
                          " not in (select t2.id from policytransaction as t1  left join claim_policy as t2 on t2.claim_id =t1.id  where ((t2.settle_date < '" + str(june_start) + "' and (t2.settle_type =650 or t2.settle_type =651))" \
                          "  or  (t2.settle_reputation_date < '" + str(june_start) + "' and (t2.settle_type =644 ))))"

                if lines.months == '01-07':
                    jul_start = str(start_year) + str('-07-01')
                    jul_end = str(start_year) + str('-07-31')
                    query3 += " where t2.claim_date < '" + str(jul_start) + "' and t2.id " \
                          " not in (select t2.id from policytransaction as t1  left join claim_policy as t2 on t2.claim_id =t1.id  where ((t2.settle_date < '" + str(jul_start) + "' and (t2.settle_type =650 or t2.settle_type =651))" \
                          "  or  (t2.settle_reputation_date < '" + str(jul_start) + "' and (t2.settle_type =644 ))))"

                if lines.months == '01-08':
                    aug_start = str(start_year) + str('-08-01')
                    aug_end = str(start_year) + str('-08-31')
                    query3 += " where t2.claim_date  < '" + str(aug_start) + "' and t2.id " \
                          " not in (select t2.id from policytransaction as t1  left join claim_policy as t2 on t2.claim_id =t1.id  where ((t2.settle_date < '" + str(aug_start) + "' and (t2.settle_type =650 or t2.settle_type =651))" \
                          "  or  (t2.settle_reputation_date < '" + str(aug_start) + "' and (t2.settle_type =644 ))))"

                if lines.months == '01-09':
                    sep_start = str(start_year) + str('-09-01')
                    sep_end = str(start_year) + str('-09-30')
                    query3 += " where t2.claim_date < '" + str(sep_start) + "' and t2.id " \
                          " not in (select t2.id from policytransaction as t1  left join claim_policy as t2 on t2.claim_id =t1.id  where ((t2.settle_date < '" + str(sep_start) + "' and (t2.settle_type =650 or t2.settle_type =651))" \
                          "  or  (t2.settle_reputation_date < '" + str(sep_start) + "' and (t2.settle_type =644 ))))"

                if lines.months == '01-10':
                    oct_start = str(start_year) + str('-10-01')
                    oct_end = str(start_year) + str('-10-31')
                    query3 += " where t2.claim_date  < '" + str(oct_start) + "' and t2.id " \
                          " not in (select t2.id from policytransaction as t1  left join claim_policy as t2 on t2.claim_id =t1.id  where ((t2.settle_date < '" + str(oct_start) + "' and (t2.settle_type =650 or t2.settle_type =651))" \
                          "  or  (t2.settle_reputation_date < '" + str(oct_start) + "' and (t2.settle_type =644 ))))"
                if lines.months == '01-11':
                    nov_start = str(start_year) + str('-11-01')
                    nov_end = str(start_year) + str('-11-30')
                    query3 += " where t2.claim_date  < '" + str(nov_start) + "' and t2.id " \
                          " not in (select t2.id from policytransaction as t1  left join claim_policy as t2 on t2.claim_id =t1.id  where ((t2.settle_date < '" + str(nov_start) + "' and (t2.settle_type =650 or t2.settle_type =651))" \
                          "  or  (t2.settle_reputation_date < '" + str(nov_start) + "' and (t2.settle_type =644 ))))"
                if lines.months == '01-12':
                    dec_start = str(start_year) + str('-12-01')
                    dec_end = str(start_year) + str('-12-31')
                    query3 += " where t2.claim_date  < '" + str(dec_start) + "' and t2.id " \
                          " not in (select t2.id from policytransaction as t1  left join claim_policy as t2 on t2.claim_id =t1.id  where ((t2.settle_date < '" + str(dec_start) + "' and (t2.settle_type =650 or t2.settle_type =651))" \
                          "  or  (t2.settle_reputation_date < '" + str(dec_start) + "' and (t2.settle_type =644 ))))"

            if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                # if lines.quarter == "q1":
                #     query3 += " where t2.claim_date  < '" + str(lines.fiscal_year.date_start) +  "' AND  t2.id is not null "
                if lines.quarter == "q1" or lines.quarter == "q2" or lines.quarter == "q3" or lines.quarter == "q4":
                    query3+=" where (t2.claim_date < '" + str(lines.date_from) + "') and t2.id " \
                            " not in (select t2.id from policytransaction as t1 " \
                            " left join claim_policy as t2 on t2.claim_id =t1.id " \
                            " where ((t2.settle_date < '" + str(lines.date_from) + "' and (t2.settle_type =650 or t2.settle_type =651)) " \
                            " or  (t2.settle_reputation_date < '" + str(lines.date_from) + "' and (t2.settle_type =644 ))))"

            print (query3,"OPENING QUERYS>>>>>>>")
            cr.execute(query3)
            usr_detail3 = cr.dictfetchall()


            

            if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                query += " where t2.claim_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                    lines.fiscal_year.date_end) + "' AND t2.id is not null "

            if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                year = lines.fiscal_year.name
                if lines.months == '01-01':
                    jan_start = str(end_year) + str('-01-01')
                    jan_end = str(end_year) + str('-01-31')

                    query += " where t2.claim_date  BETWEEN '" + str(jan_start) + "' AND '" + str(
                        jan_end) + "' AND  t2.id is not null" \

                if lines.months == '01-02':
                    feb_start = str(end_year) + str('-02-01')
                    feb_end = str(end_year) + str('-02-28')
                    query += " where t2.claim_date  BETWEEN '" + str(feb_start) + "' AND '" + str(
                        feb_end) + "' AND  t2.id is not null"

                if lines.months == '01-03':
                    mar_start = str(end_year) + str('-03-01')
                    mar_end = str(end_year) + str('-03-31')
                    query += " where t2.claim_date  BETWEEN '" + str(mar_start) + "' AND '" + str(
                        mar_end) + "' AND  t2.id is not null"

                if lines.months == '01-04':
                    apr_start = str(start_year) + str('-04-01')
                    apr_end = str(start_year) + str('-04-30')
                    query += " where t2.claim_date  BETWEEN '" + str(apr_start) + "' AND '" + str(
                        apr_end) + "' AND  t2.id is not null"

                if lines.months == '01-05':
                    may_start = str(start_year) + str('-05-01')
                    may_end = str(start_year) + str('-05-31')
                    query += " where t2.claim_date  BETWEEN '" + str(may_start) + "' AND '" + str(
                        may_end) + "' AND t2.id is not null"

                if lines.months == '01-06':
                    june_start = str(start_year) + str('-06-01')
                    june_end = str(start_year) + str('-06-30')
                    query += " where t2.claim_date  BETWEEN '" + str(june_start) + "' AND '" + str(
                        june_end) + "' AND t2.id is not null"

                if lines.months == '01-07':
                    jul_start = str(start_year) + str('-07-01')
                    jul_end = str(start_year) + str('-07-31')
                    query += " where t2.claim_date  BETWEEN '" + str(jul_start) + "' AND '" + str(
                        jul_end) + "' AND  t2.id is not null"

                if lines.months == '01-08':
                    aug_start = str(start_year) + str('-08-01')
                    aug_end = str(start_year) + str('-08-31')
                    query += " where t2.claim_date  BETWEEN '" + str(aug_start) + "' AND '" + str(
                        aug_end) + "' AND  t2.id is not null"

                if lines.months == '01-09':
                    sep_start = str(start_year) + str('-09-01')
                    sep_end = str(start_year) + str('-09-30')
                    query += " where t2.claim_date  BETWEEN '" + str(sep_start) + "' AND '" + str(
                        sep_end) + "' AND  t2.id is not null"

                if lines.months == '01-10':
                    oct_start = str(start_year) + str('-10-01')
                    oct_end = str(start_year) + str('-10-31')
                    query += " where t2.claim_date  BETWEEN '" + str(oct_start) + "' AND '" + str(
                        oct_end) + "' AND  t2.id is not null"
                if lines.months == '01-11':
                    nov_start = str(start_year) + str('-11-01')
                    nov_end = str(start_year) + str('-11-30')
                    query += " where t2.claim_date  BETWEEN '" + str(nov_start) + "' AND '" + str(
                        nov_end) + "' AND  t2.id is not null"
                if lines.months == '01-12':
                    dec_start = str(start_year) + str('-12-01')
                    dec_end = str(start_year) + str('-12-31')
                    query += " where t2.claim_date  BETWEEN '" + str(dec_start) + "' AND '" + str(
                        dec_end) + "' AND  t2.id is not null"

            if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                query += " where t2.claim_date  BETWEEN '" + str(lines.date_from) + "' AND '" + str(
                    lines.date_to) + "' AND  t2.id is not null"

            print(query,"QUERYS11>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<")
            cr.execute(query)
            usr_detail = cr.dictfetchall()

            


            if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                query1 += " where t2.settle_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                    lines.fiscal_year.date_end) + "' AND t2.id is not null and (t2.settle_type = 651 or t2.settle_type = 650)"

            if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                year = lines.fiscal_year.name
                if lines.months == '01-01':
                    jan_start = str(end_year) + str('-01-01')
                    jan_end = str(end_year) + str('-01-31')

                    query1 += " where t2.settle_date  BETWEEN '" + str(jan_start) + "' AND '" + str(
                        jan_end) + "' AND  t2.id is not null and (t2.settle_type = 651 or t2.settle_type = 650)"

                if lines.months == '01-02':
                    feb_start = str(end_year) + str('-02-01')
                    feb_end = str(end_year) + str('-02-28')
                    query1 += " where t2.settle_date  BETWEEN '" + str(feb_start) + "' AND '" + str(
                        feb_end) + "' AND  t2.id is not null and (t2.settle_type = 651 or t2.settle_type = 650)"

                if lines.months == '01-03':
                    mar_start = str(end_year) + str('-03-01')
                    mar_end = str(end_year) + str('-03-31')
                    query1 += " where t2.settle_date  BETWEEN '" + str(mar_start) + "' AND '" + str(
                        mar_end) + "' AND  t2.id is not null and (t2.settle_type = 651 or t2.settle_type = 650)"

                if lines.months == '01-04':
                    apr_start = str(start_year) + str('-04-01')
                    apr_end = str(start_year) + str('-04-30')
                    query1 += " where t2.settle_date  BETWEEN '" + str(apr_start) + "' AND '" + str(
                        apr_end) + "' AND  t2.id is not null and (t2.settle_type = 651 or t2.settle_type = 650)"

                if lines.months == '01-05':
                    may_start = str(start_year) + str('-05-01')
                    may_end = str(start_year) + str('-05-31')
                    query1 += " where t2.settle_date  BETWEEN '" + str(may_start) + "' AND '" + str(
                        may_end) + "' AND t2.id is not null and (t2.settle_type = 651 or t2.settle_type = 650)"

                if lines.months == '01-06':
                    june_start = str(start_year) + str('-06-01')
                    june_end = str(start_year) + str('-06-30')
                    query1 += " where t2.settle_date  BETWEEN '" + str(june_start) + "' AND '" + str(
                        june_end) + "' AND t2.id is not null and (t2.settle_type = 651 or t2.settle_type = 650)"

                if lines.months == '01-07':
                    jul_start = str(start_year) + str('-07-01')
                    jul_end = str(start_year) + str('-07-31')
                    query1 += " where t2.settle_date  BETWEEN '" + str(jul_start) + "' AND '" + str(
                        jul_end) + "' AND  t2.id is not null and (t2.settle_type = 651 or t2.settle_type = 650)"

                if lines.months == '01-08':
                    aug_start = str(start_year) + str('-08-01')
                    aug_end = str(start_year) + str('-08-31')
                    query1 += " where t2.settle_date  BETWEEN '" + str(aug_start) + "' AND '" + str(
                        aug_end) + "' AND  t2.id is not null and (t2.settle_type = 651 or t2.settle_type = 650)"

                if lines.months == '01-09':
                    sep_start = str(start_year) + str('-09-01')
                    sep_end = str(start_year) + str('-09-30')
                    query1 += " where t2.settle_date  BETWEEN '" + str(sep_start) + "' AND '" + str(
                        sep_end) + "' AND  t2.id is not null and (t2.settle_type = 651 or t2.settle_type = 650)"

                if lines.months == '01-10':
                    oct_start = str(start_year) + str('-10-01')
                    oct_end = str(start_year) + str('-10-31')
                    query1 += " where t2.settle_date  BETWEEN '" + str(oct_start) + "' AND '" + str(
                        oct_end) + "' AND  t2.id is not null and (t2.settle_type = 651 or t2.settle_type = 650)"
                if lines.months == '01-11':
                    nov_start = str(start_year) + str('-11-01')
                    nov_end = str(start_year) + str('-11-30')
                    query1 += " where t2.settle_date  BETWEEN '" + str(nov_start) + "' AND '" + str(
                        nov_end) + "' AND  t2.id is not null and (t2.settle_type = 651 or t2.settle_type = 650)"
                if lines.months == '01-12':
                    dec_start = str(start_year) + str('-12-01')
                    dec_end = str(start_year) + str('-12-31')
                    query1 += " where t2.settle_date  BETWEEN '" + str(dec_start) + "' AND '" + str(
                        dec_end) + "' AND  t2.id is not null and (t2.settle_type = 651 or t2.settle_type = 650)"

            if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                query1 += " where t2.settle_date  BETWEEN '" + str(lines.date_from) + "' AND '" + str(
                    lines.date_to) + "' AND  t2.id is not null and (t2.settle_type = 651 or t2.settle_type = 650)"


            print(query1,"query111111")
            cr.execute(query1)
            usr_detail1 = cr.dictfetchall()


            if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                query2 += " where t2.settle_reputation_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                    lines.fiscal_year.date_end) + "' AND t2.id is not null and t2.settle_type = 644"

            if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                year = lines.fiscal_year.name
                if lines.months == '01-01':
                    jan_start = str(end_year) + str('-01-01')
                    jan_end = str(end_year) + str('-01-31')

                    query2 += " where t2.settle_reputation_date  BETWEEN '" + str(jan_start) + "' AND '" + str(
                        jan_end) + "' AND  t2.id is not null and t2.settle_type = 644"

                if lines.months == '01-02':
                    feb_start = str(end_year) + str('-02-01')
                    feb_end = str(end_year) + str('-02-28')
                    query2 += " where t2.settle_reputation_date BETWEEN '" + str(feb_start) + "' AND '" + str(
                        feb_end) + "' AND  t2.id is not null and t2.settle_type = 644"

                if lines.months == '01-03':
                    mar_start = str(end_year) + str('-03-01')
                    mar_end = str(end_year) + str('-03-31')
                    query2 += " where t2.settle_reputation_date  BETWEEN '" + str(mar_start) + "' AND '" + str(
                        mar_end) + "' AND  t2.id is not null and t2.settle_type = 644"

                if lines.months == '01-04':
                    apr_start = str(start_year) + str('-04-01')
                    apr_end = str(start_year) + str('-04-30')
                    query2 += " where t2.settle_reputation_date  BETWEEN '" + str(apr_start) + "' AND '" + str(
                        apr_end) + "' AND  t2.id is not null and t2.settle_type = 644"

                if lines.months == '01-05':
                    may_start = str(start_year) + str('-05-01')
                    may_end = str(start_year) + str('-05-31')
                    query2 += " where t2.settle_reputation_date  BETWEEN '" + str(may_start) + "' AND '" + str(
                        may_end) + "' AND t2.id is not null and t2.settle_type = 644"

                if lines.months == '01-06':
                    june_start = str(start_year) + str('-06-01')
                    june_end = str(start_year) + str('-06-30')
                    query2 += " where t2.settle_reputation_Date  BETWEEN '" + str(june_start) + "' AND '" + str(
                        june_end) + "' AND t2.id is not null and t2.settle_type = 644"

                if lines.months == '01-07':
                    jul_start = str(start_year) + str('-07-01')
                    jul_end = str(start_year) + str('-07-31')
                    query2 += " where t2.settle_reputation_date  BETWEEN '" + str(jul_start) + "' AND '" + str(
                        jul_end) + "' AND  t2.id is not null and t2.settle_type = 644"

                if lines.months == '01-08':
                    aug_start = str(start_year) + str('-08-01')
                    aug_end = str(start_year) + str('-08-31')
                    query2 += " where t2.settle_reputation_date  BETWEEN '" + str(aug_start) + "' AND '" + str(
                        aug_end) + "' AND  t2.id is not null and t2.settle_type = 644"

                if lines.months == '01-09':
                    sep_start = str(start_year) + str('-09-01')
                    sep_end = str(start_year) + str('-09-30')
                    query2 += " where t2.settle_reputation_date  BETWEEN '" + str(sep_start) + "' AND '" + str(
                        sep_end) + "' AND  t2.id is not null and t2.settle_type = 644"

                if lines.months == '01-10':
                    oct_start = str(start_year) + str('-10-01')
                    oct_end = str(start_year) + str('-10-31')
                    query2 += " where t2.settle_reputation_date  BETWEEN '" + str(oct_start) + "' AND '" + str(
                        oct_end) + "' AND  t2.id is not null and t2.settle_type = 644"
                if lines.months == '01-11':
                    nov_start = str(start_year) + str('-11-01')
                    nov_end = str(start_year) + str('-11-30')
                    query2 += " where t2.settle_reputation_date  BETWEEN '" + str(nov_start) + "' AND '" + str(
                        nov_end) + "' AND  t2.id is not null and t2.settle_type = 644"
                if lines.months == '01-12':
                    dec_start = str(start_year) + str('-12-01')
                    dec_end = str(start_year) + str('-12-31')
                    query2 += " where t2.settle_reputation_date  BETWEEN '" + str(dec_start) + "' AND '" + str(
                        dec_end) + "' AND  t2.id is not null and t2.settle_type = 644"

            if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                query2 += " where t2.settle_reputation_date  BETWEEN '" + str(lines.date_from) + "' AND '" + str(
                    lines.date_to) + "' AND  t2.id is not null and t2.settle_type = 644"

            cr.execute(query2)
            usr_detail2 = cr.dictfetchall()

            

        temp = []
        for i in usr_detail:
            val = {
                "count": i['count'],
                "claim_amount": i['claim_amount'],
            }
        temp.append(val)


        temp1 = []
        for i in usr_detail1:
            val = {
                "count1": i['count1'],
                "claim_amount1": i['claim_amount1'],
            }
        temp1.append(val)


        temp2 = []
        for i in usr_detail2:
            val = {
                "count2": i['count2'],
                "claim_amount2": i['claim_amount2'],
            }
        temp2.append(val)

        temp3 = []
        for i in usr_detail3:
            val = {
                "count3": i['count3'],
                "claim_amount3": i['claim_amount3'],
            }
        temp3.append(val)


        temp4 = []
        for i in usr_detail4:
            val = {
                "count4": i['count4'],
                "claim_amount4": i['claim_amount4'],
            }
        temp4.append(val)

        quat=''
        if lines.monthly=='yearly':
            quat = 'Financial Year (' + str(lines.fiscal_year.date_start) + ' to ' + str(lines.fiscal_year.date_end) + ')'
        elif lines.monthly=='quatar':
            if lines.quarter =='q1':
                q1_start = str('01-04-') + str(start_year)
                q1_end =  str('30-06-') + str(start_year)
                quat ='Quarter-1 (' + str(q1_start) + ' to ' + str(q1_end) + ')'
            if lines.quarter =='q2':
                q2_start = str('01-07-') + str(start_year)
                q2_end = str('30-09-') + str(start_year)
                quat='Quarter-2 (' + str(q2_start) + ' to ' + str(q2_end) + ')'
            if lines.quarter =='q3':
                q3_start = str('01-10-') + str(start_year)
                q3_end = str('31-12-') + str(start_year)
                quat='Quarter-3 (' + str(q3_start) + ' to ' + str(q3_end) + ')'
            if lines.quarter=='q4':
                q4_start = str('01-01-') + str(end_year)
                q4_end = str('31-03-') + str(end_year)
                quat='Quarter-4 ('  + str(q4_start) + ' to ' + str(q4_end) + ')'
        else:
            pass

        import datetime
        x = datetime.datetime.now()
        report_name = "sheet 1"
        # One sheet by partner
        sheet = workbook.add_worksheet(report_name[:31])

        merge_format = workbook.add_format(
            {'bold': 1, 'align': 'center', 'valign': 'vcenter', 'font_color': 'black'})
        bold = workbook.add_format({'border': 1, 'bold': True, 'align':'left'})
        bold_less = workbook.add_format({ 'bold': True, 'align':'left'})
        bold1 = workbook.add_format({'bold': True, 'align': 'right'})
        bold2 = workbook.add_format({'bold': True, 'align': 'center'})
        bold3 = workbook.add_format({'bold': True, 'align': 'center','border': 1})
        border = workbook.add_format({'border': 1, 'align':'right'})
        border2 = workbook.add_format({'num_format': '#,##0.00','border': 1, 'align':'right'})
        border1 = workbook.add_format({'border': 1, 'align': 'left'})
        align_right = workbook.add_format({'align': 'right','border':1, 'bold': True,})
        numbersformat = workbook.add_format({'num_format': '#,##0.00','border': 1, 'align':'right','bold': True})
        report_head = 'Claims Movement (From Policy Holders And Customers)'
        report_head1 = 'for Financial Year ' + str(lines.fiscal_year.name)
        report_head2= str(quat)
        report_head4='IRDA-Claims-Summary'
        report_head3 = 'Security Insurance Brokers (India) Private Limited'
        report_head6 = 'New Delhi-Nehru Place'
        sheet.write(1, 3, ('Printed On  ' + str(x.strftime("%x"))), bold1)
        sheet.write(10, 1, ('Particulars'), bold)
        sheet.write(10, 2, ('Number Of Claims'), bold3)
        sheet.write(10, 3, ('Claims Amount'), bold3)
        sheet.write(11, 1, ('Claims pending at the beginning of the year (' + str(lines.fiscal_year.date_start) + ')'), bold)
        sheet.write(12, 1, ('New Claims registered during the year'), border1)
        sheet.write(13, 1, ('Claims settled/closed during the year'), border1)
        sheet.write(14, 1, ('Claims rejected/withdrawn during the year'), border1)
        sheet.write(15, 1, ('Claims pending at the end of the year (' + str(lines.fiscal_year.date_end) + ')'), bold)

        # increasing width of column
        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 80)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)

        sheet.merge_range('B3:D3', report_head4, bold1)
        sheet.merge_range('B5:D5', report_head, bold2)
        sheet.merge_range('B6:D6', report_head1, bold2)
        sheet.merge_range('B8:D8', report_head2, bold2)
        sheet.merge_range('B2:C2', report_head6, bold_less)
        sheet.merge_range('B1:C1', report_head3, bold_less)



        # row = 11
        # s_no = 1
        count_0 = 0
        count_1 = 0
        count_2 = 0
        count_3 = 0
        claim_amount_0 = 0
        claim_amount_1 = 0
        claim_amount_2 = 0
        claim_amount_3 = 0
        for res in temp:
            sheet.write(12, 2, res['count'], border)
            count_0 = res['count']
            sheet.write(12, 3, res['claim_amount'], border2)
            claim_amount_0 = res['claim_amount']

        for res1 in temp1:
            sheet.write(13, 2, res1['count1'], border)
            count_1 = res1['count1']
            sheet.write(13, 3, res1['claim_amount1'], border2)
            claim_amount_1 = res1['claim_amount1']

        for res2 in temp2:
            sheet.write(14, 2, res2['count2'], border)
            count_2 = res2['count2']
            sheet.write(14, 3, res2['claim_amount2'], border2)
            claim_amount_2 = res2['claim_amount2']

        for res3 in temp3:
            sheet.write(11, 2, res3['count3'], align_right)
            count_3 = res3['count3']
            sheet.write(11, 3, res3['claim_amount3'],  numbersformat)
            claim_amount_3 = res3['claim_amount3']

        for res4 in temp4:
            sheet.write(15, 2, res4['count4'], align_right)
            sheet.write(15, 3, res4['claim_amount4'], numbersformat)


        # if claim_amount_0 == None or claim_amount_0 == False:
        #     claim_amount_0 = 0
        # if claim_amount_1 == None or claim_amount_1 == False:
        #     claim_amount_1 = 0
        # if claim_amount_2 == None or claim_amount_2 == False:
        #     claim_amount_2 = 0
        # if claim_amount_3 == None or claim_amount_3 == False:
        #     claim_amount_3 = 0
        # if count_0 == None or count_0 == False:
        #     count_0 = 0
        # if count_1 == None or count_1 == False:
        #     count_1 = 0
        # if count_2 == None or count_2 == False:
        #     count_2 = 0
        # if count_3 == None or count_3 == False:
        #     count_3 = 0
        # sheet.write(15, 2, (count_3 + count_0) - (count_1 + count_2), align_right)
        # sheet.write(15, 3, (claim_amount_3 + claim_amount_0) - (claim_amount_1 + claim_amount_2),  numbersformat)
        #     sheet.write(row, 2, res['netprem'], border2)
        #     sheet.write(row, 3, res['commssionamt'], border2)
        #     sheet.write(row, 4, res['brokeragepercent'],numbersformat)
        #

    print("Report Printed")


GeneralXlsx('report.clickbima.irda_claims_summary.xlsx', 'irdaclaimssummary.report')

