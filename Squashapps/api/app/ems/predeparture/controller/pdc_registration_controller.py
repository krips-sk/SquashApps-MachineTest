# Name: pdc_registration_controller.py
# Description: used for PDC Registration Inspection item related operation.
# Author: Mycura
# Created: 2020.12.10
# Copyright: © 2020 EMS . All Rights Reserved.
# Change History:
#                |2020.12.10
from flask import request
from flask_restplus import Resource
from app.ems.predeparture.sevice.pdc_registration_service import add_pdc_registration, get_by_id, get_pdc_list, \
    delete_pdc, save_approval_pdc, get_check_list, get_approval_item, acknowledge_pdc,rkp_login,get_rkp_login_hours
from app.ems.predeparture.util.dto import PDCRegistrationdto
from app.cura.user.util.decorator import token_required

api = PDCRegistrationdto.api
_add_pdc_registration = PDCRegistrationdto.add_pdc_registration
_delete_pdc = PDCRegistrationdto.delete_pdc
_res_pdc_reg_info = PDCRegistrationdto.res_pdc_reg_info
_add_approval_pdc = PDCRegistrationdto.add_approval_pdc
_pdc_ack = PDCRegistrationdto.pdc_ack
_res_check_list = PDCRegistrationdto.res_check_list

_rkp_login=PDCRegistrationdto.rkp_login
#
#   feat - Used to add/update the PDC Registration
#
@api.route('/add_pdc_registration')
class AddPDCRegistration(Resource):
    @api.doc("PDC Registration add")
    @api.expect(_add_pdc_registration, validate=True)
    @api.response(200, "PDC Registration added successfully")
    # @token_required
    def post(self):
        data = request.json
        return add_pdc_registration(data)


#
#   feat - Used to get the list of PDC Registration
#
@api.route('/get_list/<approval_status>/<page>/<row>/<search>/<int:tabindex>/<int:sortindex>/<int:inspection_type>')
class GetPDCRegistrationList(Resource):
    @api.doc("Schedule List")
    # @token_required
    def get(self, approval_status, page, row, search, tabindex, sortindex, inspection_type):
        return get_pdc_list(int(approval_status), page, row, search, tabindex, sortindex, inspection_type)


#
#   feat - Used to get the particular PDC Registration using the pdc_registration_id
#
@api.route('/get_by_id/<int:pdc_registration_id>')
class GetPDCRegistrationById(Resource):
    @api.doc("PDC Registration get by id")
    # @token_required
    # @api.marshal_with(_add_pdc_registration)
    def get(self, pdc_registration_id):
        return get_by_id(pdc_registration_id)


#
#   feat - Used to delete the schedule using the schedule id
#
@api.route('/delete')
class DeletePDCRegistration(Resource):
    @api.doc("PDC Registration Delete")
    @api.expect(_delete_pdc, validate=True)
    @token_required
    def post(self):
        data = request.json
        return delete_pdc(data)


#
#   feat - Used to delete the schedule using the schedule id
#
@api.route('/acknowledge')
class AckPDCRegistration(Resource):
    @api.doc("PDC Registration Delete")
    @api.expect(_pdc_ack, validate=True)
    # @token_required
    def post(self):
        data = request.json
        return acknowledge_pdc(data)


#
#   feat - Used to add/update the PDC Approval or reject changes
#
@api.route('/update_approval')
class UpdatePDCApproval(Resource):
    @api.doc("PDC Approval status update")
    @api.expect(_add_approval_pdc, validate=True)
    @api.response(200, "PDC approval updated successfully")
    # @token_required
    def post(self):
        data = request.json
        return save_approval_pdc(data)


#
#   feat - Used to get the check list of the PDC item
#
@api.route('/get_check_list/<int:sub_module>/<int:schedule_id>')
class GetPDCRegistrationById(Resource):
    @api.doc("PDC get all check list")
    # @token_required
    @api.marshal_with(_res_check_list)
    def get(self, sub_module, schedule_id):
        return get_check_list(sub_module, schedule_id)


#
#   feat - Used to get the approval items using the pdc_registration_id
#
@api.route('/get_approval_item/<int:pdc_registration_id>')
class GetPDCApprovalItemById(Resource):
    @api.doc("PDC Registration get by id")
    # @token_required
    def get(self, pdc_registration_id):
        return get_approval_item(pdc_registration_id)

@api.route('/rkp_login')
class RKPLogin(Resource):
    @api.doc("PDC Approval sta tus update")
    @api.expect(_rkp_login, validate=True)
    @api.response(200, "PDC approval updated successfully")
    # @token_required
    def post(self):
        data = request.json
        return rkp_login(data)

@api.route('/get_rkp_login_hours/<int:user_id>')
class GetRKPLoginHours(Resource):
    @api.doc("Get RKP login hours")
    # @token_required
    def get(self, user_id):
        return get_rkp_login_hours(user_id)
