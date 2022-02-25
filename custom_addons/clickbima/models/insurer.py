from odoo.exceptions import ValidationError
from odoo import exceptions
from odoo import models, fields, api,_
from odoo.modules.registry import Registry
import odoo
import logging
import json
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class company1(models.Model):
    _name = 'insurer'
    _order = 'name asc'


    name = fields.Many2one('res.partner',string="Insurer Name",required=True ,domain=[('customer','=',True),('is_company','=',True)])
    type = fields.Selection([('nonlifeinsurance','Non Life Insurance'),('lifeinsurance','Life Insurance')], placeholder="Select Insurer Type",required=True)
    branch = fields.Many2one('insurerbranch', string="Branch",required=True)
    series = fields.Char(string="Series",size=14,required=True)
    attachment =fields.Many2many('ir.attachment',string="Attachment")
    header =fields.Text(string="Header")

    @api.model
    def create(self, vals):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        type = vals.get(' type')
        branch = vals.get(' branch')
        name = vals.get('name')
        series = vals.get(' series')
        datas = self.env['insurer'].search([('name', '=', name), ('type', '=',  type), ('series', '=', series), ('series', '=', series)])
        print(datas, "DATAs")
        result = super(company1, self).create(vals)
        if datas:
            print("qwertyui")
            raise UserError(_("Record Already Exist"))
        else:
            return result

    @api.model
    def create(self, vals):
        name= vals.get('name')
        branch= vals.get('branch')
        obj = self.env['insurer'].search([('name','=',name),('branch', '=',branch)])
        if not obj:
            return super(company1, self).create(vals)
        else:
            raise ValidationError("Its branch already exists")