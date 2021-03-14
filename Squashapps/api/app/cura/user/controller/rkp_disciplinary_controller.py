from flask import request
from flask_restplus import Resource
import logging
from ..util.dto import RKPDisciplinary
from ..service.rkp_service import add_disciplinary, get_rkp_discipline, get_disciplinary_list,DocumentUpload,get_all_disciplinary_list
from werkzeug.datastructures import FileStorage

api = RKPDisciplinary.api
discipline_add = RKPDisciplinary.discipline_add

upload_parser = api.parser()
upload_parser.add_argument('file', location='files',type=FileStorage, required=True)


@api.route('/add_disciplinary')
class AddRKPDiscipline(Resource):
    @api.expect(discipline_add, validate=True)
    @api.response(201, 'RKP disciplinary Added successfully.')
    @api.doc('create a RKP disciplinary')
    def post(self):
        """Creates or update Role menu"""
        data = request.json
        print(data);
        return add_disciplinary(data)

@api.route('/get_disciplinary_by_user/<user_id>')
class GetDisciplinary(Resource):
    @api.response(201, 'Got disciplinary details.')
    @api.doc('Get  RKP disciplinary')
    def get(self,user_id):
        """Creates or update Role menu"""

        return get_rkp_discipline(user_id)

@api.route('/get_disciplinary_list/<user_id>/<page>/<row>')
class GetDisciplinaryList(Resource):
    @api.response(201, 'Got disciplinary details.')
    @api.doc('Get  RKP disciplinary')
    def get(self,user_id,page,row):
        """Get RKP disciplinary"""

        return get_disciplinary_list(user_id,page,row)

@api.route('/getall_disciplinary_list/<page>/<row>')
class GetDisciplinaryList(Resource):
    @api.response(201, 'Got disciplinary details.')
    @api.doc('Get  RKP disciplinary')
    def get(self,page,row):
        """Get RKP disciplinary"""

        return get_all_disciplinary_list(page,row)


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
