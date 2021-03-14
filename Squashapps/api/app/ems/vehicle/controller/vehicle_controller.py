import logging

from flask_restplus import Resource
from flask import request
from ..service.vehicle_service import save_vehicle_details,get_vehicle_list,get_available_rt\
    ,get_expiring_rt,get_rt_details,get_rt_dashboardDetails,get_location_list,get_rt_serviceCount,get_rt_locationCount,rt_profile_upload,rt_profile_get
from ..util.dto import VehicleDto

api = VehicleDto.api
add_vehicle = VehicleDto.add_vehicle
get_autocmplt = VehicleDto.get_autocmplt
get_autocmplt_city = VehicleDto.get_autocmplt_city
fileupload = VehicleDto.fileupload
@api.route('/add/vehicle')
class RT_Details_Save(Resource):
    @api.doc("vehicle Registration")
    @api.expect(add_vehicle, validate=True)
    def post(self):
        try:
            data = request.json
            return save_vehicle_details(data)
        except Exception as e:
            print("Apply Leave controller error: " + str(e))
            logging.exception(e)

@api.route('/get_vehicle_list')
class GetScheduleList(Resource):
    @api.expect(get_autocmplt)
    @api.doc("Schedule List")
    #@token_required
    def post(self):
        data=request.json
        return get_vehicle_list(data)

@api.route('/get_available_rt/<page>/<row>/<search>/<int:tabindex>/<int:sortindex>/<rt_regn>/<schedule_date>')
class GetAvailableRt(Resource):
    @api.doc("Schedule List")
    #@token_required
    def get(self, page, row, search, tabindex, sortindex,rt_regn,schedule_date):
        return get_available_rt(page, row, search, tabindex, sortindex,rt_regn,schedule_date)

@api.route('/get_rt_info/<rt_regn>')
class GetAvailableRt(Resource):
    @api.doc("Schedule List")
    #@token_required
    def get(self,rt_regn):
        return get_rt_details(rt_regn)

@api.route('/expiring_vehcile_list')
class GetExpiringRt(Resource):
    @api.doc("Expire List")
    #@token_required
    def get(self):
        return get_expiring_rt()


@api.route('/get_rt_dashboardDetails/<regn_no>')
class getRTDashboardDetails(Resource):
    @api.doc("Expire List")
    #@token_required
    def get(self,regn_no):
        return get_rt_dashboardDetails(regn_no)


@api.route('/get_location_list')
class GetLocationList(Resource):
    @api.expect(get_autocmplt_city)
    @api.doc("Location List")
    #@token_required
    def post(self):
        data=request.json
        return get_location_list(data)

@api.route('/get_rt_serviceCount')
class getRTServiceCount(Resource):
    @api.doc("RT Service Details")
    #@token_required
    def get(self):
        return get_rt_serviceCount()

@api.route('/get_rt_locationCount')
class getRTLocationCount(Resource):
    @api.doc("RT Location Count")
    #@token_required
    def get(self):
        return get_rt_locationCount()

@api.route('/upload_profile_image')
class UpdateFile(Resource):
    @api.response(201, 'uploaded updated.')
    @api.expect(fileupload, validate=True)
    @api.doc('upload file')
    def post(self):
        """Upload File """
        # file = request.files['file']
        file=request.json['data']
        image_side = request.json['image_side']
        return rt_profile_upload(image_side, file)[0]

@api.route('/get_rt_image/<filename>')
class GetFile(Resource):
    @api.response(201, 'uploaded updated.')
    @api.doc('upload file')
    def get(self,filename):
       """Upload File """
       return rt_profile_get(filename)