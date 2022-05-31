from odoo import api, fields, models, _
from odoo.http import request, route, Controller


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Reapproval functionality
    state = fields.Selection(selection_add=[('reapproval', 'Re-Approval')])
    is_image_remove = fields.Boolean('Is Image Remove')
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
