from odoo import fields, models


class PandoImages(models.Model):

    _name = "pando.images"
    _description = 'Here We Store All The Images'

    image_url = fields.Char('Image URL')
    product_id = fields.Many2one('product.product', string='Product')
    type = fields.Selection([('base_image', 'Base Image'), ('multi_image', 'Multi Image')], string='Image Type')

