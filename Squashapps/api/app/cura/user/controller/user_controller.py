from flask import request
from flask_restplus import Resource
import logging

from app.cura.user.util.decorator import admin_token_required
from ..util.dto import UserDto
from ..service.user_service import add_user, update_user, get_a_user, delete_user \
    , update_user_password, forgotpassword, get_all_users_bytype, Validate_OTP, profile_upload, file_get, \
    update_lat_long, update_device_token, update_device_config_into_user, get_user_dropdown, getuserInformation, \
    getuserdocexpiry, yearlist,pdf_download,save_user,DocumentUpload,get_states,get_empid_dropdown
from app.cura.util.constants import constant
from werkzeug.datastructures import FileStorage

api = UserDto.api

upload_parser = api.parser()
upload_parser.add_argument('file', location='files',type=FileStorage, required=True)

_user = UserDto.user
user_update = UserDto.user_update
user_delete = UserDto.user_delete
update_password = UserDto.update_password
validate_otp = UserDto.validate_otp
add_account_details = UserDto.add_account_details
profile_password_update=UserDto.profile_password_update
fileupload =UserDto.fileupload
lat_long=UserDto.lat_long
notify_token=UserDto.notify_token
download_pdf = UserDto.download_pdf
new_user = UserDto.new_user
@api.route('/getuserlist/<searchterm>/<role>/<int:page>/<int:row>')
class GetUserList(Resource):
    @api.doc('list_of_registered_users')
    #@token_required
    #@api.marshal_list_with(_user, envelope='data')
    def get(self, searchterm, role, page, row):
        logging.info("This is a test log")
        logging.info(constant("INVALID_USER"))

        """List all registered users"""
        return get_all_users_bytype(searchterm, role, page, row)


@api.route('/id/<public_id>')
class UserGet(Resource):
    @api.doc('get a user')
    #@token_required
    @api.marshal_with(_user)
    def get(self, public_id):
        """get a user given its identifier"""
        user = get_a_user(public_id)
        if not user:
            api.abort(404)
        else:
            return user

@api.route('/add')
class UserAdd(Resource):
    @api.expect(_user, validate=True)
    #@token_required
    @api.response(201, 'User successfully created.')
    @api.doc('create a new user')
    def post(self):
        """Creates a new User """
        data = request.json
        print(data);
        return add_user(data)


@api.route('/update')
class UserUpdate(Resource):
    @api.expect(user_update, validate=True)
    #@token_required
    @api.response(201, 'User successfully updated.')
    @api.doc('update user')
    def post(self):
        """Update User """
        data = request.json
        return update_user(data=data)

@api.route('/updatepassword')
class UserUpdate(Resource):
    @api.expect(update_password, validate=True)
    @api.response(201, 'Password successfully updated.')
    @api.doc('update password')
    def post(self):
        """Update Password """
        data = request.json
        return update_user_password(data=data)

@api.route('/validateotp')
class ValidateOTP(Resource):
    @api.expect(validate_otp, validate=True)
    @api.response(201, 'Password successfully updated.')
    @api.doc('update password')
    def post(self):
        """Update Password """
        data = request.json
        return Validate_OTP(data=data)

@api.route('/delete/<status>')
class UserDelete(Resource):
    @api.expect(user_delete, validate   =True)
    #@token_required
    @api.response(201, 'User deleted.')
    @api.doc('Delete user')
    def post(self,status):
        """Delete User """
        data = request.json
        logging.info("This is a test log")
        return delete_user(data,status)


@api.route('/forgotpassword/<email>')
class UserUpdate(Resource):
    # @api.expect(profile_password_update, validate=True)
    #@token_required
    @api.response(201, 'Password successfully updated.')
    @api.doc('update password')
    def get(self,email):
        """Update Password """
        return forgotpassword(email)

@api.route('/upload_profile_image')
class UpdateFile(Resource):
    @api.response(201, 'uploaded updated.')
    @api.expect(fileupload, validate=True)
    @api.doc('upload file')
    def post(self):
        """Upload File """
        # file = request.files['file']
        file=request.json['data']
        return profile_upload('base64', file)[0]

@api.route('/get_profile_image/<filename>')
class GetFile(Resource):
    @api.response(201, 'uploaded updated.')
    @api.doc('upload file')
    def get(self,filename):
       """Upload File """
       return file_get(filename)

@api.route('/update_lat_long')
class UpdateuserLatLong(Resource):
    @api.expect(lat_long, validate=True)
    @api.response(201, 'Password successfully updated.')
    @api.doc('update password')
    def post(self):
        """Update Password """
        data = request.json
        return update_lat_long(data=data)

@api.route('/save/notification_token')
class UpdateNotificationToken(Resource):
    @api.expect(notify_token, validate=True)
    @api.response(201, 'Notification Token updated.')
    @api.doc('update notification token')
    def post(self):
        data = request.json
        return update_device_token(data=data)

@api.route('/update/device_config_user/<user_id>/<device_config_id>')
class UpdateNotificationToken(Resource):
    @api.response(201, 'Device Config Updated.')
    @api.doc('Update Device Config')
    def get(self,user_id,device_config_id):

        return update_device_config_into_user(user_id,device_config_id)


@api.route('/user_dropdown_list/<search>/<page>/<row>')
class GetDropdown(Resource):
    @api.doc('get a user dropdown list')
    #@token_required
    def get(self,search,page,row):
        user = get_user_dropdown(search,page,row)
        if not user:
            api.abort(404)
        else:
            return user

@api.route('/getuserInformation/<user_id>')
class GetUserInformation(Resource):
    @api.response(201, 'Get User Information')
    @api.doc('Get User Information')
    def get(self,user_id):
        try:
            return getuserInformation(user_id)
        except Exception as e:
            logging.exception(e)

@api.route('/getuserdocexpiry/<location>/<page>/<row>')
class GetUserDocExpiry(Resource):
    @api.response(201, 'Get User Information')
    @api.doc('Get User Information')
    def get(self,location,page,row):
        try:
            return getuserdocexpiry(location,page,row)
        except Exception as e:
            logging.exception(e)

@api.route('/yearlist')
class YearList(Resource):
    @api.response(201, 'Get Year List')
    @api.doc('Get Year List')
    def get(self):
        try:
            return yearlist()
        except Exception as e:
            logging.exception(e)

@api.route('/pdf/download')
class DonloadPDF(Resource):
    @api.expect(download_pdf, validate=True)
    @api.response(201, 'Notification Token updated.')
    @api.doc('update notification token')
    def post(self):
        data = request.json
        return pdf_download(data=data)

@api.route('/save')
class SaveNewUser(Resource):
    @api.expect(new_user, validate=True)
    @api.response(201, 'User Details Updated')
    @api.doc('Add or update user details')
    def post(self):
        data = request.json
        return save_user(data=data)

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

@api.route('/get_state_list')
class StateList(Resource):
    @api.response(201, 'Get State List')
    @api.doc('Get State List')
    def get(self):
        try:
            return get_states()
        except Exception as e:
            logging.exception(e)

@api.route('/empid_dropdown_list/<search>/<page>/<row>')
class GetDropdown(Resource):
    @api.doc('get a employee id dropdown list')
    #@token_required
    def get(self,search,page,row):
        user = get_empid_dropdown(search,page,row)
        if not user:
            api.abort(404)
        else:
            return user