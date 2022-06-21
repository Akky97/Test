
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    in_process = fields.Boolean(string='In Process', default=False)