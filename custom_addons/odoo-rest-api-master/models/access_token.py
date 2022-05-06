import os
import hashlib
import logging

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

expires_in = 'odoo-rest-api-master.access_token_expires_in'


def nonce(length=40, prefix='access_token'):
    rbytes = os.urandom(length)
    return '{}_{}'.format(prefix, str(hashlib.sha1(rbytes).hexdigest()))


class APIAccessToken(models.Model):
    _name = 'api.access_token'

    token = fields.Char('Access Token', required=True)
    user_id = fields.Many2one('res.users', string='User', required=True)
    expires = fields.Datetime('Expires', required=True)
    scope = fields.Char('Scope')


    def find_one_or_create_token(self, user_id=None, create=False):
        if not user_id:
            user_id = self.env.user.id

        access_token = self.env['api.access_token'].sudo().search(
            [('user_id', '=', user_id)], order='id DESC', limit=1)
        if access_token:
            access_token = access_token[0]
            if access_token.has_expired():
                access_token = None
        if not access_token and create:
            expires = datetime.now() + \
                timedelta(seconds=int(self.env.ref(expires_in).sudo().value))
            vals = {
                'user_id': user_id,
                'scope': 'userinfo',
                'expires': expires.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'token': nonce(),
            }
            access_token = self.env['api.access_token'].sudo().create(vals)
            self._cr.commit()
        if not access_token:
            return None
        return access_token.token


    def is_valid(self, scopes=None):
        """
        Checks if the access token is valid.
        :param scopes: An iterable containing the scopes to check or None
        """
        self.ensure_one()
        return not self.has_expired() and self._allow_scopes(scopes)


    def has_expired(self):
        self.ensure_one()
        return datetime.now() > fields.Datetime.from_string(self.expires)


    def _allow_scopes(self, scopes):
        self.ensure_one()
        if not scopes:
            return True

        provided_scopes = set(self.scope.split())
        resource_scopes = set(scopes)

        return resource_scopes.issubset(provided_scopes)


class Users(models.Model):
    _inherit = 'res.users'
    token_ids = fields.One2many('api.access_token', 'user_id',
                                string="Access Tokens")

    gst_number = fields.Char(string="GST Number")
    account_name = fields.Char(string="Account Name")
    account_number = fields.Char(string="Account Number")
    ifsc_code = fields.Char(string="IFSC CODE")
    user_type = fields.Selection([('customer', 'Customer'),
                                     ('vendor', 'Vendor')])
    owner_name = fields.Char(string="Owner name")
    business_name = fields.Char(string="Business name")
    supplier_country_id = fields.Many2one('res.country', string="Country")
    supplier_address = fields.Char('Street Address')
    supplier_city = fields.Char('City')
    supplier_state_id = fields.Many2one('res.country.state', 'State')
    supplier_phone = fields.Char(string="Phone")
    pickup_address_line = fields.One2many('pickup.address', 'user_id', string='Pickup Address Lines')
    deviceToken = fields.Char('Device Token')

class PickupAddress(models.Model):
    _name = 'pickup.address'

    user_id = fields.Many2one('res.users', string='User Reference')
    country_id = fields.Many2one('res.country', string="Country")
    address = fields.Char('Street Address')
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', 'State')
    zip = fields.Char('ZIP')
