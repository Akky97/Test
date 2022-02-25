from odoo.exceptions import ValidationError
from odoo import exceptions
from odoo import models, fields, api,_
from odoo.modules.registry import Registry
import odoo
import logging
import json
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class registery(models.Model):
    _name = 'registryentry'

    broker = fields.Many2one('res.company',required=True,string="Broker",default=lambda self: self.env.user.company_id.id)
    location = fields.Many2one('clickbima.clickbima',required=True,string="Location")
    financial = fields.Many2one('fyyear',required=True, default=lambda self: self.env['fyyear'].search([('ex_active', '=',True)],limit=1).id)
    # fy    =     fields.Many2one('fyyear', domain="[('ex_active','=',True)]")
    # register = fields.Many2one('infotype.infotype',string="Register")
    register_name = fields.Many2one('subdata.subdata',string="Register Name",required=True)
    category = fields.Many2many('category.category',required=True)

    @api.multi
    @api.onchange('broker')
    def _compute_register_name(self):
        print("amanmourya")
        res = {}
        locations = self.env['infodata'].search([('name', '=', 57)])
        print(locations, "location")
        temp = []

        for i in locations:
            temp.append(i.infosubdata.name)
        print(temp, "TEM")
        res['domain'] = ({'register_name': [('name', 'in', temp)]})
        print res, "RES"
        return res

    @api.model
    def create(self, vals):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        location = vals.get('location')
        register_name = vals.get('register_name')
        datas = self.env['registryentry'].search([('location', '=', location), ('register_name', '=', register_name)])
        print(datas, "DATAs")
        result = super(registery, self).create(vals)
        if datas:
            print("qwertyui")
            raise UserError(_("Record Already Exist"))
        else:
            return result


    # @api.multi
    # @api.onchange('register')
    # def _compute_info_name(self):
    #     res = {}
    #     infoname = self.register.name
    #     locations = self.env['infodata'].search([('name', '=', infoname)])
    #     temp = []
    #     for i in locations:
    #         temp.append(i.infosubdata.name)
    #     res['domain'] = ({'register_name': [('name', 'in', temp)]})
    #     return res

    
