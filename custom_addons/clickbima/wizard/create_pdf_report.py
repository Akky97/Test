from odoo import api, fields, models, _
import odoo
from odoo.tools.misc import xlwt
from odoo.exceptions import UserError, AccessError
import io
import base64
import operator
import itertools
import time
from datetime import date
from odoo.modules.registry import Registry
from datetime import timedelta


class Policypdfreport(models.TransientModel):
    _name = "report.pdf"
    _description = "Policy Transaction Report"

    start_date = fields.Date(string="Date")

    @api.multi
    def test_report1(self):
        # print('data:',self.read()[0])
        datas = {
            'model': 'report.pdf',
            'form': self.read()[0]
        }
        return self.env.ref('clickbima.non_life_insurerwise_report').report_action(self ,data=datas)


