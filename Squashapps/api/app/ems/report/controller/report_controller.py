import logging

from flask_restplus import Resource
from ..util.dto import ReportDto
from ..service.report_service import leavesummary,workhoursummary,summary_report_download,get_report_list,get_file,get_report_status

api = ReportDto.api


@api.route('/leavesummary/<month>/<year>/<page>/<row>')
class LeaveSummary(Resource):
    @api.response(201, 'Get User Leave Summary Info Information')
    @api.doc('Get User Leave Summary Info Information')
    def get(self,month,year,page,row):
        try:
            return leavesummary(month,year,page,row)
        except Exception as e:
            logging.exception(e)

@api.route('/workhoursummary/<month>/<year>/<page>/<row>')
class WorkHourSummary(Resource):
    @api.response(201, 'Get Work Hour Summary Info Information')
    @api.doc('Get Work Hour Summary Info Information')
    def get(self,month,year,page,row):
        try:
            return workhoursummary(month,year,page,row)
        except Exception as e:
            logging.exception(e)

@api.route('/download/<month>/<year>/<type>/<userid>')
class WorkHourSummaryReport(Resource):
    @api.response(201, 'Get Work Hour Summary Report Info Information')
    @api.doc('Get Work Hour SummaryR eport Info Information')
    def get(self,month,year,type,userid):
        try:
            return summary_report_download(month,year,type,userid)
        except Exception as e:
            logging.exception(e)

@api.route('/get_report_list/<page>/<row>/<type>')
class GetReportList(Resource):
    @api.response(201, 'Get Report List Info Information')
    @api.doc('Get Report List Info Information')
    def get(self,page,row,type):
        try:
            return get_report_list(page,row,type)
        except Exception as e:
            logging.exception(e)

@api.route('/get_report_status/<report_id>')
class GetReportStatus(Resource):
    @api.response(201, 'Get Report Status Information')
    @api.doc('Get Report Status Information')
    def get(self,report_id):
        try:
            return get_report_status(report_id)
        except Exception as e:
            logging.exception(e)

@api.route('/get_file/<public_id>')
class GetFile(Resource):
    @api.response(201, 'Get File Information')
    @api.doc('Get File Information')
    def get(self,public_id):
        try:
            return get_file(public_id)
        except Exception as e:
            logging.exception(e)
