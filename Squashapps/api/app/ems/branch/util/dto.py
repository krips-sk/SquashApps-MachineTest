from flask_restplus import Namespace, fields


class BranchDto:
    api = Namespace('branch', description='Branch related operations')
    branch_save = api.model('branch_save', {
        'id': fields.Integer(required=False, description='Branch id'),
        'public_id': fields.String(required=False, description='Branch public id'),
        'branch_name': fields.String(required=True, description='Name of the Branch'),
        'branch_location': fields.String(required=True, description='Location of the Company Branch'),
        'contact_number': fields.String(required=True, description='Branch Contact Number'),
        'email_id': fields.String(required=True, description='Email Address for the Company branch'),
        'logo_path': fields.String(required=True, description='Company Branch Logo Uploaded Path'),
        'created_by': fields.Integer(required=True, description='created by')
    })
    delete_branch = api.model('delete_from_branch', {
        'user_id': fields.Integer(required=True, description='userID'),
        'public_id': fields.String(required=True, description='branch public Id')
    })

    branch_info = api.model('branch_info', {
        'public_id': fields.String(required=False, description='Company id'),
        'branch_name': fields.String(required=True, description='Name of the Company branch'),
        'branch_location': fields.String(required=True, description='Location of the Company branch'),
        'contact_number': fields.String(required=True, description='Company branch Contact Number'),
        'email_id': fields.String(required=True, description='Email Address for the Company branch'),
        'logo_path': fields.String(required=True, description='Company branch Logo Uploaded Path')
    })

    branch_info_r = api.model('branch_info_r', {
        'Data': fields.Raw(branch_info,required=False, description='branch information'),
        "ErrorCode": fields.String(required=False, description='ErrorCode'),
        "URL": fields.String(required=False, description='URL'),
        "Message": fields.String(required=False, description='Message'),
    })

    branch_list_resp = api.model('branch_list_resp', {
        "total_count": fields.Integer(required=True, description='total_count'),
        "data": fields.List(fields.Nested(branch_info))
    })