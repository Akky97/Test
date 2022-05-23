from odoo import api, fields, models, _
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


class ReturnOrder(models.Model):
    _name = "return.policy"
    _description = "Return Policy"

    product_id = fields.Many2one('product.product', string='Product')
    order_id = fields.Many2one('sale.order', string='Sale Order')
    order_line = fields.Many2one('sale.order.line', string='Sale Order Line')
    seller_id = fields.Many2one("res.partner", string="Seller")
    partner_id = fields.Many2one("res.partner", string="Customer")
    reason = fields.Text(String="Reason")
    payment_info = fields.Text(String="Payment Intent")
    payment_intent = fields.Char(String="Payment Data")
    state = fields.Selection([('draft', 'Draft'), ('picked', 'Picked'), ('in-stock', 'In-Stock'),
                                             ('refund', 'Refund'), ('cancel', 'Cancel')], string='Return Status', default='draft')
    product_uom_qty = fields.Integer(string='Product Qty')

    def cancel(self):
        self.ensure_one()
        if self.state:
            self.state = 'cancel'
            self.order_line.return_state = 'cancel'

    def confirm(self):
        self.ensure_one()
        if self.state:
            self.state = 'picked'
            self.order_line.return_state = 'picked'

    def update_stock(self):
        self.ensure_one()
        if self.state:
            self.state = 'in-stock'
            self.order_line.return_state = 'in-stock'
            location_id = self.order_id.warehouse_id.lot_stock_id.id
            stockQuant = self.env['stock.quant'].sudo().search([('product_id', '=', self.product_id.id), ('location_id', '=', location_id)])
            for rec in stockQuant:
                rec.sudo().write({
                    'quantity': rec.quantity + self.product_uom_qty
                })
            self.order_line.sudo().write({
                'return_qty': self.product_uom_qty
            })

    def refund(self):
        self.ensure_one()
        if self.state:
            self.state = 'refund'
            self.order_line.is_return = True
            self.order_line.return_state = 'refund'

    @api.onchange('order_line')
    def update_data(self):
        if self.order_line:
            self.order_id = self.order_line.order_id.id
            self.product_id = self.order_line.product_id.id
            self.seller_id = self.order_line.product_id.marketplace_seller_id.id
            self.partner_id = self.order_line.order_id.partner_id.id


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_stockable = fields.Boolean("Is a Stockable", compute='_compute_is_stockable',
                                  store=True, compute_sudo=True,
                                  help="Sales Order item should generate a task and/or a project, depending "
                                       "on the product settings.")
    shipping_Details = fields.Selection([('draft', 'Draft'), ('ordered', 'Ordered'), ('in_transit', 'In-Transit'),
                                         ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancel', 'Cancel')],
                                        string='Shipping Status')
    return_state = fields.Selection([('draft', 'Draft'), ('picked', 'Picked'), ('in-stock', 'In-Stock'),
                                     ('refund', 'Refund'), ('cancel', 'Cancel')], string='Return Status')

    return_qty = fields.Integer(string='Return Qty')
    is_return = fields.Boolean(string="Is Return", default=False)

    @api.depends('product_id')
    def _compute_is_stockable(self):
        for so_line in self:
            so_line.is_stockable = so_line.product_id.type == 'product'


class ProjectTaskPando(models.Model):
    _inherit = "project.task"

    sale_line_id_pando = fields.Many2one(
        'sale.order.line', 'Sales Order Item', store=True, readonly=False, copy=False)
    ticket_number = fields.Char(string="Ticket No", readonly=True, required=True, copy=False, default='New')
    product_id = fields.Many2one(
        'product.product', 'Product', store=True, readonly=False, copy=False)
    user_type = fields.Selection([('vendor', 'Vendor'), ('customer', 'Customer')], string='User type')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ticket_number', 'New') == 'New':
                vals['ticket_number'] = next_by_code(self, 'project.task') or 'New'
        result = super(ProjectTaskPando, self).create(vals_list)
        return result


