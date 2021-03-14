import logging

from flask_restplus import Resource
from flask import request
from ..service.leave_management_service import getleavesummary, Apply_Leave, getmonthleavecount, getapplieduserlist, \
    get_LeaveApplication, getleaveInformation, approve_Leave, getLeaveStatus, getuserlist, getuserInformation, \
    updateleavecount, getleavesummaryinfo, getleaveappliedlist, addmedicalclaim, getmedicalclaimlist, getmedicalclaim, \
    getmedicalclaimsummaryinfo, updatemediclaimsummary, userbalanceleavecount, getapprovedleavecount, approveduserlist, \
    usermedicalclaimsummary, usermedicalcheckupsummary,DocumentUpload,get_leave_document,DocumentUpload_Claim,delete_medicalclaim,download_doc

from ..util.dto import Leave_ManagementDto
from werkzeug.datastructures import FileStorage

api = Leave_ManagementDto.api

upload_parser = api.parser()
upload_parser.add_argument('file', location='files',type=FileStorage, required=True)
# upload_parser.add_argument("user_id")

applyLeave = Leave_ManagementDto.applyLeave
approveLeave = Leave_ManagementDto.approveLeave
updateleave_count = Leave_ManagementDto.updateleave_count
add_medicalclaim = Leave_ManagementDto.add_medicalclaim
updatemediclaim_summary =Leave_ManagementDto.updatemediclaimsummary
_delete_medical_claim = Leave_ManagementDto.delete_medical_claim

@api.route('/getleavesummary/<userid>/<year>')
class GetUserLeaveSummary(Resource):
    @api.response(201, 'User profile List.')
    @api.doc('user profile list')
    def get(self, userid,year):
        try:
            return getleavesummary(userid,year)

        except Exception as e:
            logging.exception(e)

@api.route('/applyleave')
class ApplyLeave(Resource):
    @api.doc("Apply Leave")
    @api.expect(applyLeave, validate=True)
    def post(self):
        try:
            data = request.json
            return Apply_Leave(data)
        except Exception as e:
            print("Apply Leave controller error: " + str(e))
            logging.exception(e)


@api.route('/getleaveInformation/<user_id>/<leave_id>')
class GetLeaveInformation(Resource):
    @api.response(201, 'Get Leave Information List.')
    @api.doc('Get Leave Information list')
    def get(self, user_id,leave_id):
        try:
            return getleaveInformation(user_id,leave_id)

        except Exception as e:
            logging.exception(e)

@api.route('/approveLeave')
class ApproveLeave(Resource):
    @api.doc("Approve Leave")
    @api.expect(approveLeave, validate=True)
    def post(self):
        try:
            data = request.json
            return approve_Leave(data)

        except Exception as e:
            logging.exception(e)

@api.route('/getmonthleavecount/<month>/<year>/<type>')
class GetLeaveCountOfMonth(Resource):
    @api.response(201, 'User profile List.')
    @api.doc('user profile list')
    def get(self, month,year,type):
        try:
            return getmonthleavecount(month,year,type)

        except Exception as e:
            logging.exception(e)

@api.route('/applieduserlist/<date>/<type>')
class GetUserListApplied(Resource):
    @api.response(201, 'User profile List.')
    @api.doc('user profile list')
    def get(self, date,type):
        try:
            return getapplieduserlist(date,type)

        except Exception as e:
            logging.exception(e)

@api.route('/getLeaveApplication/<leave_id>')
class GetLeaveApplication(Resource):
    @api.response(201, 'User profile List.')
    @api.doc('user profile list')
    def get(self, leave_id):
        try:
            return get_LeaveApplication(leave_id)

        except Exception as e:
            logging.exception(e)

@api.route('/getLeaveStatus/<user_id>')
class GetLeaveStatus(Resource):
    @api.response(201, 'Get Leave Status')
    @api.doc('Get Leave Status')
    def get(self, user_id):
        try:
            return getLeaveStatus(user_id)

        except Exception as e:
            logging.exception(e)

@api.route('/getuserlist/<page>/<row>')
class GetUserList(Resource):
    @api.response(201, 'User List.')
    @api.doc('user list')
    def get(self,page,row):
        try:
            return getuserlist(page,row)

        except Exception as e:
            logging.exception(e)

@api.route('/getuserInformation/<user_id>')
class GetUserInformation(Resource):
    @api.response(201, 'Get User Information')
    @api.doc('Get User Information')
    def get(self,user_id):
        try:
            return getuserInformation(user_id)
        except Exception as e:
            logging.exception(e)


@api.route('/updateleavecount')
class UpdateLeaveCount(Resource):
    @api.doc("Update Leave Count")
    @api.expect(updateleave_count, validate=True)
    def post(self):
        try:
            data = request.json
            return updateleavecount(data)
        except Exception as e:
            print("Update Leave Count controller error: " + str(e))
            logging.exception(e)

@api.route('/getleavesummaryinfo/<user_id>/<year>')
class GetLeaveSummaryInfo(Resource):
    @api.response(201, 'Get User Information')
    @api.doc('Get User Information')
    def get(self,user_id,year):
        try:
            return getleavesummaryinfo(user_id,year)
        except Exception as e:
            logging.exception(e)

@api.route('/getleaveappliedlist/<user_id>/<year>/<type>')
class GetLeaveAppliedList(Resource):
    @api.response(201, 'Get Leave Applied List')
    @api.doc('Get Leave Applied List')
    def get(self,user_id,year,type):
        try:
            return getleaveappliedlist(user_id,year,type)
        except Exception as e:
            logging.exception(e)


@api.route('/addmedicalclaim')
class AddMedicalClaim(Resource):
    @api.doc("Update Leave Count")
    @api.expect(add_medicalclaim, validate=True)
    def post(self):
        try:
            data = request.json
            return addmedicalclaim(data)
        except Exception as e:
            print("Update Leave Count controller error: " + str(e))
            logging.exception(e)

@api.route('/getmedicalclaimlist/<user_id>/<year>')
class GetMedicalClaimList(Resource):
    @api.response(201, 'Get Leave Applied List')
    @api.doc('Get Leave Applied List')
    def get(self,user_id,year):
        try:
            return getmedicalclaimlist(user_id,year)
        except Exception as e:
            logging.exception(e)

@api.route('/getmedicalclaim/<claim_id>')
class GetMedicalClaim(Resource):
    @api.response(201, 'Get Leave Applied List')
    @api.doc('Get Leave Applied List')
    def get(self,claim_id):
        try:
            return getmedicalclaim(claim_id)
        except Exception as e:
            logging.exception(e)

@api.route('/deletemedicalclaim')
class DeleteMedicalClaim(Resource):
    @api.response(201, 'Delete Medical Claim')
    @api.expect(_delete_medical_claim, validate=True)
    @api.doc('Delete Medical Claim')
    def post(self):
        data = request.json
        return delete_medicalclaim(data)


@api.route('/getmedicalclaimsummaryinfo/<user_id>/<year>')
class GetMedicalClaimSummaryInfo(Resource):
    @api.response(201, 'Get Medical Claim Summary Info Information')
    @api.doc('Get Medical Claim Summary Info Information')
    def get(self,user_id,year):
        try:
            return getmedicalclaimsummaryinfo(user_id,year)
        except Exception as e:
            logging.exception(e)

@api.route('/updatemediclaimsummary')
class UpdateMediClaimSummary(Resource):
    @api.doc("Update Leave Count")
    @api.expect(updatemediclaim_summary, validate=True)
    def post(self):
        try:
            data = request.json
            return updatemediclaimsummary(data)
        except Exception as e:
            print("Update Leave Count controller error: " + str(e))
            logging.exception(e)


@api.route('/userbalanceleavecount/<page>/<row>/<search>')
class UserBalanceLeaveCount(Resource):
    @api.response(201, 'Get User Balance Count Info Information')
    @api.doc('Get User Balance Count Info Information')
    def get(self,page,row,search):
        try:
            return userbalanceleavecount(page,row,search)
        except Exception as e:
            logging.exception(e)

@api.route('/getapprovedleavecount/<month>/<year>')
class GetApprovedLeaveCount(Resource):
    @api.response(201, 'User profile List.')
    @api.doc('user profile list')
    def get(self, month,year):
        try:
            return getapprovedleavecount(month,year)

        except Exception as e:
            logging.exception(e)

@api.route('/approveduserlist/<date>')
class ApprovedUserList(Resource):
    @api.response(201, 'User profile List.')
    @api.doc('user profile list')
    def get(self, date):
        try:
            return approveduserlist(date)

        except Exception as e:
            logging.exception(e)


@api.route('/usermedicalclaimsummary/<year>/<search>/<page>/<row>')
class UserMedicalClaimSummary(Resource):
    @api.response(201, 'Get User Balance Count Info Information')
    @api.doc('Get User Balance Count Info Information')
    def get(self,year,search,page,row):
        try:
            return usermedicalclaimsummary(year,search,page,row)
        except Exception as e:
            logging.exception(e)

@api.route('/usermedicalcheckupsummary/<year>/<search>/<page>/<row>')
class UserMedicalCheckupSummary(Resource):
    @api.response(201, 'Get User Balance Count Info Information')
    @api.doc('Get User Balance Count Info Information')
    def get(self,year,search,page,row):
        try:
            return usermedicalcheckupsummary(year,search,page,row)
        except Exception as e:
            logging.exception(e)

@api.route('/documentUpload')
class documentUpload(Resource):
    @api.expect(upload_parser, validate=True)
    @api.response(201, 'file_uploaded successfully')
    @api.doc('file_upload details')
    def post(self):
        try:
            file = request
            files = DocumentUpload(file)
            if not files:
                api.abort(404)
            else:
                return files
        except request.exceptions.HTTPError as e:
            print(200)
            logging.exception(str(e))
            print("save file details controller error: " + str(e))

@api.route('/get_leave_upload_doc/<filename>')
class GetLegalDoc(Resource):
    def get(self,filename):
        try:
            return get_leave_document(filename)
        except Exception as e:
            print("Apply Leave controller error: " + str(e))
            logging.exception(e)

upload_parser_claim = api.parser()
upload_parser_claim.add_argument('file', location='files',type=FileStorage, required=True)
@api.route('/documentUploadClaim')
class documentUploadClaim(Resource):
    @api.expect(upload_parser, validate=True)
    @api.response(201, 'file_uploaded successfully')
    @api.doc('file_upload details')
    def post(self):
        try:
            file = request.files['file']
            files = DocumentUpload_Claim(file)
            if not files:
                api.abort(404)
            else:
                return files
        except request.exceptions.HTTPError as e:
            print(200)
            logging.exception(str(e))
            print("save file details controller error: " + str(e))

@api.route('/download/<uuid_filename>')
class downloadFile (Resource):
    def get(self,uuid_filename):
        try:
            return download_doc(uuid_filename)
        except Exception as e:
            print("Apply Leave controller error: " + str(e))
            logging.exception(e)

