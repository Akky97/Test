from odoo import fields, models, api


class UploadUsers(models.Model):
    _name = 'upload.users'
    _description = 'Upload or Delete Users'
