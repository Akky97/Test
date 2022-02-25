from odoo import models, fields, api


class CountryState(models.Model):
    _description = "Country state"
    _inherit = 'res.country.state'

    region = fields.Selection([('north', 'North'),
                               ('south', 'South'),
                               ('east', 'East'),
                               ('west', 'West'),
                               ('ihq', 'IHQ'),
                               ('central', 'Central'), ], string='Region')
