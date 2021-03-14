# Name: audit_log.py
# Description: used for audit log related operation.
# Author: Mycura
# Created: 2020.12.14
# Copyright: © 2020 EMS . All Rights Reserved.
# Change History:
#                |2020.12.14
from flask import request
from flask_restplus import Resource
from app.ems.audit_log.sevice.audit_log_service import save_audit_log, get_by_id, get_audit_log_list, \
    delete_audit_log
from app.ems.audit_log.util.dto import AuditLogdto
from app.cura.user.util.decorator import token_required

api = AuditLogdto.api
_audit_log_save = AuditLogdto.audit_log_save
_delete_audit_log = AuditLogdto.delete_audit_log
_res_audit_log_info = AuditLogdto.res_audit_log_info


#
#   feat - Used to add/update the PDC Registration
#
@api.route('/add')
class AddAuditLog(Resource):
    @api.doc("PDC Registration add")
    @api.expect(_audit_log_save, validate=True)
    @api.response(200, "PDC Registration added successfully")
    # @token_required
    def post(self):
        data = request.json
        return save_audit_log(data)


#
#   feat - Used to get the list of PDC Registration
#
@api.route('/get_list/<page>/<row>/<search>/<int:tabindex>/<int:sortindex>')
class GetAuditLogList(Resource):
    @api.doc("Schedule List")
    # @token_required
    # @api.marshal_with(_res_audit_log_info)
    def get(self, page, row, search, tabindex, sortindex):
        return get_audit_log_list(page, row, search, tabindex, sortindex)


#
#   feat - Used to get the particular PDC Registration using the pdc_registration_id
#
@api.route('/get_by_id/<int:audit_log_id>')
class GetAuditLogById(Resource):
    @api.doc("PDC Registration get by id")
    # @token_required
    @api.marshal_with(_audit_log_save)
    def get(self, audit_log_id):
        return get_by_id(audit_log_id)


#
#   feat - Used to delete the schedule using the schedule id
#
@api.route('/delete')
class DeleteAuditLog(Resource):
    @api.doc("PDC Registration Delete")
    @api.expect(_delete_audit_log, validate=True)
    @token_required
    def post(self):
        data = request.json
        return delete_audit_log(data)