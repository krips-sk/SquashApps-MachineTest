from flask_restplus import Namespace, fields


class ClaimDto:
    api = Namespace('claim', description='claim related operations')
    claim_details = api.model('claim_details', {
        'detail_id':fields.Integer(required=True, description='detail_id'),
        'item': fields.String(required=True, description='claim item'),
        'description': fields.String(required=True, description='claim description'),
        'company_name': fields.String(required=True, description='company or retailer name'),
        'qty': fields.String(required=True, description='quantity'),
        'unit_price': fields.String(required=True, description='unit price'),
        'amount': fields.String(required=True, description='qty * unit price'),
        'file_path': fields.String(required=True, description='file_path')
    })
    claim_new = api.model('new claim', {
        'claim_id': fields.String(required=False, description='claim id'),
        'user_id': fields.String(required=False, description='user id'),
        'emp_id': fields.String(required=True, description='Employee id'),
        'loc': fields.String(required=True, description='Location'),
        'department': fields.String(required=True, description='department'),
        'claim_type': fields.String(required=True, description='claim type'),
        'claim_date': fields.String(required=True, description='claim date'),
        'status': fields.String(required=True, description='status'),
        'grand_total': fields.String(required=True, description='grand total'),
        'claim_details': fields.List(fields.Nested(claim_details), required=True, description='Claim Details list'),
        'created_by' :fields.String(required=True, description='created by')
    })

