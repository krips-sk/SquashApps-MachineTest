# Name: pdc_registration_service.py
# Description: used for PDC Registration Inspection item related operation.
# Author: Mycura
# Created: 2020.12.10
# Copyright: © 2020 EMS . All Rights Reserved.
# Change History:
#                |2020.12.10
import os
import datetime
import subprocess
from app.cura import db
import logging
from sqlalchemy import or_, desc, asc, and_
from app.cura.common import common
from app.cura.common.Dict2Obj import Dict2Obj
from app.cura.user.model.user import User
from app.ems.audit_log.model.audit_log import AuditLog
from app.ems.predeparture.model.CheckList import Checklist
from app.ems.predeparture.model.PDCRegistration import PDCRegistration
from app.ems.predeparture.model.InspectionItem import InspectionItem
from app.ems.predeparture.model.rkp_login import RKPLogin
from app.ems.schedule.model.Schedule import Schedule

from app.ems.vehicle.model.vehicle import Vehicle
from app.cura.email.service.email_service import send_notification
from sqlalchemy import Date, cast
def save_changes(data):
    db.session.add(data)
    db.session.commit()


def save_pdc_inspection_item(pdc_data, pdc_registration_id, created_by, inspection_type):
    pdc_item_res = []
    try:
        for data in pdc_data:
            exists_pdc_item = InspectionItem.query.filter(InspectionItem.isActive == 1,
                                                          InspectionItem.inspection_type == inspection_type,
                                                          InspectionItem.checklist_id ==
                                                          data["checklist_id"],
                                                          InspectionItem.
                                                          reference_id == pdc_registration_id).first()

            if exists_pdc_item:
                exists_pdc_item.pdc_registration_id = pdc_registration_id
                exists_pdc_item.inspection_type = inspection_type
                exists_pdc_item.findings = data["findings"]
                exists_pdc_item.inspection_status = data["inspection_status"]
                exists_pdc_item.updated_by = created_by
                exists_pdc_item.updated_date = datetime.datetime.utcnow()
                save_changes(exists_pdc_item)
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "PDC updated successfully",
                    "inspection_id": exists_pdc_item.reference_id
                }
                pdc_item_res.append(response_object)
            else:
                new_pdc_item = InspectionItem(
                    reference_id=pdc_registration_id,
                    inspection_type=inspection_type,
                    checklist_id=data["checklist_id"],
                    findings=data["findings"],
                    inspection_status=data["inspection_status"],
                    created_by=created_by,
                    created_date=datetime.datetime.utcnow()
                )
                save_changes(new_pdc_item)
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "PDC added successfully",
                    "inspection_id": new_pdc_item.reference_id
                }
                pdc_item_res.append(response_object)

        return pdc_item_res

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "PDC save failed",
            "Error": str(e)
        }
        pdc_item_res.append(response_object)
        return pdc_item_res


#
#   feat - Used to add/update the PDC Registration
#
def add_pdc_registration(data):
    try:
        pdc_registration_id = 0
        send_pjc_notification = False
        if data["pdc_inspection"]:
            send_pjc_notification = True

        exists_pdc = PDCRegistration.query.filter(PDCRegistration.isActive == 1,
                                                  PDCRegistration.schedule_id == data["schedule_id"],PDCRegistration.inspection_type == data["inspection_type"]
                                                  ).first()
        if exists_pdc:
            exists_pdc.inspection_notes = data["inspection_notes"]
            exists_pdc.approval_status = 1 if data["submit_type"] == 1 else 0
            exists_pdc.updated_by = data["created_by"]
            exists_pdc.updated_date = datetime.datetime.utcnow()
            save_changes(exists_pdc)
            pdc_item_res = save_pdc_inspection_item(data["pdc_inspection"],
                                                    exists_pdc.pdc_registration_id,
                                                    data["created_by"], data["inspection_type"])
            response_object = {
                "ErrorCode": "9999",
                "Status": "PDC updated successfully",
                "pdc_registration_id": exists_pdc.pdc_registration_id,
                "pdc_item_res": pdc_item_res
            }
            pdc_registration_id = exists_pdc.pdc_registration_id
        else:
            new_pdc = PDCRegistration(
                schedule_id=data["schedule_id"],
                user_id=data["user_id"],
                vehicle_id=data["vehicle_id"],
                inspection_type=data["inspection_type"],
                inspection_notes=data["inspection_notes"],
                approval_status=1 if data["submit_type"] == 1 else 0,
                created_by=data["created_by"],
                created_date=datetime.datetime.utcnow(),
                completed_status=0
            )
            save_changes(new_pdc)
            log_details = {"description": "pdc registration added successfully",
                           "reference_id": new_pdc.pdc_registration_id}
            audit_log = AuditLog(
                type='RKP',
                sub_type='PDC',
                details=log_details,
                created_by=new_pdc.created_by,
                created_date=datetime.datetime.utcnow()
            )
            save_changes(audit_log)
            pdc_item_res = save_pdc_inspection_item(data["pdc_inspection"],
                                                    new_pdc.pdc_registration_id,
                                                    data["created_by"], data["inspection_type"])
            response_object = {
                "ErrorCode": "9999",
                "Status": "PDC added successfully",
                "pdc_registration_id": new_pdc.pdc_registration_id,
                "pdc_item_res": pdc_item_res
            }
            pdc_registration_id = new_pdc.pdc_registration_id

        if data["submit_type"]==1:
            send_notification(1,data["user_id"],'',0,0,'','')

        if data["inspection_type"]==2 and send_pjc_notification:
            rkp_data={"user_id": data["user_id"]}
            rkp_login(rkp_data)
            send_notification('PJC Submit', data["user_id"], '', 1, 1, 'tblPDCRegistration',pdc_registration_id)

        return response_object

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "PDC save failed",
            "pdc_item_res": [],
            "Error": str(e)
        }

        return response_object


#
#   feat - Used to get the list of PDC
#
def get_pdc_list(approval_status, page, row, searchterm, tabindex, sortindex, inspection_type):
    try:
        user_sub_query = db.session.query(User.rkp_name). \
            filter(User.id == PDCRegistration.created_by).label("created_user")

        user_sub_query1 = db.session.query( User.licence_expiry). \
            filter(User.id == PDCRegistration.created_by).label("licence_expiry")

        vehicle_sub_query = db.session.query(Vehicle.regn_no). \
            filter(Vehicle.id == PDCRegistration.vehicle_id).label("regn_no")

        vehicle_sub_query1 = db.session.query( Vehicle.ld_insurance). \
            filter(Vehicle.id == PDCRegistration.vehicle_id).label("insurance")
        vehicle_sub_query2 = db.session.query(Vehicle.ld_road_tax). \
            filter(Vehicle.id == PDCRegistration.vehicle_id).label("road_tax")
        vehicle_sub_query3 = db.session.query(Vehicle.ld_puspakom). \
            filter(Vehicle.id == PDCRegistration.vehicle_id).label("puspakom")
        pdc_query = db.session.query(PDCRegistration, user_sub_query, user_sub_query1, vehicle_sub_query,vehicle_sub_query1,vehicle_sub_query2,vehicle_sub_query3) \
            .filter(PDCRegistration.isActive == 1)

        if searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            pdc_query = pdc_query.filter(or_(PDCRegistration.inspection_notes.ilike(search)))
        if approval_status >= 0:
            if approval_status == 0:
                pdc_query = pdc_query.filter(
                    or_(PDCRegistration.approval_status == None, PDCRegistration.approval_status == 0))
            else:
                pdc_query = pdc_query.filter(PDCRegistration.approval_status == approval_status)
        if inspection_type > 0:
            pdc_query = pdc_query.filter(PDCRegistration.inspection_type == inspection_type)
        # Sorting functionality
        if tabindex == 1:
            if sortindex == 1:
                pdc_query = pdc_query.order_by(asc(PDCRegistration.approval_status))
            else:
                pdc_query = pdc_query.order_by(desc(PDCRegistration.approval_status))
        elif tabindex == 2:
            if sortindex == 1:
                pdc_query = pdc_query.order_by(asc(PDCRegistration.inspection_notes))
            else:
                pdc_query = pdc_query.order_by(desc(PDCRegistration.inspection_notes))
        elif tabindex == 3:
            if sortindex == 1:
                pdc_query = pdc_query.order_by(asc(PDCRegistration.vehicle_id))
            else:
                pdc_query = pdc_query.order_by(desc(PDCRegistration.vehicle_id))
        else:
            pdc_query = pdc_query.order_by(desc(PDCRegistration.pdc_registration_id))

        pdc_data = pdc_query.paginate(int(page), int(row), False).items
        pdc_list = []
        for pdc in pdc_data:
            dataobj = {}
            dataobj["pdc_registration_id"] = pdc.PDCRegistration.pdc_registration_id
            dataobj["vehicle_id"] = pdc.PDCRegistration.vehicle_id
            dataobj["approval_status"] = str(pdc.PDCRegistration.approval_status)
            dataobj["created_date"] = pdc.PDCRegistration.created_date.strftime("%d/%m/%Y") \
                if pdc.PDCRegistration.created_date else ""
            dataobj["inspection_notes"] = pdc.PDCRegistration.inspection_notes
            dataobj["created_user"] = pdc.created_user
            dataobj["regn_no"] = pdc.regn_no
            dataobj["licence_expiry"] = str("" if pdc.licence_expiry==None or pdc.licence_expiry=="null" else pdc.licence_expiry.strftime("%d/%m/%Y"))
            dataobj["road_tax"] = str("" if pdc.road_tax==None or pdc.road_tax=="null" else datetime.datetime.strptime(pdc.road_tax, '%Y-%m-%d').strftime("%d/%m/%Y"))
            dataobj["puspakom"] = str("" if pdc.puspakom==None or pdc.puspakom=="null" else datetime.datetime.strptime(pdc.puspakom, '%Y-%m-%d').strftime("%d/%m/%Y"))
            dataobj["insurance"] = str("" if pdc.insurance==None or pdc.insurance=="null" else datetime.datetime.strptime(pdc.insurance, '%Y-%m-%d').strftime("%d/%m/%Y"))
            pdc_list.append(dataobj)

        count = pdc_query.count()

        if pdc_data:
            response_object = {
                "data": pdc_list,
                "count": count,
                "ErrorCode": "9999"
            }
        else:
            response_object = {
                "data": [],
                "count": count,
                "ErrorCode": "9997"
            }

        return response_object, 200

    except Exception as e:

        logging.exception(e)

        response_object = {
            "data": [],
            "count": "0",
            "ErrorCode": "0000"
        }

        return response_object, 200


#
#   feat - Used to get the PDC Registration using the given id
#
def get_by_id(pdc_registration_id):
    try:
        pdc_registration = PDCRegistration.query.filter_by(isActive=1, pdc_registration_id=pdc_registration_id).first()
        return pdc_registration, 200

    except Exception as e:

        logging.exception(e)
        return {}, 201


#
#   feat - Used to get the PDC approval using the given id
#
def get_approval_item(pdc_registration_id):
    try:
        response_object = {'front': [], 'right': [], 'rear': [], 'left': []}
        pdc_registration = PDCRegistration.query.filter_by(isActive=1, pdc_registration_id=pdc_registration_id).first()
        response_object["pdc_registration_id"] = pdc_registration.pdc_registration_id
        response_object["vehicle_id"] = pdc_registration.vehicle_id
        items = db.session.query(InspectionItem, Checklist) \
            .select_from(InspectionItem).join(Checklist, and_(InspectionItem.checklist_id ==
                                                              Checklist.checklist_id)) \
            .filter(InspectionItem.inspection_status == 2,
                    InspectionItem.reference_id == pdc_registration_id,
                    InspectionItem.isActive == 1).all()
        failed_list = []
        for data in items:
            data_obj = {}
            data_obj["checklist_id"] = data.InspectionItem.checklist_id
            data_obj["pdc_registration_id"] = data.InspectionItem.reference_id
            data_obj["findings"] = data.InspectionItem.findings
            data_obj["approval_category"] = data.InspectionItem.approval_category
            data_obj["item_description"] = data.Checklist.item_description
            data_obj["zone"] = data.Checklist.zone
            data_obj["icon_name"] = "inspection_icon.png" if data.Checklist.icon_name == None else data.Checklist.icon_name
            failed_list.append(data_obj)
        if failed_list:
            response_object['front'] = [d for d in failed_list if d["zone"] == 1]
            response_object['right'] = [d for d in failed_list if d["zone"] == 2]
            response_object['rear'] = [d for d in failed_list if d["zone"] == 3]
            response_object['left'] = [d for d in failed_list if d["zone"] == 4]
            response_object['ErrorCode'] = "9999"
        else:
            response_object['ErrorCode'] = "9997"

        return response_object, 201

    except Exception as e:

        logging.exception(e)
        return {}, 201


#
#   feat - Used to delete the PDC Registration
#
def delete_pdc(data):
    try:
        pdc_registration = PDCRegistration.query.filter_by(isActive=1,
                                                           pdc_registration_id=data["pdc_registration_id"]).first()

        if pdc_registration:
            pdc_registration.isActive = "0"
            pdc_registration.updated_by = data["userid"]
            pdc_registration.updated_date = datetime.datetime.utcnow()

            save_changes(pdc_registration)

            response_object = {
                "ErrorCode": "9999",
                "Status": "pdc registration delete successfully"
            }

        else:
            response_object = {
                "ErrorCode": "9997",
                "Status": "pdc registration not exists"
            }
        return response_object, 201

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "pdc registration delete failed"
        }

        return response_object, 201


def save_approval_pdc(pdc_data):
    try:
        pdc_item_res = []
        send_approve_notification = False
        if pdc_data['pdc_registration_id'] > 0:
            pdc_reg = PDCRegistration.query.filter(PDCRegistration.pdc_registration_id ==
                                                   pdc_data["pdc_registration_id"]
                                                   ).first()
            pdc_reg.approval_notes = pdc_data["approval_notes"]
            pdc_reg.approval_status = pdc_data["approval_status"]
            pdc_reg.approved_by = pdc_data["created_by"]
            pdc_reg.approved_date = datetime.datetime.utcnow()
            save_changes(pdc_reg)
            response_object = {
                "ErrorCode": "9999",
                "Status": "PDC updated successfully"
            }
            log_details = {"description": "pdc registration " +
                                          (
                                              "approved" if pdc_reg.approval_status == 2 else "rejected"
                                          ) + " successfully",
                           "reference_id": pdc_reg.pdc_registration_id}
            audit_log = AuditLog(
                type='RKP',
                sub_type='PDC',
                details=log_details,
                created_by=pdc_reg.created_by,
                created_date=datetime.datetime.utcnow()
            )
            save_changes(audit_log)

            if pdc_data["approval_pdc_item"]:
                send_approve_notification = True

            for data in pdc_data["approval_pdc_item"]:
                is_failed_occur = 0
                if data["inspection_id"] > 0:
                    exists_pdc_item = InspectionItem.query.filter_by(isActive = 1,reference_id = pdc_data["pdc_registration_id"],checklist_id = data["inspection_id"]).first()

                    if exists_pdc_item:
                        exists_pdc_item.approval_category = data["approval_category"]
                        exists_pdc_item.updated_by = pdc_data["created_by"]
                        exists_pdc_item.updated_date = datetime.datetime.utcnow()
                        save_changes(exists_pdc_item)
                        if exists_pdc_item.inspection_status == 2:
                            is_failed_occur = 1
                        result = {
                            "ErrorCode": "9999",
                            "Status": "PDC updated successfully"
                        }
                        pdc_item_res.append(result)
                    else:
                        result = {
                            "ErrorCode": "9997",
                            "Status": "PDC Item not exists"
                        }
                        pdc_item_res.append(result)
                # if is_failed_occur == 1:
                #    pdc_reg.approval_status = 1.5

            approve_status = 1 if pdc_reg.approval_status == 2 else -1
            send_notification(2, pdc_reg.approved_by, pdc_reg.user_id, 0, approve_status,'','')

            if approve_status == 1 and send_approve_notification:
                send_notification('PDC Approve', pdc_reg.approved_by, '', 1, approve_status, 'tblPDCRegistration', pdc_data["pdc_registration_id"])

        else:
            response_object = {
                "ErrorCode": "9997",
                "Status": "PDC not exists"
            }
        response_object["pdc_item_res"] = pdc_item_res




        return response_object, 200

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "PDC save failed",
            "Error": str(e)
        }

        return response_object, 201


#
#   feat - PDC Registration Acknowledge
#
def acknowledge_pdc(data):
    try:
        pdc_registration = PDCRegistration.query.filter_by(isActive=1,
                                                           schedule_id=data["schedule_id"]).first()

        if pdc_registration:
            sch = Schedule.query.filter(Schedule.schedule_id == pdc_registration.schedule_id).first()
            if sch:
                sch.schedule_status = 4
                save_changes(sch)
            if pdc_registration.is_acknowledged is None or pdc_registration.is_acknowledged == False:
                pdc_registration.is_acknowledged = True
                pdc_registration.acknowledged_date = datetime.datetime.utcnow()
                save_changes(pdc_registration)
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "pdc registration acknowledge successfully"
                }
                log_details = {"description": "pdc registration acknowledged successfully",
                               "reference_id": pdc_registration.pdc_registration_id}
                audit_log = AuditLog(
                    type='RKP',
                    sub_type='PDC',
                    details=log_details,
                    created_by=pdc_registration.created_by,
                    created_date=datetime.datetime.utcnow()
                )
                save_changes(audit_log)
            else:
                response_object = {
                    "ErrorCode": "9997",
                    "Status": "pdc registration is already acknowledged"
                }

        else:
            response_object = {
                "ErrorCode": "9998",
                "Status": "pdc registration not exists"
            }
        return response_object, 201

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "pdc registration acknowledge failed"
        }

        return response_object, 201


#
#   feat - Get list of checklist
#
def get_check_list(sub_module, schedule_id):
    response_object = {'front': [], 'right': [], 'rear': [], 'left': []}
    try:
        schedule_exists = PDCRegistration.query.filter_by(schedule_id=schedule_id,
                                                          isActive=1,
                                                          inspection_type=sub_module).first()
        pdc_check_list = []
        if schedule_id > 0 and schedule_exists:
            query_data = db.session.query(PDCRegistration, InspectionItem, Checklist).select_from(PDCRegistration) \
                .join(InspectionItem, and_(InspectionItem.reference_id == PDCRegistration.pdc_registration_id)) \
                .join(Checklist, and_(InspectionItem.checklist_id == Checklist.checklist_id)) \
                .filter(PDCRegistration.schedule_id == schedule_id,
                        PDCRegistration.isActive == 1,
                        InspectionItem.isActive == 1,
                        Checklist.isActive == 1).all()
            for res in query_data:
                pdc_check_list.append(Dict2Obj({
                    "checklist_id": res.InspectionItem.checklist_id,
                    "item_description": res.Checklist.item_description,
                    "zone": res.Checklist.zone,
                    "sub_module": res.Checklist.sub_module,
                    "module": res.Checklist.module,
                    "findings": res.InspectionItem.findings,
                    "inspection_status": res.InspectionItem.inspection_status,
                    "inspection_type": res.InspectionItem.inspection_type,
                    "icon_name": "inspection_icon" if res.Checklist.icon_name==None else res.Checklist.icon_name
                }))
        else:
            pdc_check_list = Checklist.query.filter_by(isActive=1,
                                                       module=1,
                                                       sub_module=sub_module).all()
        if pdc_check_list:
            response_object['front'] = [d for d in pdc_check_list if d.zone == 1]
            response_object['right'] = [d for d in pdc_check_list if d.zone == 2]
            response_object['rear'] = [d for d in pdc_check_list if d.zone == 3]
            response_object['left'] = [d for d in pdc_check_list if d.zone == 4]
            response_object['ErrorCode'] = "9999"
        else:
            response_object['ErrorCode'] = "9997"

        return response_object, 200

    except Exception as e:
        logging.exception(e)
        response_object['ErrorCode'] = "0000"
        response_object['Error'] = str(e)
        return response_object, 201

def rkp_login(data):
    try:
        # subprocess.run(["python", os.path.abspath(os.path.dirname("jobs/send_notification/")) + "/notification_service.py",
        #                 'test'])
        rkp = RKPLogin.query.filter_by(isActive=1, user_id=data['user_id'],rt_status=1).first()
        if rkp:
                RKPLogin.query.filter_by(isActive=1, user_id=data['user_id'],rt_status=1).update(dict(rt_status=2,stoped_date=datetime.datetime.utcnow()))
                db.session.commit()
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Updated Successfully"
                }
        else:
            rkp_list = db.session.query(RKPLogin).filter(RKPLogin.isActive == 1, RKPLogin.user_id == data['user_id']).distinct(
                cast(RKPLogin.stoped_date, Date)).all()
            # rkp_list = RKPLogin.query.filter_by(isActive=1, user_id=data['user_id']).order_by(RKPLogin.id.desc()).distinct(RKPLogin.stoped_date).limit(6).all()
            hours=10
            is_consecutive=0
            if rkp_list:
                rkp=rkp_list[len(rkp_list) -1]
                if rkp.stoped_date:
                    diff = datetime.datetime.utcnow() - rkp.stoped_date
                    seconds=diff.total_seconds()
                    hours = seconds / 3600
                    if len(rkp_list) > 5:
                        is_consecutive = get_is_consecutive(rkp_list)

            if hours >= 10 and is_consecutive !=1:
                rkp_login_info = RKPLogin(
                    user_id=data['user_id'],
                    rt_status=1,
                    start_date=datetime.datetime.utcnow(),
                    created_by=data['user_id'],
                    created_date=datetime.datetime.utcnow()
                )
                save_changes(rkp_login_info)
                rkp_login_id=rkp_login_info.id
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "rkp login saved successfully.",
                    "rkp_login_id":rkp_login_id
                }
            else:
                response_object = {
                    "ErrorCode": "9998",
                    "Status": 'fail',
                    "message": "Rest hour not completed.",
                }
                if is_consecutive ==1 and len(rkp_list)>=6:
                    response_object = {
                        "ErrorCode": "9997",
                        "Status":'fail',
                        "message": "Rest hour not completed.",
                    }
        return response_object, 201

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "login or logoff failed"
        }

        return response_object, 201
def get_is_consecutive(date_strs):
    try:
        is_consecutive=0
        dates=[]
        last_date=date_strs[0]
        for d in date_strs:
            date=datetime.datetime.strptime(datetime.datetime.strftime(d.created_date.date(),"%m-%d-%Y"),"%m-%d-%Y")
            dates.append(date)
        dates.reverse()
        date_ints = set([d.toordinal() for d in dates])

        if max(date_ints) - min(date_ints) == len(date_ints) - 1:
            is_consecutive=1
        return  is_consecutive
    except Exception as e:
        print(e)

def get_rkp_login_hours(user_id):
    try:
        rkp =RKPLogin.query.filter_by(user_id=user_id,isActive=1,rt_status=1).first()
        if rkp:
            diff = datetime.datetime.utcnow() - rkp.start_date
            seconds = diff.total_seconds()
            # hours = seconds / 3600
            response_object={"seconds":seconds,
                             "time_diff":str(diff),
                             "started_date":str(rkp.start_date),
                             "ErrorCode": "9999",
                             "Status": "success",
                             }
        else:
            response_object = {"seconds": "",
                               "time_diff": "",
                               "started_date": "",
                               "ErrorCode": "9998",
                               "Status": "fail",
                               }
        return response_object
    except Exception as e:
        print(e)
