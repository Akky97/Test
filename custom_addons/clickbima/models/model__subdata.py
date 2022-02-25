# -*- coding: utf-8 -*-
from odoo import exceptions
from odoo import models, fields, api,_
from odoo.modules.registry import Registry
import odoo
import logging
import json
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class subdata(models.Model):
    _name = 'subdata.subdata'

    name = fields.Char()
    # _sql_constraints = [('name', 'unique (name)', "Info Subdata Already Exist")]
    @api.model
    def create(self, vals):
        print ('VALUES', vals)
        db_name = odoo.tools.config.get('db_name')
        registry = Registry(db_name)
        name = vals.get('name')
        print (name)
        result = super(subdata, self).create(vals)
        result_name =result.name
        print(result_name)
        with registry.cursor() as cr:
            cr.execute("SELECT * FROM subdata_subdata  where name='" + str(result_name) + "'")
            rows = (cr.dictfetchone())
            print (rows)
            auth = json.dumps(rows)
            all = json.loads(auth)
            if all is None:
                return result
            else:
                if all['name'] == result.name:
                    raise UserError(_("Info type Already Exist"))
                else:
                    pass
                return result