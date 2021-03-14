import logging

from flask_restplus import Resource
from flask import request
from werkzeug.datastructures import FileStorage
from ..service.legal_document_service import get_admin_approve_docs,DocumentUpload,Savelegaldocument,get_document,get_document_data,Update_approver_status\
    ,download_doc
from ..util.dto import Legal_DocumentsDto



api = Legal_DocumentsDto.api
save_legaldocument = Legal_DocumentsDto.save_legaldocument
update_approver_status = Legal_DocumentsDto.update_approver_status

upload_parser = api.parser()
upload_parser.add_argument('file', location='files',type=FileStorage, required=True)
# upload_parser.add_argument('user_id', required=True)
# upload_parser.add_argument('document_type', required=True)

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

@api.route('/savelegaldocument')
class savelegaldocument(Resource):
    @api.doc("Save Legal Document")
    @api.expect(save_legaldocument, validate=True)
    def post(self):
        try:
            data = request.json
            return Savelegaldocument(data)
        except Exception as e:
            print("Apply Leave controller error: " + str(e))
            logging.exception(e)

@api.route('/get_legal_doc/<filename>')
class GetLegalDoc(Resource):
    def get(self,filename):
        try:
            return get_document(filename)
        except Exception as e:
            print("Apply Leave controller error: " + str(e))
            logging.exception(e)

@api.route('/get_document_date/<userid>')
class GetLegalDoc(Resource):
    def get(self,userid):
        try:
            return get_document_data(userid)
        except Exception as e:
            print("Apply Leave controller error: " + str(e))
            logging.exception(e)

@api.route('/get_admin_legal_docs')
class GetAdminLegalDocs(Resource):
    def get(self):
        try:
            return get_admin_approve_docs()
        except Exception as e:
            print("get list error: " + str(e))
            logging.exception(e)

@api.route('/update_approved_status')
class UpdateLegaldocApproveStatus(Resource):
    @api.doc("Update Status")
    @api.expect(update_approver_status, validate=True)
    def post(self):
        try:
            data = request.json
            return Update_approver_status(data)
        except Exception as e:
            print("Apply Leave controller error: " + str(e))
            logging.exception(e)

@api.route('/download/<uuid_filename>')
class downloadFile (Resource):
    def get(self,uuid_filename):
        try:
            return download_doc(uuid_filename)
        except Exception as e:
            print("Apply Leave controller error: " + str(e))
            logging.exception(e)