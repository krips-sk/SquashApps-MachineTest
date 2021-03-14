from flask import request
from flask_restplus import Resource
import logging

from ..util.dto import EmailDto
from ..service.email_service import sendemail, verify_emaillink

api = EmailDto.api
_email = EmailDto.email
emailverifylink = EmailDto.verifylink


@api.route('/useremail')
class UserEmail(Resource):
    @api.expect(_email, validate=True)
    @api.response(201, 'User email send.')
    @api.doc('create a new email to user')
    def post(self):
        data = request.json
        """List all registered users"""
        return sendemail(data)

@api.route('/verifylink')
class UserEmail(Resource):
    @api.expect(emailverifylink, validate=True)
    @api.response(201, 'This link is Expired')
    @api.doc('create a new email to user')
    def post(self):
        data = request.json
        """List all registered users"""
        return verify_emaillink(data)
