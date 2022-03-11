from odoo import api, fields, models, _

class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    popular_category = fields.Boolean('Popular Category')
