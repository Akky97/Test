# -*- coding: utf-8 -*-

import re
from odoo.exceptions import ValidationError
from odoo import exceptions
from odoo import models, fields, api,_
from odoo.modules.registry import Registry
import odoo
import logging
import json
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class clickbima(models.Model):
    _name = 'clickbima.clickbima'

    # name = fields.Char(string="Code")
    companyname = fields.Many2one('res.company', string="Company Name",required=True)
    name = fields.Char(string="Location Name",required=True)
    shortname = fields.Char(string="Short Name",required=True)
    contactperson = fields.Many2one('res.partner',string="Contact Person",required=True)
    contactno = fields.Char(string="Contact No.",size=10,required=True)
    email = fields.Char(string="Email",required=True)
    address = fields.Text(string="Address",required=True)
    city = fields.Char(required=True)
    state = fields.Many2one('res.country.state', help='Enter State',required=True)
    country = fields.Many2one('res.country', help='Enter Country',required=True)
    pincode = fields.Char(required=True)
    zone = fields.Char(required=True)
    start_active=fields.Boolean(default=False, string='Active')

    @api.onchange('email')
    def validate_mail(self):
        if self.email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
            if match == None:
                raise ValidationError('Please enter a valid email address')

    @api.model
    def create(self, vals):
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        # companyname = vals.get('companyname')
        name = vals.get('name')
        contactperson = vals.get('contactperson')
        datas = self.env['clickbima.clickbima'].search([('name', '=', name), ('contactperson', '=', contactperson)])
        print(datas, "DATAs")
        result = super(clickbima, self).create(vals)
        if datas:
            print("qwertyui")
            raise UserError(_("Record Already Exist"))
        else:
            return result

    # @api.onchange('city')
    # def _onchange_city(self):
    #     self.state =self.city.state_id.name
    #     self.country = self.city.country_id.name
    #     self.zone = self.city.code








