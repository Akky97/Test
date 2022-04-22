from odoo import fields, models


class NotificationCenter(models.Model):
    _name = "notification.center"

    product_id = fields.Many2one('product.product', string='Product')
    seller_id = fields.Many2one("res.partner", string="Seller")
    vendor_message = fields.Text()
    approve_by = fields.Many2one("res.partner", string="Approved By")
    is_read = fields.Boolean("Check is Read", default=True)
    title = fields.Char('Title')
    model = fields.Char('Model Name')





