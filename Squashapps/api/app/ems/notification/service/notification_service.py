import datetime
import logging
from app.cura import db
from app.cura.email.model.email import Notification
from sqlalchemy import desc


def get_notification_count(user_id):

    try:

        notification_count = Notification.query.filter_by(to=user_id, is_web=1, isactive=1,isViewed=0).count()

        response_object = {
            "ErrorCode": "9999",
            "notification_count": notification_count
        }
        return response_object

    except Exception as e:
        logging.exception(e)
        response_object = {
            "ErrorCode": "0000",
            "notification_count": 0
        }
        return response_object

def get_notification_list(user_id,page,row):

    try:
        lst = []
        notification_count = Notification.query.filter_by(to=user_id, is_web=1, isactive=1).count()
        notification_list = Notification.query.filter_by(to=user_id, is_web=1, isactive=1).order_by(desc(Notification.id)).paginate(int(page), int(row), False).items

        if notification_list:

            for list in notification_list:
                notification = {}

                notification['id'] = list.id
                notification['to'] = list.to
                notification['from_user'] = list.from_user
                notification['body'] = list.body
                notification['is_web'] = list.is_web
                notification['isViewed'] = list.isViewed
                notification['notification_type'] = list.notification_type
                notification['table_name'] = list.table_name
                notification['table_detail_id'] = list.table_detail_id
                notification['created_date'] = (list.created_date + datetime.timedelta(hours=8)).strftime('%d-%m-%Y %H:%M:%S')

                lst.append(notification)

        response_object = {
            "ErrorCode": "9999",
            "data": lst,
            "count":notification_count
        }
        return response_object

    except Exception as e:
        logging.exception(e)
        response_object = {
            "ErrorCode": "0000",
            "data": [],
            "count": 0
        }
        return response_object

def get_app_notification_list(user_id, page, row):

    try:
        lst = []
        notification_count = Notification.query.filter_by(to=user_id, is_web=0, isactive=1).count()
        notification_list = Notification.query.filter_by(to=user_id, is_web=0, isactive=1).order_by(
            desc(Notification.id)).paginate(int(page), int(row), False).items

        if notification_list:

            for list in notification_list:
                notification = {}

                notification['id'] = list.id
                notification['to'] = list.to
                notification['from_user'] = list.from_user
                notification['body'] = list.body
                notification['is_web'] = list.is_web
                notification['isViewed'] = list.isViewed
                notification['notification_type'] = list.notification_type
                notification['table_name'] = list.table_name
                notification['table_detail_id'] = list.table_detail_id
                notification['created_date'] = (list.created_date + datetime.timedelta(hours=8)).strftime(
                    '%d-%m-%Y %H:%M:%S')

                lst.append(notification)

        response_object = {
            "ErrorCode": "9999",
            "data": lst,
            "count": notification_count
        }
        return response_object

    except Exception as e:
        logging.exception(e)
        response_object = {
            "ErrorCode": "0000",
            "data": [],
            "count": 0
        }
        return response_object
def update_notification_status(user_id):

    try:

        notification_list = Notification.query.filter_by(to=user_id, is_web=1, isactive=1,isViewed=0).all()

        if notification_list:

            for list in notification_list:
                list.isViewed = 1
                list.updated_by = user_id
                list.updated_date = datetime.datetime.utcnow()
                save_changes(list)


        response_object = {
            "ErrorCode": "9999",
            "message": "Notification Viewed Status Updated Successfully"
        }
        return response_object

    except Exception as e:
        logging.exception(e)
        response_object = {
            "ErrorCode": "0000",
            "message": "Notification Viewed Status Updated Failed"
        }
        return response_object

def update_notification_status_byId(user_id,notification_id):

    try:

        notification = Notification.query.filter_by(id=notification_id,to=user_id, is_web=1, isactive=1).first()

        if notification:
            notification.isViewed = 1
            notification.updated_by = user_id
            notification.updated_date = datetime.datetime.utcnow()
            save_changes(notification)


        response_object = {
            "ErrorCode": "9999",
            "message": "Notification Viewed Status Updated Successfully"
        }
        return response_object

    except Exception as e:
        logging.exception(e)
        response_object = {
            "ErrorCode": "0000",
            "message": "Notification Viewed Status Updated Failed"
        }
        return response_object

def save_changes(data):
    db.session.add(data)
    db.session.commit()