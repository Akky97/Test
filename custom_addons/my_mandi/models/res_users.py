from odoo import api, fields, models, _


class Users(models.Model):
    _inherit = "res.users"

    area_id = fields.Many2one('user.area', string='User Area')
    user_type = fields.Selection([('sm', 'Sale Manager'), ('se', 'Sale Executive'), ('pm', 'Procurement Manager'), ('pe', 'Procurement Executive'), ('wm', 'Warehouse Manager'), ('oe', 'Operational Executive')], string='User Role')
class areaTable(models.Model):
    _name = "user.area"
    _description = "user area store here"

    area = fields.Char(sting='User Area')





