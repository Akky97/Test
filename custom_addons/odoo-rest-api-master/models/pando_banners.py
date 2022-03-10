from odoo import fields, models


class pandoBanner(models.Model):

    _name = "pando.banner"
    _description = 'Here We Store All The Banners'

    name = fields.Char('Name')
    drop_down = fields.Selection([('home', 'Home'),('banner','Banner')], string='Drop Down')
    image = fields.Binary(attachment=True)





