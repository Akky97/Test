from odoo import api, fields, models
import odoo

class message_wizard(models.TransientModel):
    _name = "message.wizard"


    message1 = fields.Text( required=True, readonly=True,translate=True)


    @api.multi
    def action_ok(self):
        return {'type': 'ir.action.act_window_close'}