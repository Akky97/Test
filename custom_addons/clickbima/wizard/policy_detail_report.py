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


class Policydetailreport(models.TransientModel):
    _name = "policydetail.report"
    _description = "Policy Detail Report"

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    monthly = fields.Selection([('monthly', 'Monthly'), ('quatar', 'Quarterly'), ('yearly', 'Yearly')],
                               default='monthly', string='Period Type')
    quarter = fields.Selection([('q1', 'Quarter 1'), ('q2', 'Quarter 2'), ('q3', 'Quarter 3'), ('q4', 'Quarter 4')],
                               string='Quarter')
    groupby = fields.Selection([('create_date', 'All'), ('individual', 'Individual'),('company', 'Company')],default='create_date', string="Group BY")
    filterby = fields.Selection([('all', 'All'),('client', 'Client'), ('group', 'Group'),('individual_client','Individual Client'),('individual_group','Individual Group')] , default='all', string="Filter BY")
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
        return self.env['report'].get_action(self, report_name='clickbima.policy_detail.xlsx', data=data)


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

            query4 =" select t1.id,t2.claim_of_est_cause as amount," \
                    " t1.name as docket_number,t3.name as ticket_number , " \
                    " to_char(t2.claim_date_int, 'dd-mm-yyyy') as create_date,t1.name as docket_number,COALESCE(t2.claim_manual,'') as claim_manual, " \
                    " COALESCE(t4.name,'') as insured_name,COALESCE(t5.name,'') as patient_name,COALESCE(t6.name,'') as insurer_name " \
                    " ,COALESCE(t2.policy_pol_no,'') as policy_number,COALESCE(t7.name,'') as policy_tpa,COALESCE(t2.claim_brief,'') as claim_brief" \
                    " ,t2.claim_date,t2.claim_of_est_cause as claim_cause,t2.claim_amount,to_char(t2.settle_date, 'dd-mm-yyyy') as settle_date" \
                    " ,COALESCE(t8.name,'') as settle_type,COALESCE(t3.x_reply,'') as reply ,t2.settle_amount, " \
                    " COALESCE(t10.name,'') as claim_sub_status,COALESCE(t9.name,'') as claim_status, COALESCE(t1.group,'')as group,COALESCE(t2.location,'') as location, " \
                    " COALESCE(t12.name,'') as contact_person,COALESCE(t14.name,'') as scheme_name,COALESCE(t15.name,'') as surveyer_name ,t2.claim_of_admiss as claim_of_admiss," \
                    " to_char(t2.settle_reputation_date, 'dd-mm-yyyy') as settle_reputation_date,t16.name as client" \
                    " from policytransaction as t1 " \
                    " left join claim_policy as t2 on t2.claim_id =t1.id " \
                    " left join  project_issue as t3 on t3.id =t2.claim_ticket " \
                    " left join res_partner as t4 on t2.policy_insured_name =t4.id " \
                    " left join res_partner as t5 on t2.policy_patient_name =t5.id " \
                    " left join res_partner as t6 on t2.policy_insurer_name =t6.id " \
                    " left join res_partner as t7 on t2.policy_tpa =t7.id " \
                    " left join subdata_subdata as t8 on t2.settle_type =t8.id " \
                    " left join subdata_subdata as t9 on t3.x_claim_status =t9.id " \
                    " left join infosubdatadropdown as t10 on t3.x_claim_sub_status =t10.id " \
                    " left join clickbima_clickbima as t11 on t1.location =t11.id " \
                    " left join res_partner as t12 on t2.policy_contact_person =t12.id " \
                    " left join product_product as t13 on t2.policy_scheme =t13.id " \
                    " left join product_template as t14 on t13.product_tmpl_id=t14.id " \
                    " left join res_partner as t15 on t2.policy_surveyer_name =t15.id " \
                    " left join res_partner as t16 on t1.clientname =t16.id "

            query3 = " select t1.id,t2.claim_of_est_cause as amount," \
                    " t1.name as docket_number,t3.name as ticket_number , " \
                    " to_char(t2.claim_date_int, 'dd-mm-yyyy') as create_date,t1.name as docket_number,COALESCE(t2.claim_manual,'') as claim_manual, " \
                    " COALESCE(t4.name,'') as insured_name,COALESCE(t5.name,'') as patient_name,COALESCE(t6.name,'') as insurer_name " \
                    " ,COALESCE(t2.policy_pol_no,'') as policy_number,COALESCE(t7.name,'') as policy_tpa,COALESCE(t2.claim_brief,'') as claim_brief" \
                    " ,t2.claim_date,t2.claim_of_est_cause as claim_cause,t2.claim_amount,to_char(t2.settle_date, 'dd-mm-yyyy') as settle_date" \
                    " ,COALESCE(t8.name,'') as settle_type,COALESCE(t3.x_reply,'') as reply ,t2.settle_amount, " \
                    " COALESCE(t10.name,'') as claim_sub_status,COALESCE(t9.name,'') as claim_status, COALESCE(t1.group,'')as group,COALESCE(t2.location,'') as location, " \
                    " COALESCE(t12.name,'') as contact_person,COALESCE(t14.name,'') as scheme_name,COALESCE(t15.name,'') as surveyer_name ,t2.claim_of_admiss as claim_of_admiss," \
                    " to_char(t2.settle_reputation_date, 'dd-mm-yyyy') as settle_reputation_date,t16.name as client" \
                    " from policytransaction as t1 " \
                    " left join claim_policy as t2 on t2.claim_id =t1.id " \
                    " left join  project_issue as t3 on t3.id =t2.claim_ticket " \
                    " left join res_partner as t4 on t2.policy_insured_name =t4.id " \
                    " left join res_partner as t5 on t2.policy_patient_name =t5.id " \
                    " left join res_partner as t6 on t2.policy_insurer_name =t6.id " \
                    " left join res_partner as t7 on t2.policy_tpa =t7.id " \
                    " left join subdata_subdata as t8 on t2.settle_type =t8.id " \
                    " left join subdata_subdata as t9 on t3.x_claim_status =t9.id " \
                    " left join infosubdatadropdown as t10 on t3.x_claim_sub_status =t10.id " \
                    " left join clickbima_clickbima as t11 on t1.location =t11.id " \
                    " left join res_partner as t12 on t2.policy_contact_person =t12.id " \
                    " left join product_product as t13 on t2.policy_scheme =t13.id " \
                    " left join product_template as t14 on t13.product_tmpl_id=t14.id " \
                    " left join res_partner as t15 on t2.policy_surveyer_name =t15.id " \
                    " left join res_partner as t16 on t1.clientname =t16.id "

            query2 = " select t1.id,t2.claim_of_est_cause as amount," \
                    " t1.name as docket_number,t3.name as ticket_number , " \
                    " to_char(t2.claim_date_int, 'dd-mm-yyyy') as create_date,t1.name as docket_number,COALESCE(t2.claim_manual,'') as claim_manual, " \
                    " COALESCE(t4.name,'') as insured_name,COALESCE(t5.name,'') as patient_name,COALESCE(t6.name,'') as insurer_name " \
                    " ,COALESCE(t2.policy_pol_no,'') as policy_number,COALESCE(t7.name,'') as policy_tpa,COALESCE(t2.claim_brief,'') as claim_brief" \
                    " ,t2.claim_date,t2.claim_of_est_cause as claim_cause,t2.claim_amount,to_char(t2.settle_date, 'dd-mm-yyyy') as settle_date" \
                    " ,COALESCE(t8.name,'') as settle_type,COALESCE(t3.x_reply,'') as reply ,t2.settle_amount, " \
                    " COALESCE(t10.name,'') as claim_sub_status,COALESCE(t9.name,'') as claim_status, COALESCE(t1.group,'')as group,COALESCE(t2.location,'') as location, " \
                    " COALESCE(t12.name,'') as contact_person,COALESCE(t14.name,'') as scheme_name,COALESCE(t15.name,'') as surveyer_name ,t2.claim_of_admiss as claim_of_admiss," \
                    " to_char(t2.settle_reputation_date, 'dd-mm-yyyy') as settle_reputation_date,t16.name as client" \
                    " from policytransaction as t1 " \
                    " left join claim_policy as t2 on t2.claim_id =t1.id " \
                    " left join  project_issue as t3 on t3.id =t2.claim_ticket " \
                    " left join res_partner as t4 on t2.policy_insured_name =t4.id " \
                    " left join res_partner as t5 on t2.policy_patient_name =t5.id " \
                    " left join res_partner as t6 on t2.policy_insurer_name =t6.id " \
                    " left join res_partner as t7 on t2.policy_tpa =t7.id " \
                    " left join subdata_subdata as t8 on t2.settle_type =t8.id " \
                    " left join subdata_subdata as t9 on t3.x_claim_status =t9.id " \
                    " left join infosubdatadropdown as t10 on t3.x_claim_sub_status =t10.id " \
                    " left join clickbima_clickbima as t11 on t1.location =t11.id " \
                    " left join res_partner as t12 on t2.policy_contact_person =t12.id " \
                    " left join product_product as t13 on t2.policy_scheme =t13.id " \
                    " left join product_template as t14 on t13.product_tmpl_id=t14.id " \
                    " left join res_partner as t15 on t2.policy_surveyer_name =t15.id " \
                    " left join res_partner as t16 on t1.clientname =t16.id "

            query1 = " select t1.id,t2.claim_of_est_cause as amount," \
                    " t1.name as docket_number,t3.name as ticket_number , " \
                    " to_char(t2.claim_date_int, 'dd-mm-yyyy') as create_date,t1.name as docket_number,COALESCE(t2.claim_manual,'') as claim_manual, " \
                    " COALESCE(t4.name,'') as insured_name,COALESCE(t5.name,'') as patient_name,COALESCE(t6.name,'') as insurer_name " \
                    " ,COALESCE(t2.policy_pol_no,'') as policy_number,COALESCE(t7.name,'') as policy_tpa,COALESCE(t2.claim_brief,'') as claim_brief" \
                    " ,t2.claim_date,t2.claim_of_est_cause as claim_cause,t2.claim_amount,to_char(t2.settle_date, 'dd-mm-yyyy') as settle_date" \
                    " ,COALESCE(t8.name,'') as settle_type,COALESCE(t3.x_reply,'') as reply ,t2.settle_amount, " \
                    " COALESCE(t10.name,'') as claim_sub_status,COALESCE(t9.name,'') as claim_status, COALESCE(t1.group,'')as group,COALESCE(t2.location,'') as location, " \
                    " COALESCE(t12.name,'') as contact_person,COALESCE(t14.name,'') as scheme_name,COALESCE(t15.name,'') as surveyer_name ,t2.claim_of_admiss as claim_of_admiss," \
                    " to_char(t2.settle_reputation_date, 'dd-mm-yyyy') as settle_reputation_date,t16.name as client" \
                    " from policytransaction as t1 " \
                    " left join claim_policy as t2 on t2.claim_id =t1.id " \
                    " left join  project_issue as t3 on t3.id =t2.claim_ticket " \
                    " left join res_partner as t4 on t2.policy_insured_name =t4.id " \
                    " left join res_partner as t5 on t2.policy_patient_name =t5.id " \
                    " left join res_partner as t6 on t2.policy_insurer_name =t6.id " \
                    " left join res_partner as t7 on t2.policy_tpa =t7.id " \
                    " left join subdata_subdata as t8 on t2.settle_type =t8.id " \
                    " left join subdata_subdata as t9 on t3.x_claim_status =t9.id " \
                    " left join infosubdatadropdown as t10 on t3.x_claim_sub_status =t10.id " \
                    " left join clickbima_clickbima as t11 on t1.location =t11.id " \
                    " left join res_partner as t12 on t2.policy_contact_person =t12.id " \
                    " left join product_product as t13 on t2.policy_scheme =t13.id " \
                    " left join product_template as t14 on t13.product_tmpl_id=t14.id " \
                    " left join res_partner as t15 on t2.policy_surveyer_name =t15.id " \
                    " left join res_partner as t16 on t1.clientname =t16.id "

            query = " select t1.id,t2.claim_of_est_cause as amount," \
                    " t1.name as docket_number,t3.name as ticket_number , " \
                    " to_char(t2.claim_date_int, 'dd-mm-yyyy') as create_date,t1.name as docket_number,COALESCE(t2.claim_manual,'') as claim_manual, " \
                    " COALESCE(t4.name,'') as insured_name,COALESCE(t5.name,'') as patient_name,COALESCE(t6.name,'') as insurer_name " \
                    " ,COALESCE(t2.policy_pol_no,'') as policy_number,COALESCE(t7.name,'') as policy_tpa,COALESCE(t2.claim_brief,'') as claim_brief" \
                    " ,t2.claim_date,t2.claim_of_est_cause as claim_cause,t2.claim_amount,to_char(t2.settle_date, 'dd-mm-yyyy') as settle_date" \
                    " ,COALESCE(t8.name,'') as settle_type,COALESCE(t3.x_reply,'') as reply ,t2.settle_amount, " \
                    " COALESCE(t10.name,'') as claim_sub_status,COALESCE(t9.name,'') as claim_status, COALESCE(t1.group,'')as group,COALESCE(t2.location,'') as location, " \
                    " COALESCE(t12.name,'') as contact_person,COALESCE(t14.name,'') as scheme_name,COALESCE(t15.name,'') as surveyer_name ,t2.claim_of_admiss as claim_of_admiss," \
                    " to_char(t2.settle_reputation_date, 'dd-mm-yyyy') as settle_reputation_date,t16.name as client" \
                    " from policytransaction as t1 " \
                    " left join claim_policy as t2 on t2.claim_id =t1.id " \
                    " left join  project_issue as t3 on t3.id =t2.claim_ticket " \
                    " left join res_partner as t4 on t2.policy_insured_name =t4.id " \
                    " left join res_partner as t5 on t2.policy_patient_name =t5.id " \
                    " left join res_partner as t6 on t2.policy_insurer_name =t6.id " \
                    " left join res_partner as t7 on t2.policy_tpa =t7.id " \
                    " left join subdata_subdata as t8 on t2.settle_type =t8.id " \
                    " left join subdata_subdata as t9 on t3.x_claim_status =t9.id " \
                    " left join infosubdatadropdown as t10 on t3.x_claim_sub_status =t10.id " \
                    " left join clickbima_clickbima as t11 on t1.location =t11.id " \
                    " left join res_partner as t12 on t2.policy_contact_person =t12.id " \
                    " left join product_product as t13 on t2.policy_scheme =t13.id " \
                    " left join product_template as t14 on t13.product_tmpl_id=t14.id " \
                    " left join res_partner as t15 on t2.policy_surveyer_name =t15.id " \
                    " left join res_partner as t16 on t1.clientname =t16.id "

            if lines.fiscal_year and lines.monthly == "yearly" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
                query3+= " where t2.claim_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' AND t2.id is not null "

                query4 += " where t2.claim_date <= '" + str(lines.fiscal_year.date_end) + "' and t1.id  not in (select t1.id from policytransaction as t1 " \
                         " left join claim_policy as t2 on t2.claim_id =t1.id " \
                         " where  (t2.settle_date <= '" + str(lines.fiscal_year.date_end) + "' and (t2.settle_type =650 or t2.settle_type =651)) or " \
                         " (t2.settle_reputation_date <= '" + str(lines.fiscal_year.date_end) + "' and (t2.settle_type =644))) "
                query2 += " where t2.settle_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(
                    lines.fiscal_year.date_end) + "' AND t2.id is not null and (t2.settle_type = 651 or t2.settle_type = 650)"

                query1 += " where t2.settle_reputation_date  BETWEEN '" + str(
                    lines.fiscal_year.date_start) + "' AND '" + str(
                    lines.fiscal_year.date_end) + "' AND t2.id is not null and t2.settle_type = 644"

                query += " where t2.claim_date < '" + str(lines.fiscal_year.date_start) +  "' AND t2.id is not null  " \
                         " and t1.id not in (select t1.id from policytransaction as t1 " \
                         " left join claim_policy as t2 on   t2.claim_id=t1.id " \
                         " where t2.settle_date  < '" + str(lines.fiscal_year.date_start) + "' AND  t1.id is  not null " \
                         " and (t2.settle_type = 651 or t2.settle_type = 650) " \
                         " Union all " \
                         " select t1.id from policytransaction as t1 " \
                         " left join claim_policy as t2 on   t2.claim_id=t1.id " \
                         " where t2.settle_reputation_date  < '" + str(lines.fiscal_year.date_start) + "' AND t2.id is  not null and (t2.settle_type = 644))"

            if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "yearly" and not lines.monthly == "quatar":
                year = lines.fiscal_year.name
                if lines.months == '01-01':
                    jan_start = str(end_year) + str('-01-01')
                    jan_end = str(end_year) + str('-01-31')

                    query4 += " where t2.claim_date  BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "' "
                    query3 += " where t2.claim_date  BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "' "
                    query2 += " where t2.claim_date  BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "' "
                    query1 += " where t2.claim_date  BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "' "
                    query += " where t2.claim_date  BETWEEN '" + str(jan_start) + "' AND '" + str(jan_end) + "' "
                if lines.months == '01-02':
                    feb_start = str(end_year) + str('-02-01')
                    feb_end = str(end_year) + str('-02-28')
                    query4 += " where t2.claim_date  BETWEEN '" + str(feb_start) + "' AND '" + str(feb_end) + "' "
                    query3 += " where t2.claim_date  BETWEEN '" + str(feb_start) + "' AND '" + str(feb_end) + "' "
                    query2 += " where t2.claim_date  BETWEEN '" + str(feb_start) + "' AND '" + str(feb_end) + "' "
                    query1 += " where t2.claim_date  BETWEEN '" + str(feb_start) + "' AND '" + str(feb_end) + "' "
                    query += " where t2.claim_date  BETWEEN '" + str(feb_start) + "' AND '" + str(feb_end) + "' "
                if lines.months == '01-03':
                    mar_start = str(end_year) + str('-03-01')
                    mar_end = str(end_year) + str('-03-31')
                    query4 += " where t2.claim_date  BETWEEN '" + str(mar_start) + "' AND '" + str(mar_end) + "' "
                    query3 += " where t2.claim_date  BETWEEN '" + str(mar_start) + "' AND '" + str(mar_end) + "' "
                    query2 += " where t2.claim_date  BETWEEN '" + str(mar_start) + "' AND '" + str(mar_end) + "' "
                    query1 += " where t2.claim_date  BETWEEN '" + str(mar_start) + "' AND '" + str(mar_end) + "' "
                    query += " where t2.claim_date  BETWEEN '" + str(mar_start) + "' AND '" + str(mar_end) + "' "
                if lines.months == '01-04':
                    apr_start = str(start_year) + str('-04-01')
                    apr_end = str(start_year) + str('-04-30')
                    query4 += " where t2.claim_date  BETWEEN '" + str(apr_start) + "' AND '" + str(apr_end) + "' "
                    query3 += " where t2.claim_date  BETWEEN '" + str(apr_start) + "' AND '" + str(apr_end) + "' "
                    query2 += " where t2.claim_date  BETWEEN '" + str(apr_start) + "' AND '" + str(apr_end) + "' "
                    query1 += " where t2.claim_date  BETWEEN '" + str(apr_start) + "' AND '" + str(apr_end) + "' "
                    query += " where t2.claim_date  BETWEEN '" + str(apr_start) + "' AND '" + str(apr_end) + "' "
                if lines.months == '01-05':
                    may_start = str(start_year) + str('-05-01')
                    may_end = str(start_year) + str('-05-31')
                    query4 += " where t2.claim_date  BETWEEN '" + str(may_start) + "' AND '" + str(may_end) + "' "
                    query3 += " where t2.claim_date  BETWEEN '" + str(may_start) + "' AND '" + str(may_end) + "' "
                    query2 += " where t2.claim_date  BETWEEN '" + str(may_start) + "' AND '" + str(may_end) + "' "
                    query1 += " where t2.claim_date  BETWEEN '" + str(may_start) + "' AND '" + str(may_end) + "' "
                    query += " where t2.claim_date  BETWEEN '" + str(may_start) + "' AND '" + str(may_end) + "' "
                if lines.months == '01-06':
                    june_start = str(start_year) + str('-06-01')
                    june_end = str(start_year) + str('-06-30')
                    query4 += " where t2.claim_date  BETWEEN '" + str(june_start) + "' AND '" + str(june_end) + "' "
                    query3 += " where t2.claim_date  BETWEEN '" + str(june_start) + "' AND '" + str(june_end) + "' "
                    query2 += " where t2.claim_date  BETWEEN '" + str(june_start) + "' AND '" + str(june_end) + "' "
                    query1 += " where t2.claim_date  BETWEEN '" + str(june_start) + "' AND '" + str(june_end) + "' "
                    query += " where t2.claim_date  BETWEEN '" + str(june_start) + "' AND '" + str(june_end) + "' "
                if lines.months == '01-07':
                    jul_start = str(start_year) + str('-07-01')
                    jul_end = str(start_year) + str('-07-31')
                    query4 += " where t2.claim_date  BETWEEN '" + str(jul_start) + "' AND '" + str(jul_end) + "' "
                    query3 += " where t2.claim_date  BETWEEN '" + str(jul_start) + "' AND '" + str(jul_end) + "' "
                    query2 += " where t2.claim_date  BETWEEN '" + str(jul_start) + "' AND '" + str(jul_end) + "' "
                    query1 += " where t2.claim_date  BETWEEN '" + str(jul_start) + "' AND '" + str(jul_end) + "' "
                    query += " where t2.claim_date  BETWEEN '" + str(jul_start) + "' AND '" + str(jul_end) + "' "
                if lines.months == '01-08':
                    aug_start = str(start_year) + str('-08-01')
                    aug_end = str(start_year) + str('-08-31')
                    query4 += " where t2.claim_date  BETWEEN '" + str(aug_start) + "' AND '" + str(aug_end) + "' "
                    query3 += " where t2.claim_date  BETWEEN '" + str(aug_start) + "' AND '" + str(aug_end) + "' "
                    query2 += " where t2.claim_date  BETWEEN '" + str(aug_start) + "' AND '" + str(aug_end) + "' "
                    query1 += " where t2.claim_date  BETWEEN '" + str(aug_start) + "' AND '" + str(aug_end) + "' "
                    query += " where t2.claim_date  BETWEEN '" + str(aug_start) + "' AND '" + str(aug_end) + "' "
                if lines.months == '01-09':
                    sep_start = str(start_year) + str('-09-01')
                    sep_end = str(start_year) + str('-09-30')
                    query4 += " where t2.claim_date  BETWEEN '" + str(sep_start) + "' AND '" + str(sep_end) + "' "
                    query3 += " where t2.claim_date  BETWEEN '" + str(sep_start) + "' AND '" + str(sep_end) + "' "
                    query2 += " where t2.claim_date  BETWEEN '" + str(sep_start) + "' AND '" + str(sep_end) + "' "
                    query1 += " where t2.claim_date  BETWEEN '" + str(sep_start) + "' AND '" + str(sep_end) + "' "
                    query += " where t2.claim_date  BETWEEN '" + str(sep_start) + "' AND '" + str(sep_end) + "' "
                if lines.months == '01-10':
                    oct_start = str(start_year) + str('-10-01')
                    oct_end = str(start_year) + str('-10-31')
                    query4 += " where t2.claim_date  BETWEEN '" + str(oct_start) + "' AND '" + str(oct_end) + "' "
                    query3 += " where t2.claim_date  BETWEEN '" + str(oct_start) + "' AND '" + str(oct_end) + "' "
                    query2 += " where t2.claim_date  BETWEEN '" + str(oct_start) + "' AND '" + str(oct_end) + "' "
                    query1 += " where t2.claim_date  BETWEEN '" + str(oct_start) + "' AND '" + str(oct_end) + "' "
                    query += " where t2.claim_date  BETWEEN '" + str(oct_start) + "' AND '" + str(oct_end) + "' "
                if lines.months == '01-11':
                    nov_start = str(start_year) + str('-11-01')
                    nov_end = str(start_year) + str('-11-30')
                    query4 += " where t2.claim_date  BETWEEN '" + str(nov_start) + "' AND '" + str(nov_end) + "' "
                    query3 += " where t2.claim_date  BETWEEN '" + str(nov_start) + "' AND '" + str(nov_end) + "' "
                    query2 += " where t2.claim_date  BETWEEN '" + str(nov_start) + "' AND '" + str(nov_end) + "' "
                    query1 += " where t2.claim_date  BETWEEN '" + str(nov_start) + "' AND '" + str(nov_end) + "' "
                    query += " where t2.claim_date  BETWEEN '" + str(nov_start) + "' AND '" + str(nov_end) + "' "

                if lines.months == '01-12':
                    dec_start = str(start_year) + str('-12-01')
                    dec_end = str(start_year) + str('-12-31')
                    query4 += " where t2.claim_date  BETWEEN '" + str(dec_start) + "' AND '" + str(dec_end) + "' "
                    query3 += " where t2.claim_date  BETWEEN '" + str(dec_start) + "' AND '" + str(dec_end) + "' "
                    query2 += " where t2.claim_date  BETWEEN '" + str(dec_start) + "' AND '" + str(dec_end) + "' "
                    query1 += " where t2.claim_date  BETWEEN '" + str(dec_start) + "' AND '" + str(dec_end) + "' "
                    query += " where t2.claim_date  BETWEEN '" + str(dec_start) + "' AND '" + str(dec_end) + "' "
            if lines.quarter and not lines.monthly == 'yearly' and not lines.monthly == 'monthly':
                if lines.quarter == "q2" or lines.quarter == "q3" or lines.quarter == "q4" or lines.quarter == "q1":
                    query4 += " where t2.claim_date <= '" + str(
                        lines.date_to) + "' and t1.id  not in (select t1.id from policytransaction as t1 " \
                                         " left join claim_policy as t2 on t2.claim_id =t1.id " \
                                         " where  (t2.settle_date <= '" + str(lines.date_to) + "' and " \
                                         "(t2.settle_type =650 or t2.settle_type =651)) or " \
                                        " (t2.settle_reputation_date <= '" + str(lines.date_to) + "' and (t2.settle_type =644))) "
                    query3 += " where t2.claim_date  BETWEEN '" + str(lines.date_from) + "' AND '" + str(lines.date_to) + "' AND  t2.id is not null"
                    query2 += " where t2.settle_date  BETWEEN '" + str(lines.date_from) + "' AND '" + str(lines.date_to) + "' AND  t2.id is not null and (t2.settle_type = 651 or t2.settle_type = 650)"
                    query1 += " where t2.settle_reputation_date  BETWEEN '" + str(lines.date_from) + "' AND '" + str(lines.date_to) + "' AND  t2.id is not null and t2.settle_type = 644"
                    query +=  " where t2.claim_date < '" + str(lines.date_from) + "' and t1.id  not in (select t1.id from policytransaction as t1 " \
                              " left join claim_policy as t2 on t2.claim_id =t1.id " \
                              " where  (t2.settle_date < '" + str(lines.date_from) + "' and " \
                              " (t2.settle_type =650 or t2.settle_type =651)) or  (t2.settle_reputation_date < '" + str(lines.date_from) + "' and (t2.settle_type =644))) "


            if lines.filterby == 'group':
                query4 += " and  t1.group is not null order by t1.group "
                query3 += " and  t1.group is not null order by t1.group "
                query2 += " and  t1.group is not null order by t1.group "
                query1 += " and  t1.group is not null order by t1.group "
                query  += " and  t1.group is not null order by t1.group"




            if lines.filterby == 'client':
                query4 += " and  t1.group is null order by t1.group "
                query3 += " and  t1.group is null order by t1.group "
                query2 += " and  t1.group is null order by t1.group "
                query1 += " and  t1.group is null order by t1.group "
                query  += " and  t1.group is null order by t1.group"




            cr.execute(query)
            usr_detail = cr.dictfetchall()
            cr.execute(query1)
            usr_detail1 = cr.dictfetchall()
            cr.execute(query2)
            usr_detail2 = cr.dictfetchall()
            cr.execute(query3)
            usr_detail3 = cr.dictfetchall()
            cr.execute(query4)
            usr_detail4 = cr.dictfetchall()




        quat = ''
        period =''
        if lines.monthly == 'yearly':
            quat = '(' + str(lines.fiscal_year.date_start) + ' to ' + str(
                lines.fiscal_year.date_end) + ')'
            period = '  Yearly'
            per_date =  '  From ' + str(lines.fiscal_year.date_start) + ' To ' + str(
                lines.fiscal_year.date_end)
        elif lines.monthly == 'quatar':
            if lines.quarter == 'q1':
                q1_start = str('01-04-') + str(start_year)
                q1_end = str('30-06-') + str(start_year)
                quat = '(' + str(q1_start) + ' to ' + str(q1_end) + ')'
                period = '  Quarter  April-June'
                per_date = '  From ' + str(q1_start) + ' To ' + str(q1_end)
            if lines.quarter == 'q2':
                q2_start = str('01-07-') + str(start_year)
                q2_end = str('30-09-') + str(start_year)
                quat = '(' + str(q2_start) + ' to ' + str(q2_end) + ')'
                period = '  Quarter  July-September'
                per_date = '  From ' + str(q2_start) + ' To ' + str(q2_end)
            if lines.quarter == 'q3':
                q3_start = str('01-10-') + str(start_year)
                q3_end = str('31-12-') + str(start_year)
                quat = '(' + str(q3_start) + ' to ' + str(q3_end) + ')'
                period = ' Quarter  October-December'
                per_date = ' From ' + str(q3_start) + ' To ' + str(q3_end)
            if lines.quarter == 'q4':
                q4_start = str('01-01-') + str(end_year)
                q4_end = str('31-03-') + str(end_year)
                quat = '(' + str(q4_start) + ' to ' + str(q4_end) + ')'
                period = ' Quarter  January-March'
                per_date = ' From ' + str(q4_start) + ' To ' + str(q4_end)
        elif lines.monthly == 'monthly':
            if lines.months == '01-01':
                jan_start =  str('01-01-') + str(end_year)
                jan_end = str('31-01-') + str(end_year)
                period = '  Monthly  January'
                per_date = '  From ' + str(jan_start) + ' To ' + str(jan_end)
                quat = '(' + str(jan_start) + ' to ' + str(jan_end) + ')'

            if lines.months == '01-02':
                feb_start =  str('01-02-') + str(end_year)
                feb_end =  str('28-02-') + str(end_year)
                period = '  Monthly  February'
                per_date = '  From ' + str(feb_start) + ' To ' + str(feb_end)
                quat = '(' + str(feb_start) + ' to ' + str(feb_end) + ')'
            if lines.months == '01-03':
                mar_start = str('01-03-') + str(end_year)
                mar_end =  str('31-03-')+ str(end_year)
                period = '  Monthly  March'
                per_date = '  From ' + str(mar_start) + ' To ' + str(mar_end)
                quat = '(' + str(mar_start) + ' to ' + str(mar_end) + ')'
            if lines.months == '01-04':
                apr_start =  str('01-04-') + str(start_year)
                apr_end =  str('30-04-') + str(start_year)
                period = '  Monthly   April'
                per_date = '  From ' + str(apr_start) + ' To ' + str(apr_end)
                quat = '(' + str(apr_start) + ' to ' + str(apr_end) + ')'
            if lines.months == '01-05':
                may_start =  str('01-05-') + str(start_year)
                may_end =  str('31-05-') + str(start_year)
                period = '  Monthly  May'
                per_date = '  From ' + str(may_start) + ' To ' + str(may_end)
                quat = '(' + str(may_start) + ' to ' + str(may_end) + ')'
            if lines.months == '01-06':
                june_start = str('01-06-') + str(start_year)
                june_end =  str('30-06-') + str(start_year)
                period = '  Monthly  June'
                per_date = '  From ' + str(june_start) + ' To ' + str(june_end)
                quat = '(' + str(june_start) + ' to ' + str(june_end) + ')'
            if lines.months == '01-07':
                jul_start =  str('01-07-') + str(start_year)
                jul_end = str('31-07-') + str(start_year)
                period = '  Monthly  July'
                per_date = '  From ' + str(jul_start) + ' To ' + str(jul_end)
                quat = '(' + str(jul_start) + ' to ' + str(jul_end) + ')'
            if lines.months == '01-08':
                aug_start =  str('01-08-') + str(start_year)
                aug_end = str('31-08-') + str(start_year)
                period = '  Monthly  August'
                per_date = '  From ' + str(aug_start) + ' To ' + str(aug_end)
                quat = '(' + str(aug_start) + ' to ' + str(aug_end) + ')'
            if lines.months == '01-09':
                sep_start =str('01-09-') + str(start_year)
                sep_end = str('30-09-') + str(start_year)
                period = '  Monthly  September'
                per_date = '  From ' + str(sep_start) + ' To ' + str(sep_end)
                quat = '(' + str(sep_start) + ' to ' + str(sep_end) + ')'
            if lines.months == '01-10':
                oct_start =  str('01-10-') + str(start_year)
                oct_end =str('31-10-') + str(start_year)
                period = '  Monthly  October'
                per_date = '  From ' + str(oct_start) + ' To ' + str(oct_end)
                quat = '(' + str(oct_start) + ' to ' + str(oct_end) + ')'
            if lines.months == '01-11':
                nov_start = str('01-11-') + str(start_year)
                nov_end = str('30-11-') + str(start_year)
                period = '  Monthly  November'
                per_date = '  From ' + str(nov_start) + ' To ' + str(nov_end)
                quat = '(' + str(nov_start) + ' to ' + str(nov_end) + ')'
            if lines.months == '01-12':
                dec_start = str('01-12-') + str(start_year)
                dec_end =str('31-12-') + str(start_year)
                period = '  Monthly  December'
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
        bold4 = workbook.add_format({ 'align': 'center', 'border': 1})
        border = workbook.add_format({'border': 1, 'align': 'right','bold': True,})
        border2 = workbook.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'right'})
        border1 = workbook.add_format({'border': 1, 'align': 'left'})
        align_right = workbook.add_format({'align': 'right', 'border': 1, 'bold': True, })
        numbersformat = workbook.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'right','bold': True})
        report_head1 = 'Fin. Year'
        report_head2 = str(lines.fiscal_year.name)
        report_head3 = 'Security Insurance Brokers (India) Private Limited'
        report_head4 = 'New Delhi'
        report_head5 = 'Register Detail'
        report_head6 = 'Transaction Detail'
        report_head7 = 'Previous Insurer Name/Branch'
        report_head8 = 'Previous Policy No'
        report_head9 = 'Issue Date'
        report_head10 = 'From'
        report_head11 = 'To'
        report_head12 = 'Client Name / Group'
        report_head13 = 'Referred By'
        report_head14 = 'Sales Team'
        report_head15 = 'Sales Person'
        report_head16 = 'Campaign'
        report_head17 = 'Medium'
        report_head18 = 'Source'
        report_head19 = 'Policy Name, Insurer and Branch'
        report_head20 = 'Policy No'
        report_head21 = 'Renewal'
        report_head22 = 'Declaration'
        report_head23 = 'Sum Insured'
        report_head24 = 'Brokerage Premium'
        report_head25 = 'Third Party Premium'
        report_head26 = 'Terrorism Premium'
        report_head27 = 'Stamp Duty'
        report_head28 = 'Net Premium'
        report_head29 = 'GST Rate (%)'
        report_head30 = 'GST Amount'
        report_head31 = 'Round Off'
        report_head32 = 'Gross Premium'
        report_head33 = 'Endorsement Details'
        report_head34 = 'Type'
        report_head35 = 'Reason'
        report_head36 = 'Payment Details'
        report_head37 = 'Bank'


        sheet.write(3, 5, ('Pipeline'), bold3)
        sheet.write(3, 6, ('RFQ No.'), bold3)
        sheet.write(3, 7, ('RFQ Date'), bold3)
        sheet.write(3, 8, ('Docket'), bold3)
        # sheet.write(5, 9, ('Docket'), bold3)
        # sheet.write(5, 9, ('Docket'), bold3)
        # sheet.write(5, 9, ('Docket'), bold3)
        # sheet.write(5, 9, ('Docket'), bold3)
        sheet.merge_range('J1:K1', report_head1, bold3)
        sheet.merge_range('J2:K2', report_head2, bold3)
        sheet.merge_range('B2:I2', report_head4, bold)
        sheet.merge_range('B1:I1', report_head3, bold)
        sheet.merge_range('B4:E4', report_head5, bold)
        sheet.merge_range('J4:K4', report_head6, bold3)
        sheet.merge_range('B7:E7', report_head7, bold)
        sheet.merge_range('F7:G7', report_head8, bold)
        sheet.merge_range('F8:G8', report_head9, bold3)
        sheet.merge_range('H8:I8', report_head10, bold3)
        sheet.merge_range('J8:K8', report_head11, bold3)
        sheet.merge_range('B11:E11', report_head12, bold)
        sheet.merge_range('F11:G11', report_head13, bold3)
        sheet.merge_range('H11:I11', report_head14, bold3)
        sheet.merge_range('J11:K11', report_head15, bold3)
        sheet.merge_range('B14:E14', report_head16, bold3)
        sheet.merge_range('F14:H14', report_head17, bold3)
        sheet.merge_range('I14:K14', report_head18, bold3)
        sheet.merge_range('B17:E17', report_head19, bold)
        sheet.merge_range('F17:G17', report_head20, bold3)
        sheet.merge_range('F18:G18', report_head9, bold3)
        sheet.merge_range('H18:I18', report_head10, bold3)
        sheet.merge_range('J18:K18', report_head11, bold3)
        sheet.merge_range('H20:I20', report_head21, bold3)
        sheet.merge_range('J20:K20', report_head22, bold3)
        sheet.merge_range('B22:C22', report_head23, border)
        sheet.merge_range('D22:E22', report_head24, border)
        sheet.merge_range('F22:G22', report_head25, border)
        sheet.merge_range('H22:I22', report_head26, border)
        sheet.merge_range('J22:K22', report_head27, border)
        sheet.merge_range('B25:C25', report_head28, border)
        sheet.merge_range('D25:E25', report_head29, border)
        sheet.merge_range('F25:G25', report_head30, border)
        sheet.merge_range('H25:I25', report_head31, border)
        sheet.merge_range('J25:K25', report_head32, border)
        sheet.merge_range('B28:K28', report_head33, bold)
        sheet.merge_range('C29:D29', report_head34, bold)
        sheet.merge_range('E29:F29', report_head35, bold)
        sheet.merge_range('G29:K29', report_head23, border)
        sheet.merge_range('J29:K29', report_head32, border)
        sheet.merge_range('B34:K34', report_head36, border)

        # increasing width of column
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 15)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 15)
        sheet.set_column('K:K', 15)
        sheet.set_column('L:L', 15)
        sheet.set_column('M:M', 15)
        sheet.set_column('N:N', 15)
        sheet.set_column('O:O', 15)
        sheet.set_column('P:P', 20)
        sheet.set_column('Q:Q', 20)
        sheet.set_column('R:R', 15)
        sheet.set_column('S:S', 15)
        sheet.set_column('T:T', 20)
        sheet.set_column('U:U', 20)
        row = 8
        s_no = 1

        # # if lines.filterby == 'group':
        #
        # ##### opening registered ##########
        # o_claim_cause = 0
        # o_settle_amount = 0
        # o_claim_amount = 0
        # o_total_claim_cause = 0
        # o_total_settle_amount = 0
        # o_total_claim_amount = 0
        # # settle_date =''
        # for res in usr_detail:
        #     claim_brief = res['claim_brief']
        #     claim_brief.encode('utf-8')
        #     settle_date = ''
        #
        #     if res['claim_cause'] == None or res['claim_cause'] == False:
        #         o_claim_cause = 0
        #     else:
        #         o_claim_cause = res['claim_cause']
        #     if res['settle_amount'] == None or res['settle_amount'] == False:
        #         o_settle_amount = 0
        #     else:
        #         o_settle_amount = res['settle_amount']
        #
        #     if res['claim_amount'] == None or res['claim_amount'] == False:
        #         o_claim_amount = 0
        #     else:
        #         o_claim_amount = res['claim_amount']
        #
        #
        #     if res['settle_date']!= None:
        #         settle_date =res['settle_date']
        #     if res['settle_reputation_date']!=None:
        #         settle_date = res['settle_reputation_date']
        #
        #     o_total_claim_amount += o_claim_amount
        #     o_total_settle_amount += o_settle_amount
        #     o_total_claim_cause += o_claim_cause
        #
        #     sheet.write(row, 1, str(res['ticket_number']), border1)
        #     sheet.write(row, 2, str(res['create_date']), bold4)
        #     sheet.write(row, 3, str(res['docket_number']), bold4)
        #     sheet.write(row, 4, res['claim_manual'], bold4)
        #     sheet.write(row, 5, str(res['insured_name']) + str(',  ') + (res['group']), border1)
        #     sheet.write(row, 6, (res['patient_name']) + str(',  ') + str(res['location']), border1)
        #     sheet.write(row, 7, str(res['insurer_name']) + str(',  ') + str(res['contact_person']), border1)
        #     sheet.write(row, 8, str(res['scheme_name']) + str(',  ') + str(res['policy_number']), border1)
        #     sheet.write(row, 9, (res['surveyer_name']) + str(',  ') + (res['policy_tpa']), border1)
        #     sheet.write(row, 10, claim_brief, border1)
        #     sheet.write(row, 11, str(res['claim_date']) + str(',  ') + str(res['claim_of_admiss']), bold4)
        #     sheet.write(row, 12, o_claim_cause, numbersformat)
        #     sheet.write(row, 13, o_claim_amount, numbersformat)
        #     sheet.write(row, 14, str(res['claim_status']), border1)
        #     sheet.write(row, 15, str(res['claim_sub_status']), border1)
        #     sheet.write(row, 16, str(res['settle_type']), border1)
        #     sheet.write(row, 17, o_settle_amount, numbersformat)
        #     sheet.write(row, 18, str(settle_date), bold4)
        #     sheet.write(row, 19, (res['reply']), border1)
        #     row = row + 1
        #     s_no = s_no + 1
        # sheet.write(row, 11, "Total", bold2)
        # sheet.write(row, 12, o_total_claim_cause, numbersformat)
        # sheet.write(row, 13, o_total_claim_amount, numbersformat)
        # sheet.write(row, 17, o_total_settle_amount, numbersformat)
        #
        # if lines.filterby == 'group':
        #     an_iterator = itertools.groupby(usr_detail, key=operator.itemgetter(str(lines.filterby)))
        #     og_claim_cause = 0
        #     og_settle_amount = 0
        #     og_claim_amount = 0
        #     og_total_claim_cause = 0
        #     og_total_settle_amount = 0
        #     og_total_claim_amount = 0
        #     for key, group in an_iterator:
        #         key_and_group = {key: list(group)}
        #         for i in key_and_group.iteritems():
        #             for res in i[1]:
        #                 claim_brief = res['claim_brief']
        #                 claim_brief.encode('utf-8')
        #                 settle_date = ''
        #                 if res['claim_cause'] == None or res['claim_cause'] == False:
        #                     og_claim_cause = 0
        #                 else:
        #                     og_claim_cause = res['claim_cause']
        #                 if res['settle_amount'] == None or res['settle_amount'] == False:
        #                     og_settle_amount = 0
        #                 else:
        #                     og_settle_amount = res['settle_amount']
        #
        #                 if res['claim_amount'] == None or res['claim_amount'] == False:
        #                     og_claim_amount = 0
        #                 else:
        #                     og_claim_amount = res['claim_amount']
        #
        #                 if res['settle_date'] != None:
        #                     settle_date = res['settle_date']
        #                 if res['settle_reputation_date'] != None:
        #                     settle_date = res['settle_reputation_date']
        #
        #                 og_total_claim_amount += og_claim_amount
        #                 og_total_settle_amount += og_settle_amount
        #                 og_total_claim_cause += og_claim_cause
        #
        #                 sheet.write(row, 1, str(res['ticket_number']), border1)
        #                 sheet.write(row, 2, str(res['create_date']), bold4)
        #                 sheet.write(row, 3, str(res['docket_number']), bold4)
        #                 sheet.write(row, 4, res['claim_manual'], bold4)
        #                 sheet.write(row, 5, str(res['insured_name']) + str(',  ') + str(i[0]), border1)
        #                 sheet.write(row, 6, (res['patient_name']) + str(',  ') + str(res['location']), border1)
        #                 sheet.write(row, 7, str(res['insurer_name']) + str(',  ') + str(res['contact_person']), border1)
        #                 sheet.write(row, 8, str(res['scheme_name']) + str(',  ') + str(res['policy_number']), border1)
        #                 sheet.write(row, 9, str(res['surveyer_name']) + str(',  ') + str(res['policy_tpa']), border1)
        #                 sheet.write(row, 10, claim_brief, border1)
        #                 sheet.write(row, 11, str(res['claim_date']) + str(',  ') + str(res['claim_of_admiss']), bold4)
        #                 sheet.write(row, 12, og_claim_cause, numbersformat)
        #                 sheet.write(row, 13, og_claim_amount, numbersformat)
        #                 sheet.write(row, 14, str(res['claim_status']), border1)
        #                 sheet.write(row, 15, str(res['claim_sub_status']), border1)
        #                 sheet.write(row, 16, str(res['settle_type']), border1)
        #                 sheet.write(row, 17, og_settle_amount, numbersformat)
        #                 sheet.write(row, 18, str(settle_date), bold4)
        #                 sheet.write(row, 19, (res['reply']), border1)
        #                 row = row + 1
        #                 s_no = s_no + 1
        #             sheet.write(row, 11, "Total", bold2)
        #             sheet.write(row, 12, og_total_claim_cause, numbersformat)
        #             sheet.write(row, 13, og_total_claim_amount, numbersformat)
        #             sheet.write(row, 17, og_total_settle_amount, numbersformat)
        #
        #
        # if lines.filterby == 'client':
        #     an_iterator = itertools.groupby(usr_detail, key=operator.itemgetter(str(lines.filterby)))
        #     og_claim_cause = 0
        #     og_settle_amount = 0
        #     og_claim_amount = 0
        #     og_total_claim_cause = 0
        #     og_total_settle_amount = 0
        #     og_total_claim_amount = 0
        #     for key, group in an_iterator:
        #         key_and_group = {key: list(group)}
        #         for i in key_and_group.iteritems():
        #             for res in i[1]:
        #                 claim_brief = res['claim_brief']
        #                 claim_brief.encode('utf-8')
        #                 settle_date = ''
        #                 if res['claim_cause'] == None or res['claim_cause'] == False:
        #                     og_claim_cause = 0
        #                 else:
        #                     og_claim_cause = res['claim_cause']
        #                 if res['settle_amount'] == None or res['settle_amount'] == False:
        #                     og_settle_amount = 0
        #                 else:
        #                     og_settle_amount = res['settle_amount']
        #
        #                 if res['claim_amount'] == None or res['claim_amount'] == False:
        #                     og_claim_amount = 0
        #                 else:
        #                     og_claim_amount = res['claim_amount']
        #
        #                 if res['settle_date'] != None:
        #                     settle_date = res['settle_date']
        #                 if res['settle_reputation_date'] != None:
        #                     settle_date = res['settle_reputation_date']
        #
        #                 og_total_claim_amount += og_claim_amount
        #                 og_total_settle_amount += og_settle_amount
        #                 og_total_claim_cause += og_claim_cause
        #
        #                 sheet.write(row, 1, str(res['ticket_number']), border1)
        #                 sheet.write(row, 2, str(res['create_date']), bold4)
        #                 sheet.write(row, 3, str(res['docket_number']), bold4)
        #                 sheet.write(row, 4, res['claim_manual'], bold4)
        #                 sheet.write(row, 5, str(res['insured_name']) + str(',  ') + str(i[0]), border1)
        #                 sheet.write(row, 6, (res['patient_name']) + str(',  ') + str(res['location']), border1)
        #                 sheet.write(row, 7, str(res['insurer_name']) + str(',  ') + str(res['contact_person']), border1)
        #                 sheet.write(row, 8, str(res['scheme_name']) + str(',  ') + str(res['policy_number']), border1)
        #                 sheet.write(row, 9, str(res['surveyer_name']) + str(',  ') + str(res['policy_tpa']), border1)
        #                 sheet.write(row, 10, claim_brief, border1)
        #                 sheet.write(row, 11, str(res['claim_date']) + str(',  ') + str(res['claim_of_admiss']), bold4)
        #                 sheet.write(row, 12, og_claim_cause, numbersformat)
        #                 sheet.write(row, 13, og_claim_amount, numbersformat)
        #                 sheet.write(row, 14, str(res['claim_status']), border1)
        #                 sheet.write(row, 15, str(res['claim_sub_status']), border1)
        #                 sheet.write(row, 16, str(res['settle_type']), border1)
        #                 sheet.write(row, 17, og_settle_amount, numbersformat)
        #                 sheet.write(row, 18, str(settle_date), bold4)
        #                 sheet.write(row, 19, (res['reply']), border1)
        #                 row = row + 1
        #                 s_no = s_no + 1
        #             sheet.write(row, 11, "Total", bold2)
        #             sheet.write(row, 12, og_total_claim_cause, numbersformat)
        #             sheet.write(row, 13, og_total_claim_amount, numbersformat)
        #             sheet.write(row, 17, og_total_settle_amount, numbersformat)




        #
        # ##### during the year claim registered ##########
        # row = row + 3
        # sheet.write(row, 1, ('New Claims registered during the period ' + str(quat) ), bold)
        # row += 1
        # d_claim_cause = 0
        # d_settle_amount = 0
        # d_claim_amount = 0
        # d_total_claim_cause = 0
        # d_total_settle_amount = 0
        # d_total_claim_amount = 0
        # for res in usr_detail3:
        #     claim_brief = res['claim_brief']
        #     claim_brief.encode('utf-8')
        #
        #     settle_date = ''
        #
        #     if res['claim_cause'] == None or res['claim_cause'] == False:
        #         d_claim_cause = 0
        #     else:
        #         d_claim_cause = res['claim_cause']
        #     if res['settle_amount'] == None or res['settle_amount'] == False:
        #         d_settle_amount = 0
        #     else:
        #         d_settle_amount = res['settle_amount']
        #
        #     if res['claim_amount'] == None or res['claim_amount'] == False:
        #         d_claim_amount = 0
        #     else:
        #         d_claim_amount = res['claim_amount']
        #
        #     if res['settle_date'] != None:
        #         settle_date = res['settle_date']
        #     if res['settle_reputation_date'] != None:
        #         settle_date = res['settle_reputation_date']
        #
        #     d_total_claim_amount += d_claim_amount
        #     d_total_settle_amount += d_settle_amount
        #     d_total_claim_cause += d_claim_cause
        #
        #     sheet.write(row, 1, str(res['ticket_number']), border1)
        #     sheet.write(row, 2, str(res['create_date']), bold4)
        #     sheet.write(row, 3, str(res['docket_number']), bold4)
        #     sheet.write(row, 4, res['claim_manual'], bold4)
        #     sheet.write(row, 5, str(res['insured_name']) + str(',  ') + (res['group']), border1)
        #     sheet.write(row, 6, str(res['patient_name']) + str(',  ') + str(res['location']), border1)
        #     sheet.write(row, 7, str(res['insurer_name']) + str(',  ') + str(res['contact_person']), border1)
        #     sheet.write(row, 8, str(res['scheme_name']) + str(',  ') + str(res['policy_number']), border1)
        #     sheet.write(row, 9, str(res['surveyer_name']) + str(',  ') + str(res['policy_tpa']), border1)
        #     sheet.write(row, 10, claim_brief, border1)
        #     sheet.write(row, 11, str(res['claim_date']) + str(',  ') + str(res['claim_of_admiss']), bold4)
        #     sheet.write(row, 12, d_claim_cause, numbersformat)
        #     sheet.write(row, 13, d_claim_amount, numbersformat)
        #     sheet.write(row, 14, str(res['claim_status']), border1)
        #     sheet.write(row, 15, str(res['claim_sub_status']), border1)
        #     sheet.write(row, 16, str(res['settle_type']), border1)
        #     sheet.write(row, 17, d_settle_amount, numbersformat)
        #     sheet.write(row, 18, str(settle_date), bold4)
        #     sheet.write(row, 19, (res['reply']), border1)
        #     row = row + 1
        #     s_no = s_no + 1
        # sheet.write(row, 11, "Total", bold2)
        # sheet.write(row, 12, d_total_claim_cause, numbersformat)
        # sheet.write(row, 13, d_total_claim_amount, numbersformat)
        # sheet.write(row, 17, d_total_settle_amount, numbersformat)
        #
        # if lines.filterby == 'group':
        #     an_iterator = itertools.groupby(usr_detail3, key=operator.itemgetter(str(lines.filterby)))
        #     o_claim_cause = 0
        #     o_settle_amount = 0
        #     o_claim_amount = 0
        #     o_total_claim_cause = 0
        #     o_total_settle_amount = 0
        #     o_total_claim_amount = 0
        #
        #     for key, group in an_iterator:
        #         key_and_group = {key: list(group)}
        #         for i in key_and_group.iteritems():
        #             for res in i[1]:
        #                 claim_brief = res['claim_brief']
        #                 claim_brief.encode('utf-8')
        #                 settle_date = ''
        #                 if res['claim_cause'] == None or res['claim_cause'] == False:
        #                     o_claim_cause = 0
        #                 else:
        #                     o_claim_cause = res['claim_cause']
        #                 if res['settle_amount'] == None or res['settle_amount'] == False:
        #                     o_settle_amount = 0
        #                 else:
        #                     o_settle_amount = res['settle_amount']
        #
        #                 if res['claim_amount'] == None or res['claim_amount'] == False:
        #                     o_claim_amount = 0
        #                 else:
        #                     o_claim_amount = res['claim_amount']
        #
        #                 if res['settle_date'] != None:
        #                     settle_date = res['settle_date']
        #                 if res['settle_reputation_date'] != None:
        #                     settle_date = res['settle_reputation_date']
        #
        #                 o_total_claim_amount += o_claim_amount
        #                 o_total_settle_amount += o_settle_amount
        #                 o_total_claim_cause += o_claim_cause
        #
        #                 sheet.write(row, 1, str(res['ticket_number']), border1)
        #                 sheet.write(row, 2, str(res['create_date']), bold4)
        #                 sheet.write(row, 3, str(res['docket_number']), bold4)
        #                 sheet.write(row, 4, res['claim_manual'], bold4)
        #                 sheet.write(row, 5, str(res['insured_name']) + str(',  ') + str(i[0]), border1)
        #                 sheet.write(row, 6, str(res['patient_name']) + str(',  ') + str(res['location']), border1)
        #                 sheet.write(row, 7, str(res['insurer_name']) + str(',  ') + str(res['contact_person']), border1)
        #                 sheet.write(row, 8, str(res['scheme_name']) + str(',  ') + str(res['policy_number']), border1)
        #                 sheet.write(row, 9, str(res['surveyer_name']) + str(',  ') + str(res['policy_tpa']), border1)
        #                 sheet.write(row, 10, claim_brief, border1)
        #                 sheet.write(row, 11, str(res['claim_date']) + str(',  ') + str(res['claim_of_admiss']), bold4)
        #                 sheet.write(row, 12, o_claim_cause, numbersformat)
        #                 sheet.write(row, 13, o_claim_amount, numbersformat)
        #                 sheet.write(row, 14, str(res['claim_status']), border1)
        #                 sheet.write(row, 15, str(res['claim_sub_status']), border1)
        #                 sheet.write(row, 16, str(res['settle_type']), border1)
        #                 sheet.write(row, 17, o_settle_amount, numbersformat)
        #                 sheet.write(row, 18, str(settle_date), bold4)
        #                 sheet.write(row, 19, str(res['reply']), border1)
        #                 row = row + 1
        #                 s_no = s_no + 1
        #             sheet.write(row, 11, "Total", bold2)
        #             sheet.write(row, 12, o_total_claim_cause, numbersformat)
        #             sheet.write(row, 13, o_total_claim_amount, numbersformat)
        #             sheet.write(row, 17, o_total_settle_amount, numbersformat)
        #
        #
        #
        # if lines.filterby =='client':
        #     an_iterator = itertools.groupby(usr_detail3, key=operator.itemgetter(str(lines.filterby)))
        #     o_claim_cause = 0
        #     o_settle_amount = 0
        #     o_claim_amount = 0
        #     o_total_claim_cause = 0
        #     o_total_settle_amount = 0
        #     o_total_claim_amount = 0
        #
        #     for key, group in an_iterator:
        #         key_and_group = {key: list(group)}
        #         for i in key_and_group.iteritems():
        #             for res in i[1]:
        #                 claim_brief = res['claim_brief']
        #                 claim_brief.encode('utf-8')
        #                 settle_date = ''
        #                 if res['claim_cause'] == None or res['claim_cause'] == False:
        #                     o_claim_cause = 0
        #                 else:
        #                     o_claim_cause = res['claim_cause']
        #                 if res['settle_amount'] == None or res['settle_amount'] == False:
        #                     o_settle_amount = 0
        #                 else:
        #                     o_settle_amount = res['settle_amount']
        #
        #                 if res['claim_amount'] == None or res['claim_amount'] == False:
        #                     o_claim_amount = 0
        #                 else:
        #                     o_claim_amount = res['claim_amount']
        #
        #                 if res['settle_date'] != None:
        #                     settle_date = res['settle_date']
        #                 if res['settle_reputation_date'] != None:
        #                     settle_date = res['settle_reputation_date']
        #
        #                 o_total_claim_amount += o_claim_amount
        #                 o_total_settle_amount += o_settle_amount
        #                 o_total_claim_cause += o_claim_cause
        #
        #                 sheet.write(row, 1, str(res['ticket_number']), border1)
        #                 sheet.write(row, 2, str(res['create_date']), bold4)
        #                 sheet.write(row, 3, str(res['docket_number']), bold4)
        #                 sheet.write(row, 4, res['claim_manual'], bold4)
        #                 sheet.write(row, 5, str(res['insured_name']) + str(',  ') + str(i[0]), border1)
        #                 sheet.write(row, 6, str(res['patient_name']) + str(',  ') + str(res['location']), border1)
        #                 sheet.write(row, 7, str(res['insurer_name']) + str(',  ') + str(res['contact_person']), border1)
        #                 sheet.write(row, 8, str(res['scheme_name']) + str(',  ') + str(res['policy_number']), border1)
        #                 sheet.write(row, 9, str(res['surveyer_name']) + str(',  ') + str(res['policy_tpa']), border1)
        #                 sheet.write(row, 10, claim_brief, border1)
        #                 sheet.write(row, 11, str(res['claim_date']) + str(',  ') + str(res['claim_of_admiss']), bold4)
        #                 sheet.write(row, 12, o_claim_cause, numbersformat)
        #                 sheet.write(row, 13, o_claim_amount, numbersformat)
        #                 sheet.write(row, 14, str(res['claim_status']), border1)
        #                 sheet.write(row, 15, str(res['claim_sub_status']), border1)
        #                 sheet.write(row, 16, str(res['settle_type']), border1)
        #                 sheet.write(row, 17, o_settle_amount, numbersformat)
        #                 sheet.write(row, 18, str(settle_date), bold4)
        #                 sheet.write(row, 19, str(res['reply']), border1)
        #                 row = row + 1
        #                 s_no = s_no + 1
        #             sheet.write(row, 11, "Total", bold2)
        #             sheet.write(row, 12, o_total_claim_cause, numbersformat)
        #             sheet.write(row, 13, o_total_claim_amount, numbersformat)
        #             sheet.write(row, 17, o_total_settle_amount, numbersformat)
        #
        # ##### Closing of the settle  during year ##########
        # row=row +3
        # sheet.write(row, 1, ('Claims settled/closed during the period ' + str(quat) ), bold)
        # row +=1
        #
        # s_claim_cause = 0
        # s_settle_amount = 0
        # s_claim_amount = 0
        # s_total_claim_cause = 0
        # s_total_settle_amount = 0
        # s_total_claim_amount = 0
        # for res in usr_detail2:
        #     claim_brief = res['claim_brief']
        #     claim_brief.encode('utf-8')
        #     settle_date = ''
        #
        #     if res['claim_cause'] == None or res['claim_cause'] == False:
        #         s_claim_cause = 0
        #     else:
        #         s_claim_cause = res['claim_cause']
        #     if res['settle_amount'] == None or res['settle_amount'] == False:
        #         s_settle_amount = 0
        #     else:
        #         s_settle_amount = res['settle_amount']
        #
        #     if res['claim_amount'] == None or res['claim_amount'] == False:
        #         s_claim_amount = 0
        #     else:
        #         s_claim_amount = res['claim_amount']
        #
        #     if res['settle_date'] != None:
        #         settle_date = res['settle_date']
        #     if res['settle_reputation_date'] != None:
        #         settle_date = res['settle_reputation_date']
        #
        #     s_total_claim_amount += s_claim_amount
        #     s_total_settle_amount += s_settle_amount
        #     s_total_claim_cause += s_claim_cause
        #
        #     sheet.write(row, 1, str(res['ticket_number']), border1)
        #     sheet.write(row, 2, str(res['create_date']), bold4)
        #     sheet.write(row, 3, str(res['docket_number']), bold4)
        #     sheet.write(row, 4, res['claim_manual'], bold4)
        #     sheet.write(row, 5, str(res['insured_name']) + str(',  ') + str(res['group']), border1)
        #     sheet.write(row, 6, str(res['patient_name']) + str(',  ') + str(res['location']), border1)
        #     sheet.write(row, 7, str(res['insurer_name']) + str(',  ') + str(res['contact_person']), border1)
        #     sheet.write(row, 8, str(res['scheme_name']) + str(',  ') + str(res['policy_number']), border1)
        #     sheet.write(row, 9, str(res['surveyer_name']) + str(',  ') + str(res['policy_tpa']), border1)
        #     sheet.write(row, 10, claim_brief, border1)
        #     sheet.write(row, 11, str(res['claim_date']) + str(',  ') + str(res['claim_of_admiss']), bold4)
        #     sheet.write(row, 12, s_claim_cause, numbersformat)
        #     sheet.write(row, 13, s_claim_amount, numbersformat)
        #     sheet.write(row, 14, str(res['claim_status']), border1)
        #     sheet.write(row, 15, str(res['claim_sub_status']), border1)
        #     sheet.write(row, 16, str(res['settle_type']), border1)
        #     sheet.write(row, 17, s_settle_amount, numbersformat)
        #     sheet.write(row, 18, str(settle_date), bold4)
        #     sheet.write(row, 19, str(res['reply']), border1)
        #     row = row + 1
        #     s_no = s_no + 1
        # sheet.write(row, 11, "Total", bold2)
        # sheet.write(row, 12, s_total_claim_cause, numbersformat)
        # sheet.write(row, 13, s_total_claim_amount, numbersformat)
        # sheet.write(row, 17, s_total_settle_amount, numbersformat)
        #
        # if lines.filterby == 'group':
        #     an_iterator = itertools.groupby(usr_detail2, key=operator.itemgetter(str(lines.filterby)))
        #     o_claim_cause = 0
        #     o_settle_amount = 0
        #     o_claim_amount = 0
        #     o_total_claim_cause = 0
        #     o_total_settle_amount = 0
        #     o_total_claim_amount = 0
        #     for key, group in an_iterator:
        #         key_and_group = {key: list(group)}
        #         for i in key_and_group.iteritems():
        #             for res in i[1]:
        #                 claim_brief = res['claim_brief']
        #                 claim_brief.encode('utf-8')
        #                 settle_date = ''
        #
        #                 if res['claim_cause'] == None or res['claim_cause'] == False:
        #                     o_claim_cause = 0
        #                 else:
        #                     o_claim_cause = res['claim_cause']
        #                 if res['settle_amount'] == None or res['settle_amount'] == False:
        #                     o_settle_amount = 0
        #                 else:
        #                     o_settle_amount = res['settle_amount']
        #
        #                 if res['claim_amount'] == None or res['claim_amount'] == False:
        #                     o_claim_amount = 0
        #                 else:
        #                     o_claim_amount = res['claim_amount']
        #
        #                 if res['settle_date'] != None:
        #                     settle_date = res['settle_date']
        #                 if res['settle_reputation_date'] != None:
        #                     settle_date = res['settle_reputation_date']
        #
        #                 o_total_claim_amount += o_claim_amount
        #                 o_total_settle_amount += o_settle_amount
        #                 o_total_claim_cause += o_claim_cause
        #
        #                 sheet.write(row, 1, str(res['ticket_number']), border1)
        #                 sheet.write(row, 2, str(res['create_date']), bold4)
        #                 sheet.write(row, 3, str(res['docket_number']), bold4)
        #                 sheet.write(row, 4, res['claim_manual'], bold4)
        #                 sheet.write(row, 5, str(res['insured_name']) + str(',  ') + str(i[0]), border1)
        #                 sheet.write(row, 6, str(res['patient_name']) + str(',  ') + str(res['location']), border1)
        #                 sheet.write(row, 7, str(res['insurer_name']) + str(',  ') + str(res['contact_person']), border1)
        #                 sheet.write(row, 8, str(res['scheme_name']) + str(',  ') + str(res['policy_number']), border1)
        #                 sheet.write(row, 9, str(res['surveyer_name']) + str(',  ') + str(res['policy_tpa']), border1)
        #                 sheet.write(row, 10, claim_brief, border1)
        #                 sheet.write(row, 11, str(res['claim_date']) + str(',  ') + str(res['claim_of_admiss']), bold4)
        #                 sheet.write(row, 12, o_claim_cause, numbersformat)
        #                 sheet.write(row, 13, o_claim_amount, numbersformat)
        #                 sheet.write(row, 14, str(res['claim_status']), border1)
        #                 sheet.write(row, 15, str(res['claim_sub_status']), border1)
        #                 sheet.write(row, 16, str(res['settle_type']), border1)
        #                 sheet.write(row, 17, o_settle_amount, numbersformat)
        #                 sheet.write(row, 18, str(settle_date), bold4)
        #                 sheet.write(row, 19, str(res['reply']), border1)
        #                 row = row + 1
        #                 s_no = s_no + 1
        #             sheet.write(row, 11, "Total", bold2)
        #             sheet.write(row, 12, o_total_claim_cause, numbersformat)
        #             sheet.write(row, 13, o_total_claim_amount, numbersformat)
        #             sheet.write(row, 17, o_total_settle_amount, numbersformat)
        #
        # if lines.filterby == 'client':
        #     an_iterator = itertools.groupby(usr_detail2, key=operator.itemgetter(str(lines.filterby)))
        #     o_claim_cause = 0
        #     o_settle_amount = 0
        #     o_claim_amount = 0
        #     o_total_claim_cause = 0
        #     o_total_settle_amount = 0
        #     o_total_claim_amount = 0
        #     for key, group in an_iterator:
        #         key_and_group = {key: list(group)}
        #         for i in key_and_group.iteritems():
        #             for res in i[1]:
        #                 claim_brief = res['claim_brief']
        #                 claim_brief.encode('utf-8')
        #                 settle_date = ''
        #
        #                 if res['claim_cause'] == None or res['claim_cause'] == False:
        #                     o_claim_cause = 0
        #                 else:
        #                     o_claim_cause = res['claim_cause']
        #                 if res['settle_amount'] == None or res['settle_amount'] == False:
        #                     o_settle_amount = 0
        #                 else:
        #                     o_settle_amount = res['settle_amount']
        #
        #                 if res['claim_amount'] == None or res['claim_amount'] == False:
        #                     o_claim_amount = 0
        #                 else:
        #                     o_claim_amount = res['claim_amount']
        #
        #                 if res['settle_date'] != None:
        #                     settle_date = res['settle_date']
        #                 if res['settle_reputation_date'] != None:
        #                     settle_date = res['settle_reputation_date']
        #
        #                 o_total_claim_amount += o_claim_amount
        #                 o_total_settle_amount += o_settle_amount
        #                 o_total_claim_cause += o_claim_cause
        #
        #                 sheet.write(row, 1, str(res['ticket_number']), border1)
        #                 sheet.write(row, 2, str(res['create_date']), bold4)
        #                 sheet.write(row, 3, str(res['docket_number']), bold4)
        #                 sheet.write(row, 4, res['claim_manual'], bold4)
        #                 sheet.write(row, 5, str(res['insured_name']) + str(',  ') + str(i[0]), border1)
        #                 sheet.write(row, 6, str(res['patient_name']) + str(',  ') + str(res['location']), border1)
        #                 sheet.write(row, 7, str(res['insurer_name']) + str(',  ') + str(res['contact_person']), border1)
        #                 sheet.write(row, 8, str(res['scheme_name']) + str(',  ') + str(res['policy_number']), border1)
        #                 sheet.write(row, 9, str(res['surveyer_name']) + str(',  ') + str(res['policy_tpa']), border1)
        #                 sheet.write(row, 10, claim_brief, border1)
        #                 sheet.write(row, 11, str(res['claim_date']) + str(',  ') + str(res['claim_of_admiss']), bold4)
        #                 sheet.write(row, 12, o_claim_cause, numbersformat)
        #                 sheet.write(row, 13, o_claim_amount, numbersformat)
        #                 sheet.write(row, 14, str(res['claim_status']), border1)
        #                 sheet.write(row, 15, str(res['claim_sub_status']), border1)
        #                 sheet.write(row, 16, str(res['settle_type']), border1)
        #                 sheet.write(row, 17, o_settle_amount, numbersformat)
        #                 sheet.write(row, 18, str(settle_date), bold4)
        #                 sheet.write(row, 19, str(res['reply']), border1)
        #                 row = row + 1
        #                 s_no = s_no + 1
        #             sheet.write(row, 11, "Total", bold2)
        #             sheet.write(row, 12, o_total_claim_cause, numbersformat)
        #             sheet.write(row, 13, o_total_claim_amount, numbersformat)
        #             sheet.write(row, 17, o_total_settle_amount, numbersformat)
        # ##### Closing of the  Rejected  Claim  ##########
        # row = row + 3
        # sheet.write(row, 1, ('Claims rejected/withdrawn during the period ' + str(quat)), bold)
        # row += 1
        #
        # r_claim_cause = 0
        # r_settle_amount = 0
        # r_claim_amount = 0
        # r_total_claim_cause = 0
        # r_total_settle_amount = 0
        # r_total_claim_amount = 0
        # for res in usr_detail1:
        #     claim_brief = res['claim_brief']
        #     claim_brief.encode('utf-8')
        #     settle_date = ''
        #
        #     if res['claim_cause'] == None or res['claim_cause'] == False:
        #         r_claim_cause = 0
        #     else:
        #         r_claim_cause = res['claim_cause']
        #     if res['settle_amount'] == None or res['settle_amount'] == False:
        #         r_settle_amount = 0
        #     else:
        #         r_settle_amount = res['settle_amount']
        #
        #     if res['claim_amount'] == None or res['claim_amount'] == False:
        #         r_claim_amount = 0
        #     else:
        #        r_claim_amount = res['claim_amount']
        #
        #     if res['settle_date'] != None:
        #         settle_date = res['settle_date']
        #     if res['settle_reputation_date'] != None:
        #         settle_date = res['settle_reputation_date']
        #
        #     r_total_claim_amount += r_claim_amount
        #     r_total_settle_amount += r_settle_amount
        #     r_total_claim_cause += r_claim_cause
        #
        #     sheet.write(row, 1, str(res['ticket_number']), border1)
        #     sheet.write(row, 2, str(res['create_date']), bold4)
        #     sheet.write(row, 3, str(res['docket_number']), bold4)
        #     sheet.write(row, 4, res['claim_manual'], bold4)
        #     sheet.write(row, 5, str(res['insured_name']) + str(',  ') + str(res['group']), border1)
        #     sheet.write(row, 6, str(res['patient_name']) + str(',  ') + str(res['location']), border1)
        #     sheet.write(row, 7, str(res['insurer_name']) + str(',  ') + str(res['contact_person']), border1)
        #     sheet.write(row, 8, str(res['scheme_name']) + str(',  ') + str(res['policy_number']), border1)
        #     sheet.write(row, 9, str(res['surveyer_name']) + str(',  ') + str(res['policy_tpa']), border1)
        #     sheet.write(row, 10, claim_brief, border1)
        #     sheet.write(row, 11, str(res['claim_date']) + str(',  ') + str(res['claim_of_admiss']), bold4)
        #     sheet.write(row, 12, r_claim_cause, numbersformat)
        #     sheet.write(row, 13, r_claim_amount, numbersformat)
        #     sheet.write(row, 14, str(res['claim_status']), border1)
        #     sheet.write(row, 15, str(res['claim_sub_status']), border1)
        #     sheet.write(row, 16, str(res['settle_type']), border1)
        #     sheet.write(row, 17, r_settle_amount, numbersformat)
        #     sheet.write(row, 18, str(settle_date), bold4)
        #     sheet.write(row, 19, str(res['reply']), border1)
        #     row = row + 1
        #     s_no = s_no + 1
        # sheet.write(row, 11, "Total", bold2)
        # sheet.write(row, 12, r_total_claim_cause, numbersformat)
        # sheet.write(row, 13, r_total_claim_amount, numbersformat)
        # sheet.write(row, 17, r_total_settle_amount, numbersformat)
        #
        # if lines.filterby == 'group':
        #     an_iterator = itertools.groupby(usr_detail1, key=operator.itemgetter(str(lines.filterby)))
        #     o_claim_cause = 0
        #     o_settle_amount = 0
        #     o_claim_amount = 0
        #     o_total_claim_cause = 0
        #     o_total_settle_amount = 0
        #     o_total_claim_amount = 0
        #     for key, group in an_iterator:
        #         key_and_group = {key: list(group)}
        #         for i in key_and_group.iteritems():
        #             for res in i[1]:
        #                 claim_brief = res['claim_brief']
        #                 claim_brief.encode('utf-8')
        #                 settle_date = ''
        #
        #                 if res['claim_cause'] == None or res['claim_cause'] == False:
        #                     o_claim_cause = 0
        #                 else:
        #                     o_claim_cause = res['claim_cause']
        #                 if res['settle_amount'] == None or res['settle_amount'] == False:
        #                     o_settle_amount = 0
        #                 else:
        #                     o_settle_amount = res['settle_amount']
        #
        #                 if res['claim_amount'] == None or res['claim_amount'] == False:
        #                     o_claim_amount = 0
        #                 else:
        #                     o_claim_amount = res['claim_amount']
        #
        #                 if res['settle_date'] != None:
        #                     settle_date = res['settle_date']
        #                 if res['settle_reputation_date'] != None:
        #                     settle_date = res['settle_reputation_date']
        #
        #                 o_total_claim_amount += o_claim_amount
        #                 o_total_settle_amount += o_settle_amount
        #                 o_total_claim_cause += o_claim_cause
        #
        #                 sheet.write(row, 1, str(res['ticket_number']), border1)
        #                 sheet.write(row, 2, str(res['create_date']), bold4)
        #                 sheet.write(row, 3, str(res['docket_number']), bold4)
        #                 sheet.write(row, 4, res['claim_manual'], bold4)
        #                 sheet.write(row, 5, str(res['insured_name']) + str(',  ') + str(i[0]), border1)
        #                 sheet.write(row, 6, str(res['patient_name']) + str(',  ') + str(res['location']), border1)
        #                 sheet.write(row, 7, str(res['insurer_name']) + str(',  ') + str(res['contact_person']), border1)
        #                 sheet.write(row, 8, str(res['scheme_name']) + str(',  ') + str(res['policy_number']), border1)
        #                 sheet.write(row, 9, str(res['surveyer_name']) + str(',  ') + str(res['policy_tpa']), border1)
        #                 sheet.write(row, 10, claim_brief, border1)
        #                 sheet.write(row, 11, str(res['claim_date']) + str(',  ') + str(res['claim_of_admiss']), bold4)
        #                 sheet.write(row, 12, o_claim_cause, numbersformat)
        #                 sheet.write(row, 13, o_claim_amount, numbersformat)
        #                 sheet.write(row, 14, str(res['claim_status']), border1)
        #                 sheet.write(row, 15, str(res['claim_sub_status']), border1)
        #                 sheet.write(row, 16, str(res['settle_type']), border1)
        #                 sheet.write(row, 17, o_settle_amount, numbersformat)
        #                 sheet.write(row, 18, str(settle_date), bold4)
        #                 sheet.write(row, 19, str(res['reply']), border1)
        #                 row = row + 1
        #                 s_no = s_no + 1
        #             sheet.write(row, 11, "Total", bold2)
        #             sheet.write(row, 12, o_total_claim_cause, numbersformat)
        #             sheet.write(row, 13, o_total_claim_amount, numbersformat)
        #             sheet.write(row, 17, o_total_settle_amount, numbersformat)
        #
        # if lines.filterby == 'client':
        #     an_iterator = itertools.groupby(usr_detail1, key=operator.itemgetter(str(lines.filterby)))
        #     o_claim_cause = 0
        #     o_settle_amount = 0
        #     o_claim_amount = 0
        #     o_total_claim_cause = 0
        #     o_total_settle_amount = 0
        #     o_total_claim_amount = 0
        #     for key, group in an_iterator:
        #         key_and_group = {key: list(group)}
        #         for i in key_and_group.iteritems():
        #             for res in i[1]:
        #                 claim_brief = res['claim_brief']
        #                 claim_brief.encode('utf-8')
        #                 settle_date = ''
        #
        #                 if res['claim_cause'] == None or res['claim_cause'] == False:
        #                     o_claim_cause = 0
        #                 else:
        #                     o_claim_cause = res['claim_cause']
        #                 if res['settle_amount'] == None or res['settle_amount'] == False:
        #                     o_settle_amount = 0
        #                 else:
        #                     o_settle_amount = res['settle_amount']
        #
        #                 if res['claim_amount'] == None or res['claim_amount'] == False:
        #                     o_claim_amount = 0
        #                 else:
        #                     o_claim_amount = res['claim_amount']
        #
        #                 if res['settle_date'] != None:
        #                     settle_date = res['settle_date']
        #                 if res['settle_reputation_date'] != None:
        #                     settle_date = res['settle_reputation_date']
        #
        #                 o_total_claim_amount += o_claim_amount
        #                 o_total_settle_amount += o_settle_amount
        #                 o_total_claim_cause += o_claim_cause
        #
        #                 sheet.write(row, 1, str(res['ticket_number']), border1)
        #                 sheet.write(row, 2, str(res['create_date']), bold4)
        #                 sheet.write(row, 3, str(res['docket_number']), bold4)
        #                 sheet.write(row, 4, res['claim_manual'], bold4)
        #                 sheet.write(row, 5, str(res['insured_name']) + str(',  ') + str(i[0]), border1)
        #                 sheet.write(row, 6, str(res['patient_name']) + str(',  ') + str(res['location']), border1)
        #                 sheet.write(row, 7, str(res['insurer_name']) + str(',  ') + str(res['contact_person']), border1)
        #                 sheet.write(row, 8, str(res['scheme_name']) + str(',  ') + str(res['policy_number']), border1)
        #                 sheet.write(row, 9, str(res['surveyer_name']) + str(',  ') + str(res['policy_tpa']), border1)
        #                 sheet.write(row, 10, claim_brief, border1)
        #                 sheet.write(row, 11, str(res['claim_date']) + str(',  ') + str(res['claim_of_admiss']), bold4)
        #                 sheet.write(row, 12, o_claim_cause, numbersformat)
        #                 sheet.write(row, 13, o_claim_amount, numbersformat)
        #                 sheet.write(row, 14, str(res['claim_status']), border1)
        #                 sheet.write(row, 15, str(res['claim_sub_status']), border1)
        #                 sheet.write(row, 16, str(res['settle_type']), border1)
        #                 sheet.write(row, 17, o_settle_amount, numbersformat)
        #                 sheet.write(row, 18, str(settle_date), bold4)
        #                 sheet.write(row, 19, str(res['reply']), border1)
        #                 row = row + 1
        #                 s_no = s_no + 1
        #             sheet.write(row, 11, "Total", bold2)
        #             sheet.write(row, 12, o_total_claim_cause, numbersformat)
        #             sheet.write(row, 13, o_total_claim_amount, numbersformat)
        #             sheet.write(row, 17, o_total_settle_amount, numbersformat)
        #
        #
        # ##### Closing of the Claim pending ##########
        # row = row +3
        # sheet.write(row, 1, ('Claims pending at the end of the period  ( ' +str(lines.fiscal_year.date_end) + ')'), bold)
        # row = row + 1
        # s_no = 1
        #
        # claim_cause=0
        # settle_amount=0
        # claim_amount=0
        # total_claim_cause =0
        # total_settle_amount =0
        # total_claim_amount =0
        # for res in usr_detail4:
        #     claim_brief=res['claim_brief']
        #     claim_brief.encode('utf-8')
        #     settle_date = ''
        #
        #     if res['claim_cause'] == None or res['claim_cause'] == False:
        #         claim_cause = 0
        #     else:
        #         claim_cause = res['claim_cause']
        #     if res['settle_amount'] == None or res['settle_amount'] == False:
        #         settle_amount = 0
        #     else:
        #         settle_amount = res['settle_amount']
        #
        #     if res['claim_amount'] == None or res['claim_amount'] == False:
        #         claim_amount = 0
        #     else:
        #         claim_amount = res['claim_amount']
        #
        #     if res['settle_date'] != None:
        #         settle_date = res['settle_date']
        #     if res['settle_reputation_date'] != None:
        #         settle_date = res['settle_reputation_date']
        #
        #     total_claim_amount += claim_amount
        #     total_settle_amount += settle_amount
        #     total_claim_cause += claim_cause
        #
        #     sheet.write(row, 1, str(res['ticket_number']), border1)
        #     sheet.write(row, 2, str(res['create_date']), bold4)
        #     sheet.write(row, 3, str(res['docket_number']), bold4)
        #     sheet.write(row, 4, res['claim_manual'], bold4)
        #     sheet.write(row, 5, str(res['insured_name']) + str(',  ') + str(res['group']), border1)
        #     sheet.write(row, 6, str(res['patient_name']) + str(',  ') + str(res['location']), border1)
        #     sheet.write(row, 7, str(res['insurer_name']) + str(',  ') + str(res['contact_person']), border1)
        #     sheet.write(row, 8, str(res['scheme_name']) + str(',  ') + str(res['policy_number']), border1)
        #     sheet.write(row, 9, str(res['surveyer_name']) + str(',  ') + str(res['policy_tpa']), border1)
        #     sheet.write(row, 10, claim_brief, border1)
        #     sheet.write(row, 11, str(res['claim_date']) + str(',  ') + str(res['claim_of_admiss']), bold4)
        #     sheet.write(row, 12, claim_cause, numbersformat)
        #     sheet.write(row, 13, claim_amount, numbersformat)
        #     sheet.write(row, 14, str(res['claim_status']), border1)
        #     sheet.write(row, 15, str(res['claim_sub_status']), border1)
        #     sheet.write(row, 16, str(res['settle_type']), border1)
        #     sheet.write(row, 17, settle_amount, numbersformat)
        #     sheet.write(row, 18, str(settle_date), bold4)
        #     sheet.write(row, 19, str(res['reply']), border1)
        #     row = row + 1
        #     s_no = s_no + 1
        # sheet.write(row, 11, "Total", bold2)
        # sheet.write(row, 12, total_claim_cause, numbersformat)
        # sheet.write(row, 13, total_claim_amount, numbersformat)
        # sheet.write(row, 17, total_settle_amount, numbersformat)
        #
        # if lines.filterby == 'group':
        #     an_iterator = itertools.groupby(usr_detail4, key=operator.itemgetter(str(lines.filterby)))
        #     o_claim_cause = 0
        #     o_settle_amount = 0
        #     o_claim_amount = 0
        #     o_total_claim_cause = 0
        #     o_total_settle_amount = 0
        #     o_total_claim_amount = 0
        #     for key, group in an_iterator:
        #         key_and_group = {key: list(group)}
        #         for i in key_and_group.iteritems():
        #             for res in i[1]:
        #                 claim_brief = res['claim_brief']
        #                 claim_brief.encode('utf-8')
        #                 settle_date = ''
        #
        #                 if res['claim_cause'] == None or res['claim_cause'] == False:
        #                     o_claim_cause = 0
        #                 else:
        #                     o_claim_cause = res['claim_cause']
        #                 if res['settle_amount'] == None or res['settle_amount'] == False:
        #                     o_settle_amount = 0
        #                 else:
        #                     o_settle_amount = res['settle_amount']
        #
        #                 if res['claim_amount'] == None or res['claim_amount'] == False:
        #                     o_claim_amount = 0
        #                 else:
        #                     o_claim_amount = res['claim_amount']
        #
        #                 if res['settle_date'] != None:
        #                     settle_date = res['settle_date']
        #                 if res['settle_reputation_date'] != None:
        #                     settle_date = res['settle_reputation_date']
        #
        #                 o_total_claim_amount += o_claim_amount
        #                 o_total_settle_amount += o_settle_amount
        #                 o_total_claim_cause += o_claim_cause
        #
        #                 sheet.write(row, 1, str(res['ticket_number']), border1)
        #                 sheet.write(row, 2, str(res['create_date']), bold4)
        #                 sheet.write(row, 3, str(res['docket_number']), bold4)
        #                 sheet.write(row, 4, res['claim_manual'], bold4)
        #                 sheet.write(row, 5, str(res['insured_name']) + str(',  ') + str(i[0]), border1)
        #                 sheet.write(row, 6, str(res['patient_name']) + str(',  ') + str(res['location']), border1)
        #                 sheet.write(row, 7, str(res['insurer_name']) + str(',  ') + str(res['contact_person']), border1)
        #                 sheet.write(row, 8, str(res['scheme_name']) + str(',  ') + str(res['policy_number']), border1)
        #                 sheet.write(row, 9, str(res['surveyer_name']) + str(',  ') + str(res['policy_tpa']), border1)
        #                 sheet.write(row, 10, claim_brief, border1)
        #                 sheet.write(row, 11, str(res['claim_date']) + str(',  ') + str(res['claim_of_admiss']), bold4)
        #                 sheet.write(row, 12, o_claim_cause, numbersformat)
        #                 sheet.write(row, 13, o_claim_amount, numbersformat)
        #                 sheet.write(row, 14, str(res['claim_status']), border1)
        #                 sheet.write(row, 15, str(res['claim_sub_status']), border1)
        #                 sheet.write(row, 16, str(res['settle_type']), border1)
        #                 sheet.write(row, 17, o_settle_amount, numbersformat)
        #                 sheet.write(row, 18, str(settle_date), bold4)
        #                 sheet.write(row, 19, str(res['reply']), border1)
        #                 row = row + 1
        #                 s_no = s_no + 1
        #             sheet.write(row, 11, "Total", bold2)
        #             sheet.write(row, 12, o_total_claim_cause, numbersformat)
        #             sheet.write(row, 13, o_total_claim_amount, numbersformat)
        #             sheet.write(row, 17, o_total_settle_amount, numbersformat)
        #
        # if lines.filterby == 'client':
        #     an_iterator = itertools.groupby(usr_detail4, key=operator.itemgetter(str(lines.filterby)))
        #     o_claim_cause = 0
        #     o_settle_amount = 0
        #     o_claim_amount = 0
        #     o_total_claim_cause = 0
        #     o_total_settle_amount = 0
        #     o_total_claim_amount = 0
        #     for key, group in an_iterator:
        #         key_and_group = {key: list(group)}
        #         for i in key_and_group.iteritems():
        #             for res in i[1]:
        #                 claim_brief = res['claim_brief']
        #                 claim_brief.encode('utf-8')
        #                 settle_date = ''
        #
        #                 if res['claim_cause'] == None or res['claim_cause'] == False:
        #                     o_claim_cause = 0
        #                 else:
        #                     o_claim_cause = res['claim_cause']
        #                 if res['settle_amount'] == None or res['settle_amount'] == False:
        #                     o_settle_amount = 0
        #                 else:
        #                     o_settle_amount = res['settle_amount']
        #
        #                 if res['claim_amount'] == None or res['claim_amount'] == False:
        #                     o_claim_amount = 0
        #                 else:
        #                     o_claim_amount = res['claim_amount']
        #
        #                 if res['settle_date'] != None:
        #                     settle_date = res['settle_date']
        #                 if res['settle_reputation_date'] != None:
        #                     settle_date = res['settle_reputation_date']
        #
        #                 o_total_claim_amount += o_claim_amount
        #                 o_total_settle_amount += o_settle_amount
        #                 o_total_claim_cause += o_claim_cause
        #
        #                 sheet.write(row, 1, str(res['ticket_number']), border1)
        #                 sheet.write(row, 2, str(res['create_date']), bold4)
        #                 sheet.write(row, 3, str(res['docket_number']), bold4)
        #                 sheet.write(row, 4, res['claim_manual'], bold4)
        #                 sheet.write(row, 5, str(res['insured_name']) + str(',  ') + str(i[0]), border1)
        #                 sheet.write(row, 6, str(res['patient_name']) + str(',  ') + str(res['location']), border1)
        #                 sheet.write(row, 7, str(res['insurer_name']) + str(',  ') + str(res['contact_person']), border1)
        #                 sheet.write(row, 8, str(res['scheme_name']) + str(',  ') + str(res['policy_number']), border1)
        #                 sheet.write(row, 9, str(res['surveyer_name']) + str(',  ') + str(res['policy_tpa']), border1)
        #                 sheet.write(row, 10, claim_brief, border1)
        #                 sheet.write(row, 11, str(res['claim_date']) + str(',  ') + str(res['claim_of_admiss']), bold4)
        #                 sheet.write(row, 12, o_claim_cause, numbersformat)
        #                 sheet.write(row, 13, o_claim_amount, numbersformat)
        #                 sheet.write(row, 14, str(res['claim_status']), border1)
        #                 sheet.write(row, 15, str(res['claim_sub_status']), border1)
        #                 sheet.write(row, 16, str(res['settle_type']), border1)
        #                 sheet.write(row, 17, o_settle_amount, numbersformat)
        #                 sheet.write(row, 18, str(settle_date), bold4)
        #                 sheet.write(row, 19, str(res['reply']), border1)
        #                 row = row + 1
        #                 s_no = s_no + 1
        #             sheet.write(row, 11, "Total", bold2)
        #             sheet.write(row, 12, o_total_claim_cause, numbersformat)
        #             sheet.write(row, 13, o_total_claim_amount, numbersformat)
        #             sheet.write(row, 17, o_total_settle_amount, numbersformat)
        #

    print("Report Printed")


GeneralXlsx('report.clickbima.policy_detail.xlsx', 'policydetail.report')

