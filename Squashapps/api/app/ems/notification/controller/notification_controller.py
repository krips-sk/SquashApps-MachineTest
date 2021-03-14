import logging

from flask_restplus import Resource
from flask import request

from ..service.notification_service import get_notification_count, get_notification_list, update_notification_status,update_notification_status_byId,get_app_notification_list
from ..util.dto import NotificationDto

api = NotificationDto.api

@api.route('/get_notification_count/<user_id>')
class GetNotificationCount(Resource):
    def get(self,user_id):
        try:
            return get_notification_count(user_id)
        except Exception as e:
            print("get notification count error: " + str(e))
            logging.exception(e)


@api.route('/get_notification_list/<user_id>/<page>/<row>')
class GetNotificationList(Resource):
    def get(self,user_id,page,row):
        try:
            return get_notification_list(user_id,page,row)
        except Exception as e:
            print("get list error: " + str(e))
            logging.exception(e)

@api.route('/update_notification_status/<user_id>')
class UpdateNotificationStatus(Resource):
    def get(self,user_id):
        try:
            return update_notification_status(user_id)
        except Exception as e:
            print("get Update Notification Status error: " + str(e))
            logging.exception(e)

@api.route('/update_notification_status_byId/<user_id>/<notification_id>')
class UpdateNotificationStatusById(Resource):
    def get(self,user_id,notification_id):
        try:
            return update_notification_status_byId(user_id,notification_id)
        except Exception as e:
            print("get Update Notification Status error: " + str(e))
            logging.exception(e)

@api.route('/get_app_notification_list/<user_id>/<page>/<row>')
class GetAppNotificationList(Resource):
    def get(self,user_id,page,row):
        try:
            return get_app_notification_list(user_id,page,row)
        except Exception as e:
            print("get list error: " + str(e))
            logging.exception(e)
