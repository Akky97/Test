from werkzeug.exceptions import NotFound, Forbidden
from odoo.http import request
from odoo.tools import consteq, plaintext2html
from .exceptions import QueryFormatError
from odoo import http, _, exceptions, fields
from odoo.addons.portal.controllers.mail import PortalChatter
from .error_or_response_parser import *

_logger = logging.getLogger(__name__)


def _check_special_access(res_model, res_id, token='', _hash='', pid=False):
    record = request.env[res_model].browse(res_id).sudo()
    if token:  # Token Case: token is the global one of the document
        token_field = request.env[res_model]._mail_post_token_field
        return (token and record and consteq(record[token_field], token))
    elif _hash and pid:  # Signed Token Case: hash implies token is signed by partner pid
        return consteq(_hash, record._sign_token(pid))
    else:
        raise Forbidden()
def _message_post_helper(res_model, res_id, message, token='', _hash=False, pid=False, nosubscribe=True, **kw):
    """ Generic chatter function, allowing to write on *any* object that inherits mail.thread. We
        distinguish 2 cases:
            1/ If a token is specified, all logged in users will be able to write a message regardless
            of access rights; if the user is the public user, the message will be posted under the name
            of the partner_id of the object (or the public user if there is no partner_id on the object).

            2/ If a signed token is specified (`hash`) and also a partner_id (`pid`), all post message will
            be done under the name of the partner_id (as it is signed). This should be used to avoid leaking
            token to all users.

        Required parameters
        :param string res_model: model name of the object
        :param int res_id: id of the object
        :param string message: content of the message

        Optional keywords arguments:
        :param string token: access token if the object's model uses some kind of public access
                             using tokens (usually a uuid4) to bypass access rules
        :param string hash: signed token by a partner if model uses some token field to bypass access right
                            post messages.
        :param string pid: identifier of the res.partner used to sign the hash
        :param bool nosubscribe: set False if you want the partner to be set as follower of the object when posting (default to True)

        The rest of the kwargs are passed on to message_post()
    """
    record = request.env[res_model].browse(res_id)

    # check if user can post with special token/signed token. The "else" will try to post message with the
    # current user access rights (_mail_post_access use case).
    if token or (_hash and pid):
        pid = int(pid) if pid else False
        if _check_special_access(res_model, res_id, token=token, _hash=_hash, pid=pid):
            record = record.sudo()
        else:
            raise Forbidden()

    # deduce author of message
    author_id = request.env.user.partner_id.id if request.env.user.partner_id else False

    # Token Case: author is document customer (if not logged) or itself even if user has not the access
    if token:
        if request.env.user._is_public():
            # TODO : After adding the pid and sign_token in access_url when send invoice by email, remove this line
            # TODO : Author must be Public User (to rename to 'Anonymous')
            author_id = record.partner_id.id if hasattr(record, 'partner_id') and record.partner_id.id else author_id
        else:
            if not author_id:
                raise NotFound()
    # Signed Token Case: author_id is forced
    elif _hash and pid:
        author_id = pid

    email_from = None
    if author_id and 'email_from' not in kw:
        partner = request.env['res.partner'].sudo().browse(author_id)
        email_from = partner.email_formatted if partner.email else None

    message_post_args = dict(
        body=message,
        message_type=kw.pop('message_type', "comment"),
        subtype_xmlid=kw.pop('subtype_xmlid', "mail.mt_comment"),
        author_id=author_id,
        **kw
    )

    # This is necessary as mail.message checks the presence
    # of the key to compute its default email from
    if email_from:
        message_post_args['email_from'] = email_from

    return record.with_context(mail_create_nosubscribe=nosubscribe).message_post(**message_post_args)

class PortalChatter(PortalChatter):

    @validate_token
    @http.route('/api/v1/c/product.rating', type='http', auth='public', methods=['POST'], csrf=False,
                cors='*')
    def product_rating(self, **params):
        try:
            try:
                jdata = json.loads(request.httprequest.stream.read())
            except:
                jdata = {}
            if jdata:
                if not jdata.get('message') or not jdata.get('product_id') or not jdata.get('rating_value'):
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)

                product_id = request.env['product.product'].sudo().search([('id','=',int(jdata.get('product_id')))])
                if product_id:
                    res_id = product_id.product_tmpl_id.id
                else:
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)
                message = jdata.get('message')
                res_model = 'product.template'
                attachment_ids = []
                attachment_tokens = []
                self._portal_post_check_attachments(attachment_ids, attachment_tokens)
                kw = {
                    'rating_value': jdata.get('rating_value'),
                    'rating_feedback': message
                }
                if message or attachment_ids:
                    # message is received in plaintext and saved in html
                    if message:
                        message = plaintext2html(message)
                    post_values = {
                        'res_model': res_model,
                        'res_id': res_id,
                        'message': message,
                        'send_after_commit': False,
                        'attachment_ids': False,  # will be added afterward
                    }
                    post_values.update((fname, kw.get(fname)) for fname in self._portal_post_filter_params())
                    message = _message_post_helper(**post_values)
                    if message:
                        rating = request.env['rating.rating'].sudo().search([('message_id','=',message.id)], limit=1)
                        if rating:
                            rating.sudo().write({
                                'rating_product_id': product_id.id
                            })
                            res = {
                                'message': 'success',
                                'status': 200
                            }
                            return return_Response(res)
                        else:
                            msg = {"message": "Something Went Wrong.", "status_code": 400}
                            return return_Response_error(msg)
                    else:
                        msg = {"message": "Something Went Wrong.", "status_code": 400}
                        return return_Response_error(msg)
                else:
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)

    @http.route('/api/v1/c/product.rating.display/<id>', type='http', auth='public', methods=['POST'], csrf=False,
                cors='*')
    def product_rating_display(self, id=None, **params):
        try:
            if not id:
                error = {"message": "id is not present in the request", "status": 400}
                return return_Response_error(error)
            rating = request.env['rating.rating'].sudo().search([('rating_product_id','=',int(id))], order='id desc')
            temp = []
            for rec in rating:
                temp.append({
                    'partnerId': rec.partner_id.id,
                    'partnerName': rec.partner_id.name,
                    'rating': rec.rating,
                    'rating_text': rec.rating_text,
                    'feedback': rec.feedback
                })

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
        res = {
            'count': len(temp),
            'ratingList': temp,
            }
        return return_Response(res)
