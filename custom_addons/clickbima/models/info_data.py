from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class info_data(models.Model):
    _name = 'infodata'
    _order ='name asc'


    # name = fields.Char(string="Info Type Code")
    name = fields.Many2one('infotype.infotype', required=True, string="Info-Type Name")
    infosubdata = fields.Many2one('subdata.subdata', required=True, string="Info-Type-Data Name")

    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id,readonly=True)

    @api.multi
    def write(self,vals):
        if self.env['infotype.infotype'].search([('user_id','=',True),('id','=',self.name.id)]):
            raise ValidationError(_('You are no allowed to perform this action.'))
        else:
            return super(info_data, self).write(vals)

    @api.model
    def create(self,vals):
        if self.env.user.x_typeofcontact == 'superadmin':
            check =self.env['infodata'].search([('name','=',vals.get('name')),('infosubdata','=',vals.get('infosubdata'))])
            if check:
                raise ValidationError(_('Record already Exists'))
        return super(info_data, self).create(vals)
        # else:
        #     name = vals.get('name')
        #     # usertype = self.env.user.x_typeofcontact
        #     # print (usertype, "usertype")
        #     # print (name,"deepak name")
        #     check = self.env['infotype.infotype'].search([('id', '=', name), ('user_id', '=', True)])
        #     print(check, "check>>>>>>>>>>>>")
        #     if check:
        #         raise ValidationError(_('You are no allowed to perform this action.'))
        #     else:
        #         pass
        # return super(info_data, self).create(vals)
    # @api.multi
    # @api.onchange('name')
    # def _compute_info_name(self):
    #     print ('aman11')
    #     res = {}
    #     infoname = self.name.name
    #     locations = self.env['infodata'].search([('name', '=', infoname)])
    #     temp = []
    #     for i in locations:
    #         temp.append(i.infosubdata.name)
    #     res['domain'] = ({'infosubdata': [('name', '=', temp)]})
    #     return res

    # @api.multi
    # def write(self, vals):
    #     if self.env.user.x_typeofcontact == 'superadmin':
    #         return super(infodata, self).write(vals)
    #     else:
    #         raise UserError(_("You are not allowed to change this Record ! Contact to Administator"))
    # @api.onchange('name')
    # def onchange_infotype(self):
    #     aman = self.env['infotype.infotype'].search([('user_id','=',self.user_id.id)])
    #     print ('self',aman)






