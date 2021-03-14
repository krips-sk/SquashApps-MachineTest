from flask_restplus import Namespace, fields

bank_insurance = {
        "policy": "string",
        "loc": "string",
        "ref_no": "string",
        "due_date": "datetime",
        "bank_or_insurer": "string",
        "amount": "string",
        "remarks": "string",
        "types": "string"
    }
class VehicleDto:
   api = Namespace('Vehicle', description='Vehicle related operations')

   # bank_insurance = api.model('bank_insurance', {
   #     'policy': fields.String,
   #     'loc': fields.String,
   #     'ref_no': fields.String,
   #     'bank_or_insurer': fields.String,
   #     'due_date': fields.DateTime(dt_format='rfc822'),
   #     'amount': fields.String,
   #     'remarks': fields.String,
   #     'types': fields.String,
   # })
   add_vehicle = api.model('add_vehicle', {
        'user_id':fields.Integer(required=False),
       'vehicle_id': fields.Integer(required=False),
      'model' : fields.String(required=False),
      'commissioned_date' : fields.String(required=False),
      'regn_date' : fields.String(required=False),
      'chassis_no' : fields.String(required=False),
      'regn_no' : fields.String(required=False),
      'engine_no' : fields.String(required=False),
      'engine_capacity': fields.String(required=False),
      'engine_fuel_type': fields.String(required=False),
      'trailer_regn' : fields.String(required=False),
      'trailer_model' : fields.String(required=False),
      'trailer_type' : fields.String(required=False),
      'weight_category_bdm' : fields.String(required=False),
      'weight_category_btm' : fields.String(required=False),
      'weight_category_bt1' : fields.String(required=False),
      'ld_road_tax' : fields.String(required=False),
      'ld_puspakom' : fields.String(required=False),
      'ld_insurance' : fields.String(required=False),
      'pump_fitted' : fields.String(required=False),
      'top_loading' : fields.String(required=False),
      'pto_equip' : fields.String(required=False),
      'bottom_load' : fields.String(required=False),
        'location':fields.String(required=False),
      'bank_insurance':fields.List(fields.Raw(bank_insurance),required=False),
       'client_name': fields.String(required=False),
       'color_scheme': fields.String(required=False),
       'front': fields.String(required=False),
       'rear': fields.String(required=False),
       'starboard': fields.String(required=False),
       'port': fields.String(required=False)
   })
   get_autocmplt=api.model('get rt list', {
       'search_text': fields.String(required=False),
   })

   get_autocmplt_city = api.model('get city list', {
       'city': fields.String(required=False),
   })

   fileupload = api.model('fileupload', {
       'data': fields.String(required=True, description='Base64 image data to upload.'),
       'image_side': fields.String(required=True, description='image side')
   })