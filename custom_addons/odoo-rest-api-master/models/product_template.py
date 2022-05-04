from odoo import api, fields, models, _
from odoo.http import request, route, Controller


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
        for res in self:
            rec = self.env['pando.images'].sudo().search(
                [('product_id.product_tmpl_id', '=', res.id), ('type', '=', 'multi_image')])
            img_attach =''
            for r in rec:
                img_url = r.image_url
                img_attach += '<img src="%s" style="height:100px;width: 100px;padding:10px;"/> ' % img_url
            res.img_multi_attach = img_attach

    def _get_img_url(self):
        for res in self:
            rec = self.env['pando.images'].sudo().search([('product_id.product_tmpl_id','=',res.id),('type','=','base_image')],limit=1)
            res.image_url = rec.image_url
            res.image_name = rec.image_name

    def _get_img_html(self):
        for elem in self:
            img_url = elem.image_url
            if img_url:
                elem.img_attach = '<img src="%s" style="float:right;height:70px;width: 100px;"/>' % img_url
            else:
                elem.img_attach = '<img src="%s" style="float:right;height:70px;width: 100px;"/>' % "https://pandomall.s3.ap-southeast-1.amazonaws.com/1650525013noimage.png"


class ProductProduct(models.Model):
    _inherit = 'product.product'

    sale_count_pando = fields.Float(string='Product Sale Count')
    is_product_publish = fields.Boolean('Product Publish', default=True)
    rating_count = fields.Float('Rating Count')


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    payment_intent = fields.Char('Payment Intent Id')
    payment_data = fields.Char('Payment Data')
    device_name = fields.Text('Device Name')


class VariantApprovalWizard(models.TransientModel):
    _inherit = 'variant.approval.wizard'

    def approve_selected_variant(self):
        product_id = self.product_id
        product_id.sudo().write({"status": "approved", "sale_ok": True})
        product_id.check_state_send_mail()
        uid = request.env.user.id
        result = request.env['pando.images'].sudo().search([('product_id', '=', product_id.id)])
        base_image = {}
        for j in result:
            if j.type == 'base_image':
                base_image = {
                    "id": j.product_id.id,
                    "image_url": j.image_url,
                    'image_name': j.image_name
                }
        img = base_image.get(
            'image_url') if 'image_url' in base_image else "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/330px-No-Image-Placeholder.svg.png?20200912122019"
        vals = {
            "product_id": product_id.id,
            "seller_id": product_id.marketplace_seller_id.id,
            "approve_by": uid,
            "vendor_message": f"""Your product {product_id.name} is approved by Admin""",
            "model": "product.template",
            "title": "Product",
            "image_data": img
        }
        request.env['notification.center'].sudo().create(vals)
        if not product_id.is_initinal_qty_set and len(product_id.product_variant_ids) == 1:
            product_id.set_initial_qty()
        if self.variant_ids:
            self.variant_ids.set_to_approved()
        return True
