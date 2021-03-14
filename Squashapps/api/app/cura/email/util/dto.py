from flask_restplus import Namespace, fields


class EmailDto:
    api = Namespace('email', description='user email related operations')
    email = api.model('email', {
        'email': fields.String(required=True, description='user email address'),
        'templatename': fields.String(required=True, description='email templatename'),
    })

    verifylink = api.model('verifylink', {
        'fid': fields.String(required=True, description='fid'),
    })