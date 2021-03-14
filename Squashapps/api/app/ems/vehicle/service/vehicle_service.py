import logging
from app.cura import db
from datetime import datetime

from app.cura.common import common
from ..model.vehicle import Vehicle

from ..model.insurance import Insurance
from ..model.location import Location
import uuid
from sqlalchemy import func, text, cast, Date, asc, desc
from sqlalchemy import and_, or_
from ...schedule.model.Schedule import Schedule

from ...predeparture.model.InspectionItem import InspectionItem
from ...predeparture.model.PDCRegistration import PDCRegistration
from app.ems import config
import os
import uuid
import base64
from flask import send_from_directory

def save_vehicle_details(data):
    try:
        vehicle = Vehicle.query.filter(Vehicle.id == data['vehicle_id'], Vehicle.isActive == 1).first()
        if not vehicle:

            vehicle_already_exists = Vehicle.query.filter(Vehicle.regn_no == data['regn_no'], Vehicle.isActive == 1).first()

            if not vehicle_already_exists:
                public_id = str(uuid.uuid4())
                new_vehicle = Vehicle(
                    public_id=public_id,
                    model=data["model"],
                    chassis_no=data["chassis_no"],
                    regn_no=data["regn_no"],
                    engine_no=data["engine_no"],
                    engine_capacity=data["engine_capacity"],
                    engine_fuel_type=data["engine_fuel_type"],
                    trailer_regn=data["trailer_regn"],
                    trailer_model=data["trailer_model"],
                    trailer_type=data["trailer_type"],
                    weight_category_bdm=data["weight_category_bdm"],
                    weight_category_btm=data["weight_category_btm"],
                    weight_category_bt1=data["weight_category_bt1"],
                    pump_fitted=data["pump_fitted"],
                    top_loading=data["top_loading"],
                    pto_equip=data["pto_equip"],
                    bottom_load=data["bottom_load"],
                    created_by=data["user_id"],
                    created_date=datetime.utcnow(),
                    isActive=1,
                    location=data['location'],
                    client_name=data["client_name"],
                    color_scheme=data["color_scheme"],
                    front=data["front"],
                    rear=data["rear"],
                    starboard=data["starboard"],
                    port=data["port"]

                )
                if data["regn_date"] != "":
                    data["regn_date"] = common.convertdmy_to_date2(data["regn_date"])
                    new_vehicle.regn_date = data["regn_date"]
                if data["commissioned_date"] != "":
                    data["commissioned_date"] = common.convertdmy_to_date2(data["commissioned_date"])
                    new_vehicle.commissioned_date = data["commissioned_date"]

                if data["ld_road_tax"] != "":
                    new_vehicle.ld_road_tax = data["ld_road_tax"]
                if data["ld_puspakom"] != "":
                    new_vehicle.ld_puspakom = data["ld_puspakom"]
                if data["ld_insurance"] != "":
                    new_vehicle.ld_insurance = data["ld_insurance"]

                save_changes(new_vehicle)
                vehicle_id = new_vehicle.id
                for item in data['bank_insurance']:
                    new_Insurance = Insurance(
                        public_id=str(uuid.uuid4()),
                        vehicle_id=vehicle_id,
                        policy=item['policy'],
                        loc=item['loc'],
                        ref_no=item['ref_no'],
                        bank_or_insurer=item['bank_or_insurer'],
                        amount=item['amount'],
                        remarks=item['remarks'],
                        types=item['types'],
                        created_by=data["user_id"],
                        created_date=datetime.utcnow(),
                        isActive=1
                    )
                    if item['due_date'] != "":
                        item['due_date'] = common.convertdmy_to_date2(item["due_date"])
                        new_Insurance.due_date = item['due_date']
                    save_changes(new_Insurance)

                response_obj = {
                    "message": "Vehicle Added Successfully",
                    "vehicle_id": vehicle_id,
                    "Errorcode": 9999
                }
            else:
                response_obj = {
                    "message": "Vehicle Regn No Already Exists",
                    "vehicle_id": 0,
                    "Errorcode": 9997
                }

        else:
            vehicle.model = data["model"],
            if data["regn_date"] != "":
                vehicle.regn_date = common.convertdmy_to_date2(data["regn_date"])
            if data["commissioned_date"] != "":
                vehicle.commissioned_date = common.convertdmy_to_date2(data["commissioned_date"])
            vehicle.chassis_no = data["chassis_no"],
            vehicle.regn_no = data["regn_no"],
            vehicle.engine_no = data["engine_no"],
            vehicle.engine_capacity = data["engine_capacity"],
            vehicle.engine_fuel_type = data["engine_fuel_type"],
            vehicle.trailer_regn = data["trailer_regn"],
            vehicle.trailer_model = data["trailer_model"],
            vehicle.trailer_type = data["trailer_type"],
            vehicle.weight_category_bdm = data["weight_category_bdm"],
            vehicle.weight_category_btm = data["weight_category_btm"],
            vehicle.weight_category_bt1 = data["weight_category_bt1"],
            vehicle.client_name = data["client_name"],
            vehicle.color_scheme = data["color_scheme"],
            vehicle.front = data["front"],
            vehicle.rear = data["rear"],
            vehicle.starboard = data["starboard"],
            vehicle.port = data["port"]

            if data["ld_road_tax"] != "":
                vehicle.ld_road_tax = data["ld_road_tax"]
            if data["ld_puspakom"] != "":
                vehicle.ld_puspakom = data["ld_puspakom"]
            if data["ld_insurance"] != "":
                vehicle.ld_insurance = data["ld_insurance"]

            vehicle.pump_fitted = data["pump_fitted"],
            vehicle.top_loading = data["top_loading"],
            vehicle.pto_equip = data["pto_equip"],
            vehicle.bottom_load = data["bottom_load"],
            vehicle.updated_date = datetime.utcnow(),
            vehicle.location = data['location']
            save_changes(vehicle)
            # update query
            # .update({Insurance.isActive: 0})
            insur = Insurance.query.filter(Insurance.vehicle_id == vehicle.id, Insurance.isActive == 1).all()
            if insur:
                for item in insur:
                    item.isActive = 0
                    save_changes(item)
            for item in data['bank_insurance']:
                new_Insurance = Insurance(
                    public_id=str(uuid.uuid4()),
                    vehicle_id=vehicle.id,
                    policy=item['policy'],
                    loc=item['loc'],
                    ref_no=item['ref_no'],
                    bank_or_insurer=item['bank_or_insurer'],
                    amount=item['amount'],
                    remarks=item['remarks'],
                    types=item['types'],
                    created_by=data["user_id"],
                    created_date=datetime.utcnow(),
                    isActive=1
                )
                if item['due_date'] != "":
                    item['due_date'] = common.convertdmy_to_date2(item["due_date"])
                    new_Insurance.due_date = item['due_date']
                save_changes(new_Insurance)
            response_obj = {
                "message": "Vehicle Updated Successfully",
                "vehicle_id": vehicle.id,
                "Errorcode": 9999
            }
        return response_obj

    except Exception as e:
        print("Leave Applied service error: " + str(e))
        logging.exception(e)
        response_obj = {
            "message": "Failed to save",
            "Errorcode": 9998
        }
        return response_obj


def get_vehicle_list(data):
    try:
        return_list = []
        list_query = Vehicle.query.filter(Vehicle.isActive == 1)
        if data['search_text'] != "":
            search = "%{}%".format(data['search_text'])
            list_query = list_query.filter(or_(Vehicle.regn_no.ilike(search), Vehicle.location.ilike(search)))


        rt = list_query.all()
        for item in rt:
            rt = {}
            rt['model'] = item.model
            rt['regn_no'] = item.regn_no
            return_list.append(rt)
        response_obj = {
            "Errorcode": 9999,
            "List": return_list
        }
        return response_obj
    except Exception as e:
        print(e)


def get_rt_details(regn_no):
    try:
        item = Vehicle.query.filter(Vehicle.regn_no == regn_no, Vehicle.isActive == 1).first()
        rt = {}
        bank_insur = []
        if item:
            rt['bottom_load'] = 2 if item.bottom_load == None else item.bottom_load
            rt['chassis_no'] = '' if item.chassis_no == None else item.chassis_no
            rt['commissioned_date'] = "" if (
                    item.commissioned_date == '' or item.commissioned_date == None) else item.commissioned_date.strftime(
                '%d-%m-%Y')
            rt['engine_capacity'] = '' if item.engine_capacity == None else item.engine_capacity
            rt['engine_fuel_type'] = '' if item.engine_fuel_type == None else item.engine_fuel_type
            rt['engine_no'] = '' if item.engine_no == None else item.engine_no
            rt['id'] = item.id
            rt['ld_insurance'] = '' if item.ld_insurance == None else item.ld_insurance
            rt['ld_puspakom'] = '' if item.ld_puspakom == None else item.ld_puspakom
            rt['ld_road_tax'] = '' if item.ld_road_tax == None else item.ld_road_tax
            rt['model'] = '' if item.model == None else item.model
            rt['pto_equip'] = 2 if item.pto_equip == None else item.pto_equip
            rt['public_id'] = item.public_id
            rt['pump_fitted'] = 2 if item.pump_fitted== None else item.pump_fitted
            rt['regn_date'] = "" if (item.regn_date == '' or item.regn_date == None) else item.regn_date.strftime(
                '%d-%m-%Y')
            rt['regn_no'] = '' if item.regn_no == None else item.regn_no
            rt['top_loading'] = 2 if item.top_loading == None else item.top_loading
            rt['trailer_model'] = '' if item.trailer_model == None else item.trailer_model
            rt['trailer_regn'] = '' if item.trailer_regn == None else item.trailer_regn
            rt['trailer_type'] = '' if item.trailer_type == None else item.trailer_type
            rt['weight_category_bdm'] = '' if item.weight_category_bdm == None else item.weight_category_bdm
            rt['weight_category_bt1'] =  '' if item.weight_category_bt1 == None else item.weight_category_bt1
            rt['weight_category_btm'] = '' if item.weight_category_btm == None else item.weight_category_btm
            rt['location'] = '' if item.location == None else item.location
            rt['client_name'] = '' if item.client_name == None else item.client_name
            rt['color_scheme'] = '' if item.color_scheme == None else item.color_scheme
            rt['front'] = '' if item.front == None else item.front
            rt['rear'] = '' if item.rear == None else item.rear
            rt['starboard'] = '' if item.starboard == None else item.starboard
            rt['port'] = '' if item.port == None else item.port

            insur = Insurance.query.filter(Insurance.vehicle_id == item.id, Insurance.isActive == 1).all()
            if insur:
                for insur_det in insur:
                    temp = {}
                    temp['amount'] = str(round(insur_det.amount,2))
                    temp['bank_or_insurer'] = insur_det.bank_or_insurer
                    temp['due_date'] = "" if (
                            insur_det.due_date == '' or insur_det.due_date == None) else insur_det.due_date.strftime(
                        '%d-%m-%Y')
                    temp['loc'] = insur_det.loc
                    temp['policy'] = insur_det.policy
                    temp['ref_no'] = insur_det.ref_no
                    temp['remarks'] = insur_det.remarks
                    temp['types'] = insur_det.types
                    bank_insur.append(temp)
            rt['bank_insur'] = bank_insur
        response_object = {
            'vehicle': rt,
            'status': 'success',
            'error_code': 9999
        }
        return response_object
    except Exception as e:
        logging.exception(e)
        response_obj = {
            "error_code": 0000,
            'status': 'error',
            "vehicle": {}
        }
        return response_obj


def get_available_rt(page, row, searchterm, tabindex, sortindex,rt_regn,schedule_date):
    try:

        from sqlalchemy.ext.serializer import loads, dumps
        return_list = []
        rt_query = Vehicle.query.filter(Vehicle.isActive == 1)


        if searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            rt_query = rt_query.filter(or_(Vehicle.chassis_no.ilike(search),
                                           Vehicle.regn_no.ilike(search)
                                           ))
            #Vehicle.bottom_load.ilike(search)

        # Sorting functionality
        if tabindex == 1:
            if sortindex == 1:
                rt_query = rt_query.order_by(asc(Vehicle.regn_no))
            else:
                rt_query = rt_query.order_by(desc(Vehicle.regn_no))
        elif tabindex == 2:
            if sortindex == 1:
                rt_query = rt_query.order_by(asc(Vehicle.engine_capacity))
            else:
                rt_query = rt_query.order_by(desc(Vehicle.engine_capacity))
        elif tabindex == 3:
            if sortindex == 1:
                rt_query = rt_query.order_by(asc(Vehicle.ld_road_tax))
            else:
                rt_query = rt_query.order_by(desc(Vehicle.ld_road_tax))
        elif tabindex == 4:
            if sortindex == 1:
                rt_query = rt_query.order_by(asc(Vehicle.ld_insurance))
            else:
                rt_query = rt_query.order_by(desc(Vehicle.ld_insurance))
        elif tabindex == 5:
            if sortindex == 1:
                rt_query = rt_query.order_by(asc(Vehicle.ld_puspakom))
            else:
                rt_query = rt_query.order_by(desc(Vehicle.ld_puspakom))
        else:
            rt_query = rt_query.order_by(desc(Vehicle.id))


        if rt_regn!="" and rt_regn!="\"\"":
            rt_query = rt_query.filter(or_(~Schedule.query.filter(Schedule.isActive==1,Schedule.schedule_date==common.convertdmy_to_date2(schedule_date),Schedule.rt_regn==Vehicle.regn_no).exists(),
                                   Vehicle.regn_no==rt_regn))

        rt = rt_query.paginate(int(page), int(row), False).items
        count = rt_query.count()

        for item in rt:
            rt = {}
            rt['bottom_load'] = item.bottom_load
            rt['chassis_no'] = item.chassis_no
            rt['commissioned_date'] = str(item.commissioned_date)
            rt['engine_capacity'] = item.engine_capacity
            rt['engine_fuel_type'] = item.engine_fuel_type
            rt['engine_no'] = item.engine_no
            rt['id'] = item.id
            rt['ld_insurance'] = item.ld_insurance
            rt['ld_puspakom'] = item.ld_puspakom
            rt['ld_road_tax'] = item.ld_road_tax
            rt['model'] = item.model
            rt['pto_equip'] = item.pto_equip
            rt['public_id'] = item.public_id
            rt['pump_fitted'] = item.pump_fitted
            rt['regn_date'] = str(item.regn_date)
            rt['regn_no'] = item.regn_no
            rt['top_loading'] = item.top_loading
            rt['trailer_model'] = item.trailer_model
            rt['trailer_regn'] = item.trailer_regn
            rt['trailer_type'] = item.trailer_type
            rt['weight_category_bdm'] = item.weight_category_bdm
            rt['weight_category_bt1'] = item.weight_category_bt1
            rt['weight_category_btm'] = item.weight_category_btm
            rt['location'] = item.location

            return_list.append(rt)
        response_obj = {
            "Errorcode": 9999,
            "List": return_list,
            "count": count
        }
        return response_obj
    except Exception as e:
        response_obj = {
            "Errorcode": "0000",
            "List": [],
            "count": 0,
            "Error": str(e)
        }
        return response_obj


def get_expiring_rt():
    try:
        return_list = []
        rt = Vehicle.query.filter(
            Vehicle.isActive == 1,
            and_(or_(func.date_part('day', cast(Vehicle.ld_insurance, Date) - datetime.utcnow()) < 6,
                     func.date_part('day', cast(Vehicle.ld_road_tax, Date) - datetime.utcnow()) < 6,
                     func.date_part('day', cast(Vehicle.ld_puspakom, Date) - datetime.utcnow()) < 6))).all()

        for item in rt:

            if item.ld_insurance != None:
                if (datetime.strptime(item.ld_insurance, '%Y-%m-%d') - datetime.today()).days < 6:
                    rt = {}
                    rt['regn_date'] = str(item.regn_date)
                    rt['regn_no'] = item.regn_no
                    rt['document_name'] = "Insurance"
                    rt['days'] = (datetime.strptime(item.ld_insurance, '%Y-%m-%d') - datetime.today()).days
                    return_list.append(rt)

            if item.ld_puspakom != None:
                if (datetime.strptime(item.ld_puspakom, '%Y-%m-%d') - datetime.today()).days < 6:
                    rt = {}
                    rt['regn_date'] = str(item.regn_date)
                    rt['regn_no'] = item.regn_no
                    rt['document_name'] = "Puspakom"
                    rt['days'] = (datetime.strptime(item.ld_puspakom, '%Y-%m-%d') - datetime.today()).days
                    return_list.append(rt)

            if item.ld_road_tax != None:
                if (datetime.strptime(item.ld_road_tax, '%Y-%m-%d') - datetime.today()).days < 6:
                    rt = {}
                    rt['regn_date'] = str(item.regn_date)
                    rt['regn_no'] = item.regn_no
                    rt['document_name'] = "Road Tax"
                    rt['days'] = (datetime.strptime(item.ld_road_tax, '%Y-%m-%d') - datetime.today()).days
                    return_list.append(rt)

        response_obj = {
            "Errorcode": 9999,
            "List": return_list
        }
        return response_obj
    except Exception as e:
        logging.exception(e)
        response_obj = {
            "Errorcode": 0000,
            "List": []
        }
        return response_obj


def get_rt_dashboardDetails(regn_no):
    try:
        item = Vehicle.query.filter(Vehicle.regn_no == regn_no, Vehicle.isActive == 1).first()
        rt = {}
        bank_insur = []
        if item:
            rt['bottom_load'] = item.bottom_load
            rt['chassis_no'] = item.chassis_no
            rt['commissioned_date'] = "" if item.commissioned_date == '' else item.commissioned_date.strftime(
                '%d-%m-%Y')
            rt['engine_capacity'] = item.engine_capacity
            rt['engine_fuel_type'] = item.engine_fuel_type
            rt['engine_no'] = item.engine_no
            rt['id'] = item.id
            rt['ld_insurance'] = item.ld_insurance
            rt['ld_puspakom'] = item.ld_puspakom
            rt['ld_road_tax'] = item.ld_road_tax
            rt['model'] = item.model
            rt['pto_equip'] = item.pto_equip
            rt['public_id'] = item.public_id
            rt['pump_fitted'] = item.pump_fitted
            rt['regn_date'] = "" if item.regn_date == '' else item.regn_date.strftime('%d-%m-%Y')
            rt['regn_no'] = item.regn_no
            rt['top_loading'] = item.top_loading
            rt['trailer_model'] = item.trailer_model
            rt['trailer_regn'] = item.trailer_regn
            rt['trailer_type'] = item.trailer_type
            rt['weight_category_bdm'] = item.weight_category_bdm
            rt['weight_category_bt1'] = item.weight_category_bt1
            rt['weight_category_btm'] = item.weight_category_btm
            rt['location'] = item.location

            insur = Insurance.query.filter(Insurance.vehicle_id == item.id, Insurance.isActive == 1).all()
            if insur:
                for insur_det in insur:
                    temp = {}
                    temp['insur_id'] = str(insur_det.id)
                    temp['amount'] = str(round(insur_det.amount,2))
                    temp['bank_or_insurer'] = insur_det.bank_or_insurer
                    temp['due_date'] = "" if insur_det.due_date == '' else insur_det.due_date.strftime('%d-%m-%Y')
                    temp['loc'] = insur_det.loc
                    temp['policy'] = insur_det.policy
                    temp['ref_no'] = insur_det.ref_no
                    temp['remarks'] = insur_det.remarks
                    temp['types'] = insur_det.types
                    bank_insur.append(temp)
            rt['bank_insur'] = bank_insur
        response_object = {
            'vehicle': rt,
            'status': 'success',
            'error_code': 9999
        }
        return response_object
    except Exception as e:
        logging.exception(e)
        response_obj = {
            "Errorcode": 0000,
            'vehicle': {}
        }
        return response_obj


def get_location_list(data):
    try:
        return_list = []
        list_query = Location.query.filter(Location.isActive == 1)

        if data['city'] != '' and data['city'] != "\"\"":
            search = "%{}%".format(data['city'])
            list_query = list_query.filter(Location.city.ilike(search))

        city = list_query.all()

        for item in city:
            lt = {}
            lt['city'] = item.city
            return_list.append(lt)

        response_obj = {
            "Errorcode": 9999,
            "List": return_list
        }
        return response_obj
    except Exception as e:
        logging.exception(e)
        response_obj = {
            "Errorcode": 0000,
            "List": []
        }
        return response_obj


def get_rt_serviceCount():
    try:
        return_list = {}
        rt_regis_count = 0
        rt_count = Vehicle.query.filter(Vehicle.isActive == 1, Vehicle.regn_no.isnot(None)).distinct(
            Vehicle.regn_no).count()
        rt_regis_list = PDCRegistration.query.filter(PDCRegistration.isActive == 1).all()

        if rt_regis_list:
            for list in rt_regis_list:
                wp_count = InspectionItem.query.filter(InspectionItem.isActive == 1,
                                                       InspectionItem.reference_id == list.pdc_registration_id,
                                                       InspectionItem.workshop_status == 1).count()
                if wp_count > 0:
                    rt_regis_count = rt_regis_count + 1

        return_list['rt_operation'] = rt_count - rt_regis_count
        return_list['rt_unservice'] = rt_regis_count

        response_obj = {
            "Errorcode": 9999,
            "List": return_list
        }
        return response_obj
    except Exception as e:
        logging.exception(e)
        response_obj = {
            "Errorcode": 0000,
            "List": {}
        }
        return response_obj


def get_rt_locationCount():
    try:
        return_list = []
        list_query = db.session.query(db.func.count(Vehicle.location), Vehicle.location).filter(
            Vehicle.isActive == 1).group_by(Vehicle.location).all()

        if list_query:
            for item in list_query:
                if (item.location != '' and item.location != None):
                    lt = {}
                    lt['city_name'] = item.location
                    lt['city_count'] = item[0]
                    return_list.append(lt)

        response_obj = {
            "Errorcode": 9999,
            "List": return_list
        }
        return response_obj
    except Exception as e:
        logging.exception(e)
        response_obj = {
            "Errorcode": 0000,
            "List": []
        }
        return response_obj

def rt_profile_upload(image_side,file):
    try:
        extension='.'+file.split('data:image/')[1].split(';base64')[0];
        new_date=datetime.today().strftime('%Y%m%d%H%M%S')
        newfilename = image_side+"_"+str(uuid.uuid4())+"_"+new_date+extension
        directory = config.rt_images

        imgdata = base64.b64decode(file.split(';base64,')[1])

        if not os.path.exists(directory):
            os.makedirs(directory)
        filepath=os.path.join(config.rt_images,newfilename);
        with open(filepath, "wb") as fh:
         fh.write(imgdata)
         fh.close()
        response_object = {
                'filename':newfilename,
                # 'fileorgname':filename,
                'status': 'success',
                'message': 'file uploaded',
            }
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': e
        }
    return response_object, 200

def rt_profile_get(filename):
    try:
        if filename == "\"\"" or filename=="":
            filename=config.default_profile
        directory = os.path.join(config.rt_images)
        return send_from_directory(directory, filename)
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': e
        }
    return response_object, 200

def save_changes(data):
    db.session.add(data)
    db.session.commit()
