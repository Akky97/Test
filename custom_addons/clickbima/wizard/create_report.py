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

class Policyreport(models.TransientModel):
    _name = "create.report"
    _description = "Policy Transaction Report"

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    monthly = fields.Selection([('none','None'),('monthly', 'Monthly'), ('quatar', 'Quarterly')], default='none')
    quarter = fields.Selection([('q1', 'Quarter 1'), ('q2', 'Quarter 2'), ('q3', 'Quarter 3'), ('q4', 'Quarter 4')],
                               string='Quarter')
    groupby = fields.Selection([('create_date', 'Create Date'), ('insurername123', 'Insurer Name')],string="Group BY")
    fiscal_year =fields.Many2one(comodel_name='date.range',string="Fiscal Year", default=lambda self: self.env['date.range'].search([('name', '=', 'FY2021')]))
    months = fields.Selection(
        [('01-01', 'January'), ('01-02', 'February'), ('01-03', 'March'), ('01-04', 'April'), ('01-05', 'May'), ('01-06', 'June'),
         ('01-07', 'July'), ('01-08', 'August'), ('01-09', 'September'), ('01-10', 'October'), ('01-11', 'November'),
         ('01-12', 'December')])

    @api.onchange('quarter')
    def onchange_quarter(self):
        if self.quarter:
            if (self.quarter == 'q1'):
                self.date_from = "2020-04-01"
                self.date_to = "2020-06-30"
            elif (self.quarter == 'q2'):
                self.date_from = "2020-07-01"
                self.date_to = "2020-09-30"
            elif (self.quarter == 'q3'):
                self.date_from = "2020-10-01"
                self.date_to = "2020-12-31"
            elif (self.quarter == 'q4'):
                self.date_from = "2020-01-01"
                self.date_to = "2020-03-31"
            else:
                return ("Please select any")

    # @api.multi
    # def _get_fiscal_year(self, cr, uid, context=None):
    #     res = self.pool.get('date.range').search(cr, uid, [('name', '=', 'FY2021')], context=context)
    #     return res and res[0] or False


    # @api.multi
    # def generate_xlsx_report(self):
    #     data = {}
    #     print ("1")
    #     data['form'] = self.read([])[0]
    #     print ("2")
    #     print (data)
    #     return self.env['report'].get_action(self, report_name='clickbima.res_partner.xlsx', data=data)

#general report
    # @api.multi
    # def test_report(self):
    #     data = {}
    #     print ("1")
    #     data['form'] = self.read([])[0]
    #     print ("2")
    #     print (data)
    #     return self.env['report'].get_action(self, report_name='clickbima.general_report_excel.xlsx', data=data)

#non life insurerwise
    # @api.multi
    # def test_report1(self):
    #     data = {}
    #     print ("1")
    #     data['form'] = self.read([])[0]
    #     print ("2")
    #     print (data)
    #     return self.env['report'].get_action(self, report_name='clickbima.non_life_insurer.xlsx', data=data)

# non life insurerwise
    @api.multi
    def test_report2(self):
        data = {}
        print("1")
        data['form'] = self.read([])[0]
        print("2")
        print(data)
        return self.env['report'].get_action(self, report_name='clickbima.non_life_top10_client.xlsx', data=data)

    # def create_report_xlsx(self):
    #     usr_detail = self.env['policytransaction'].search(
    #         [('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to)])
    #     print ("user------>", usr_detail)


from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
# class PartnerXlsx(ReportXlsx):
#         def generate_xlsx_report(self, workbook, data, lines):
#
#             # usr_detail = self.env['policytransaction'].search(
#             #     [('create_date', '>=', lines.date_from), ('create_date', '<=', lines.date_to)])
#             import odoo
#             db_name = odoo.tools.config.get('db_name')
#             registry = Registry(db_name)
#             # date_from=lines.date_from + ' 00:00:00'
#             # date_to=lines.date_to + ' 23:59:59'
#             with registry.cursor() as cr:
#
#                 query = "select t1.regsitersrno as srno,t1.name as docketno,"\
#                         " t1.pipeline_id as pipelineno,t1.sale_order_id as quotationno,"\
#                         " t1.proposaldate as proposaldate,t1.suminsured as sumi,t1.rm as salesperson,"\
#                         " t1.ref as referby,t1.controlno as ennom,sum(t1.grossprem) as grossprem,"\
#                         " sum(t1.netprem) as net,t1.startfrom as startdate,t1.expiry as enddate,"\
#                         " t8.name as location,t10.name as insurername,t3.name as registername,"\
#                         " t4.name as insurerbranch,t5.name as subcategory,t6.name as csc,t7.name as event"\
#                         " from policytransaction as t1 left join res_partner as t10 on t10.id=t1.insurername123"\
#                         " left join subdata_subdata as t3 on t3.id=t1.registername1"\
#                         " left join insurerbranch as t4 on t4.id=t1.insurerbranch"\
#                         " left join subcategory_subcategory as t5 on t5.id=t1.name1"\
#                         " left join utm_medium as t6 on t6.id=t1.csc"\
#                         " left join utm_source as t7 on t7.id=t1.event left join clickbima_clickbima as t8 on t8.id=t1.location "
#
#                 if lines.fiscal_year and lines.monthly=="none" and not lines.monthly=="quatar" and not lines.monthly=="monthly":
#                     query +=" where t1.create_date  BETWEEN '"+ str(lines.fiscal_year.date_start) + "' AND '"+ str(lines.fiscal_year.date_end) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
#                             "t7.name,t8.name,t1.regsitersrno,t1.name,t1.proposaldate,t1.suminsured,t1.rm,t1.ref,t1.controlno,t1.startfrom,t1.expiry"
#
#
#                 if lines.fiscal_year and lines.monthly=="monthly" and not lines.monthly=="none" and not lines.monthly=="quatar":
#                     year =lines.fiscal_year.name
#                     print year,"year"
#                     if lines.months =='01-01':
#                         query +=" where t1.create_date  BETWEEN '"+ str(lines.fiscal_year.date_start) + "' AND '"+ str(lines.fiscal_year.date_end) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
#                                 "t7.name,t8.name,t1.regsitersrno,t1.name,t1.proposaldate,t1.suminsured,t1.rm,t1.ref,t1.controlno,t1.startfrom,t1.expiry"
#
#                     if lines.months =='01-02':
#                         query +=" where t1.create_date  BETWEEN '"+ str(lines.fiscal_year.date_start) + "' AND '"+ str(lines.fiscal_year.date_end) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
#                                 "t7.name,t8.name,t1.regsitersrno,t1.name,t1.proposaldate,t1.suminsured,t1.rm,t1.ref,t1.controlno,t1.startfrom,t1.expiry"
#
#                     if lines.months =='01-03':
#                         query +=" where t1.create_date  BETWEEN '"+ str(lines.fiscal_year.date_start) + "' AND '"+ str(lines.fiscal_year.date_end) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
#                                 "t7.name,t8.name,t1.regsitersrno,t1.name,t1.proposaldate,t1.suminsured,t1.rm,t1.ref,t1.controlno,t1.startfrom,t1.expiry"
#
#                     if lines.months =='01-04':
#                         query +=" where t1.create_date  BETWEEN '"+ str(lines.fiscal_year.date_start) + "' AND '"+ str(lines.fiscal_year.date_end) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
#                                 "t7.name,t8.name,t1.regsitersrno,t1.name,t1.proposaldate,t1.suminsured,t1.rm,t1.ref,t1.controlno,t1.startfrom,t1.expiry"
#
#                     if lines.months == '01-05':
#                         query +=" where t1.create_date  BETWEEN '"+ str(lines.fiscal_year.date_start) + "' AND '"+ str(lines.fiscal_year.date_end) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
#                                 "t7.name,t8.name,t1.regsitersrno,t1.name,t1.proposaldate,t1.suminsured,t1.rm,t1.ref,t1.controlno,t1.startfrom,t1.expiry"
#
#                     if lines.months == '01-06':
#                         query +=" where t1.create_date  BETWEEN '"+ str(lines.fiscal_year.date_start) + "' AND '"+ str(lines.fiscal_year.date_end) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
#                                 "t7.name,t8.name,t1.regsitersrno,t1.name,t1.proposaldate,t1.suminsured,t1.rm,t1.ref,t1.controlno,t1.startfrom,t1.expiry"
#
#                     if lines.months == '01-07':
#                         query +=" where t1.create_date  BETWEEN '"+ str(lines.fiscal_year.date_start) + "' AND '"+ str(lines.fiscal_year.date_end) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
#                                 "t7.name,t8.name,t1.regsitersrno,t1.name,t1.proposaldate,t1.suminsured,t1.rm,t1.ref,t1.controlno,t1.startfrom,t1.expiry"
#
#                     if lines.months == '01-08':
#                         query +=" where t1.create_date  BETWEEN '"+ str(lines.fiscal_year.date_start) + "' AND '"+ str(lines.fiscal_year.date_end) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
#                                 "t7.name,t8.name,t1.regsitersrno,t1.name,t1.proposaldate,t1.suminsured,t1.rm,t1.ref,t1.controlno,t1.startfrom,t1.expiry"
#
#                     if lines.months == '01-09':
#                         query +=" where t1.create_date  BETWEEN '"+ str(lines.fiscal_year.date_start) + "' AND '"+ str(lines.fiscal_year.date_end) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
#                                 "t7.name,t8.name,t1.regsitersrno,t1.name,t1.proposaldate,t1.suminsured,t1.rm,t1.ref,t1.controlno,t1.startfrom,t1.expiry"
#
#                     if lines.months == '01-10':
#                         query +=" where t1.create_date  BETWEEN '"+ str(lines.fiscal_year.date_start) + "' AND '"+ str(lines.fiscal_year.date_end) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
#                                 "t7.name,t8.name,t1.regsitersrno,t1.name,t1.proposaldate,t1.suminsured,t1.rm,t1.ref,t1.controlno,t1.startfrom,t1.expiry"
#
#                     if lines.months == '01-11':
#                         query +=" where t1.create_date  BETWEEN '"+ str(lines.fiscal_year.date_start) + "' AND '"+ str(lines.fiscal_year.date_end) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
#                                 "t7.name,t8.name,t1.regsitersrno,t1.name,t1.proposaldate,t1.suminsured,t1.rm,t1.ref,t1.controlno,t1.startfrom,t1.expiry"
#
#                     if lines.months == '01-12':
#                         query +=" where t1.create_date  BETWEEN '"+ str(lines.fiscal_year.date_start) + "' AND '"+ str(lines.fiscal_year.date_end) + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name," \
#                                 "t7.name,t8.name,t1.regsitersrno,t1.name,t1.proposaldate,t1.suminsured,t1.rm,t1.ref,t1.controlno,t1.startfrom,t1.expiry"
#                 if lines.quarter and  not lines.monthly =='none' and not lines.monthly =='monthly':
#                     query +=" where t1.create_date  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(lines.date_to + ' 23:59:59') + "' group by t1.pipeline_id,t1.sale_order_id,t3.name,t10.name,t4.name,t5.name,t6.name,t7.name,t8.name,t1.regsitersrno,t1.name,t1.proposaldate,t1.suminsured,t1.rm,t1.ref,t1.controlno,t1.startfrom,t1.expiry"
#
#                 cr.execute(query)
#                 usr_detail = cr.dictfetchall()
#
#                 print("user------>ss", usr_detail)
#                 report_name = "sheet 1"
#                 report_head = 'Security Insurance Brokers (India) Private Limited'
#                 report_head1 = 'New Delhi - Nehru Place'
#                 report_head2 = 'Register Name'
#
#                 print("data---->", data)
#
#                 arr = []
#                 for i in usr_detail:
#                     val = {
#                         "s.no": i['srno'],
#                         "pipelineno": i['pipelineno'],
#                         "proposal_date": i['proposaldate'],
#                         "docket_no": i['docketno'],
#                         "register_name": i['registername'],
#                         "location": i['location'],
#                         "insurer_name": i['insurername'],
#                         "insurer_branch": i['insurerbranch'],
#                         "sub_category": i['subcategory'],
#                         "suminsured": i['sumi'],
#                         "salesperson": i['salesperson'],
#                         "source": i['event'],
#                         "medium": i['csc'],
#                         "refer_by": i['referby'],
#                         "endorsment_no": i['ennom'],
#                         "netprem": i['net'],
#                         "grossprem": i['grossprem'],
#                         "start_from": i['startdate'],
#                         "expiry": i['enddate'],
#                         "quotationno": i['quotationno']
#                     }
#                     arr.append(val)
#                 print(arr)
#
#                 # One sheet by partner
#                 sheet = workbook.add_worksheet(report_name[:31])
#
#                 merge_format = workbook.add_format(
#                     {'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vleft', 'font_color': 'black'})
#                 merge_format1 = workbook.add_format(
#                     {'bold': 1, 'align': 'left', 'valign': 'vleft', 'font_color': 'black'})
#                 bold = workbook.add_format({'border': 1, 'bold': True})
#                 bold1 = workbook.add_format({'bold': True})
#                 border = workbook.add_format({'border': 1})
#                 border1 = workbook.add_format({'border': 1, 'align': 'left'})
#                 align_left = workbook.add_format({'align': 'left'})
#
#                 sheet.write(5, 6, ('Start Date : ' + str(lines.date_from) + '  to End Date : ' + str(lines.date_to)),
#                             bold1)
#
#                 sheet.write(6, 0, ('Register/Sr.No.'), bold)
#                 sheet.write(6, 1, ('Pipeline No.'), bold)
#                 sheet.write(6, 2, ('Quotation/Proposal No.'), bold)
#                 sheet.write(6, 3, ('Proposal Date'), bold)
#                 sheet.write(6, 4, ('Docket No.'), bold)
#                 sheet.write(6, 5, ('Policy Status'), bold)
#                 sheet.write(6, 6, ('Sub Category'), bold)
#                 sheet.write(6, 7, ('Insured Name'), bold)
#                 sheet.write(6, 8, ('Insurer Name'), bold)
#                 sheet.write(6, 9, ('Branch Name'), bold)
#                 sheet.write(6, 10, ('Payment Type'), bold)
#                 sheet.write(6, 11, ('Sum Insured'), bold)
#                 sheet.write(6, 12, ('Gross Premium'), bold)
#                 sheet.write(6, 13, ('Net Premium'), bold)
#                 sheet.write(6, 14, ('Other Premium'), bold)
#                 sheet.write(6, 15, ('Covernote No.'), bold)
#                 sheet.write(6, 16, ('Endorsement No.'), bold)
#                 sheet.write(6, 17, ('Start Date'), bold)
#                 sheet.write(6, 18, ('Expiry Date'), bold)
#                 sheet.write(6, 19, ('Refer By'), bold)
#                 sheet.write(6, 20, ('Sales Person'), bold)
#                 sheet.write(6, 21, ('Source(Employee)'), bold)
#                 sheet.write(6, 22, ('Medium(POS)'), bold)
#
#                 # increasing width of column
#                 sheet.set_column('B:B', 20)
#                 sheet.set_column('C:C', 20)
#                 sheet.set_column('D:D', 20)
#                 sheet.set_column('E:E', 20)
#                 sheet.set_column('F:F', 20)
#                 sheet.set_column('G:G', 20)
#                 sheet.set_column('H:H', 20)
#                 sheet.set_column('I:I', 20)
#                 sheet.set_column('J:J', 20)
#                 sheet.set_column('K:K', 20)
#                 sheet.set_column('L:L', 20)
#                 sheet.set_column('M:M', 20)
#                 sheet.set_column('N:N', 20)
#                 sheet.set_column('O:O', 20)
#                 sheet.set_column('P:P', 20)
#                 sheet.set_column('Q:Q', 20)
#                 sheet.set_column('R:R', 20)
#                 sheet.set_column('S:S', 20)
#                 sheet.set_column('T:T', 20)
#                 sheet.set_column('U:U', 20)
#                 sheet.set_column('V:V', 20)
#                 sheet.set_column('W:W', 20)
#                 sheet.merge_range('A1:W1', report_head, merge_format1)
#                 sheet.merge_range('A2:W2', report_head1, merge_format1)
#                 sheet.merge_range('A3:W3', report_head2, merge_format1)
#
#                 row = 7
#                 s_no = 1
#                 for res in arr:
#                     sheet.write(row, 0, res['register_name'], border1)
#                     sheet.write(row, 1, res['pipelineno'], border)
#                     sheet.write(row, 2, res['quotationno'], border)
#                     sheet.write(row, 3, res['proposal_date'], border)
#                     sheet.write(row, 4, res['docket_no'], border)
#                     # sheet.write(row, 5, res['policy_status'], border )
#                     sheet.write(row, 6, res['sub_category'], border)
#                     # sheet.write(row, 7, res['insured_name'], border )
#                     sheet.write(row, 8, res['insurer_name'], border)
#                     sheet.write(row, 9, res['insurer_branch'], border)
#                     # sheet.write(row, 10, res['payment_type'], border )
#                     sheet.write(row, 11, res['suminsured'], border)
#                     sheet.write(row, 12, res['grossprem'], border)
#                     sheet.write(row, 13, res['netprem'], border)
#                     # sheet.write(row, 14, res['otherprem'], border )
#                     # sheet.write(row, 15, res['covernoteno'], border )
#                     sheet.write(row, 16, res['endorsment_no'], border)
#                     sheet.write(row, 17, res['start_from'], border)
#                     sheet.write(row, 18, res['expiry'], border)
#                     sheet.write(row, 19, res['refer_by'], border)
#                     sheet.write(row, 20, res['salesperson'], border)
#                     sheet.write(row, 21, res['source'], border)
#                     sheet.write(row, 22, res['medium'], border)
#
#                     row = row + 1
#                     s_no = s_no + 1
#                     print("Array printed for s.no :", s_no - 1)
#
#             print("Report Printed")
# PartnerXlsx('report.clickbima.res_partner.xlsx', 'create.report')

#general report:
# class GeneralXlsx(ReportXlsx):
#     def generate_xlsx_report(self, workbook, data, lines):
#
#         import odoo
#         db_name = odoo.tools.config.get('db_name')
#         registry = Registry(db_name)
#         # date_from = lines.date_from + ' 00:00:00'
#         # date_to = lines.date_to + ' 23:59:59'
#         with registry.cursor() as cr:
#             query = "select t2.name as registername, count(t1.registername1) as total," \
#                     " sum(t1.grossprem) as grossprem,"\
#                     " sum(t1.brokerageprem) as brokerageprem"\
#                     " from policytransaction as t1 left join subdata_subdata as t2 on t2.id = t1.registername1"\
#
#             # query = "select t1.regsitersrno as srno,t1.suminsured as sumi," \
#             #         " sum(t1.netprem) as net,sum(t1.tppremium) as thirdprem,"\
#             #         " sum(t1.servicetaxamt) as gst,count(t1.registername1) as totalcount,"\
#             #         " t3.name as insurername,"\
#             #         " sum(t1.grossprem) as grossprem,sum(t1.brokerageprem) as brokerageprem"\
#             #         " from policytransaction as t1 left join subdata_subdata as t2 on t2.id = t1.registername1"\
#             #         " left join res_partner as t3 on t3.id=t1.insurername123"\
#
#
#
#             if lines.fiscal_year and lines.monthly == "none" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
#                 query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' AND  grossprem>0  group by t2.name"
#
#             if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "none" and not lines.monthly == "quatar":
#                 year = lines.fiscal_year.name
#                 print year, "year"
#
#                 if lines.months == '01-01':
#                     query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' AND  grossprem>0 group by t2.name"
#
#                 if lines.months == '01-02':
#                     query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' AND  grossprem>0  group by t2.name"
#
#                 if lines.months == '01-03':
#                     query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' AND  grossprem>0  group by t2.name"
#
#                 if lines.months == '01-04':
#                     query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' AND  grossprem>0  group by t2.name"
#
#                 if lines.months == '01-05':
#                     query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' AND  grossprem>0  group by t2.name"
#
#                 if lines.months == '01-06':
#                     query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' AND  grossprem>0  group by t2.name"
#
#                 if lines.months == '01-07':
#                     query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' AND  grossprem>0  group by t2.name"
#
#                 if lines.months == '01-08':
#                     query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' AND  grossprem>0  group by t2.name"
#
#                 if lines.months == '01-09':
#                     query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' AND  grossprem>0  group by t2.name"
#
#                 if lines.months == '01-10':
#                     query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' AND  grossprem>0  group by t2.name"
#                 if lines.months == '01-11':
#                     query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' AND  grossprem>0  group by t2.name"
#                 if lines.months == '01-12':
#                     query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' AND  grossprem>0  group by t2.name"
#
#             if lines.quarter and not lines.monthly == 'none' and not lines.monthly == 'monthly':
#                 query += " where t1.create_date  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(lines.date_to + ' 23:59:59') + "' AND  grossprem>0  group by t2.name"
#             cr.execute(query)
#             usr_detail = cr.dictfetchall()
#
#
#         print ("user------>ss", usr_detail)
#         report_name = "sheet 1"
#         report_head = 'Security Insurance Broker(India) Pvt Ltd.'
#         print ("data---->", data)
#
#         arr = []
#         totalpol = 0
#         totalprem = 0
#         totalbrok = 0
#         totalperc = 0
#         for i in usr_detail:
#             totalpol+= i['total']
#             totalprem+= i['grossprem']
#             totalbrok+= i['brokerageprem']
#             totalperc+= ((i['brokerageprem']/i['grossprem']) *100)
#             val = {
#                 # "s.no": i['id'],
#                 "registername": i['registername'],
#                 "total": i['total'],
#                 "grossprem": i['grossprem'],
#                 "brokerageprem": i['brokerageprem'],
#                 "brokeragepercent": (i['brokerageprem']/i['grossprem']) *100,
#                 # "s.no": i['srno'],
#                 # "insurername": i['insurername'],
#                 # "totalcount": i['totalcount'],
#                 # "suminsured": i['sumi'],
#                 # "premium": i['grossprem'],
#                 # "gstpremium": i['grossprem'],
#                 # "netpremium": i['net'],
#                 # "thirdpremium": i['thirdprem'],
#                 # "gstamount": i['gst'],
#                 # "brokerageincome": i['brokerageprem'],
#             }
#             arr.append(val)
#         print (arr,"array")
#         nrows= int(len(arr))
#
#         # One sheet by partner
#         sheet = workbook.add_worksheet(report_name[:31])
#
#         merge_format = workbook.add_format(
#             {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_color': 'black',
#              'fg_color': 'white'})
#         merge_format1 = workbook.add_format(
#             {'bold': 1, 'align': 'left', 'valign': 'vleft','border': 1, 'font_color': 'black'})
#         bold = workbook.add_format({'border': 1, 'bold': True})
#         bold1 = workbook.add_format({'bold': True, 'border':1, 'align': 'left'})
#         border = workbook.add_format({'border': 1})
#         border1 = workbook.add_format({'border': 1, 'align': 'left'})
#         align_left = workbook.add_format({'align': 'left'})
#
#         # sheet.write(5, 4, ('Start Date : ' + str(lines.date_from) + '  to End Date : ' + str(lines.date_to)), bold1)
#         sheet.write(1, 0, ('Financial Year'), bold1)
#         sheet.write(1, 3, ('Quarter'), bold1)
#         sheet.write(2, 0, ('Line of Business'), bold)
#         sheet.write(2, 1, ('No of policies'), bold)
#         sheet.write(2, 2, ('Premium Amount'), bold)
#         sheet.write(2, 3, ('Brokerage Income'), bold)
#         sheet.write(2, 4, ('Brokerage %'), bold)
#         sheet.write(nrows + 3, 0, ('Total'), border)
#         # sheet.write(6, 5, ('Gst (Premium) Amount'), bold)
#         # sheet.write(6, 6, ('Net Premium'), bold)
#         # sheet.write(6, 7, ('Brokerage Premium'), bold)
#         # sheet.write(6, 8, ('Third Party Premium'), bold)
#         # sheet.write(6, 9, ('Brokerage Amount'), bold)
#         # sheet.write(6, 10, ('Gst (Brokerage) Amount'), bold)
#
#
#         # increasing width of column
#         sheet.set_column('A:A', 20)
#         sheet.set_column('B:B', 20)
#         sheet.set_column('C:C', 20)
#         sheet.set_column('D:D', 20)
#         sheet.set_column('E:E', 20)
#         # sheet.set_column('F:F', 20)
#         # sheet.set_column('G:G', 20)
#         # sheet.set_column('H:H', 20)
#         # sheet.set_column('I:I', 20)
#         # sheet.set_column('J:J', 20)
#         # sheet.set_column('K:K', 20)
#         # sheet.set_column('L:L', 20)
#         sheet.merge_range('A1:E1', report_head, merge_format)
#         # sheet.merge_range('A2:A2', report_head1, merge_format1)
#         # sheet.merge_range('D2:D2', report_head2, merge_format1)
#
#         row = 3
#         s_no = 1
#         for res in arr:
#             sheet.write(row, 0, res['registername'], border1)
#             sheet.write(row, 1, res['total'], border)
#             sheet.write(row, 2, res['grossprem'], border)
#             sheet.write(row, 3, res['brokerageprem'], border)
#             sheet.write(row, 4, res['brokeragepercent'], border)
#             sheet.write(nrows + 3, 1, totalpol, border)
#             sheet.write(nrows + 3, 2, totalprem, border)
#             sheet.write(nrows + 3, 3, totalbrok, border)
#             sheet.write(nrows + 3, 4, totalperc, border)
#             # sheet.write(row, 0, res['s.no'], border1)
#             # sheet.write(row, 1, res['insurername'], border)
#             # sheet.write(row, 2, res['totalcount'], border)
#             # sheet.write(row, 3, res['suminsured'], border)
#             # sheet.write(row, 4, res['premium'], border)
#             # sheet.write(row, 5, res['gstpremium'], border)
#             # sheet.write(row, 6, res['netpremium'], border)
#             # sheet.write(row, 7, res['brokerageincome'], border)
#             # sheet.write(row, 8, res['thirdpremium'], border)
#             # sheet.write(row, 9, res['gstamount'], border)
#             # sheet.write(row 10, res['brokerageamount'], border)
#
#             row = row + 1
#             s_no = s_no + 1
#             print ("Array printed for s.no :", s_no - 1)
#
#     print ("Report Printed")
#
#
# GeneralXlsx('report.clickbima.general_report_excel.xlsx', 'create.report')

# non_life insurerwise report:
# class NonLifeInsurerXlsx(ReportXlsx):
#     def generate_xlsx_report(self, workbook, data, lines):
#
#         import odoo
#         db_name = odoo.tools.config.get('db_name')
#         registry = Registry(db_name)
#         # date_from = lines.date_from + ' 00:00:00'
#         # date_to = lines.date_to + ' 23:59:59'
#         # print(lines.date_to,lines.date_from,"DATETETETETETETE")
#         with registry.cursor() as cr:
#             arrquery = "select distinct t2.name as register ,t1.registername1 "\
#                        " from policytransaction as t1 left join subdata_subdata as t2 on t2.id = t1.registername1"\
#
#             cr.execute(arrquery)
#             usr_detail =cr.dictfetchall()
#             temp=[]
#             for i in usr_detail:
#                 print(i['registername1'],"TESTqaaa")
#                 query = "select b2.name as insurername,t2.name as registername,"\
#                         " count(t1.registername1) as total,sum(t1.grossprem) as grossprem"\
#                         " from policytransaction as t1 left join res_partner as b2 on b2.id = t1.insurername123 " \
#                         " left join subdata_subdata as t2 on t2.id = t1.registername1"\
#                         " where t1.registername1 ='"+str(i['registername1'])+"'  and t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by b2.name,t2.name"
#                 cr.execute(query)
#                 usr_detail1 = cr.dictfetchall()
#                 for j in usr_detail1:
#                     temp.append({"insurername":j['insurername'],"registername":j['registername'],"total":j['total'],"grossprem":j['grossprem']})
#             print(temp,"USER DETALKS")
#
#
#                 # if lines.fiscal_year and lines.monthly == "none" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
#             #     query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             # if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "none" and not lines.monthly == "quatar":
#             #     year = lines.fiscal_year.name
#             #     print year, "year"
#             #
#             #     if lines.months == '01-01':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-02':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-03':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-04':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-05':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-06':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-07':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-08':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-09':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-10':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-11':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-12':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             # if lines.quarter and not lines.monthly == 'none' and not lines.monthly == 'monthly':
#             #     query += " where t1.create_date  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(lines.date_to + ' 23:59:59') + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             # if lines.fiscal_year:
#             #     cr.execute(query)
#
#
#             # if lines.fiscal_year:
#             #
#             #     cr.execute("select t1.controlno as ennom,t1.startfrom as startdate,"
#             #                " t1.expiry as enddate,t1.proposaldate as proposaldate,"
#             #                " t2.name as subcategory,t4.name as insurerbranch, t1.regsitersrno as srno,"
#             #                " t1.name as docketno, t1.policyno as policyno, t1.suminsured as sumi,sum(t1.servicetaxamt) as gst,"
#             #                " t11.name as insurer, t10.name as insurername, sum(t1.grossprem) as grossprem,sum(t1.brokerageprem) as brokerageprem "
#             #                " from policytransaction as t1 left join subcategory_subcategory as t2 on t2.id = t1.name1 "
#             #                " left join insurer as t11 on t11.id=t1.insurername123"
#             #                " left join res_partner as t10 on t10.id =t11.name"
#             #                " left join insurerbranch as t4 on t4.id=t1.insurerbranch"
#             #                " where t1.create_date  BETWEEN '"+str(lines.fiscal_year.date_start)+"' AND '"+str(lines.fiscal_year.date_end)+"'"
#             #                " group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno")
#             #
#         # print (usr_detail, "Registernamessssss")
#         # print ("Insurerwise------>ss", usr_detail1)
#         report_name = "sheet 1"
#         report_head = 'Security Insurance Brokers (India) Private Limited'
#         print ("data---->", data)
#
#         arrque = []
#         for i in usr_detail:
#             val = {
#                 "register" : i['register']
#             }
#             arrque.append(val)
#         print (arrque)
#
#
#         totalpol = 0
#         totalprem = 0
#         arr = []
#         for i in temp:
#             totalpol+= i['total']
#             totalprem+= i['grossprem']
#             val = {
#                 "insurername": i['insurername'],
#                 "total": i['total'],
#                 "grossprem": i['grossprem']
#             }
#             arr.append(val)
#         print (arr)
#         nrows = int(len(arr))
#         # One sheet by partner
#         sheet = workbook.add_worksheet(report_name[:31])
#
#         merge_format = workbook.add_format(
#             {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_color': 'black',
#              'fg_color': 'white'})
#         merge_format1 = workbook.add_format(
#             {'bold': 1, 'align': 'left', 'valign': 'vleft', 'font_color': 'black'})
#         bold = workbook.add_format({'border': 1, 'bold': True})
#         bold1 = workbook.add_format({'bold': True})
#         border = workbook.add_format({'border': 1})
#         border1 = workbook.add_format({'border': 1, 'align': 'left'})
#         align_left = workbook.add_format({'align': 'left'})
#
#         # sheet.write(5, 4, ('Start Date : ' + str(lines.date_from) + '  to End Date : ' + str(lines.date_to)), bold1)
#
#         sheet.write(1, 0, ('Financial Year'), bold)
#         sheet.write(1, 3, ('Quarter'), bold)
#         sheet.write(3, 0, ('Name of Insurers'), bold)
#         # sheet.write(3, 1, ('No of Policies'), bold)
#         for i in range(0,len(arrque)):
#             print i*2+1,"iiiiiiiiiiii"
#             sheet.write(3, 2*i+1, ('No of Policies'), bold)
#             sheet.write(3, 2*i+2, ('Premium'), bold)
#         sheet.write(nrows + 4, 0, ('Total'), border)
#
#         # sheet.write(6, 3, ('Sub-Category'), bold)
#         # sheet.write(6, 4, ('Policy No'), bold)
#         # sheet.write(6, 5, ('Endorsement No'), bold)
#         # sheet.write(6, 6, ('Insured Name'), bold)
#         # sheet.write(6, 7, ('Insurer Name'), bold)
#         # sheet.write(6, 8, ('Branch Name'), bold)
#         # sheet.write(6, 9, ('Sum Insured'), bold)
#         # sheet.write(6, 10, ('share (%)'), bold)
#         # sheet.write(6, 11, ('Gross Premium'), bold)
#         # sheet.write(6, 12, ('Gst Amount'), bold)
#         # sheet.write(6, 13, ('Brokerage Premium'), bold)
#         # sheet.write(6, 14, ('Brokerage Amount'), bold)
#         # sheet.write(6, 15, ('Proposal Date'), bold)
#         # sheet.write(6, 16, ('Start Date'), bold)
#         # sheet.write(6, 17, ('Expiry Date'), bold)
#
#         # increasing width of column
#         sheet.set_column('A:A', 50)
#         sheet.set_column('B:B', 20)
#         sheet.set_column('C:C', 20)
#         sheet.set_column('D:D', 20)
#         sheet.set_column('E:E', 20)
#         sheet.set_column('F:F', 20)
#         sheet.set_column('G:G', 20)
#         sheet.set_column('H:H', 20)
#         sheet.set_column('I:I', 20)
#         sheet.set_column('J:J', 20)
#         sheet.set_column('K:K', 20)
#         sheet.set_column('L:L', 20)
#         sheet.set_column('M:M', 20)
#         sheet.set_column('N:N', 20)
#         sheet.set_column('O:O', 20)
#         sheet.set_column('P:P', 20)
#         sheet.set_column('Q:Q', 20)
#         sheet.set_column('R:R', 20)
#
#         sheet.merge_range('A1:G1', report_head, merge_format)
#         # sheet.merge_range('A2:G2', report_head1, merge_format1)
#         # sheet.merge_range('A3:G3', report_head2, merge_format1)
#
#         col=1
#         for reg in arrque:
#             sheet.write(2, col, reg['register'], bold)
#             col=col+2
#
#         row = 4
#         s_no = 1
#         for res in arr:
#             # sheet.write(row, 0, s_no, align_left)
#             sheet.write(row, 0, res['insurername'], border1)
#             for i in range(0,len(arrque)):
#                 sheet.write(row, i*2 + 1, res['total'], border) # to be printd on even index
#                 sheet.write(row, i*2 + 2, res['grossprem'], border) # to be printed on odd index
#                 sheet.write(nrows + 4, 2*i + 1, totalpol, border)
#                 sheet.write(nrows + 4, i*2 + 2 , totalprem, border)
#
#             # sheet.write(row, 6, res['insuredname'], border)
#             # sheet.write(row, 7, res['insurer_name'], border)
#             # sheet.write(row, 8, res['insurer_branch'], border)
#             # sheet.write(row, 9, res['suminsured'], border)
#             # sheet.write(row, 10, res['share'], border)
#             # sheet.write(row, 11, res['grossprem'], border)
#             # sheet.write(row, 12, res['gstamount'], border)
#             # sheet.write(row, 13, res['brokeragepremium'], border)
#             # sheet.write(row, 14, res['brokerageper'], border)
#             # sheet.write(row, 15, res['brokerageamount'], border)
#             # sheet.write(row, 16, res['proposal_date'], border)
#             # sheet.write(row, 17, res['start_from'], border)
#             # sheet.write(row, 18, res['expiry'], border)
#
#             row = row + 1
#             s_no = s_no + 1
#             print ("Array printed for s.no :", s_no - 1)
#
#     print ("Report Printed")
#
#
# NonLifeInsurerXlsx('report.clickbima.non_life_insurer.xlsx', 'create.report')


# non_life top10 client report:
# class NonLifeTopClientXlsx(ReportXlsx):
#     def generate_xlsx_report(self, workbook, data, lines):
#
#         import odoo
#         db_name = odoo.tools.config.get('db_name')
#         registry = Registry(db_name)
#         # date_from = lines.date_from + ' 00:00:00'
#         # date_to = lines.date_to + ' 23:59:59'
#         # print(lines.date_to,lines.date_from,"DATETETETETETETE")
#         with registry.cursor() as cr:
#             arrquery = "select distinct t2.name as register ,t1.registername1 " \
#                        " from policytransaction as t1 left join subdata_subdata as t2 on t2.id = t1.registername1" \
#
#             cr.execute(arrquery)
#             usr_detail = cr.dictfetchall()
#             temp = []
#             for i in usr_detail:
#                 print(i['registername1'], "TESTqaaa")
#                 query = "select b2.name as clientname,t2.name as registername," \
#                         " count(t1.registername1) as total,sum(t1.grossprem) as grossprem" \
#                         " from policytransaction as t1 left join res_partner as b2 on b2.id = t1.clientname " \
#                         " left join subdata_subdata as t2 on t2.id = t1.registername1" \
#                         " where t1.registername1 ='" + str(i['registername1']) + "' and t1.grossprem is not null  and t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by b2.name,t2.name order by total desc limit 10"
#                 cr.execute(query)
#                 usr_detail1 = cr.dictfetchall()
#                 for j in usr_detail1:
#                     temp.append(
#                         {"clientname": j['clientname'], "registername": j['registername'], "total": j['total'],"grossprem": j['grossprem']})
#             print(temp, "USER DETALKS")
#
#             # if lines.fiscal_year and lines.monthly == "none" and not lines.monthly == "quatar" and not lines.monthly == "monthly":
#             #     query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             # if lines.fiscal_year and lines.monthly == "monthly" and not lines.monthly == "none" and not lines.monthly == "quatar":
#             #     year = lines.fiscal_year.name
#             #     print year, "year"
#             #
#             #     if lines.months == '01-01':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-02':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-03':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-04':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-05':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-06':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-07':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-08':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-09':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-10':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-11':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             #     if lines.months == '01-12':
#             #         query += " where t1.create_date  BETWEEN '" + str(lines.fiscal_year.date_start) + "' AND '" + str(lines.fiscal_year.date_end) + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             #
#             # if lines.quarter and not lines.monthly == 'none' and not lines.monthly == 'monthly':
#             #     query += " where t1.create_date  BETWEEN '" + str(lines.date_from + ' 00:00:00') + "' AND '" + str(lines.date_to + ' 23:59:59') + "' group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno"
#             # if lines.fiscal_year:
#             #     cr.execute(query)
#
#             # if lines.fiscal_year:
#             #
#             #     cr.execute("select t1.controlno as ennom,t1.startfrom as startdate,"
#             #                " t1.expiry as enddate,t1.proposaldate as proposaldate,"
#             #                " t2.name as subcategory,t4.name as insurerbranch, t1.regsitersrno as srno,"
#             #                " t1.name as docketno, t1.policyno as policyno, t1.suminsured as sumi,sum(t1.servicetaxamt) as gst,"
#             #                " t11.name as insurer, t10.name as insurername, sum(t1.grossprem) as grossprem,sum(t1.brokerageprem) as brokerageprem "
#             #                " from policytransaction as t1 left join subcategory_subcategory as t2 on t2.id = t1.name1 "
#             #                " left join insurer as t11 on t11.id=t1.insurername123"
#             #                " left join res_partner as t10 on t10.id =t11.name"
#             #                " left join insurerbranch as t4 on t4.id=t1.insurerbranch"
#             #                " where t1.create_date  BETWEEN '"+str(lines.fiscal_year.date_start)+"' AND '"+str(lines.fiscal_year.date_end)+"'"
#             #                " group by t1.controlno,t1.startfrom,t1.expiry,t1.proposaldate,t1.policyno,t1.name,t4.name,t2.name,t11.name,t10.name,t1.suminsured,t1.regsitersrno")
#             #
#         # print (usr_detail, "Registernamessssss")
#         # print ("Insurerwise------>ss", usr_detail1)
#         report_name = "sheet 1"
#         report_head = 'Security Insurance Brokers (India) Private Limited'
#         report_head1 = 'Top 10 Client Non Life Insurance'
#         print("data---->", data)
#
#         arrque = []
#         for i in usr_detail:
#             val = {
#                 "register": i['register']
#             }
#             arrque.append(val)
#         print(arrque)
#
#         totalpol = 0
#         totalprem = 0
#         arr = []
#         for i in temp:
#             totalpol += i['total']
#             totalprem += i['grossprem']
#             val = {
#                 "clientname": i['clientname'],
#                 "total": i['total'],
#                 "grossprem": i['grossprem']
#             }
#             arr.append(val)
#         print(arr)
#         nrows = int(len(arr))
#         # One sheet by partner
#         sheet = workbook.add_worksheet(report_name[:31])
#
#         merge_format = workbook.add_format(
#             {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_color': 'black',
#              'fg_color': 'white'})
#         merge_format1 = workbook.add_format(
#             {'bold': 1, 'align': 'left', 'valign': 'vleft', 'font_color': 'black'})
#         bold = workbook.add_format({'border': 1, 'bold': True})
#         bold1 = workbook.add_format({'bold': True})
#         border = workbook.add_format({'border': 1})
#         border1 = workbook.add_format({'border': 1, 'align': 'left'})
#         align_left = workbook.add_format({'align': 'left'})
#
#         # sheet.write(5, 4, ('Start Date : ' + str(lines.date_from) + '  to End Date : ' + str(lines.date_to)), bold1)
#
#         sheet.write(1, 0, ('Financial Year'), bold)
#         sheet.write(1, 3, ('Quarter'), bold)
#         sheet.write(2, 0, ('Top 10 Client Non Life Insurance'), bold)
#         sheet.write(4, 0, ('Clientname'), bold)
#         # sheet.write(3, 1, ('No of Policies'), bold)
#         for i in range(0, len(arrque)):
#             sheet.write(4, 2 * i + 1, ('No of Policies'), bold)
#             sheet.write(4, 2 * i + 2, ('Premium'), bold)
#         sheet.write(nrows + 5, 0, ('Total'), border)
#
#         # sheet.write(6, 3, ('Sub-Category'), bold)
#         # sheet.write(6, 4, ('Policy No'), bold)
#         # sheet.write(6, 5, ('Endorsement No'), bold)
#         # sheet.write(6, 6, ('Insured Name'), bold)
#         # sheet.write(6, 7, ('Insurer Name'), bold)
#         # sheet.write(6, 8, ('Branch Name'), bold)
#         # sheet.write(6, 9, ('Sum Insured'), bold)
#         # sheet.write(6, 10, ('share (%)'), bold)
#         # sheet.write(6, 11, ('Gross Premium'), bold)
#         # sheet.write(6, 12, ('Gst Amount'), bold)
#         # sheet.write(6, 13, ('Brokerage Premium'), bold)
#         # sheet.write(6, 14, ('Brokerage Amount'), bold)
#         # sheet.write(6, 15, ('Proposal Date'), bold)
#         # sheet.write(6, 16, ('Start Date'), bold)
#         # sheet.write(6, 17, ('Expiry Date'), bold)
#
#         # increasing width of column
#         sheet.set_column('A:A', 50)
#         sheet.set_column('B:B', 20)
#         sheet.set_column('C:C', 20)
#         sheet.set_column('D:D', 20)
#         sheet.set_column('E:E', 20)
#         sheet.set_column('F:F', 20)
#         sheet.set_column('G:G', 20)
#         sheet.set_column('H:H', 20)
#         sheet.set_column('I:I', 20)
#         sheet.set_column('J:J', 20)
#         sheet.set_column('K:K', 20)
#         sheet.set_column('L:L', 20)
#         sheet.set_column('M:M', 20)
#         sheet.set_column('N:N', 20)
#         sheet.set_column('O:O', 20)
#         sheet.set_column('P:P', 20)
#         sheet.set_column('Q:Q', 20)
#         sheet.set_column('R:R', 20)
#
#         sheet.merge_range('A1:G1', report_head, merge_format)
#         # sheet.merge_range('A2:G2', report_head1, merge_format1)
#         # sheet.merge_range('A3:G3', report_head2, merge_format1)
#
#         col = 1
#         for reg in arrque:
#             sheet.write(3, col, reg['register'], bold)
#             col = col + 2
#
#         row = 5
#         s_no = 1
#         for res in arr:
#             # sheet.write(row, 0, s_no, align_left)
#             sheet.write(row, 0, res['clientname'], border1)
#             for i in range(0, len(arrque)):
#                 sheet.write(row, i * 2 + 1, res['total'], border)  # to be printd on even index
#                 sheet.write(row, i * 2 + 2, res['grossprem'], border)  # to be printed on odd index
#                 sheet.write(nrows + 5, 2 * i + 1, totalpol, border)
#                 sheet.write(nrows + 5, i * 2 + 2, totalprem, border)
#
#             # sheet.write(row, 6, res['insuredname'], border)
#             # sheet.write(row, 7, res['insurer_name'], border)
#             # sheet.write(row, 8, res['insurer_branch'], border)
#             # sheet.write(row, 9, res['suminsured'], border)
#             # sheet.write(row, 10, res['share'], border)
#             # sheet.write(row, 11, res['grossprem'], border)
#             # sheet.write(row, 12, res['gstamount'], border)
#             # sheet.write(row, 13, res['brokeragepremium'], border)
#             # sheet.write(row, 14, res['brokerageper'], border)
#             # sheet.write(row, 15, res['brokerageamount'], border)
#             # sheet.write(row, 16, res['proposal_date'], border)
#             # sheet.write(row, 17, res['start_from'], border)
#             # sheet.write(row, 18, res['expiry'], border)
#
#             row = row + 1
#             s_no = s_no + 1
#             print("Array printed for s.no :", s_no - 1)
#
#     print("Report Printed")
#
#
# NonLifeTopClientXlsx('report.clickbima.non_life_top10_client.xlsx', 'create.report')
#
#












