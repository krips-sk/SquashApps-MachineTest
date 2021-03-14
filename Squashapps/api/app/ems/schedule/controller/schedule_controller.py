# Name: schedule_controller.py
# Description: used to schedule the RT with RKP.
# Author: Mycura
# Created: 2020.12.09
# Copyright: © 2020 EMS . All Rights Reserved.
# Change History:
#                |2020.12.09
from flask import request
from flask_restplus import Resource
from app.ems.schedule.sevice.schedule_service import add_schedule, add_multiple_schedule, delete_schedule, \
    get_by_id, get_schedule_list, get_rkp_schedule_list, get_rt_info_for_rkp, upload_doc, get_available_rkp, \
    get_total_distance, get_total_goods_delivered, get_delivery_status_station, get_delivery_status_product, \
    get_rt_latlang, get_status_summary, add_multiple_schedule_v1, get_schedule_list_v1, get_rkp_schedule_list_v1, \
    get_by_id_v1, delete_schedule_v1, get_rt_info_for_rkp_v1, get_total_distance_v1, get_total_goods_delivered_v1, \
    get_delivery_status_station_v1, get_delivery_status_product_v1, get_status_summary_v1, upload_doc_v2, \
    get_schedule_list_v2, \
    add_multiple_schedule_v2, update_schedule, get_schedule_type, get_rkp_schedule_list_v2, get_total_work_hrs, \
    get_delivery_note_graph,get_trip_pershipment, get_dashboard_schedule_list_v2,upload_doc_v3,add_multiple_schedule_v3,\
    update_schedule_v3,get_schedule_list_v3,get_rkp_schedule_list_v3,get_dashboard_schedule_list_v3,upload_doc_v4,get_rt_info_for_rkp_v2
from app.ems.schedule.util.dto import Scheduledto
from app.cura.user.util.decorator import token_required
from werkzeug.datastructures import FileStorage

api = Scheduledto.api
_add_schedule = Scheduledto.add_schedule
_delete_schedule = Scheduledto.delete_schedule
_add_multiple_schedule = Scheduledto.add_multiple_schedule
_add_multiple_schedule_v3 = Scheduledto.add_multiple_schedule_v3
_res_schedule_info = Scheduledto.res_schedule_info
_graph_filter = Scheduledto.graph_filter
_update_schedule = Scheduledto.update_schedule_detail
_update_schedule_v3 = Scheduledto.update_schedule_detail_v3
file_upload = api.parser()
file_upload.add_argument('file', location='files', type=FileStorage, required=True)



#
#   feat - Used to add/update the schedule for the RT and the RKP
#
@api.route('/v3/update_schedule')
class UpdateSchedule(Resource):
    @api.doc("Country add")
    @api.expect(_update_schedule_v3, validate=True)
    @api.response(200, "Schedule added successfully")
    # @token_required
    def post(self):
        data = request.json
        return update_schedule_v3(data)

#
#   feat - Used to add/update the schedule for the RT and the RKP
#
@api.route('/v2/update_schedule')
class UpdateSchedule(Resource):
    @api.doc("Country add")
    @api.expect(_update_schedule, validate=True)
    @api.response(200, "Schedule added successfully")
    # @token_required
    def post(self):
        data = request.json
        return update_schedule(data)


#
#   feat - Used to add/update the schedule for the RT and the RKP
#
@api.route('/add_schedule')
class AddSchedule(Resource):
    @api.doc("Country add")
    @api.expect(_add_schedule, validate=True)
    @api.response(200, "Schedule added successfully")
    # @token_required
    def post(self):
        data = request.json
        return add_schedule(data)


#
#   feat - Used to add/update multiple schedules
#
@api.route('/v1/add_multiple_schedule')
class AddMultipleSchedule(Resource):
    @api.doc("Schedule add")
    @api.expect(_add_multiple_schedule, validate=True)
    @api.response(200, "Multiple Schedule added successfully")
    # @token_required
    def post(self):
        data = request.json
        return add_multiple_schedule_v1(data)


#
#   feat - Used to add/update multiple schedules
#
@api.route('/add_multiple_schedule')
class AddMultipleSchedule(Resource):
    @api.doc("Schedule add")
    @api.expect(_add_multiple_schedule, validate=True)
    @api.response(200, "Multiple Schedule added successfully")
    # @token_required
    def post(self):
        data = request.json
        return add_multiple_schedule(data)


#
#   feat - Used to add/update multiple schedules
#
@api.route('/v2/add_multiple_schedule')
class AddMultipleSchedule(Resource):
    @api.doc("Schedule add")
    @api.expect(_add_multiple_schedule, validate=True)
    @api.response(200, "Multiple Schedule added successfully")
    # @token_required
    def post(self):
        data = request.json
        return add_multiple_schedule_v2(data)


#
#   feat - Used to add/update multiple schedules
#
@api.route('/v3/add_multiple_schedule')
class AddMultipleSchedule(Resource):
    @api.doc("Schedule add")
    @api.expect(_add_multiple_schedule_v3, validate=True)
    @api.response(200, "Multiple Schedule added successfully")
    # @token_required
    def post(self):
        data = request.json
        return add_multiple_schedule_v3(data)

#
#   feat - Used to get the list of schedule for the RT and the RKP
#
@api.route('/get_list/<page>/<row>/<search>/<int:tabindex>/<int:sortindex>/<schedule_date>')
class GetScheduleList(Resource):
    @api.doc("Schedule List")
    # @token_required
    @api.marshal_with(_res_schedule_info)
    def get(self, page, row, search, tabindex, sortindex, schedule_date):
        return get_schedule_list(page, row, search, tabindex, sortindex, schedule_date)


#
#   feat - Used to get the list of schedule for the RT and the RKP
#
@api.route('/v1/get_list/<page>/<row>/<search>/<int:tabindex>/<int:sortindex>/<schedule_date>')
class GetScheduleListV1(Resource):
    @api.doc("Schedule List")
    # @token_required
    @api.marshal_with(_res_schedule_info)
    def get(self, page, row, search, tabindex, sortindex, schedule_date):
        return get_schedule_list_v1(page, row, search, tabindex, sortindex, schedule_date)


#
#   feat - Used to get the list of schedule for the RT and the RKP
#
@api.route('/v2/get_list/<page>/<row>/<schedule_type>/<search>/<int:tabindex>/<int:sortindex>')
class GetScheduleListV2(Resource):
    @api.doc("Schedule List")
    # @token_required
    @api.marshal_with(_res_schedule_info)
    def get(self, page, row, schedule_type, search, tabindex, sortindex):
        return get_schedule_list_v2(page, row, schedule_type, search, tabindex, sortindex)


#
#   feat - Used to get the list of schedule for the RT and the RKP
#
@api.route('/v3/get_list/<page>/<row>/<schedule_type>/<search>/<int:tabindex>/<int:sortindex>/<date>')
class GetScheduleListV3(Resource):
    @api.doc("Schedule List")
    # @token_required
    def get(self, page, row, schedule_type, search, tabindex, sortindex,date):
        return get_schedule_list_v3(page, row, schedule_type, search, tabindex, sortindex,date)

#
#   feat - Used to get the list of schedule for for Dashboard page
#
@api.route('/v2/dashboard/get_list/<page>/<row>/<schedule_type>/<search>/<schedule_date>/<int:tabindex>/<int:sortindex>')
class GetScheduleListV2(Resource):
    @api.doc("Schedule List")
    # @token_required
    @api.marshal_with(_res_schedule_info)
    def get(self, page, row, schedule_type, search, schedule_date, tabindex, sortindex):
        return get_dashboard_schedule_list_v2(page, row, schedule_type, search, schedule_date, tabindex, sortindex)


#
#   feat - Used to get the list of schedule for for Dashboard page
#
@api.route('/v3/dashboard/get_list/<page>/<row>/<schedule_type>/<search>/<schedule_date>/<int:tabindex>/<int:sortindex>')
class GetScheduleListV2(Resource):
    @api.doc("Schedule List")
    # @token_required
    def get(self, page, row, schedule_type, search, schedule_date, tabindex, sortindex):
        return get_dashboard_schedule_list_v3(page, row, schedule_type, search, schedule_date, tabindex, sortindex)

#
#   feat - Used to get the list of schedule for the particular RKP
#
@api.route('/rkp/get_list/<int:user_id>/<page>/<row>/<search>/<int:tabindex>/<int:sortindex>')
class GetScheduleList(Resource):
    @api.doc("Schedule List")
    # @token_required
    @api.marshal_with(_res_schedule_info)
    def get(self, user_id, page, row, search, tabindex, sortindex):
        return get_rkp_schedule_list(user_id, page, row, search, tabindex, sortindex)


#
#   feat - Used to get the list of schedule for the particular RKP
#
@api.route('/v1/rkp/get_list/<int:user_id>/<page>/<row>/<search>/<int:tabindex>/<int:sortindex>')
class GetScheduleListV1(Resource):
    @api.doc("Schedule List")
    # @token_required
    @api.marshal_with(_res_schedule_info)
    def get(self, user_id, page, row, search, tabindex, sortindex):
        return get_rkp_schedule_list_v1(user_id, page, row, search, tabindex, sortindex)


#
#   feat - Used to get the list of schedule for the particular RKP
#
@api.route('/v2/rkp/get_list/<int:user_id>/<page>/<row>/<search>/<int:tabindex>/<int:sortindex>/<schedule_type>')
class GetScheduleListV1(Resource):
    @api.doc("Schedule List")
    # @token_required
    @api.marshal_with(_res_schedule_info)
    def get(self, user_id, page, row, search, tabindex, sortindex, schedule_type):
        return get_rkp_schedule_list_v2(user_id, page, row, search, tabindex, sortindex, schedule_type)


#
#   feat - Used to get the list of schedule for the particular RKP
#
@api.route('/v3/rkp/get_list/<int:user_id>/<page>/<row>/<search>/<int:tabindex>/<int:sortindex>/<schedule_type>')
class GetScheduleListV3(Resource):
    @api.doc("Schedule List")
    # @token_required
    def get(self, user_id, page, row, search, tabindex, sortindex, schedule_type):
        return get_rkp_schedule_list_v3(user_id, page, row, search, tabindex, sortindex, schedule_type)

#
#   feat - Used to get the particular schedule using the schedule id
#
@api.route('/get_by_id/<int:schedule_id>')
class GetScheduleById(Resource):
    @api.doc("Schedule get by id")
    # @token_required
    @api.marshal_with(_add_schedule)
    def get(self, schedule_id):
        return get_by_id(schedule_id)


#
#   feat - Used to get the particular schedule using the schedule id
#
@api.route('/v1/get_by_id/<int:schedule_id>')
class GetScheduleById(Resource):
    @api.doc("Schedule get by id")
    # @token_required
    @api.marshal_with(_add_schedule)
    def get(self, schedule_id):
        return get_by_id_v1(schedule_id)


#
#   feat - Used to delete the schedule using the schedule id
#
@api.route('/delete')
class DeleteSchedule(Resource):
    @api.doc("Country Delete")
    @api.expect(_delete_schedule, validate=True)
    @token_required
    def post(self):
        data = request.json
        return delete_schedule(data)


#
#   feat - Used to delete the schedule using the schedule id
#
@api.route('/v1/delete')
class DeleteScheduleV1(Resource):
    @api.doc("Country Delete")
    @api.expect(_delete_schedule, validate=True)
    def post(self):
        data = request.json
        return delete_schedule_v1(data)


#
#   feat - Used to get the RT information for the particular RKP
#
@api.route('/rkp/get_rt/<int:user_id>')
class GetRKPDefaultRTInfo(Resource):
    @api.doc("Schedule get by id")
    # @token_required
    def get(self, user_id):
        return get_rt_info_for_rkp(user_id)


#
#   feat - Used to get the RT information for the particular RKP
#
@api.route('/v1/rkp/get_rt/<int:user_id>')
class GetRKPDefaultRTInfoV1(Resource):
    @api.doc("Schedule get by id")
    # @token_required
    def get(self, user_id):
        return get_rt_info_for_rkp_v1(user_id)


#
#   feat - Used to get the RT information for the particular RKP
#
@api.route('/v2/rkp/get_rt/<user_id>/<rt_regn>')
class GetRKPDefaultRTInfoV2(Resource):
    @api.doc("Schedule get by id")
    # @token_required
    def get(self, user_id,rt_regn):
        return get_rt_info_for_rkp_v2(user_id,rt_regn)


#
#   feat - Used to get the RT information for the particular RKP
#
@api.route('/get_available_rkp/<page>/<row>/<search>/<int:tabindex>/<int:sortindex>/<int:user_id>/<schedule_detail_id>/<schedule_date>')
class GetAvailableRKP(Resource):
    @api.doc("Schedule get by id")
    # @token_required
    def get(self, page, row, search, tabindex, sortindex, user_id,schedule_detail_id,schedule_date):
        return get_available_rkp(page, row, search, tabindex, sortindex, user_id,schedule_detail_id,schedule_date)


@api.route('/upload_doc')
class UpdateFile(Resource):
    @api.response(201, 'uploaded updated.')
    @api.expect(file_upload)
    @api.doc('upload file')
    def post(self):
        """Upload File """
        # file = request.files['file']
        file = request.files
        return upload_doc(file['file'])


@api.route('/v2/upload_doc')
class UpdateFile(Resource):
    @api.response(201, 'uploaded updated.')
    @api.expect(file_upload)
    @api.doc('upload file')
    def post(self):
        """Upload File """
        # file = request.files['file']
        file = request.files
        return upload_doc_v2(file['file'])


@api.route('/v3/upload_doc')
class UpdateFile(Resource):
    @api.response(201, 'uploaded updated.')
    @api.expect(file_upload)
    @api.doc('upload file')
    def post(self):
        """Upload File """
        # file = request.files['file']
        file = request.files
        return upload_doc_v3(file['file'])


@api.route('/v4/upload_doc')
class UpdateFile(Resource):
    @api.response(201, 'uploaded updated.')
    @api.expect(file_upload)
    @api.doc('upload file')
    def post(self):
        """Upload File """
        # file = request.files['file']
        file = request.files
        return upload_doc_v4(file['file'])


@api.route('/graph/get_distance')
class GetTotalDistance(Resource):
    @api.response(201, 'get distance graph for operator module')
    @api.expect(_graph_filter)
    @api.doc('Get total distance graph')
    def post(self):
        """Upload File """
        data = request.json
        return get_total_distance(data)


@api.route('/v1/graph/get_distance')
class GetTotalDistance(Resource):
    @api.response(201, 'get distance graph for operator module')
    @api.expect(_graph_filter)
    @api.doc('Get total distance graph')
    def post(self):
        """Upload File """
        data = request.json
        return get_total_distance_v1(data)


@api.route('/graph/get_goods_delivered')
class GetTotalGoodsDelivered(Resource):
    @api.response(201, 'get total goods delivered graph for operator module')
    @api.expect(_graph_filter)
    @api.doc('Get total goods delivered graph')
    def post(self):
        """Upload File """
        data = request.json
        return get_total_goods_delivered(data)


@api.route('/v1/graph/get_goods_delivered')
class GetTotalGoodsDelivered(Resource):
    @api.response(201, 'get total goods delivered graph for operator module')
    @api.expect(_graph_filter)
    @api.doc('Get total goods delivered graph')
    def post(self):
        """Upload File """
        data = request.json
        return get_total_goods_delivered_v1(data)


@api.route('/graph/get_delivery_status_station')
class GetStationDeliveryStatus(Resource):
    @api.response(201, 'get delivery status based on station graph for operator module')
    @api.expect(_graph_filter)
    @api.doc('Get delivery status based on station graph')
    def post(self):
        """delivery status based on station Graph """
        data = request.json
        return get_delivery_status_station(data)


@api.route('/v1/graph/get_delivery_status_station')
class GetStationDeliveryStatus(Resource):
    @api.response(201, 'get delivery status based on station graph for operator module')
    @api.expect(_graph_filter)
    @api.doc('Get delivery status based on station graph')
    def post(self):
        """delivery status based on station Graph """
        data = request.json
        return get_delivery_status_station_v1(data)


@api.route('/graph/get_delivery_status_product')
class GetProductDeliveryStatus(Resource):
    @api.response(201, 'get delivery status based on product graph for operator module')
    @api.expect(_graph_filter)
    @api.doc('Get delivery status based on product graph')
    def post(self):
        """delivery status based on product Graph """
        data = request.json
        return get_delivery_status_product(data)


@api.route('/v1/graph/get_delivery_status_product')
class GetProductDeliveryStatusV1(Resource):
    @api.response(201, 'get delivery status based on product graph for operator module v1')
    @api.expect(_graph_filter)
    @api.doc('Get delivery status based on product graph v1')
    def post(self):
        """delivery status based on product Graph """
        data = request.json
        return get_delivery_status_product_v1(data)


@api.route('/get_rt_lat_lang')
class GetRTLatLang(Resource):
    @api.doc("Schedule get by id")
    # @token_required
    def get(self):
        return get_rt_latlang()


@api.route('/get_status_summary')
class GetStatusSummary(Resource):
    @api.doc("get status summary for operation module")
    # @token_required
    def get(self):
        return get_status_summary()


@api.route('/v1/get_status_summary')
class GetStatusSummary(Resource):
    @api.doc("get status summary for operation module")
    # @token_required
    def get(self):
        return get_status_summary_v1()


@api.route('/get_schedule_type')
class GetScheduleType(Resource):
    @api.doc("get schedule type for operation module")
    # @token_required
    def get(self):
        return get_schedule_type()


@api.route('/graph/get_work_hrs')
class GetWorkHrs(Resource):
    @api.response(201, 'get work hrs graph for operator module')
    @api.expect(_graph_filter)
    @api.doc('Get total work hrs graph')
    def post(self):
        """Upload File """
        data = request.json
        return get_total_work_hrs(data)


@api.route('/graph/get_delivery_note')
class GetDeliveryNote(Resource):
    @api.response(201, 'get delivery note graph for operator module')
    @api.expect(_graph_filter)
    @api.doc('Get delivery note hrs graph')
    def post(self):
        """Upload File """
        data = request.json
        return get_delivery_note_graph(data)

@api.route('/graph/trip_pershipment')
class GetTripPershipment(Resource):
    @api.response(201, 'get total trip perday by product')
    @api.expect(_graph_filter)
    @api.doc('get total trip perday by product')
    def post(self):
        """Upload File """
        data = request.json
        return get_trip_pershipment(data)