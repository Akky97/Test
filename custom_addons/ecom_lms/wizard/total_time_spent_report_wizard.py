import pandas as pd

from odoo import fields, models, _, api
import io
import xlwt
from io import BytesIO
import base64
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from xlsxwriter.workbook import Workbook
from io import StringIO


class TotalTimeSpentReportWizard(models.TransientModel):
    _name = 'total.time.spent.report.wizard'

    # user_ids = fields.Many2many('res.users', 'error_per_module_report_user_rel',
    #                             'error_per_module_report_id', 'usr_id', string='User')

    date_from = fields.Date('From')
    date_to = fields.Date('To')
    user = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    user_ids = fields.Many2many('res.users', 'total_time_spent_report_rel',
                                'total_time_report_id', 'user_id', string='Users', )
    user_role = fields.Char('User Role', compute='_compute_user_role')
    region = fields.Selection([('all', 'All'),
                               ('north', 'North'),
                               ('south', 'South'),
                               ('east', 'East'),
                               ('west', 'West'),
                               ('ihq', 'IHQ'),
                               ('central', 'Central'), ], string='Region', default='all')
    user_is_regional_admin = fields.Boolean('Regional Admin', default=False)

    @api.depends('user')
    def _compute_user_role(self):
        for rec in self:
            if rec.user.sudo().role_line_ids.role_id.name == 'Regional Admin':
                rec.user_is_regional_admin = True
                rec.user_role = 'Regional Admin'
            else:
                rec.user_is_regional_admin = False
                rec.user_role = ''

    def button_print(self):
        string = 'Total Time Spent Report'
        wb = xlwt.Workbook(encoding='utf-8')
        worksheet = wb.add_sheet(string)
        filename = 'Total Time Spent Report' + '.xls'
        style_value = xlwt.easyxf(
            'font: bold on, name Arial ,colour_index black;')
        style_header = xlwt.easyxf(
            'font: bold on ,colour_index red;' "borders: top double , bottom double ,left double , right double;")

        worksheet.write_merge(0, 0, 0, 12, "Total Time Spent Report", xlwt.easyxf(
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
        worksheet.write(1, 9, 'No. of Logins', style_value)
        worksheet.write(1, 10, 'Total Time Spent (HH:MM:SS)', style_value)
        a = 2

        if self.env.user.has_group('base.group_system') or self.env.user.has_group('ecom_lms.admin_user_group'):
            if self.region == 'all':
                if self.user_ids:
                    domain = [('id', 'in', self.user_ids.ids)]
                else:
                    domain = []
                if self.date_from and not self.date_to:
                    raise UserError(_('Please select "To" date.'))
                elif not self.date_from and self.date_to:
                    raise UserError(_('Please select "From" date.'))
                if self.date_from and self.date_to:
                    res_users = self.env['res.users'].sudo().search(domain)
                    for user in res_users:
                        time_spent_records = self.env['time.spent.report'].sudo().search(
                            [('name', '=', user.id), ('check_in_date', '>=', self.date_from),
                             ('check_out_date', '<=', self.date_to), ('logout', '=', True)])
                        time_spent_records_count = self.env['time.spent.report'].sudo().search_count(
                            [('name', '=', user.id), ('check_in_date', '>=', self.date_from),
                             ('check_out_date', '<=', self.date_to)])
                        time_spent_records_without_check_out_count = self.env['time.spent.report'].sudo().search_count(
                            [('name', '=', user.id), ('check_in_date', '>=', self.date_from),
                             ('check_out_date', '=', False), ('logout', '=', False)])
                        time_spent_records_without_check_out = self.env['time.spent.report'].sudo().search(
                            [('name', '=', user.id), ('check_in_date', '>=', self.date_from),
                             ('check_out_date', '=', False), ('logout', '=', False)])
                        if time_spent_records_without_check_out and time_spent_records_without_check_out_count:
                            no_of_logins = time_spent_records_without_check_out_count
                            time_spent = ''
                            employee_code = ''
                            name = ''
                            function_code = ''
                            designation = ''
                            state_name = ''
                            work_location_code = ''
                            cost_type_code = ''
                            band_code = ''
                            region = ''
                            hr = 0
                            min = 0
                            sec = 0
                            total_days = 0
                            for idx, record in enumerate(time_spent_records_without_check_out):
                                res_user = self.env['res.users'].sudo().search([('id', '=', record.name.id)])
                                days = ''
                                hh_mm_ss = ''
                                if record.time_spent:
                                    time_spent = record.time_spent
                                    split_time = time_spent.split(',')
                                    if (len(split_time)) == 1:
                                        hh_mm_ss = split_time[-1].split(':')
                                        hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(
                                            hh_mm_ss[2])
                                    if (len(split_time)) == 2:
                                        days = split_time[0]
                                        days_split = days.split('days') or days.split('day')
                                        total_days = int(total_days) + int(days_split[0])
                                        hh_mm_ss = split_time[-1].split(':')
                                        hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(hh_mm_ss[2])
                                if not record.time_spent:
                                    now = datetime.now()
                                    hr_min_sec = (now - record.check_in)
                                    split_time = str(hr_min_sec).split(',')
                                    if (len(split_time)) == 1:
                                        hh_mm_ss = split_time[-1].split(':')
                                        hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(
                                            float(hh_mm_ss[2]))
                                    if (len(split_time)) == 2:
                                        days = split_time[0]
                                        days_split = days.split('day') or days.split('days')
                                        total_days = int(total_days) + int(days_split[0])
                                        hh_mm_ss = split_time[-1].split(':')
                                        hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(float(hh_mm_ss[2]))
                                if idx == (len(time_spent_records_without_check_out) - 1):
                                    tdelta = timedelta(hours=hr, minutes=min, seconds=sec)
                                    if str(tdelta).find('day') != -1:
                                        split_days = str(tdelta).split(',')
                                        add_days = str(split_days[0]).split('day')
                                        total_days = str((int(add_days[0]) + int(total_days)))
                                        days_into_hours = int(total_days) * 24
                                        split_hours = str(split_days[-1]).split(':')
                                        tt_hours = split_hours[0]
                                        complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                        time_spent = complete_duration
                                        # time_spent = str(total_days) + ' days ,' + split_days[-1]
                                        user_code = record.user_code
                                        name = record.name.name
                                        function_code = record.function_code
                                        designation = record.designation
                                        state_name = record.state_name
                                        work_location_code = record.work_location_code
                                        cost_type_code = record.cost_type_code
                                        band_code = record.band_code
                                        region = record.region
                                        worksheet.write(a, 0, user_code or '')
                                        worksheet.write(a, 1, name or '')
                                        worksheet.write(a, 2, function_code or '')
                                        worksheet.write(a, 3, designation or '')
                                        worksheet.write(a, 4, state_name or '')
                                        worksheet.write(a, 5, work_location_code or '')
                                        worksheet.write(a, 6, cost_type_code or '')
                                        worksheet.write(a, 7, band_code or '')
                                        worksheet.write(a, 8, str(res_user.region) or '')
                                        worksheet.write(a, 9, no_of_logins or '')
                                        worksheet.write(a, 10, str(time_spent) or '')
                                        a += 1
                                    else:
                                        days_into_hours = int(total_days) * 24
                                        split_hours = str(tdelta).split(':')
                                        tt_hours = split_hours[0]
                                        complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                        time_spent = complete_duration
                                        # time_spent = str(tdelta)
                                        user_code = record.user_code
                                        name = record.name.name
                                        function_code = record.function_code
                                        designation = record.designation
                                        state_name = record.state_name
                                        work_location_code = record.work_location_code
                                        cost_type_code = record.cost_type_code
                                        band_code = record.band_code
                                        region = str(res_user.region)
                                        worksheet.write(a, 0, user_code or '')
                                        worksheet.write(a, 1, name or '')
                                        worksheet.write(a, 2, function_code or '')
                                        worksheet.write(a, 3, designation or '')
                                        worksheet.write(a, 4, state_name or '')
                                        worksheet.write(a, 5, work_location_code or '')
                                        worksheet.write(a, 6, cost_type_code or '')
                                        worksheet.write(a, 7, band_code or '')
                                        worksheet.write(a, 8, region or '')
                                        worksheet.write(a, 9, no_of_logins or '')
                                        worksheet.write(a, 10, str(time_spent) or '')
                                        a += 1
                        else:
                            no_of_logins = time_spent_records_count
                            time_spent = ''
                            employee_code = ''
                            name = ''
                            function_code = ''
                            designation = ''
                            state_name = ''
                            work_location_code = ''
                            cost_type_code = ''
                            band_code = ''
                            region = ''
                            hr = 0
                            min = 0
                            sec = 0
                            total_days = 0
                            for idx, record in enumerate(time_spent_records):
                                res_user = self.env['res.users'].sudo().search([('id', '=', record.name.id)])
                                days = ''
                                hh_mm_ss = ''
                                if record.time_spent:
                                    time_spent = record.time_spent
                                    split_time = time_spent.split(',')
                                    if (len(split_time)) == 1:
                                        hh_mm_ss = split_time[-1].split(':')
                                        hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(
                                            hh_mm_ss[2])
                                    if (len(split_time)) == 2:
                                        days = split_time[0]
                                        days_split = days.split('days') or days.split('day')
                                        total_days = int(total_days) + int(days_split[0])
                                        hh_mm_ss = split_time[-1].split(':')
                                        hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(hh_mm_ss[2])
                                if not record.time_spent:
                                    now = datetime.now()
                                    hr_min_sec = (now - record.check_in)
                                    split_time = str(hr_min_sec).split(',')
                                    if (len(split_time)) == 1:
                                        hh_mm_ss = split_time[-1].split(':')
                                        hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(
                                            float(hh_mm_ss[2]))
                                    if (len(split_time)) == 2:
                                        days = split_time[0]
                                        days_split = days.split('day') or days.split('days')
                                        total_days = int(total_days) + int(days_split[0])
                                        hh_mm_ss = split_time[-1].split(':')
                                        hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(float(hh_mm_ss[2]))
                                if idx == (len(time_spent_records) - 1):
                                    tdelta = timedelta(hours=hr, minutes=min, seconds=sec)
                                    if str(tdelta).find('day') != -1:
                                        split_days = str(tdelta).split(',')
                                        add_days = str(split_days[0]).split('day')
                                        total_days = str((int(add_days[0]) + int(total_days)))
                                        days_into_hours = int(total_days) * 24
                                        split_hours = str(split_days[-1]).split(':')
                                        tt_hours = split_hours[0]
                                        complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                        time_spent = complete_duration
                                        # time_spent = str(total_days)+' days ,'+split_days[-1]
                                        user_code = record.user_code
                                        name = record.name.name
                                        function_code = record.function_code
                                        designation = record.designation
                                        state_name = record.state_name
                                        work_location_code = record.work_location_code
                                        cost_type_code = record.cost_type_code
                                        band_code = record.band_code
                                        region = record.region
                                        worksheet.write(a, 0, user_code or '')
                                        worksheet.write(a, 1, name or '')
                                        worksheet.write(a, 2, function_code or '')
                                        worksheet.write(a, 3, designation or '')
                                        worksheet.write(a, 4, state_name or '')
                                        worksheet.write(a, 5, work_location_code or '')
                                        worksheet.write(a, 6, cost_type_code or '')
                                        worksheet.write(a, 7, band_code or '')
                                        worksheet.write(a, 8, str(res_user.region) or '')
                                        worksheet.write(a, 9, no_of_logins or '')
                                        worksheet.write(a, 10, str(time_spent) or '')
                                        a += 1
                                    else:
                                        days_into_hours = int(total_days) * 24
                                        split_hours = str(tdelta).split(':')
                                        tt_hours = split_hours[0]
                                        complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                        time_spent = complete_duration
                                        # time_spent = str(tdelta)
                                        user_code = record.user_code
                                        name = record.name.name
                                        function_code = record.function_code
                                        designation = record.designation
                                        state_name = record.state_name
                                        work_location_code = record.work_location_code
                                        cost_type_code = record.cost_type_code
                                        band_code = record.band_code
                                        region = str(res_user.region)
                                        worksheet.write(a, 0, user_code or '')
                                        worksheet.write(a, 1, name or '')
                                        worksheet.write(a, 2, function_code or '')
                                        worksheet.write(a, 3, designation or '')
                                        worksheet.write(a, 4, state_name or '')
                                        worksheet.write(a, 5, work_location_code or '')
                                        worksheet.write(a, 6, cost_type_code or '')
                                        worksheet.write(a, 7, band_code or '')
                                        worksheet.write(a, 8, region or '')
                                        worksheet.write(a, 9, no_of_logins or '')
                                        worksheet.write(a, 10, str(time_spent) or '')
                                        a += 1
                else:
                    res_users = self.env['res.users'].sudo().search(domain)
                    for user in res_users:
                        time_spent_records = self.env['time.spent.report'].sudo().search([('name', '=', user.id)])
                        time_spent_records_count = self.env['time.spent.report'].sudo().search_count(
                            [('name', '=', user.id)])
                        no_of_logins = time_spent_records_count
                        time_spent = ''
                        employee_code = ''
                        name = ''
                        function_code = ''
                        designation = ''
                        state_name = ''
                        work_location_code = ''
                        cost_type_code = ''
                        band_code = ''
                        region = ''
                        hr = 0
                        min = 0
                        sec = 0
                        total_days = 0
                        for idx, record in enumerate(time_spent_records):
                            res_user = self.env['res.users'].sudo().search([('id', '=', record.name.id)])
                            days = ''
                            hh_mm_ss = ''
                            if record.time_spent:
                                time_spent = record.time_spent
                                split_time = time_spent.split(',')
                                if (len(split_time)) == 1:
                                    hh_mm_ss = split_time[-1].split(':')
                                    hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(hh_mm_ss[2])
                                if (len(split_time)) == 2:
                                    days = split_time[0]
                                    days_split = days.split('day') or days.split('days')
                                    total_days = int(total_days) + int(days_split[0])
                                    hh_mm_ss = split_time[-1].split(':')
                                    hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(hh_mm_ss[2])
                            if not record.time_spent:
                                now = datetime.now()
                                hr_min_sec = (now - record.check_in)
                                split_time = str(hr_min_sec).split(',')
                                if (len(split_time)) == 1:
                                    hh_mm_ss = split_time[-1].split(':')
                                    hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(
                                        float(hh_mm_ss[2]))
                                if (len(split_time)) == 2:
                                    days = split_time[0]
                                    days_split = days.split('day') or days.split('days')
                                    total_days = int(total_days) + int(days_split[0])
                                    hh_mm_ss = split_time[-1].split(':')
                                    hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(float(hh_mm_ss[2]))
                            if idx == (len(time_spent_records) - 1):
                                tdelta = timedelta(hours=hr, minutes=min, seconds=sec)
                                if str(tdelta).find('day') != -1:
                                    split_days = str(tdelta).split(',')
                                    add_days = str(split_days[0]).split('day')
                                    total_days = str((int(add_days[0]) + int(total_days)))
                                    days_into_hours = int(total_days) * 24
                                    split_hours = str(split_days[-1]).split(':')
                                    tt_hours = split_hours[0]
                                    complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                    time_spent = complete_duration
                                    # time_spent = str(total_days)+' days ,'+split_days[-1]
                                    user_code = record.user_code
                                    name = record.name.name
                                    function_code = record.function_code
                                    designation = record.designation
                                    state_name = record.state_name
                                    work_location_code = record.work_location_code
                                    cost_type_code = record.cost_type_code
                                    band_code = record.band_code
                                    region = str(res_user.region)
                                    worksheet.write(a, 0, user_code or '')
                                    worksheet.write(a, 1, name or '')
                                    worksheet.write(a, 2, function_code or '')
                                    worksheet.write(a, 3, designation or '')
                                    worksheet.write(a, 4, state_name or '')
                                    worksheet.write(a, 5, work_location_code or '')
                                    worksheet.write(a, 6, cost_type_code or '')
                                    worksheet.write(a, 7, band_code or '')
                                    worksheet.write(a, 8, region or '')
                                    worksheet.write(a, 9, no_of_logins or '')
                                    worksheet.write(a, 10, str(time_spent) or '')
                                    a += 1
                                else:
                                    days_into_hours = int(total_days) * 24
                                    split_hours = str(tdelta).split(':')
                                    tt_hours = split_hours[0]
                                    complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                    time_spent = complete_duration
                                    # time_spent = str(tdelta)
                                    user_code = record.user_code
                                    name = record.name.name
                                    function_code = record.function_code
                                    designation = record.designation
                                    state_name = record.state_name
                                    work_location_code = record.work_location_code
                                    cost_type_code = record.cost_type_code
                                    band_code = record.band_code
                                    region = str(res_user.region)
                                    worksheet.write(a, 0, user_code or '')
                                    worksheet.write(a, 1, name or '')
                                    worksheet.write(a, 2, function_code or '')
                                    worksheet.write(a, 3, designation or '')
                                    worksheet.write(a, 4, state_name or '')
                                    worksheet.write(a, 5, work_location_code or '')
                                    worksheet.write(a, 6, cost_type_code or '')
                                    worksheet.write(a, 7, band_code or '')
                                    worksheet.write(a, 8, region or '')
                                    worksheet.write(a, 9, no_of_logins or '')
                                    worksheet.write(a, 10, str(time_spent) or '')
                                    a += 1

            else:
                if self.user_ids:
                    domain = [('id', 'in', self.user_ids.ids), ('region', '=', self.region)]
                else:
                    domain = []
                if self.date_from and not self.date_to:
                    raise UserError(_('Please select "To" date.'))
                elif not self.date_from and self.date_to:
                    raise UserError(_('Please select "From" date.'))
                if self.date_from and self.date_to:
                    res_users = self.env['res.users'].sudo().search(domain)
                    for user in res_users:
                        time_spent_records = self.env['time.spent.report'].sudo().search(
                            [('name', '=', user.id), ('check_in_date', '>=', self.date_from),
                             ('check_out_date', '<=', self.date_to)])
                        time_spent_records_count = self.env['time.spent.report'].sudo().search_count(
                            [('name', '=', user.id), ('check_in_date', '>=', self.date_from),
                             ('check_out_date', '<=', self.date_to)])
                        time_spent_records_without_check_out_count = self.env['time.spent.report'].sudo().search_count(
                            [('name', '=', user.id), ('check_in_date', '>=', self.date_from),
                             ('check_out_date', '=', None)])
                        time_spent_records_without_check_out = self.env['time.spent.report'].sudo().search(
                            [('name', '=', user.id), ('check_in_date', '>=', self.date_from),
                             ('check_out_date', '=', None)])
                        if time_spent_records_without_check_out and time_spent_records_without_check_out_count:
                            no_of_logins = time_spent_records_without_check_out_count
                            time_spent = ''
                            employee_code = ''
                            name = ''
                            function_code = ''
                            designation = ''
                            state_name = ''
                            work_location_code = ''
                            cost_type_code = ''
                            band_code = ''
                            region = ''
                            hr = 0
                            min = 0
                            sec = 0
                            total_days = 0
                            for idx, record in enumerate(time_spent_records_without_check_out):
                                res_user = self.env['res.users'].sudo().search([('id', '=', record.name.id)])
                                days = ''
                                hh_mm_ss = ''
                                if record.time_spent:
                                    time_spent = record.time_spent
                                    split_time = time_spent.split(',')
                                    if (len(split_time)) == 1:
                                        hh_mm_ss = split_time[-1].split(':')
                                        hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(
                                            hh_mm_ss[2])
                                    if (len(split_time)) == 2:
                                        days = split_time[0]
                                        days_split = days.split('days') or days.split('day')
                                        total_days = int(total_days) + int(days_split[0])
                                        hh_mm_ss = split_time[-1].split(':')
                                        hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(hh_mm_ss[2])
                                if not record.time_spent:
                                    now = datetime.now()
                                    hr_min_sec = (now - record.check_in)
                                    split_time = str(hr_min_sec).split(',')
                                    if (len(split_time)) == 1:
                                        hh_mm_ss = split_time[-1].split(':')
                                        hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(
                                            float(hh_mm_ss[2]))
                                    if (len(split_time)) == 2:
                                        days = split_time[0]
                                        days_split = days.split('day') or days.split('days')
                                        total_days = int(total_days) + int(days_split[0])
                                        hh_mm_ss = split_time[-1].split(':')
                                        hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(float(hh_mm_ss[2]))
                                if idx == (len(time_spent_records_without_check_out) - 1):
                                    tdelta = timedelta(hours=hr, minutes=min, seconds=sec)
                                    if str(tdelta).find('day') != -1:
                                        split_days = str(tdelta).split(',')
                                        add_days = str(split_days[0]).split('day')
                                        total_days = str((int(add_days[0]) + int(total_days)))
                                        days_into_hours = int(total_days) * 24
                                        split_hours = str(split_days[-1]).split(':')
                                        tt_hours = split_hours[0]
                                        complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                        time_spent = complete_duration
                                        # time_spent = str(total_days) + ' days ,' + split_days[-1]
                                        user_code = record.user_code
                                        name = record.name.name
                                        function_code = record.function_code
                                        designation = record.designation
                                        state_name = record.state_name
                                        work_location_code = record.work_location_code
                                        cost_type_code = record.cost_type_code
                                        band_code = record.band_code
                                        region = record.region
                                        worksheet.write(a, 0, user_code or '')
                                        worksheet.write(a, 1, name or '')
                                        worksheet.write(a, 2, function_code or '')
                                        worksheet.write(a, 3, designation or '')
                                        worksheet.write(a, 4, state_name or '')
                                        worksheet.write(a, 5, work_location_code or '')
                                        worksheet.write(a, 6, cost_type_code or '')
                                        worksheet.write(a, 7, band_code or '')
                                        worksheet.write(a, 8, str(res_user.region) or '')
                                        worksheet.write(a, 9, no_of_logins or '')
                                        worksheet.write(a, 10, str(time_spent) or '')
                                        a += 1
                                    else:
                                        days_into_hours = int(total_days) * 24
                                        split_hours = str(tdelta).split(':')
                                        tt_hours = split_hours[0]
                                        complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                        time_spent = complete_duration
                                        # time_spent = str(tdelta)
                                        user_code = record.user_code
                                        name = record.name.name
                                        function_code = record.function_code
                                        designation = record.designation
                                        state_name = record.state_name
                                        work_location_code = record.work_location_code
                                        cost_type_code = record.cost_type_code
                                        band_code = record.band_code
                                        region = str(res_user.region)
                                        worksheet.write(a, 0, user_code or '')
                                        worksheet.write(a, 1, name or '')
                                        worksheet.write(a, 2, function_code or '')
                                        worksheet.write(a, 3, designation or '')
                                        worksheet.write(a, 4, state_name or '')
                                        worksheet.write(a, 5, work_location_code or '')
                                        worksheet.write(a, 6, cost_type_code or '')
                                        worksheet.write(a, 7, band_code or '')
                                        worksheet.write(a, 8, region or '')
                                        worksheet.write(a, 9, no_of_logins or '')
                                        worksheet.write(a, 10, str(time_spent) or '')
                                        a += 1
                        else:
                            no_of_logins = time_spent_records_count
                            time_spent = ''
                            employee_code = ''
                            name = ''
                            function_code = ''
                            designation = ''
                            state_name = ''
                            work_location_code = ''
                            cost_type_code = ''
                            band_code = ''
                            region = ''
                            hr = 0
                            min = 0
                            sec = 0
                            total_days = 0
                            for idx, record in enumerate(time_spent_records):
                                res_user = self.env['res.users'].sudo().search([('id', '=', record.name.id)])
                                days = ''
                                hh_mm_ss = ''
                                if record.time_spent:
                                    time_spent = record.time_spent
                                    split_time = time_spent.split(',')
                                    if (len(split_time)) == 1:
                                        hh_mm_ss = split_time[-1].split(':')
                                        hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(
                                            hh_mm_ss[2])
                                    if (len(split_time)) == 2:
                                        days = split_time[0]
                                        days_split = days.split('day') or days.split('days')
                                        total_days = int(total_days) + int(days_split[0])
                                        hh_mm_ss = split_time[-1].split(':')
                                        hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(hh_mm_ss[2])
                                if not record.time_spent:
                                    now = datetime.now()
                                    hr_min_sec = (now - record.check_in)
                                    split_time = str(hr_min_sec).split(',')
                                    if (len(split_time)) == 1:
                                        hh_mm_ss = split_time[-1].split(':')
                                        hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(
                                            float(hh_mm_ss[2]))
                                    if (len(split_time)) == 2:
                                        days = split_time[0]
                                        days_split = days.split('day') or days.split('days')
                                        total_days = int(total_days) + int(days_split[0])
                                        hh_mm_ss = split_time[-1].split(':')
                                        hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(float(hh_mm_ss[2]))
                                if idx == (len(time_spent_records) - 1):
                                    tdelta = timedelta(hours=hr, minutes=min, seconds=sec)
                                    if str(tdelta).find('day') != -1:
                                        split_days = str(tdelta).split(',')
                                        add_days = str(split_days[0]).split('day')
                                        total_days = str((int(add_days[0]) + int(total_days)))
                                        days_into_hours = int(total_days) * 24
                                        split_hours = str(split_days[-1]).split(':')
                                        tt_hours = split_hours[0]
                                        complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                        time_spent = complete_duration
                                        # time_spent = str(total_days)+' days ,'+split_days[-1]
                                        user_code = record.user_code
                                        name = record.name.name
                                        function_code = record.function_code
                                        designation = record.designation
                                        state_name = record.state_name
                                        work_location_code = record.work_location_code
                                        cost_type_code = record.cost_type_code
                                        band_code = record.band_code
                                        region = str(res_user.region)
                                        worksheet.write(a, 0, user_code or '')
                                        worksheet.write(a, 1, name or '')
                                        worksheet.write(a, 2, function_code or '')
                                        worksheet.write(a, 3, designation or '')
                                        worksheet.write(a, 4, state_name or '')
                                        worksheet.write(a, 5, work_location_code or '')
                                        worksheet.write(a, 6, cost_type_code or '')
                                        worksheet.write(a, 7, band_code or '')
                                        worksheet.write(a, 8, region or '')
                                        worksheet.write(a, 9, no_of_logins or '')
                                        worksheet.write(a, 10, str(time_spent) or '')
                                        a += 1
                                    else:
                                        days_into_hours = int(total_days) * 24
                                        split_hours = str(tdelta).split(':')
                                        tt_hours = split_hours[0]
                                        complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                        time_spent = complete_duration
                                        # time_spent = str(tdelta)
                                        user_code = record.user_code
                                        name = record.name.name
                                        function_code = record.function_code
                                        designation = record.designation
                                        state_name = record.state_name
                                        work_location_code = record.work_location_code
                                        cost_type_code = record.cost_type_code
                                        band_code = record.band_code
                                        region = str(res_user.region)
                                        worksheet.write(a, 0, user_code or '')
                                        worksheet.write(a, 1, name or '')
                                        worksheet.write(a, 2, function_code or '')
                                        worksheet.write(a, 3, designation or '')
                                        worksheet.write(a, 4, state_name or '')
                                        worksheet.write(a, 5, work_location_code or '')
                                        worksheet.write(a, 6, cost_type_code or '')
                                        worksheet.write(a, 7, band_code or '')
                                        worksheet.write(a, 8, region or '')
                                        worksheet.write(a, 9, no_of_logins or '')
                                        worksheet.write(a, 10, str(time_spent) or '')
                                        a += 1
                else:
                    res_users = self.env['res.users'].sudo().search(domain)
                    for user in res_users:
                        time_spent_records = self.env['time.spent.report'].sudo().search([('name', '=', user.id)])
                        time_spent_records_count = self.env['time.spent.report'].sudo().search_count(
                            [('name', '=', user.id)])
                        no_of_logins = time_spent_records_count
                        time_spent = ''
                        employee_code = ''
                        name = ''
                        function_code = ''
                        designation = ''
                        state_name = ''
                        work_location_code = ''
                        cost_type_code = ''
                        band_code = ''
                        region = ''
                        hr = 0
                        min = 0
                        sec = 0
                        total_days = 0
                        for idx, record in enumerate(time_spent_records):
                            res_user = self.env['res.users'].sudo().search([('id', '=', record.name.id)])
                            days = ''
                            hh_mm_ss = ''
                            if record.time_spent:
                                time_spent = record.time_spent
                                split_time = time_spent.split(',')
                                if (len(split_time)) == 1:
                                    hh_mm_ss = split_time[-1].split(':')
                                    hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(hh_mm_ss[2])
                                if (len(split_time)) == 2:
                                    days = split_time[0]
                                    days_split = days.split('day') or days.split('days')
                                    total_days = int(total_days) + int(days_split[0])
                                    hh_mm_ss = split_time[-1].split(':')
                                    hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(hh_mm_ss[2])
                            if not record.time_spent:
                                now = datetime.now()
                                hr_min_sec = (now - record.check_in)
                                split_time = str(hr_min_sec).split(',')
                                if (len(split_time)) == 1:
                                    hh_mm_ss = split_time[-1].split(':')
                                    hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(
                                        float(hh_mm_ss[2]))
                                if (len(split_time)) == 2:
                                    days = split_time[0]
                                    days_split = days.split('day') or days.split('days')
                                    total_days = int(total_days) + int(days_split[0])
                                    hh_mm_ss = split_time[-1].split(':')
                                    hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(float(hh_mm_ss[2]))
                            if idx == (len(time_spent_records) - 1):
                                tdelta = timedelta(hours=hr, minutes=min, seconds=sec)
                                if str(tdelta).find('day') != -1:
                                    split_days = str(tdelta).split(',')
                                    add_days = str(split_days[0]).split('day')
                                    total_days = str((int(add_days[0]) + int(total_days)))
                                    days_into_hours = int(total_days) * 24
                                    split_hours = str(split_days[-1]).split(':')
                                    tt_hours = split_hours[0]
                                    complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                    time_spent = complete_duration
                                    # time_spent = str(total_days)+' days ,'+split_days[-1]
                                    user_code = record.user_code
                                    name = record.name.name
                                    function_code = record.function_code
                                    designation = record.designation
                                    state_name = record.state_name
                                    work_location_code = record.work_location_code
                                    cost_type_code = record.cost_type_code
                                    band_code = record.band_code
                                    region = str(res_user.region)
                                    worksheet.write(a, 0, user_code or '')
                                    worksheet.write(a, 1, name or '')
                                    worksheet.write(a, 2, function_code or '')
                                    worksheet.write(a, 3, designation or '')
                                    worksheet.write(a, 4, state_name or '')
                                    worksheet.write(a, 5, work_location_code or '')
                                    worksheet.write(a, 6, cost_type_code or '')
                                    worksheet.write(a, 7, band_code or '')
                                    worksheet.write(a, 8, region or '')
                                    worksheet.write(a, 9, no_of_logins or '')
                                    worksheet.write(a, 10, str(time_spent) or '')
                                    a += 1
                                else:
                                    days_into_hours = int(total_days) * 24
                                    split_hours = str(tdelta).split(':')
                                    tt_hours = split_hours[0]
                                    complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                    time_spent = complete_duration
                                    # time_spent = str(tdelta)
                                    user_code = record.user_code
                                    name = record.name.name
                                    function_code = record.function_code
                                    designation = record.designation
                                    state_name = record.state_name
                                    work_location_code = record.work_location_code
                                    cost_type_code = record.cost_type_code
                                    band_code = record.band_code
                                    region = str(res_user.region)
                                    worksheet.write(a, 0, user_code or '')
                                    worksheet.write(a, 1, name or '')
                                    worksheet.write(a, 2, function_code or '')
                                    worksheet.write(a, 3, designation or '')
                                    worksheet.write(a, 4, state_name or '')
                                    worksheet.write(a, 5, work_location_code or '')
                                    worksheet.write(a, 6, cost_type_code or '')
                                    worksheet.write(a, 7, band_code or '')
                                    worksheet.write(a, 8, region or '')
                                    worksheet.write(a, 9, no_of_logins or '')
                                    worksheet.write(a, 10, str(time_spent) or '')
                                    a += 1
        elif self.env.user.has_group('ecom_lms.regional_admin_user_group') and not self.env.user.has_group(
                'base.group_system') and not self.env.user.has_group('ecom_lms.admin_user_group'):
            if self.env.user.region != self.region or not self.env.user.region:
                raise UserError(_('You can access only your region details'))
            if self.user_ids:
                domain = [('id', 'in', self.user_ids.ids), ('region', '=', self.region)]
            else:
                domain = [(('region', '=', self.env.user.region))]
            if self.date_from and not self.date_to:
                raise UserError(_('Please select "To" date.'))
            elif not self.date_from and self.date_to:
                raise UserError(_('Please select "From" date.'))
            if self.date_from and self.date_to:
                res_users = self.env['res.users'].sudo().search(domain)
                for user in res_users:
                    time_spent_records = self.env['time.spent.report'].sudo().search(
                        [('name', '=', user.id), ('check_in_date', '>=', self.date_from),
                         ('check_out_date', '<=', self.date_to)])
                    time_spent_records_count = self.env['time.spent.report'].sudo().search_count(
                        [('name', '=', user.id), ('check_in_date', '>=', self.date_from),
                         ('check_out_date', '<=', self.date_to)])
                    no_of_logins = time_spent_records_count
                    time_spent = ''
                    employee_code = ''
                    name = ''
                    function_code = ''
                    designation = ''
                    state_name = ''
                    work_location_code = ''
                    cost_type_code = ''
                    band_code = ''
                    region = ''
                    hr = 0
                    min = 0
                    sec = 0
                    total_days = 0
                    for idx, record in enumerate(time_spent_records):
                        res_user = self.env['res.users'].sudo().search([('id', '=', record.name.id)])
                        days = ''
                        hh_mm_ss = ''
                        if record.time_spent:
                            time_spent = record.time_spent
                            split_time = time_spent.split(',')
                            if (len(split_time)) == 1:
                                hh_mm_ss = split_time[-1].split(':')
                                hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(hh_mm_ss[2])
                            if (len(split_time)) == 2:
                                days = split_time[0]
                                days_split = days.split('day') or days.split('days')
                                total_days = int(total_days) + int(days_split[0])
                                hh_mm_ss = split_time[-1].split(':')
                                hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(hh_mm_ss[2])
                        if not record.time_spent:
                            now = datetime.now()
                            hr_min_sec = (now - record.check_in)
                            split_time = str(hr_min_sec).split(',')
                            if (len(split_time)) == 1:
                                hh_mm_ss = split_time[-1].split(':')
                                hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(
                                    float(hh_mm_ss[2]))
                            if (len(split_time)) == 2:
                                days = split_time[0]
                                days_split = days.split('day') or days.split('days')
                                total_days = int(total_days) + int(days_split[0])
                                hh_mm_ss = split_time[-1].split(':')
                                hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(float(hh_mm_ss[2]))
                        if idx == (len(time_spent_records) - 1):
                            tdelta = timedelta(hours=hr, minutes=min, seconds=sec)
                            if str(tdelta).find('day') != -1:
                                split_days = str(tdelta).split(',')
                                add_days = str(split_days[0]).split('day')
                                total_days = str((int(add_days[0]) + int(total_days)))
                                days_into_hours = int(total_days) * 24
                                split_hours = str(split_days[-1]).split(':')
                                tt_hours = split_hours[0]
                                complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                time_spent = complete_duration
                                # time_spent = str(total_days) + ' days ,' + split_days[-1]
                                user_code = record.user_code
                                name = record.name.name
                                function_code = record.function_code
                                designation = record.designation
                                state_name = record.state_name
                                work_location_code = record.work_location_code
                                cost_type_code = record.cost_type_code
                                band_code = record.band_code
                                worksheet.write(a, 0, user_code or '')
                                worksheet.write(a, 1, name or '')
                                worksheet.write(a, 2, function_code or '')
                                worksheet.write(a, 3, designation or '')
                                worksheet.write(a, 4, state_name or '')
                                worksheet.write(a, 5, work_location_code or '')
                                worksheet.write(a, 6, cost_type_code or '')
                                worksheet.write(a, 7, band_code or '')
                                worksheet.write(a, 8, str(res_user.region) or '')
                                worksheet.write(a, 9, no_of_logins or '')
                                worksheet.write(a, 10, str(time_spent) or '')
                                a += 1
                            else:
                                days_into_hours = int(total_days) * 24
                                split_hours = str(tdelta).split(':')
                                tt_hours = split_hours[0]
                                complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                time_spent = complete_duration
                                # time_spent = str(tdelta)
                                user_code = record.user_code
                                name = record.name.name
                                function_code = record.function_code
                                designation = record.designation
                                state_name = record.state_name
                                work_location_code = record.work_location_code
                                cost_type_code = record.cost_type_code
                                band_code = record.band_code
                                worksheet.write(a, 0, user_code or '')
                                worksheet.write(a, 1, name or '')
                                worksheet.write(a, 2, function_code or '')
                                worksheet.write(a, 3, designation or '')
                                worksheet.write(a, 4, state_name or '')
                                worksheet.write(a, 5, work_location_code or '')
                                worksheet.write(a, 6, cost_type_code or '')
                                worksheet.write(a, 7, band_code or '')
                                worksheet.write(a, 8, str(res_user.region) or '')
                                worksheet.write(a, 9, str(no_of_logins) or '')
                                worksheet.write(a, 10, str(time_spent) or '')
                                a += 1
                    time_spent_records_without_check_out_count = self.env['time.spent.report'].sudo().search_count(
                        [('name', '=', user.id), ('check_in_date', '>=', self.date_from),
                         ('check_out_date', '=', None)])
                    time_spent_records_without_check_out = self.env['time.spent.report'].sudo().search(
                        [('name', '=', user.id), ('check_in_date', '>=', self.date_from),
                         ('check_out_date', '=', None)])
                    if time_spent_records_without_check_out and time_spent_records_without_check_out_count:
                        no_of_logins = time_spent_records_without_check_out_count
                        time_spent = ''
                        employee_code = ''
                        name = ''
                        function_code = ''
                        designation = ''
                        state_name = ''
                        work_location_code = ''
                        cost_type_code = ''
                        band_code = ''
                        region = ''
                        hr = 0
                        min = 0
                        sec = 0
                        total_days = 0
                        for idx, record in enumerate(time_spent_records_without_check_out):
                            res_user = self.env['res.users'].sudo().search([('id', '=', record.name.id)])
                            days = ''
                            hh_mm_ss = ''
                            if record.time_spent:
                                time_spent = record.time_spent
                                split_time = time_spent.split(',')
                                if (len(split_time)) == 1:
                                    hh_mm_ss = split_time[-1].split(':')
                                    hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(
                                        hh_mm_ss[2])
                                if (len(split_time)) == 2:
                                    days = split_time[0]
                                    days_split = days.split('days') or days.split('day')
                                    total_days = int(total_days) + int(days_split[0])
                                    hh_mm_ss = split_time[-1].split(':')
                                    hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(hh_mm_ss[2])
                            if not record.time_spent:
                                now = datetime.now()
                                hr_min_sec = (now - record.check_in)
                                split_time = str(hr_min_sec).split(',')
                                if (len(split_time)) == 1:
                                    hh_mm_ss = split_time[-1].split(':')
                                    hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(
                                        float(hh_mm_ss[2]))
                                if (len(split_time)) == 2:
                                    days = split_time[0]
                                    days_split = days.split('day') or days.split('days')
                                    total_days = int(total_days) + int(days_split[0])
                                    hh_mm_ss = split_time[-1].split(':')
                                    hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(float(hh_mm_ss[2]))
                            if idx == (len(time_spent_records_without_check_out) - 1):
                                tdelta = timedelta(hours=hr, minutes=min, seconds=sec)
                                if str(tdelta).find('day') != -1:
                                    split_days = str(tdelta).split(',')
                                    add_days = str(split_days[0]).split('day')
                                    total_days = str((int(add_days[0]) + int(total_days)))
                                    days_into_hours = int(total_days) * 24
                                    split_hours = str(split_days[-1]).split(':')
                                    tt_hours = split_hours[0]
                                    complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                    time_spent = complete_duration
                                    # time_spent = str(total_days) + ' days ,' + split_days[-1]
                                    user_code = record.user_code
                                    name = record.name.name
                                    function_code = record.function_code
                                    designation = record.designation
                                    state_name = record.state_name
                                    work_location_code = record.work_location_code
                                    cost_type_code = record.cost_type_code
                                    band_code = record.band_code
                                    region = record.region
                                    worksheet.write(a, 0, user_code or '')
                                    worksheet.write(a, 1, name or '')
                                    worksheet.write(a, 2, function_code or '')
                                    worksheet.write(a, 3, designation or '')
                                    worksheet.write(a, 4, state_name or '')
                                    worksheet.write(a, 5, work_location_code or '')
                                    worksheet.write(a, 6, cost_type_code or '')
                                    worksheet.write(a, 7, band_code or '')
                                    worksheet.write(a, 8, str(res_user.region) or '')
                                    worksheet.write(a, 9, no_of_logins or '')
                                    worksheet.write(a, 10, str(time_spent) or '')
                                    a += 1
                                else:
                                    days_into_hours = int(total_days) * 24
                                    split_hours = str(tdelta).split(':')
                                    tt_hours = split_hours[0]
                                    complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[
                                        1] + ':' + split_hours[-1]
                                    time_spent = complete_duration
                                    # time_spent = str(tdelta)
                                    user_code = record.user_code
                                    name = record.name.name
                                    function_code = record.function_code
                                    designation = record.designation
                                    state_name = record.state_name
                                    work_location_code = record.work_location_code
                                    cost_type_code = record.cost_type_code
                                    band_code = record.band_code
                                    region = str(res_user.region)
                                    worksheet.write(a, 0, user_code or '')
                                    worksheet.write(a, 1, name or '')
                                    worksheet.write(a, 2, function_code or '')
                                    worksheet.write(a, 3, designation or '')
                                    worksheet.write(a, 4, state_name or '')
                                    worksheet.write(a, 5, work_location_code or '')
                                    worksheet.write(a, 6, cost_type_code or '')
                                    worksheet.write(a, 7, band_code or '')
                                    worksheet.write(a, 8, region or '')
                                    worksheet.write(a, 9, no_of_logins or '')
                                    worksheet.write(a, 10, str(time_spent) or '')
                                    a += 1
            else:
                res_users = self.env['res.users'].sudo().search(domain)
                for user in res_users:
                    time_spent_records = self.env['time.spent.report'].sudo().search([('name', '=', user.id)])
                    time_spent_records_count = self.env['time.spent.report'].sudo().search_count(
                        [('name', '=', user.id)])
                    no_of_logins = time_spent_records_count
                    time_spent = ''
                    employee_code = ''
                    name = ''
                    function_code = ''
                    designation = ''
                    state_name = ''
                    work_location_code = ''
                    cost_type_code = ''
                    band_code = ''
                    region = ''
                    hr = 0
                    min = 0
                    sec = 0
                    total_days = 0
                    for idx, record in enumerate(time_spent_records):
                        res_user = self.env['res.users'].sudo().search([('id', '=', record.name.id)])
                        days = ''
                        hh_mm_ss = ''
                        if record.time_spent:
                            time_spent = record.time_spent
                            split_time = time_spent.split(',')
                            if (len(split_time)) == 1:
                                hh_mm_ss = split_time[-1].split(':')
                                hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(hh_mm_ss[2])
                            if (len(split_time)) == 2:
                                days = split_time[0]
                                days_split = days.split('day') or days.split('days')
                                total_days = int(total_days) + int(days_split[0])
                                hh_mm_ss = split_time[-1].split(':')
                                hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(hh_mm_ss[2])
                        if not record.time_spent:
                            now = datetime.now()
                            hr_min_sec = (now - record.check_in)
                            split_time = str(hr_min_sec).split(',')
                            if (len(split_time)) == 1:
                                hh_mm_ss = split_time[-1].split(':')
                                hr, min, sec = hr + int(hh_mm_ss[0]), min + int(hh_mm_ss[1]), sec + int(
                                    float(hh_mm_ss[2]))
                            if (len(split_time)) == 2:
                                days = split_time[0]
                                days_split = days.split('day') or days.split('days')
                                total_days = int(total_days) + int(days_split[0])
                                hh_mm_ss = split_time[-1].split(':')
                                hr, min, sec = int(hh_mm_ss[0]), int(hh_mm_ss[1]), int(float(hh_mm_ss[2]))
                        if idx == (len(time_spent_records) - 1):
                            tdelta = timedelta(hours=hr, minutes=min, seconds=sec)
                            if str(tdelta).find('day') != -1:
                                split_days = str(tdelta).split(',')
                                add_days = str(split_days[0]).split('day')
                                total_days = str((int(add_days[0]) + int(total_days)))
                                days_into_hours = int(total_days) * 24
                                split_hours = str(split_days[-1]).split(':')
                                tt_hours = split_hours[0]
                                complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                time_spent = complete_duration
                                # time_spent = str(total_days) + ' days ,' + split_days[-1]
                                user_code = record.user_code
                                name = record.name.name
                                function_code = record.function_code
                                designation = record.designation
                                state_name = record.state_name
                                work_location_code = record.work_location_code
                                cost_type_code = record.cost_type_code
                                band_code = record.band_code
                                region = str(res_user.region)
                                worksheet.write(a, 0, user_code or '')
                                worksheet.write(a, 1, name or '')
                                worksheet.write(a, 2, function_code or '')
                                worksheet.write(a, 3, designation or '')
                                worksheet.write(a, 4, state_name or '')
                                worksheet.write(a, 5, work_location_code or '')
                                worksheet.write(a, 6, cost_type_code or '')
                                worksheet.write(a, 7, band_code or '')
                                worksheet.write(a, 8, region or '')
                                worksheet.write(a, 9, no_of_logins or '')
                                worksheet.write(a, 10, str(time_spent) or '')
                                a += 1
                            else:
                                days_into_hours = int(total_days) * 24
                                split_hours = str(tdelta).split(':')
                                tt_hours = split_hours[0]
                                complete_duration = str(int(tt_hours) + int(days_into_hours)) + ':' + split_hours[1] + ':' + split_hours[-1]
                                time_spent = complete_duration
                                # time_spent = str(tdelta)
                                user_code = record.user_code
                                name = record.name.name
                                function_code = record.function_code
                                designation = record.designation
                                state_name = record.state_name
                                work_location_code = record.work_location_code
                                cost_type_code = record.cost_type_code
                                band_code = record.band_code
                                region = str(res_user.region)
                                worksheet.write(a, 0, user_code or '')
                                worksheet.write(a, 1, name or '')
                                worksheet.write(a, 2, function_code or '')
                                worksheet.write(a, 3, designation or '')
                                worksheet.write(a, 4, state_name or '')
                                worksheet.write(a, 5, work_location_code or '')
                                worksheet.write(a, 6, cost_type_code or '')
                                worksheet.write(a, 7, band_code or '')
                                worksheet.write(a, 8, region or '')
                                worksheet.write(a, 9, no_of_logins or '')
                                worksheet.write(a, 10, str(time_spent) or '')
                                a += 1

        fp = io.BytesIO()
        wb.save(fp)
        out = base64.encodestring(fp.getvalue())
        view_report_status_id = self.env['total.time.spent.view.report'].create(
            {'excel_file': out, 'file_name': filename})
        return {
            'res_id': view_report_status_id.id,
            'name': 'Report',
            'view_mode': 'form',
            'res_model': 'total.time.spent.view.report',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }


class total_time_spent_report(models.TransientModel):
    _name = "total.time.spent.view.report"
    _rec_name = 'excel_file'

    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64)
