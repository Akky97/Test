from odoo import api, fields, models, _


#
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    country_id = fields.Many2one('res.country', string='Country')
    additional_info = fields.Text(string='Additional Information')
    shipping_return = fields.Text(string='Shipping & Returns')
    image_url = fields.Char('Image URL',compute="_get_img_url")
    image_name = fields.Char('Image URL')
    img_attach = fields.Html('Image', compute="_get_img_html")
    img_multi_attach = fields.Html('Image', compute="_get_multi_img_html")
    def _get_multi_img_html(self):
        rec = self.env['pando.images'].sudo().search(
            [('product_id.product_tmpl_id', '=', self.id), ('type', '=', 'multi_image')])
        img_attach =''
        for r in rec:
            img_url = r.image_url
            img_attach += '<img src="%s" style="height:100px;width: 100px;padding:10px;"/> ' % img_url
        self.img_multi_attach = img_attach

    def _get_img_url(self):
        rec = self.env['pando.images'].sudo().search([('product_id.product_tmpl_id','=',self.id),('type','=','base_image')],limit=1)
        self.image_url = rec.image_url
        self.image_name = rec.image_name

    def _get_img_html(self):
        for elem in self:
            img_url = self.image_url
            elem.img_attach = '<img src="%s" style="float:right !important;height:100px;width: 100px;"/>' % img_url

class ProductProduct(models.Model):
    _inherit = 'product.product'

    sale_count_pando = fields.Float(string='Product Sale Count')


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    payment_intent = fields.Char('Payment Intent Id')
    payment_data = fields.Char('Payment Data')
