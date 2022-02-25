from odoo import models, fields, api
import requests
import json
class declaration1(models.Model):
    _name = 'declaration'

    name = fields.Char()

