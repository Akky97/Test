from odoo import api, fields, models, _


#
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    country_id = fields.Many2one('res.country', string='Country')
    additional_info = fields.Text(string='Additional Information')
    shipping_return = fields.Text(string='Shipping & Returns')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    sale_count_pando = fields.Float(string='Product Sale Count')


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    payment_intent = fields.Char('Payment Intent Id')
    payment_data = fields.Char('Payment Data')
