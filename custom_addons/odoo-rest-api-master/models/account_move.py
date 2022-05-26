from odoo import fields, models, _, api
import json
from odoo.tools import float_compare, date_utils, email_split, email_re


class AccountMove(models.Model):
    _inherit = 'account.move'

    pando_transaction_id = fields.Many2one('payment.transaction', 'Transaction')

    @api.depends('move_type', 'line_ids.amount_residual')
    def _compute_payments_widget_reconciled_info(self):
        for move in self:
            payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}

            if move.state == 'posted' and move.is_invoice(include_receipts=True):
                payments_widget_vals['content'] = move._get_reconciled_info_JSON_values()

            if payments_widget_vals['content']:
                move.invoice_payments_widget = json.dumps(payments_widget_vals, default=date_utils.json_default)
            else:
                move.invoice_payments_widget = json.dumps(False)
            for transaction in move.transaction_ids:
                if transaction.state == 'done':
                    move.pando_transaction_id = transaction.id

