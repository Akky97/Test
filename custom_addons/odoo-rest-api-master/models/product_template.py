from odoo import api, fields, models, _


#
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    country_id = fields.Many2one('res.country', string='Country')
    additional_info = fields.Text(string='Additional Information')
    shipping_return = fields.Text(string='Shipping & Returns')
