from flask_restplus import Namespace, fields


class PDCRegistrationdto:
    api = Namespace('pdc_registration', description='PDC Registration related operations')

    pdc_inspection = api.model('pdc_inspection', {
        'inspection_id': fields.Integer(required=False, description='id of pdc inspection item'),
        'inspection_status': fields.Integer(required=True, description='status of the inspection'),
        'checklist_id': fields.Integer(required=True, description='check list id'),
        'findings': fields.String(required=True, description='inspection item detail')
    })

    add_pdc_registration = api.model('add_pdc_registration', {
        'pdc_registration_id': fields.Integer(required=True, description='id of pdc registration'),
        'inspection_type': fields.Integer(required=True, description='inspection type'),
        'submit_type': fields.Integer(required=True, description='submit type'),
        'user_id': fields.Integer(required=True, description='user id of the RKP - delivery person'),
        'vehicle_id': fields.Integer(required=True, description='vehicle id chosen'),
        'inspection_notes': fields.String(required=True, description='notes for the inspection'),
        'schedule_id': fields.Integer(required=True, description='schedule_id for doing pdc'),
        'pdc_inspection': fields.List(fields.Nested(pdc_inspection), required=True, description='PDC Inspection list'),
        'created_by': fields.Integer(required=False, description='login user id'),
    })

    approval_pdc_item = api.model('approval_pdc_item', {
        'inspection_id': fields.Integer(required=True, description='id of pdc inspection item'),
        'approval_category': fields.Integer(required=True, description='category of the inspection')
    })
    add_approval_pdc = api.model('add_approval_pdc', {
        'pdc_registration_id': fields.Integer(required=True, description='id of pdc registration'),
        'user_id': fields.Integer(required=True, description='user id of the RKP - delivery person'),
        'vehicle_id': fields.Integer(required=True, description='vehicle id chosen'),
        'approval_notes': fields.String(required=True, description='notes for the inspection'),
        'approval_pdc_item': fields.List(fields.Nested(approval_pdc_item), required=True,
                                         description='PDC Inspection list'),
        'approval_status': fields.Integer(required=True, description='Status of the approval'),
        'created_by': fields.Integer(required=False, description='login user id'),
    })

    delete_pdc = api.model('delete_pdc', {
        'pdc_registration_id': fields.Integer(required=True, description='id of pdc registration'),
        'userid': fields.Integer(required=True, description='login user id')
    })
    res_pdc_reg_info = api.model('res_pdc_reg_info', {
        'ErrorCode': fields.String(required=True, description='Error code'),
        'count': fields.Integer(required=True, description='count'),
        'data': fields.List(fields.Nested(add_pdc_registration), required=True, description='')
    })
    pdc_ack = api.model('pdc_ack', {
        'schedule_id': fields.Integer(required=True, description='id of schedule'),
        'userid': fields.Integer(required=True, description='login user id')
    })
    inspection_item = api.model('inspection_item', {
        'checklist_id': fields.Integer(required=True, description='id of pdc registration'),
        'module': fields.Integer(required=True, description='module id', default=1),
        'sub_module': fields.Integer(required=True, description='sub module id', default=1),
        'zone': fields.Integer(required=True, description='zone id'),
        'item_description': fields.String(required=True, description='description of the item'),
        'findings': fields.String(required=True, description='inspection item detail', default=''),
        'inspection_status': fields.Integer(required=True, description='status of the inspection', default=1),
        'icon_name': fields.String(required=True, description='inspection item icon name', default='inspection_icon.png'),
    })
    res_check_list = api.model('res_check_list', {
        'ErrorCode': fields.String(required=True, description='Error code'),
        'front': fields.List(fields.Nested(inspection_item), required=True, description=''),
        'right': fields.List(fields.Nested(inspection_item), required=True, description=''),
        'rear': fields.List(fields.Nested(inspection_item), required=True, description=''),
        'left': fields.List(fields.Nested(inspection_item), required=True, description='')
    })

    rkp_login = api.model('rkp login', {
        'user_id': fields.Integer(required=False, description='user id'),
        'is_start': fields.Integer(required=True, description='RT status'),
        'rkp_login_id': fields.Integer(required=True, description='Login Id'),
    })
