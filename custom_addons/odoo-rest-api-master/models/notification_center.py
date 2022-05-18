from odoo import fields, models


class NotificationCenter(models.Model):
    _name = "notification.center"
    _description = "Notification Center"

    product_id = fields.Many2one('product.template', string='Product')
    seller_id = fields.Many2one("res.partner", string="Seller")
    vendor_message = fields.Text()
    approve_by = fields.Many2one("res.partner", string="Approved By")
    is_read = fields.Boolean("Marked As Read", default=False)
    title = fields.Char('Title')
    model = fields.Char('Model Name')
    image_data = fields.Char('Image Data', store=True)





