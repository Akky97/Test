import uuid
from datetime import time

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class TotalTimeSpentReport(models.Model):
    _name = 'time.spent.report'
    _description = 'Total Time Spent Report'


    name = fields.Many2one('res.users','User Name')
    user_code = fields.Char(string='User Code')
    function_code = fields.Char('Function Code')
    designation = fields.Char('Designation')
    state_name = fields.Char('State Name')
    work_location_code = fields.Char('Work Location Code')
    cost_type_code = fields.Char('Cost Type Code')
    band_code = fields.Char('Band Code')
    region = fields.Char('Region')
    number_of_login = fields.Char('No. of Logins')
    time_spent = fields.Char('Time Spent(in hh:mm:ss)',compute='_compute_total_time_spent',store=True)
    logout = fields.Boolean('Logout',default=False)
    check_in = fields.Datetime('Check In')
    check_in_date = fields.Char('Check in date (only date)',compute='_compute_check_in_out_date',store=True)
    check_out_date = fields.Char('Check out date (only date)',compute='_compute_check_in_out_date',store=True)
    check_out = fields.Datetime('Check out')


    @api.depends('check_in','check_out')
    def _compute_check_in_out_date(self):
        for rec in self:
            if rec.check_in:
                rec.check_in_date = rec.check_in.date()
            if rec.check_out:
                rec.check_out_date = rec.check_out.date()




    @api.depends('check_in','check_out')
    def _compute_total_time_spent(self):
        for rec in self:
            if rec.check_out:
                time_spent = rec.check_out - rec.check_in
                time_spent = (str(time_spent)).split('.')
                del time_spent[-1]
                time_spent = ''.join(map(str, (time_spent)))
                rec.time_spent = time_spent
            else:
                rec.time_spent = None