from flask_restplus import Namespace, fields


class DepartmentDto:
    api = Namespace('department', description='Department related operations')
    department_save = api.model('department_save', {
        'id': fields.Integer(required=False, description='Department id'),
        'public_id': fields.String(required=False, description='Department public id'),
        'department_name': fields.String(required=True, description='Name of the Department'),
        'department_location': fields.String(required=True, description='Location of the Company department'),
        'contact_number': fields.String(required=True, description='department Contact Number'),
        'email_id': fields.String(required=True, description='Email Address for the Company department'),
        'logo_path': fields.String(required=True, description='Company department Logo Uploaded Path'),
        'created_by': fields.Integer(required=True, description='created by')
    })
    delete_department = api.model('delete_from_department', {
        'user_id': fields.Integer(required=True, description='userID'),
        'public_id': fields.String(required=True, description='department public Id')
    })

    department_info = api.model('department_info', {
        'public_id': fields.String(required=False, description='Company id'),
        'department_name': fields.String(required=True, description='Name of the Company department'),
        'department_location': fields.String(required=True, description='Location of the Company department'),
        'contact_number': fields.String(required=True, description='Company department Contact Number'),
        'email_id': fields.String(required=True, description='Email Address for the Company department'),
        'logo_path': fields.String(required=True, description='Company department Logo Uploaded Path')
    })

    department_info_r = api.model('department_info_r', {
        'Data': fields.Raw(department_info,required=False, description='department information'),
        "ErrorCode": fields.String(required=False, description='ErrorCode'),
        "URL": fields.String(required=False, description='URL'),
        "Message": fields.String(required=False, description='Message'),
    })

    department_list_resp = api.model('department_list_resp', {
        "total_count": fields.Integer(required=True, description='total_count'),
        "data": fields.List(fields.Nested(department_info))
    })