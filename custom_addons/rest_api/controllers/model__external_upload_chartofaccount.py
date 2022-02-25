# -*- coding: utf-8 -*-
from .main import *
import xmlrpclib
# from flask import Flask, request, render_template
import calendar;
import time;
import base64, os
import requests
import json
from odoo.modules.registry import Registry
import odoo
import logging
import calendar
import time
from tempfile import TemporaryFile
import numpy as np
import pandas as pd

from werkzeug.utils import secure_filename
ts=calendar.timegm(time.gmtime())


_logger = logging.getLogger(__name__)

# List of REST resources in current file:
#   (url prefix)        (method)        (action)
# /api/report/<method>  PUT         - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/report/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__report__call_method__SUCCESS_CODE = 200  # editable


#   Possible ERROR CODES:
#       501 'report_method_not_implemented'
#       409 'not_called_method_in_odoo'


# HTTP controller of REST resources:

class ControllerREST(http.Controller):

    @http.route('/api/externaluploadchart', method=['POST'], type='http', auth='none', csrf=False ,cors='*')
    def api_top_agent(self,file):
        # print('SELF',self)
        # filename = secure_filename(file.filename)
        # encoded = filename
        # print (encoded)
        # data = encoded
        # excel_fileobj = TemporaryFile('wb+')
        # excel_fileobj.write(data)
        excel_fileobj =file
        df1 = pd.read_excel(excel_fileobj)
        header = ['state_id', 'city', 'street2', 'street', 'zip', 'partner_gst_number', 'Journal Items / Partner','Journal Items / Account ', 'chartofaccount_name', 'type', 'line_ids/debit', 'line_ids/credit', 'ref','Journal', 'Journal Items / Label', 'reconcile']
        totalrow = df1.shape[0]
        print (totalrow, "Total Row")
        correct_header = 0
        matched = False

        for i in range(totalrow):
            print (i, "I Rows")
            ext_header = pd.read_excel(excel_fileobj, header=i).columns
            extracted_column = (np.array(ext_header).tolist())
            header_external = (np.array(header).tolist())
            print("header External", header_external)
            set_cols = set(extracted_column) & set(header_external)
            print (set_cols, "Set Cols")
            if len(set_cols) == len(header_external):
                match = True
                correct_header = i
                break;
            else:
                print ("Unmatched")
        dataframe = pd.read_excel(excel_fileobj, nrows=None, header=correct_header)

        print(dataframe, "DATAFRAME->>>>")
        df = pd.DataFrame(dataframe, columns=['state_id', 'city', 'street2', 'street', 'zip', 'partner_gst_number','Journal Items / Partner', 'Journal Items / Account','chartofaccount_name', 'type', 'line_ids/debit', 'line_ids/credit', 'ref','Journal', 'Journal Items / Label', 'reconcile'])
        df = df.fillna('')
        dfshape = df.shape[0]
        types_acc = [
            {"name": "Receivable", "id": '1024'},
            {"name": "Payable", "id": '1025'},
            {"name": "Bank and Cash", "id": '1026'},
            {"name": "Credit Card", "id": '1074'},
            {"name": "Current Assets", "id": '1028'},
            {"name": "Non-current Assets", "id": '1029'},
            {"name": "Prepayments", "id": '1030'},
            {"name": "Fixed Assets", "id": '1031'},
            {"name": "Current Liabilities", "id": '1032'},
            {"name": "Non-current Liabilities", "id": '1033'},
            {"name": "Equity", "id": '1034'},
            {"name": "Current Year Earnings", "id": '1035'},
            {"name": "Other Income", "id": '1036'},
            {"name": "Income", "id": '1037'},
            {"name": "Depreciation", "id": '1038'},
            {"name": "Expenses", "id": '1039'},
            {"name": "Cost of Revenue", "id": '17'}]
        # types_acc = [
        #     {"name": "Receivable", "id": '1'},
        #     {"name": "Payable", "id": '2'},
        #     {"name": "Bank and Cash", "id": '3'},
        #     {"name": "Credit Card", "id": '4'},
        #     {"name": "Current Assets", "id": '5'},
        #     {"name": "Non-current Assets", "id": '6'},
        #     {"name": "Prepayments", "id": '7'},
        #     {"name": "Fixed Assets", "id": '8'},
        #     {"name": "Current Liabilities", "id": '9'},
        #     {"name": "Non-current Liabilities", "id": '10'},
        #     {"name": "Equity", "id": '11'},
        #     {"name": "Current Year Earnings", "id": '12'},
        #     {"name": "Other Income", "id": '13'},
        #     {"name": "Income", "id": '14'},
        #     {"name": "Depreciation", "id": '15'},
        #     {"name": "Expenses", "id": '16'},
        #     {"name": "Cost of Revenue", "id": '17'}]

        type_journal = [
            {"name": "Customer Invoices", "id": '1'},
            {"name": "Vendor Bills", "id": '2'},
            {"name": "Miscellaneous Operations", "id": '3'},
            {"name": "Exchange Difference", "id": '4'},
            {"name": "Cash", "id": '5'},
            {"name": "Bank", "id": '6'},
            {"name": "Tax Invoice", "id": '7'},
            {"name": "Retail Invoice", "id": '8'},
            {"name": "Stock Journal", "id": '9'}]
        state = [{"name": "Andaman and Nicobar", "id": '576'},
                 {"name": "Andhra Pradesh", "id": '577'},
                 {"name": "Arunachal Pradesh", "id": '578'},
                 {"name": "Assam", "id": '579'},
                 {"name": "Bihar", "id": '580'},
                 {"name": "Chandigarh", "id": '581'},
                 {"name": "Chattisgarh", "id": '582'},
                 {"name": "Dadra and Nagar Haveli", "id": '583'},
                 {"name": "Daman and Diu", "id": '584'},
                 {"name": "Delhi", "id": '585'},
                 {"name": "Goa", "id": '586'},
                 {"name": "Gujarat", "id": '587'},
                 {"name": "Haryana", "id": '588'},
                 {"name": "Himachal Pradesh", "id": '589'},
                 {"name": "Jammu and Kashmir", "id": '590'},
                 {"name": "Jharkhand", "id": '591'},
                 {"name": "Karnataka", "id": '592'},
                 {"name": "Kerala", "id": '593'},
                 {"name": "Lakshadweep", "id": '594'},
                 {"name": "Madhya Pradesh", "id": '595'},
                 {"name": "Maharashtra", "id": '596'},
                 {"name": "Manipur", "id": '597'},
                 {"name": "Meghalaya", "id": '598'},
                 {"name": "Mizoram", "id": '599'},
                 {"name": "Nagaland", "id": '600'},
                 {"name": "Orissa", "id": '601'},
                 {"name": "Puducherry", "id": '602'},
                 {"name": "Punjab", "id": '603'},
                 {"name": "Rajasthan", "id": '604'},
                 {"name": "Sikkim", "id": '605'},
                 {"name": "Tamil Nadu", "id": '606'},
                 {"name": "Telangana", "id": '607'},
                 {"name": "Tripura", "id": '608'},
                 {"name": "Uttar Pradesh", "id": '609'},
                 {"name": "Uttarakhand", "id": '610'},
                 {"name": "West Bengal", "id": '611'}]

        for row in range(dfshape):
            if df['Journal Items / Partner'][row] != '':
                for state1 in state:
                    if df['state_id'][row] == state1['name']:
                        vals = {
                            "name": df['Journal Items / Partner'][row],
                            "street": df['street'][row],
                            "street2": df['street2'][row],
                            "city": df['city'][row],
                            "partner_gst_number": df['partner_gst_number'][row],
                            "zip": df['zip'][row],
                            "state_id": state1['id']
                        }
                        print (vals)
                        # self.env['res.partner'].create(vals)

            if df['Journal Items / Account'][row] != '':
                for acc in types_acc:
                    if df['type'][row] == acc['name']:
                        vals1 = {
                            "code": df['Journal Items / Account'][row],
                            "name": df['chartofaccount_name'][row],
                            "user_type_id": acc['id'],
                            "reconcile": df['reconcile'][row],
                        }
                        print (vals1)
                        # self.env['account.account'].create(vals1)

        return werkzeug.wrappers.Response(

            status=OUT__report__call_method__SUCCESS_CODE,
            content_type='application/json; charset=utf-8',
            headers=[('Cache-Control', 'no-store'),
                     ('Pragma', 'no-cache')],
            response=json.dumps({
                'DATA': "Success",
            }),
        )






