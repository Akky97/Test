# Copyright 2014 ABF OSIELL <http://osiell.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import datetime
import logging

from odoo import SUPERUSER_ID, api, fields, models
from odoo.exceptions import ValidationError

# logger = logging.getLogger(__name_)

class ResUsersRole(models.Model):
    _inherit = "res.users.role"


    group_category_id = fields.Many2one(
        related="group_id.category_id",
        default=lambda cls: cls.env.ref("ecom_lms.ecom_ir_module_category_role").id,
        string="Associated category",
        help="Associated group's category",
        readonly=False,
    )

class ResUsersRoleLine(models.Model):
    _inherit = "res.users.role.line"


    @api.model
    def create(self, vals_list):
        res = super(ResUsersRoleLine, self).create(vals_list)
        res_user_id = self.env['res.users'].browse(vals_list.get('user_id'))
        res_users_role_line = self.env['res.users.role.line'].search([('user_id','=',res_user_id.id),('id','!=',res.id)])
        if res_users_role_line:
            raise ValidationError(f'This User is already added in {res_users_role_line.role_id.name} role.')
        return res