# Name: schedule_service.py
# Description: used to schedule the RT with RKP.
# Author: Mycura
# Created: 2020.12.09
# Copyright: © 2020 EMS . All Rights Reserved.
# Change History:
#                |2020.12.09

import datetime
from pytz import timezone
import pandas as pd
from pandas import ExcelWriter
import sqlalchemy
import xlrd
from app.cura import db
import logging
from sqlalchemy import or_, desc, asc, and_, func, cast, extract, case
from app.cura.common import common
from app.cura.user.model.user import User
from app.ems.predeparture.model.PDCRegistration import PDCRegistration
from app.ems.predeparture.model.rkp_login import RKPLogin
from app.ems.schedule.model.Schedule import Schedule
from app.ems.schedule.model.schedule_detail import ScheduleDetail
from app.ems.schedule.model.schedulel_document import Schedule_Document
from app.ems.schedule.model.schedule_type import ScheduleType
from app.ems.vehicle.model.vehicle import Vehicle
from app.ems.audit_log.model.audit_log import AuditLog
from app.cura.email.service.email_service import send_notification
from app.ems.predeparture.model.InspectionItem import InspectionItem
from app.ems.dropdown_list.model.product import Product

import os
import uuid
import base64
from flask import send_from_directory
from app.ems.config import doc_savedir, RKP_RoleId, ems_local_time_zone
from werkzeug.utils import secure_filename
from sqlalchemy import exists, and_


def save_changes(data):
    db.session.add(data)
    db.session.commit()


#
#   feat - Used to add/update the schedule for the RT and the RKP
#
def add_schedule_v2(data, created_by, schedule_type):
    try:

        sch_id = 0

        day = datetime.datetime.utcnow()
        time_str = day.strftime('%d%b%Y %M%S')
        version_no = time_str + " " + "v1"

        # // here need to save head and detail
        # first check the RT and date in first table.
        data["payment"] = '0' if data["payment"] == '' else data["payment"]
        data["dist"] = '0' if data["dist"] == '' else data['dist']
        data["Qty"] = '0' if data["Qty"] == '' else data['Qty']
        sch = Schedule.query.filter(Schedule.isActive == 1,
                                    Schedule.vehicle_id == data["vehicle_id"],
                                    Schedule.schedule_date == common.convertdmy_to_date2(data["schedule_date"])
                                    ).first()
        if sch:

            sch_id = sch.schedule_id

            sch.schedule_status = data["schedule_status"]
            sch.schedule_type = schedule_type
            sch.updated_by = created_by
            sch.updated_date = datetime.datetime.utcnow()
            save_changes(sch)

        else:
            sch = Schedule(
                vehicle_id=data["vehicle_id"],
                schedule_date=common.convertdmy_to_date2(data["schedule_date"]),
                rt_regn=data["rt_regn"],
                schedule_status=data["schedule_status"],
                schedule_type=schedule_type,
                version_no=version_no,
                created_by=created_by,
                created_date=datetime.datetime.utcnow()
            )
            save_changes(sch)

            sch_id = sch.schedule_id
        # here need to check the schedule detail table and save.
        if sch:
            sch_detail = ScheduleDetail.query.filter(ScheduleDetail.isActive == 1,
                                                     ScheduleDetail.schedule_id == sch.schedule_id,
                                                     ScheduleDetail.user_id == data["user_id"]
                                                     ).first()
            if sch_detail:
                sch_detail.user_id = data["user_id"]
                sch_detail.rt_regn = data["rt_regn"]
                sch_detail.schedule_status = data["schedule_status"]
                sch_detail.shipment_no = data["shipment_no"]
                sch_detail.delivery_note_no = data["delivery_note_no"]
                sch_detail.client = data["client"]
                sch_detail.ship_to_party = data["ship_to_party"]
                sch_detail.loc = data["loc"]
                sch_detail.product = data["product"]
                sch_detail.dist = data["dist"]
                sch_detail.payment = data["payment"]
                sch_detail.updated_by = created_by
                sch_detail.updated_date = datetime.datetime.utcnow()
                sch_detail.rg = data["Rg"],
                sch_detail.pld_time = data["PLdTime"],
                sch_detail.qty = data["Qty"]
                save_changes(sch_detail)
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Schedule updated successfully",
                    "schedule_id": sch_detail.schedule_id
                }
            else:
                new_schedule_detail = ScheduleDetail(
                    user_id=data["user_id"],
                    schedule_id=sch.schedule_id,
                    rt_regn=data["rt_regn"],
                    shipment_no=data["shipment_no"],
                    delivery_note_no=data["delivery_note_no"],
                    client=data["client"],
                    ship_to_party=data["ship_to_party"],
                    loc=data["loc"],
                    product=data["product"],
                    dist=data["dist"],
                    payment=data["payment"],
                    created_by=created_by,
                    created_date=datetime.datetime.utcnow(),
                    rg=data["Rg"],
                    pld_time=data["PLdTime"],
                    qty=data["Qty"]

                )
                save_changes(new_schedule_detail)
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Schedule added successfully",
                    "schedule_id": new_schedule_detail.schedule_id
                }

            end_date = datetime.datetime.utcnow().date() + datetime.timedelta(days=3)
            if common.convertdmy_to_date2(data["schedule_date"]) != "" and common.convertdmy_to_date2(
                    data["schedule_date"]) != None:
                if common.convertdmy_to_date2(data["schedule_date"]).date() <= end_date and common.convertdmy_to_date2(
                        data["schedule_date"]).date() >= datetime.datetime.utcnow().date():
                    send_notification('Schedule Add', created_by, data["user_id"], 0, 1, 'tblSchedule', sch_id)


        else:
            response_object = {
                "ErrorCode": "9996",
                "Status": "Schedule not exists",
                "schedule_id": 0
            }
        return response_object

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule save failed",
            "schedule_id": 0,
            "Error": str(e)
        }

        return response_object



#
#   feat - Used to add/update the schedule for the RT and the RKP
#
def add_schedule_v3(data, created_by, schedule_type):
    try:

        sch_id = 0

        day = datetime.datetime.utcnow()
        time_str = day.strftime('%d%b%Y %M%S')
        version_no = time_str + " " + "v1"

        # // here need to save head and detail
        # first check the RT and date in first table.
        data["payment"] = '0' if data["payment"] == '' else data["payment"]
        data["dist"] = '0' if data["dist"] == '' else data['dist']
        data["Qty"] = '0' if data["Qty"] == '' else data['Qty']
        sch = Schedule.query.filter(Schedule.isActive == 1,
                                    Schedule.vehicle_id == data["vehicle_id"],
                                    Schedule.schedule_date == common.convertdmy_to_date2(data["PlnStLdDt"])
                                    ).first()
        if sch:

            sch_id = sch.schedule_id

            sch.schedule_status = data["schedule_status"]
            sch.schedule_type = schedule_type
            sch.updated_by = created_by
            sch.updated_date = datetime.datetime.utcnow()
            save_changes(sch)

        else:
            sch = Schedule(
                vehicle_id=data["vehicle_id"],
                schedule_date=common.convertdmy_to_date2(data["PlnStLdDt"]),
                rt_regn=data["rt_regn"],
                schedule_status=data["schedule_status"],
                schedule_type=schedule_type,
                version_no=version_no,
                created_by=created_by,
                created_date=datetime.datetime.utcnow()
            )
            save_changes(sch)

            sch_id = sch.schedule_id
        # here need to check the schedule detail table and save.
        if sch:
            sch_detail = ScheduleDetail.query.filter(ScheduleDetail.isActive == 1,
                                                     ScheduleDetail.schedule_id == sch.schedule_id,
                                                     ScheduleDetail.user_id == data["user_id"]
                                                     ).first()
            if sch_detail:
                sch_detail.user_id = data["user_id"]
                sch_detail.rt_regn = data["rt_regn"]
                sch_detail.dist = data["dist"]
                sch_detail.payment = data["payment"]

                sch_detail.shipment_no = data["Shipment"]
                sch_detail.delivery_note_no = data["D Note"]
                sch_detail.loc = data["City"]
                sch_detail.product = data["Material"]
                sch_detail.rg = data["Rg"]
                sch_detail.t = data["T"]
                sch_detail.pld_time = data["PLdTime"]
                sch_detail.qty = data["Qty"]
                sch_detail.client = data["Name"]
                sch_detail.plnt = data["Plnt"]
                sch_detail.sc = data["SC"]
                sch_detail.trans_pln_date = common.convertdmy_to_date2(data["TransPlnDt"])
                sch_detail.dlvr = data["Dlvr"]
                sch_detail.s = data["S"]
                sch_detail.act_st_ldt = data["ActStLdT"]
                sch_detail.sold_to = data["Sold-to"]
                sch_detail.maximum_volume = data["Maximum volume"]
                sch_detail.eta_time = data["ETA time"]
                sch_detail.ship_to_party = data["Ship-to"]
                sch_detail.shty = data["ShTy"]

                sch_detail.updated_by = created_by
                sch_detail.updated_date = datetime.datetime.utcnow()


                save_changes(sch_detail)
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Schedule updated successfully",
                    "schedule_id": sch_detail.schedule_id
                }
            else:
                new_schedule_detail = ScheduleDetail(
                    schedule_id=sch.schedule_id,
                    user_id=data["user_id"],
                    rt_regn=data["rt_regn"],
                    dist=data["dist"],
                    payment=data["payment"],

                    shipment_no = data["Shipment"],
                    delivery_note_no = data["D Note"],
                    loc = data["City"],
                    product = data["Material"],
                    rg = data["Rg"],
                    t = data["T"],
                    pld_time = data["PLdTime"],
                    qty = data["Qty"],
                    client = data["Name"],
                    plnt = data["Plnt"],
                    sc = data["SC"],
                    trans_pln_date = common.convertdmy_to_date2(data["TransPlnDt"]),
                    dlvr = data["Dlvr"],
                    s = data["S"],
                    act_st_ldt = data["ActStLdT"],
                    sold_to = data["Sold-to"],
                    maximum_volume = data["Maximum volume"],
                    eta_time = data["ETA time"],
                    ship_to_party = data["Ship-to"],
                    shty = data["ShTy"],

                    created_by = created_by,
                    created_date = datetime.datetime.utcnow(),

                )
                save_changes(new_schedule_detail)
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Schedule added successfully",
                    "schedule_id": new_schedule_detail.schedule_id
                }

            end_date = datetime.datetime.utcnow().date() + datetime.timedelta(days=3)
            if common.convertdmy_to_date2(data["PlnStLdDt"]) != "" and common.convertdmy_to_date2(
                    data["PlnStLdDt"]) != None:
                if common.convertdmy_to_date2(data["PlnStLdDt"]).date() <= end_date and common.convertdmy_to_date2(
                        data["PlnStLdDt"]).date() >= datetime.datetime.utcnow().date():
                    send_notification('Schedule Add', created_by, data["user_id"], 0, 1, 'tblSchedule', sch_id)


        else:
            response_object = {
                "ErrorCode": "9996",
                "Status": "Schedule not exists",
                "schedule_id": 0
            }
        return response_object

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule save failed",
            "schedule_id": 0,
            "Error": str(e)
        }

        return response_object



#
#   feat - Used to add/update the schedule for the RT and the RKP
#
def add_schedule_v1(data, created_by):
    try:
        # // here need to save head and detail
        # first check the RT and date in first table.
        data["payment"] = '0' if data["payment"] == '' else data["payment"]
        data["dist"] = '0' if data["dist"] == '' else data['dist']
        data["Qty"] = '0' if data["Qty"] == '' else data['Qty']
        sch = Schedule.query.filter(Schedule.isActive == 1,
                                    Schedule.vehicle_id == data["vehicle_id"],
                                    Schedule.schedule_date == common.convertdmy_to_date2(data["schedule_date"])
                                    ).first()
        if sch:
            sch.schedule_status = data["schedule_status"]
            sch.updated_by = created_by
            sch.updated_date = datetime.datetime.utcnow()
            save_changes(sch)

        else:
            sch = Schedule(
                vehicle_id=data["vehicle_id"],
                schedule_date=common.convertdmy_to_date2(data["schedule_date"]),
                rt_regn=data["rt_regn"],
                schedule_status=data["schedule_status"],
                created_by=created_by,
                created_date=datetime.datetime.utcnow()
            )
            save_changes(sch)
        # here need to check the schedule detail table and save.
        if sch:
            sch_detail = ScheduleDetail.query.filter(ScheduleDetail.isActive == 1,
                                                     ScheduleDetail.schedule_id == sch.schedule_id,
                                                     ScheduleDetail.user_id == data["user_id"]
                                                     ).first()
            if sch_detail:
                sch_detail.user_id = data["user_id"]
                sch_detail.rt_regn = data["rt_regn"]
                sch_detail.schedule_status = data["schedule_status"]
                sch_detail.shipment_no = data["shipment_no"]
                sch_detail.delivery_note_no = data["delivery_note_no"]
                sch_detail.client = data["client"]
                sch_detail.ship_to_party = data["ship_to_party"]
                sch_detail.loc = data["loc"]
                sch_detail.product = data["product"]
                sch_detail.dist = data["dist"]
                sch_detail.payment = data["payment"]
                sch_detail.updated_by = created_by
                sch_detail.updated_date = datetime.datetime.utcnow()
                sch_detail.rg = data["Rg"],
                sch_detail.pld_time = data["PLdTime"],
                sch_detail.qty = data["Qty"]
                save_changes(sch_detail)
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Schedule updated successfully",
                    "schedule_id": sch_detail.schedule_id
                }
            else:
                new_schedule_detail = ScheduleDetail(
                    user_id=data["user_id"],
                    schedule_id=sch.schedule_id,
                    rt_regn=data["rt_regn"],
                    shipment_no=data["shipment_no"],
                    delivery_note_no=data["delivery_note_no"],
                    client=data["client"],
                    ship_to_party=data["ship_to_party"],
                    loc=data["loc"],
                    product=data["product"],
                    dist=data["dist"],
                    payment=data["payment"],
                    created_by=created_by,
                    created_date=datetime.datetime.utcnow(),
                    rg=data["Rg"],
                    pld_time=data["PLdTime"],
                    qty=data["Qty"]

                )
                save_changes(new_schedule_detail)
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Schedule added successfully",
                    "schedule_id": new_schedule_detail.schedule_id
                }
        else:
            response_object = {
                "ErrorCode": "9996",
                "Status": "Schedule not exists",
                "schedule_id": 0
            }
        return response_object

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule save failed",
            "schedule_id": 0,
            "Error": str(e)
        }

        return response_object



#
#   feat - Used to add/update the schedule for the RT and the RKP
#
def update_schedule_v3(data):
    try:

        schedule_data = data['update_schedule']
        schedule_type = data['schedule_type']
        updated_by = data['updated_by']
        for sched_data in schedule_data:
            end_date = datetime.datetime.now().date() + datetime.timedelta(days=3)

            sched_data["payment"] = '0' if sched_data["payment"] == '' else sched_data["payment"]
            sched_data["dist"] = '0' if sched_data["dist"] == '' else sched_data['dist']
            sched_data["Qty"] = '0' if sched_data["Qty"] == '' else sched_data['Qty']

            schedule_parent_id = 0
            previous_version = ''

            day = datetime.datetime.utcnow()
            time_str = day.strftime('%d%b%Y %M%S')

            if sched_data["schedule_id"] != 0 and sched_data["audit_log"]:
                schedule = Schedule.query.filter(Schedule.isActive == 1,
                                                 Schedule.schedule_id == sched_data["schedule_id"]).first()

                if schedule:
                    schedule_parent_id = sched_data["schedule_id"]
                    schedule_version_no = schedule.version_no
                    version_arr = schedule_version_no.split()
                    previous_version_no = version_arr[-1]
                    previous_version_no = int(''.join(filter(str.isdigit, previous_version_no))) + 1

                    previous_version = time_str + " " + "v" + str(previous_version_no)

                    schedule.isActive = 0
                    save_changes(schedule)

                    sch = Schedule(
                        vehicle_id=sched_data["vehicle_id"],
                        schedule_date=common.convertdmy_to_date2(sched_data["PlnStLdDt"]),
                        rt_regn=sched_data["rt_regn"],
                        schedule_status=sched_data["schedule_status"],
                        schedule_type=schedule_type,
                        parent_id=schedule_parent_id,
                        version_no=previous_version,
                        created_by=updated_by,
                        created_date=datetime.datetime.utcnow()
                    )
                    save_changes(sch)

                    new_schedule_detail = ScheduleDetail(
                        user_id=sched_data["user_id"],
                        schedule_id=sch.schedule_id,
                        rt_regn=sched_data["rt_regn"],
                        dist=sched_data["dist"],
                        payment=sched_data["payment"],

                        shipment_no=sched_data["Shipment"],
                        delivery_note_no=sched_data["D Note"],
                        loc=sched_data["City"],
                        product=sched_data["Material"],
                        rg=sched_data["Rg"],
                        t=sched_data["T"],
                        pld_time=sched_data["PLdTime"],
                        qty=sched_data["Qty"],
                        client=sched_data["Name"],
                        plnt=sched_data["Plnt"],
                        sc=sched_data["SC"],
                        trans_pln_date=common.convertdmy_to_date2(sched_data["TransPlnDt"]),
                        dlvr=sched_data["Dlvr"],
                        s=sched_data["S"],
                        act_st_ldt=sched_data["ActStLdT"],
                        sold_to=sched_data["Sold-to"],
                        maximum_volume=sched_data["Maximum volume"],
                        eta_time=sched_data["ETA time"],
                        ship_to_party=sched_data["Ship-to"],
                        shty=sched_data["ShTy"],

                        created_by=updated_by,
                        created_date=datetime.datetime.utcnow(),

                    )
                    save_changes(new_schedule_detail)

                    for log in sched_data["audit_log"]:

                        if log["type"] != "audit_log":

                            log_details = {"description": log["type"] +" is Replaced from "+log["old_value"] +" to " +log["new_value"] +" for Schedule",
                                           "reference_id": sch.schedule_id}

                            audit_log = AuditLog(
                                type="Operations",
                                sub_type="Schedule",
                                details=log_details,
                                created_by=updated_by,
                                created_date=datetime.datetime.utcnow()
                            )
                            save_changes(audit_log)

                            if log["type"] == "user_name":

                                if schedule.schedule_date.date() <= end_date:
                                    send_notification('Schedule Add',updated_by, sched_data["user_id"], 0, 1,
                                                      'tblSchedule', sched_data["schedule_id"])

                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Schedule updated successfully",
                }

        return response_object

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule save failed",
        }

        return response_object




#
#   feat - Used to add/update the schedule for the RT and the RKP
#
def update_schedule(data):
    try:

        schedule_data = data['update_schedule']
        schedule_type = data['schedule_type']
        updated_by = data['updated_by']
        for sched_data in schedule_data:
            end_date = datetime.datetime.now().date() + datetime.timedelta(days=3)

            sched_data["payment"] = '0' if sched_data["payment"] == '' else sched_data["payment"]
            sched_data["dist"] = '0' if sched_data["dist"] == '' else sched_data['dist']
            sched_data["Qty"] = '0' if sched_data["Qty"] == '' else sched_data['Qty']

            schedule_parent_id = 0
            previous_version = ''

            day = datetime.datetime.utcnow()
            time_str = day.strftime('%d%b%Y %M%S')

            if sched_data["schedule_id"] != 0 and sched_data["audit_log"]:
                schedule = Schedule.query.filter(Schedule.isActive == 1,
                                                 Schedule.schedule_id == sched_data["schedule_id"]).first()

                if schedule:
                    schedule_parent_id = sched_data["schedule_id"]
                    schedule_version_no = schedule.version_no
                    version_arr = schedule_version_no.split()
                    previous_version_no = version_arr[-1]
                    previous_version_no = int(''.join(filter(str.isdigit, previous_version_no))) + 1

                    previous_version = time_str + " " + "v" + str(previous_version_no)

                    schedule.isActive = 0
                    save_changes(schedule)

                    sch = Schedule(
                        vehicle_id=sched_data["vehicle_id"],
                        schedule_date=common.convertdmy_to_date2(sched_data["schedule_date"]),
                        rt_regn=sched_data["rt_regn"],
                        schedule_status=sched_data["schedule_status"],
                        schedule_type=schedule_type,
                        parent_id=schedule_parent_id,
                        version_no=previous_version,
                        created_by=updated_by,
                        created_date=datetime.datetime.utcnow()
                    )
                    save_changes(sch)

                    new_schedule_detail = ScheduleDetail(
                        user_id=sched_data["user_id"],
                        schedule_id=sch.schedule_id,
                        rt_regn=sched_data["rt_regn"],
                        shipment_no=sched_data["shipment_no"],
                        delivery_note_no=sched_data["delivery_note_no"],
                        client=sched_data["client"],
                        ship_to_party=sched_data["ship_to_party"],
                        loc=sched_data["loc"],
                        product=sched_data["product"],
                        dist=sched_data["dist"],
                        payment=sched_data["payment"],
                        created_by=sched_data["created_by"],
                        created_date=datetime.datetime.utcnow(),
                        rg=sched_data["Rg"],
                        pld_time=sched_data["PLdTime"],
                        qty=sched_data["Qty"]

                    )
                    save_changes(new_schedule_detail)

                    for log in sched_data["audit_log"]:

                        if log["type"] != "audit_log":

                            log_details = {"description": log["type"] +" is Replaced from "+log["old_value"] +" to " +log["new_value"] +" for Schedule",
                                           "reference_id": sch.schedule_id}

                            audit_log = AuditLog(
                                type="Operations",
                                sub_type="Schedule",
                                details=log_details,
                                created_by=updated_by,
                                created_date=datetime.datetime.utcnow()
                            )
                            save_changes(audit_log)

                            if log["type"] == "user_name":

                                if schedule.schedule_date.date() <= end_date:
                                    send_notification('Schedule Add',updated_by, sched_data["user_id"], 0, 1,
                                                      'tblSchedule', sched_data["schedule_id"])

                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Schedule updated successfully",
                }

        return response_object

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule save failed",
        }

        return response_object


#
#   feat - Used to add/update the schedule for the RT and the RKP
#
def add_schedule(data, created_by):
    try:
        data["payment"] = '0' if data["payment"] == '' else data["payment"]
        data["dist"] = '0' if data["dist"] == '' else data['dist']
        data["Qty"] = '0' if data["Qty"] == '' else data['Qty']
        if data["schedule_id"] == 0:
            country = Schedule.query.filter(Schedule.isActive == 1,
                                            Schedule.user_id == data["user_id"],
                                            Schedule.vehicle_id == data["vehicle_id"],
                                            Schedule.schedule_date == common.convertdmy_to_date2(data["schedule_date"])
                                            ).first()
            if country:
                response_object = {
                    "ErrorCode": "9997",
                    "Status": "Schedule already exists"
                }
            else:
                new_schedule = Schedule(
                    user_id=data["user_id"],
                    vehicle_id=data["vehicle_id"],
                    schedule_date=common.convertdmy_to_date2(data["schedule_date"]),
                    rt_regn=data["rt_regn"],
                    schedule_status=data["schedule_status"],
                    shipment_no=data["shipment_no"],
                    delivery_note_no=data["delivery_note_no"],
                    client=data["client"],
                    ship_to_party=data["ship_to_party"],
                    loc=data["loc"],
                    product=data["product"],
                    dist=data["dist"],
                    payment=data["payment"],
                    created_by=created_by,
                    created_date=datetime.datetime.utcnow(),
                    rg=data["Rg"],
                    pld_time=data["PLdTime"],
                    qty=data["Qty"]

                )
                save_changes(new_schedule)
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Schedule added successfully",
                    "schedule_id": new_schedule.schedule_id
                }
        else:
            exists_schedule = Schedule.query.filter(Schedule.isActive == 1,
                                                    Schedule.schedule_id != data["schedule_id"],
                                                    Schedule.user_id == data["user_id"],
                                                    Schedule.vehicle_id == data["vehicle_id"],
                                                    Schedule.schedule_date == common.convertdmy_to_date2(
                                                        data["schedule_date"])).first()
            if exists_schedule:
                response_object = {
                    "ErrorCode": "9997",
                    "Status": "Schedule already exists",
                    "schedule_id": exists_schedule.schedule_id
                }
            else:
                schedule = Schedule.query.filter(Schedule.isActive == 1,
                                                 Schedule.schedule_id == data["schedule_id"]).first()
                if schedule:
                    schedule.user_id = data["user_id"]
                    schedule.vehicle_id = data["vehicle_id"]
                    schedule.schedule_date = common.convertdmy_to_date2(data["schedule_date"])
                    schedule.rt_regn = data["rt_regn"]
                    schedule.schedule_status = data["schedule_status"]
                    schedule.shipment_no = data["shipment_no"]
                    schedule.delivery_note_no = data["delivery_note_no"]
                    schedule.client = data["client"]
                    schedule.ship_to_party = data["ship_to_party"]
                    schedule.loc = data["loc"]
                    schedule.product = data["product"]
                    schedule.dist = data["dist"]
                    schedule.payment = data["payment"]
                    schedule.updated_by = created_by
                    schedule.updated_date = datetime.datetime.utcnow()
                    schedule.rg = data["Rg"],
                    schedule.pld_time = data["PLdTime"],
                    schedule.qty = data["Qty"]
                    save_changes(schedule)
                    response_object = {
                        "ErrorCode": "9999",
                        "Status": "Schedule updated successfully",
                        "schedule_id": schedule.schedule_id
                    }

                else:
                    response_object = {
                        "ErrorCode": "9996",
                        "Status": "Schedule not exists",
                        "schedule_id": 0
                    }

        return response_object

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule save failed",
            "schedule_id": 0,
            "Error": str(e)
        }

        return response_object


#
#   feat - Used to get the list of schedule for the particular RKP
#
def get_rkp_schedule_list(user_id, page, row, searchterm, tabindex, sortindex):
    try:
        end_date = datetime.datetime.now().date() + datetime.timedelta(days=3)
        schedule_query = Schedule.query.filter_by(isActive=1)
        schedule_query = schedule_query.filter(Schedule.user_id == user_id,
                                               Schedule.schedule_date >= datetime.datetime.now().date(),
                                               Schedule.schedule_date <= end_date)
        if searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            schedule_query = schedule_query.filter(or_(Schedule.ship_to_party.ilike(search),
                                                       Schedule.rt_regn.ilike((search)),
                                                       Schedule.delivery_note_no.ilike(search),
                                                       Schedule.dist.ilike(search),
                                                       Schedule.loc.ilike(search),
                                                       Schedule.product.ilike(search),
                                                       Schedule.shipment_no.ilike(search)))

        # Sorting functionality
        if tabindex == 1:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(Schedule.rt_regn))
            else:
                schedule_query = schedule_query.order_by(desc(Schedule.rt_regn))
        elif tabindex == 2:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(Schedule.shipment_no))
            else:
                schedule_query = schedule_query.order_by(desc(Schedule.shipment_no))
        elif tabindex == 3:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(Schedule.delivery_note_no))
            else:
                schedule_query = schedule_query.order_by(desc(Schedule.delivery_note_no))
        else:
            schedule_query = schedule_query.order_by(desc(Schedule.schedule_id))

        schedules = schedule_query.paginate(int(page), int(row), False).items
        count = schedule_query.count()

        if schedules:
            response_object = {
                "data": schedules,
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
#   feat - Used to get the list of schedule for the particular RKP
#
def get_rkp_schedule_list_v1(user_id, page, row, searchterm, tabindex, sortindex):
    try:
        end_date = datetime.datetime.now().date() + datetime.timedelta(days=3)

        schedule_query = db.session.query(Schedule, ScheduleDetail, User) \
            .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)).filter(
            ScheduleDetail.isActive == 1, Schedule.isActive == 1) \
            .join(User, and_(ScheduleDetail.user_id == User.id)).filter(
            ScheduleDetail.isActive == 1, Schedule.isActive == 1)

        schedule_query = schedule_query.filter(ScheduleDetail.user_id == user_id,
                                               Schedule.schedule_date >= datetime.datetime.now().date(),
                                               Schedule.schedule_date <= end_date)

        if searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            schedule_query = schedule_query.filter(or_(ScheduleDetail.ship_to_party.ilike(search),
                                                       ScheduleDetail.rt_regn.ilike((search)),
                                                       ScheduleDetail.delivery_note_no.ilike(search),
                                                       ScheduleDetail.dist.ilike(search),
                                                       ScheduleDetail.loc.ilike(search),
                                                       ScheduleDetail.product.ilike(search),
                                                       ScheduleDetail.shipment_no.ilike(search)))

        # Sorting functionality
        if tabindex == 1:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.rt_regn))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.rt_regn))
        elif tabindex == 2:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.shipment_no))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.shipment_no))
        elif tabindex == 3:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.delivery_note_no))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.delivery_note_no))
        else:
            schedule_query = schedule_query.order_by(asc(Schedule.schedule_date))

        schedules = schedule_query.paginate(int(page), int(row), False).items
        count = schedule_query.count()
        schedules_list = []
        for sch in schedules:
            schedules_list.append({
                'schedule_id': sch.ScheduleDetail.schedule_id,
                'vehicle_id': sch.Schedule.vehicle_id,
                'schedule_status': sch.Schedule.schedule_status,
                'rt_regn': sch.ScheduleDetail.rt_regn,
                'schedule_date': sch.Schedule.schedule_date.strftime('%d.%m.%Y') if sch.Schedule.schedule_date else "",
                'shipment_no': sch.ScheduleDetail.shipment_no,
                'delivery_note_no': sch.ScheduleDetail.delivery_note_no,
                'ship_to_party': sch.ScheduleDetail.ship_to_party,
                'client': sch.ScheduleDetail.client,
                'loc': sch.ScheduleDetail.loc,
                'product': sch.ScheduleDetail.product,
                'dist': str(sch.ScheduleDetail.dist),
                'payment': str(sch.ScheduleDetail.payment),
                'Rg': sch.ScheduleDetail.rg,
                'PLdTime': sch.ScheduleDetail.pld_time,
                'Qty': sch.ScheduleDetail.qty,
                'created_by': sch.ScheduleDetail.created_by,
                'user_name': sch.User.rkp_name if sch.User.rkp_name != None and sch.User.rkp_name != "" else
                sch.User.first_name + ' ' + (sch.User.last_name) if sch.User.last_name != None else "",
                'user_id': sch.ScheduleDetail.user_id
            })

        if schedules_list:
            response_object = {
                "data": schedules_list,
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
#   feat - Used to get the list of schedule for the particular RKP
#
def get_rkp_schedule_list_v2(user_id, page, row, searchterm, tabindex, sortindex, schedule_type):
    try:
        end_date = datetime.datetime.now().date() + datetime.timedelta(days=3)

        schedule_query = db.session.query(Schedule, ScheduleDetail, User) \
            .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)).filter(
            ScheduleDetail.isActive == 1, Schedule.isActive == 1) \
            .join(User, and_(ScheduleDetail.user_id == User.id)).filter(
            ScheduleDetail.isActive == 1, Schedule.isActive == 1, Schedule.schedule_type == schedule_type)

        schedule_query = schedule_query.filter(ScheduleDetail.user_id == user_id,
                                               Schedule.schedule_date >= datetime.datetime.now().date(),
                                               Schedule.schedule_date <= end_date)

        if searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            schedule_query = schedule_query.filter(or_(ScheduleDetail.ship_to_party.ilike(search),
                                                       ScheduleDetail.rt_regn.ilike((search)),
                                                       ScheduleDetail.delivery_note_no.ilike(search),
                                                       ScheduleDetail.dist.ilike(search),
                                                       ScheduleDetail.loc.ilike(search),
                                                       ScheduleDetail.product.ilike(search),
                                                       ScheduleDetail.shipment_no.ilike(search)))

        # Sorting functionality
        if tabindex == 1:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.rt_regn))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.rt_regn))
        elif tabindex == 2:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.shipment_no))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.shipment_no))
        elif tabindex == 3:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.delivery_note_no))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.delivery_note_no))
        else:
            schedule_query = schedule_query.order_by(asc(Schedule.schedule_date))

        schedules = schedule_query.paginate(int(page), int(row), False).items
        count = schedule_query.count()
        schedules_list = []
        for sch in schedules:
            schedules_list.append({
                'schedule_id': sch.ScheduleDetail.schedule_id,
                'vehicle_id': sch.Schedule.vehicle_id,
                'schedule_status': sch.Schedule.schedule_status,
                'rt_regn': sch.ScheduleDetail.rt_regn,
                'schedule_date': sch.Schedule.schedule_date.strftime('%d.%m.%Y') if sch.Schedule.schedule_date else "",
                'shipment_no': sch.ScheduleDetail.shipment_no,
                'delivery_note_no': sch.ScheduleDetail.delivery_note_no,
                'ship_to_party': sch.ScheduleDetail.ship_to_party,
                'client': sch.ScheduleDetail.client,
                'loc': sch.ScheduleDetail.loc,
                'product': sch.ScheduleDetail.product,
                'dist': str(sch.ScheduleDetail.dist),
                'payment': str(sch.ScheduleDetail.payment),
                'Rg': sch.ScheduleDetail.rg,
                'PLdTime': sch.ScheduleDetail.pld_time,
                'Qty': sch.ScheduleDetail.qty,
                'created_by': sch.ScheduleDetail.created_by,
                'user_name': sch.User.rkp_name if sch.User.rkp_name != None and sch.User.rkp_name != "" else
                sch.User.first_name + ' ' + (sch.User.last_name) if sch.User.last_name != None else "",
                'user_id': sch.ScheduleDetail.user_id
            })

        if schedules_list:
            response_object = {
                "data": schedules_list,
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
#   feat - Used to get the list of schedule for the particular RKP
#
def get_rkp_schedule_list_v3(user_id, page, row, searchterm, tabindex, sortindex, schedule_type):
    try:
        end_date = datetime.datetime.now().date() + datetime.timedelta(days=3)

        schedule_query = db.session.query(Schedule, ScheduleDetail, User) \
            .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)).filter(
            ScheduleDetail.isActive == 1, Schedule.isActive == 1) \
            .join(User, and_(ScheduleDetail.user_id == User.id)).filter(
            ScheduleDetail.isActive == 1, Schedule.isActive == 1, Schedule.schedule_type == schedule_type)

        schedule_query = schedule_query.filter(ScheduleDetail.user_id == user_id,
                                               Schedule.schedule_date >= datetime.datetime.now().date(),
                                               Schedule.schedule_date <= end_date)

        if searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            schedule_query = schedule_query.filter(or_(ScheduleDetail.ship_to_party.ilike(search),
                                                       ScheduleDetail.rt_regn.ilike((search)),
                                                       ScheduleDetail.delivery_note_no.ilike(search),
                                                       ScheduleDetail.dist.ilike(search),
                                                       ScheduleDetail.loc.ilike(search),
                                                       ScheduleDetail.product.ilike(search),
                                                       ScheduleDetail.shipment_no.ilike(search)))

        # Sorting functionality
        if tabindex == 1:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.rt_regn))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.rt_regn))
        elif tabindex == 2:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.shipment_no))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.shipment_no))
        elif tabindex == 3:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.delivery_note_no))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.delivery_note_no))
        else:
            schedule_query = schedule_query.order_by(asc(Schedule.schedule_date))

        schedules = schedule_query.paginate(int(page), int(row), False).items
        count = schedule_query.count()
        schedules_list = []
        for sch in schedules:
            data = {}
            data['schedule_id'] = sch.ScheduleDetail.schedule_id
            data['vehicle_id'] = sch.Schedule.vehicle_id
            data['schedule_status'] = sch.Schedule.schedule_status
            data['rt_regn'] = sch.ScheduleDetail.rt_regn
            data['dist'] = str(sch.ScheduleDetail.dist)
            data['payment'] = str(sch.ScheduleDetail.payment)
            data['created_by'] = sch.ScheduleDetail.created_by
            data['user_name'] = sch.User.rkp_name if sch.User.rkp_name != None and sch.User.rkp_name != "" else sch.User.first_name + ' ' + (
                sch.User.last_name) if sch.User.last_name != None else ""
            data['user_id'] = sch.ScheduleDetail.user_id

            data['PlnStLdDt'] = sch.Schedule.schedule_date.strftime('%d.%m.%Y') if sch.Schedule.schedule_date else ""
            data['Shipment'] = sch.ScheduleDetail.shipment_no
            data['D Note'] = sch.ScheduleDetail.delivery_note_no
            data['Name'] = sch.ScheduleDetail.client
            data['City'] = sch.ScheduleDetail.loc
            data['Material'] = sch.ScheduleDetail.product
            data['Rg'] = sch.ScheduleDetail.rg
            data['PLdTime'] = sch.ScheduleDetail.pld_time
            data['Qty'] = str(sch.ScheduleDetail.qty)
            data["T"] = sch.ScheduleDetail.t
            data["Plnt"] = sch.ScheduleDetail.plnt
            data["SC"] = sch.ScheduleDetail.sc
            data["TransPlnDt"] = sch.ScheduleDetail.trans_pln_date.strftime('%d.%m.%Y') if sch.ScheduleDetail.trans_pln_date else ""
            data["Dlvr"] = sch.ScheduleDetail.dlvr
            data["S"] = sch.ScheduleDetail.s
            data["ActStLdT"] = sch.ScheduleDetail.act_st_ldt
            data["Sold-to"] = sch.ScheduleDetail.sold_to
            data["Maximum volume"] = sch.ScheduleDetail.maximum_volume
            data["ETA time"] = sch.ScheduleDetail.eta_time
            data["Ship-to"] = sch.ScheduleDetail.ship_to_party
            data["ShTy"] = sch.ScheduleDetail.shty

            schedules_list.append(data)

        if schedules_list:
            response_object = {
                "data": schedules_list,
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
#   feat - Used to get the list of schedule for the RT and the RKP
#
def get_schedule_list(page, row, searchterm, tabindex, sortindex, schedule_date):
    try:
        user_query = db.session.query(func.concat(User.first_name, ' ', User.last_name)). \
            filter(User.id == Schedule.user_id).label("user_name")

        schedule_query = db.session.query(Schedule, user_query).filter(Schedule.isActive == 1)
        if schedule_date:
            report_date = common.convertdmy_to_date2(schedule_date)
            schedule_query = schedule_query.filter(Schedule.schedule_date == report_date)

        if searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            schedule_query = schedule_query.filter(or_(Schedule.ship_to_party.ilike(search),
                                                       Schedule.rt_regn.ilike((search)),
                                                       Schedule.delivery_note_no.ilike(search),
                                                       Schedule.dist.ilike(search),
                                                       Schedule.loc.ilike(search),
                                                       Schedule.product.ilike(search),
                                                       Schedule.shipment_no.ilike(search)))

        # Sorting functionality
        if tabindex == 1:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(Schedule.rt_regn))
            else:
                schedule_query = schedule_query.order_by(desc(Schedule.rt_regn))
        elif tabindex == 2:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(Schedule.shipment_no))
            else:
                schedule_query = schedule_query.order_by(desc(Schedule.shipment_no))
        elif tabindex == 3:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(Schedule.delivery_note_no))
            else:
                schedule_query = schedule_query.order_by(desc(Schedule.delivery_note_no))
        else:
            schedule_query = schedule_query.order_by(desc(Schedule.schedule_id))

        schedules = schedule_query.paginate(int(page), int(row), False).items
        count = schedule_query.count()

        schedules_list = []
        for sch in schedules:
            schedules_list.append({
                'schedule_id': sch.Schedule.schedule_id,
                'vehicle_id': sch.Schedule.vehicle_id,
                'schedule_status': sch.Schedule.schedule_status,
                'rt_regn': sch.Schedule.rt_regn,
                'schedule_date': sch.Schedule.schedule_date.strftime('%d.%m.%Y') if sch.Schedule.schedule_date else "",
                'shipment_no': sch.Schedule.shipment_no,
                'delivery_note_no': sch.Schedule.delivery_note_no,
                'ship_to_party': sch.Schedule.ship_to_party,
                'client': sch.Schedule.client,
                'loc': sch.Schedule.loc,
                'product': sch.Schedule.product,
                'dist': str(sch.Schedule.dist),
                'payment': str(sch.Schedule.payment),
                'Rg': sch.Schedule.rg,
                'PLdTime': sch.Schedule.pld_time,
                'Qty': sch.Schedule.qty,
                'created_by': sch.Schedule.created_by,
                'user_name': sch.user_name,
                'user_id': sch.Schedule.user_id
            })

        if schedules:
            response_object = {
                "data": schedules_list,
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
            "ErrorCode": "0000",
            "error": str(e)
        }

        return response_object, 200


#
#   feat - Used to get the list of schedule for the RT and the RKP
#
def get_schedule_list_v1(page, row, searchterm, tabindex, sortindex, schedule_date):
    try:
        user_query = db.session.query(func.concat(User.first_name, ' ', User.last_name)). \
            filter(User.id == ScheduleDetail.user_id).label("user_name")

        schedule_query = db.session.query(Schedule, ScheduleDetail, User) \
            .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)) \
            .join(User, and_(ScheduleDetail.user_id == User.id)).filter(
            ScheduleDetail.isActive == 1, Schedule.isActive == 1)
        if schedule_date:
            report_date = common.convertdmy_to_date2(schedule_date)
            schedule_query = schedule_query.filter(Schedule.schedule_date == report_date)
            
        if searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            schedule_query = schedule_query.filter(or_(ScheduleDetail.rg.ilike(search),
                                                       ScheduleDetail.rt_regn.ilike(search),
                                                       ScheduleDetail.loc.ilike(search),
                                                       ScheduleDetail.shipment_no.ilike(search),
                                                       ScheduleDetail.client.ilike(search),
                                                       ScheduleDetail.delivery_note_no.ilike(search),
                                                       ScheduleDetail.product.ilike(search),
                                                       User.rkp_name.ilike(search),
                                                       User.first_name.ilike(search),
                                                       User.last_name.ilike(search),
                                                       User.rkp_ic_number.ilike(search)
                                                       ))

        # Sorting functionality
        if tabindex == 1:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.rt_regn))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.rt_regn))
        elif tabindex == 2:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.shipment_no))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.shipment_no))
        elif tabindex == 3:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.delivery_note_no))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.delivery_note_no))
        else:
            schedule_query = schedule_query.order_by(desc(ScheduleDetail.schedule_id))

        schedules = schedule_query.paginate(int(page), int(row), False).items
        count = schedule_query.count()

        schedules_list = []
        for sch in schedules:
            schedules_list.append({
                'schedule_id': sch.ScheduleDetail.schedule_id,
                'vehicle_id': sch.Schedule.vehicle_id,
                'schedule_status': sch.Schedule.schedule_status,
                'rt_regn': sch.ScheduleDetail.rt_regn,
                'schedule_date': sch.Schedule.schedule_date.strftime('%d.%m.%Y') if sch.Schedule.schedule_date else "",
                'shipment_no': sch.ScheduleDetail.shipment_no,
                'delivery_note_no': sch.ScheduleDetail.delivery_note_no,
                'ship_to_party': sch.ScheduleDetail.ship_to_party,
                'client': sch.ScheduleDetail.client,
                'loc': sch.ScheduleDetail.loc,
                'product': sch.ScheduleDetail.product,
                'dist': str(sch.ScheduleDetail.dist),
                'payment': str(sch.ScheduleDetail.payment),
                'Rg': sch.ScheduleDetail.rg,
                'PLdTime': sch.ScheduleDetail.pld_time,
                'Qty': sch.ScheduleDetail.qty,
                'created_by': sch.ScheduleDetail.created_by,
                'user_name': sch.User.rkp_name if sch.User.rkp_name != None and sch.User.rkp_name != "" else
                sch.User.first_name + ' ' + (sch.User.last_name) if sch.User.last_name != None else "",
                'user_id': sch.ScheduleDetail.user_id,
                'version_no': sch.Schedule.version_no
            })

        response_object = {
            "data": schedules_list,
            "count": count,
            "ErrorCode": "9999"
        }

        return response_object, 200

    except Exception as e:

        logging.exception(e)

        response_object = {
            "data": [],
            "count": "0",
            "ErrorCode": "0000",
            "error": str(e)
        }

        return response_object, 200


#
#   feat - Used to get the list of schedule for the RT and the RKP
#
def get_schedule_list_v2(page, row, schedule_type, searchterm, tabindex, sortindex):
    try:
        user_query = db.session.query(func.concat(User.first_name, ' ', User.last_name)). \
            filter(User.id == ScheduleDetail.user_id).label("user_name")

        schedule_query = db.session.query(Schedule, ScheduleDetail, User) \
            .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)) \
            .join(User, and_(ScheduleDetail.user_id == User.id)).filter(
            ScheduleDetail.isActive == 1, Schedule.isActive == 1, Schedule.schedule_type == schedule_type)

        if searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            schedule_query = schedule_query.filter(or_(ScheduleDetail.rg.ilike(search),
                                                       ScheduleDetail.rt_regn.ilike(search),
                                                       ScheduleDetail.loc.ilike(search),
                                                       ScheduleDetail.shipment_no.ilike(search),
                                                       ScheduleDetail.client.ilike(search),
                                                       ScheduleDetail.delivery_note_no.ilike(search),
                                                       ScheduleDetail.product.ilike(search),
                                                       User.rkp_name.ilike(search),
                                                       User.first_name.ilike(search),
                                                       User.last_name.ilike(search),
                                                       User.rkp_ic_number.ilike(search)
                                                       ))

        # Sorting functionality
        if tabindex == 1:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.rt_regn))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.rt_regn))
        elif tabindex == 2:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.shipment_no))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.shipment_no))
        elif tabindex == 3:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.delivery_note_no))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.delivery_note_no))
        else:
            schedule_query = schedule_query.order_by(desc(Schedule.schedule_date))

        schedules = schedule_query.paginate(int(page), int(row), False).items
        count = schedule_query.count()

        schedules_list = []
        for sch in schedules:
            schedules_list.append({
                'schedule_id': sch.ScheduleDetail.schedule_id,
                'vehicle_id': sch.Schedule.vehicle_id,
                'schedule_status': sch.Schedule.schedule_status,
                'rt_regn': sch.ScheduleDetail.rt_regn,
                'schedule_date': sch.Schedule.schedule_date.strftime('%d.%m.%Y') if sch.Schedule.schedule_date else "",
                'shipment_no': sch.ScheduleDetail.shipment_no,
                'delivery_note_no': sch.ScheduleDetail.delivery_note_no,
                'ship_to_party': sch.ScheduleDetail.ship_to_party,
                'client': sch.ScheduleDetail.client,
                'loc': sch.ScheduleDetail.loc,
                'product': sch.ScheduleDetail.product,
                'dist': str(sch.ScheduleDetail.dist),
                'payment': str(sch.ScheduleDetail.payment),
                'Rg': sch.ScheduleDetail.rg,
                'PLdTime': sch.ScheduleDetail.pld_time,
                'Qty': sch.ScheduleDetail.qty,
                'created_by': sch.ScheduleDetail.created_by,
                'user_name': sch.User.rkp_name if sch.User.rkp_name != None and sch.User.rkp_name != "" else
                sch.User.first_name + ' ' + (sch.User.last_name) if sch.User.last_name != None else "",
                'user_id': sch.ScheduleDetail.user_id,
                'isRow_Editable': False

            })

        response_object = {
            "data": schedules_list,
            "count": count,
            "ErrorCode": "9999"
        }

        return response_object, 200

    except Exception as e:

        logging.exception(e)

        response_object = {
            "data": [],
            "count": "0",
            "ErrorCode": "0000",
            "error": str(e)
        }

        return response_object, 200
    



#
#   feat - Used to get the list of schedule for the RT and the RKP
#
def get_schedule_list_v3(page, row, schedule_type, searchterm, tabindex, sortindex,date):
    try:
        user_query = db.session.query(func.concat(User.first_name, ' ', User.last_name)). \
            filter(User.id == ScheduleDetail.user_id).label("user_name")

        schedule_query = db.session.query(Schedule, ScheduleDetail, User) \
            .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)) \
            .outerjoin(User, and_(ScheduleDetail.user_id == User.id)).filter(
            ScheduleDetail.isActive == 1, Schedule.isActive == 1, Schedule.schedule_type == schedule_type, Schedule.schedule_date == common.convertdmy_to_date2(date))

        if searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            schedule_query = schedule_query.filter(or_(ScheduleDetail.rg.ilike(search),
                                                       ScheduleDetail.rt_regn.ilike(search),
                                                       ScheduleDetail.loc.ilike(search),
                                                       ScheduleDetail.shipment_no.ilike(search),
                                                       ScheduleDetail.client.ilike(search),
                                                       ScheduleDetail.delivery_note_no.ilike(search),
                                                       ScheduleDetail.product.ilike(search),
                                                       User.rkp_name.ilike(search),
                                                       User.first_name.ilike(search),
                                                       User.last_name.ilike(search),
                                                       User.rkp_ic_number.ilike(search)
                                                       ))

        # Sorting functionality
        if tabindex == 1:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.rt_regn))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.rt_regn))
        elif tabindex == 2:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.shipment_no))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.shipment_no))
        elif tabindex == 3:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.delivery_note_no))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.delivery_note_no))
        else:
            schedule_query = schedule_query.order_by(desc(Schedule.schedule_date))

        schedules = schedule_query.paginate(int(page), int(row), False).items
        count = schedule_query.count()

        schedules_list = []
        for sch in schedules:
            data = {}
            data['schedule_id'] = sch.ScheduleDetail.schedule_id
            data['vehicle_id'] = sch.Schedule.vehicle_id
            data['schedule_status'] = sch.Schedule.schedule_status
            data['rt_regn'] = sch.ScheduleDetail.rt_regn
            data['dist'] = str(sch.ScheduleDetail.dist)
            data['payment'] = str(sch.ScheduleDetail.payment)
            data['created_by'] = sch.ScheduleDetail.created_by
            data['user_name'] =  (sch.User.rkp_name if sch.User.rkp_name != None and sch.User.rkp_name != "" else sch.User.first_name + ' ' + (sch.User.last_name) if sch.User.last_name != None else "") if sch.User else ""
            data['user_id'] = sch.ScheduleDetail.user_id
            data['isRow_Editable'] =  False

            data['PlnStLdDt'] = sch.Schedule.schedule_date.strftime('%d.%m.%Y') if sch.Schedule.schedule_date else ""
            data['Shipment'] = sch.ScheduleDetail.shipment_no if sch.ScheduleDetail.shipment_no else ""
            data['D Note'] = sch.ScheduleDetail.delivery_note_no if sch.ScheduleDetail.delivery_note_no else ""
            data['Name'] = sch.ScheduleDetail.client if sch.ScheduleDetail.client else ""
            data['City'] = sch.ScheduleDetail.loc if sch.ScheduleDetail.loc else ""
            data['Material'] = sch.ScheduleDetail.product if sch.ScheduleDetail.product else ""
            data['Rg'] = sch.ScheduleDetail.rg if sch.ScheduleDetail.rg else ""
            data['PLdTime'] = sch.ScheduleDetail.pld_time if sch.ScheduleDetail.pld_time else ""
            data['Qty'] = str(sch.ScheduleDetail.qty) if sch.ScheduleDetail.qty else ""
            data["T"] = sch.ScheduleDetail.t if sch.ScheduleDetail.t else ""
            data["Plnt"] = sch.ScheduleDetail.plnt if sch.ScheduleDetail.plnt else ""
            data["SC"] = sch.ScheduleDetail.sc if sch.ScheduleDetail.sc else ""
            data["TransPlnDt"] = sch.ScheduleDetail.trans_pln_date.strftime('%d.%m.%Y') if sch.ScheduleDetail.trans_pln_date else ""
            data["Dlvr"] = sch.ScheduleDetail.dlvr if sch.ScheduleDetail.dlvr else ""
            data["S"] = sch.ScheduleDetail.s if sch.ScheduleDetail.s  else ""
            data["ActStLdT"] = sch.ScheduleDetail.act_st_ldt if sch.ScheduleDetail.act_st_ldt else ""
            data["Sold-to"] = sch.ScheduleDetail.sold_to if sch.ScheduleDetail.sold_to else ""
            data["Maximum volume"] = sch.ScheduleDetail.maximum_volume if sch.ScheduleDetail.maximum_volume else ""
            data["ETA time"] = sch.ScheduleDetail.eta_time if sch.ScheduleDetail.eta_time else ""
            data["Ship-to"] = sch.ScheduleDetail.ship_to_party if sch.ScheduleDetail.ship_to_party else ""
            data["ShTy"] = sch.ScheduleDetail.shty if sch.ScheduleDetail.shty else ""

            schedules_list.append(data)

        response_object = {
            "data": schedules_list,
            "count": count,
            "ErrorCode": "9999"
        }

        return response_object, 200

    except Exception as e:

        logging.exception(e)

        response_object = {
            "data": [],
            "count": "0",
            "ErrorCode": "0000",
            "error": str(e)
        }

        return response_object, 200


#
#   feat - Used to get the list of schedule for the RT and the RKP
#
def get_dashboard_schedule_list_v2(page, row, schedule_type, searchterm, schedule_date, tabindex, sortindex):
    try:
        user_query = db.session.query(func.concat(User.first_name, ' ', User.last_name)). \
            filter(User.id == ScheduleDetail.user_id).label("user_name")

        schedule_query = db.session.query(Schedule, ScheduleDetail, User) \
            .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)) \
            .join(User, and_(ScheduleDetail.user_id == User.id)).filter(
            ScheduleDetail.isActive == 1, Schedule.isActive == 1, Schedule.schedule_type == schedule_type)

        if schedule_date:
            report_date = common.convertdmy_to_date2(schedule_date)
            schedule_query = schedule_query.filter(Schedule.schedule_date == report_date)

        if searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            schedule_query = schedule_query.filter(or_(ScheduleDetail.rg.ilike(search),
                                                       ScheduleDetail.rt_regn.ilike(search),
                                                       ScheduleDetail.loc.ilike(search),
                                                       ScheduleDetail.shipment_no.ilike(search),
                                                       ScheduleDetail.client.ilike(search),
                                                       ScheduleDetail.delivery_note_no.ilike(search),
                                                       ScheduleDetail.product.ilike(search),
                                                       User.rkp_name.ilike(search),
                                                       User.first_name.ilike(search),
                                                       User.last_name.ilike(search),
                                                       User.rkp_ic_number.ilike(search)
                                                       ))

        # Sorting functionality
        if tabindex == 1:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.rt_regn))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.rt_regn))
        elif tabindex == 2:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.shipment_no))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.shipment_no))
        elif tabindex == 3:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.delivery_note_no))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.delivery_note_no))
        else:
            schedule_query = schedule_query.order_by(desc(ScheduleDetail.schedule_id))

        schedules = schedule_query.paginate(int(page), int(row), False).items
        count = schedule_query.count()

        schedules_list = []
        for sch in schedules:
            schedules_list.append({
                'schedule_id': sch.ScheduleDetail.schedule_id,
                'vehicle_id': sch.Schedule.vehicle_id,
                'schedule_status': sch.Schedule.schedule_status,
                'rt_regn': sch.ScheduleDetail.rt_regn,
                'schedule_date': sch.Schedule.schedule_date.strftime('%d-%m-%Y') if sch.Schedule.schedule_date else "",
                'shipment_no': sch.ScheduleDetail.shipment_no,
                'delivery_note_no': sch.ScheduleDetail.delivery_note_no,
                'ship_to_party': sch.ScheduleDetail.ship_to_party,
                'client': sch.ScheduleDetail.client,
                'loc': sch.ScheduleDetail.loc,
                'product': sch.ScheduleDetail.product,
                'dist': str(sch.ScheduleDetail.dist),
                'payment': str(sch.ScheduleDetail.payment),
                'Rg': sch.ScheduleDetail.rg,
                'PLdTime': sch.ScheduleDetail.pld_time,
                'Qty': sch.ScheduleDetail.qty,
                'created_by': sch.ScheduleDetail.created_by,
                'user_name': sch.User.rkp_name if sch.User.rkp_name != None and sch.User.rkp_name != "" else
                sch.User.first_name + ' ' + (sch.User.last_name) if sch.User.last_name != None else "",
                'user_id': sch.ScheduleDetail.user_id,
                'isRow_Editable': False

            })

        response_object = {
            "data": schedules_list,
            "count": count,
            "ErrorCode": "9999"
        }

        return response_object, 200

    except Exception as e:

        logging.exception(e)

        response_object = {
            "data": [],
            "count": "0",
            "ErrorCode": "0000",
            "error": str(e)
        }

        return response_object, 200



#
#   feat - Used to get the list of schedule for the RT and the RKP
#
def get_dashboard_schedule_list_v3(page, row, schedule_type, searchterm, schedule_date, tabindex, sortindex):
    try:
        user_query = db.session.query(func.concat(User.first_name, ' ', User.last_name)). \
            filter(User.id == ScheduleDetail.user_id).label("user_name")

        schedule_query = db.session.query(Schedule, ScheduleDetail, User) \
            .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)) \
            .join(User, and_(ScheduleDetail.user_id == User.id)).filter(
            ScheduleDetail.isActive == 1, Schedule.isActive == 1, Schedule.schedule_type == schedule_type)

        if schedule_date:
            report_date = common.convertdmy_to_date2(schedule_date)
            schedule_query = schedule_query.filter(Schedule.schedule_date == report_date)

        if searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            schedule_query = schedule_query.filter(or_(ScheduleDetail.rg.ilike(search),
                                                       ScheduleDetail.rt_regn.ilike(search),
                                                       ScheduleDetail.loc.ilike(search),
                                                       ScheduleDetail.shipment_no.ilike(search),
                                                       ScheduleDetail.client.ilike(search),
                                                       ScheduleDetail.delivery_note_no.ilike(search),
                                                       ScheduleDetail.product.ilike(search),
                                                       User.rkp_name.ilike(search),
                                                       User.first_name.ilike(search),
                                                       User.last_name.ilike(search),
                                                       User.rkp_ic_number.ilike(search)
                                                       ))

        # Sorting functionality
        if tabindex == 1:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.rt_regn))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.rt_regn))
        elif tabindex == 2:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.shipment_no))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.shipment_no))
        elif tabindex == 3:
            if sortindex == 1:
                schedule_query = schedule_query.order_by(asc(ScheduleDetail.delivery_note_no))
            else:
                schedule_query = schedule_query.order_by(desc(ScheduleDetail.delivery_note_no))
        else:
            schedule_query = schedule_query.order_by(desc(ScheduleDetail.schedule_id))

        schedules = schedule_query.paginate(int(page), int(row), False).items
        count = schedule_query.count()

        schedules_list = []
        for sch in schedules:
            data = {}
            data['schedule_id'] = sch.ScheduleDetail.schedule_id
            data['vehicle_id'] = sch.Schedule.vehicle_id
            data['schedule_status'] = sch.Schedule.schedule_status
            data['rt_regn'] = sch.ScheduleDetail.rt_regn
            data['dist'] = str(sch.ScheduleDetail.dist)
            data['payment'] = str(sch.ScheduleDetail.payment)
            data['created_by'] = sch.ScheduleDetail.created_by
            data['user_name'] = sch.User.rkp_name if sch.User.rkp_name != None and sch.User.rkp_name != "" else sch.User.first_name + ' ' + (
                sch.User.last_name) if sch.User.last_name != None else ""
            data['user_id'] = sch.ScheduleDetail.user_id
            data['isRow_Editable'] = False

            data['PlnStLdDt'] = sch.Schedule.schedule_date.strftime('%d.%m.%Y') if sch.Schedule.schedule_date else ""
            data['Shipment'] = sch.ScheduleDetail.shipment_no if sch.ScheduleDetail.shipment_no else ""
            data['D Note'] = sch.ScheduleDetail.delivery_note_no if sch.ScheduleDetail.delivery_note_no else ""
            data['Name'] = sch.ScheduleDetail.client if sch.ScheduleDetail.client else ""
            data['City'] = sch.ScheduleDetail.loc if sch.ScheduleDetail.loc else ""
            data['Material'] = sch.ScheduleDetail.product if sch.ScheduleDetail.product else ""
            data['Rg'] = sch.ScheduleDetail.rg if sch.ScheduleDetail.rg else ""
            data['PLdTime'] = sch.ScheduleDetail.pld_time if sch.ScheduleDetail.pld_time else ""
            data['Qty'] = str(sch.ScheduleDetail.qty) if sch.ScheduleDetail.qty else ""
            data["T"] = sch.ScheduleDetail.t if sch.ScheduleDetail.t else ""
            data["Plnt"] = sch.ScheduleDetail.plnt if sch.ScheduleDetail.plnt else ""
            data["SC"] = sch.ScheduleDetail.sc if sch.ScheduleDetail.sc else ""
            data["TransPlnDt"] = sch.ScheduleDetail.trans_pln_date.strftime('%d.%m.%Y') if sch.ScheduleDetail.trans_pln_date else ""
            data["Dlvr"] = sch.ScheduleDetail.dlvr if sch.ScheduleDetail.dlvr else ""
            data["S"] = sch.ScheduleDetail.s if sch.ScheduleDetail.s else ""
            data["ActStLdT"] = sch.ScheduleDetail.act_st_ldt if sch.ScheduleDetail.act_st_ldt else ""
            data["Sold-to"] = sch.ScheduleDetail.sold_to if sch.ScheduleDetail.sold_to else ""
            data["Maximum volume"] = sch.ScheduleDetail.maximum_volume if sch.ScheduleDetail.maximum_volume else ""
            data["ETA time"] = sch.ScheduleDetail.eta_time if sch.ScheduleDetail.eta_time else ""
            data["Ship-to"] = sch.ScheduleDetail.ship_to_party if sch.ScheduleDetail.ship_to_party else ""
            data["ShTy"] = sch.ScheduleDetail.shty if sch.ScheduleDetail.shty else ""
            
            schedules_list.append(data)

        response_object = {
            "data": schedules_list,
            "count": count,
            "ErrorCode": "9999"
        }

        return response_object, 200

    except Exception as e:

        logging.exception(e)

        response_object = {
            "data": [],
            "count": "0",
            "ErrorCode": "0000",
            "error": str(e)
        }

        return response_object, 200


#
#   feat - Used to get the particular schedule using the schedule id
#
def get_by_id(schedule_id):
    try:
        schedule = Schedule.query.filter_by(isActive=1, schedule_id=schedule_id).first()
        return schedule, 200

    except Exception as e:

        logging.exception(e)
        return {}, 201


#
#   feat - Used to get the particular schedule using the schedule id
#
def get_by_id_v1(schedule_id):
    try:
        # schedule = Schedule.query.filter_by(isActive=1, schedule_id=schedule_id).first()
        user_query = db.session.query(func.concat(User.first_name, ' ', User.last_name)). \
            filter(User.id == ScheduleDetail.user_id).label("user_name")

        schedule = db.session.query(Schedule, ScheduleDetail, user_query) \
            .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)).filter(
            Schedule.schedule_id == schedule_id,
            ScheduleDetail.isActive == 1, Schedule.isActive == 1).all()

        schedules_list = []
        for sch in schedule:
            schedules_list.append({
                'schedule_id': sch.ScheduleDetail.schedule_id,
                'vehicle_id': sch.Schedule.vehicle_id,
                'schedule_status': sch.Schedule.schedule_status,
                'rt_regn': sch.ScheduleDetail.rt_regn,
                'schedule_date': sch.Schedule.schedule_date.strftime('%d.%m.%Y') if sch.Schedule.schedule_date else "",
                'shipment_no': sch.ScheduleDetail.shipment_no,
                'delivery_note_no': sch.ScheduleDetail.delivery_note_no,
                'ship_to_party': sch.ScheduleDetail.ship_to_party,
                'client': sch.ScheduleDetail.client,
                'loc': sch.ScheduleDetail.loc,
                'product': sch.ScheduleDetail.product,
                'dist': str(sch.ScheduleDetail.dist),
                'payment': str(sch.ScheduleDetail.payment),
                'Rg': sch.ScheduleDetail.rg,
                'PLdTime': sch.ScheduleDetail.pld_time,
                'Qty': sch.ScheduleDetail.qty,
                'created_by': sch.ScheduleDetail.created_by,
                'user_name': sch.user_name,
                'user_id': sch.ScheduleDetail.user_id
            })

        return schedules_list, 200

    except Exception as e:

        logging.exception(e)
        return {}, 201

#
#   feat - Used to delete the schedule using the schedule id
#
def delete_schedule(data):
    try:
        schedule = Schedule.query.filter_by(isActive=1, schedule_id=data["schedule_id"]).first()

        if schedule:
            schedule.isActive = "0"
            schedule.updated_by = data["userid"]
            schedule.updated_date = datetime.datetime.utcnow()

            save_changes(schedule)

            response_object = {
                "ErrorCode": "9999",
                "Status": "Schedule delete successfully"
            }

        else:
            response_object = {
                "ErrorCode": "9997",
                "Status": "Schedule not exists"
            }
        return response_object, 201

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule delete failed"
        }

        return response_object, 201


#
#   feat - Used to delete the schedule using the schedule id
#
def delete_schedule_v1(data):
    try:
        schedule = Schedule.query.filter_by(isActive=1, schedule_id=data["schedule_id"]).first()

        if schedule:
            schedule.isActive = "0"
            schedule.updated_by = data["userid"]
            schedule.updated_date = datetime.datetime.utcnow()

            save_changes(schedule)

        schedule_detail = ScheduleDetail.query.filter_by(isActive=1, schedule_id=data["schedule_id"]).all()

        if schedule_detail:
            for detail in schedule_detail:
                detail.isActive = "0"
                detail.updated_by = data["userid"]
                detail.updated_date = datetime.datetime.utcnow()

                save_changes(detail)

            response_object = {
                "ErrorCode": "9999",
                "Status": "Schedule delete successfully"
            }

        else:
            response_object = {
                "ErrorCode": "9997",
                "Status": "Schedule not exists"
            }
        return response_object, 201

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule delete failed"
        }

        return response_object, 201


#
#   feat - Used to add/update multiple schedules
#
def add_multiple_schedule_v1(data):
    try:
        schedule_res_total = []
        for schedule_data in data["schedule"]:
            schedule_res = add_schedule_v1(schedule_data, data["userid"])
            if schedule_res:
                schedule_res_total.append(schedule_res)
        response_object = {
            "ErrorCode": "9999",
            "Status": "Schedule added successfully",
            "schedule_res": schedule_res_total
        }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule add failed",
            "Error": e
        }

        return response_object, 201


#
#   feat - Used to add/update multiple schedules
#
def add_multiple_schedule_v2(data):
    try:
        schedule_res_total = []
        for schedule_data in data["schedule"]:
            schedule_res = add_schedule_v2(schedule_data, data["userid"], data['schedule_type'])
            if schedule_res:
                schedule_res_total.append(schedule_res)
        response_object = {
            "ErrorCode": "9999",
            "Status": "Schedule added successfully",
            "schedule_res": schedule_res_total
        }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule add failed",
            "Error": e
        }

        return response_object, 201


#
#   feat - Used to add/update multiple schedules
#
def add_multiple_schedule_v3(data):
    try:
        schedule_res_total = []
        for schedule_data in data["schedule"]:
            schedule_res = add_schedule_v3(schedule_data, data["userid"], data['schedule_type'])
            if schedule_res:
                schedule_res_total.append(schedule_res)
        response_object = {
            "ErrorCode": "9999",
            "Status": "Schedule added successfully",
            "schedule_res": schedule_res_total
        }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule add failed",
            "Error": e
        }

        return response_object, 201


#
#   feat - Used to add/update multiple schedules
#
def add_multiple_schedule(data):
    try:
        schedule_res_total = []
        for schedule_data in data["schedule"]:
            schedule_res = add_schedule(schedule_data, data["userid"])
            if schedule_res:
                schedule_res_total.append(schedule_res)
        response_object = {
            "ErrorCode": "9999",
            "Status": "Schedule added successfully",
            "schedule_res": schedule_res_total
        }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule add failed",
            "Error": e
        }

        return response_object, 201


#
#   feat - Used to get the RT information for the particular RKP
#
def upload_doc(file):
    try:
        import_data_list = []
        if file:
            org_filename = secure_filename(file.filename)
            ext = org_filename.split('.')[1]
            uuid_file = str(uuid.uuid4())
            uuid_filename = uuid_file + "." + ext
            directory = os.path.join(doc_savedir)
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_path = os.path.join(doc_savedir, uuid_filename)
            file.save(file_path)
            new_doc = Schedule_Document(document_path=file_path,
                                        original_file_name=org_filename,
                                        uuid_file_name=uuid_filename,
                                        created_date=datetime.datetime.utcnow())
            save_changes(new_doc)
            ext = ext.lower().strip() if ext else ''
            if ext == 'xlsx':

                wb = xlrd.open_workbook(file_path)
                sheet_list = wb.sheet_names()

                columns_list = ['RoadTanker', 'PlnStLdDt', 'T', 'Shipment', 'D Note', 'Name', 'Rg', 'City', 'Material',
                                'Qty', 'PLdTime']

                for sheet_name in sheet_list:

                    column_row_no = {}
                    row_start = 0

                    sheet = wb.sheet_by_name(sheet_name)

                    for row in range(sheet.nrows):
                        if row < 20:
                            for column in range(sheet.ncols):
                                column_name = sheet.cell(row, column).value
                                if column_name == columns_list[0]:
                                    row_start = row
                            if row_start > 0:
                                break

                    for given_column in columns_list:

                        for column in range(sheet.ncols):
                            column_name = sheet.cell(row_start, column).value.strip()
                            if column_name == given_column:
                                column_row_no[given_column] = column

                    for row in range(sheet.nrows):
                        if row > row_start:
                            RoadTanker = sheet.cell(row, column_row_no['RoadTanker']).value
                            ClientName = sheet.cell(row, column_row_no['Name']).value
                            Product = sheet.cell(row, column_row_no['Material']).value
                            QTY = sheet.cell(row, column_row_no['Qty']).value

                            if RoadTanker != '' and common.hasNumbers(
                                    RoadTanker) and ClientName != '' and Product != '' and QTY != '':
                                val = {}
                                # val['rt_regn'] = sheet.cell(row, column_row_no['RoadTanker']).value
                                val['road_tanker'] = RoadTanker
                                val['rt_regn'] = ""
                                val['schedule_date'] = sheet.cell(row, column_row_no['PlnStLdDt']).value

                                ship_no = sheet.cell(row, column_row_no['Shipment']).value

                                if type(ship_no) is float:
                                    ship_no = int(ship_no)
                                    ship_no = str(ship_no)

                                val['shipment_no'] = ship_no

                                delivery_no = sheet.cell(row, column_row_no['D Note']).value

                                if type(delivery_no) is float:
                                    delivery_no = int(delivery_no)
                                    delivery_no = str(delivery_no)

                                val['delivery_note_no'] = delivery_no

                                product = sheet.cell(row, column_row_no['Material']).value

                                if type(product) is float:
                                    product = int(product)
                                    product = str(product)

                                val['product'] = product

                                qty = sheet.cell(row, column_row_no['Qty']).value

                                if type(qty) is float:
                                    qty = int(qty)
                                    qty = str(qty)

                                val['Qty'] = qty

                                PLdTime = sheet.cell(row, column_row_no['PLdTime']).value
                                if type(PLdTime) is float:
                                    date_values = xlrd.xldate_as_tuple(PLdTime, wb.datemode)
                                    PLdTime = datetime.time(*date_values[3:])
                                    PLdTime = PLdTime.strftime("%H:%M:%S %p")

                                val['PLdTime'] = PLdTime

                                val['client'] = sheet.cell(row, column_row_no['Name']).value
                                val['loc'] = sheet.cell(row, column_row_no['City']).value
                                val['Rg'] = sheet.cell(row, column_row_no['Rg']).value
                                val['schedule_id'] = 0
                                val['user_id'] = 0
                                val['vehicle_id'] = 0
                                val['schedule_status'] = 0
                                val['ship_to_party'] = ""
                                val['dist'] = ""
                                val['payment'] = ""
                                val['created_by'] = 1

                                import_data_list.append(val)

            response_obj = {
                "ErrorCode": 9999,
                "uuid_filename": uuid_filename,
                "org_filename": org_filename,
                "doc_id": new_doc.id,
                "import_data_list": import_data_list
            }
            if ext != 'xlsx':
                response_obj['Error'] = 'Unsupported extension :' + ext
        else:
            response_obj = {
                "ErrorCode": 9998,
                "uuid_filename": "",
                "org_filename": ""
            }
        return response_obj, 201
    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule Upload failed",
            "Error": str(e)
        }

        return response_object, 201


#
#   feat - Used to get the RT information for the particular RKP
#
def upload_doc_v2(file):
    try:
        import_data_list = []
        if file:
            org_filename = secure_filename(file.filename)
            ext = org_filename.split('.')[-1]
            uuid_file = str(uuid.uuid4())
            uuid_filename = uuid_file + "." + ext
            directory = os.path.join(doc_savedir)
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_path = os.path.join(doc_savedir, uuid_filename)
            file.save(file_path)
            new_doc = Schedule_Document(document_path=file_path,
                                        original_file_name=org_filename,
                                        uuid_file_name=uuid_filename,
                                        created_date=datetime.datetime.utcnow())
            save_changes(new_doc)
            ext = ext.lower().strip() if ext else ''
            if ext == 'xlsx':

                wb = xlrd.open_workbook(file_path)

                columns_list = ['RoadTanker', 'PlnStLdDt', 'T', 'Shipment', 'D Note', 'Name', 'Rg', 'City', 'Material',
                                'Qty', 'PLdTime']

                column_row_no = {}
                row_start = 0

                sheet = wb.sheet_by_index(0)

                for row in range(sheet.nrows):
                    if row < 20:
                        for column in range(sheet.ncols):
                            column_name = sheet.cell(row, column).value
                            if column_name == columns_list[0]:
                                row_start = row
                        if row_start > 0:
                            break

                for given_column in columns_list:

                    for column in range(sheet.ncols):
                        column_name = sheet.cell(row_start, column).value.strip()
                        if column_name == given_column:
                            column_row_no[given_column] = column

                for row in range(sheet.nrows):
                    if row > row_start:
                        RoadTanker = sheet.cell(row, column_row_no['RoadTanker']).value
                        ClientName = sheet.cell(row, column_row_no['Name']).value
                        Product = sheet.cell(row, column_row_no['Material']).value
                        QTY = sheet.cell(row, column_row_no['Qty']).value

                        if RoadTanker != '' and common.hasNumbers(
                                RoadTanker) and ClientName != '' and Product != '' and QTY != '':
                            val = {}
                            # val['rt_regn'] = sheet.cell(row, column_row_no['RoadTanker']).value
                            val['road_tanker'] = RoadTanker
                            val['rt_regn'] = ""
                            val['schedule_date'] = sheet.cell(row, column_row_no['PlnStLdDt']).value

                            ship_no = sheet.cell(row, column_row_no['Shipment']).value

                            if type(ship_no) is float:
                                ship_no = int(ship_no)
                                ship_no = str(ship_no)

                            val['shipment_no'] = ship_no

                            delivery_no = sheet.cell(row, column_row_no['D Note']).value

                            if type(delivery_no) is float:
                                delivery_no = int(delivery_no)
                                delivery_no = str(delivery_no)

                            val['delivery_note_no'] = delivery_no

                            product = sheet.cell(row, column_row_no['Material']).value

                            if type(product) is float:
                                product = int(product)
                                product = str(product)

                            val['product'] = product

                            qty = sheet.cell(row, column_row_no['Qty']).value

                            if type(qty) is float:
                                qty = int(qty)
                                qty = str(qty)

                            val['Qty'] = qty

                            PLdTime = sheet.cell(row, column_row_no['PLdTime']).value
                            if type(PLdTime) is float:
                                date_values = xlrd.xldate_as_tuple(PLdTime, wb.datemode)
                                PLdTime = datetime.time(*date_values[3:])
                                PLdTime = PLdTime.strftime("%H:%M:%S %p")

                            val['PLdTime'] = PLdTime

                            val['client'] = sheet.cell(row, column_row_no['Name']).value
                            val['loc'] = sheet.cell(row, column_row_no['City']).value
                            val['Rg'] = sheet.cell(row, column_row_no['Rg']).value
                            val['schedule_id'] = 0
                            val['user_id'] = 0
                            val['vehicle_id'] = 0
                            val['schedule_status'] = 0
                            val['ship_to_party'] = ""
                            val['dist'] = ""
                            val['payment'] = ""
                            val['created_by'] = 1
                            val['isRow_Editable'] = True

                            import_data_list.append(val)

            response_obj = {
                "ErrorCode": 9999,
                "uuid_filename": uuid_filename,
                "org_filename": org_filename,
                "doc_id": new_doc.id,
                "import_data_list": import_data_list
            }
            if ext != 'xlsx':
                response_obj['Error'] = 'Unsupported extension :' + ext
        else:
            response_obj = {
                "ErrorCode": 9998,
                "uuid_filename": "",
                "org_filename": ""
            }
        return response_obj, 201
    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule Upload failed",
            "Error": str(e)
        }

        return response_object, 201


#
#   feat - Used to get the RT information for the particular RKP
#
def upload_doc_v3(file):
    try:
        import_data_list = []
        if file:
            org_filename = secure_filename(file.filename)
            ext = org_filename.split('.')[-1]
            uuid_file = str(uuid.uuid4())
            uuid_filename = uuid_file + "." + ext
            directory = os.path.join(doc_savedir)
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_path = os.path.join(doc_savedir, uuid_filename)
            file.save(file_path)
            new_doc = Schedule_Document(document_path=file_path,
                                        original_file_name=org_filename,
                                        uuid_file_name=uuid_filename,
                                        created_date=datetime.datetime.utcnow())
            save_changes(new_doc)
            ext = ext.lower().strip() if ext else ''
            if ext == 'xlsx':

                wb = xlrd.open_workbook(file_path)

                columns_list = ['RoadTanker', 'PlnStLdDt', 'T', 'Shipment', 'D Note', 'Name', 'Rg', 'City', 'Material',
                                'Qty', 'PLdTime', 'Plnt', 'SC', 'TransPlnDt', 'Dlvr', 'S', 'ActStLdT', 'Ship-to',
                                'Maximum volume', 'ETA time', 'Sold-to']

                column_row_no = {}
                row_start = 0

                sheet = wb.sheet_by_index(0)

                for row in range(sheet.nrows):
                    if row < 20:
                        for column in range(sheet.ncols):
                            column_name = sheet.cell(row, column).value
                            if column_name == columns_list[0]:
                                row_start = row
                        if row_start > 0:
                            break

                for given_column in columns_list:

                    for column in range(sheet.ncols):
                        column_name = sheet.cell(row_start, column).value.strip()
                        if column_name == given_column:
                            column_row_no[given_column] = column

                for row in range(sheet.nrows):
                    if row > row_start:

                        RoadTanker = sheet.cell(row, column_row_no['RoadTanker']).value
                        ClientName = sheet.cell(row, column_row_no['Name']).value
                        Product = sheet.cell(row, column_row_no['Material']).value
                        QTY = sheet.cell(row, column_row_no['Qty']).value

                        if RoadTanker != '' and common.hasNumbers(
                                RoadTanker) and ClientName != '' and Product != '' and QTY != '':

                            val = {}
                            # val['rt_regn'] = sheet.cell(row, column_row_no['RoadTanker']).value
                            val['road_tanker'] = RoadTanker
                            val['rt_regn'] = ""

                            if 'PlnStLdDt' in column_row_no:
                                val['PlnStLdDt'] = sheet.cell(row, column_row_no['PlnStLdDt']).value
                            else:
                                val['PlnStLdDt'] = ''

                            if 'Shipment' in column_row_no:
                                ship_no = sheet.cell(row, column_row_no['Shipment']).value

                                if type(ship_no) is float:
                                    ship_no = int(ship_no)
                                    ship_no = str(ship_no)

                                val['Shipment'] = ship_no
                            else:
                                val['Shipment'] = ''

                            if 'D Note' in column_row_no:
                                delivery_no = sheet.cell(row, column_row_no['D Note']).value

                                if type(delivery_no) is float:
                                    delivery_no = int(delivery_no)
                                    delivery_no = str(delivery_no)

                                val['D Note'] = delivery_no
                            else:
                                val['D Note'] = delivery_no


                            if 'T' in column_row_no:
                                delivery_no = sheet.cell(row, column_row_no['T']).value

                                if type(delivery_no) is float:
                                    delivery_no = int(delivery_no)
                                    delivery_no = str(delivery_no)

                                val['T'] = delivery_no
                            else:
                                val['T'] = delivery_no

                            if 'Material' in column_row_no:
                                product = sheet.cell(row, column_row_no['Material']).value

                                if type(product) is float:
                                    product = int(product)
                                    product = str(product)

                                val['Material'] = product
                            else:
                                val['Material'] = ''

                            if 'Qty' in column_row_no:
                                qty = sheet.cell(row, column_row_no['Qty']).value

                                if type(qty) is float:
                                    qty = int(qty)
                                    qty = str(qty)

                                val['Qty'] = qty

                            else:
                                val['Qty'] = ''

                            if 'PLdTime' in column_row_no:

                                PLdTime = sheet.cell(row, column_row_no['PLdTime']).value
                                if type(PLdTime) is float:
                                    date_values = xlrd.xldate_as_tuple(PLdTime, wb.datemode)
                                    PLdTime = datetime.time(*date_values[3:])
                                    PLdTime = PLdTime.strftime("%H:%M:%S %p")

                                val['PLdTime'] = PLdTime

                            else:
                                val['PLdTime'] = ''

                            if 'Name' in column_row_no:
                                val['Name'] = sheet.cell(row, column_row_no['Name']).value
                            else:
                                val['Name'] = ''

                            if 'City' in column_row_no:
                                val['City'] = sheet.cell(row, column_row_no['City']).value
                            else:
                                val['City'] = ''

                            if 'Rg' in column_row_no:
                                val['Rg'] = sheet.cell(row, column_row_no['Rg']).value
                            else:
                                val['Rg'] = ''

                            if 'Plnt' in column_row_no:
                                val['Plnt'] = sheet.cell(row, column_row_no['Plnt']).value
                            else:
                                val['Plnt'] = ''

                            if 'SC' in column_row_no:
                                val['SC'] = sheet.cell(row, column_row_no['SC']).value
                            else:
                                val['SC'] = ''

                            if 'TransPlnDt' in column_row_no:

                                TransPlnDt = sheet.cell(row, column_row_no['TransPlnDt']).value
                                if type(TransPlnDt) is float:
                                    date_values = xlrd.xldate_as_tuple(TransPlnDt, wb.datemode)
                                    TransPlnDt = datetime.time(*date_values[3:])
                                    TransPlnDt = TransPlnDt.strftime("%d.%m.%Y")

                                val['TransPlnDt'] = TransPlnDt
                            else:
                                val['TransPlnDt'] = ''

                            if 'Dlvr' in column_row_no:
                                val['Dlvr'] = sheet.cell(row, column_row_no['Dlvr']).value
                            else:
                                val['Dlvr'] = ''

                            if 'S' in column_row_no:

                                S_Val = sheet.cell(row, column_row_no['S']).value
                                if type(S_Val) is float:
                                    S_Val = int(S_Val)
                                    S_Val = str(S_Val)

                                val['S'] = S_Val

                            else:
                                val['S'] = ''

                            if 'ActStLdT' in column_row_no:

                                ActStLdT = sheet.cell(row, column_row_no['ActStLdT']).value
                                if type(ActStLdT) is float:
                                    date_values = xlrd.xldate_as_tuple(ActStLdT, wb.datemode)
                                    ActStLdT = datetime.time(*date_values[3:])
                                    ActStLdT = ActStLdT.strftime("%H:%M:%S %p")

                                val['ActStLdT'] = ActStLdT

                            else:
                                val['ActStLdT'] = ''

                            if 'Ship-to' in column_row_no:
                                Ship_to = sheet.cell(row, column_row_no['Ship-to']).value
                                if type(Ship_to) is float:
                                    Ship_to = int(Ship_to)
                                    Ship_to = str(Ship_to)

                                val['Ship-to'] = Ship_to

                            else:
                                val['Ship-to'] = ''

                            if 'Maximum volume' in column_row_no:

                                Maximum_volume = sheet.cell(row, column_row_no['Maximum volume']).value
                                if type(Maximum_volume) is float:
                                    Maximum_volume = int(Maximum_volume)
                                    Maximum_volume = str(Maximum_volume)

                                val['Maximum volume'] = Maximum_volume
                            else:
                                val['Maximum volume'] = ''

                            if 'ETA time' in column_row_no:

                                ETA_time = sheet.cell(row, column_row_no['ETA time']).value
                                if type(ETA_time) is float:
                                    date_values = xlrd.xldate_as_tuple(ETA_time, wb.datemode)
                                    ETA_time = datetime.time(*date_values[3:])
                                    ETA_time = ETA_time.strftime("%H:%M:%S %p")

                                val['ETA time'] = ETA_time

                            else:
                                val['ETA time'] = ''

                            if 'Sold-to' in column_row_no:

                                Sold_to = sheet.cell(row, column_row_no['Sold-to']).value
                                if type(Sold_to) is float:
                                    Sold_to = int(Sold_to)
                                    Sold_to = str(Sold_to)

                                val['Sold-to'] = Ship_to

                            else:
                                val['Sold-to'] = ''

                            val['schedule_id'] = 0
                            val['user_id'] = 0
                            val['vehicle_id'] = 0
                            val['schedule_status'] = 0
                            val['ship_to_party'] = ""
                            val['dist'] = ""
                            val['payment'] = ""
                            val['created_by'] = 1
                            val['isRow_Editable'] = True

                            import_data_list.append(val)

            response_obj = {
                "ErrorCode": 9999,
                "uuid_filename": uuid_filename,
                "org_filename": org_filename,
                "doc_id": new_doc.id,
                "import_data_list": import_data_list
            }
            if ext != 'xlsx':
                response_obj['Error'] = 'Unsupported extension :' + ext
        else:
            response_obj = {
                "ErrorCode": 9998,
                "uuid_filename": "",
                "org_filename": ""
            }
        return response_obj, 201
    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule Upload failed",
            "Error": str(e)
        }

        return response_object, 201



#
#   feat - Used to get the RT information for the particular RKP
#
def upload_doc_v4(file):
    try:
        import_data_list = []

        shipment_no_list = []
        rt_regn_list = []
        latest_schedule_date = ""


        if file:
            org_filename = secure_filename(file.filename)
            ext = org_filename.split('.')[-1]
            uuid_file = str(uuid.uuid4())
            uuid_filename = uuid_file + "." + ext
            directory = os.path.join(doc_savedir)
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_path = os.path.join(doc_savedir, uuid_filename)
            file.save(file_path)
            new_doc = Schedule_Document(document_path=file_path,
                                        original_file_name=org_filename,
                                        uuid_file_name=uuid_filename,
                                        created_date=datetime.datetime.utcnow())
            save_changes(new_doc)
            ext = ext.lower().strip() if ext else ''
            if (ext == 'xlsx' or ext == 'xls'):

                wb = xlrd.open_workbook(file_path)

                columns_list = ['RoadTanker', 'PlnStLdDt', 'T', 'Shipment', 'D Note', 'Name', 'Rg', 'City', 'Material',
                                'Qty', 'PLdTime', 'Plnt', 'SC', 'TransPlnDt', 'Dlvr', 'S', 'ActStLdT', 'Ship-to',
                                'Maximum volume', 'ETA time', 'Sold-to','ShTy']

                column_row_no = {}
                row_start = 0

                sheet = wb.sheet_by_index(0)

                for row in range(sheet.nrows):
                    if row < 20:
                        for column in range(sheet.ncols):
                            column_name = sheet.cell(row, column).value
                            if column_name == columns_list[0]:
                                row_start = row
                        if row_start > 0:
                            break

                for given_column in columns_list:

                    for column in range(sheet.ncols):
                        column_name = sheet.cell(row_start, column).value.strip()
                        if column_name == given_column:
                            column_row_no[given_column] = column

                for row in range(sheet.nrows):
                    if row > row_start:

                        RoadTanker = sheet.cell(row, column_row_no['RoadTanker']).value
                        ClientName = sheet.cell(row, column_row_no['Name']).value
                        Product = sheet.cell(row, column_row_no['Material']).value
                        QTY = sheet.cell(row, column_row_no['Qty']).value

                        if RoadTanker != '' and common.hasNumbers(
                                RoadTanker) and ClientName != '' and Product != '' and QTY != '':

                            val = {}
                            # val['rt_regn'] = sheet.cell(row, column_row_no['RoadTanker']).value
                            val['road_tanker'] = RoadTanker

                            if RoadTanker.replace(' ', '') not in rt_regn_list:
                                rt_regn_list.append(RoadTanker.replace(' ', ''))


                            return_obj = CheckRTRegn(RoadTanker)
                            if not return_obj['rt_available']:
                                val['rt_regn'] = return_obj['rt_regn']
                                val['vehicle_id'] = return_obj['rt_regn_id']
                            else:
                                val['rt_regn'] = ""
                                val['vehicle_id'] = 0

                            if 'PlnStLdDt' in column_row_no:
                                sch_date = sheet.cell(row, column_row_no['PlnStLdDt']).value
                                val['PlnStLdDt'] = sch_date

                                if latest_schedule_date == "":
                                    latest_schedule_date = datetime.datetime.strptime(sch_date, "%d.%m.%Y").strftime('%d/%m/%Y')
                                else:
                                    prev_sch_date = latest_schedule_date
                                    curr_sch_date = sch_date

                                    if datetime.datetime.strptime(curr_sch_date, "%d.%m.%Y") > datetime.datetime.strptime(prev_sch_date, "%d/%m/%Y"):
                                        latest_schedule_date = datetime.datetime.strptime(sch_date, "%d.%m.%Y").strftime('%d/%m/%Y')

                            else:
                                val['PlnStLdDt'] = ''

                            if 'Shipment' in column_row_no:
                                ship_no = sheet.cell(row, column_row_no['Shipment']).value

                                if type(ship_no) is float:
                                    ship_no = int(ship_no)
                                    ship_no = str(ship_no)

                                if ship_no not in shipment_no_list:
                                    shipment_no_list.append(ship_no)

                                val['Shipment'] = ship_no
                            else:
                                val['Shipment'] = ''

                            if 'D Note' in column_row_no:
                                delivery_no = sheet.cell(row, column_row_no['D Note']).value

                                if type(delivery_no) is float:
                                    delivery_no = int(delivery_no)
                                    delivery_no = str(delivery_no)

                                val['D Note'] = delivery_no
                            else:
                                val['D Note'] = delivery_no


                            if 'T' in column_row_no:
                                delivery_no = sheet.cell(row, column_row_no['T']).value

                                if type(delivery_no) is float:
                                    delivery_no = int(delivery_no)
                                    delivery_no = str(delivery_no)

                                val['T'] = delivery_no
                            else:
                                val['T'] = delivery_no

                            if 'Material' in column_row_no:
                                product = sheet.cell(row, column_row_no['Material']).value

                                if type(product) is float:
                                    product = int(product)
                                    product = str(product)

                                val['Material'] = product
                            else:
                                val['Material'] = ''

                            if 'Qty' in column_row_no:
                                qty = sheet.cell(row, column_row_no['Qty']).value

                                if type(qty) is float:
                                    qty = int(qty)
                                    qty = str(qty)

                                val['Qty'] = qty

                            else:
                                val['Qty'] = ''

                            if 'PLdTime' in column_row_no:

                                PLdTime = sheet.cell(row, column_row_no['PLdTime']).value
                                if type(PLdTime) is float:
                                    date_values = xlrd.xldate_as_tuple(PLdTime, wb.datemode)
                                    PLdTime = datetime.time(*date_values[3:])
                                    PLdTime = PLdTime.strftime("%H:%M:%S %p")

                                val['PLdTime'] = PLdTime

                            else:
                                val['PLdTime'] = ''

                            if 'Name' in column_row_no:
                                val['Name'] = sheet.cell(row, column_row_no['Name']).value
                            else:
                                val['Name'] = ''

                            if 'City' in column_row_no:
                                val['City'] = sheet.cell(row, column_row_no['City']).value
                            else:
                                val['City'] = ''

                            if 'ShTy' in column_row_no:
                                val['ShTy'] = sheet.cell(row, column_row_no['ShTy']).value
                            else:
                                val['ShTy'] = ''

                            if 'Rg' in column_row_no:
                                val['Rg'] = sheet.cell(row, column_row_no['Rg']).value
                            else:
                                val['Rg'] = ''

                            if 'Plnt' in column_row_no:
                                val['Plnt'] = sheet.cell(row, column_row_no['Plnt']).value
                            else:
                                val['Plnt'] = ''

                            if 'SC' in column_row_no:
                                val['SC'] = sheet.cell(row, column_row_no['SC']).value
                            else:
                                val['SC'] = ''

                            if 'TransPlnDt' in column_row_no:

                                TransPlnDt = sheet.cell(row, column_row_no['TransPlnDt']).value
                                if type(TransPlnDt) is float:
                                    date_values = xlrd.xldate_as_tuple(TransPlnDt, wb.datemode)
                                    TransPlnDt = datetime.time(*date_values[3:])
                                    TransPlnDt = TransPlnDt.strftime("%d.%m.%Y")

                                val['TransPlnDt'] = TransPlnDt
                            else:
                                val['TransPlnDt'] = ''

                            if 'Dlvr' in column_row_no:
                                val['Dlvr'] = sheet.cell(row, column_row_no['Dlvr']).value
                            else:
                                val['Dlvr'] = ''

                            if 'S' in column_row_no:

                                S_Val = sheet.cell(row, column_row_no['S']).value
                                if type(S_Val) is float:
                                    S_Val = int(S_Val)
                                    S_Val = str(S_Val)

                                val['S'] = S_Val

                            else:
                                val['S'] = ''

                            if 'ActStLdT' in column_row_no:

                                ActStLdT = sheet.cell(row, column_row_no['ActStLdT']).value
                                if type(ActStLdT) is float:
                                    date_values = xlrd.xldate_as_tuple(ActStLdT, wb.datemode)
                                    ActStLdT = datetime.time(*date_values[3:])
                                    ActStLdT = ActStLdT.strftime("%H:%M:%S %p")

                                val['ActStLdT'] = ActStLdT

                            else:
                                val['ActStLdT'] = ''

                            if 'Ship-to' in column_row_no:
                                Ship_to = sheet.cell(row, column_row_no['Ship-to']).value
                                if type(Ship_to) is float:
                                    Ship_to = int(Ship_to)
                                    Ship_to = str(Ship_to)

                                val['Ship-to'] = Ship_to

                            else:
                                val['Ship-to'] = ''

                            if 'Maximum volume' in column_row_no:

                                Maximum_volume = sheet.cell(row, column_row_no['Maximum volume']).value
                                if type(Maximum_volume) is float:
                                    Maximum_volume = int(Maximum_volume)
                                    Maximum_volume = str(Maximum_volume)

                                val['Maximum volume'] = Maximum_volume
                            else:
                                val['Maximum volume'] = ''

                            if 'ETA time' in column_row_no:

                                ETA_time = sheet.cell(row, column_row_no['ETA time']).value
                                if type(ETA_time) is float:
                                    date_values = xlrd.xldate_as_tuple(ETA_time, wb.datemode)
                                    ETA_time = datetime.time(*date_values[3:])
                                    ETA_time = ETA_time.strftime("%H:%M:%S %p")

                                val['ETA time'] = ETA_time

                            else:
                                val['ETA time'] = ''

                            if 'Sold-to' in column_row_no:

                                Sold_to = sheet.cell(row, column_row_no['Sold-to']).value
                                if type(Sold_to) is float:
                                    Sold_to = int(Sold_to)
                                    Sold_to = str(Sold_to)

                                val['Sold-to'] = Ship_to

                            else:
                                val['Sold-to'] = ''

                            val['schedule_id'] = 0
                            val['user_id'] = 0
                            val['schedule_status'] = 0
                            val['ship_to_party'] = ""
                            val['dist'] = ""
                            val['payment'] = ""
                            val['created_by'] = 1
                            val['isRow_Editable'] = True

                            import_data_list.append(val)

            response_obj = {
                "ErrorCode": 9999,
                "uuid_filename": uuid_filename,
                "org_filename": org_filename,
                "doc_id": new_doc.id,
                "import_data_list": import_data_list,
                "total_shipment_no":len(shipment_no_list),
                "total_rt_regn_no":len(rt_regn_list),
                "latest_schedule_date":latest_schedule_date,
                "update_date":datetime.datetime.now().strftime("%H:%M %p")
            }
        else:
            response_obj = {
                "ErrorCode": 9998,
                "uuid_filename": "",
                "org_filename": "",
                "Error": "File Not Uploaded,Please Try Again"
            }
        return response_obj, 201

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": 0000,
            "Status": "Schedule Upload failed",
            "Error": str(e)
        }

        return response_object, 201



def CheckRTRegn(rt_regn):
    try:

        rt_id = 0

        is_rt_available = False

        rt_arr = []
        rt_arr.append(rt_regn)
        rt_arr.append(rt_regn.replace(' ', ''))

        vehicle = Vehicle.query.filter(Vehicle.regn_no.in_(rt_arr),Vehicle.isActive == 1).first()


        if vehicle:

            rt_id = vehicle.id

            pdc_defect_list = db.session.query(PDCRegistration, InspectionItem, Vehicle) \
                .join(InspectionItem, and_(PDCRegistration.pdc_registration_id == InspectionItem.reference_id)) \
                .join(Vehicle, and_(PDCRegistration.vehicle_id == Vehicle.id))

            pdc_defect_list = pdc_defect_list.filter(PDCRegistration.vehicle_id == vehicle.id,InspectionItem.workshop_status != 2,PDCRegistration.completed_status != 1).\
                                filter(or_(InspectionItem.approval_category == 1,InspectionItem.approval_category == 2)).all()

            if pdc_defect_list:
                is_rt_available = True
        else:
            is_rt_available = True

        response_object = {
            "rt_regn": rt_regn.replace(' ', ''),
            "rt_regn_id": rt_id,
            "rt_available": is_rt_available
        }

        return response_object

    except Exception as e:
        logging.exception(e)

        response_object = {
            "rt_regn": rt_regn,
            "rt_regn_id": 0,
            "rt_available": False
        }

        return response_object

#
#   feat - used to get the available RKP list
#
def get_available_rkp(page, row, searchterm, tabindex, sortindex, user_id,schedule_detail_id,schedule_date):
    try:
        available_query = User.query.filter_by(isActive=1)
        available_query = available_query.filter(User.roles.any(RKP_RoleId))
        schedule_date=common.convertdmy_to_date2(schedule_date)
        if schedule_detail_id != "0" and schedule_detail_id != "" and schedule_detail_id != "\"\"":
            available_query = available_query.filter(or_(~Schedule.query.join(ScheduleDetail,Schedule.schedule_id==ScheduleDetail.schedule_id).filter(Schedule.schedule_date == schedule_date,User.id==ScheduleDetail.user_id,Schedule.isActive==1,ScheduleDetail.isActive==1).exists()
                                                 ,Schedule.query.join(ScheduleDetail,Schedule.schedule_id==ScheduleDetail.schedule_id).filter(ScheduleDetail.schedule_detail_id == schedule_detail_id,User.id==ScheduleDetail.user_id,Schedule.isActive==1,ScheduleDetail.isActive==1).exists()))
        else:
            available_query = available_query.filter(
                ~Schedule.query.join(ScheduleDetail, Schedule.schedule_id == ScheduleDetail.schedule_id).filter(
                    Schedule.schedule_date == schedule_date, User.id == ScheduleDetail.user_id,Schedule.isActive==1,ScheduleDetail.isActive==1).exists()
            )
        if searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            available_query = available_query.filter(or_(User.reg_no.ilike(search),
                                                         User.rkp_name.ilike(search),
                                                         User.first_name.ilike(search),
                                                         User.last_name.ilike(search)))

        # Sorting functionality
        if user_id > 0:
            available_query = available_query.order_by(asc(case(
                [
                    (
                        User.id == user_id,
                        1
                    )
                ],
                else_=2
            )))

        if tabindex == 1:
            if sortindex == 1:
                available_query = available_query.order_by(asc(User.first_name))
            else:
                available_query = available_query.order_by(desc(User.first_name))
        elif tabindex == 2:
            if sortindex == 1:
                available_query = available_query.order_by(asc(User.reg_no))
            else:
                available_query = available_query.order_by(desc(User.reg_no))
        else:
            available_query = available_query.order_by(desc(User.id))

        rkp_data = available_query.paginate(int(page), int(row), False).items
        count = available_query.count()
        rkp_list = []
        if rkp_data:
            for rkp in rkp_data:

                name = rkp.rkp_name if rkp.rkp_name != None and rkp.rkp_name != "" else rkp.first_name + (
                    "" if rkp.last_name == None else rkp.last_name)

                if name != "" and name != None:
                    data = {
                        "user_id": rkp.id,
                        "first_name": name,
                        "last_name": "",
                        "reg_no": rkp.reg_no,
                        "address": rkp.address,
                        "capacity": "A,B,C",
                        "category": "1,2,3"
                    }
                    rkp_list.append(data)

            response_object = {
                "ErrorCode": "9999",
                "Status": "RKP List get successfully",
                "data": rkp_list,
                "count": count
            }
        else:
            response_object = {
                "ErrorCode": "9997",
                "Status": "RKP list not exists"
            }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "RKP List getting failed",
            "Error": e
        }

        return response_object, 201


def get_pjc_pending(user_id):
    try:
        result = {"schedule_id": 0, "approval_notes": "", "date": "", "regn_no": "", "rt_type": ""}
        date_obj = datetime.datetime.utcnow() - datetime.timedelta(days=90)
        pdc = db.session.query(PDCRegistration.schedule_id).select_from(PDCRegistration) \
            .join(Schedule, and_(PDCRegistration.schedule_id == Schedule.schedule_id)) \
            .filter(PDCRegistration.isActive == 1,
                    Schedule.user_id == user_id,
                    PDCRegistration.approval_status == 2,
                    PDCRegistration.inspection_type == 1,
                    PDCRegistration.created_date >= date_obj
                    ).all()
        if pdc:
            pjc_done = db.session.query(PDCRegistration.schedule_id) \
                .filter(PDCRegistration.isActive == 1,
                        PDCRegistration.inspection_type == 2,
                        PDCRegistration.approval_status > 0,
                        Schedule.schedule_id == PDCRegistration.schedule_id).exists()
            schedule_ids = []
            for c_pdc in pdc:
                schedule_ids.append(c_pdc.schedule_id)
            pjc = db.session.query(Schedule.schedule_id, Schedule.vehicle_id, Schedule.schedule_date).filter(
                Schedule.schedule_id.in_(schedule_ids), ~pjc_done,
                Schedule.isActive == 1).order_by(asc(Schedule.schedule_date)).first()
            if pjc:
                result["schedule_id"] = pjc.schedule_id
                vehicle = Vehicle.query.filter_by(id=pjc.vehicle_id).first()
                result["date"] = pjc.schedule_date.strftime("%d/%m/%Y") \
                    if pjc.schedule_date else ""
                result["regn_no"] = vehicle.regn_no
                result["rt_type"] = vehicle.model
                result["rt_category"] = vehicle.model
                result["rt_load"] = vehicle.engine_no
                result["vehicle_id"] = vehicle.id
                result["approval_status"] = 0
        return result
    except Exception as e:

        logging.exception(e)

        response_object = {
            "schedule_id": 0
        }

        return response_object


# if the schedule is declined then also need to show if other schedule is created.
def get_rt_info_for_rkp(user_id):
    try:
        pjc_data = get_pjc_pending(user_id)
        end_date = datetime.datetime.now().date() + datetime.timedelta(days=3)
        schedule_query = Schedule.query.filter_by(isActive=1)
        schedule_data = schedule_query.filter(Schedule.user_id == user_id,
                                              Schedule.schedule_date >= datetime.datetime.now().date(),
                                              Schedule.schedule_date <= end_date) \
            .order_by(asc(Schedule.schedule_date)).first()

        if schedule_data:
            vehicle = Vehicle.query.filter_by(id=schedule_data.vehicle_id).first()
            pdc_registration = PDCRegistration.query.filter_by(isActive=1,
                                                               schedule_id=schedule_data.schedule_id).first()
            data = {
                "date": schedule_data.schedule_date.strftime("%d/%m/%Y") \
                    if schedule_data.schedule_date else "",
                "regn_no": vehicle.regn_no,
                "rt_type": vehicle.model,
                "rt_category": vehicle.model,
                "rt_load": vehicle.engine_no,
                "vehicle_id": vehicle.id,
                "approval_status": 0,
                "schedule_id": schedule_data.schedule_id,
                "approval_notes": ""
            }
            if pdc_registration:
                data["approval_status"] = str(
                    pdc_registration.approval_status) if pdc_registration.approval_status else 0
                data["approval_notes"] = pdc_registration.approval_notes if pdc_registration.approval_notes else ""
            response_object = {
                "ErrorCode": "9999",
                "Status": "Schedule added successfully",
                "data": data,
                "pjc_data": pjc_data
            }
        else:
            response_object = {
                "ErrorCode": "9997",
                "Status": "Schedule not exists",
                "pjc_data": pjc_data
            }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule add failed",
            "Error": str(e),
            "pjc_data": {}
        }

        return response_object, 201


def get_pjc_pending_v1(user_id):
    try:
        result = {"schedule_id": 0, "approval_notes": "", "date": "", "regn_no": "", "rt_type": ""}
        date_obj = datetime.datetime.utcnow() - datetime.timedelta(days=90)
        # pdc = db.session.query(PDCRegistration.schedule_id).select_from(PDCRegistration) \
        #     .join(Schedule, and_(PDCRegistration.schedule_id == Schedule.schedule_id)) \
        pdc = db.session.query(PDCRegistration, Schedule, ScheduleDetail) \
            .join(Schedule, and_(PDCRegistration.schedule_id == Schedule.schedule_id)) \
            .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)) \
            .filter(PDCRegistration.isActive == 1,
                    ScheduleDetail.user_id == user_id,
                    PDCRegistration.approval_status == 2,
                    PDCRegistration.inspection_type == 1,
                    PDCRegistration.created_date >= date_obj
                    ).all()
        if pdc:
            pjc_done = db.session.query(PDCRegistration.schedule_id) \
                .filter(PDCRegistration.isActive == 1,
                        PDCRegistration.inspection_type == 2,
                        PDCRegistration.approval_status > 0,
                        Schedule.schedule_id == PDCRegistration.schedule_id).exists()
            schedule_ids = []
            for c_pdc in pdc:
                schedule_ids.append(c_pdc.Schedule.schedule_id)
            pjc = db.session.query(Schedule.schedule_id, Schedule.vehicle_id, Schedule.schedule_date).filter(
                Schedule.schedule_id.in_(schedule_ids), ~pjc_done,
                Schedule.isActive == 1).order_by(asc(Schedule.schedule_date)).first()
            if pjc:
                result["schedule_id"] = pjc.schedule_id
                vehicle = Vehicle.query.filter_by(id=pjc.vehicle_id).first()
                result["date"] = pjc.schedule_date.strftime("%d/%m/%Y") \
                    if pjc.schedule_date else ""
                result["regn_no"] = vehicle.regn_no
                result["rt_type"] = vehicle.model
                result["rt_category"] = vehicle.model
                result["rt_load"] = vehicle.engine_no
                result["vehicle_id"] = vehicle.id
                result["approval_status"] = 0
        return result
    except Exception as e:

        logging.exception(e)

        response_object = {
            "schedule_id": 0
        }

        return response_object


# if the schedule is declined then also need to show if other schedule is created.
def get_rt_info_for_rkp_v1(user_id):
    try:
        pjc_data = get_pjc_pending_v1(user_id)
        end_date = datetime.datetime.now().date() + datetime.timedelta(days=3)

        schedule_query = db.session.query(Schedule, ScheduleDetail) \
            .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)).filter(
            ScheduleDetail.isActive == 1, Schedule.isActive == 1)

        # schedule_query = Schedule.query.filter_by(isActive=1)
        schedule_data = schedule_query.filter(ScheduleDetail.user_id == user_id,
                                              Schedule.schedule_status != 4,
                                              Schedule.schedule_date >= datetime.datetime.now(
                                                  timezone(ems_local_time_zone)).date(),
                                              Schedule.schedule_date <= end_date) \
            .order_by(asc(Schedule.schedule_date)).first()

        if schedule_data:
            vehicle = Vehicle.query.filter_by(id=schedule_data.Schedule.vehicle_id).first()
            pdc_registration = PDCRegistration.query.filter_by(isActive=1,
                                                               schedule_id=schedule_data.Schedule.schedule_id).first()
            data = {
                "date": schedule_data.Schedule.schedule_date.strftime("%d/%m/%Y") \
                    if schedule_data.Schedule.schedule_date else "",
                "regn_no": vehicle.regn_no,
                "rt_type": vehicle.model,
                "rt_category": vehicle.model,
                "rt_load": vehicle.engine_no,
                "vehicle_id": vehicle.id,
                "approval_status": 0,
                "schedule_id": schedule_data.Schedule.schedule_id,
                "approval_notes": ""
            }
            if pdc_registration:
                data["approval_status"] = str(
                    pdc_registration.approval_status) if pdc_registration.approval_status else 0
                data["approval_notes"] = pdc_registration.approval_notes if pdc_registration.approval_notes else ""
            response_object = {
                "ErrorCode": "9999",
                "Status": "Schedule added successfully",
                "data": data,
                "pjc_data": pjc_data
            }
        else:
            response_object = {
                "ErrorCode": "9999",
                "Status": "Schedule not exists",
                "data": {},
                "pjc_data": pjc_data
            }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule add failed",
            "Error": str(e),
            "pjc_data": {}
        }

        return response_object, 201


def get_pjc_pending_status(user_id,vehicle_id,sch_id):
    try:
        result = {"schedule_id": 0, "approval_notes": "", "date": "", "regn_no": "", "rt_type": "",
                  "pdc_completed":False,"pdc_approved":False,"pdc_acknowledge":False,"pjc_completed":False}

        pdc = db.session.query(PDCRegistration, Schedule, ScheduleDetail) \
            .join(Schedule, and_(PDCRegistration.schedule_id == Schedule.schedule_id)) \
            .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)) \
            .filter(PDCRegistration.isActive == 1,
                    ScheduleDetail.user_id == user_id,
                    PDCRegistration.vehicle_id == vehicle_id,
                    PDCRegistration.inspection_type == 1,
                    Schedule.schedule_id == sch_id).all()
        if pdc:
            result['pdc_completed'] = True

            is_pdc_approved = db.session.query(PDCRegistration, Schedule, ScheduleDetail) \
                .join(Schedule, and_(PDCRegistration.schedule_id == Schedule.schedule_id)) \
                .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)) \
                .filter(PDCRegistration.isActive == 1,
                        ScheduleDetail.user_id == user_id,
                        PDCRegistration.vehicle_id == vehicle_id,
                        PDCRegistration.inspection_type == 1,
                        PDCRegistration.approval_status == 2,
                        Schedule.schedule_id == sch_id).all()

            if is_pdc_approved:
                result['pdc_approved'] = True

                is_pdc_acknowledge = db.session.query(PDCRegistration, Schedule, ScheduleDetail) \
                                    .join(Schedule, and_(PDCRegistration.schedule_id == Schedule.schedule_id)) \
                                    .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)) \
                                    .filter(PDCRegistration.isActive == 1,
                                            ScheduleDetail.user_id == user_id,
                                            PDCRegistration.vehicle_id == vehicle_id,
                                            PDCRegistration.inspection_type == 1,
                                            PDCRegistration.approval_status == 2,
                                            PDCRegistration.is_acknowledged == True,
                                            Schedule.schedule_id == sch_id).all()

                if is_pdc_acknowledge:
                    result["pdc_acknowledge"] = True

                    pjc_done = db.session.query(PDCRegistration.schedule_id) \
                        .filter(PDCRegistration.isActive == 1,
                                PDCRegistration.inspection_type == 2,
                                PDCRegistration.approval_status > 0,
                                ScheduleDetail.user_id == user_id,
                                PDCRegistration.vehicle_id == vehicle_id,
                                PDCRegistration.schedule_id == sch_id).exists()
                    schedule_ids = []
                    for c_pdc in pdc:
                        schedule_ids.append(c_pdc.Schedule.schedule_id)
                    pjc = db.session.query(Schedule.schedule_id, Schedule.vehicle_id, Schedule.schedule_date).filter(
                        Schedule.schedule_id.in_(schedule_ids), ~pjc_done,
                        Schedule.isActive == 1).order_by(asc(Schedule.schedule_date)).first()
                    if pjc:
                        result["schedule_id"] = pjc.schedule_id
                        vehicle = Vehicle.query.filter_by(id=pjc.vehicle_id).first()
                        result["date"] = pjc.schedule_date.strftime("%d/%m/%Y") \
                            if pjc.schedule_date else ""
                        result["regn_no"] = vehicle.regn_no
                        result["rt_type"] = vehicle.model
                        result["rt_category"] = vehicle.model
                        result["rt_load"] = vehicle.engine_no
                        result["vehicle_id"] = vehicle.id
                        result["approval_status"] = 0
                    else:
                        result['pjc_completed'] = True
        return result
    except Exception as e:

        logging.exception(e)

        response_object = {
            "schedule_id": 0
        }

        return response_object


# if the schedule is declined then also need to show if other schedule is created.
def get_rt_info_for_rkp_v2(user_id,rt_regn):
    try:

        is_pdc_completed = False
        is_pdc_approved = False
        is_pdc_acknowledge = False
        is_pjc_completed = False

        from_date = datetime.datetime.now().date() - datetime.timedelta(days=2)
        end_date = datetime.datetime.now().date() + datetime.timedelta(days=3)
        current_sch_id = 0
        vehicle_id = 0
        rt_arr = []
        rt_arr.append(rt_regn)
        rt_arr.append(rt_regn.replace(' ', ''))

        vehicle = Vehicle.query.filter(Vehicle.regn_no.in_(rt_arr), Vehicle.isActive == 1).first()

        if vehicle:
            vehicle_id = vehicle.id

        if vehicle_id != 0:

            schedule_ids=[]

            schedule_lst = db.session.query(Schedule, ScheduleDetail) \
                    .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id))\
                    .filter(ScheduleDetail.isActive == 1, Schedule.isActive == 1)\
                    .filter(ScheduleDetail.user_id == user_id, Schedule.vehicle_id == vehicle_id,
                            Schedule.schedule_date >= from_date, Schedule.schedule_date <= end_date)\
                    .order_by(asc(Schedule.schedule_date)).all()

            for sch in schedule_lst:
                schedule_ids.append(sch.Schedule.schedule_id)


            for sch_id in schedule_ids:

                # check whether PJC Exists for an Completed PDC

                current_sch_id = sch_id
                pjc_data = get_pjc_pending_status(user_id,vehicle_id,sch_id)

                is_pdc_completed = pjc_data['pdc_completed']
                is_pdc_approved = pjc_data["pdc_approved"]
                is_pdc_acknowledge = pjc_data["pdc_acknowledge"]
                is_pjc_completed = pjc_data['pjc_completed']

                if (pjc_data['pdc_completed'] and pjc_data["pdc_approved"] and pjc_data["pdc_acknowledge"] and pjc_data['pjc_completed']):
                    current_sch_id = 0
                else:
                    break


            schedule_data = db.session.query(Schedule, ScheduleDetail) \
                .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)).filter(
                ScheduleDetail.isActive == 1, Schedule.isActive == 1,Schedule.schedule_id == current_sch_id).first()

            if schedule_data:

                return_obj = CheckRTRegn(rt_regn)

                if not return_obj['rt_available']:

                    vehicle = Vehicle.query.filter_by(id=schedule_data.Schedule.vehicle_id).first()
                    pdc_registration = PDCRegistration.query.filter_by(isActive=1,
                                                                       schedule_id=schedule_data.Schedule.schedule_id).first()
                    data = {
                        "date": schedule_data.Schedule.schedule_date.strftime("%d/%m/%Y") \
                            if schedule_data.Schedule.schedule_date else "",
                        "regn_no": vehicle.regn_no,
                        "rt_type": vehicle.model,
                        "rt_category": vehicle.model,
                        "rt_load": vehicle.engine_no,
                        "vehicle_id": vehicle.id,
                        "approval_status": 0,
                        "schedule_id": schedule_data.Schedule.schedule_id,
                        "approval_notes": "",
                        "is_pdc_completed": is_pdc_completed,
                        "is_pdc_approved": is_pdc_approved,
                        "is_pdc_acknowledge": is_pdc_acknowledge,
                        "is_pjc_completed": is_pjc_completed,
                        "front": '' if vehicle.front == None else vehicle.front,
                        "rear": '' if vehicle.rear == None else vehicle.rear,
                        "starboard": '' if vehicle.starboard == None else vehicle.starboard,
                        "port": '' if vehicle.port == None else vehicle.port,
                    }
                    if pdc_registration:
                        data["approval_status"] = str(
                            pdc_registration.approval_status) if pdc_registration.approval_status else 0
                        data["approval_notes"] = pdc_registration.approval_notes if pdc_registration.approval_notes else ""
                    response_object = {
                        "ErrorCode": "9999",
                        "Status": "Schedule added successfully",
                        "data": data,
                        "pjc_data": pjc_data
                    }
                else:
                    response_object = {
                        "ErrorCode": "9996",
                        "Status": "Vechile is in Worshop Please Contact Administrator",
                        "data": {},
                        "pjc_data": {}
                    }

            else:
                response_object = {
                    "ErrorCode": "9998",
                    "Status": "Schedule not exists",
                    "data": {},
                    "pjc_data": {}
                }

        else:
            response_object = {
                "ErrorCode": "9997",
                "Status": "Invalid RegNo",
                "data": {},
                "pjc_data": {}
            }

        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Schedule add failed",
            "Error": str(e),
            "pjc_data": {}
        }

        return response_object, 201



# #################################### Dashboard related operation ##########################
#
#   feat - used to get the total distance dashboard
#
def get_total_distance(data):
    try:

        data_query = db.session.query(Schedule.product,
                                      func.sum(Schedule.dist).label('dist'),
                                      func.date(Schedule.schedule_date).label('schedule_date')). \
            filter(Schedule.isActive == 1)
        if 'search' in data and data['search'] != "":
            search = data['search']
            data_query = data_query.filter(or_(Schedule.ship_to_party.ilike(search),
                                               Schedule.rt_regn.ilike((search)),
                                               Schedule.delivery_note_no.ilike(search),
                                               Schedule.loc.ilike(search),
                                               Schedule.product.ilike(search),
                                               Schedule.shipment_no.ilike(search)))
        date_list = []
        # Filter 1 - Date filter add check
        if data["date"]:
            report_date = common.convertdmy_to_date2(data["date"])
            data_query = data_query.filter(Schedule.schedule_date == report_date
                                           )
            date_list.append(report_date.strftime("%d-%m-%Y"))
        else:
            num_days = 5
            period_days = get_days_period(-num_days)
            data_query = data_query.filter(Schedule.schedule_date >= period_days[0],
                                           Schedule.schedule_date <= period_days[-1])
            for cday in period_days:
                date_list.append(cday.strftime("%d-%m-%Y"))

        # Filter 2 - Loc
        if data["loc"]:
            data_query = data_query.filter(Schedule.loc == data["loc"])

        # Filter 3 - RKP
        if data["rkp"]:
            data_query = data_query.filter(Schedule.user_id == data["rkp"])

        # Filter 4 - RT
        if data["rt"]:
            data_query = data_query.filter(Schedule.vehicle_id == data["rt"])

        data_query = data_query.group_by(Schedule.product, func.date(Schedule.schedule_date))
        full_data = data_query.all()
        result = {}
        if full_data:
            for res in full_data:
                if res.product and not hasattr(result, res.product):
                    result[res.product] = []
                if res.product:
                    result[res.product].append({
                        "schedule_date": "" if res.schedule_date == '' else res.schedule_date.strftime('%d-%m-%Y'),
                        "dist": str(res.dist) if res.dist else "0.00"
                    })

                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Product based distance get successfully",
                    "data": result,
                    "date_list": date_list
                }
        else:
            response_object = {
                "ErrorCode": "9999",
                "Status": "Product based distance get successfully",
                "data": result,
                "date_list": date_list
            }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Product based distance List getting failed",
            "Error": str(e),
            "date_list": []
        }

        return response_object, 201


def get_total_distance_v1(data):
    try:

        data_query = db.session.query(ScheduleDetail.product,
                                      func.sum(ScheduleDetail.dist).label('dist'),
                                      func.date(Schedule.schedule_date).label('schedule_date')). \
            select_from(Schedule). \
            join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)). \
            filter(Schedule.isActive == 1, ScheduleDetail.isActive == 1)
        if 'search' in data and data['search'] != "":
            search = data['search']
            data_query = data_query.filter(or_(Schedule.ship_to_party.ilike(search),
                                               Schedule.rt_regn.ilike((search)),
                                               Schedule.delivery_note_no.ilike(search),
                                               Schedule.loc.ilike(search),
                                               Schedule.product.ilike(search),
                                               Schedule.shipment_no.ilike(search)))

        date_list = []
        # Filter 1 - Date filter add check
        # if data["date"]:
        #     report_date = common.convertdmy_to_date2(data["date"])
        #     data_query = data_query.filter(Schedule.schedule_date == report_date
        #                                    )
        #     date_list.append(report_date.strftime("%d-%m-%Y"))
        # else:
        # Filter 2 - Loc
        if data["loc"]:
            data_query = data_query.filter(Schedule.loc == data["loc"])

        # Filter 3 - RKP
        if data["rkp"]:
            data_query = data_query.filter(ScheduleDetail.user_id == data["rkp"])

        # Filter 4 - RT
        if data["rt"]:
            data_query = data_query.filter(Schedule.vehicle_id == data["rt"])
        num_days = 5
        report_date = common.convertdmy_to_date2(data["date"])
        period_days = get_days_period(-num_days, base=report_date)
        result = {}
        for cday in period_days:
            new_data_name = str(cday.strftime("%b")) + " " + str(cday.day)
            date_list.append(new_data_name)
            data_query_date = data_query.filter(Schedule.schedule_date == cday)

            data_query_date = data_query_date.group_by(ScheduleDetail.product, func.date(Schedule.schedule_date))
            res = data_query_date.first()
            result[new_data_name] = []
            if res:
                result[new_data_name].append({
                    "schedule_date": "" if res.schedule_date == '' else res.schedule_date.strftime('%d-%m-%Y'),
                    "dist": str(res.dist) if res.dist else "0.00",
                    "product":res.product

                })
            else:
                result[new_data_name].append({
                    "schedule_date": "",
                    "dist": "0.00",
                    "product":""
                })
                # if not hasattr(result, res.product):
                #     result[res.product] = []


                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Product based distance get successfully",
                    "data": result,
                    "date_list": date_list
                }
        else:
            response_object = {
                "ErrorCode": "9999",
                "Status": "Product based distance get successfully",
                "data": result,
                "date_list": date_list
            }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Product based distance List getting failed",
            "Error": str(e),
            "date_list": []
        }

        return response_object, 201


#
#   feat - used to get the total goods delivered
#
def get_total_goods_delivered(data):
    try:

        data_query = db.session.query(Schedule.product,
                                      func.sum(Schedule.qty).label('qty')). \
            filter(Schedule.isActive == 1)
        if 'search' in data and data['search'] != "":
            search = data['search']
            data_query = data_query.filter(or_(Schedule.ship_to_party.ilike(search),
                                               Schedule.rt_regn.ilike((search)),
                                               Schedule.delivery_note_no.ilike(search),
                                               Schedule.loc.ilike(search),
                                               Schedule.product.ilike(search),
                                               Schedule.shipment_no.ilike(search)))
        # Filter 1 - Date filter add check
        if data["date"]:
            data_query = data_query.filter(Schedule.schedule_date ==
                                           common.convertdmy_to_date2(data["date"]))
        else:
            data_query = data_query.filter(Schedule.schedule_date == datetime.datetime.today().date())

        # Filter 2 - Loc
        if data["loc"]:
            data_query = data_query.filter(Schedule.loc == data["loc"])

        # Filter 3 - RKP
        if data["rkp"]:
            data_query = data_query.filter(Schedule.user_id == data["rkp"])

        # Filter 4 - RT
        if data["rt"]:
            data_query = data_query.filter(Schedule.vehicle_id == data["rt"])

        data_query = data_query.group_by(Schedule.product)
        full_data = data_query.all()
        result = {}
        if full_data:
            for res in full_data:
                result[res.product] = str(res.qty) if res.qty else "0.00"
            response_object = {
                "ErrorCode": "9999",
                "Status": "Product based Goods delivery get successfully",
                "data": result
            }
        else:
            response_object = {
                "ErrorCode": "9999",
                "Status": "Product based Goods delivery get successfully",
                "data": result
            }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Product based Goods delivery List getting failed",
            "Error": str(e)
        }

        return response_object, 201


def get_total_goods_delivered_v1(data):
    try:

        data_query = db.session.query(ScheduleDetail.product,
                                      func.sum(ScheduleDetail.qty).label('qty')).select_from(Schedule). \
            join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)). \
            filter(Schedule.isActive == 1)

        if 'search' in data and data['search'] != "":
            search = data['search']
            data_query = data_query.filter(or_(Schedule.ship_to_party.ilike(search),
                                               Schedule.rt_regn.ilike((search)),
                                               Schedule.delivery_note_no.ilike(search),
                                               Schedule.loc.ilike(search),
                                               Schedule.product.ilike(search),
                                               Schedule.shipment_no.ilike(search)))
        # Filter 1 - Date filter add check
        if data["date"]:
            data_query = data_query.filter(Schedule.schedule_date ==
                                           common.convertdmy_to_date2(data["date"]))
        else:
            data_query = data_query.filter(Schedule.schedule_date == datetime.datetime.today().date())

        # Filter 2 - Loc
        if data["loc"]:
            data_query = data_query.filter(ScheduleDetail.loc == data["loc"])

        # Filter 3 - RKP
        if data["rkp"]:
            data_query = data_query.filter(ScheduleDetail.user_id == data["rkp"])

        # Filter 4 - RT
        if data["rt"]:
            data_query = data_query.filter(Schedule.vehicle_id == data["rt"])

        data_query = data_query.group_by(ScheduleDetail.product)
        full_data = data_query.all()
        result = {}
        if full_data:
            for res in full_data:
                result[res.product] = str(res.qty) if res.qty else "0.00"
            response_object = {
                "ErrorCode": "9999",
                "Status": "Product based Goods delivery get successfully",
                "data": result
            }
        else:
            response_object = {
                "ErrorCode": "9997",
                "data": {},
                "Status": "Schedule list not exists"
            }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Product based Goods delivery List getting failed",
            "Error": str(e)
        }

        return response_object, 201


#
#   feat - used to get the delivery status based on the station.
#
def get_delivery_status_station(data):
    try:

        data_query = db.session.query(Schedule.loc,
                                      func.count(Schedule.schedule_id).label('schedule_count')). \
            filter(Schedule.isActive == 1)
        # Filter 1 - Date filter add check
        if data["date"]:
            data_query = data_query.filter(Schedule.schedule_date ==
                                           common.convertdmy_to_date2(data["date"]))
        else:
            data_query = data_query.filter(Schedule.schedule_date == datetime.datetime.today().date())

        # Filter 2 - Loc
        if data["loc"]:
            data_query = data_query.filter(Schedule.loc == data["loc"])

        # Filter 3 - RKP
        if data["rkp"]:
            data_query = data_query.filter(Schedule.user_id == data["rkp"])

        # Filter 4 - RT
        if data["rt"]:
            data_query = data_query.filter(Schedule.vehicle_id == data["rt"])

        data_query = data_query.group_by(Schedule.loc)
        full_data = data_query.all()
        result = {}
        if full_data:
            for res in full_data:
                result[res.loc] = int(res.schedule_count) if res.schedule_count else 0

            response_object = {
                "ErrorCode": "9999",
                "Status": "Stations based delivery status get successfully",
                "data": result
            }
        else:
            response_object = {
                "ErrorCode": "9999",
                "Status": "Stations based delivery status get successfully",
                "data": result
            }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Stations based delivery status List getting failed",
            "Error": str(e)
        }

        return response_object, 201


def get_delivery_status_station_v1(data):
    try:

        data_query = db.session.query(ScheduleDetail.loc,
                                      func.count(Schedule.schedule_id).label('schedule_count')). \
            select_from(Schedule).join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)). \
            filter(Schedule.isActive == 1)
        if 'search' in data and data['search'] != "":
            search = data['search']
            data_query = data_query.filter(or_(Schedule.ship_to_party.ilike(search),
                                               Schedule.rt_regn.ilike((search)),
                                               Schedule.delivery_note_no.ilike(search),
                                               Schedule.loc.ilike(search),
                                               Schedule.product.ilike(search),
                                               Schedule.shipment_no.ilike(search)))
        # Filter 1 - Date filter add check
        if data["date"]:
            data_query = data_query.filter(Schedule.schedule_date ==
                                           common.convertdmy_to_date2(data["date"]))
        else:
            data_query = data_query.filter(Schedule.schedule_date == datetime.datetime.today().date())

        # Filter 2 - Loc
        if data["loc"]:
            data_query = data_query.filter(ScheduleDetail.loc == data["loc"])

        # Filter 3 - RKP
        if data["rkp"]:
            data_query = data_query.filter(ScheduleDetail.user_id == data["rkp"])

        # Filter 4 - RT
        if data["rt"]:
            data_query = data_query.filter(Schedule.vehicle_id == data["rt"])

        data_query = data_query.group_by(ScheduleDetail.loc)
        full_data = data_query.all()
        result = {}
        if full_data:
            for res in full_data:
                result[res.loc] = int(res.schedule_count) if res.schedule_count else 0

            response_object = {
                "ErrorCode": "9999",
                "Status": "Stations based delivery status get successfully",
                "data": result
            }
        else:
            response_object = {
                "ErrorCode": "9997",
                "data": {},
                "Status": "Schedule list not exists"
            }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Stations based delivery status List getting failed",
            "Error": str(e)
        }

        return response_object, 201


#
#   feat - used to get the delivery status based on the product.
#
def get_delivery_status_product(data):
    try:

        data_query = db.session.query(Schedule.product,
                                      func.count(Schedule.schedule_id).label('schedule_count')). \
            filter(Schedule.isActive == 1)
        if 'search' in data and data['search'] != "":
            search = data['search']
            data_query = data_query.filter(or_(Schedule.ship_to_party.ilike(search),
                                               Schedule.rt_regn.ilike((search)),
                                               Schedule.delivery_note_no.ilike(search),
                                               Schedule.loc.ilike(search),
                                               Schedule.product.ilike(search),
                                               Schedule.shipment_no.ilike(search)))
        # Filter 1 - Date filter add check
        num_days = 5
        report_date = None
        if data["date"]:
            report_date = common.convertdmy_to_date2(data["date"])
        period_days = get_days_period(-num_days, base=report_date)

        # Filter 2 - Loc
        if data["loc"]:
            data_query = data_query.filter(Schedule.loc == data["loc"])

        # Filter 3 - RKP
        if data["rkp"]:
            data_query = data_query.filter(Schedule.user_id == data["rkp"])

        # Filter 4 - RT
        if data["rt"]:
            data_query = data_query.filter(Schedule.vehicle_id == data["rt"])
        result = {}
        for cday in period_days:
            # if data["date"]:
            #     data_query = data_query.filter(Schedule.schedule_date ==
            #                                    common.convertdmy_to_date2(data["date"]))
            # else:
            data_query = data_query.filter(Schedule.schedule_date == cday)

            data_query = data_query.group_by(Schedule.product)
            res = data_query.first()

            if res:
                result[cday.strftime("%d-%m-%Y")] = int(res.schedule_count) if res.schedule_count else 0

                response_object = {
                    "ErrorCode": "9999",
                    "Status": "product based delivery status get successfully",
                    "data": result
                }
            else:
                response_object = {
                    "ErrorCode": "9997",
                    "data": {},
                    "Status": "Schedule list not exists"
                }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "product based delivery status List getting failed",
            "Error": str(e)
        }

        return response_object, 201

def get_delivery_status_product_v1(data):
    try:
        product = []

        num_days = 5
        report_date = None
        if data["date"]:
            report_date = common.convertdmy_to_date2(data["date"])
        period_days = get_days_period(-num_days, base=report_date)

        result = {}
        for cday in period_days:
            data_query = db.session.query(ScheduleDetail.product,
                                          func.count(Schedule.schedule_id).label('schedule_count')). \
                select_from(Schedule).join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)). \
                filter(Schedule.isActive == 1)

            # Filter 2 - Loc
            if data["loc"]:
                data_query = data_query.filter(ScheduleDetail.loc == data["loc"])

            # Filter 3 - RKP
            if data["rkp"]:
                data_query = data_query.filter(ScheduleDetail.user_id == data["rkp"])

            # Filter 4 - RT
            if data["rt"]:
                data_query = data_query.filter(Schedule.vehicle_id == data["rt"])

            data_query = data_query.filter(Schedule.schedule_date == cday)
            data_query = data_query.group_by(ScheduleDetail.product)
            res = data_query.all()
            if res:
                new_data = {}
                for item in res:
                    product_query = Product.query.filter(Product.product_value == item.product,
                                                         Product.isActive == 1).first()
                    new_data_name = str(cday.strftime("%b")) + " " + str(cday.day)
                    if product_query:
                        new_data[product_query.product_name]=int(item.schedule_count) if item.schedule_count else 0
                        result[new_data_name] = new_data
                        if product_query.product_name not in product:
                            product.append(product_query.product_name)
                    else:
                        new_data[item.product] = 0
                        result[new_data_name] = new_data
                        if item.product not in product:
                            product.append(item.product)
        if result:
            response_object = {
                "ErrorCode": "9999",
                "Status": "product based delivery status get successfully",
                "data": result,
                "product": product
            }
        else:
            response_object = {
                "ErrorCode": "9997",
                "data": {},
                "Status": "Schedule list not exists",
                "product": product
            }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "product based delivery status List getting failed",
            "Error": str(e),
            "product": []
        }

        return response_object, 201


#
#   feat - used to get the status summary.
#
def get_status_summary():
    try:
        rt_count = db.session.query(Vehicle).select_from(Vehicle).filter(Vehicle.isActive == 1).count()
        sch_data = db.session.query(func.count(func.distinct(Schedule.vehicle_id)).label("rt_count"),
                                    func.count(func.distinct(Schedule.user_id)).label("rkp_count"),
                                    func.sum(Schedule.qty).label("total_delivery"),
                                    func.sum(Schedule.dist).label("total_dist")).select_from(Schedule) \
            .filter(Schedule.isActive == 1,
                    Schedule.schedule_date == datetime.datetime.today().date()).first()
        rkp_count = User.query.filter_by(isActive=1).filter(User.roles.any(RKP_RoleId)).count()

        result = {"total_delivery": 0, "rt_fuel": 230000, "total_dist": "0", "rt_expense": 10000}
        if sch_data:
            result["rt_us"] = rt_count - (sch_data.rt_count if sch_data.rt_count else sch_data.rt_count)
            result["rkp_avail"] = rkp_count - (sch_data.rkp_count if sch_data.rkp_count else sch_data.rkp_count)
            result["total_delivery"] = str(sch_data.total_delivery if sch_data.total_delivery else 0)
            result["total_dist"] = str(sch_data.total_dist if sch_data.total_dist else 0)
        else:
            result["rt_us"] = rt_count
            result["rkp_avail"] = rkp_count
        response_object = {
            "ErrorCode": "9999",
            "Status": "product based delivery status get successfully",
            "data": result
        }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "product based delivery status List getting failed",
            "Error": str(e)
        }

        return response_object, 201


def get_status_summary_v1():
    try:
        rt_count = db.session.query(Vehicle).select_from(Vehicle).filter(Vehicle.isActive == 1).count()
        sch_data = db.session.query(func.count(func.distinct(Schedule.vehicle_id)).label("rt_count"),
                                    func.count(func.distinct(ScheduleDetail.user_id)).label("rkp_count"),
                                    func.sum(ScheduleDetail.qty).label("total_delivery"),
                                    func.sum(ScheduleDetail.dist).label("total_dist")).select_from(Schedule) \
            .join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)) \
            .filter(Schedule.isActive == 1,
                    Schedule.schedule_date == datetime.datetime.today().date()).first()
        rkp_count = User.query.filter_by(isActive=1).filter(User.roles.any(RKP_RoleId)).count()

        result = {"total_delivery": 0, "rt_fuel": 230000, "total_dist": "0", "rt_expense": 10000}
        if sch_data:
            result["rt_us"] = (sch_data.rt_count if sch_data.rt_count else sch_data.rt_count)
            result["rkp_avail"] = rkp_count - (sch_data.rkp_count if sch_data.rkp_count else sch_data.rkp_count)
            result["total_delivery"] = str(sch_data.total_delivery if sch_data.total_delivery else 0)
            result["total_dist"] = str(sch_data.total_dist if sch_data.total_dist else 0)
        else:
            result["rt_us"] = rt_count
            result["rkp_avail"] = rkp_count
        response_object = {
            "ErrorCode": "9999",
            "Status": "product based delivery status get successfully",
            "data": result
        }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "product based delivery status List getting failed",
            "Error": str(e)
        }

        return response_object, 201


# Generic Methods
def get_days_period(num_days, base=None):
    base = datetime.datetime.today().date() if base is None else base
    return [base + datetime.timedelta(days=x) for x in range(num_days, 1)]


def update_latlong(user_id, lat, long):
    try:
        from sqlalchemy.orm import aliased
        incl_alias = aliased(PDCRegistration, name="pr")
        resp = db.session.query(incl_alias).filter(incl_alias.user_id == user_id,
                                                   incl_alias.inspection_type == 1,
                                                   incl_alias.isActive == 1). \
            filter(
            ~db.session.query(PDCRegistration).filter(PDCRegistration.inspection_type == 2,
                                                      PDCRegistration.schedule_id == incl_alias.schedule_id).exists()
        ).first()
        if resp:
            schedule_rt = Schedule.query.filter_by(schedule_id=resp.schedule_id).first()
            schedule_rt.latitude = lat
            schedule_rt.longitude = long
            save_changes(schedule_rt)
        return 201
    except Exception as e:
        print(e)


def get_rt_latlang():
    try:
        # update_latlong(688, '3.025340', '101.617767')
        List = []
        from sqlalchemy.orm import aliased
        incl_alias = aliased(PDCRegistration, name="pr")

        schedule_data = db.session.query(incl_alias, Schedule).filter(
            incl_alias.schedule_id == Schedule.schedule_id).filter(incl_alias.inspection_type == 1,
                                                                   incl_alias.isActive == 1,
                                                                   Schedule.isActive == 1). \
            filter(
            ~db.session.query(PDCRegistration).filter(PDCRegistration.inspection_type == 2,
                                                      PDCRegistration.schedule_id == incl_alias.schedule_id).exists()

        ).all()
        for rt in schedule_data:
            data = {
                "vehicle_id": rt.Schedule.vehicle_id,
                "rt_regn": rt.Schedule.rt_regn,
                "latitude": rt.Schedule.latitude,
                "longitude": rt.Schedule.longitude,
                "user_id": rt.Schedule.user_id
            }
            List.append(data)
        response_object = {
            "ErrorCode": "9999",
            "Status": "List get successfully",
            "data": List
        }
        return response_object, 201
    except Exception as e:
        print(e)


def get_schedule_type():
    try:

        lst = []

        schedule_type_list = ScheduleType.query.filter_by(isActive=1).all()

        if schedule_type_list:

            for schedule_type in schedule_type_list:
                data = {}
                data["schedule_type_id"] = schedule_type.schedule_type_id
                data["schedule_type"] = schedule_type.schedule_type
                data["display_name"] = schedule_type.display_name

                lst.append(data)

                response_object = {
                    "ErrorCode": "9999",
                    "data": lst
                }
        else:
            response_object = {
                "ErrorCode": "9998",
                "data": lst
            }

        return response_object
    except Exception as e:
        logging.exception(e)
        response_object = {
            "message": "Exception",
            "ErrorCode": "0000",
            "data": {}
        }
        return response_object


def get_total_work_hrs(data):
    try:
        response_object = {
            "ErrorCode": "9999",
            "Status": "Total work hours get successfully",
            "data": [],
            "date_list": []
        }
        num_days = 5
        report_date = None
        if data["date"]:
            report_date = common.convertdmy_to_date2(data["date"])
        period_days = get_days_period(-num_days, base=report_date)
        date_list = []
        result = {}
        for cday in period_days:
            new_data_name = str(cday.strftime("%b")) + " " + str(cday.day)

            date_list.append(new_data_name)

            data_query = db.session.query(func.sum(func.trunc((

                                                                      extract('epoch',
                                                                              case(
                                                                                  [
                                                                                      (
                                                                                          RKPLogin.start_date ==
                                                                                          RKPLogin.stoped_date,
                                                                                          RKPLogin.stoped_date
                                                                                      )
                                                                                  ],
                                                                                  else_=datetime.datetime(
                                                                                      year=cday.year,
                                                                                      month=cday.month,
                                                                                      day=cday.day,
                                                                                      hour=23,
                                                                                      minute=59, second=31)
                                                                              )
                                                                              ) -
                                                                      extract('epoch', RKPLogin.start_date)
                                                              ) / 60)).label('work_hrs')).select_from(RKPLogin) \
                .filter(func.date(RKPLogin.start_date) == cday)
            # Filter 3 - RKP
            if data["rkp"]:
                data_query = data_query.filter(RKPLogin.user_id == data["rkp"])
            full_data = data_query.first()
            result[new_data_name] = full_data.work_hrs or 0
            response_object = {
                "ErrorCode": "9999",
                "Status": "Total work hours get successfully",
                "data": result,
                "date_list": date_list
            }

        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Total work hours getting failed",
            "Error": str(e),
            "date_list": []
        }

        return response_object, 201


def get_delivery_note_graph(data):
    try:
        response_object = {
            "ErrorCode": "9999",
            "Status": "Get delivery note graph get successfully",
            "data": [],
            "date_list": []
        }
        num_days = 5
        report_date = None
        if data["date"]:
            report_date = common.convertdmy_to_date2(data["date"])
        period_days = get_days_period(-num_days, base=report_date)
        date_list = []
        result = {}
        for cday in period_days:
            new_data_name = str(cday.strftime("%b")) + " " + str(cday.day)

            date_list.append(new_data_name)

            data_query = db.session.query(func.count(
                cast(func.NULLIF(func.regexp_replace(ScheduleDetail.delivery_note_no, '\D', '', 'g'), ''),
                     sqlalchemy.Integer)
            ).label('delivery_note_no')) \
                .select_from(Schedule).join(ScheduleDetail, and_(Schedule.schedule_id == ScheduleDetail.schedule_id)) \
                .filter(and_(Schedule.isActive == 1, ScheduleDetail.isActive == 1, Schedule.schedule_date == cday))
            # Filter 3 - RKP
            if data["rkp"]:
                data_query = data_query.filter(ScheduleDetail.user_id == data["rkp"])
            full_data = data_query.first()
            result[new_data_name] = full_data.delivery_note_no
            response_object = {
                "ErrorCode": "9999",
                "Status": "Delivery note graph data get successfully",
                "data": result,
                "date_list": date_list
            }

        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Delivery note graph data getting failed",
            "Error": str(e),
            "date_list": []
        }

        return response_object, 201

def get_trip_pershipment(data):
    try:

        # data_query = db.session.query(func.count(Schedule.schedule_id).label('schedule_count'),Schedule.schedule_date)\
        #     .join(PDCRegistration,Schedule.schedule_id==PDCRegistration.schedule_id).filter(Schedule.isActive == 1,PDCRegistration.inspection_type==2,Schedule.product!="null")

        # Filter 1 - Date filter add check
        return_list=[]
        num_days = 5
        report_date = None
        if data["date"]:
            report_date = common.convertdmy_to_date2(data["date"])
        period_days = get_days_period(-num_days, base=report_date)
        index=0
        for cday in period_days:
            data_query = db.session.query(func.count(Schedule.schedule_id).label('schedule_count'),
                                          Schedule.schedule_date) \
                .join(PDCRegistration, Schedule.schedule_id == PDCRegistration.schedule_id).filter(
                Schedule.isActive == 1, PDCRegistration.inspection_type == 2, Schedule.product != "null")

            data_query = data_query.filter(Schedule.schedule_date == cday)
            data_query = data_query.group_by(Schedule.schedule_date)
            data_query = data_query.order_by(desc(Schedule.schedule_date))
            res = data_query.first()
            result = {}
            new_data_name = str(cday.date().strftime("%b")) + " " + str(cday.day)
            if res:
                result['count'] = int(res.schedule_count) if res.schedule_count else 0
                result['date'] =new_data_name
            else:
                result['count'] = 0,
                result['date'] = new_data_name
            return_list.append(result)
            index=1
        if len(return_list)>0:
            response_object = {
                "ErrorCode": "9999",
                "Status": "products list delivered  successfully",
                "data": return_list
            }
        else:
            response_object = {
                "ErrorCode": "9997",
                "data": {},
                "Status": "Schedule list not exists"
            }
        return response_object, 201
    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "products list delivered  failed",
            "Error": str(e)
        }

        return response_object, 201

