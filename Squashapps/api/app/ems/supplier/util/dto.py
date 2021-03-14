from flask_restplus import Namespace, fields


class SupplierDto:
    api = Namespace('supplier', description='supplier related operations')
    supplier_save = api.model('supplier_save', {
        'id': fields.Integer(required=False, description='supplier id'),
        'public_id': fields.String(required=False, description='supplier public id'),
        'supplier_name': fields.String(required=True, description='Name of the supplier'),
        'supplier_location': fields.String(required=True, description='Location of the Company supplier'),
        'contact_number': fields.String(required=True, description='supplier Contact Number'),
        'email_id': fields.String(required=True, description='Email Address for the Company supplier'),
        'created_by': fields.Integer(required=True, description='created by')
    })
    delete_supplier = api.model('delete_from_supplier', {
        'user_id': fields.Integer(required=True, description='userID'),
        'public_id': fields.String(required=True, description='supplier public Id')
    })

    supplier_info = api.model('supplier_info', {
        'public_id': fields.String(required=False, description='Company id'),
        'supplier_name': fields.String(required=True, description='Name of the Company supplier'),
        'supplier_location': fields.String(required=True, description='Location of the Company supplier'),
        'contact_number': fields.String(required=True, description='Company supplier Contact Number'),
        'email_id': fields.String(required=True, description='Email Address for the Company supplier')
    })

    supplier_info_r = api.model('supplier_info_r', {
        'Data': fields.Raw(supplier_info,required=False, description='supplier information'),
        "ErrorCode": fields.String(required=False, description='ErrorCode'),
        "URL": fields.String(required=False, description='URL'),
        "Message": fields.String(required=False, description='Message'),
    })

    supplier_list_resp = api.model('supplier_list_resp', {
        "total_count": fields.Integer(required=True, description='total_count'),
        "data": fields.List(fields.Nested(supplier_info))
    })