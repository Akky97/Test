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


class Review_report(models.TransientModel):
    _name = 'export.review'

    user_ids = fields.Many2many('res.users', 'export_review_rel',
                                'export_review_report_id', 'usr_id', string='User', )

    region = fields.Selection([('all','All'),('north', 'North'),
                               ('south', 'South'),
                               ('east', 'East'),
                               ('west', 'West'),
                               ('ihq', 'IHQ'),
                               ('central', 'Central'), ], string='Region',default='all')


    def button_print(self):
        string = 'Review Report'
        wb = xlwt.Workbook(encoding='utf-8')
        worksheet = wb.add_sheet(string)
        filename = 'Review Report' + '.xls'
        style_value = xlwt.easyxf(
            'font: bold on, name Arial ,colour_index black;')
        style_header = xlwt.easyxf(
            'font: bold on ,colour_index red;' "borders: top double , bottom double ,left double , right double;")

        worksheet.write_merge(0, 0, 0, 12, "Review Report", xlwt.easyxf(
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
        worksheet.write(1, 9, 'Resource/Course Name', style_value)
        worksheet.write(1, 10, 'Rating', style_value)
        worksheet.write(1, 11, 'Comment', style_value)
        worksheet.write(1, 12, 'Submitted On', style_value)
        a = 2

        if self.env.user.has_group('base.group_system')  or self.env.user.has_group('ecom_lms.admin_user_group'):
            if self.region != 'all':
                users_ids = self.env['res.users'].search([('region', '=', self.region)])

                for user in users_ids:
                    code = ''
                    course_lst = []
                    slide_channel_partner_obj = self.env['rating.rating'].search([('partner_id', '=', user.partner_id.id)])
                    print(slide_channel_partner_obj,"slideobj")
                    for slide_partner in slide_channel_partner_obj:
                        if slide_partner.id not in course_lst:
                            course_lst.append(slide_partner.id)

                    if len(course_lst) > 0:
                        for course in course_lst:
                            course_id = self.env['rating.rating'].browse(course)
                            new_partner = self.env['res.users'].sudo().search([('name', '=', course_id.partner_id.name)])
                            worksheet.write(a, 9, course_id.resource_ref.name or '')
                            worksheet.write(a, 11, course_id.feedback or '0')
                            worksheet.write(a, 10, course_id.rating_text or '')
                            worksheet.write(a, 12, course_id.create_date.strftime('%m/%d/%Y %H:%M:%S') or '')

                            if new_partner.customer_code:
                                code = new_partner.customer_code
                            elif new_partner.emp_code:
                                code = new_partner.emp_code
                            elif new_partner.pre_joinee_code:
                                code = new_partner.pre_joinee_code
                            worksheet.write(a, 0, code or '')
                            worksheet.write(a, 1, new_partner.name or '')
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
                            a += 1
                    else:
                        a += 0
            else:
                users_ids = self.env['res.users'].search([])

                for user in users_ids:
                    code = ''
                    course_lst = []
                    slide_channel_partner_obj = self.env['rating.rating'].search(
                        [('partner_id', '=', user.partner_id.id)])
                    print(slide_channel_partner_obj, "slideobj")
                    for slide_partner in slide_channel_partner_obj:
                        if slide_partner.id not in course_lst:
                            course_lst.append(slide_partner.id)

                    if len(course_lst) > 0:
                        for course in course_lst:
                            course_id = self.env['rating.rating'].browse(course)
                            new_partner = self.env['res.users'].sudo().search(
                                [('name', '=', course_id.partner_id.name)])
                            worksheet.write(a, 9, course_id.resource_ref.name or '')
                            worksheet.write(a, 11, course_id.feedback or '0')
                            worksheet.write(a, 10, course_id.rating_text or '')
                            worksheet.write(a, 12, course_id.create_date.strftime('%m/%d/%Y %H:%M:%S') or '')

                            if new_partner.customer_code:
                                code = new_partner.customer_code
                            elif new_partner.emp_code:
                                code = new_partner.emp_code
                            elif new_partner.pre_joinee_code:
                                code = new_partner.pre_joinee_code
                            worksheet.write(a, 0, code or '')
                            worksheet.write(a, 1, new_partner.name or '')
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
                slide_channel_partner_obj = self.env['rating.rating'].search(
                    [('partner_id', '=', user.partner_id.id)])
                for slide_partner in slide_channel_partner_obj:
                    if slide_partner.id not in course_lst:
                        course_lst.append(slide_partner.id)

                if len(course_lst) > 0:
                    for course in course_lst:
                        course_id = self.env['rating.rating'].sudo().browse(course)
                        print(course_id, "courseid222")
                        new_partner = self.env['res.users'].sudo().search([('name', '=', course_id.partner_id.name)])
                        worksheet.write(a, 9, course_id.resource_ref.name or '')
                        worksheet.write(a, 11, course_id.feedback or '0')
                        worksheet.write(a, 10, course_id.rating_text or '')
                        worksheet.write(a, 12, course_id.create_date.strftime('%m/%d/%Y %H:%M:%S') or '')

                        if new_partner.customer_code:
                            code = new_partner.customer_code
                        elif new_partner.emp_code:
                            code = new_partner.emp_code
                        elif new_partner.pre_joinee_code:
                            code = new_partner.pre_joinee_code
                        worksheet.write(a, 0, code or '')
                        worksheet.write(a, 1, new_partner.name or '')
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
                        a += 1
                else:
                    a += 0

        fp = io.BytesIO()
        wb.save(fp)
        out = base64.encodestring(fp.getvalue())
        view_report_status_id = self.env['export.review.report'].create(
            {'excel_file': out, 'file_name': filename})
        return {
            'res_id': view_report_status_id.id,
            'name': 'Report',
            'view_mode': 'form',
            'res_model': 'export.review.report',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }



class export_review_report(models.TransientModel):
    _name = 'export.review.report'
    _rec_name = 'excel_file'

    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64)