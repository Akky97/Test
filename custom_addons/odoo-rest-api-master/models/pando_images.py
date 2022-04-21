from odoo import fields, models


class PandoImages(models.Model):

    _name = "pando.images"
    _description = 'Here We Store All The Images'

    image_url = fields.Char('Image URL')
    image_name = fields.Char('Image Name')
    product_id = fields.Many2one('product.product', string='Product')
    type = fields.Selection([('base_image', 'Base Image'), ('multi_image', 'Multi Image')], string='Image Type')
    img_attach = fields.Html('Image', compute="_get_img_html")

    def _get_img_html(self):
        for elem in self:
            img_url = self.image_url
            elem.img_attach = '<img src="%s" style="height:200px;width: 200px;"/>' % img_url
