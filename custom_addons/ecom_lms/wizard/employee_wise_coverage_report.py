from odoo import fields, models, _
import io
import xlwt
from io import BytesIO
import base64
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from xlsxwriter.workbook import Workbook
from io import StringIO



class EmployeeWiseCoverageReport(models.TransientModel):
    _name = 'employee.wise.coverage.report'
    
    
    user_ids= fields.Many2many('res.users', 'employeewise_report_user_rel',
        'employeewise_report_id', 'user_id', string='User',)
    
    
    region = fields.Selection([('all', 'All'),('north', 'North'),
                                      ('south', 'South'),
                                      ('east', 'East'),
                                      ('west', 'West'),
                                      ('ihq', 'IHQ'),
                                      ('central', 'Central'),],string='Region',default='all')
    
    course_journey = fields.Selection([('course', 'Course'),
                                      ('journey', 'Journey'),],string='Course/Journey',default='course')
    
    
    def button_print(self):

        string = 'Employee Wise Coverage Report'
        wb = xlwt.Workbook(encoding='utf-8')
        worksheet = wb.add_sheet(string)
        filename = 'Employee Wise Coverage Report' + '.xls'
        style_value = xlwt.easyxf(
            'font: bold on, name Arial ,colour_index black;')
        style_header = xlwt.easyxf(
            'font: bold on ,colour_index red;' "borders: top double , bottom double ,left double , right double;")

        worksheet.write_merge(0, 0, 0, 10, "Employee Wise Coverage Report", xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz center;'))

        worksheet.write(1, 0, 'Employee Code', style_value)
        worksheet.write(1, 1, 'Name', style_value)
        worksheet.write(1, 2, 'Function/Department Code', style_value)
        worksheet.write(1, 3, 'Designation', style_value)
        worksheet.write(1, 4, 'State Name/Zone Code', style_value)
        worksheet.write(1, 5, 'Work Location Code', style_value)
        worksheet.write(1, 6, 'Cost Type Code', style_value)
        worksheet.write(1, 7, 'Band Code', style_value)
        worksheet.write(1, 8, 'Region', style_value)
        
        if self.course_journey == 'course':
            worksheet.write(1, 9, 'No. Of Done Courses', style_value)
            worksheet.write(1, 10, 'Course Name', style_value)
        else:
            worksheet.write(1, 9, 'No. Of Done Journies', style_value)
            worksheet.write(1, 10, 'Journey Name', style_value)
        
        a=2
        
        if self.course_journey == 'course':
            if self.env.user.has_group('base.group_system') or self.env.user.has_group('ecom_lms.admin_user_group'):
                if self.region != 'all':
                    print("myfirst")
                    user_ids= self.env['res.users'].sudo().search([('region','=',self.region),('is_employee','=',True)])
                    for user in user_ids:
                        # if user.emp_code:
                        #     code=user.emp_code
                        # elif user.pre_joinee_code:
                        #     code=user.pre_joinee_code
                        code = ''
                        done_course_lst = []
                        done_course_name_lst = []
                        slide_channel_partner_obj = self.env['slide.channel.partner'].sudo().search(
                            [('completion', '=', 100)])
                        for slide in slide_channel_partner_obj:
                            if user.partner_id.id == slide.partner_id.id:
                                if slide.id not in done_course_lst:
                                    done_course_lst.append(slide.id)
                                    # done_course_name_lst.append(slide.name)
    
                        if len(done_course_lst) > 0:
                            for course_name in done_course_lst:
                                course_id = self.env['slide.channel.partner'].browse(course_name)
                                new_partner = self.env['res.users'].sudo().search(
                                    [('name', '=', course_id.partner_id.name)])
                                worksheet.write(a, 1, new_partner.name or '')
                                if new_partner.customer_code:
                                    code = new_partner.customer_code
                                elif new_partner.emp_code:
                                    code = new_partner.emp_code
                                elif new_partner.pre_joinee_code:
                                    code = new_partner.pre_joinee_code
                                worksheet.write(a, 0, code or '')
                                worksheet.write(a, 3, new_partner.designation or '')
                                worksheet.write(a, 4, new_partner.state_id.name or '')
                                worksheet.write(a, 5, new_partner.work_location or '')
                                worksheet.write(a, 7, new_partner.band or '')
                                region_val = ''
                                if new_partner.region == 'north':
                                    region_val = 'North'
                                if new_partner.region == 'south':
                                    region_val = 'South'
                                if new_partner.region == 'east':
                                    region_val = 'East'
                                if new_partner.region == 'west':
                                    region_val = 'West'
                                if new_partner.region == 'ihq':
                                    region_val = 'IHQ'
                                if new_partner.region == 'central':
                                    region_val = 'Central'
                                worksheet.write(a, 8, region_val or '')
                                value = ''
                                if len(done_course_lst) > 0:
                                    value = 1
                                else:
                                    value = 0
                                worksheet.write(a, 9, value or 0)
                                worksheet.write(a, 10, course_id.channel_id.name or '')
                                a += 1
    
                        else:
                            # worksheet.write(a, 10, '---')
                            a += 0
                else:
                    print("mysecond")
                    user_ids= self.env['res.users'].sudo().search([('is_employee','=',True)])
                    for user in user_ids:
                        # if user.emp_code:
                        #     code=user.emp_code
                        # elif user.pre_joinee_code:
                        #     code=user.pre_joinee_code
                        code =''
                        done_course_lst=[]
                        done_course_name_lst=[]
                        slide_channel_partner_obj= self.env['slide.channel.partner'].sudo().search([('completion','=',100)])
                        for slide in slide_channel_partner_obj:
                            if user.partner_id.id == slide.partner_id.id:
                                if slide.id not in done_course_lst:
                                    done_course_lst.append(slide.id)
                                    # done_course_name_lst.append(slide.name)
    
                        if len(done_course_lst) >0:
                            for course_name in done_course_lst:
                                course_id = self.env['slide.channel.partner'].browse(course_name)
                                new_partner = self.env['res.users'].sudo().search([('name', '=', course_id.partner_id.name)])
                                worksheet.write(a, 1, new_partner.name or '')
                                if new_partner.customer_code:
                                    code = new_partner.customer_code
                                elif new_partner.emp_code:
                                    code = new_partner.emp_code
                                elif new_partner.pre_joinee_code:
                                    code = new_partner.pre_joinee_code
                                worksheet.write(a, 0, code or '')
                                worksheet.write(a, 3, new_partner.designation or '')
                                worksheet.write(a, 4, new_partner.state_id.name or '')
                                worksheet.write(a, 5, new_partner.work_location or '')
                                worksheet.write(a, 7, new_partner.band or '')
                                region_val = ''
                                if new_partner.region == 'north':
                                    region_val = 'North'
                                if new_partner.region == 'south':
                                    region_val = 'South'
                                if new_partner.region == 'east':
                                    region_val = 'East'
                                if new_partner.region == 'west':
                                    region_val = 'West'
                                if new_partner.region == 'ihq':
                                    region_val = 'IHQ'
                                if new_partner.region == 'central':
                                    region_val = 'Central'
                                worksheet.write(a, 8, region_val or '')
                                value = ''
                                if len(done_course_lst) >0:
                                    value = 1
                                else:
                                    value = 0
                                worksheet.write(a, 9, value or 0)
                                worksheet.write(a, 10, course_id.channel_id.name or '')
                                a += 1
                                
                        else:
                            # worksheet.write(a, 10, '---')
                            a += 0
    
            elif self.env.user.has_group('ecom_lms.regional_admin_user_group') and not self.env.user.has_group('base.group_system'):
                if not self.region:
                    raise UserError(_('Please Select Your Region'))
                
                if self.env.user.region != self.region or not self.env.user.region:
                        raise UserError(_('You can access only your region details'))
                user_ids= self.env['res.users'].search([('region','=',self.region),('is_employee','=',True)])
                for user in user_ids:
                    # if user.emp_code:
                    #     code=user.emp_code
                    # elif user.pre_joinee_code:
                    #     code=user.pre_joinee_code
                    code = ''
                    done_course_lst = []
                    done_course_name_lst = []
                    slide_channel_partner_obj = self.env['slide.channel.partner'].sudo().search([('completion', '=', 100)])
                    for slide in slide_channel_partner_obj:
                        if user.partner_id.id == slide.partner_id.id:
                            if slide.id not in done_course_lst:
                                done_course_lst.append(slide.id)
                                # done_course_name_lst.append(slide.name)
    
                    if len(done_course_lst) > 0:
                        for course_name in done_course_lst:
                            course_id = self.env['slide.channel.partner'].browse(course_name)
                            new_partner = self.env['res.users'].sudo().search([('name', '=', course_id.partner_id.name)])
                            worksheet.write(a, 1, new_partner.name or '')
                            if new_partner.customer_code:
                                code = new_partner.customer_code
                            elif new_partner.emp_code:
                                code = new_partner.emp_code
                            elif new_partner.pre_joinee_code:
                                code = new_partner.pre_joinee_code
                            worksheet.write(a, 0, code or '')
                            worksheet.write(a, 3, new_partner.designation or '')
                            worksheet.write(a, 4, new_partner.state_id.name or '')
                            worksheet.write(a, 5, new_partner.work_location or '')
                            worksheet.write(a, 7, new_partner.band or '')
                            region_val = ''
                            if new_partner.region == 'north':
                                region_val = 'North'
                            if new_partner.region == 'south':
                                region_val = 'South'
                            if new_partner.region == 'east':
                                region_val = 'East'
                            if new_partner.region == 'west':
                                region_val = 'West'
                            if new_partner.region == 'ihq':
                                region_val = 'IHQ'
                            if new_partner.region == 'central':
                                region_val = 'Central'
                            worksheet.write(a, 8, region_val or '')
                            value = ''
                            if len(done_course_lst) > 0:
                                value = 1
                            else:
                                value = 0
                            worksheet.write(a, 9, value or 0)
                            worksheet.write(a, 10, course_id.channel_id.name or '')
                            a += 1
    
                    else:
                        # worksheet.write(a, 10, '---')
                        a += 0
                        
                        
                        
                        
                        
        
        elif self.course_journey == 'journey':    
            if self.env.user.has_group('base.group_system') or self.env.user.has_group('ecom_lms.admin_user_group'):
                if self.region != 'all':
                    print("myfirst")
                    user_ids= self.env['res.users'].sudo().search([('region','=',self.region),('is_employee','=',True)])
                    for user in user_ids:
                        code = ''
                        done_journey_lst = []
                        done_journey_name_lst = []
                        slide_journey_partner_obj = self.env['course.journey.partner'].sudo().search([])
                        for slide_journey in slide_journey_partner_obj:
                            if slide_journey.journey_completion == 100:
                                if user.partner_id.id == slide_journey.partner_id.id:
                                    if slide_journey.id not in done_journey_lst:
                                        done_journey_lst.append(slide_journey.id)
                                    # done_course_name_lst.append(slide.name)
                            
                        if len(done_journey_lst) > 0:
                            for journey_name in done_journey_lst:
                                journey_val_id = self.env['course.journey.partner'].browse(journey_name)
                                new_partner = self.env['res.users'].sudo().search(
                                    [('name', '=', journey_val_id.partner_id.name)])
                                worksheet.write(a, 1, new_partner.name or '')
                                if new_partner.customer_code:
                                    code = new_partner.customer_code
                                elif new_partner.emp_code:
                                    code = new_partner.emp_code
                                elif new_partner.pre_joinee_code:
                                    code = new_partner.pre_joinee_code
                                worksheet.write(a, 0, code or '')
                                worksheet.write(a, 3, new_partner.designation or '')
                                worksheet.write(a, 4, new_partner.state_id.name or '')
                                worksheet.write(a, 5, new_partner.work_location or '')
                                worksheet.write(a, 7, new_partner.band or '')
                                region_val = ''
                                if new_partner.region == 'north':
                                    region_val = 'North'
                                if new_partner.region == 'south':
                                    region_val = 'South'
                                if new_partner.region == 'east':
                                    region_val = 'East'
                                if new_partner.region == 'west':
                                    region_val = 'West'
                                if new_partner.region == 'ihq':
                                    region_val = 'IHQ'
                                if new_partner.region == 'central':
                                    region_val = 'Central'
                                worksheet.write(a, 8, region_val or '')
                                value = ''
                                if len(done_journey_lst) > 0:
                                    value = 1
                                else:
                                    value = 0
                                worksheet.write(a, 9, value or 0)
                                worksheet.write(a, 10, journey_val_id.journey_id.description_short or '')
                                a += 1
    
                        else:
                            # worksheet.write(a, 10, '---')
                            a += 0
                else:
                    user_ids= self.env['res.users'].sudo().search([('is_employee','=',True)])
                    for user in user_ids:
                        # if user.emp_code:
                        #     code=user.emp_code
                        # elif user.pre_joinee_code:
                        #     code=user.pre_joinee_code
                        code =''
                        done_journey_lst=[]
                        done_journey_name_lst=[]
                        slide_journey_partner_obj= self.env['course.journey.partner'].sudo().search([])
                        for slide_journey in slide_journey_partner_obj:
                            if slide_journey.journey_completion == 100:
                                if user.partner_id.id == slide_journey.partner_id.id:
                                    if slide_journey.id not in done_journey_lst:
                                        done_journey_lst.append(slide_journey.id)
                                    # done_course_name_lst.append(slide.name)
                        if len(done_journey_lst) >0:
                            for journey_name in done_journey_lst:
                                journey_val_id = self.env['course.journey.partner'].browse(journey_name)
                                new_partner = self.env['res.users'].sudo().search([('name', '=', journey_val_id.partner_id.name)])
                                worksheet.write(a, 1, new_partner.name or '')
                                if new_partner.customer_code:
                                    code = new_partner.customer_code
                                elif new_partner.emp_code:
                                    code = new_partner.emp_code
                                elif new_partner.pre_joinee_code:
                                    code = new_partner.pre_joinee_code
                                worksheet.write(a, 0, code or '')
                                worksheet.write(a, 3, new_partner.designation or '')
                                worksheet.write(a, 4, new_partner.state_id.name or '')
                                worksheet.write(a, 5, new_partner.work_location or '')
                                worksheet.write(a, 7, new_partner.band or '')
                                region_val = ''
                                if new_partner.region == 'north':
                                    region_val = 'North'
                                if new_partner.region == 'south':
                                    region_val = 'South'
                                if new_partner.region == 'east':
                                    region_val = 'East'
                                if new_partner.region == 'west':
                                    region_val = 'West'
                                if new_partner.region == 'ihq':
                                    region_val = 'IHQ'
                                if new_partner.region == 'central':
                                    region_val = 'Central'
                                worksheet.write(a, 8, region_val or '')
                                value = ''
                                if len(done_journey_lst) >0:
                                    value = 1
                                else:
                                    value = 0
                                worksheet.write(a, 9, value or 0)
                                worksheet.write(a, 10, journey_val_id.journey_id.description_short or '')
                                a += 1
                                
                        else:
                            # worksheet.write(a, 10, '---')
                            a += 0
    
            elif self.env.user.has_group('ecom_lms.regional_admin_user_group') and not self.env.user.has_group('base.group_system'):
                if not self.region:
                    raise UserError(_('Please Select Your Region'))
                
                if self.env.user.region != self.region or not self.env.user.region:
                        raise UserError(_('You can access only your region details'))
                user_ids= self.env['res.users'].search([('region','=',self.region),('is_employee','=',True)])
                for user in user_ids:
                    # if user.emp_code:
                    #     code=user.emp_code
                    # elif user.pre_joinee_code:
                    #     code=user.pre_joinee_code
                    code = ''
                    done_journey_lst = []
                    done_journey_name_lst = []
                    slide_journey_partner_obj = self.env['course.journey.partner'].sudo().search([])
                    for slide_journey in slide_journey_partner_obj:
                        if slide_journey.journey_completion == 100:
                            if user.partner_id.id == slide_journey.partner_id.id:
                                if slide_journey.id not in done_journey_lst:
                                    done_journey_lst.append(slide_journey.id)
                                # done_course_name_lst.append(slide.name)
    
                    if len(done_journey_lst) > 0:
                        for journey_name in done_journey_lst:
                            journey_val_id = self.env['course.journey.partner'].browse(journey_name)
                            new_partner = self.env['res.users'].sudo().search([('name', '=', journey_val_id.partner_id.name)])
                            worksheet.write(a, 1, new_partner.name or '')
                            if new_partner.customer_code:
                                code = new_partner.customer_code
                            elif new_partner.emp_code:
                                code = new_partner.emp_code
                            elif new_partner.pre_joinee_code:
                                code = new_partner.pre_joinee_code
                            worksheet.write(a, 0, code or '')
                            worksheet.write(a, 3, new_partner.designation or '')
                            worksheet.write(a, 4, new_partner.state_id.name or '')
                            worksheet.write(a, 5, new_partner.work_location or '')
                            worksheet.write(a, 7, new_partner.band or '')
                            region_val = ''
                            if new_partner.region == 'north':
                                region_val = 'North'
                            if new_partner.region == 'south':
                                region_val = 'South'
                            if new_partner.region == 'east':
                                region_val = 'East'
                            if new_partner.region == 'west':
                                region_val = 'West'
                            if new_partner.region == 'ihq':
                                region_val = 'IHQ'
                            if new_partner.region == 'central':
                                region_val = 'Central'
                            worksheet.write(a, 8, region_val or '')
                            value = ''
                            if len(done_journey_lst) > 0:
                                value = 1
                            else:
                                value = 0
                            worksheet.write(a, 9, value or 0)
                            worksheet.write(a, 10, journey_val_id.journey_id.description_short or '')
                            a += 1
    
                    else:
                        # worksheet.write(a, 10, '---')
                        a += 0
            
            
            
            
            
            
            
            
            
            
            
        # if self.user_ids:
        #     for user in self.user_ids:
        #         code=''
        #         # if user.customer_code:
        #         #     code=user.customer_code
        #         if user.emp_code:
        #             code=user.emp_code
        #         # elif user.pre_joinee_code:
        #         #     code=user.pre_joinee_code
        #         done_course_lst=[]
        #         done_course_name_lst=[]
        #         slide_channel_partner_obj= self.env['slide.channel.partner'].search([('completion','=',100)])
        #         for slide in slide_channel_partner_obj:
        #             if user.partner_id.id == slide.partner_id.id:
        #                 if slide.channel_id.id not in done_course_lst:
        #                     done_course_lst.append(slide.channel_id.id)
        #                     done_course_name_lst.append(slide.channel_id.name)
        #
        #         worksheet.write(a, 0, user.name or '')
        #         worksheet.write(a, 1, code or '')
        #         worksheet.write(a, 2, user.region or '')
        #         worksheet.write(a, 3, len(done_course_lst) or 0)
        #         if len(done_course_name_lst) >0:
        #             for course_name in done_course_name_lst:
        #                 worksheet.write(a, 4, course_name or '')
        #                 a += 1
        #
        #         else:
        #             worksheet.write(a, 4, '---')
        #             a += 1
        #
        # else:
        #     all_user_ids = self.env['res.users'].search([('is_employee','=',True)])
        #     for user_id in all_user_ids:
        #         code=''
        #         # if user_id.customer_code:
        #         #     code=user_id.customer_code
        #         if user_id.emp_code:
        #             code=user_id.emp_code
        #         # elif user_id.pre_joinee_code:
        #         #     code=user_id.pre_joinee_code
        #         done_course_lst=[]
        #         done_course_name_lst=[]
        #         slide_channel_partner_obj= self.env['slide.channel.partner'].search([('completion','=',100)])
        #         for slide in slide_channel_partner_obj:
        #             if user_id.partner_id.id == slide.partner_id.id:
        #                 if slide.channel_id.id not in done_course_lst:
        #                     done_course_lst.append(slide.channel_id.id)
        #                     done_course_name_lst.append(slide.channel_id.name)
        #
        #
        #
        #         worksheet.write(a, 0, user_id.name or '')
        #         worksheet.write(a, 1, code or '')
        #         worksheet.write(a, 2, user_id.region or '')
        #         worksheet.write(a, 3, len(done_course_lst) or 0)
        #         if len(done_course_name_lst) >0:
        #             for course_name in done_course_name_lst:
        #                 worksheet.write(a, 4, course_name or '')
        #                 a += 1
        #
        #         else:
        #             worksheet.write(a, 4, '---')
        #             a += 1
                


        fp = io.BytesIO()
        wb.save(fp)
        out = base64.encodestring(fp.getvalue())
        view_report_status_id = self.env['employee.wise.coverage.view.report'].create( {'excel_file':out, 'file_name':filename})
        return {
            'res_id'   :view_report_status_id.id,
            'name'     :'Report',
            'view_mode':'form',
            'res_model':'employee.wise.coverage.view.report',
            'view_id'  : False ,
            'type'     :'ir.actions.act_window',
        }

    
    
    
    
class employee_wise_coverage_view_report(models.TransientModel):
    _name = 'employee.wise.coverage.view.report'
    _rec_name = 'excel_file'

    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64)
    