from flask_restplus import Namespace, fields

class Leave_ManagementDto:
   api = Namespace('leave_management', description='Leave Management related operations')

   applyLeave = api.model('applyLeave', {
      'leave_id': fields.Integer(required=True, description='Leave Id of Applied User'),
      'user_id': fields.Integer(required=True, description='User Id of Applied User'),
      'from_date': fields.String(required=True, description='Leave Start Date'),
      'to_date': fields.String(required=True, description='Leave From Date'),
      'days_of_leave': fields.Integer(required=True, description='No of Days Leave'),
      'leave_type': fields.String(required=True, description='Type of Leave'),
      'leave_save_type':fields.Integer(required=True, description='Leave Application Approve Type'),
      'reason': fields.String(required=True, description='Reason for leave'),
      'file_name': fields.String(required=True, description='Uploaded file name'),
      'is_after_leave_taken': fields.Integer(required=True, description='is after leave taken'),
   })

   approveLeave = api.model('approveLeave', {
      'leave_id': fields.Integer(required=True, description='Leave Id of Applied User'),
      'user_id': fields.Integer(required=True, description='User Id of Applied User'),
      'status': fields.Integer(required=True, description='Leave Start Date'),
      'updated_by': fields.Integer(required=True, description='Leave Start Date'),
      'type': fields.Integer(required=True, description='Approver Type'),
   })

   updateleave_count = api.model('updateleave_count', {
      'entitle_leave': fields.Integer(required=True, description='entitle leave of Applied User'),
      'entitle_medical_leave': fields.Integer(required=True, description='entitle medical leave of Applied User'),
      'user_id': fields.Integer(required=True, description='user id'),
      'year': fields.String(required=True, description='year'),
   })

   add_medicalclaim = api.model('add_medicalclaim', {
      'claim_id': fields.Integer(required=True, description='medical claim id'),
      'medical_date': fields.String(required=True, description='medical date claim'),
      'claim_type': fields.String(required=True, description='claim type'),
      'claim_amount': fields.String(required=True, description='claim amount'),
      'clinic_name': fields.String(required=True, description='clinic name'),
      'user_id': fields.Integer(required=True, description='user id'),
      'ori_file_name':fields.String(required=True, description='ori_file_name'),
      'uuid_file_name':fields.String(required=True, description='uuid_file_name')
   })

   delete_medical_claim = api.model('delete_medical_claim', {
      'claim_id': fields.Integer(required=True, description='id of claim'),
      'user_id': fields.Integer(required=True, description='login user id')
   })

   updatemediclaimsummary = api.model('updatemediclaimsummary', {
      'entitle_claim': fields.String(required=True, description='entitle leave of Applied User'),
      'user_id': fields.Integer(required=True, description='user id'),
      'year': fields.String(required=True, description='year'),
   })