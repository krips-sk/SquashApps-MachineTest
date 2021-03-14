# Name: claim_controller.py
# Description: This is used to claim  save and get related operations
# Author: AJITH T
# Created: 2021.02.16
# Copyright: © 2020 MYCURA Technologies . All Rights Reserved.
# Change History:
#                 |2021.02.16 claim new added

from flask import request, send_file
import logging
from flask_restplus import Resource, marshal_with
from werkzeug.datastructures import FileStorage

from app.cura.user.util.decorator import admin_token_required, token_required
from ..util.dto import ClaimDto
from ..sevice.claim_service import save_claim,get_claim_list,DocumentUpload,get_claim_details,download_doc\
    ,get_claim_type_count,get_dashboard_list

api = ClaimDto.api
claim_new = ClaimDto.claim_new

upload_parser = api.parser()
upload_parser.add_argument('file', location='files',type=FileStorage, required=True)
@api.route('/documentUpload')
class documentUpload(Resource):
    @api.expect(upload_parser, validate=True)
    @api.response(201, 'file_uploaded successfully')
    @api.doc('file_upload details')
    def post(self):
        try:
            file = request.files['file']
            files = DocumentUpload(file)
            if not files:
                api.abort(404)
            else:
                return files
        except request.exceptions.HTTPError as e:
            print(200)
            logging.exception(str(e))
            print("save file details controller error: " + str(e))

@api.route('/save_claim')
class SaveDropDown(Resource):
    @api.expect(claim_new, validate=True)
    @api.response(201, 'new claim added')
    @api.doc('add new claim')
    def post(self):
        data = request.json
        return save_claim(data=data)

#
#   feat  get the list of dropdown list.
#
@api.route('/get_claim_list/<user_id>')
class GetAllDropdownList(Resource):
    @api.doc('Get claim list')
    #@token_required
    # @marshal_with(claimlist)
    def get(self,user_id):
        try:
            """get claim list"""
            return get_claim_list(user_id)
        except Exception as e:
            logging.exception(e)
            return ""

@api.route('/get_claim_details/<claim_id>')
class GetAllDropdownList(Resource):
    @api.doc('Get claim detils')
    def get(self,claim_id):
        try:
            """get claim detils"""
            return get_claim_details(claim_id)
        except Exception as e:
            logging.exception(e)
            return ""

@api.route('/download/<uuid_filename>')
class downloadFile (Resource):
    def get(self,uuid_filename):
        try:
            return download_doc(uuid_filename)
        except Exception as e:
            print("Apply Leave controller error: " + str(e))
            logging.exception(e)

@api.route('/get_claim_type_count/<year>/<month>')
class GetTypeCounts(Resource):
    @api.doc('Get claim type count')
    def get(self,year,month):
        try:
            """get claim count"""
            return get_claim_type_count(year,month)
        except Exception as e:
            logging.exception(e)
            return ""

@api.route('/get_dashboard_list/<year>/<month>')
class GetDashboardList(Resource):
    @api.doc('Get Dashboard List')
    def get(self,year,month):
        try:
            """get claim count"""
            return get_dashboard_list(year,month)
        except Exception as e:
            logging.exception(e)
            return ""