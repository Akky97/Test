# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Rating(models.Model):
    _inherit = 'rating.rating'

    rating_product_id = fields.Many2one("product.product", string="Product name")
