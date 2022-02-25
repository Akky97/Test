from odoo import models, fields, api
import json
from odoo.modules.registry import Registry
import odoo
import logging

class insurertemp(models.Model):
    _name = 'insurertemplate'


    company_id = fields.Many2one('res.company',required=True, string="Broker Name", help="Broker Name",
                                 default=lambda self: self.env.user.company_id.id)
    claimtype = fields.Many2one('infotype.infotype', readonly=True,
                                default=lambda self: self.env['infotype.infotype'].search(
                                    [('name', '=', 'Template Type')]))
    claimtype1 = fields.Many2one('subdata.subdata',required=True, string="Template Type")
    category = fields.Many2one('category.category',required=True)
    subcategory = fields.Many2many('subcategory.subcategory',required=True)
    # clientname = fields.Many2one('res.partner',required=True, string="Insurer Name", options="{'no_create': True, 'no_create_edit':True}")
    # product = fields.Many2one('scheme',required=True)
    clientname = fields.Many2one('res.partner', string="Name", required=True,
                                     domain=[('customer', '=', True), ('is_company', '=', True)])
    product = fields.Many2one('insurerbranch', string="Branch", required=True)
    searchheader = fields.Char(requied=True,required=True)
    remarksearch = fields.Char(required=True)
    headerdescripe = fields.One2many('availheader','name')

    @api.multi
    @api.onchange('clientname')
    def _compute_info_insurerbranch(self):
        res = {}
        locations = self.env['insurer'].search([('name', '=', self.clientname.id)])
        temp = []
        for i in locations:
            temp.append(i.branch.id)
        res['domain'] = ({'product': [('id', 'in', temp)]})
        return res

    # @api.onchange('clientname')
    # def _onchange_scheme_branch12(self):
    #     """ returns the new values when partner_id has changed """
    #     client12 = self.clientname
    #     print('client', client12.name)
    #     self.product = client12.name

    # @api.multi
    # @api.onchange('clientname')
    # def _compute_info_schemeclient(self):
    #     res = {}
    #     temp1 = []
    #     for i in self.clientname:
    #         temp1.append(i.name)
    #     locations = self.env['scheme'].search([('branch', '=', temp1)])
    #     print (locations,'loc')
    #     temp = []
    #     for i in locations:
    #         temp.append(i.id)
    #     res['domain'] = ({'product': [('id', 'in', temp)]})
    #     return res

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

    def templatesearch(self):
        category = self.category.id
        subcategory = self.subcategory.id
        claimtype1 = self.claimtype1.id

        print(category,subcategory,claimtype1,'catsubtype')
        db_name = odoo.tools.config.get('db_name')
        if not db_name:
            _logger.error(
                "ERROR: To proper setup OAuth2 and Redis - it's necessary to set the parameter 'db_name' in Odoo config file!")
            print(
                "ERROR: To proper setup OAuth2 and Token Store - it's necessary to set the parameter 'db_name' in Odoo config file!")
        else:
            # Read system parameters...
            registry = Registry(db_name)
            with registry.cursor() as cr:

                cr.execute("select t6.header,t6.remark,t1.claimtype1, t2.name as type,t3.name as category,t4.tempmaster_id as subcategory,t1.category as catid, t5.name from tempmaster as t1 left join subdata_subdata as t2 on t1.claimtype1 = t2.id left join category_category as t3 on t1.category = t3.id left join subcategory_subcategory_tempmaster_rel as t4 on t1.id = t4.tempmaster_id left join subcategory_subcategory as t5 on t4.subcategory_subcategory_id = t5.id left join temphead as t6 on t1.id = t6.name where t5.id = '" + str(subcategory) + "' and t3.id = '" + str(category) + "' and t1.claimtype1 = '" + str(claimtype1) + "'")
                data=(cr.dictfetchall())


                temp=[]
                temp2=[]
                for i in data:

                    header1 = i['header']
                    remark = i['remark']
                    temp.append(str(header1))
                    temp2.append(str(remark))
                listToStr1 = ','.join([str(elem) for elem in temp])
                listToStr2 = ','.join([str(elem) for elem in temp2])
                self.searchheader = listToStr1
                self.remarksearch = listToStr2
                header = self.searchheader.split(',')
                mark = self.remarksearch.split(',')
                # cr.execute("insert into headermark (remark) values ('" + mark + "')")
                # print (header,'header')
                # print(remark, 're')
                cr.execute("select name,remark from headermark")
                data = (cr.dictfetchall())
                # print(data,'data')
                temp1=[]
                for j in data:
                    head = j['name']
                    temp1.append(str(head))
                listToStr = ','.join([str(elem) for elem in temp1])
                matchsearchheader = listToStr
                # print(matchsearchheader,'match')
                if matchsearchheader != self.searchheader:
                    for i in range(len(header)):
                        cr.execute("insert into headermark (name,remark) values ('" + header[i] + "','" + mark[i] + "')")

                else:
                    pass










class remark(models.Model):
    _name = 'availheader'

    name = fields.Integer()
    header = fields.Many2one('headermark',options="{'no_create': True, 'no_create_edit':True}")
    remark = fields.Char(options="{'no_create': True, 'no_create_edit':True}")
    detail = fields.Char()
    remark1 = fields.Char()

    @api.onchange('header')
    def _onchange_scheme_header(self):
        """ returns the new values when partner_id has changed """
        head = self.header
        print('head', head.name, head.remark)
        self.remark = head.remark


