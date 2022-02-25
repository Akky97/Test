from odoo import models, fields, api,_
from datetime import datetime,date

from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class policytrans(models.Model):
    _name = 'fyyear'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True,string="Fiscal Year")
    date_start = fields.Date(string='Start date', required=True)
    sequence =  fields.Integer(string="Sequence" )
    date_end = fields.Date(string='End date', required=True)
    ex_active = fields.Boolean(
        help="The active field allows you to hide the date range without "
             "removing it.", default=False,string="Active")
    _sql_constraints = [('date_range_uniq', 'unique (name)','A date range must be unique per company !')]
