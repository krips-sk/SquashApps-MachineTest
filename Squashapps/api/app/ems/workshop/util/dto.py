from flask_restplus import Namespace, fields
from werkzeug.datastructures import FileStorage

total_availability = {}


class Wrokshopdto:
    api = Namespace('workshop', description='Workshop related operations')
    inspection = api.model('inspection', {
        'inspection_id': fields.Integer(required=False, description='id of pdc inspection item'),
        'inspections_defects': fields.String(required=True, description='inspections_defects'),
        'technician_remarks': fields.String(required=True, description='technician_remarks'),
        'workshop_status': fields.String(required=True, description='workshop_status')
    })

    add_adhoc = api.model('add_adhoc', {
        'adhoc_breakdown_id': fields.Integer(required=True, description='id of pdc registration'),
        'date_in': fields.String(required=True, description='notes for the inspection'),
        'mechanic': fields.String(required=True, description='notes for the inspection'),
        'supervisor': fields.String(required=True, description='notes for the inspection'),
        'mileage': fields.String(required=True, description='notes for the inspection'),
        'next_due': fields.String(required=True, description='notes for the inspection'),
        'rt_regn': fields.String(required=True, description='notes for the inspection'),
        'date_in': fields.String(required=True, description='notes for the inspection'),
        'trailer_regn': fields.String(required=True, description='schedule_id for doing pdc'),
        'inspection': fields.List(fields.Nested(inspection), required=True, description='PDC Inspection list'),
        'created_by': fields.Integer(required=False, description='login user id'),
    })

    add_schedule_maintenance = api.model('add_schedule_maintenance', {
        'scheduled_maintenance_id': fields.Integer(required=True, description='id of pdc registration'),
        'date_in': fields.String(required=True, description='notes for the inspection'),
        'mechanic': fields.String(required=True, description='notes for the inspection'),
        'supervisor': fields.String(required=True, description='notes for the inspection'),
        'mileage': fields.String(required=True, description='notes for the inspection'),
        'next_due': fields.String(required=True, description='notes for the inspection'),
        'rt_regn': fields.String(required=True, description='notes for the inspection'),
        'date_in': fields.String(required=True, description='notes for the inspection'),
        'trailer_regn': fields.String(required=True, description='schedule_id for doing pdc'),
        'inspection': fields.List(fields.Nested(inspection), required=True, description='PDC Inspection list'),
        'created_by': fields.Integer(required=False, description='login user id'),
    })

    delete_adhoc = api.model('delete_adhoc', {
        'adhoc_breakdown_id': fields.Integer(required=True, description='id of audit log'),
        'userid': fields.Integer(required=True, description='login user id')
    })
    res_adhoc_info = api.model('res_adhoc_info', {
        'ErrorCode': fields.String(required=True, description='Error code'),
        'count': fields.Integer(required=True, description='count'),
        'data': fields.List(fields.Nested(add_adhoc), required=True, description='')
    })

    repair_status_save = api.model('repair_status_save', {
        'repair_status_id': fields.Integer(required=True, description='id of pdc registration'),
        'repair_status_type': fields.String(required=True, description='notes for the inspection'),
        'date_in': fields.String(required=True, description='notes for the inspection'),
        'date_out': fields.String(required=True, description='notes for the inspection'),
        'mechanic': fields.String(required=True, description='notes for the inspection'),
        'supervisor': fields.String(required=True, description='notes for the inspection'),
        'mileage': fields.String(required=True, description='notes for the inspection'),
        'next_due': fields.String(required=True, description='notes for the inspection'),
        'rt_regn': fields.String(required=True, description='notes for the inspection'),
        'trailer_regn': fields.String(required=True, description='schedule_id for doing pdc'),
        'inspection': fields.List(fields.Nested(inspection), required=True, description='PDC Inspection list'),
        'remarks': fields.String(required=True, description='login user id'),

        'repair_overhaul': fields.String(required=True, description='login user id'),
        'welding_shop': fields.String(required=True, description='login user id'),
        'tyre_shop': fields.String(required=True, description='login user id'),

        'brake_lining_pad_thickness_pm': fields.List(fields.Raw(total_availability), required=False,
                                                     description='variable_details'),
        'brake_lining_pad_thickness_trailer': fields.List(fields.Raw(total_availability), required=False,
                                                          description='variable_details'),
        'clutch_Details_info': fields.List(fields.Raw(total_availability), required=False,
                                           description='variable_details'),
        'created_by': fields.Integer(required=False, description='login user id'),
    })

    inspection_defects = api.model('inspection_defects', {
        'inspection_id': fields.Integer(required=False, description='id of pdc inspection item'),
        'workshop_action': fields.String(required=True, description='workshop_status'),
        'date_in': fields.String(required=True, description='technician_remarks'),
        'date_out': fields.String(required=True, description='technician_remarks'),
        'approval_category': fields.String(required=True, description='technician_remarks'),
        'workshop_status': fields.String(required=True, description='technician_remarks'),
        'supervisor': fields.String(required=True, description='supervisor name'),
        'mechanic': fields.String(required=True, description='mechanic name'),
    })

    update_pdc_defects = api.model('repair_status_info', {

        'updated_by': fields.Integer(required=True, description='technician_remarks'),
        'inspection_defects': fields.List(fields.Nested(inspection_defects), required=True,
                                          description='PDC Inspection list'),

    })

    job_excel_upload = api.parser()
    job_excel_upload.add_argument('file', type=FileStorage, location='files')
    job_excel_upload.add_argument('date', location='args', help='Year to generate report')
    job_excel_upload.add_argument('user_id', location='args', help='user id')
    job_excel_upload.add_argument('report_type', location='args', help='type of report')

    corrective_report_filter = api.model('corrective_report_filter', {
        'supplier_id': fields.Integer(required=True, description='id of the supplier'),
        'department_id': fields.Integer(required=True, description='id of the department'),
        'report_date': fields.String(required=True, description='filter date'),
        'description': fields.String(required=True, description='description to filter')
    })

    workshop_part_list = api.model('workshop_part_list', {
        'parts_id': fields.Integer(required=True, description='id of the supplier'),
        'parts': fields.String(required=True, description='name of part'),
        'parts_no': fields.String(required=True, description='parts no for ref'),
        'quantity': fields.String(required=True, description='quantity to parts'),
        'isActive': fields.Integer(required=False, description='Active status of the parts')
    })

    workshop_action_list = api.model('workshop_action_list', {
        'action_id': fields.Integer(required=True, description='id of the supplier'),
        'description': fields.String(required=True, description='description of action'),
        'status': fields.String(required=True, description='status of action'),
        'isActive': fields.Integer(required=False, description='Active status of the action')
    })

    combinePartsAction = api.model('combinePartsAction', {
        'parts_list': fields.List(fields.Nested(workshop_part_list), required=True, description=''),
        'actions_list': fields.List(fields.Nested(workshop_action_list), required=True, description=''),
    })

    getlist_workaction = api.model('getlist_workaction', {
        'ErrorCode': fields.String(required=True, description='status of process'),
        'parts_count': fields.Integer(required=True, description='Count of parts table items'),
        'actions_count': fields.Integer(required=True, description='Count of action table items'),
        'data': fields.List(fields.Nested(combinePartsAction), required=True, description='')
    })

    save_workaction = api.model('save_workaction', {
        'pdcregistration_reference_id': fields.Integer(required=True, description='id of PDC registration'),
        'inspection_id': fields.Integer(required=True, description='id of inspection'),
        'regn_no': fields.String(required=True, description='regn no of vehicle'),
        'workshop_parts': fields.List(fields.Nested(workshop_part_list), validate=True, description="data for parts table"),
        'workshop_actions': fields.List(fields.Nested(workshop_action_list), validate=True, description="data for action table"),
        'updated_by': fields.Integer(required=True, description='Updated user id')
    })