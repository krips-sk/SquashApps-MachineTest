# Name: workshop_controller.py
# Description: used for workshop related operation.
# Author: Mycura
# Created: 2020.12.16
# Copyright: © 2020 EMS . All Rights Reserved.
# Change History:
#                |2020.12.16
import logging

from flask import request
from flask_restplus import Resource
from ...workshop.sevice.workshop_service import save_adhoc, get_by_id, get_adhoc_list, \
    delete_adhoc, save_schedule_maintenance, get_dashboard_daily_downtime, get_pdc_defects_list, repair_status_save, \
    get_repair_status_by_headId, update_pdc_defects, upload_excel, get_report_status, get_parts_report, \
    get_parts_report_summary, get_dashboard_count, get_expense_report, total_defect_category, total_repair_count, \
    get_purchase_report, get_corrective_action_report,get_pdc_defects_by_id, get_workshop_parts_action_list, saveWorkShopActions
from app.ems.workshop.util.dto import Wrokshopdto
from app.cura.user.util.decorator import token_required

api = Wrokshopdto.api
_add_adhoc = Wrokshopdto.add_adhoc
_add_schedule_maintenance = Wrokshopdto.add_schedule_maintenance
_delete_adhoc = Wrokshopdto.delete_adhoc
_res_adhoc_info = Wrokshopdto.res_adhoc_info
_repair_status_save = Wrokshopdto.repair_status_save
_update_pdc_defects = Wrokshopdto.update_pdc_defects
_job_excel_upload = Wrokshopdto.job_excel_upload
_corrective_report_filter = Wrokshopdto.corrective_report_filter
_parts_list = Wrokshopdto.workshop_part_list
_action_list = Wrokshopdto.workshop_action_list
_getlist_workaction = Wrokshopdto.getlist_workaction
_save_workaction = Wrokshopdto.save_workaction

#
#   feat - Used to add/update the adhoc
#
@api.route('/adhoc/add')
class AddAdhoc(Resource):
    @api.doc("PDC Registration add")
    @api.expect(_add_adhoc, validate=True)
    @api.response(200, "PDC Registration added successfully")
    # @token_required
    def post(self):
        data = request.json
        return save_adhoc(data)


#
#   feat - Used to add/update the Schedule Maintenance
#
@api.route('/schedule_maintenance/add')
class AddScheduleMaintenance(Resource):
    @api.doc("Schedule maintenance add")
    @api.expect(_add_schedule_maintenance, validate=True)
    @api.response(200, "Schedule Maintenance added successfully")
    # @token_required
    def post(self):
        data = request.json
        return save_schedule_maintenance(data)


#
#   feat - Used to get the list of adhoc
#
@api.route('/get_list/<page>/<row>/<search>/<int:tabindex>/<int:sortindex>')
class GetAdhocList(Resource):
    @api.doc("Schedule List")
    # @token_required
    @api.marshal_with(_res_adhoc_info)
    def get(self, page, row, search, tabindex, sortindex):
        return get_adhoc_list(page, row, search, tabindex, sortindex)


#
#   feat - Used to get the particular adhoc using the adhoc_breakdown_id
#
@api.route('/get_by_id/<int:adhoc_breakdown_id>')
class GetAdhocById(Resource):
    @api.doc("PDC Registration get by id")
    # @token_required
    @api.marshal_with(_add_adhoc)
    def get(self, adhoc_breakdown_id):
        return get_by_id(adhoc_breakdown_id)


#
#   feat - Used to delete the adhoc using the adhoc id
#
@api.route('/delete')
class DeleteAdhoc(Resource):
    @api.doc("PDC Registration Delete")
    @api.expect(_delete_adhoc, validate=True)
    # @token_required
    def post(self):
        data = request.json
        return delete_adhoc(data)


#
#   feat - Used to get the daily dashboard downtime
#
@api.route('/get_dashboard_daily_downtime/<page>/<row>/<date_in>/<date_out>/<search>')
class GetDashboardDowntime(Resource):
    @api.doc("Dashboard downtime get details")
    # @token_required
    def get(self,page,row,date_in,date_out,search):
        return get_dashboard_daily_downtime(page,row,date_in,date_out,search)


@api.route('/get_pdc_defects/<page>/<row>/<search>/<date_in_search>/<date_out_search>/<int:reference_id>')
class GetPDCDefectsList(Resource):
    @api.doc("Dashboard downtime get details")
    # @token_required
    def get(self, page, row, search, date_in_search, date_out_search, reference_id):
        return get_pdc_defects_list(page, row, search, date_in_search, date_out_search, reference_id)


@api.route('/get_pdc_defects_by_id/<id>')
class GetPDCDefectsById(Resource):
    @api.doc("Dashboard downtime get details")
    # @token_required
    def get(self, id):
        return get_pdc_defects_by_id(id)


@api.route('/update_pdc_defects')
class UpdatePDCDefects(Resource):
    @api.doc("PDC Registration add")
    @api.expect(_update_pdc_defects, validate=True)
    @api.response(200, "Repair Status added successfully")
    # @token_required
    def post(self):
        data = request.json
        return update_pdc_defects(data)


@api.route('/repair_status_save')
class RepairStatusSave(Resource):
    @api.doc("PDC Registration add")
    @api.expect(_repair_status_save, validate=True)
    @api.response(200, "Repair Status added successfully")
    # @token_required
    def post(self):
        data = request.json
        return repair_status_save(data)


@api.route('/get_repair_status/<head_id>')
class GetRepairStatuse(Resource):
    @api.doc("Dashboard downtime get details")
    # @token_required
    def get(self, head_id):
        return get_repair_status_by_headId(head_id)


@api.route('/report/job_excel_upload')
class UploadReportFile(Resource):
    @api.doc("PDC Registration add")
    @api.expect(_job_excel_upload, validate=True)
    @api.response(200, "Repair Status added successfully")
    # @token_required
    def post(self):
        try:
            file = request.files['file']
            file_date = request.args.get("date")
            user_id = request.args.get("user_id")
            report_type = int(request.args.get("report_type"))
            file_res = upload_excel(file, file_date, user_id, report_type)
            if not file_res:
                api.abort(404)
            else:
                return file_res
        except request.exceptions.HTTPError as e:
            logging.exception(str(e))


#
#   Get Status of Report
#
@api.route('/report/get_status/<report_date>/<user_id>/<report_type>')
class GetReportStatus(Resource):
    @api.doc("Get Boss Report data")
    # @token_required
    def get(self, report_date, user_id, report_type):
        return get_report_status(report_type, report_date, user_id)


#
#   Get Branch Parts report
#
@api.route('/report/get_parts_report/<report_date>/<user_id>')
class GetBranchPartsReport(Resource):
    @api.doc("Get Boss Report data")
    # @token_required
    def get(self, report_date, user_id):
        return get_parts_report(user_id, report_date)


#
#   Get Branch Parts report - Summary
#
@api.route('/report/get_parts_report_summary/<report_year>/<user_id>')
class GetBranchPartsReportSummary(Resource):
    @api.doc("Get Boss Report data")
    # @token_required
    def get(self, report_year, user_id):
        return get_parts_report_summary(user_id, report_year)


#
#   Get Supplier purchase listing report
#
@api.route('/report/get_purchase_listing_report/<report_date>/<user_id>')
class GetSupplierPurchaseReport(Resource):
    @api.doc("Get Boss Report data")
    # @token_required
    def get(self, report_date, user_id):
        return get_purchase_report(user_id, report_date)


#
#   Get Branch Parts report - Summary
#
@api.route('/report/get_expense_report/<report_date>/<user_id>')
class GetExpenseReport(Resource):
    @api.doc("Get Boss Report data")
    # @token_required
    def get(self, report_date, user_id):
        return get_expense_report(user_id, report_date)


#
#   Get Dashboard Count Information
#

@api.route('/total_defect_category/<date_in>/<date_out>/<search>')
class TotalDefectCategory(Resource):
    @api.doc("Get Boss Report data")
    # @token_required
    def get(self, date_in, date_out, search):
        return total_defect_category(date_in, date_out, search)

@api.route('/total_repair_count/<date_in>/<date_out>/<search>')
class TotalRepairCount(Resource):
    @api.doc("Get Total Repair Count data")
    # @token_required
    def get(self, date_in, date_out, search):
        return total_repair_count(date_in, date_out, search)


#
#   Get Branch Parts report
#
@api.route('/report/get_corrective_report/<report_date>/<user_id>')
class GetCorrectiveActionReport(Resource):
    @api.doc("Get Boss Report data")
    # @token_required
    @api.expect(_corrective_report_filter, validate=True)
    def post(self):
        data = request.json
        return get_corrective_action_report(data)

#
#   Get Workshop Parts List
#
@api.route('/workaction/get_list/<int:rt_regn>')
class GetWorkActionPartsList(Resource):
    @api.doc("Get Work Action Parts List")
    # @token_required
    @api.marshal_with(_getlist_workaction)
    def get(self, rt_regn):
        return get_workshop_parts_action_list(rt_regn)

@api.route('/workaction/save_workactions')
class saveAllWorkshopActions(Resource):
    @api.doc("Save all workshop actions")
    @api.expect(_save_workaction, validate=True)
    @api.response(200, "Workshop Work Actions Save")
    # @token_required
    def post(self):
        data = request.json
        return saveWorkShopActions(data)