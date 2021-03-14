# Name: branch_controller.py
# Description: This is used to save the Branch and related operations
# Author: Thirumurthy
# Created: 2020.12.23
# Copyright: © 2020 MYCURA Technologies . All Rights Reserved.
# Change History:
#                 |2020.12.23 save Branch added

from flask import request, send_file
import logging
from flask_restplus import Resource, marshal_with

from app.cura.user.util.decorator import admin_token_required, token_required
from ..util.dto import BranchDto
from app.ems.branch.sevice.branch_service import save_branch, get_branchlist, delete_branchdata, \
    get_branch_details, get_allbranchlist

api = BranchDto.api
branch_save = BranchDto.branch_save
delete_branch = BranchDto.delete_branch
branch_list_resp = BranchDto.branch_list_resp
branch_info_rsp = BranchDto.branch_info


#
#   feat  Used to save the branch.
#
@api.route('/add')
class AddBranch(Resource):
    @api.response(201, 'branch added successfully.')
    @api.expect(branch_save, validate=True)
    #@token_required
    @api.doc('branch added successfully.')
    def post(self):
        """Add item to branch """
        data = request.json
        return save_branch(data=data)


#
#   feat  get the list of Company branch.
#
@api.route('/get_branch_list/<user_id>/<page>/<row>/<searchterm>')
class GetAllBranch(Resource):
    @api.doc('Get branch list')
    #@token_required
    @marshal_with(branch_list_resp)
    def get(self, user_id, page, row, searchterm):
        try:
            """get branch list"""
            doc_list = get_branchlist(user_id, page, row, searchterm)
            if not doc_list:
                api.abort(404)
            else:
                return doc_list
        except Exception as e:
            logging.exception(e)
            return ""


#
#   feat  get the list of Company branch.
#
@api.route('/get_all_branch')
class GetAllBranchList(Resource):
    @api.doc('Get branch list')
    #@token_required
    @marshal_with(branch_list_resp)
    def get(self):
        try:
            """get branch list"""
            doc_list = get_allbranchlist()
            if not doc_list:
                api.abort(404)
            else:
                return doc_list
        except Exception as e:
            logging.exception(e)
            return ""


#
#   feat  delete the branch information by using id
#
@api.route('/delete')
class DeleteBranch(Resource):
    @api.response(201, 'branch deleted from  Company.')
    #@token_required
    @api.expect(delete_branch, validate=True)
    @api.doc('delete branch from Company.')
    def post(self):
        """Delete branch"""
        data = request.json
        return delete_branchdata(data)


#
#   feat  Used to get the branch details.
#
@api.route('/get_details/<public_id>')
class GetBranchDetails(Resource):
    @api.response(201, 'Used to get the company details.')
    @api.doc('Used to get the company details.')
    @marshal_with(branch_info_rsp)
    def get(self, public_id):
        """Used to get the branch details."""
        return get_branch_details(public_id)
