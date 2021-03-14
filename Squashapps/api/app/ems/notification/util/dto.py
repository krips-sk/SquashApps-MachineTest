from flask_restplus import Namespace, fields

class NotificationDto:
   api = Namespace('notification', description='Notification related operations')