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

    @http.route('/api/projectdashboardcount', method=['POST'], type='http', auth='none', csrf=False ,cors='*')
    @check_permissions
    def api_revenue_report_POST(self):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        print ('JDATA', jdata)
        user_id = jdata.get('user_id')
        partner_id =jdata.get('partner_id')
        type=jdata.get('type')
        if partner_id == None:
            id = 0
            partner_id = id
        if partner_id == '':
            id = 0
            partner_id = id

        if user_id ==None:
            id=0
            user_id =id
        if user_id == '':
            id = 0
            user_id = id

        # from_date = jdata.get('from_date')
        # if not to_date:
        #     error_descrip = "No to date was provided in request!"
        #     error = 'no_to_date'
        #     _logger.error(error_descrip)
        #     return error_response(400, error, error_descrip)
        # if not from_date:
        #     error_descrip = "No from date was provided in request!"
        #     error = 'no_from_date'
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
                # cr.execute("select count(t2.project_id) as project_task_count ,count(t3.project_id) as project_issue_count,t1.id as project_id,t4.name as projectname from project_project as t1 left join project_task as t2 on t1.id =t2.project_id left join project_issue as t3 on t1.id = t3.project_id left join account_analytic_account as t4 on t1.id = t4.id where t1.user_id ='"+str(user_id)+ "' group by t2.project_id ,t3.project_id,t1.id,t4.name")
                # cr.execute("select count(t2.project_id) as project_task_count ,t1.id as project_id,t4.name as projectname,t6.id as partner_id  from project_project as t1 \
                #            left join project_task as t2 on t1.id =t2.project_id \
                #            left join account_analytic_account as t4 on t1.id = t4.id \
                #            left join res_users as t5 on t1.user_id = t5.id \
                #            left join res_partner as t6 on  t5.partner_id = t6.id \
                #            left join x_project_project_res_partner_rel as t7 on t1.id = t7.project_project_id \
                #            where case when 'admin' = '"+str(type)+"' then 1=1 \
                #            when 'employee' = '"+str(type)+"' then t7.res_partner_id = '"+str(partner_id)+"' \
                #            when 'customer'='"+str(type)+"'then t1.user_id ='"+str(user_id)+"' end \
                #            group by t2.project_id ,t1.id,t4.name,t6.id")
                # cr.execute("select count(t2),t1.id as project_id,t3.name,t6.name as Status,t5.id as partner_id  from project_project as t1 \
                #             left join project_task as t2  on t2.project_id = t1.analytic_account_id \
                #             left join account_analytic_account as t3 on t1.analytic_account_id =t3.id \
                #             left join res_users as t4 on t4.id = t1.user_id \
                #             left join res_partner as t5 on  t4.partner_id = t5.id \
                #             left join project_task_type as t6 on t1.analytic_account_id = t6.id \
                #                 left join x_project_project_res_partner_rel as t7 on t1.id = t7.project_project_id\
                #         where case when 'admin' = '"+str(type)+"' then 1=1 \
                #         when 'employee' = '"+str(type)+"' then t7.res_partner_id = '"+str(partner_id)+"' \
                #         when 'customer'='"+str(type)+"'then t1.user_id ='"+str(user_id)+"' \
                #         when 'status' = 'status' then t6.name LIKE '%Open%'  or t6.name  LIKE '%Closed%' or  t6.name LIKE '%Completed%' or t6.name LIKE '%In Progress%' end  group by t2.project_id ,t3.name,t5.id,t6.name,t1.id")
                # cr.execute("select count(t2),t1.analytic_account_id as project_id,t2.name,t4.name,t6.id as partner_id From project_project as t1 \
                #             left join account_analytic_account as t2 on  t1.id =t2.id \
                #             left join project_task as t3  on t3.project_id =t1.id \
                #             left join project_task_type as t4 on t3.stage_id =t4.id \
                #             left join res_users as t5 on t1.user_id = t5.id \
                #             left join res_partner as t6 on t5.partner_id =t6.id \
                #             left join x_project_project_res_partner_rel as t7 on t6.id = t7.res_partner_id \
                #             where case when 'admin' = '"+str(type)+"' then 1=1 \
                #             when 'employee' = '"+str(type)+"' then t7.res_partner_id = '"+str(partner_id)+"' \
                #             when 'customer'='"+str(type)+"'then t1.user_id ='"+str(user_id)+"' end\
                #             group by t2.name, t4.name, t6.id, t1.analytic_account_id")
                cr.execute("select count(t2),t1.analytic_account_id as project_id,t2.name,t6.id as partner_id From project_project as t1 left join account_analytic_account as t2 on  t1.id =t2.id  left join project_task as t3  on t3.project_id =t1.id left join project_task_type as t4 on t3.stage_id =t4.id left join res_users as t5 on t1.user_id = t5.id left join res_partner as t6 on t5.partner_id =t6.id left join(select distinct project_project_id,res_partner_id from x_project_project_res_partner_rel where res_partner_id='"+str(partner_id)+"' ) as t7 on t1.analytic_account_id =t7.project_project_id   where case when 'admin' = '"+str(type)+"' then 1=1 when 'customer'='"+str(type)+"'then t1.user_id ='"+str(user_id)+"'    when 'employee' = '"+str(type)+"' then t7.res_partner_id = '"+str(partner_id)+"' end  group by t2.name,t6.id, t1.analytic_account_id   ORDER BY  t2.name ASC")
                temp = []
                rows = cr.fetchall()
                for id in rows:
                    if id[1] == None:
                        error = {
                            "message": "No Project found",
                            "status_code": 0
                        }
                        return error
                    else:
                        cr.execute("select count(t2),t1.analytic_account_id,t2.name,t4.name as Stage From project_project as t1 left join account_analytic_account as t2 on  t1.id =t2.id left join project_task as t3  on t3.project_id =t1.id left join project_task_type as t4 on t3.stage_id =t4.id where t1.analytic_account_id='" + str(id[1])+ "' group by t2.name,t4.name,t1.analytic_account_id")
                        # cr.execute("Select  distinct * From(select count(t2),t1.analytic_account_id,t2.name,t4.name as Stage From project_project as t1 left join account_analytic_account as t2 on  t1.id =t2.id \
                        #             left join project_task as t3  on t3.project_id =t1.id \
                        #             left join project_task_type as t4 on t3.stage_id =t4.id \
                        #             where t1.analytic_account_id='" + str(id[1])+ "' group by t2.name,t4.name,t1.analytic_account_id \
                        #             union all \
                        #              select 1,t1.project_id,t3.name,t2.name from project_task as t1 \
                        #             left join project_task_type as t2 on t1.stage_id =t2.id \
                        #             left join account_analytic_account as t3 on  t3.id =t1.project_id \
                        #             where t1.stage_id Not  in \
                        #             ( select t3.stage_id \
		                #              From project_project as t1 left join account_analytic_account as t2 on  t1.id =t2.id \
 		               #               left join project_task as t3  on t3.project_id =t1.id  where t1.analytic_account_id='" + str(id[1])+ "')  and t3.id='" + str(id[1])+ "' ) As Tab ")
                        groupvalue =cr.fetchall()
                        data = []
                        for row in groupvalue:
                            project_groupby={"count":row[0],"project_id":row[1],"project_name":row[2],"stage_id":row[3]}
                            data.append(project_groupby)
                        obj = {"project_task_count": id[0], "project_id": id[1], "project_name": id[2], "partner_id": id[3],"stage_wise":data}
                        temp.append(obj)
                        print(temp)

            return werkzeug.wrappers.Response(
                status=OUT__report__call_method__SUCCESS_CODE,
                content_type='application/json; charset=utf-8',
                headers=[('Cache-Control', 'no-store'),
                         ('Pragma', 'no-cache')],
                response=json.dumps({
                    'dashboardcountapi': temp,

                    # 'To FROM': rows,
                    'message': 'response ok',

                }),
            )



