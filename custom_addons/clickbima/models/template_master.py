from odoo.exceptions import ValidationError
from odoo import exceptions
from odoo import models, fields, api,_
from odoo.modules.registry import Registry
import odoo
import logging
import json
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class temmaster(models.Model):
    _name = 'tempmaster'

    name = fields.Many2one('res.company',help="Broker Name",required=True, default=lambda self: self.env.user.company_id.id)
    # claimtype = fields.Selection()

    claimtype = fields.Many2one('infotype.infotype',required=True, readonly=True, default=lambda self: self.env['infotype.infotype'].search(
                                   [('name', '=', 'Template Type')]))
    claimtype1 = fields.Many2one('subdata.subdata',required=True, string="Template Type")
    category = fields.Many2one('category.category',required=True)
    subcategory = fields.Many2one('subcategory.subcategory' ,required=True)

    tempremark = fields.One2many('temphead','name',required=True)

    @api.model
    def create(self, vals):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        claimtype1 = vals.get('claimtype1')
        category = vals.get('category')
        subcategory = vals.get('subcategory')
        datas = self.env['tempmaster'].search([('claimtype1', '=', claimtype1), ('category', '=', category), ('subcategory', '=', subcategory)])
        print(datas, "DATAs")
        result = super(temmaster, self).create(vals)
        if datas:
            print("qwertyui")
            raise UserError(_("Record Already Exist"))
        else:
            return result

    @api.multi
    @api.onchange('claimtype')
    def _compute_info_claimtype(self):
        print ('aman')
        res = {}
        infoname = self.claimtype.name
        locations = self.env['infodata'].search([('name', '=', infoname)])
        # print (locations.name)
        temp = []
        for i in locations:
            temp.append(i.infosubdata.name)

        res['domain'] = ({'claimtype1': [('name', '=', temp)]})
        return res

    @api.multi
    @api.onchange('category')
    def _compute_info_cattemp(self):
        res = {}
        temp1 = []
        for i in self.category:
            temp1.append(i.name)
        locations = self.env['subcategory.subcategory'].search([('x_category', '=', temp1)])
        temp = []
        for i in locations:
            temp.append(i.id)
        res['domain'] = ({'subcategory': [('id', 'in', temp)]})
        return res


class remark(models.Model):
    _name = 'temphead'
    _order = "sequence,id"

    name = fields.Integer()
    header = fields.Char()
    sequence = fields.Integer(string="Sequence", widget="handle")
    remark = fields.Char()
