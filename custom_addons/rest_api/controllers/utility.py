import json
import werkzeug


def generateResponse(status_code,response):
    return werkzeug.wrappers.Response(
        status=status_code,
        content_type='application/json; charset=utf-8',
        headers=[('Cache-Control', 'no-store'),
                 ('Pragma', 'no-cache'),
                 ('Strict-Transport-Security','max-age=31536000'),
                 ('X-Content-Type-Options','nosniff'),
                 ('X-XSS-Protection','1; mode=block'),
                 ('Expires','0'),
                 ('X-Frame-Options','deny')],
        response=json.dumps(response))