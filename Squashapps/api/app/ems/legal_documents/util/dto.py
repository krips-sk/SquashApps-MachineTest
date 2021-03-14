from flask_restplus import Namespace, fields
obj= {
      "doc_id": 0,
      "doc_org_name": ""
    }
class Legal_DocumentsDto:
   api = Namespace('legal_documents', description='Legal Documents related operations')

   save_legaldocument = api.model('save_legaldocument', {
      'user_id': fields.Integer(required=True, description='User Id of Applied User'),
      'document_type': fields.String(required=True, description='Document Type'),
      'notice_content': fields.String(required=True, description='Notice Content'),
      'original_doc_name': fields.List(fields.Raw(obj), required=False, description='original names'),
      'uuid_doc_name': fields.List(fields.String(required=True, description='Original Doc Name'))
   })

   update_approver_status = api.model('update approver status ', {
      'user_id': fields.Integer(required=True, description='User Id of Applied User'),
      'approval_notes': fields.String(required=True, description='notes for the inspection'),
       'approved_by': fields.Integer(required=True, description='approver id'),
       'approval_status': fields.Integer(required=True, description='Status of the approval'),
      'passport_expiry_date':  fields.String(required=True, description='passport expiry date'),
      'base_pass_expiry_date':  fields.String(required=True, description='gdl expiry date'),

       # user details
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
       'created_by': fields.Integer(required=False, description='created_by')
   })