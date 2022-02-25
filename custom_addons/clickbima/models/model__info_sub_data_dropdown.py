from odoo import exceptions
from odoo import models, fields, api,_
from odoo.modules.registry import Registry
import odoo
import logging
import json
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class subdata(models.Model):
    _name = 'infosubdatadropdown'

    name = fields.Char()
    info_type =fields.Many2one('infotype.infotype',string="Info Type")
    info_sub_name =fields.Many2one('subdata.subdata',string="Info Sub Data Name")

    @api.multi
    @api.onchange('info_type')
    def _compute_info_name(self):
        res = {}
        infoname = self.info_type.name
        locations = self.env['infodata'].search([('name', '=', infoname)])
        temp = []
        for i in locations:
            temp.append(i.infosubdata.id)
        res['domain'] = ({'info_sub_name': [('id', '=', temp)]})
        return res

    @api.model
    def create(self, vals):
        # print ('VALUES', vals)
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        name = vals.get('name')
        info_types = vals.get('info_type')
        info_sub_names = vals.get('info_sub_name')
        print (name,"@WERTYujik")
        datas = self.env['infosubdatadropdown'].search([('name', '=', name),('info_type','=',info_types),('info_sub_name','=',info_sub_names)])
        if datas:
            raise UserError(_("Info-Sub type Already Exist"))
        else:
            result = super(subdata, self).create(vals)
            return result
        # # datas = self.env['infosubdatadropdown'].search([('name', '=', name)]).name
        # # print (datas,"Dtaa")
        # # if datas:
        # #     raise UserError(_("Info-Sub type Already Exist"))
        # # else:
        # #     return result
        # result_name = result.name
        # print(result_name)
        # with registry.cursor() as cr:
        #     cr.execute("SELECT * FROM infosubdatadropdown  where name='" + str(result_name) + "'")
        #     rows = (cr.dictfetchone())
        #     print (rows)
        #     auth = json.dumps(rows)
        #     all = json.loads(auth)
        #     if all is None:
        #         return result
        #     else:
        #         if all['name'] == result.name:
        #             raise UserError(_("Info Sub-data type Already Exist"))
        #         else:
        #             pass
        # return result