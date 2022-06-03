from odoo import api, fields, models, _
from odoo.http import request, route, Controller


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Reapproval functionality
    state = fields.Selection(selection_add=[('reapproval', 'Re-Approval')])
    is_image_remove = fields.Boolean('Is Image Remove', default=True)
    # end

    def approve(self):
        self.ensure_one()
        if self.seller:
            self.state = "approved"
            uid = request.env.user.id
            res_id = request.env['ir.attachment'].sudo()
            res_id = res_id.sudo().search([('res_model', '=', 'res.partner'),
                                           ('res_field', '=', 'image_1920'),
                                           ('res_id', 'in', [self.id])])
            # res_id.sudo().write({"public": True})
            base_url = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')], limit=1)
            img = base_url.value + '/web/image/' + str(res_id.id)
            vals = {"seller_id": self.id,
                    "approve_by": uid,
                    "vendor_message": f"""You are approved by Admin as Seller""",
                    "model": "res.partner",
                    "title": "Seller Approval",
                    "image_data": img
                    }
            request.env['notification.center'].sudo().create(vals)

    def _compute_last_website_so_id(self):
        SaleOrder = self.env['sale.order']
        for partner in self:
            is_public = any(u._is_public() for u in partner.with_context(active_test=False).user_ids)
            website = request.env['website'].sudo().browse(1)
            if website and not is_public:
                partner.last_website_so_id = SaleOrder.search([
                    ('partner_id', '=', partner.id),
                    ('website_id', '=', website.id),
                    ('state', '=', 'draft'),('in_process', '=', False)
                ], order='write_date desc', limit=1)
            else:
                partner.last_website_so_id = SaleOrder  # Not in a website context or public User
