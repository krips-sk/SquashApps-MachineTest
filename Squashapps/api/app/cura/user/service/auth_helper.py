import json

import requests

from app.cura.common.common import get_date_difference
from app.cura.user.model.user import User
import logging

from app.cura.user.service.menuitem_service import get_login_menu
from sqlalchemy import func


class Auth:

    @staticmethod
    def login_user(data):
        try:
            user = User.query.filter(func.lower(User.email)==func.lower(data.get('email')), User.isActive==1).first()
            if user and user.check_password(data.get('password')):
                response_object = {
                    'ErrorCode': '9999',
                    'status': 'success',
                    'message': 'Successfully logged in.',
                    'roles': user.roles,
                    'public_id': user.public_id,
                    'id': user.id,
                    'image_path':user.image_path,
                    'first_name': user.rkp_name,
                    'last_name': "",
                    'rkp_name': user.rkp_name,
                    'login_menu': get_login_menu(user.roles[0], user.id),
                    'license_expiry_date':user.license_expiry_date,
                    'licence_expire': get_date_difference(user.license_expiry_date)
                    # 'passport_expiry_date': user.passport_expiry_date,
                    # 'passport_expire': get_date_difference(user.passport_expiry_date),
                    # 'medical_check_up': user.medical_check_up,
                    # 'medical_expire': get_date_difference(user.medical_check_up)
                }
                return response_object, 200

            else:
                response_object = {
                    'status': 'fail',
                    'message': 'email or password does not match.',
                    'ErrorCode': '9990'
                }
                return response_object, 200

        except Exception as e:
            logging.error(e)
            response_object = {
                'status': 'fail',
                'message': 'Try again',
                'ErrorCode': '9990',
                'Error': str(e)
            }
            return response_object, 200

    @staticmethod
    def logout_user(data):
        if data:
            auth_token = data.split(" ")[1] if len(data.split(" ")) > 2 else data
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                # mark the token as blacklisted
                return save_token(token=auth_token)
            else:
                response_object = {
                    'status': 'fail',
                    'message': resp,
                    'ErrorCode': '9990'
                }
                return response_object, 200
        else:
            response_object = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return response_object, 200

    @staticmethod
    def get_logged_in_user(new_request):
        # get the auth token
        auth_token = new_request.headers.get('Authorization')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                response_object = {
                    'status': 'success',
                    'data': {
                        'user_id': user.id,
                        'email': user.email,
                        'admin': 1 in user.roles,
                        "roles": user.roles,
                        'registered_on': str(user.created_date)
                    }
                }
                return response_object, 200
            response_object = {
                'status': 'fail',
                'message': resp,
                'ErrorCode': '9990'
            }
            return response_object, 200
        else:
            response_object = {
                'status': 'fail',
                'message': 'Provide a valid auth token.',
                'ErrorCode': '9990'
            }
            return response_object, 200
