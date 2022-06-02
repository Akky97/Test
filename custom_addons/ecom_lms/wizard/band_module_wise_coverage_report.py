from odoo import fields, models, _
import io
import xlwt
from io import BytesIO
import base64
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from xlsxwriter.workbook import Workbook
from io import StringIO



class BandModuleWiseCoverageReport(models.TransientModel):
    _name = 'band.module.wise.coverage.report'
    
    region = fields.Selection([('all', 'All'),('north', 'North'),
                                      ('south', 'South'),
                                      ('east', 'East'),
                                      ('west', 'West'),
                                      ('ihq', 'IHQ'),
                                      ('central', 'Central'),],string='Region',default='all')
    
    band= fields.Char('Band')
    
    course_ids = fields.Many2many('slide.channel', 'band_module_report_course_rel',
        'band_module_report_id', 'course_id', string='Courses',)
    
    journey_ids = fields.Many2many('course.journey', 'band_module_report_journey_rel',
        'band_module_report_id', 'journey_id', string='Journey',)
    
    course_journey = fields.Selection([('course', 'Course'),
                                      ('journey', 'Journey'),],string='Course/Journey',default='course')
    
    
    def button_print(self):

        string = 'Band & Module Wise Coverage Report'
        wb = xlwt.Workbook(encoding='utf-8')
        worksheet = wb.add_sheet(string)
        filename = 'Band & Module Wise Coverage Report' + '.xls'
        style_value = xlwt.easyxf(
            'font: bold on, name Arial ,colour_index black;')
        style_header = xlwt.easyxf(
            'font: bold on ,colour_index red;' "borders: top double , bottom double ,left double , right double;")

        worksheet.write_merge(0, 0, 0, 10, "Band & Module Wise Coverage Report", xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz center;'))
        
        worksheet.write(1, 0, 'Region', style_value)

        worksheet.write(1, 1, 'Band', style_value)
        worksheet.write(1, 2, 'Employee Code', style_value)
        worksheet.write(1, 3, 'Name', style_value)
        worksheet.write(1, 4, 'Designation', style_value)
        worksheet.write(1, 5, 'State Name/Zone Code', style_value)
        worksheet.write(1, 6, 'Work Location Code', style_value)
        
        
        
        if self.course_journey == 'course':
            worksheet.write(1, 7, 'Completed Course Name', style_value)
            if not self.course_ids and not self.band:
                raise UserError(_('Please Select Band or Course'))
            
        if self.course_journey == 'journey':
            worksheet.write(1, 7, 'Completed Journey Name', style_value)
            if not self.journey_ids and not self.band:
                raise UserError(_('Please Select Band or Journey'))
        
        a=2
        if self.course_journey == 'course':
            if self.env.user.has_group('base.group_system') or self.env.user.has_group('ecom_lms.admin_user_group'):
                if self.region == 'all':
                    if self.band and not self.course_ids:
                        user_ids= self.env['res.users'].search([('band','=',self.band)])
                        
                        for user in user_ids:
                            code=''
                            if user.customer_code:
                                code = user.customer_code
                            elif user.emp_code:
                                code = user.emp_code
                            elif user.pre_joinee_code:
                                code = user.pre_joinee_code
                            done_course_name_lst=[]
                            slide_channel_partner_obj= self.env['slide.channel.partner'].sudo().search([('completion','=',100),('partner_id','=',user.partner_id.id)])
                            
                            if slide_channel_partner_obj:
                                for slide_channel in slide_channel_partner_obj:
                                    if slide_channel.channel_id.id not in done_course_name_lst:
                                        done_course_name_lst.append(slide_channel.channel_id.id)
                                        
                            if len(done_course_name_lst) > 0:
                                for course_name in done_course_name_lst:
                                    course_id = self.env['slide.channel'].browse(course_name)
                                    if course_id:
                                        worksheet.write(a, 0, user.region or '')
                                        worksheet.write(a, 1, user.band or '')
                                        worksheet.write(a, 2, code or '')
                                        worksheet.write(a, 3, user.name or '')
                                        worksheet.write(a, 4, user.designation or '')
                                        worksheet.write(a, 5, user.state_id.name or '')
                                        worksheet.write(a, 6, user.work_location or '')
                                        worksheet.write(a, 7, course_id.name or '')
                                        a=a+1
                                        
                            else:
                                worksheet.write(a, 0, user.region or '')
                                worksheet.write(a, 1, user.band or '')
                                worksheet.write(a, 2, code or '')
                                worksheet.write(a, 3, user.name or '')
                                worksheet.write(a, 4, user.designation or '')
                                worksheet.write(a, 5, user.state_id.name or '')
                                worksheet.write(a, 6, user.work_location or '')
                                a=a+1
                                
                    if  self.course_ids and not self.band:   
                        for course in self.course_ids:
                            if course.sudo().channel_partner_ids:
                                for channel_partner in course.sudo().channel_partner_ids:
                                    if channel_partner.completion == 100:
                                        user= self.env['res.users'].search([('partner_id','=',channel_partner.partner_id.id)],limit=1)
                                        if user:
                                            code=''
                                            if user.customer_code:
                                                code = user.customer_code
                                            elif user.emp_code:
                                                code = user.emp_code
                                            elif user.pre_joinee_code:
                                                code = user.pre_joinee_code
                                            worksheet.write(a, 0, user.region or '')
                                            worksheet.write(a, 1, user.band or '')
                                            worksheet.write(a, 2, code or '')
                                            worksheet.write(a, 3, user.name or '')
                                            worksheet.write(a, 4, user.designation or '')
                                            worksheet.write(a, 5, user.state_id.name or '')
                                            worksheet.write(a, 6, user.work_location or '')
                                            worksheet.write(a, 7, course.name or '')
                                            a=a+1
                                            
                                            
                    if  self.course_ids and self.band:   
                        for course in self.course_ids:
                            if course.sudo().channel_partner_ids:
                                for channel_partner in course.sudo().channel_partner_ids:
                                    if channel_partner.completion == 100:
                                        user= self.env['res.users'].search([('partner_id','=',channel_partner.partner_id.id)],limit=1)
                                        if user and user.band== self.band:
                                            code=''
                                            if user.customer_code:
                                                code = user.customer_code
                                            elif user.emp_code:
                                                code = user.emp_code
                                            elif user.pre_joinee_code:
                                                code = user.pre_joinee_code
                                            worksheet.write(a, 0, user.region or '')
                                            worksheet.write(a, 1, user.band or '')
                                            worksheet.write(a, 2, code or '')
                                            worksheet.write(a, 3, user.name or '')
                                            worksheet.write(a, 4, user.designation or '')
                                            worksheet.write(a, 5, user.state_id.name or '')
                                            worksheet.write(a, 6, user.work_location or '')
                                            worksheet.write(a, 7, course.name or '')
                                            a=a+1
                                    
                else:
                    if self.band and not self.course_ids:
                        user_ids= self.env['res.users'].search([('band','=',self.band),('region','=',self.region)])
                        
                        for user in user_ids:
                            code=''
                            if user.customer_code:
                                code = user.customer_code
                            elif user.emp_code:
                                code = user.emp_code
                            elif user.pre_joinee_code:
                                code = user.pre_joinee_code
                                
                            done_course_name_lst=[]
                            slide_channel_partner_obj= self.env['slide.channel.partner'].sudo().search([('completion','=',100),('partner_id','=',user.partner_id.id)])
                            
                            if slide_channel_partner_obj:
                                for slide_channel in slide_channel_partner_obj:
                                    if slide_channel.channel_id.id not in done_course_name_lst:
                                        done_course_name_lst.append(slide_channel.channel_id.id)
                                        
                            if len(done_course_name_lst) > 0:
                                for course_name in done_course_name_lst:
                                    course_id = self.env['slide.channel'].browse(course_name)
                                    if course_id:
                                        worksheet.write(a, 0, user.band or '')
                                        worksheet.write(a, 1, code or '')
                                        worksheet.write(a, 2, user.name or '')
                                        worksheet.write(a, 3, user.designation or '')
                                        worksheet.write(a, 4, user.state_id.name or '')
                                        worksheet.write(a, 5, user.work_location or '')
                                        worksheet.write(a, 6, user.region or '')
                                        worksheet.write(a, 7, course_id.name or '')
                                        a=a+1
                                        
                            else:
                                worksheet.write(a, 0, user.region or '')
                                worksheet.write(a, 1, user.band or '')
                                worksheet.write(a, 2, code or '')
                                worksheet.write(a, 3, user.name or '')
                                worksheet.write(a, 4, user.designation or '')
                                worksheet.write(a, 5, user.state_id.name or '')
                                worksheet.write(a, 6, user.work_location or '')
                                
                                a=a+1
                                
                    if  self.course_ids and not self.band:   
                        for course in self.course_ids:
                            if course.sudo().channel_partner_ids:
                                for channel_partner in course.sudo().channel_partner_ids:
                                    if channel_partner.completion == 100:
                                        user= self.env['res.users'].search([('partner_id','=',channel_partner.partner_id.id)],limit=1)
                                        if user and user.region== self.region:
                                            code=''
                                            if user.customer_code:
                                                code = user.customer_code
                                            elif user.emp_code:
                                                code = user.emp_code
                                            elif user.pre_joinee_code:
                                                code = user.pre_joinee_code
                                            worksheet.write(a, 0, user.band or '')
                                            worksheet.write(a, 1, code or '')
                                            worksheet.write(a, 2, user.name or '')
                                            worksheet.write(a, 3, user.designation or '')
                                            worksheet.write(a, 4, user.state_id.name or '')
                                            worksheet.write(a, 5, user.work_location or '')
                                            worksheet.write(a, 6, user.region or '')
                                            worksheet.write(a, 7, course.name or '')
                                            a=a+1
                                            
                                            
                    if  self.course_ids and self.band:   
                        for course in self.course_ids:
                            if course.sudo().channel_partner_ids:
                                for channel_partner in course.sudo().channel_partner_ids:
                                    if channel_partner.completion == 100:
                                        user= self.env['res.users'].search([('partner_id','=',channel_partner.partner_id.id)],limit=1)
                                        if user and user.band== self.band and user.region== self.region:
                                            code=''
                                            if user.customer_code:
                                                code = user.customer_code
                                            elif user.emp_code:
                                                code = user.emp_code
                                            elif user.pre_joinee_code:
                                                code = user.pre_joinee_code
                                            worksheet.write(a, 0, user.region or '')
                                            worksheet.write(a, 1, user.band or '')
                                            worksheet.write(a, 2, code or '')
                                            worksheet.write(a, 3, user.name or '')
                                            worksheet.write(a, 4, user.designation or '')
                                            worksheet.write(a, 5, user.state_id.name or '')
                                            worksheet.write(a, 6, user.work_location or '')
                                            worksheet.write(a, 7, course.name or '')
                                            a=a+1
            
            
            elif self.env.user.has_group('ecom_lms.regional_admin_user_group') and not self.env.user.has_group('base.group_system'):
                if self.env.user.region != self.region or not self.env.user.region:
                    raise UserError(_('You can access only your region details'))
                
                if self.band and not self.course_ids:
                    user_ids= self.env['res.users'].search([('band','=',self.band),('region','=',self.region)])
                    
                    for user in user_ids:
                        code=''
                        if user.customer_code:
                            code = user.customer_code
                        elif user.emp_code:
                            code = user.emp_code
                        elif user.pre_joinee_code:
                            code = user.pre_joinee_code
                        done_course_name_lst=[]
                        slide_channel_partner_obj= self.env['slide.channel.partner'].sudo().search([('completion','=',100),('partner_id','=',user.partner_id.id)])
                        
                        if slide_channel_partner_obj:
                            for slide_channel in slide_channel_partner_obj:
                                if slide_channel.channel_id.id not in done_course_name_lst:
                                    done_course_name_lst.append(slide_channel.channel_id.id)
                                    
                        if len(done_course_name_lst) > 0:
                            for course_name in done_course_name_lst:
                                course_id = self.env['slide.channel'].browse(course_name)
                                
                                if course_id:
                                    
                                    worksheet.write(a, 0, user.region or '')
                                    worksheet.write(a, 1, user.band or '')
                                    worksheet.write(a, 2, code or '')
                                    worksheet.write(a, 3, user.name or '')
                                    worksheet.write(a, 4, user.designation or '')
                                    worksheet.write(a, 5, user.state_id.name or '')
                                    worksheet.write(a, 6, user.work_location or '')
                                    worksheet.write(a, 7, course_id.name or '')
                                    a=a+1
                                    
                        else:
                            worksheet.write(a, 0, user.region or '')
                            worksheet.write(a, 1, user.band or '')
                            worksheet.write(a, 2, code or '')
                            worksheet.write(a, 3, user.name or '')
                            worksheet.write(a, 4, user.designation or '')
                            worksheet.write(a, 5, user.state_id.name or '')
                            worksheet.write(a, 6, user.work_location or '')
                            
                            a=a+1
                            
                if  self.course_ids and not self.band:   
                    for course in self.course_ids:
                        if course.sudo().channel_partner_ids:
                            for channel_partner in course.sudo().channel_partner_ids:
                                if channel_partner.completion == 100:
                                    user= self.env['res.users'].search([('partner_id','=',channel_partner.partner_id.id)],limit=1)
                                    if user and user.region== self.region:
                                        code=''
                                        if user.customer_code:
                                            code = user.customer_code
                                        elif user.emp_code:
                                            code = user.emp_code
                                        elif user.pre_joinee_code:
                                            code = user.pre_joinee_code
                                            
                                        worksheet.write(a, 0, user.region or '')
                                        worksheet.write(a, 1, user.band or '')
                                        worksheet.write(a, 2, code or '')
                                        worksheet.write(a, 3, user.name or '')
                                        worksheet.write(a, 4, user.designation or '')
                                        worksheet.write(a, 5, user.state_id.name or '')
                                        worksheet.write(a, 6, user.work_location or '')
                                        
                                        worksheet.write(a, 7, course.name or '')
                                        a=a+1
                                        
                                        
                if  self.course_ids and self.band:   
                    for course in self.course_ids:
                        if course.sudo().channel_partner_ids:
                            for channel_partner in course.sudo().channel_partner_ids:
                                if channel_partner.completion == 100:
                                    user= self.env['res.users'].search([('partner_id','=',channel_partner.partner_id.id)],limit=1)
                                    if user and user.band== self.band and user.region== self.region:
                                        code=''
                                        if user.customer_code:
                                            code = user.customer_code
                                        elif user.emp_code:
                                            code = user.emp_code
                                        elif user.pre_joinee_code:
                                            code = user.pre_joinee_code
                                            
                                        worksheet.write(a, 0, user.region or '')
                                        worksheet.write(a, 1, user.band or '')
                                        worksheet.write(a, 2, code or '')
                                        worksheet.write(a, 3, user.name or '')
                                        worksheet.write(a, 4, user.designation or '')
                                        worksheet.write(a, 5, user.state_id.name or '')
                                        worksheet.write(a, 6, user.work_location or '')
                                        worksheet.write(a, 7, course.name or '')
                                        a=a+1
            
        
        
        
        
        
        
        
        if self.course_journey == 'journey':
            if self.env.user.has_group('base.group_system') or self.env.user.has_group('ecom_lms.admin_user_group'):
                if self.region == 'all':
                    if self.band and not self.journey_ids:
                        user_ids= self.env['res.users'].search([('band','=',self.band)])
                        for user in user_ids:
                            code=''
                            if user.customer_code:
                                code = user.customer_code
                            elif user.emp_code:
                                code = user.emp_code
                            elif user.pre_joinee_code:
                                code = user.pre_joinee_code
                            done_journey_name_lst=[]
                            slide_journey_partner_obj= self.env['course.journey.partner'].sudo().search([('partner_id','=',user.partner_id.id)])
                            
                            if slide_journey_partner_obj:
                                for slide_journey in slide_journey_partner_obj:
                                    if slide_journey.journey_completion == 100:
                                        if slide_journey.journey_id.id not in done_journey_name_lst:
                                            done_journey_name_lst.append(slide_journey.journey_id.id)
                                        
                            if len(done_journey_name_lst) > 0:
                                for journey_name in done_journey_name_lst:
                                    journey_val_id = self.env['course.journey'].browse(journey_name)
                                    if journey_val_id:
                                        worksheet.write(a, 0, user.region or '')
                                        worksheet.write(a, 1, user.band or '')
                                        worksheet.write(a, 2, code or '')
                                        worksheet.write(a, 3, user.name or '')
                                        worksheet.write(a, 4, user.designation or '')
                                        worksheet.write(a, 5, user.state_id.name or '')
                                        worksheet.write(a, 6, user.work_location or '')
                                        worksheet.write(a, 7, journey_val_id.description_short or '')
                                        a=a+1
                                        
                            else:
                                worksheet.write(a, 0, user.region or '')
                                worksheet.write(a, 1, user.band or '')
                                worksheet.write(a, 2, code or '')
                                worksheet.write(a, 3, user.name or '')
                                worksheet.write(a, 4, user.designation or '')
                                worksheet.write(a, 5, user.state_id.name or '')
                                worksheet.write(a, 6, user.work_location or '')
                                a=a+1
                                
                    if self.journey_ids and not self.band:   
                        for journey in self.journey_ids:
                            if journey.sudo().journey_channel_partner_ids:
                                for journey_partner in journey.sudo().journey_channel_partner_ids:
                                    if journey_partner.journey_completion == 100:
                                        user= self.env['res.users'].search([('partner_id','=',journey_partner.partner_id.id)],limit=1)
                                        if user:
                                            code=''
                                            if user.customer_code:
                                                code = user.customer_code
                                            elif user.emp_code:
                                                code = user.emp_code
                                            elif user.pre_joinee_code:
                                                code = user.pre_joinee_code
                                            worksheet.write(a, 0, user.region or '')
                                            worksheet.write(a, 1, user.band or '')
                                            worksheet.write(a, 2, code or '')
                                            worksheet.write(a, 3, user.name or '')
                                            worksheet.write(a, 4, user.designation or '')
                                            worksheet.write(a, 5, user.state_id.name or '')
                                            worksheet.write(a, 6, user.work_location or '')
                                            worksheet.write(a, 7, journey.description_short or '')
                                            a=a+1
                                            
                                            
                    if  self.journey_ids and self.band:   
                        for journey in self.journey_ids:
                            if journey.sudo().journey_channel_partner_ids:
                                for journey_partner in journey.sudo().journey_channel_partner_ids:
                                    if journey_partner.journey_completion == 100:
                                        user= self.env['res.users'].search([('partner_id','=',journey_partner.partner_id.id)],limit=1)
                                        if user and user.band== self.band:
                                            code=''
                                            if user.customer_code:
                                                code = user.customer_code
                                            elif user.emp_code:
                                                code = user.emp_code
                                            elif user.pre_joinee_code:
                                                code = user.pre_joinee_code
                                            worksheet.write(a, 0, user.region or '')
                                            worksheet.write(a, 1, user.band or '')
                                            worksheet.write(a, 2, code or '')
                                            worksheet.write(a, 3, user.name or '')
                                            worksheet.write(a, 4, user.designation or '')
                                            worksheet.write(a, 5, user.state_id.name or '')
                                            worksheet.write(a, 6, user.work_location or '')
                                            worksheet.write(a, 7, journey.description_short or '')
                                            a=a+1
                                    
                else:
                    if self.band and not self.journey_ids:
                        user_ids= self.env['res.users'].search([('band','=',self.band),('region','=',self.region)])
                        
                        for user in user_ids:
                            code=''
                            if user.customer_code:
                                code = user.customer_code
                            elif user.emp_code:
                                code = user.emp_code
                            elif user.pre_joinee_code:
                                code = user.pre_joinee_code
                                
                            done_journey_name_lst=[]
                            slide_journey_partner_obj= self.env['course.journey.partner'].sudo().search([('partner_id','=',user.partner_id.id)])
                            
                            if slide_journey_partner_obj:
                                for slide_journey in slide_journey_partner_obj:
                                    if slide_journey.journey_completion == 100:
                                        if slide_journey.journey_id.id not in done_journey_name_lst:
                                            done_journey_name_lst.append(slide_journey.journey_id.id)
                                        
                            if len(done_journey_name_lst) > 0:
                                for journey_name in done_journey_name_lst:
                                    journey_val_id = self.env['course.journey'].browse(journey_name)
                                    if journey_val_id:
                                        worksheet.write(a, 0, user.band or '')
                                        worksheet.write(a, 1, code or '')
                                        worksheet.write(a, 2, user.name or '')
                                        worksheet.write(a, 3, user.designation or '')
                                        worksheet.write(a, 4, user.state_id.name or '')
                                        worksheet.write(a, 5, user.work_location or '')
                                        worksheet.write(a, 6, user.region or '')
                                        worksheet.write(a, 7, journey_val_id.description_short or '')
                                        a=a+1
                                        
                            else:
                                worksheet.write(a, 0, user.region or '')
                                worksheet.write(a, 1, user.band or '')
                                worksheet.write(a, 2, code or '')
                                worksheet.write(a, 3, user.name or '')
                                worksheet.write(a, 4, user.designation or '')
                                worksheet.write(a, 5, user.state_id.name or '')
                                worksheet.write(a, 6, user.work_location or '')
                                
                                a=a+1
                                
                    if  self.journey_ids and not self.band:   
                        for journey in self.journey_ids:
                            if journey.sudo().journey_channel_partner_ids:
                                for journey_partner in journey.sudo().journey_channel_partner_ids:
                                    if journey_partner.journey_completion == 100:
                                        user= self.env['res.users'].search([('partner_id','=',journey_partner.partner_id.id)],limit=1)
                                        if user and user.region== self.region:
                                            code=''
                                            if user.customer_code:
                                                code = user.customer_code
                                            elif user.emp_code:
                                                code = user.emp_code
                                            elif user.pre_joinee_code:
                                                code = user.pre_joinee_code
                                            worksheet.write(a, 0, user.band or '')
                                            worksheet.write(a, 1, code or '')
                                            worksheet.write(a, 2, user.name or '')
                                            worksheet.write(a, 3, user.designation or '')
                                            worksheet.write(a, 4, user.state_id.name or '')
                                            worksheet.write(a, 5, user.work_location or '')
                                            worksheet.write(a, 6, user.region or '')
                                            worksheet.write(a, 7, journey.description_short or '')
                                            a=a+1
                                            
                                            
                    if  self.journey_ids and self.band:   
                        for journey in self.journey_ids:
                            if journey.sudo().journey_channel_partner_ids:
                                for journey_partner in journey.sudo().journey_channel_partner_ids:
                                    if journey_partner.journey_completion == 100:
                                        user= self.env['res.users'].search([('partner_id','=',journey_partner.partner_id.id)],limit=1)
                                        if user and user.band== self.band and user.region== self.region:
                                            code=''
                                            if user.customer_code:
                                                code = user.customer_code
                                            elif user.emp_code:
                                                code = user.emp_code
                                            elif user.pre_joinee_code:
                                                code = user.pre_joinee_code
                                            worksheet.write(a, 0, user.region or '')
                                            worksheet.write(a, 1, user.band or '')
                                            worksheet.write(a, 2, code or '')
                                            worksheet.write(a, 3, user.name or '')
                                            worksheet.write(a, 4, user.designation or '')
                                            worksheet.write(a, 5, user.state_id.name or '')
                                            worksheet.write(a, 6, user.work_location or '')
                                            worksheet.write(a, 7, journey.description_short or '')
                                            a=a+1
            
            
            elif self.env.user.has_group('ecom_lms.regional_admin_user_group') and not self.env.user.has_group('base.group_system'):
                if self.env.user.region != self.region or not self.env.user.region:
                    raise UserError(_('You can access only your region details'))
                
                if self.band and not self.journey_ids:
                    user_ids= self.env['res.users'].search([('band','=',self.band),('region','=',self.region)])
                    
                    for user in user_ids:
                        code=''
                        if user.customer_code:
                            code = user.customer_code
                        elif user.emp_code:
                            code = user.emp_code
                        elif user.pre_joinee_code:
                            code = user.pre_joinee_code
                        done_journey_name_lst=[]
                        slide_journey_partner_obj= self.env['course.journey.partner'].sudo().search([('partner_id','=',user.partner_id.id)])
                        
                        if slide_journey_partner_obj:
                            for slide_journey in slide_journey_partner_obj:
                                if slide_journey.journey_completion == 100:
                                    if slide_journey.journey_id.id not in done_journey_name_lst:
                                        done_journey_name_lst.append(slide_journey.journey_id.id)
                                    
                        if len(done_journey_name_lst) > 0:
                            for journey_name in done_journey_name_lst:
                                journey_val_id = self.env['course.journey'].browse(journey_name)
                                
                                if journey_val_id:
                                    
                                    worksheet.write(a, 0, user.region or '')
                                    worksheet.write(a, 1, user.band or '')
                                    worksheet.write(a, 2, code or '')
                                    worksheet.write(a, 3, user.name or '')
                                    worksheet.write(a, 4, user.designation or '')
                                    worksheet.write(a, 5, user.state_id.name or '')
                                    worksheet.write(a, 6, user.work_location or '')
                                    worksheet.write(a, 7, journey_val_id.description_short or '')
                                    a=a+1
                                    
                        else:
                            worksheet.write(a, 0, user.region or '')
                            worksheet.write(a, 1, user.band or '')
                            worksheet.write(a, 2, code or '')
                            worksheet.write(a, 3, user.name or '')
                            worksheet.write(a, 4, user.designation or '')
                            worksheet.write(a, 5, user.state_id.name or '')
                            worksheet.write(a, 6, user.work_location or '')
                            
                            a=a+1
                            
                if  self.journey_ids and not self.band:   
                    for journey in self.journey_ids:
                        if journey.sudo().journey_channel_partner_ids:
                            for journey_partner in journey.sudo().journey_channel_partner_ids:
                                if journey_partner.journey_completion == 100:
                                    user= self.env['res.users'].search([('partner_id','=',journey_partner.partner_id.id)],limit=1)
                                    if user and user.region== self.region:
                                        code=''
                                        if user.customer_code:
                                            code = user.customer_code
                                        elif user.emp_code:
                                            code = user.emp_code
                                        elif user.pre_joinee_code:
                                            code = user.pre_joinee_code
                                            
                                        worksheet.write(a, 0, user.region or '')
                                        worksheet.write(a, 1, user.band or '')
                                        worksheet.write(a, 2, code or '')
                                        worksheet.write(a, 3, user.name or '')
                                        worksheet.write(a, 4, user.designation or '')
                                        worksheet.write(a, 5, user.state_id.name or '')
                                        worksheet.write(a, 6, user.work_location or '')
                                        
                                        worksheet.write(a, 7, journey.description_short or '')
                                        a=a+1
                                        
                                        
                if  self.journey_ids and self.band:   
                    for journey in self.journey_ids:
                        if journey.sudo().journey_channel_partner_ids:
                            for journey_partner in journey.sudo().journey_channel_partner_ids:
                                if journey_partner.journey_completion == 100:
                                    user= self.env['res.users'].search([('partner_id','=',journey_partner.partner_id.id)],limit=1)
                                    if user and user.band== self.band and user.region== self.region:
                                        code=''
                                        if user.customer_code:
                                            code = user.customer_code
                                        elif user.emp_code:
                                            code = user.emp_code
                                        elif user.pre_joinee_code:
                                            code = user.pre_joinee_code
                                            
                                        worksheet.write(a, 0, user.region or '')
                                        worksheet.write(a, 1, user.band or '')
                                        worksheet.write(a, 2, code or '')
                                        worksheet.write(a, 3, user.name or '')
                                        worksheet.write(a, 4, user.designation or '')
                                        worksheet.write(a, 5, user.state_id.name or '')
                                        worksheet.write(a, 6, user.work_location or '')
                                        worksheet.write(a, 7, journey.description_short or '')
                                        a=a+1
            
            
            
            
                    
        fp = io.BytesIO()
        wb.save(fp)
        out = base64.encodestring(fp.getvalue())
        view_report_status_id = self.env['band.module.wise.coverage.view.report'].create( {'excel_file':out, 'file_name':filename})
        return {
            'res_id'   :view_report_status_id.id,
            'name'     :'Report',
            'view_mode':'form',
            'res_model':'band.module.wise.coverage.view.report',
            'view_id'  : False ,
            'type'     :'ir.actions.act_window',
        }

    
    
    
    
class band_module_wise_coverage_view_report(models.TransientModel):
    _name = 'band.module.wise.coverage.view.report'
    _rec_name = 'excel_file'

    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64)