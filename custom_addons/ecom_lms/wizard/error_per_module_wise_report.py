from odoo import fields, models, _
import io
import xlwt
from io import BytesIO
import base64
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from xlsxwriter.workbook import Workbook
from io import StringIO



class ErrorPerModuleWiseReport(models.TransientModel):
    _name = 'error.per.module.wise.report'
    
    
    user_ids= fields.Many2many('res.users', 'error_per_module_report_user_rel',
        'error_per_module_report_id', 'usr_id', string='User')
    
    region = fields.Selection([('all', 'All'),('north', 'North'),
                                      ('south', 'South'),
                                      ('east', 'East'),
                                      ('west', 'West'),
                                      ('ihq', 'IHQ'),
                                      ('central', 'Central'),],string='Region',default='all')
    
    
    def button_print(self):

        string = 'Errors Per module Wise Report'
        wb = xlwt.Workbook(encoding='utf-8')
        worksheet = wb.add_sheet(string)
        filename = 'Errors Per module Wise Report' + '.xls'
        style_value = xlwt.easyxf(
            'font: bold on, name Arial ,colour_index black;')
        style_header = xlwt.easyxf(
            'font: bold on ,colour_index red;' "borders: top double , bottom double ,left double , right double;")

        worksheet.write_merge(0, 0, 0, 12, "Errors Per module Wise Report", xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz center;'))

        worksheet.write(1, 0, 'Employee Code', style_value)
        worksheet.write(1, 1, 'Name', style_value)
        worksheet.write(1, 2, 'Function/Department Code', style_value)
        worksheet.write(1, 3, 'Designation', style_value)
        worksheet.write(1, 4, 'State Name/Zone Code', style_value)
        worksheet.write(1, 5, 'Work Location Code', style_value)
        worksheet.write(1, 6, 'Cost Type Code', style_value)
        worksheet.write(1, 7, 'Band Code', style_value)
        worksheet.write(1, 8, 'Region', style_value)
        worksheet.write(1, 9, 'Course', style_value)
        worksheet.write(1, 10, 'Quiz', style_value)
        worksheet.write(1, 11, 'Wrong Attempt', style_value)
        # worksheet.write(1, 11, 'No. of wrong answers', style_value)
        worksheet.write(1, 12, 'Questions', style_value)
        a=2
        
        if self.env.user.has_group('base.group_system') or self.env.user.has_group('ecom_lms.admin_user_group'):
            if self.region != 'all':
                user_ids= self.env['res.users'].search([('region','=',self.region)])
                region_val=''
                if self.region=='north':
                    region_val='North'
                if self.region=='south':
                    region_val='South'
                if self.region=='east':
                    region_val='East'
                if self.region=='west':
                    region_val='West'
                if self.region=='ihq':
                    region_val='IHQ'
                if self.region=='central':
                    region_val='Central'
                for user in user_ids:
                    code=''
                    if user.customer_code:
                        code=user.customer_code
                    elif user.emp_code:
                        code=user.emp_code
                    elif user.pre_joinee_code:
                        code=user.pre_joinee_code

                    # worksheet.write(a, 1, user.name or '')
                    # worksheet.write(a, 0, code or '')
                    # worksheet.write(a, 3, user.designation or '')
                    # worksheet.write(a, 4, user.state_id.name or '')
                    # worksheet.write(a, 5, user.work_location or '')
                    # worksheet.write(a, 7, user.band or '')
                    # worksheet.write(a, 8, user.region or '')
                    course_lst=[]
                    slide_channel_partner_obj= self.env['slide.channel.partner'].search([('partner_id','=',user.partner_id.id)])
                    for slide in slide_channel_partner_obj:
                        if slide.channel_id.id not in course_lst:
                            course_lst.append(slide.channel_id.id)
                    if len(course_lst) >0:
                        for course in course_lst:
                            course_id = self.env['slide.channel'].browse(course)
                            if course_id:
                                # worksheet.write(a, 9, course_id.name or '')
                                if course_id.slide_ids:
                                    no_quiz=1
                                    for slide in course_id.slide_ids:
                                        if slide.slide_type == 'quiz':
                                            no_quiz=no_quiz+1
                                            wrong_attempt=0
                                            slide_partner_id= self.env['slide.slide.partner'].search([('slide_id','=',slide.id),('partner_id','=',user.partner_id.id)],limit=1)
                                            for slide_ptnr in slide_partner_id:
                                                if slide_ptnr.quiz_attempts_count>0:
                                                    if slide_ptnr.completed:
                                                        wrong_attempt=wrong_attempt+(slide_ptnr.quiz_attempts_count-1)
                                                    else:
                                                        wrong_attempt=wrong_attempt+slide_ptnr.quiz_attempts_count
                                                        
                                                        
                                            if slide_partner_id and slide_partner_id.wrong_qus_line:
                                                for wrong_attempt_qus in slide_partner_id.wrong_qus_line:
                                                    wrong_attempt_qus_lst=[]
                                                    if wrong_attempt_qus.wrong_qus_ids:
                                                        for wrong_qus in wrong_attempt_qus.wrong_qus_ids:
                                                            wrong_attempt_qus_lst.append(wrong_qus.question)
                                                        
                                            # if slide.question_ids:
                                                # for question_val in slide.question_ids:
                                                    worksheet.write(a, 1, user.name or '')
                                                    worksheet.write(a, 0, code or '')
                                                    worksheet.write(a, 3, user.designation or '')
                                                    worksheet.write(a, 4, user.state_id.name or '')
                                                    worksheet.write(a, 5, user.work_location or '')
                                                    worksheet.write(a, 7, user.band or '')
                                                    worksheet.write(a, 8, user.region or '')
                                                    worksheet.write(a, 9, course_id.name or '')
                                                    worksheet.write(a, 10, slide.name or '')
                                                    worksheet.write(a, 11, wrong_attempt_qus.wrong_attempt_count or '')
                                                    worksheet.write(a, 12, wrong_attempt_qus_lst or '')
                                                    # worksheet.write(a, 11, wrong_attempt or '')
                                                    # worksheet.write(a, 12, question_val.question or '')
                                                    a += 1
                                                    
                                            else:
                                                worksheet.write(a, 1, user.name or '')
                                                worksheet.write(a, 0, code or '')
                                                worksheet.write(a, 3, user.designation or '')
                                                worksheet.write(a, 4, user.state_id.name or '')
                                                worksheet.write(a, 5, user.work_location or '')
                                                worksheet.write(a, 7, user.band or '')
                                                worksheet.write(a, 8, user.region or '')
                                                worksheet.write(a, 9, course_id.name or '')
                                                worksheet.write(a, 10, slide.name or '')
                                                worksheet.write(a, 11, wrong_attempt or '')
                                                a += 1
                                            # a += 1
                                    if no_quiz ==1:
                                        worksheet.write(a, 1, user.name or '')
                                        worksheet.write(a, 0, code or '')
                                        worksheet.write(a, 3, user.designation or '')
                                        worksheet.write(a, 4, user.state_id.name or '')
                                        worksheet.write(a, 5, user.work_location or '')
                                        worksheet.write(a, 7, user.band or '')
                                        worksheet.write(a, 8, user.region or '')
                                        worksheet.write(a, 9, course_id.name or '')
                                        a += 1
                                            
                                        
                                else:
                                    worksheet.write(a, 1, user.name or '')
                                    worksheet.write(a, 0, code or '')
                                    worksheet.write(a, 3, user.designation or '')
                                    worksheet.write(a, 4, user.state_id.name or '')
                                    worksheet.write(a, 5, user.work_location or '')
                                    worksheet.write(a, 7, user.band or '')
                                    worksheet.write(a, 8, user.region or '')
                                    worksheet.write(a, 9, course_id.name or '')
                                    a += 1
                    else:
                        worksheet.write(a, 1, user.name or '')
                        worksheet.write(a, 0, code or '')
                        worksheet.write(a, 3, user.designation or '')
                        worksheet.write(a, 4, user.state_id.name or '')
                        worksheet.write(a, 5, user.work_location or '')
                        worksheet.write(a, 7, user.band or '')
                        worksheet.write(a, 8, user.region or '')
                        a += 1
                        
        
            else:
                user_ids= self.env['res.users'].search([])
                
                for user in user_ids:
                    region_val=''
                    if user.region=='north':
                        region_val='North'
                    if user.region=='south':
                        region_val='South'
                    if user.region=='east':
                        region_val='East'
                    if user.region=='west':
                        region_val='West'
                    if user.region=='ihq':
                        region_val='IHQ'
                    if user.region=='central':
                        region_val='Central'
                    
                    
                    code=''
                    if user.customer_code:
                        code=user.customer_code
                    elif user.emp_code:
                        code=user.emp_code
                    elif user.pre_joinee_code:
                        code=user.pre_joinee_code

                    # worksheet.write(a, 1, user.name or '')
                    # worksheet.write(a, 0, code or '')
                    # worksheet.write(a, 3, user.designation or '')
                    # worksheet.write(a, 4, user.state_id.name or '')
                    # worksheet.write(a, 5, user.work_location or '')
                    # worksheet.write(a, 7, user.band or '')
                    # worksheet.write(a, 8, user.region or '')
                    course_lst=[]
                    slide_channel_partner_obj= self.env['slide.channel.partner'].search([('partner_id','=',user.partner_id.id)])
                    
                    for slide in slide_channel_partner_obj:
                        if slide.channel_id.id not in course_lst:
                            course_lst.append(slide.channel_id.id)
                    
                    if len(course_lst) >0:
                        for course in course_lst:
                            course_id = self.env['slide.channel'].browse(course)
                            if course_id:
                                
                                # worksheet.write(a, 9, course_id.name or '')
                                if course_id.slide_ids:
                                    no_quiz=1
                                    for slide in course_id.slide_ids:
                                        if slide.slide_type == 'quiz':
                                            no_quiz=no_quiz+1
                                            wrong_attempt=0
                                            slide_partner_id= self.env['slide.slide.partner'].search([('slide_id','=',slide.id),('partner_id','=',user.partner_id.id)],limit=1)
                                            for slide_ptnr in slide_partner_id:
                                                if slide_ptnr.quiz_attempts_count>0:
                                                    if slide_ptnr.completed:
                                                        wrong_attempt=wrong_attempt+(slide_ptnr.quiz_attempts_count-1)
                                                    else:
                                                        wrong_attempt=wrong_attempt+slide_ptnr.quiz_attempts_count
                                            
                                            # worksheet.write(a, 10, slide.name or '')
                                            # worksheet.write(a, 11, wrong_attempt or '')
                                            if slide_partner_id and slide_partner_id.wrong_qus_line:
                                                for wrong_attempt_qus in slide_partner_id.wrong_qus_line:
                                                    wrong_attempt_qus_lst=[]
                                                    if wrong_attempt_qus.wrong_qus_ids:
                                                        for wrong_qus in wrong_attempt_qus.wrong_qus_ids:
                                                            wrong_attempt_qus_lst.append(wrong_qus.question)
                                                            
                                                    worksheet.write(a, 1, user.name or '')
                                                    worksheet.write(a, 0, code or '')
                                                    worksheet.write(a, 3, user.designation or '')
                                                    worksheet.write(a, 4, user.state_id.name or '')
                                                    worksheet.write(a, 5, user.work_location or '')
                                                    worksheet.write(a, 7, user.band or '')
                                                    worksheet.write(a, 8, user.region or '')
                                                    worksheet.write(a, 9, course_id.name or '')
                                                    worksheet.write(a, 10, slide.name or '')
                                                    worksheet.write(a, 11, wrong_attempt_qus.wrong_attempt_count or '')
                                                    worksheet.write(a, 12, wrong_attempt_qus_lst or '')
                                                    a += 1
                                                    
                                            # if slide.question_ids:
                                            #     for question_val in slide.question_ids:
                                            #         worksheet.write(a, 1, user.name or '')
                                            #         worksheet.write(a, 0, code or '')
                                            #         worksheet.write(a, 3, user.designation or '')
                                            #         worksheet.write(a, 4, user.state_id.name or '')
                                            #         worksheet.write(a, 5, user.work_location or '')
                                            #         worksheet.write(a, 7, user.band or '')
                                            #         worksheet.write(a, 8, user.region or '')
                                            #         worksheet.write(a, 9, course_id.name or '')
                                            #         worksheet.write(a, 10, slide.name or '')
                                            #         worksheet.write(a, 11, wrong_attempt or '')
                                            #         worksheet.write(a, 12, question_val.question or '')
                                            #         a += 1
                                                    
                                            else:
                                                worksheet.write(a, 1, user.name or '')
                                                worksheet.write(a, 0, code or '')
                                                worksheet.write(a, 3, user.designation or '')
                                                worksheet.write(a, 4, user.state_id.name or '')
                                                worksheet.write(a, 5, user.work_location or '')
                                                worksheet.write(a, 7, user.band or '')
                                                worksheet.write(a, 8, user.region or '')
                                                worksheet.write(a, 9, course_id.name or '')
                                                worksheet.write(a, 10, slide.name or '')
                                                worksheet.write(a, 11, wrong_attempt or '')
                                                a += 1
                                            # a += 1
                                    if no_quiz ==1:
                                        worksheet.write(a, 1, user.name or '')
                                        worksheet.write(a, 0, code or '')
                                        worksheet.write(a, 3, user.designation or '')
                                        worksheet.write(a, 4, user.state_id.name or '')
                                        worksheet.write(a, 5, user.work_location or '')
                                        worksheet.write(a, 7, user.band or '')
                                        worksheet.write(a, 8, user.region or '')
                                        worksheet.write(a, 9, course_id.name or '')
                                        a += 1
                                            
                                        
                                else:
                                    worksheet.write(a, 1, user.name or '')
                                    worksheet.write(a, 0, code or '')
                                    worksheet.write(a, 3, user.designation or '')
                                    worksheet.write(a, 4, user.state_id.name or '')
                                    worksheet.write(a, 5, user.work_location or '')
                                    worksheet.write(a, 7, user.band or '')
                                    worksheet.write(a, 8, user.region or '')
                                    worksheet.write(a, 9, course_id.name or '')
                                    a += 1
                    else:
                        worksheet.write(a, 1, user.name or '')
                        worksheet.write(a, 0, code or '')
                        worksheet.write(a, 3, user.designation or '')
                        worksheet.write(a, 4, user.state_id.name or '')
                        worksheet.write(a, 5, user.work_location or '')
                        worksheet.write(a, 7, user.band or '')
                        worksheet.write(a, 8, user.region or '')
                        a += 1
                
                
        elif self.env.user.has_group('ecom_lms.regional_admin_user_group') and not self.env.user.has_group('base.group_system'):       
        # elif self.env.user.has_group('ecom_lms.regional_lead_group') and not self.env.user.has_group('base.group_system'):
            if not self.region:
                raise UserError(_('Please Select Your Region'))
            if self.env.user.region != self.region or not self.env.user.region:
                raise UserError(_('You can access only your region details'))     
            
            all_user_ids = self.env['res.users'].search([('region','=',self.region)])
            region_val=''
            if self.region=='north':
                region_val='North'
            if self.region=='south':
                region_val='South'
            if self.region=='east':
                region_val='East'
            if self.region=='west':
                region_val='West'
            if self.region=='ihq':
                region_val='IHQ'
            if self.region=='central':
                region_val='Central'
            for user_id in all_user_ids:
                code=''
                if user_id.customer_code:
                    code=user_id.customer_code
                elif user_id.emp_code:
                    code=user_id.emp_code
                elif user_id.pre_joinee_code:
                    code=user_id.pre_joinee_code

                # worksheet.write(a, 1, user_id.name or '')
                # worksheet.write(a, 0, code or '')
                # worksheet.write(a, 3, user_id.designation or '')
                # worksheet.write(a, 4, user_id.state_id.name or '')
                # worksheet.write(a, 5, user_id.work_location or '')
                # worksheet.write(a, 7, user_id.band or '')
                # worksheet.write(a, 8, user_id.region or '')
                course_lst=[]
                slide_channel_partner_obj= self.env['slide.channel.partner'].search([('partner_id','=',user_id.partner_id.id)])
                for slide in slide_channel_partner_obj:
                    if slide.channel_id.id not in course_lst:
                        course_lst.append(slide.channel_id.id)
                if len(course_lst) >0:
                    for course in course_lst:
                        course_id = self.env['slide.channel'].browse(course)
                        if course_id:
                            # worksheet.write(a, 9, course_id.name or '')
                            if course_id.slide_ids:
                                no_quiz=1
                                for slide in course_id.slide_ids:
                                    if slide.slide_type == 'quiz':
                                        no_quiz=no_quiz+1
                                        wrong_attempt=0
                                        slide_partner_id= self.env['slide.slide.partner'].search([('slide_id','=',slide.id),('partner_id','=',user_id.partner_id.id)],limit=1)
                                        for slide_ptnr in slide_partner_id:
                                            if slide_ptnr.quiz_attempts_count>0:
                                                if slide_ptnr.completed:
                                                    wrong_attempt=wrong_attempt+(slide_ptnr.quiz_attempts_count-1)
                                                else:
                                                    wrong_attempt=wrong_attempt+slide_ptnr.quiz_attempts_count
                                                    
                                                    
                                        if slide_partner_id and slide_partner_id.wrong_qus_line:
                                            for wrong_attempt_qus in slide_partner_id.wrong_qus_line:
                                                wrong_attempt_qus_lst=[]
                                                if wrong_attempt_qus.wrong_qus_ids:
                                                    for wrong_qus in wrong_attempt_qus.wrong_qus_ids:
                                                        wrong_attempt_qus_lst.append(wrong_qus.question)
                                        # worksheet.write(a, 10, slide.name or '')
                                        # worksheet.write(a, 11, wrong_attempt or '')
                                        # if slide.question_ids:
                                        #     for question_val in slide.question_ids:
                                                worksheet.write(a, 1, user_id.name or '')
                                                worksheet.write(a, 0, code or '')
                                                worksheet.write(a, 3, user_id.designation or '')
                                                worksheet.write(a, 4, user_id.state_id.name or '')
                                                worksheet.write(a, 5, user_id.work_location or '')
                                                worksheet.write(a, 7, user_id.band or '')
                                                worksheet.write(a, 8, user_id.region or '')
                                                worksheet.write(a, 9, course_id.name or '')
                                                worksheet.write(a, 10, slide.name or '')
                                                worksheet.write(a, 11, wrong_attempt_qus.wrong_attempt_count or '')
                                                worksheet.write(a, 12, wrong_attempt_qus_lst or '')
                                                # worksheet.write(a, 11, wrong_attempt or '')
                                                # worksheet.write(a, 12, question_val.question or '')
                                                a += 1
                                        else:
                                            worksheet.write(a, 1, user_id.name or '')
                                            worksheet.write(a, 0, code or '')
                                            worksheet.write(a, 3, user_id.designation or '')
                                            worksheet.write(a, 4, user_id.state_id.name or '')
                                            worksheet.write(a, 5, user_id.work_location or '')
                                            worksheet.write(a, 7, user_id.band or '')
                                            worksheet.write(a, 8, user_id.region or '')
                                            worksheet.write(a, 9, course_id.name or '')
                                            worksheet.write(a, 10, slide.name or '')
                                            worksheet.write(a, 11, wrong_attempt or '')
                                            a += 1
                                        # a += 1
                                        # a += 1
                                if no_quiz ==1:
                                    worksheet.write(a, 1, user_id.name or '')
                                    worksheet.write(a, 0, code or '')
                                    worksheet.write(a, 3, user_id.designation or '')
                                    worksheet.write(a, 4, user_id.state_id.name or '')
                                    worksheet.write(a, 5, user_id.work_location or '')
                                    worksheet.write(a, 7, user_id.band or '')
                                    worksheet.write(a, 8, user_id.region or '')
                                    worksheet.write(a, 9, course_id.name or '')
                                    a += 1
                                    
                            else:
                                worksheet.write(a, 1, user_id.name or '')
                                worksheet.write(a, 0, code or '')
                                worksheet.write(a, 3, user_id.designation or '')
                                worksheet.write(a, 4, user_id.state_id.name or '')
                                worksheet.write(a, 5, user_id.work_location or '')
                                worksheet.write(a, 7, user_id.band or '')
                                worksheet.write(a, 8, user_id.region or '')
                                worksheet.write(a, 9, course_id.name or '')
                                a += 1
                else:
                    worksheet.write(a, 1, user_id.name or '')
                    worksheet.write(a, 0, code or '')
                    worksheet.write(a, 3, user_id.designation or '')
                    worksheet.write(a, 4, user_id.state_id.name or '')
                    worksheet.write(a, 5, user_id.work_location or '')
                    worksheet.write(a, 7, user_id.band or '')
                    worksheet.write(a, 8, user_id.region or '')
                    a += 1   
            
                
        
        fp = io.BytesIO()
        wb.save(fp)
        out = base64.encodestring(fp.getvalue())
        view_report_status_id = self.env['error.per.module.wise.view.report'].create( {'excel_file':out, 'file_name':filename})
        return {
            'res_id'   :view_report_status_id.id,
            'name'     :'Report',
            'view_mode':'form',
            'res_model':'error.per.module.wise.view.report',
            'view_id'  : False ,
            'type'     :'ir.actions.act_window',
        }

    
    
    
    
class error_per_module_wise_view_report(models.TransientModel):
    _name = 'error.per.module.wise.view.report'
    _rec_name = 'excel_file'

    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64)
    