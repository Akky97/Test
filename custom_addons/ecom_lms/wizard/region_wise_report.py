from odoo import fields, models, _
import io
import xlwt
from io import BytesIO
import base64
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from xlsxwriter.workbook import Workbook
from io import StringIO
from odoo.exceptions import ValidationError



class RegionWiseReport(models.TransientModel):
    _name = 'region.wise.report'
    
    
    user_ids= fields.Many2many('res.users', 'report_user_rel',
        'report_id', 'usr_id', string='User',)
    
    region = fields.Selection([('all', 'All'),('north', 'North'),
                                      ('south', 'South'),
                                      ('east', 'East'),
                                      ('west', 'West'),
                                      ('ihq', 'IHQ'),
                                      ('central', 'Central'),],string='Region',default='all')
    
    course_journey = fields.Selection([('course', 'Course'),
                                      ('journey', 'Journey'),],string='Course/Journey',default='course')
    
    
    def button_print(self):

        string = 'Region Wise Report'
        wb = xlwt.Workbook(encoding='utf-8')
        worksheet = wb.add_sheet(string)
        filename = 'Region Wise Report' + '.xls'
        style_value = xlwt.easyxf(
            'font: bold on, name Arial ,colour_index black;')
        style_header = xlwt.easyxf(
            'font: bold on ,colour_index red;' "borders: top double , bottom double ,left double , right double;")

        worksheet.write_merge(0, 0, 0, 9, "Region Wise Report", xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz center;'))
        worksheet.write(1, 0, 'User Code', style_value)
        worksheet.write(1, 1, 'Name', style_value)
        worksheet.write(1, 2, 'Function/Department Code', style_value)
        worksheet.write(1, 3, 'Designation', style_value)
        worksheet.write(1, 4, 'State Name/Zone Code', style_value)
        worksheet.write(1, 5, 'Work Location Code', style_value)
        worksheet.write(1, 6, 'Cost Type Code', style_value)
        worksheet.write(1, 7, 'Band Code', style_value)
        worksheet.write(1, 8, 'Region', style_value)
        if self.course_journey == 'course':
            worksheet.write(1, 9, 'Course Name', style_value)
        else:
            worksheet.write(1, 9, 'Journey Name', style_value)

        a=2
        
        if self.course_journey == 'course':
            if self.env.user.has_group('base.group_system') or self.env.user.has_group('ecom_lms.admin_user_group'):
                if self.region != 'all':
                    users_ids= self.env['res.users'].search([('region','=',self.region)])
    
                    for user in users_ids:
                        code=''
                        course_lst=[]
                        slide_channel_partner_obj= self.env['slide.channel.partner'].search([('partner_id','=',user.partner_id.id)])
                        for slide_partner in slide_channel_partner_obj:
                            if slide_partner.id not in course_lst:
                                course_lst.append(slide_partner.id)
    
                        if len(course_lst)>0:
                            for course in course_lst:
                                course_id = self.env['slide.channel.partner'].browse(course)
                                new_partner = self.env['res.users'].sudo().search([('partner_id', '=', course_id.partner_id.id)])
                                worksheet.write(a, 9, course_id.channel_id.name or '')
                                worksheet.write(a, 1, new_partner.name or '')
                                worksheet.write(a, 3, new_partner.designation or '')
                                worksheet.write(a, 4, new_partner.state_id.name or '')
                                worksheet.write(a, 5, new_partner.work_location or '')
                                worksheet.write(a, 7, new_partner.band or '')
                                if new_partner.customer_code:
                                    code = new_partner.customer_code
                                elif new_partner.emp_code:
                                    code = new_partner.emp_code
                                elif new_partner.pre_joinee_code:
                                    code = new_partner.pre_joinee_code
                                worksheet.write(a, 0, code or '')
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
                                a += 1
                        else:
                            a += 0
                            
                else:
                    users_ids= self.env['res.users'].search([])
                    for user in users_ids:
                        code = ''
                        course_lst = []
                        slide_channel_partner_obj = self.env['slide.channel.partner'].search(
                            [('partner_id', '=', user.partner_id.id)])
                        for slide_partner in slide_channel_partner_obj:
                            if slide_partner.id not in course_lst:
                                course_lst.append(slide_partner.id)
    
                        if len(course_lst) > 0:
                            for course in course_lst:
                                course_id = self.env['slide.channel.partner'].browse(course)
                                new_partner = self.env['res.users'].sudo().search(
                                    [('name', '=', course_id.partner_id.name)])
                                worksheet.write(a, 9, course_id.channel_id.name or '')
                                worksheet.write(a, 1, new_partner.name or '')
                                worksheet.write(a, 3, new_partner.designation or '')
                                worksheet.write(a, 4, new_partner.state_id.name or '')
                                worksheet.write(a, 5, new_partner.work_location or '')
                                worksheet.write(a, 7, new_partner.band or '')
                                if new_partner.customer_code:
                                    code = new_partner.customer_code
                                elif new_partner.emp_code:
                                    code = new_partner.emp_code
                                elif new_partner.pre_joinee_code:
                                    code = new_partner.pre_joinee_code
                                worksheet.write(a, 0, code or '')
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
                                a += 1
                        else:
                            a += 0
                    
            
            elif self.env.user.has_group('ecom_lms.regional_admin_user_group') and not self.env.user.has_group('base.group_system'):
                if not self.region:
                    raise UserError(_('Please Select Your Region'))
                if self.env.user.region != self.region or not self.env.user.region:
                    raise UserError(_('You can access only your region details'))
                
                
                users_ids= self.env['res.users'].search([('region','=',self.region)])
    
                for user in users_ids:
                    code = ''
                    course_lst = []
                    slide_channel_partner_obj = self.env['slide.channel.partner'].search(
                        [('partner_id', '=', user.partner_id.id)])
                    for slide_partner in slide_channel_partner_obj:
                        if slide_partner.id not in course_lst:
                            course_lst.append(slide_partner.id)
    
                    if len(course_lst) > 0:
                        for course in course_lst:
                            course_id = self.env['slide.channel.partner'].browse(course)
                            new_partner = self.env['res.users'].sudo().search([('partner_id', '=', course_id.partner_id.id)])
                            worksheet.write(a, 9, course_id.channel_id.name or '')
                            worksheet.write(a, 1, new_partner.name or '')
                            worksheet.write(a, 3, new_partner.designation or '')
                            worksheet.write(a, 4, new_partner.state_id.name or '')
                            worksheet.write(a, 5, new_partner.work_location or '')
                            worksheet.write(a, 7, new_partner.band or '')
                            if new_partner.customer_code:
                                code = new_partner.customer_code
                            elif new_partner.emp_code:
                                code = new_partner.emp_code
                            elif new_partner.pre_joinee_code:
                                code = new_partner.pre_joinee_code
                            worksheet.write(a, 0, code or '')
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
                            a += 1
                    else:
                        a += 0
        
        
        
        
        elif self.course_journey == 'journey':    
            
            if self.env.user.has_group('base.group_system') or self.env.user.has_group('ecom_lms.admin_user_group'):
                if self.region != 'all':
                    users_ids= self.env['res.users'].search([('region','=',self.region)])
    
                    for user in users_ids:
                        code=''
                        journey_lst=[]
                        slide_journey_partner_obj= self.env['course.journey.partner'].search([('partner_id','=',user.partner_id.id)])
                        for slide_journey_partner in slide_journey_partner_obj:
                            if slide_journey_partner.id not in journey_lst:
                                journey_lst.append(slide_journey_partner.id)
    
                        if len(journey_lst)>0:
                            for journey in journey_lst:
                                journey_val_id = self.env['course.journey.partner'].browse(journey)
                                new_partner = self.env['res.users'].sudo().search([('partner_id', '=', journey_val_id.partner_id.id)])
                                worksheet.write(a, 9, journey_val_id.journey_id.description_short or '')
                                worksheet.write(a, 1, new_partner.name or '')
                                worksheet.write(a, 3, new_partner.designation or '')
                                worksheet.write(a, 4, new_partner.state_id.name or '')
                                worksheet.write(a, 5, new_partner.work_location or '')
                                worksheet.write(a, 7, new_partner.band or '')
                                if new_partner.customer_code:
                                    code = new_partner.customer_code
                                elif new_partner.emp_code:
                                    code = new_partner.emp_code
                                elif new_partner.pre_joinee_code:
                                    code = new_partner.pre_joinee_code
                                worksheet.write(a, 0, code or '')
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
                                a += 1
                        else:
                            a += 0
                            
                else:
                    users_ids= self.env['res.users'].search([])
                    for user in users_ids:
                        code = ''
                        journey_lst = []
                        slide_journey_partner_obj = self.env['course.journey.partner'].search(
                            [('partner_id', '=', user.partner_id.id)])
                        for slide_journey_partner in slide_journey_partner_obj:
                            if slide_journey_partner.id not in journey_lst:
                                journey_lst.append(slide_journey_partner.id)
    
                        if len(journey_lst) > 0:
                            for journey in journey_lst:
                                journey_val_id = self.env['course.journey.partner'].browse(journey)
                                new_partner = self.env['res.users'].sudo().search(
                                    [('name', '=', journey_val_id.partner_id.name)])
                                worksheet.write(a, 9, journey_val_id.journey_id.description_short or '')
                                worksheet.write(a, 1, new_partner.name or '')
                                worksheet.write(a, 3, new_partner.designation or '')
                                worksheet.write(a, 4, new_partner.state_id.name or '')
                                worksheet.write(a, 5, new_partner.work_location or '')
                                worksheet.write(a, 7, new_partner.band or '')
                                if new_partner.customer_code:
                                    code = new_partner.customer_code
                                elif new_partner.emp_code:
                                    code = new_partner.emp_code
                                elif new_partner.pre_joinee_code:
                                    code = new_partner.pre_joinee_code
                                worksheet.write(a, 0, code or '')
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
                                a += 1
                        else:
                            a += 0
                    
            
            elif self.env.user.has_group('ecom_lms.regional_admin_user_group') and not self.env.user.has_group('base.group_system'):
                if not self.region:
                    raise UserError(_('Please Select Your Region'))
                if self.env.user.region != self.region or not self.env.user.region:
                    raise UserError(_('You can access only your region details'))
                
                
                users_ids= self.env['res.users'].search([('region','=',self.region)])
    
                for user in users_ids:
                    code = ''
                    journey_lst = []
                    slide_journey_partner_obj = self.env['course.journey.partner'].search(
                        [('partner_id', '=', user.partner_id.id)])
                    for slide_journey_partner in slide_journey_partner_obj:
                        if slide_journey_partner.id not in journey_lst:
                            journey_lst.append(slide_journey_partner.id)
    
                    if len(journey_lst) > 0:
                        for journey in journey_lst:
                            journey_val_id = self.env['course.journey.partner'].browse(journey)
                            new_partner = self.env['res.users'].sudo().search([('partner_id', '=', journey_val_id.partner_id.id)])
                            worksheet.write(a, 9, journey_val_id.journey_id.description_short or '')
                            worksheet.write(a, 1, new_partner.name or '')
                            worksheet.write(a, 3, new_partner.designation or '')
                            worksheet.write(a, 4, new_partner.state_id.name or '')
                            worksheet.write(a, 5, new_partner.work_location or '')
                            worksheet.write(a, 7, new_partner.band or '')
                            if new_partner.customer_code:
                                code = new_partner.customer_code
                            elif new_partner.emp_code:
                                code = new_partner.emp_code
                            elif new_partner.pre_joinee_code:
                                code = new_partner.pre_joinee_code
                            worksheet.write(a, 0, code or '')
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
                            a += 1
                    else:
                        a += 0
            
                 

        # if self.region:
        #     if self.env.user.has_group('base.group_system'):
        #         users_ids= self.env['res.users'].search([('region','=',self.region)])
        #         region_val=''
        #         if self.region=='north':
        #             region_val='North'
        #         if self.region=='south':
        #             region_val='South'
        #         if self.region=='east':
        #             region_val='East'
        #         if self.region=='west':
        #             region_val='West'
        #         if self.region=='central':
        #             region_val='Central'
        #
        #         worksheet.write(a, 0, region_val or '')
        #         for user in users_ids:
        #             code=''
        #             course_lst=[]
        #             slide_channel_partner_obj= self.env['slide.channel.partner'].search([('partner_id','=',user.partner_id.id)])
        #             for slide_partner in slide_channel_partner_obj:
        #                 if slide_partner.channel_id.id not in course_lst:
        #                     course_lst.append(slide_partner.channel_id.id)
        #
        #             if user.customer_code:
        #                 code=user.customer_code
        #             elif user.emp_code:
        #                 code=user.emp_code
        #             elif user.pre_joinee_code:
        #                 code=user.pre_joinee_code
        #             worksheet.write(a, 1, code or '')
        #             worksheet.write(a, 2, user.name or '')
        #             if len(course_lst)>0:
        #                 for course in course_lst:
        #                     course_id = self.env['slide.channel'].browse(course)
        #                     worksheet.write(a, 3, course_id.name or '')
        #                     a += 1
        #
        #             else:
        #                 a += 1
        #
        #     elif self.env.user.has_group('ecom_lms.regional_lead_group') and not self.env.user.has_group('base.group_system'):
        #         if self.env.user.region != self.region or not self.env.user.region:
        #             raise UserError(_('You can access only your region details'))
        #
        #
        #         users_ids= self.env['res.users'].search([('region','=',self.region)])
        #         region_val=''
        #         if self.region=='north':
        #             region_val='North'
        #         if self.region=='south':
        #             region_val='South'
        #         if self.region=='east':
        #             region_val='East'
        #         if self.region=='west':
        #             region_val='West'
        #         if self.region=='central':
        #             region_val='Central'
        #
        #         worksheet.write(a, 0, region_val or '')
        #         for user in users_ids:
        #             code=''
        #             course_lst=[]
        #             slide_channel_partner_obj= self.env['slide.channel.partner'].search([('partner_id','=',user.partner_id.id)])
        #             for slide_partner in slide_channel_partner_obj:
        #                 if slide_partner.channel_id.id not in course_lst:
        #                     course_lst.append(slide_partner.channel_id.id)
        #             if user.customer_code:
        #                 code=user.customer_code
        #             elif user.emp_code:
        #                 code=user.emp_code
        #             elif user.pre_joinee_code:
        #                 code=user.pre_joinee_code
        #             worksheet.write(a, 1, code or '')
        #             worksheet.write(a, 2, user.name or '')
        #             if len(course_lst)>0:
        #                 for course in course_lst:
        #                     course_id = self.env['slide.channel'].browse(course)
        #                     worksheet.write(a, 3, course_id.name or '')
        #                     a += 1
        #             else:
        #                 a += 1
                
                
                    
                
                
        

        fp = io.BytesIO()
        wb.save(fp)
        out = base64.encodestring(fp.getvalue())
        view_report_status_id = self.env['regionwise.view.report'].create( {'excel_file':out, 'file_name':filename})
        return {
            'res_id'   :view_report_status_id.id,
            'name'     :'Report',
            'view_mode':'form',
            'res_model':'regionwise.view.report',
            'view_id'  : False ,
            'type'     :'ir.actions.act_window',
        }

    
    
    
    
class regionwise_view_report(models.TransientModel):
    _name = 'regionwise.view.report'
    _rec_name = 'excel_file'

    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64)
    