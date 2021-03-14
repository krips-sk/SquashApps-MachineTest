from flask_restplus import Namespace, fields


class Scheduledto:
    api = Namespace('schedule', description='Schedule related operations')

    add_schedule = api.model('add_schedule', {
        'schedule_id': fields.Integer(required=True, description='id of schedule'),
        'user_id': fields.Integer(required=True, description='user id of the RKP - delivery person'),
        'vehicle_id': fields.Integer(required=True, description='vehicle id chosen'),
        'schedule_status': fields.Integer(required=True, description='status of the schedule'),
        'rt_regn': fields.String(required=True, description='rt registration number'),
        'schedule_date': fields.String(required=True, description='schedule date'),
        'shipment_no': fields.String(required=True, description='shipment number'),
        'delivery_note_no': fields.String(required=True, description='delivery notes number'),
        'ship_to_party': fields.String(required=True, description='party to ship'),
        'loc': fields.String(required=True, description='loc'),
        'product': fields.String(required=True, description='product'),
        'dist': fields.String(required=True, description='distance for the trip'),
        'payment': fields.String(required=True, description='Payment amount for the schedule'),
        'Rg': fields.String(required=True, description='Rg'),
        'PLdTime': fields.String(required=True, description='PLdTime'),
        'Qty': fields.String(required=True, description='Qty'),
        'client': fields.String(required=True, description='client'),
        'created_by': fields.Integer(required=False, description='login user id'),
        'user_name': fields.String(required=False, description='user name'),
        'isRow_Editable':fields.Boolean(required=False, description='user name'),
    })

    add_schedule_v3 = api.model('add_schedule_v3', {
        'schedule_id': fields.Integer(required=True, description='id of schedule'),
        'user_id': fields.Integer(required=True, description='user id of the RKP - delivery person'),
        'schedule_status': fields.Integer(required=True, description='status of the schedule'),
        'vehicle_id': fields.Integer(required=True, description='vehicle id chosen'),
        'rt_regn': fields.String(required=True, description='rt registration number'),
        'payment': fields.String(required=True, description='Payment amount for the schedule'),
        'dist': fields.String(required=True, description='distance for the trip'),
        'created_by': fields.Integer(required=False, description='login user id'),
        'user_name': fields.String(required=False, description='user name'),
        'isRow_Editable': fields.Boolean(required=False, description='user name'),

        'PlnStLdDt': fields.String(required=True, description='schedule date'),
        'Shipment': fields.String(required=True, description='shipment number'),
        'D Note': fields.String(required=True, description='delivery notes number'),
        'City': fields.String(required=True, description='loc'),
        'Material': fields.String(required=True, description='product'),
        'Rg': fields.String(required=True, description='Rg'),
        'T':fields.String(required=True, description='T'),
        'PLdTime': fields.String(required=True, description='PLdTime'),
        'Qty': fields.String(required=True, description='Qty'),
        'Name': fields.String(required=True, description='client'),
        'Plnt': fields.String(required=True, description='Plnt'),
        'SC': fields.String(required=True, description='SC'),
        'TransPlnDt': fields.String(required=True, description='TransPlnDt'),
        'Dlvr': fields.String(required=True, description='Dlvr'),
        'S': fields.String(required=True, description='S'),
        'ActStLdT': fields.String(required=True, description='ActStLdT'),
        'Ship-to': fields.String(required=True, description='Ship-to'),
        'Maximum volume': fields.String(required=True, description='Maximum volume'),
        'ETA time': fields.String(required=True, description='ETA time'),
        'Sold-to': fields.String(required=True, description='Sold-to'),
        'ShTy': fields.String(required=True, description='ShTy'),
    })

    delete_schedule = api.model('delete_schedule', {
        'schedule_id': fields.Integer(required=True, description='id of schedule'),
        'userid': fields.Integer(required=True, description='login user id')
    })

    add_multiple_schedule = api.model('add_multiple_schedule', {
        'schedule': fields.List(fields.Nested(add_schedule), required=True, description='schedule list'),
        'userid': fields.Integer(required=True, description='login user id'),
        'schedule_type': fields.Integer(required=True, description='login user id')
    })

    add_multiple_schedule_v3 = api.model('add_multiple_schedule_v3', {
        'schedule': fields.List(fields.Nested(add_schedule_v3), required=True, description='schedule list'),
        'userid': fields.Integer(required=True, description='login user id'),
        'schedule_type': fields.Integer(required=True, description='login user id')
    })

    audit_log = api.model('audit_log_info', {
        'type': fields.String(required=True, description='audit_log_type'),
        'old_value': fields.String(required=True, description='audit_log_message'),
        'new_value': fields.String(required=True, description='audit_log_message')
    })

    update_schedule = api.model('update_schedule', {
        'schedule_id': fields.Integer(required=True, description='id of schedule'),
        'user_id': fields.Integer(required=True, description='user id of the RKP - delivery person'),
        'vehicle_id': fields.Integer(required=True, description='vehicle id chosen'),
        'schedule_status': fields.Integer(required=True, description='status of the schedule'),
        'rt_regn': fields.String(required=True, description='rt registration number'),
        'schedule_date': fields.String(required=True, description='schedule date'),
        'shipment_no': fields.String(required=True, description='shipment number'),
        'delivery_note_no': fields.String(required=True, description='delivery notes number'),
        'ship_to_party': fields.String(required=True, description='party to ship'),
        'loc': fields.String(required=True, description='loc'),
        'product': fields.String(required=True, description='product'),
        'dist': fields.String(required=True, description='distance for the trip'),
        'payment': fields.String(required=True, description='Payment amount for the schedule'),
        'Rg': fields.String(required=True, description='Rg'),
        'PLdTime': fields.String(required=True, description='PLdTime'),
        'Qty': fields.String(required=True, description='Qty'),
        'client': fields.String(required=True, description='client'),
        'audit_log':fields.List(fields.Nested(audit_log), required=True, description='audit log list')
    })

    update_schedule_v3 = api.model('update_schedule_v3', {
        'schedule_id': fields.Integer(required=True, description='id of schedule'),
        'user_id': fields.Integer(required=True, description='user id of the RKP - delivery person'),
        'vehicle_id': fields.Integer(required=True, description='vehicle id chosen'),
        'schedule_status': fields.Integer(required=True, description='status of the schedule'),
        'rt_regn': fields.String(required=True, description='rt registration number'),
        'dist': fields.String(required=True, description='distance for the trip'),
        'payment': fields.String(required=True, description='Payment amount for the schedule'),
        'audit_log': fields.List(fields.Nested(audit_log), required=True, description='audit log list'),

        'PlnStLdDt': fields.String(required=True, description='schedule date'),
        'Shipment': fields.String(required=True, description='shipment number'),
        'D Note': fields.String(required=True, description='delivery notes number'),
        'City': fields.String(required=True, description='loc'),
        'Material': fields.String(required=True, description='product'),
        'Rg': fields.String(required=True, description='Rg'),
        'T': fields.String(required=True, description='T'),
        'PLdTime': fields.String(required=True, description='PLdTime'),
        'Qty': fields.String(required=True, description='Qty'),
        'Name': fields.String(required=True, description='client'),
        'Plnt': fields.String(required=True, description='Plnt'),
        'SC': fields.String(required=True, description='SC'),
        'TransPlnDt': fields.String(required=True, description='TransPlnDt'),
        'Dlvr': fields.String(required=True, description='Dlvr'),
        'S': fields.String(required=True, description='S'),
        'ActStLdT': fields.String(required=True, description='ActStLdT'),
        'Ship-to': fields.String(required=True, description='Ship-to'),
        'Maximum volume': fields.String(required=True, description='Maximum volume'),
        'ETA time': fields.String(required=True, description='ETA time'),
        'Sold-to': fields.String(required=True, description='Sold-to'),
        'ShTy': fields.String(required=True, description='ShTy'),
    })

    update_schedule_detail = api.model('update_schedule_detail', {

        'updated_by': fields.Integer(required=True, description='technician_remarks'),
        'schedule_type': fields.Integer(required=True, description='schedule type'),
        'update_schedule': fields.List(fields.Nested(update_schedule), required=True,
                                          description='PDC Inspection list'),

    })

    update_schedule_detail_v3 = api.model('update_schedule_detail_v3', {

        'updated_by': fields.Integer(required=True, description='technician_remarks'),
        'schedule_type': fields.Integer(required=True, description='schedule type'),
        'update_schedule': fields.List(fields.Nested(update_schedule_v3), required=True,
                                       description='PDC Inspection list'),

    })

    schedule_list = api.model('schedule_list', {
        'schedule_id': fields.Integer(required=True, description='id of schedule'),
        'user_id': fields.Integer(required=True, description='user id of the RKP - delivery person'),
        'vehicle_id': fields.Integer(required=True, description='vehicle id chosen'),
        'schedule_status': fields.Integer(required=True, description='status of the schedule'),
        'rt_regn': fields.String(required=True, description='rt registration number'),
        'schedule_date': fields.String(required=True, description='schedule date'),
        'shipment_no': fields.String(required=True, description='shipment number'),
        'delivery_note_no': fields.String(required=True, description='delivery notes number'),
        'ship_to_party': fields.String(required=True, description='party to ship'),
        'loc': fields.String(required=True, description='loc'),
        'product': fields.String(required=True, description='product'),
        'dist': fields.String(required=True, description='distance for the trip'),
        'payment': fields.String(required=True, description='Payment amount for the schedule'),
        'Rg': fields.String(required=True, description='Rg'),
        'PLdTime': fields.String(required=True, description='PLdTime'),
        'Qty': fields.String(required=True, description='Qty'),
        'client': fields.String(required=True, description='client'),
        'created_by': fields.Integer(required=False, description='login user id'),
        'user_name': fields.String(required=False, description='user name'),
        'isRow_Editable': fields.Boolean(required=False, description='user name'),
        'version_no': fields.String(required=True, description='version_no')
    })

    res_schedule_info = api.model('res_schedule_info', {
        'ErrorCode': fields.String(required=True, description='Error code'),
        'count': fields.Integer(required=True, description='count'),
        'data': fields.List(fields.Nested(schedule_list), required=True, description='')
    })

    graph_filter = api.model('graph_filter', {
        'search':fields.String(required=True, description='search text'),
        'rkp': fields.Integer(required=True, description='user id of the RKP - delivery person'),
        'rt': fields.Integer(required=True, description='vehicle id chosen'),
        'date': fields.String(required=True, description='schedule date'),
        'loc': fields.String(required=True, description='loc'),
        'created_by': fields.Integer(required=False, description='login user id'),
    })
