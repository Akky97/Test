from odoo import fields, models


class emailVerification(models.Model):

    _name = "email.verification"

    email = fields.Char('Email')
    send_otp = fields.Char('Send OTP')





