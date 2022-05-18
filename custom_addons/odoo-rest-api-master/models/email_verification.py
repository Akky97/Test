from odoo import fields, models


class emailVerification(models.Model):
    _name = "email.verification"
    _description = "Email Verification"

    email = fields.Char('Email')
    otp = fields.Integer('Send OTP')


class forgotPassword(models.Model):
    _name = "forgot.password"
    _description = "Forgot Password"

    email = fields.Char('Email')
    otp = fields.Integer('Send OTP')





