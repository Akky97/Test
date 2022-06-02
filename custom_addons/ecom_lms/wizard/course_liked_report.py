from odoo import fields, models, _
import io
import xlwt
from io import BytesIO
import base64
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from xlsxwriter.workbook import Workbook
from io import StringIO



class CourseLikedReport(models.TransientModel):
    _name = 'course.liked.report'
    
    # course_ids = fields.Many2many('slide.channel', 'course_liked_report_course_rel',
    #     'course_liked_report_id', 'course_id', string='Courses')
    #
    # region = fields.Selection([('all', 'All'),('north', 'North'),
    #                                   ('south', 'South'),
    #                                   ('east', 'East'),
    #                                   ('west', 'West'),
    #                                   ('ihq', 'IHQ'),
    #                                   ('central', 'Central'),],string='Region',default='all')
    
    course_journey = fields.Selection([('course', 'Course'),
                                      ('journey', 'Journey'),],string='Course/Journey',default='course')
                                      
    
    
    def button_print(self):

        string = 'Course Liked Report'
        wb = xlwt.Workbook(encoding='utf-8')
        worksheet = wb.add_sheet(string)
        filename = 'Course Liked Report' + '.xls'
        style_value = xlwt.easyxf(
            'font: bold on, name Arial ,colour_index black;')
        style_header = xlwt.easyxf(
            'font: bold on ,colour_index red;' "borders: top double , bottom double ,left double , right double;")

        worksheet.write_merge(0, 0, 0, 10, "Course Liked Report", xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz center;'))
        
        worksheet.write(1, 0, 'Course/Journey', style_value)
        worksheet.write(1, 1, 'Type', style_value)
        worksheet.write(1, 2, 'No. Of likes', style_value)
        worksheet.write(1, 3, 'No. Of Dislikes', style_value)
        a=2
        
        
        if self.course_journey=='course':
            self.env.cr.execute('SELECT id FROM slide_channel')
            channels = self.env.cr.fetchall()
            if channels:
                for channel_row in channels:
                    course_id = self.env['slide.channel'].browse(channel_row)
                    # if course.likes>0:
                    worksheet.write(a, 0, course_id.name or '')
                    worksheet.write(a, 1, 'Course' or '')
                    worksheet.write(a, 2, course_id.likes or 0)
                    worksheet.write(a, 3, course_id.dislikes or 0)
                    a=a+1
                    
                    
        if self.course_journey=='journey':
            self.env.cr.execute('SELECT id FROM course_journey')
            jouneys = self.env.cr.fetchall()
            if jouneys:
                for row in jouneys:
                    journey_id = self.env['course.journey'].browse(row)
            
                    worksheet.write(a, 0, journey_id.description_short or '')
                    worksheet.write(a, 1, 'Journey' or '')
                    worksheet.write(a, 2, journey_id.likes or 0)
                    worksheet.write(a, 3, journey_id.dislikes or 0)
                    a=a+1
        
                    
        
        # if self.env.user.has_group('base.group_system') or self.env.user.has_group('ecom_lms.admin_user_group'):
        #     if self.region == 'all':
        #         if self.course_ids:
        #             for course in self.course_ids:
        #                 if course.sudo().channel_partner_ids:
        #                     for attendee in course.sudo().channel_partner_ids:
        #                         if attendee.channel_liked:
        #                             code=''
        #                             if attendee.custom_user_id.customer_code:
        #                                 code = attendee.custom_user_id.customer_code
        #                             elif attendee.custom_user_id.emp_code:
        #                                 code = attendee.custom_user_id.emp_code
        #                             elif attendee.custom_user_id.pre_joinee_code:
        #                                 code = attendee.custom_user_id.pre_joinee_code
        #                             worksheet.write(a, 0, code or '')
        #                             worksheet.write(a, 1, attendee.custom_user_id.name or '')
        #                             worksheet.write(a, 3, attendee.custom_user_id.designation or '')
        #                             worksheet.write(a, 4, attendee.custom_user_id.state_id.name or '')
        #                             worksheet.write(a, 5, attendee.custom_user_id.work_location or '')
        #                             worksheet.write(a, 7, attendee.custom_user_id.band or '')
        #                             worksheet.write(a, 8, attendee.custom_user_id.region or '')
        #                             worksheet.write(a, 9, attendee.channel_id.name or '')
        #                             a=a+1
        #
        #         else:
        #             all_courses= self.env['slide.channel'].search([])
        #             for course in all_courses:
        #                 if course.sudo().channel_partner_ids:
        #                     for attendee in course.sudo().channel_partner_ids:
        #                         if attendee.channel_liked:
        #                             code=''
        #                             if attendee.custom_user_id.customer_code:
        #                                 code = attendee.custom_user_id.customer_code
        #                             elif attendee.custom_user_id.emp_code:
        #                                 code = attendee.custom_user_id.emp_code
        #                             elif attendee.custom_user_id.pre_joinee_code:
        #                                 code = attendee.custom_user_id.pre_joinee_code
        #                             worksheet.write(a, 0, code or '')
        #                             worksheet.write(a, 1, attendee.custom_user_id.name or '')
        #                             worksheet.write(a, 3, attendee.custom_user_id.designation or '')
        #                             worksheet.write(a, 4, attendee.custom_user_id.state_id.name or '')
        #                             worksheet.write(a, 5, attendee.custom_user_id.work_location or '')
        #                             worksheet.write(a, 7, attendee.custom_user_id.band or '')
        #                             worksheet.write(a, 8, attendee.custom_user_id.region or '')
        #                             worksheet.write(a, 9, attendee.channel_id.name or '')
        #                             a=a+1
        #
        #
        #     else:
        #         if self.course_ids:
        #             for course in self.course_ids:
        #                 if course.sudo().channel_partner_ids:
        #                     for attendee in course.sudo().channel_partner_ids:
        #                         if attendee.channel_liked and attendee.custom_user_id.region == self.region:
        #                             code=''
        #                             if attendee.custom_user_id.customer_code:
        #                                 code = attendee.custom_user_id.customer_code
        #                             elif attendee.custom_user_id.emp_code:
        #                                 code = attendee.custom_user_id.emp_code
        #                             elif attendee.custom_user_id.pre_joinee_code:
        #                                 code = attendee.custom_user_id.pre_joinee_code
        #                             worksheet.write(a, 0, code or '')
        #                             worksheet.write(a, 1, attendee.custom_user_id.name or '')
        #                             worksheet.write(a, 3, attendee.custom_user_id.designation or '')
        #                             worksheet.write(a, 4, attendee.custom_user_id.state_id.name or '')
        #                             worksheet.write(a, 5, attendee.custom_user_id.work_location or '')
        #                             worksheet.write(a, 7, attendee.custom_user_id.band or '')
        #                             worksheet.write(a, 8, attendee.custom_user_id.region or '')
        #                             worksheet.write(a, 9, attendee.channel_id.name or '')
        #                             a=a+1
        #         else:
        #             all_courses= self.env['slide.channel'].search([])
        #             for course in all_courses:
        #                 if course.sudo().channel_partner_ids:
        #                     for attendee in course.sudo().channel_partner_ids:
        #                         if attendee.channel_liked and attendee.custom_user_id.region == self.region:
        #                             code=''
        #                             if attendee.custom_user_id.customer_code:
        #                                 code = attendee.custom_user_id.customer_code
        #                             elif attendee.custom_user_id.emp_code:
        #                                 code = attendee.custom_user_id.emp_code
        #                             elif attendee.custom_user_id.pre_joinee_code:
        #                                 code = attendee.custom_user_id.pre_joinee_code
        #                             worksheet.write(a, 0, code or '')
        #                             worksheet.write(a, 1, attendee.custom_user_id.name or '')
        #                             worksheet.write(a, 3, attendee.custom_user_id.designation or '')
        #                             worksheet.write(a, 4, attendee.custom_user_id.state_id.name or '')
        #                             worksheet.write(a, 5, attendee.custom_user_id.work_location or '')
        #                             worksheet.write(a, 7, attendee.custom_user_id.band or '')
        #                             worksheet.write(a, 8, attendee.custom_user_id.region or '')
        #                             worksheet.write(a, 9, attendee.channel_id.name or '')
        #                             a=a+1
        #
        # elif self.env.user.has_group('ecom_lms.regional_admin_user_group') and not self.env.user.has_group('base.group_system'):
        #     if self.env.user.region != self.region or not self.env.user.region:
        #         raise UserError(_('You can access only your region details'))
        #
        #
        #     if self.course_ids:
        #         for course in self.course_ids:
        #             if course.sudo().channel_partner_ids:
        #                 for attendee in course.sudo().channel_partner_ids:
        #                     if attendee.channel_liked and attendee.custom_user_id.region == self.region:
        #                         code=''
        #                         if attendee.custom_user_id.customer_code:
        #                             code = attendee.custom_user_id.customer_code
        #                         elif attendee.custom_user_id.emp_code:
        #                             code = attendee.custom_user_id.emp_code
        #                         elif attendee.custom_user_id.pre_joinee_code:
        #                             code = attendee.custom_user_id.pre_joinee_code
        #                         worksheet.write(a, 0, code or '')
        #                         worksheet.write(a, 1, attendee.custom_user_id.name or '')
        #                         worksheet.write(a, 3, attendee.custom_user_id.designation or '')
        #                         worksheet.write(a, 4, attendee.custom_user_id.state_id.name or '')
        #                         worksheet.write(a, 5, attendee.custom_user_id.work_location or '')
        #                         worksheet.write(a, 7, attendee.custom_user_id.band or '')
        #                         worksheet.write(a, 8, attendee.custom_user_id.region or '')
        #                         worksheet.write(a, 9, attendee.channel_id.name or '')
        #                         a=a+1
        #     else:
        #         all_courses= self.env['slide.channel'].search([])
        #         for course in all_courses:
        #             if course.sudo().channel_partner_ids:
        #                 for attendee in course.sudo().channel_partner_ids:
        #                     if attendee.channel_liked and attendee.custom_user_id.region == self.region:
        #                         code=''
        #                         if attendee.custom_user_id.customer_code:
        #                             code = attendee.custom_user_id.customer_code
        #                         elif attendee.custom_user_id.emp_code:
        #                             code = attendee.custom_user_id.emp_code
        #                         elif attendee.custom_user_id.pre_joinee_code:
        #                             code = attendee.custom_user_id.pre_joinee_code
        #                         worksheet.write(a, 0, code or '')
        #                         worksheet.write(a, 1, attendee.custom_user_id.name or '')
        #                         worksheet.write(a, 3, attendee.custom_user_id.designation or '')
        #                         worksheet.write(a, 4, attendee.custom_user_id.state_id.name or '')
        #                         worksheet.write(a, 5, attendee.custom_user_id.work_location or '')
        #                         worksheet.write(a, 7, attendee.custom_user_id.band or '')
        #                         worksheet.write(a, 8, attendee.custom_user_id.region or '')
        #                         worksheet.write(a, 9, attendee.channel_id.name or '')
        #                         a=a+1
                    
                
        
        
        fp = io.BytesIO()
        wb.save(fp)
        out = base64.encodestring(fp.getvalue())
        view_report_status_id = self.env['course.liked.view.report'].create( {'excel_file':out, 'file_name':filename})
        return {
            'res_id'   :view_report_status_id.id,
            'name'     :'Report',
            'view_mode':'form',
            'res_model':'course.liked.view.report',
            'view_id'  : False ,
            'type'     :'ir.actions.act_window',
        }

    
    
    
    
class course_liked_view_report(models.TransientModel):
    _name = 'course.liked.view.report'
    _rec_name = 'excel_file'

    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64)
    
    