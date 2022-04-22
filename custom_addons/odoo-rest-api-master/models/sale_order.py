from odoo import api, fields, models, _

from odoo.tools.safe_eval import safe_eval
from odoo.tools.sql import column_exists, create_column
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


def next_by_code(self, sequence_code, sequence_date=None, company=False):
    """ Draw an interpolated string using a sequence with the requested code.
        If several sequences with the correct code are available to the user
        (multi-company cases), the one from the user's current company will
        be used.
    """
    self = request.env['ir.sequence']
    self.check_access_rights('read')
    company_id = request.env['res.company'].sudo().search([('name', '=', 'Pando Mall')]).id
    seq_ids = self.search([('code', '=', sequence_code), ('company_id', 'in', [company_id, False])],
                          order='company_id')
    if not seq_ids:
        _logger.debug(
            "No ir.sequence has been found for code '%s'. Please make sure a sequence is set for current company." % sequence_code)
        return False
    seq_id = seq_ids[0]
    return seq_id._next(sequence_date=sequence_date)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_stockable = fields.Boolean("Is a Stockable", compute='_compute_is_stockable', store=True, compute_sudo=True, help="Sales Order item should generate a task and/or a project, depending on the product settings.")

    @api.depends('product_id')
    def _compute_is_stockable(self):
        for so_line in self:
            so_line.is_stockable = so_line.product_id.type == 'product'


class ProjectTaskPando(models.Model):
    _inherit = "project.task"

    sale_line_id_pando = fields.Many2one(
        'sale.order.line', 'Sales Order Item', store=True, readonly=False, copy=False)
    ticket_number = fields.Char(string="Ticket No", readonly=True, required=True, copy=False, default='New')

    def create(self, vals):
        if vals.get('ticket_number', 'New') == 'New':
            # company = request.env['res.company'].sudo().search([('name', '=', '')])
            vals['ticket_number'] = next_by_code(self, 'project.task') or 'New'
        result = super(ProjectTaskPando, self).create(vals)
        return result


