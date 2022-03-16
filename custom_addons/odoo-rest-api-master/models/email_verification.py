from odoo import fields, models


class emailVerification(models.Model):

    _name = "email.verification"

    email = fields.Char('Email')
    otp = fields.Integer('Send OTP')


class forgotPassword(models.Model):

    _name = "forgot.password"

    email = fields.Char('Email')
    otp = fields.Integer('Send OTP')





