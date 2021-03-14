from flask_restplus import Namespace, fields

address = {
    "address1": "string",
    "address2": "string",
    "city": "string",
    "state": "string",
    "zip": "string",
    "country": "string",
    "phonenumber": "string"
}
contacts = {
    "Phonenumber": "string",
}

rolepermission = {

    "menuid": "string"
}


class UserDto:
    api = Namespace('user', description='user related operations')
    fileupload = api.model('fileupload', {
        'data': fields.String(required=True, description='Base64 image data to upload.'),
    })

    download_pdf = api.model('download_pdf', {
        'user_id': fields.String(required=True, description='Html String.'),
        'type': fields.String(required=True, description='Html String.'),

    })
    user = api.model('user', {
        'public_id': fields.String(required=True, description='public id'),
        'email': fields.String(required=True, description='user email address'),
        'first_name': fields.String(required=True, description='user first name'),
        'last_name': fields.String(required=True, description='user last name'),
        'password': fields.String(required=True, description='user password'),
        'roles': fields.List(fields.Integer, required=False, description='user roles'),
        'image_path': fields.String(required=True, description='profile image_name'),
        'gender': fields.String(required=False, description='gender of the user'),
        'isActive': fields.String(required=False, description='Active status of the user'),
        'licence_expiry': fields.String(required=False, description='License Expiry Date of the user'),
    })

    add_account_details = api.model('user_address', {
        'first_name': fields.String(required=False, description="user first name"),
        'last_name': fields.String(required=False, description='user last name'),
        'contact_details': fields.List(fields.Raw(contacts), required=False, description='user contacts'),
        'address_details': fields.List(fields.Raw(address), required=False, description='address details'),
        'business_name': fields.String(required=False, description='business_name'),
        'business_number': fields.String(required=False, description='business_number'),
        'created_by': fields.Integer(required=True, description='created by')
    })

    user_update = api.model('user_update', {
        'public_id': fields.String(required=True, description='user public_id'),
        'password': fields.String(required=False, description='user password'),
        'old_password': fields.String(required=False, description='user password'),
        'first_name': fields.String(required=True, description='user first name'),
        'last_name': fields.String(required=True, description='user last name'),
        'business_name': fields.String(required=False, description='business_name'),
        'business_number': fields.String(required=False, description='business_number'),
        'address': fields.List(fields.Raw(address), required=False, description='user address'),
        'roles': fields.List(fields.Integer, required=False, description='user roles'),
        'permission': fields.List(fields.Integer, required=False, description='user permission'),
        'updated_by': fields.Integer(required=True, description='updated by ')
    })

    update_password = api.model('update_password', {
        'public_id': fields.String(required=True, description='user public_id'),
        'password': fields.String(required=True, description='user password')
    })

    validate_otp = api.model('validate_otp', {
        'otp': fields.String(required=True, description='OTP'),
        'public_id': fields.String(required=True, description='user public_id')
    })

    profile_password_update = api.model('profile_password_update', {
        'public_id': fields.String(required=True, description='public_id'),
        'cpassword': fields.String(required=True, description='public_id'),
        'password': fields.String(required=True, description='user password')
    })

    user_delete = api.model('user_delete', {
        'public_id': fields.String(required=True, description='user public_id')
    })
    lat_long = api.model('lat_long_update', {
        'public_id': fields.String(required=True, description='public_id'),
        'latitude': fields.String(required=True, description='public_id'),
        'longitude': fields.String(required=True, description='user password')
    })
    notify_token = api.model('token update', {
        'device_id': fields.String(required=True, description='device id'),
        'token': fields.String(required=True, description='token'),
        'public_id': fields.String(required=True, description='public_id'),
        'latitude': fields.String(required=True, description='public_id'),
        'longitude': fields.String(required=True, description='user password')
    })

    new_user = api.model('new user', {
        'public_id': fields.String(required=True, description='public id'),
        'rkp_name': fields.String(required=True, description='rkp name'),
        'user_name': fields.String(required=False, description='user_name'),
        'employment_date': fields.String(required=True, description='employment  date'),
        'employment_status': fields.String(required=True, description='employment status'),
        'password': fields.String(required=True, description='user password'),
        'roles': fields.List(fields.Integer, required=False, description='user roles'),
        'image_path': fields.String(required=True, description='profile image_name'),
        'district': fields.String(required=False, description='district of the user'),
        'state': fields.String(required=False, description='state'),
        'post_code': fields.String(required=False, description='post code'),
        'licence_expiry': fields.String(required=False, description='licence expiry'),
        'licence_number': fields.String(required=False, description='licence number'),
        'gdl_expiry': fields.String(required=False, description=' gdl expiry'),
        'melaka_port_expiry': fields.String(required=False, description='melaka port expiry'),
        'licence_type': fields.String(required=False, description='licence type'),
        'blood_type': fields.String(required=False, description='blood type'),
        'location': fields.String(required=False, description='location'),
        'rkp_id_number': fields.String(required=False, description='rkp id'),
        'rkp_ic_number': fields.String(required=False, description='rkp ic number'),
        'phone_number': fields.String(required=False, description='phone_number'),
        'medical_expiry': fields.String(required=False, description='medical_expiry'),
        'lpg_ptp_ogsp_expiry': fields.String(required=False, description='lpg_ptp_ogsp_expiry'),
        'remarks': fields.String(required=False, description='remarks'),
        'file_path': fields.String(required=False, description='file_path'),
        'address1': fields.String(required=False, description='address1'),
        'address2': fields.String(required=False, description='address2'),
        'created_by' : fields.Integer(required=False, description='created_by'),

    })

class RoleDto:
    api = Namespace('role', description='Role related operations')
    role = api.model('role', {
        'id': fields.Integer(required=True, description='user  id'),
        'role_Id': fields.Integer(required=False, description='roleId'),
        'role_Name': fields.String(required=True, description='role name'),
        'created_by': fields.Integer(required=True, description='created by ')
    })

    role_update = api.model('role_update', {
        'public_id': fields.String(required=True, description='user public_id'),
        'id': fields.Integer(required=True, description='user  id'),
        'role_Id': fields.Integer(required=False, description='roleId'),
        'role_Name': fields.String(required=True, description='role name'),
        # 'permission': fields.List(fields.Integer, required=False, description='user permission'),
        'updated_by': fields.Integer(required=True, description='updated by ')
    })
    role_delete = api.model('role_delete', {
        'id': fields.String(required=True, description='role id')
    })


class AuthDto:
    api = Namespace('auth', description='authentication related operations')
    user_auth = api.model('auth_details', {
        'email': fields.String(required=True, description='The email address'),
        'password': fields.String(required=True, description='The user password '),
    })


class RolepremissionDto:
    api = Namespace('rolepermission', description='Rolepermission related operations')
    rolepermission = api.model('rolepermission', {
        'public_id': fields.String(required=True, description='user public id'),
        'id': fields.Integer(required=True, description='user  id'),
        'role_Id': fields.Integer(required=False, description='roleId'),
        # 'rolepermission': fields.List(fields.Raw(rolepermission), required=True, description='Role Permissions'),
        'permission': fields.List(fields.Integer, required=False, description='user permission'),
        'created_by': fields.Integer(required=True, description='created by ')
    })

    rolepermission_update = api.model('rolepermission_update', {
        'public_id': fields.String(required=True, description='user public_id'),
        'id': fields.Integer(required=True, description='user  id'),
        'role_Id': fields.Integer(required=False, description='roleId'),
        # 'rolepermission': fields.List(fields.Raw(rolepermission), required=True, description='Role Permissions'),
        'permission': fields.List(fields.Integer, required=False, description='user permission'),
        'updated_by': fields.Integer(required=True, description='updated by ')
    })

    rolepermission_delete = api.model('rolepermission_delete', {
        'public_id': fields.String(required=True, description='role public_id')

    })


class MenuItemDto:
    api = Namespace('menuitem', description='Menuitem related operations')

    menuitem = api.model('menuitem', {
        'public_id': fields.String(required=True, description='user public id'),
        'id': fields.Integer(required=True, description='user  id'),
        'menu_Id': fields.Integer(required=False, description='roleId'),
        'menu_Item': fields.String(required=True, description='role name'),
    })

    rolemenu = api.model('rolemenu', {
        'role_menu_id': fields.Integer(required=False, description='role_menu_id'),
        'role_id': fields.Integer(required=False, description='role_id'),
        'menu_id': fields.Integer(required=False, description='Menu id'),
        'is_view': fields.Integer(required=False, description='Permission for view'),
        'is_add': fields.Integer(required=False, description='Permission for add'),
        'is_edit': fields.Integer(required=False, description='Permission for edit'),
        'is_delete': fields.Integer(required=False, description='Permission for delete'),
        'created_by': fields.Integer(required=True, description='created by ')
    })

    permission = api.model('permission', {
        'id': fields.Integer(required=False, description='Menu id for setting permission'),
        'is_view': fields.Boolean(required=True, description='View Permission'),
        'is_add': fields.Boolean(required=True, description='Add Permission'),
        'is_edit': fields.Boolean(required=True, description='Edit Permission'),
        'is_delete': fields.Boolean(required=True, description='Delete Permission')
    })

    all_permission_save = api.model('all_permission_save', {
        'role_id': fields.Integer(required=False, description='role_id'),
        'role_permission': fields.List(fields.Nested(permission)),
        'created_by': fields.Integer(required=True, description='created by ')
    })
class RKPDisciplinary:
    api = Namespace(' RKP Discipline', description='RKP Discipline related operations')

    discipline_add = api.model('RKP_Discipline_add', {
        'violation_date': fields.String(required=True, description='violation date'),
        'rt_number': fields.String(required=True, description='rt number'),
        'location': fields.String(required=False, description='location'),
        'client_name': fields.String(required=True, description='client_name'),
        'file_path': fields.String(required=True, description='file_path'),
        'description': fields.String(required=True, description='description'),
        'created_by' : fields.Integer(required=False, description='created_by'),
        'user_id': fields.Integer(required=False, description='created_by')
    })