
from odoo.exceptions import ValidationError
from odoo import exceptions
from odoo import models, fields, api,_
from odoo.modules.registry import Registry
import odoo
import logging
import json
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class insurerbranchcompany(models.Model):
    _name = 'insurerbranch'
    _order = 'name asc'
    name = fields.Char(string="Branch",required=True)

    @api.model
    def create(self, vals):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        name = vals.get('name')
        datas = self.env['insurerbranch'].search([('name', '=', name)])
        print(datas, "DATAs")
        result = super(insurerbranchcompany, self).create(vals)
        if datas:
            print("qwertyui")
            raise UserError(_("Branch Name Already Exist"))
        else:
            return result