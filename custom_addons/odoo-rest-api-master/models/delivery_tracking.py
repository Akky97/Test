from odoo import fields, models


class deliveryTracking(models.Model):
    _name = "delivery.tracking"
    _description = "Delivery Tracking"

    seller_id = fields.Many2one("res.partner", string="Seller")
    dispatch_date = fields.Datetime(string='Dispatch Date')
    source_address = fields.Many2one('res.partner', string="Source address")
    destination_address = fields.Many2one('res.partner', string="Destination address")
    picking_id = fields.Many2one('stock.picking', 'Picking')
    customer_id = fields.Many2one('res.partner', string="customer")
    order_id = fields.Many2one('sale.order', string='Sale Order')
    deliveryLine = fields.One2many('delivery.address', 'delivery_id', string='Delivery Lines')


class deliveryAddress(models.Model):
    _name = "delivery.address"
    _description = "Delivery Address"

    delivery_id = fields.Many2one('delivery.tracking', string='Sale Order')
    date_time = fields.Datetime(string='Dispatch Date')
    location = fields.Char(string='Office Location')
    event = fields.Selection([('item-bagged', 'Item-Bagged'), ('item-received', 'Item-Received'), ('item-dispatched', 'Item-Dispatched')], string='Event')



