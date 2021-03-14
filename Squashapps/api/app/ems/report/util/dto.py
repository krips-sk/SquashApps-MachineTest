from flask_restplus import Namespace, fields

class ReportDto:
   api = Namespace('report', description='Report related operations')