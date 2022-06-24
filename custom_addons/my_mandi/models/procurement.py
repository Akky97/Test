import datetime

from odoo import fields, models, api


class procurementTable(models.Model):
    _name = "procurement.table"
    _description = "Item Sale History"

    procurementTableLine = fields.One2many('procurement.order.line.table', 'procurement_table_id',  string='procurementLine')
    date = fields.Date(string='Date', default=datetime.datetime.now().date())




class procurementOrderLineTable(models.Model):
    _name = "procurement.order.line.table"
    _description = "Item Sale History"

    product_id = fields.Many2one('product.product', string='Product')
    procurement_table_id = fields.Many2one('procurement.table', string='procurementId')
    date = fields.Date(string='Date', default=datetime.datetime.now().date())
    total_amount = fields.Float(string='Total Amount')
    tax_amount = fields.Float(string='Tax Amount')
    sub_total = fields.Float(string='Sub Total')
    note = fields.Text('Note')
    assigned_to = fields.Many2one('res.users')
    product_uom_qty = fields.Float(string='Product Qty')
    unit_price = fields.Float(string='Unit Price')
    qty_update_by_manager = fields.Float(string='Qty Update By Manager')
    procurementExecutiveLine = fields.One2many('procurement.executive', 'polid', string='Procurement Executive Line')


class procurementExecutive(models.Model):
    _name = "procurement.executive"
    _description = "Here We Store procurement executive details"

    polid = fields.Many2one('procurement.order.line.table', string='procurementOrderLineId')
    demand_qty = fields.Float(string='Demand Quantity')
    bought_qty = fields.Float(string=' Bought Quantity')
    grade = fields.Selection([('a', 'Grade A'), ('b', 'Grade B'), ('c', 'Grade C')])
    state = fields.Selection([('draft', 'Draft'),('cancel', 'Cancel'),('confirm', 'Confirm')],required=True, default='draft')
    note = fields.Text('Note')


