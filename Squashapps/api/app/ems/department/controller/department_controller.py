# Name: department_controller.py
# Description: This is used to save the department and related operations
# Author: Thirumurthy
# Created: 2021.01.04
# Copyright: © 2020 MYCURA Technologies . All Rights Reserved.
# Change History:
#                 |2021.01.04 save department added

from flask import request, send_file
import logging
from flask_restplus import Resource, marshal_with

from app.cura.user.util.decorator import admin_token_required, token_required
from ..util.dto import DepartmentDto
from app.ems.department.sevice.department_service import save_department, get_department_list, delete_department_data, \
    get_department_details, get_all_department_list

api = DepartmentDto.api
department_save = DepartmentDto.department_save
delete_department = DepartmentDto.delete_department
department_list_resp = DepartmentDto.department_list_resp
department_info_rsp = DepartmentDto.department_info


#
#   feat  Used to save the department.
#
@api.route('/add')
class AddDepartment(Resource):
    @api.response(201, 'department added successfully.')
    @api.expect(department_save, validate=True)
    #@token_required
    @api.doc('department added successfully.')
    def post(self):
        """Add item to department """
        data = request.json
        return save_department(data=data)


#
#   feat  get the list of Company department.
#
@api.route('/get_department_list/<user_id>/<page>/<row>/<searchterm>')
class GetAllDepartment(Resource):
    @api.doc('Get department list')
    #@token_required
    @marshal_with(department_list_resp)
    def get(self, user_id, page, row, searchterm):
        try:
            """get department list"""
            doc_list = get_department_list(user_id, page, row, searchterm)
            if not doc_list:
                api.abort(404)
            else:
                return doc_list
        except Exception as e:
            logging.exception(e)
            return ""


#
#   feat  get the list of Company department.
#
@api.route('/get_all_department')
class GetAllDepartmentList(Resource):
    @api.doc('Get department list')
    #@token_required
    @marshal_with(department_list_resp)
    def get(self):
        try:
            """get department list"""
            doc_list = get_all_department_list()
            if not doc_list:
                api.abort(404)
            else:
                return doc_list
        except Exception as e:
            logging.exception(e)
            return ""


#
#   feat  delete the department information by using id
#
@api.route('/delete')
class DeleteDepartment(Resource):
    @api.response(201, 'department deleted from  Company.')
    #@token_required
    @api.expect(delete_department, validate=True)
    @api.doc('delete department from Company.')
    def post(self):
        """Delete department"""
        data = request.json
        return delete_department_data(data)


#
#   feat  Used to get the department details.
#
@api.route('/get_details/<public_id>')
class GetDepartmentDetails(Resource):
    @api.response(201, 'Used to get the company details.')
    @api.doc('Used to get the company details.')
    @marshal_with(department_info_rsp)
    def get(self, public_id):
        """Used to get the department details."""
        return get_department_details(public_id)
