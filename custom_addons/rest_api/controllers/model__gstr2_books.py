# -*- coding: utf-8 -*-
from .main import *
import xmlrpclib
import calendar;
import time;
import base64, os
import json
from odoo.modules.registry import Registry
import odoo
import logging

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

    @http.route('/api/r2books', method=['POST'], type='http', auth='none', csrf=False ,cors='*')
    def api_top_count(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        print ('JDATA', jdata)
        date_invoice = jdata.get('date_invoice')
        partner_gst_number = jdata.get('partner_gst_number')
        # company_id = jdata.get('company_id')
        # lastmonth = jdata.get('lastmonth')
        # lastyear = jdata.get('lastyear')


        if not date_invoice:
            error_descrip = "No date_invoice was provided in request!"
            error = 'no_date_invoice'
            _logger.error(error_descrip)
            return error_response(400, error, error_descrip)
        if not partner_gst_number:
            error_descrip = "No partner_gst_number was provided in request!"
            error = 'no_partner_gst_number'
            _logger.error(error_descrip)
            return error_response(400, error, error_descrip)
        # if not company_id:
        #     error_descrip = "No company_id was provided in request!"
        #     error = 'no_company_id'
        #     _logger.error(error_descrip)
        #     return error_response(400, error, error_descrip)
        # if not year:
        #     error_descrip = "No year was provided in request!"
        #     error = 'year'
        #     _logger.error(error_descrip)
        #     return error_response(400, error, error_descrip)
        # if not lastmonth:
        #     error_descrip = "No lastmonth was provided in request!"
        #     error = 'no_lastmonth'
        #     _logger.error(error_descrip)
        #     return error_response(400, error, error_descrip)
        # if not lastyear:
        #     error_descrip = "No lastyear was provided in request!"
        #     error = 'no_lastyear'
        #     _logger.error(error_descrip)
        #     return error_response(400, error, error_descrip)



        db_name = odoo.tools.config.get('db_name')
        if not db_name:
            _logger.error(
                "ERROR: To proper setup OAuth2 and Redis - it's necessary to set the parameter 'db_name' in Odoo config file!")
            print(
                "ERROR: To proper setup OAuth2 and Token Store - it's necessary to set the parameter 'db_name' in Odoo config file!")
        else:
            # Read system parameters...
            registry = Registry(db_name)
            with registry.cursor() as cr:
                cr.execute("select t1.id,t2.vat from res_company as t1 left join res_partner as t2 on t2.company_id = t1.id where t2.vat = '" + str(partner_gst_number) + "'")
                data=(cr.dictfetchall())
                cr.execute("select  count(*), t1.number,t2.name,t2.partner_gst_number,TO_CHAR(t1.date_invoice, 'YYYY-MM'), t1.place_of_supply,t1.place_of_supply_state, t1.amount_total,t1.amount_untaxed,t1.reference, SUBSTRING(t3.name, 5, 3) as tax, t3.amount as taxamount,t1.date_invoice as date ,t4.name as company, t1.company_id , t5.name as journalname from account_invoice as t1 left join res_partner as t2 on t1.partner_id = t2.id left join account_invoice_tax as t3 on t1.id = t3.invoice_id left join res_company as t4 on t1.company_id = t4.id left join account_journal as t5 on t1.journal_id = t5.id where TO_CHAR(t1.date_invoice, 'YYYY-MM') = '" + str(date_invoice) + "' and t1.company_id = '" + str(data[0]['id']) + "' and t5.name = 'Vendor Bills' group by  t1.number,t2.name,t2.partner_gst_number,t1.date_invoice,t1.place_of_supply, t1.place_of_supply_state, t1.amount_total,t1.amount_untaxed,t1.reference,t3.name ,t3.amount, t4.name,t1.company_id,t5.name")
                temp = []
                rows = cr.fetchall()
                print('Total Row(s):', rows)
                for row in rows:
                    obj = {"count":row[0],"number":row[1],"name":row[2],"partner_gst_number":row[3],"to_char":row[4],"place_of_supply":row[5],"place_of_supply_state":row[6],"amount_total":row[7],"amount_untaxed":row[8],"reference":row[9],"tax":row[10],"taxamount":row[11],"date":row[12],"company":row[13],"company_id":row[14],"journalname":row[15]}
                    temp.append(obj)
                return werkzeug.wrappers.Response(
                    status=OUT__report__call_method__SUCCESS_CODE,
                    content_type='application/json; charset=utf-8',
                    headers=[('Cache-Control', 'no-store'),
                             ('Pragma', 'no-cache')],
                    response=json.dumps({
                        'gstr2_books': temp,

                        # 'To FROM': rows

                    }),
                )


