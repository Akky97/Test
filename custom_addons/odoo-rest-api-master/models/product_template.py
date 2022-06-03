import datetime

from odoo import api, fields, models, _
from odoo.http import request, route, Controller

from web3 import Web3

w = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/fe062e39f4fa40f581182b1de50ad71e'))

class MarketplaceStock(models.Model):
    _inherit = "marketplace.stock"

    def approve(self):
        res = super(MarketplaceStock, self).approve()
        vals = {
            # "product_id": self.product_id.id,
            "seller_id": self.product_id.marketplace_seller_id.id,
            "approve_by": self.env.user.id,
            "vendor_message": f"""Inventory Request For {self.product_id.name} Is Approved By Admin""",
            "model": "marketplace.stock",
            "title": "Product Inventory"
        }
        self.env['notification.center'].sudo().create(vals)
        return res

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    country_id = fields.Many2one('res.country', string='Country')
    additional_info = fields.Text(string='Additional Information')
    shipping_return = fields.Text(string='Shipping & Returns')
    image_url = fields.Char('Image URL',compute="_get_img_url")
    image_name = fields.Char('Image URL')
    img_attach = fields.Html('Image', compute="_get_img_html")
    img_multi_attach = fields.Html('Image', compute="_get_multi_img_html")

    def reject(self):
        res = super(ProductTemplate, self).reject()
        vals = {
            "seller_id": self.marketplace_seller_id.id,
            "vendor_message": f"""{self.name} is Rejected by Admin.""",
            "model": "product.template",
            "title": "Product"
        }
        self.env['notification.center'].sudo().create(vals)
        return res

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


def payment_validate(transaction_id, order):
    res = False
    transaction = request.env['payment.transaction'].sudo().search([('id', '=', transaction_id)])
    if transaction:
        res = transaction.sudo().write({
            'state': 'done',
            'date': datetime.datetime.now()
        })
        if res:
            res = order.action_confirm()
    return res


def dispatch_order(order):
    stockPicking = request.env['stock.picking'].sudo().search([('sale_id', '=', order.id)])
    for rec in stockPicking:
        stockMoveLine = request.env['stock.move.line'].sudo().search([('picking_id', '=', rec.id)])
        for res in stockMoveLine:
            res.sudo().write({'qty_done': res.product_uom_qty})
        rec.button_validate()


def create_invoice(transaction_id, order):
    res = payment_validate(transaction_id, order)
    result = dispatch_order(order)
    for line in order.order_line:
        line.sudo().write({'shipping_Details': 'ordered'})
    if res:
        invoice = order._create_invoices(final=True)
        if invoice:
            res = invoice.action_post()
            template = request.env.ref('account.email_template_edi_invoice')
            outgoing_server_name = request.env['ir.mail_server'].sudo().search([], limit=1).name
            template.email_from = outgoing_server_name
            template.sudo().send_mail(invoice.id, force_send=True)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    payment_intent = fields.Char('Payment Intent Id')
    payment_data = fields.Char('Payment Data')
    device_name = fields.Text('Device Name')
    from_address = fields.Char('From Address')
    to_address = fields.Char('To Address')
    hash_data = fields.Char('Hash Data')
    mode = fields.Selection([('Stripe', 'Stripe'), ('Meta Mask', 'Meta Mask')], string='Mode Of Payment')

    def meta_mask_confirm_sale_order(self):
        record = self.env['payment.transaction'].sudo().search([('state', '=', 'pending'), ('acquirer_id.name', '=', 'Meta Mask')], order='id desc')
        for rec in record:
            sales = rec.sale_order_ids
            for order in sales:
                if order.state == 'draft' and order.in_process and rec.hash_data:
                    try:
                        txns = w.eth.get_transaction(rec.hash_data)
                        if txns['blockHash'] is not None:
                            data = w.eth.wait_for_transaction_receipt(rec.hash_data)
                            if data['status'] == 1:
                                create_invoice(rec.id, order)
                    except Exception as e:
                        print(e)


class VariantApprovalWizard(models.TransientModel):
    _inherit = 'variant.approval.wizard'

    def approve_selected_variant(self):
        s3_image = request.env['ir.config_parameter'].sudo().search([('key', '=', 'product_image')], limit=1)
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
            'image_url') if 'image_url' in base_image else s3_image.value
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
