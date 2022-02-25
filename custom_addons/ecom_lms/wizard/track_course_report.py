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
import math


class TrackCourseReport(models.TransientModel):
    _name = 'track.course.completion'

    user_ids = fields.Many2many('res.users', 'track_course_rel',
                                'track_course_report_id', 'usr_id', string='User', )
    region = fields.Selection([('all','All'),('north', 'North'),
                               ('south', 'South'),
                               ('east', 'East'),
                               ('west', 'West'),
                               ('ihq', 'IHQ'),
                               ('central', 'Central'), ], string='Region',default='all')
    
    course_journey = fields.Selection([('course', 'Course'),
                                      ('journey', 'Journey'),],string='Course/Journey',default='course')


    def float_time_convert(self, float_val):    
        factor = float_val < 0 and -1 or 1   
        val = abs(float_val)    
        return (factor * int(math.floor(val)), int(round((val % 1) * 60)))
    
    

    def button_print(self):
        string = 'Track Course Completion Report'
        wb = xlwt.Workbook(encoding='utf-8')
        worksheet = wb.add_sheet(string)
        filename = 'Track Course Completion Report' + '.xls'
        style_value = xlwt.easyxf(
            'font: bold on, name Arial ,colour_index black;')
        style_header = xlwt.easyxf(
            'font: bold on ,colour_index red;' "borders: top double , bottom double ,left double , right double;")

        worksheet.write_merge(0, 0, 0, 11, "Track Course Completion Report", xlwt.easyxf(
            'font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz center;'))

        worksheet.write(1, 0, 'User Code', style_value)
        worksheet.write(1, 1, 'Name', style_value)
        worksheet.write(1, 2, 'Function/Department Code', style_value)
        worksheet.write(1, 3, 'Designation', style_value)
        worksheet.write(1, 4, 'State Name/Zone Code', style_value)
        worksheet.write(1, 5, 'Work Location Code', style_value)
        worksheet.write(1, 6, 'Cost Type Code', style_value)
        worksheet.write(1, 7, 'Band Code', style_value)
        worksheet.write(1, 8, 'Region', style_value)
        
        if self.course_journey=='course':
            worksheet.write(1, 9, 'Name Of the Course', style_value)
            worksheet.write(1, 10, 'Course Duration', style_value)
            worksheet.write(1, 11, '% Completion of course', style_value)
            worksheet.write(1, 12, 'Total Learning Hours', style_value)
            
        if self.course_journey=='journey':
            worksheet.write(1, 9, 'Name Of the Journey', style_value)
            worksheet.write(1, 10, 'Journey Duration', style_value)
            worksheet.write(1, 11, '% Completion of Journey', style_value)
            
        a = 2


        if self.course_journey=='course':
            if self.env.user.has_group('base.group_system') or self.env.user.has_group('ecom_lms.admin_user_group'):
                if self.region != 'all':
                    users_ids = self.env['res.users'].search([('region', '=', self.region)])
    
                    # worksheet.write(a, 8, region_val or '')
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
                                new_partner = self.env['res.users'].sudo().search([('partner_id','=',course_id.partner_id.id)],limit=1)
                                
                                course_duration=0.0
                                if course_id.channel_id.slide_ids:
                                    for lesson in course_id.channel_id.slide_ids:
                                        if lesson.is_published:
                                            course_duration=course_duration+lesson.completion_time
                                            
                                hour, minute = self.float_time_convert(course_duration) 
                                course_duration_val=str(hour)+':'+str(minute)
                                
                                
                                learned_time=course_duration-course_id.time_left
                                learned_hour, learned_minute = self.float_time_convert(learned_time) 
                                
                                learned_time_val=str(learned_hour)+':'+str(learned_minute)
                                
                                
                                worksheet.write(a, 9, course_id.channel_id.name or '')
                                worksheet.write(a, 10, course_duration_val or '')
                                worksheet.write(a, 11, course_id.completion or '')
                                worksheet.write(a, 12, learned_time_val or '')
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
                    users_ids = self.env['res.users'].search([])
    
                    # worksheet.write(a, 8, region_val or '')
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
                                    [('partner_id', '=', course_id.partner_id.id)],limit=1)
                                
                                course_duration=0.0
                                if course_id.channel_id.slide_ids:
                                    for lesson in course_id.channel_id.slide_ids:
                                        if lesson.is_published:
                                            course_duration=course_duration+lesson.completion_time
                                            
                                hour, minute = self.float_time_convert(course_duration) 
                                course_duration_val=str(hour)+':'+str(minute)
                                
                                
                                learned_time=course_duration-course_id.time_left
                                learned_hour, learned_minute = self.float_time_convert(learned_time) 
                                
                                learned_time_val=str(learned_hour)+':'+str(learned_minute)
                                
                                worksheet.write(a, 9, course_id.channel_id.name or '')
                                worksheet.write(a, 10, course_duration_val or '')
                                worksheet.write(a, 11, course_id.completion or '')
                                worksheet.write(a, 12, learned_time_val or '')
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
    
                users_ids = self.env['res.users'].search([('region', '=', self.region)])
    
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
                            course_id = self.env['slide.channel.partner'].sudo().browse(course)
                            course_duration=0.0
                            if course_id.channel_id.slide_ids:
                                for lesson in course_id.channel_id.slide_ids:
                                    if lesson.is_published:
                                        course_duration=course_duration+lesson.completion_time
                                        
                            hour, minute = self.float_time_convert(course_duration) 
                            course_duration_val=str(hour)+':'+str(minute)
                            
                            learned_time=course_duration-course_id.time_left
                            learned_hour, learned_minute = self.float_time_convert(learned_time) 
                            
                            learned_time_val=str(learned_hour)+':'+str(learned_minute)
                            
                            
                            new_partner = self.env['res.users'].sudo().search([('partner_id', '=', course_id.partner_id.id)],limit=1)
                            worksheet.write(a, 9, course_id.channel_id.name or '')
                            worksheet.write(a, 10, course_duration_val or '')
                            worksheet.write(a, 11, course_id.completion or '')
                            worksheet.write(a, 12, learned_time_val or '')
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
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
        if self.course_journey=='journey':
            if self.env.user.has_group('base.group_system') or self.env.user.has_group('ecom_lms.admin_user_group'):
                if self.region != 'all':
                    
                    # users_ids = self.env['res.users'].search([('region', '=', self.region)])
                    self.env.cr.execute('SELECT id FROM res_users where region = %s',(self.region,))
                    users_ids = self.env.cr.fetchall()
                   
    
                    # worksheet.write(a, 8, region_val or '')
                    for user_value in users_ids:
                        user = self.env['res.users'].browse(user_value)
                        code = ''
                        journey_lst = []
                        slide_journey_partner_obj = self.env['course.journey.partner'].search(
                            [('partner_id', '=', user.partner_id.id)])
                        for journey_partner in slide_journey_partner_obj:
                            if journey_partner.id not in journey_lst:
                                journey_lst.append(journey_partner.id)
    
                        if len(journey_lst) > 0:
                            for journey in journey_lst:
                                journey_val_id = self.env['course.journey.partner'].browse(journey)
                                self.env.cr.execute('SELECT id FROM res_users where partner_id = %s',(journey_val_id.partner_id.id,))
                                new_val_partner = self.env.cr.fetchall()
                                new_partner = self.env['res.users'].browse(new_val_partner)
                                new_partner = self.env['res.users'].browse(new_partner.id)
                                # new_partner = self.env['res.users'].sudo().search([('partner_id','=',journey_val_id.partner_id.id)],limit=1)
                                
                                journey_duration=0.0
                                if journey_val_id.journey_id.courses_ids:
                                    for journey_course in journey_val_id.journey_id.courses_ids:
                                        if journey_course.course_id.slide_ids:
                                            for lesson in journey_course.course_id.slide_ids:
                                                if lesson.is_published:
                                                    journey_duration=journey_duration+lesson.completion_time
                                            
                                hour, minute = self.float_time_convert(journey_duration) 
                                journey_duration_val=str(hour)+':'+str(minute)
                                
                                
                                # learned_time=journey_duration-course_id.time_left
                                # learned_hour, learned_minute = self.float_time_convert(learned_time) 
                                #
                                # learned_time_val=str(learned_hour)+':'+str(learned_minute)
                                
                                
                                worksheet.write(a, 9, journey_val_id.journey_id.description_short or '')
                                worksheet.write(a, 10, journey_duration_val or '')
                                worksheet.write(a, 11, journey_val_id.journey_completion or '')
                                # worksheet.write(a, 12, learned_time_val or '')
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
                    # users_ids = self.env['res.users'].search([])
                    
                    self.env.cr.execute('SELECT id FROM res_users')
                    users_ids = self.env.cr.fetchall()
                    # worksheet.write(a, 8, region_val or '')
                    for user_val in users_ids:
                        user = self.env['res.users'].browse(user_val)
                        code = ''
                        journey_lst = []
                        slide_journey_partner_obj = self.env['course.journey.partner'].search(
                            [('partner_id', '=', user.partner_id.id)])
                        for journey_partner in slide_journey_partner_obj:
                            if journey_partner.id not in journey_lst:
                                journey_lst.append(journey_partner.id)
                        if len(journey_lst) > 0:
                            for journey in journey_lst:
                                journey_val_id = self.env['course.journey.partner'].browse(journey)
                                
                                self.env.cr.execute('SELECT id FROM res_users where partner_id = %s',(journey_val_id.partner_id.id,))
                                new_val_partner = self.env.cr.fetchall()
                                new_partner = self.env['res.users'].browse(new_val_partner)
                                new_partner = self.env['res.users'].browse(new_partner.id)
                                # new_partner = self.env['res.users'].sudo().search(
                                #     [('partner_id', '=', journey_val_id.partner_id.id)],limit=1)
                                
                                journey_duration=0.0
                                if journey_val_id.journey_id.courses_ids:
                                    for journey_course in journey_val_id.journey_id.courses_ids:
                                        if journey_course.course_id.slide_ids:
                                            for lesson in journey_course.course_id.slide_ids:
                                                if lesson.is_published:
                                                    journey_duration=journey_duration+lesson.completion_time
                                            
                                hour, minute = self.float_time_convert(journey_duration) 
                                journey_duration_val=str(hour)+':'+str(minute)
                                
                                
                                # learned_time=course_duration-course_id.time_left
                                # learned_hour, learned_minute = self.float_time_convert(learned_time) 
                                #
                                # learned_time_val=str(learned_hour)+':'+str(learned_minute)
                                
                                worksheet.write(a, 9, journey_val_id.journey_id.description_short or '')
                                worksheet.write(a, 10, journey_duration_val or '')
                                worksheet.write(a, 11, journey_val_id.journey_completion or '')
                                # worksheet.write(a, 12, learned_time_val or '')
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
    
                # users_ids = self.env['res.users'].search([('region', '=', self.region)])
                self.env.cr.execute('SELECT id FROM res_users where region = %s',(self.region,))
                users_ids = self.env.cr.fetchall()
    
                for user_val in users_ids:
                    user = self.env['res.users'].browse(user_val)
                    code = ''
                    journey_lst = []
                    slide_journey_partner_obj = self.env['course.journey.partner'].search(
                        [('partner_id', '=', user.partner_id.id)])
                    for journey_partner in slide_journey_partner_obj:
                        if journey_partner.id not in journey_lst:
                            journey_lst.append(journey_partner.id)
    
                    if len(journey_lst) > 0:
                        for journey in journey_lst:
                            journey_val_id = self.env['course.journey.partner'].sudo().browse(journey)
                            journey_duration=0.0
                            if journey_val_id.journey_id.courses_ids:
                                for journey_course in journey_val_id.journey_id.courses_ids:
                                    if journey_course.course_id.slide_ids:
                                        for lesson in journey_course.course_id.slide_ids:
                                            if lesson.is_published:
                                                journey_duration=journey_duration+lesson.completion_time
                                        
                            hour, minute = self.float_time_convert(journey_duration) 
                            journey_duration_val=str(hour)+':'+str(minute)
                            
                            # learned_time=course_duration-course_id.time_left
                            # learned_hour, learned_minute = self.float_time_convert(learned_time) 
                            #
                            # learned_time_val=str(learned_hour)+':'+str(learned_minute)
                            
                            self.env.cr.execute('SELECT id FROM res_users where partner_id = %s',(journey_val_id.partner_id.id,))
                            new_val_partner = self.env.cr.fetchall()
                            new_partner = self.env['res.users'].browse(new_val_partner)
                            new_partner = self.env['res.users'].browse(new_partner.id)
                            
                            # new_partner = self.env['res.users'].sudo().search([('partner_id', '=', journey_val_id.partner_id.id)],limit=1)
                            worksheet.write(a, 9, journey_val_id.journey_id.description_short or '')
                            worksheet.write(a, 10, journey_duration_val or '')
                            worksheet.write(a, 11, journey_val_id.journey_completion or '')
                            # worksheet.write(a, 12, learned_time_val or '')
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
                        
                        
                        
        

        fp = io.BytesIO()
        wb.save(fp)
        out = base64.encodestring(fp.getvalue())
        view_report_status_id = self.env['track.course.completion.report'].create(
            {'excel_file': out, 'file_name': filename})
        return {
            'res_id': view_report_status_id.id,
            'name': 'Report',
            'view_mode': 'form',
            'res_model': 'track.course.completion.report',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }


class track_view_report(models.TransientModel):
    _name = 'track.course.completion.report'
    _rec_name = 'excel_file'

    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64)
