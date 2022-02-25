from odoo import exceptions
from odoo import models, fields, api,_
from odoo.modules.registry import Registry
import odoo
import logging
import json
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class infosub_data(models.Model):
    _name = 'infosubdata'
    _order = 'name asc'

    # name = fields.Selection([('city''City'),('region','Region'),('state','State'),('test','Test')], string="Info Type")
    name = fields.Many2one('infotype.infotype', string="Info Type",required=True)
    infoname = fields.Many2one('subdata.subdata',string="Info Sub Name",required=True)
    infosub1 = fields.Many2one('infosubdatadropdown',string="Info Sub Data Name",required=True)

    @api.model
    def create(self, vals):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        name = vals.get('name')
        info =vals.get('infoname')
        infosub =vals.get('infosub1')
        datas =self.env['infosubdata'].search([('infoname','=',info),('name','=',name),('infosub1','=',infosub)])
        print(datas,"DATAs")
        result = super(infosub_data, self).create(vals)
        if datas:
            print("qwertyui")
            raise UserError(_("Info-Sub type Already Exist"))
        else:
            return result
        # result_name = result.infosub1.name
        # print(result_name,"Result_name")
        # with registry.cursor() as cr:
        #     cr.execute("SELECT t2.name FROM infosubdata  as t1 "
        #                "left join infosubdatadropdown as t2 on t1.infosub1 =t2.id"
        #                "where t2.name ='" + str(result_name) + "'")
        #     rows = (cr.dictfetchone())
        #     print (rows)
        #     auth = json.dumps(rows)
        #     all = json.loads(auth)
        #     print (all,"ALL")
        #     if all is None:
        #         return result
        #     else:
        #         if all['name'] == result_name:

                # else:
                #     pass
                # return result



    @api.multi
    @api.onchange('infoname')
    def _compute_info_name__11(self):
        print ('infoname inside')
        res = {}
        # current name of the fields
        infosub1 = self.infoname.name
        print (infosub1,"infosub1")
        # current table name
        locations = self.env['infosubdatadropdown'].search([('info_sub_name', '=', infosub1)])
        temp=[]
        print (locations)
        for i in locations:
            temp.append(i.id)
            print(temp,"yishu")
            # name of the dropdown fields
        res['domain']=({'infosub1': [('id', '=', temp)]})
        return res


    @api.multi
    @api.onchange('name')
    def _compute_info_name(self):
        res = {}
        infoname = self.name.name
        locations = self.env['infodata'].search([('name', '=', infoname)])
        temp=[]
        for i in locations:
            temp.append(i.infosubdata.id)
        res['domain']=({'infoname': [('id', '=', temp)]})
        return res



        # if self.name:

    #     infoname= self.name.name
    #     print (infoname)
    #     locations = self.env['infodata'].search([('name', '=', infoname)])
    #     print (locations.infosubdata.id)
    #     print (locations.infosubdata.name)
    #     self.infoname = locations.infosubdata.id
    #     # for i in locations:
        #     print (i)

    #     self.infoname = self.name.infosubdata.id
