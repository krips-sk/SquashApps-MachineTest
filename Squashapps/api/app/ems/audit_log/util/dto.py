from flask_restplus import Namespace, fields


class AuditLogdto:
    api = Namespace('audit_log', description='Audit Log related operations')
    log_details = api.model('log_details', {
        'description': fields.String(required=False, description='description of audit log')
    })
    audit_log_save = api.model('audit_log_save', {
        'audit_log_id': fields.Integer(required=False, description='id of audit log'),
        'type': fields.String(required=True, description='Main type'),
        'sub_type': fields.String(required=True, description='sub type'),
        'details': fields.Nested(log_details, required=True, description='inspection item detail'),
        'created_by': fields.Integer(required=False, description='login user id')
    })

    delete_audit_log = api.model('delete_audit_log', {
        'audit_log_id': fields.Integer(required=True, description='id of audit log'),
        'userid': fields.Integer(required=True, description='login user id')
    })
    res_audit_log_info = api.model('res_audit_log_info', {
        'ErrorCode': fields.String(required=True, description='Error code'),
        'count': fields.Integer(required=True, description='count'),
        'data': fields.List(fields.Nested(audit_log_save), required=True, description='')
    })