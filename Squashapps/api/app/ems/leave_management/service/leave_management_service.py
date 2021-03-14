from decimal import Decimal
import logging
from app.cura import db
from datetime import datetime,timedelta,time

from app.cura.common import common

from app.cura.user.model.user import User

from app.cura.email.service.email_service import send_notification,send_notification_new
from ..model.leave_application import Leave_Application
from ..model.leave_summary import Leave_Summary
from app.ems.predeparture.model.rkp_login import RKPLogin
from sqlalchemy import extract, and_, desc, or_,func

from ..model.medical_claim import Medical_Claim
from ..model.medical_claim_summary import Medical_Claim_Summary
from app.ems.dropdown_list.model.dropdown import DropdownList
import json
from werkzeug.utils import secure_filename
import os
import uuid
from app.ems import config
from flask import send_file,send_from_directory
import subprocess


def getleavesummary(userid,year):

    try:

        summary_data = {}
        leave_save_details = {}

        status = 0

        res = Leave_Summary.query.filter_by(user_id=userid, year=year, isActive=1).first()

        if res:
            summary_data["summary_id"] = res.summary_id
            summary_data["leave_allocated"] = 0 if res.leave_allocated == None else res.leave_allocated
            summary_data["leave_taken"] = 0 if res.leave_taken == None else res.leave_taken
            summary_data["medical_leave"] =  (res.medical_leave_allocated - res.medical_leave) if (res.medical_leave_allocated != None and res.medical_leave != None) else 0
            summary_data["annual_leave"] = 0 if res.annual_leave == None else res.annual_leave
            summary_data["leave_others"] = 0 if res.leave_others == None else res.leave_others
            summary_data["balance_leave"] = (res.annual_leave - res.leave_taken) if (res.annual_leave != None and res.leave_taken != None ) else 0

        leave = Leave_Application.query.filter_by(user_id=userid,status=1,isActive=1).order_by(
            desc(Leave_Application.leave_id)).first()

        if leave:
            leave_save_details["leave_id"] = leave.leave_id
            leave_save_details["user_id"] = leave.user_id
            leave_save_details["from_date"] = "" if leave.from_date == '' else leave.from_date.strftime('%d-%m-%Y')
            leave_save_details["to_date"] = "" if leave.to_date == '' else leave.to_date.strftime('%d-%m-%Y')
            leave_save_details["days_of_leave"] = leave.days_of_leave
            leave_save_details["leave_type"] = leave.leave_type

        leave_status = Leave_Application.query.filter_by(user_id=userid, isActive=1).order_by(
            desc(Leave_Application.leave_id)).first()

        # 0 - No Leave Applied for the User
        # 2 - Leave Approved for the User
        # 1 - Leave Approval is Pending
        # -2 - Leave Rejected for the User
        # -1 - Leave Submitted by the User and Not Send for Approval by the User

        if leave_status:
            status = int(leave_status.status)


        response_object = {
                "ErrorCode": "9999",
                "summary_data": summary_data,
                 "leave_save_details":leave_save_details,
                 "user_leave_status" : status
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

def get_LeaveApplication(leave_id):

    try:
        leave = Leave_Application.query.filter_by(leave_id=leave_id,isActive=1).first()

        if leave:
            data = {}

            data["leave_id"] = leave.leave_id
            data["user_id"] = leave.user_id
            data["from_date"] = "" if leave.from_date == '' else leave.from_date.strftime('%d-%m-%Y')
            data["to_date"] = "" if leave.to_date == '' else leave.to_date.strftime('%d-%m-%Y')
            data["days_of_leave"] = leave.days_of_leave
            data["leave_type"] = leave.leave_type

            response_object = {
                "ErrorCode": "9999",
                "data": data
            }
        else:
            response_object = {
                "message": "Data not exists",
                "ErrorCode": "9997",
                "data": {}
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


def getLeaveStatus(user_id):

    try:
        leave = Leave_Application.query.filter_by(user_id=user_id,isActive=1).order_by(desc(Leave_Application.leave_id)).first()

        # 0 - No Leave Applied for the User
        # 2 - Leave Approved for the User
        # 1 - Leave Approval is Pending
        # -2 - Leave Rejected for the User
        # -1 - Leave Submitted by the User and Not Send for Approval by the User

        if leave:

            response_object = {
                "ErrorCode": "9999",
                "status": int(leave.status),
                 "message": "Leave Already Approved",
            }

        else:
            response_object = {
                "message": "No Pending Leave Status",
                "status" : 0,
                "ErrorCode": "9999"
            }

        return response_object
    except Exception as e:
        logging.exception(e)
        response_object = {
            "message": "Exception",
            "ErrorCode": "0000",
        }
        return response_object


def Apply_Leave(data):
    try:

        is_leave_applied = False

        leave_id = data["leave_id"]
        if data['leave_save_type'] == 1:
            is_leave_applied = True
            status = 1
        else:
            is_leave_applied = False
            status = -1

        if is_leave_applied:

            leave_already_applied = Leave_Application.query\
                                    .filter(Leave_Application.from_date==common.convertdmy_to_date2(data["from_date"])) \
                                    .filter(Leave_Application.to_date ==common.convertdmy_to_date2(data["to_date"])) \
                                    .filter(Leave_Application.user_id == data["user_id"],Leave_Application.isActive == 1,Leave_Application.status > 0).first()

            if leave_already_applied:
                is_leave_applied = True
            else:
                is_leave_applied = False

        if not is_leave_applied:

            leave = Leave_Application.query.filter_by(leave_id=data["leave_id"],isActive=1).first()

            if leave:

                leave.user_id = data["user_id"],
                leave.from_date = common.convertdmy_to_date2(data["from_date"]),
                leave.to_date = common.convertdmy_to_date2(data["to_date"]),
                leave.days_of_leave = data["days_of_leave"],
                leave.leave_type = data["leave_type"],
                leave.status = status,
                leave.updated_by = data["user_id"],
                leave.updated_date = datetime.utcnow(),
                leave.isActive = 1
                leave.reason = data['reason'],
                leave.file_path = data['file_name'],
                leave.is_after_leave_taken = data['is_after_leave_taken']

                save_changes(leave)
            else:
                ApplyLeave = Leave_Application(
                    user_id=data["user_id"],
                    from_date=common.convertdmy_to_date2(data["from_date"]),
                    to_date=common.convertdmy_to_date2(data["to_date"]),
                    days_of_leave=data["days_of_leave"],
                    leave_type=data["leave_type"],
                    status=status,
                    created_by=data["user_id"],
                    created_date=datetime.utcnow(),
                    isActive=1,
                    reason = data['reason'],
                    file_path =data['file_name'],
                    is_after_leave_taken=data['is_after_leave_taken']
                )
                save_changes(ApplyLeave)
                leave_id = ApplyLeave.leave_id

                if data['leave_save_type'] == 1:
                    send_notification('Leave Request',data["user_id"],'',1,1,'tbl_leave_application',leave_id)


                response_obj = {
                    "message": "Leave Applied Successfully",
                    "Errorcode": 9999,
                    "leave_id":leave_id
                }
        else:
            response_obj = {
                "message": "Leave has been applied for selected date",
                "Errorcode": 9998,
            }

        return response_obj

    except Exception as e:
        print("Leave Applied service error: " + str(e))
        logging.exception(e)
        response_obj = {
            "message": "Leave Applied Failed",
            "Errorcode": 9998,
            "leave_id": 0
        }
        return response_obj


def getmonthleavecount(month,year,type):

    try:
        lst = []
        total_pending_count = 0
        total_approve_count = 0
        day = timedelta(days=1)
        date1 = datetime(int(year), int(month), 1)
        d = date1
        dates = []
        while d.month == int(month):
            dates.append(d.strftime('%d-%m-%Y'))
            d += day

        res = Leave_Application.query\
            .filter(extract('month', Leave_Application.from_date) == int(month))\
            .filter(extract('year', Leave_Application.from_date) == int(year)) \
            .filter(extract('month', Leave_Application.to_date) == int(month)) \
            .filter(extract('year', Leave_Application.to_date) == int(year)) \
            .filter(Leave_Application.isActive == 1).all()

        for day in dates:
            day = datetime.strptime(day, "%d-%m-%Y")
            pending_count = 0
            approve_count = 0
            date_arr = {}

            for data in res:

                from_date = data.from_date
                to_date = data.to_date
                status = data.status

                if from_date <= day <= to_date :
                    if status == 1 and type=='1':  #Pending for HR count
                        pending_count = pending_count + 1
                        total_pending_count = total_pending_count+1
                    elif (status == 2 or status == 3) and type=='1':  # HR Approve Count
                        approve_count = approve_count + 1
                        total_approve_count = total_approve_count + 1

                    elif status == 2 and type=='2': #Pending for operator count
                        pending_count = pending_count + 1
                        total_pending_count = total_pending_count + 1

                    elif status == 3 and type=='2': # Operator Approve Count
                        approve_count = approve_count + 1
                        total_approve_count = total_approve_count + 1

            if (pending_count > 0 or approve_count > 0):
                date_arr['date'] = day.strftime('%d-%m-%Y')
                date_arr['pending_count'] = pending_count
                date_arr['approve_count'] = approve_count
                lst.append(date_arr)

        response_object = {
                "ErrorCode": "9999",
                "total_approve_count": total_approve_count,
                "total_pending_count": total_pending_count,
                "total_man_power": "",
                "data": lst

            }

        return response_object
    except Exception as e:
        logging.exception(e)
        response_object = {
            "ErrorCode": "0000",
            "total_approve_count": 0,
            "total_pending_count": 0,
            "total_man_power": "",
            "data": {}
        }
        return response_object


def getapplieduserlist(given_date,type):

    try:
        approve_list = []
        pending_list = []

        day = datetime.strptime(given_date, "%d-%m-%Y")
        month = day.month
        year = day.year

        res = Leave_Application.query \
            .filter(extract('month', Leave_Application.from_date) == int(month))\
            .filter(extract('year', Leave_Application.from_date) == int(year)) \
            .filter(extract('month', Leave_Application.to_date) == int(month)) \
            .filter(extract('year', Leave_Application.to_date) == int(year)) \
            .filter(Leave_Application.isActive == 1,Leave_Application.status != -1).all()

        for data in res:
            leave_data={}
            leave_id = data.leave_id
            userid = data.user_id
            from_date = data.from_date
            to_date = data.to_date
            status = data.status

            if from_date <= day <= to_date:
                user_name = ""
                user = User.query.filter_by(id=userid).first()
                if user:
                    user_name = user.rkp_name if user.rkp_name != None and user.rkp_name != "" else user.first_name + (" " if user.last_name == None else user.last_name )

                if status == 1 and type=='1':
                    leave_data['leave_id'] = leave_id
                    leave_data['user_id'] = userid
                    leave_data['user_name'] = user_name
                    pending_list.append(leave_data)

                elif (status == 2 or status == 3) and type=='1':
                    leave_data['leave_id'] = leave_id
                    leave_data['user_id'] = userid
                    leave_data['user_name'] = user_name
                    approve_list.append(leave_data)

                elif status == 2 and type=='2':
                    leave_data['leave_id'] = leave_id
                    leave_data['user_id'] = userid
                    leave_data['user_name'] = user_name
                    pending_list.append(leave_data)

                elif status == 3 and type == '2':
                    leave_data['leave_id'] = leave_id
                    leave_data['user_id'] = userid
                    leave_data['user_name'] = user_name
                    approve_list.append(leave_data)

        response_object = {
                "ErrorCode": "9999",
                "approve_list": approve_list,
                "pending_list": pending_list,
            }

        return response_object

    except Exception as e:
        logging.exception(e)
        response_object = {
            "ErrorCode": "0000",
            "approve_list": [],
            "pending_list": []
        }
        return response_object


def getleaveInformation(user_id,leave_id):
    try:
        from flask import send_file, send_from_directory

        data = {}

        day = datetime.utcnow()
        year = str(day.year)

        res = db.session.query(Leave_Summary, Leave_Application,User,DropdownList) \
            .join(Leave_Application, and_(Leave_Summary.user_id == Leave_Application.user_id)) \
            .join(User, and_(Leave_Summary.user_id == User.id)) \
            .join(DropdownList,and_(Leave_Application.leave_type == DropdownList.key_id, DropdownList.type == 'leave_type')) \
            .filter(Leave_Summary.year == year,Leave_Summary.user_id==user_id, Leave_Application.leave_id == leave_id).first()

        # res = Leave_Summary.query.filter_by(user_id=user_id, year=year, isActive=1).first()

        if res:
            data["leave_allocated"] = 0 if res.Leave_Summary.leave_allocated == None else res.Leave_Summary.leave_allocated
            data["leave_taken"] = 0 if res.Leave_Summary.leave_taken == None else res.Leave_Summary.leave_taken
            data["medical_leave"] =  (res.Leave_Summary.medical_leave_allocated - res.Leave_Summary.medical_leave) if (res.Leave_Summary.medical_leave_allocated != None and res.Leave_Summary.medical_leave !=None) else 0
            data["annual_leave"] = 0 if res.Leave_Summary.annual_leave == None else res.Leave_Summary.annual_leave
            data["leave_others"] = 0 if res.Leave_Summary.leave_others == None else res.Leave_Summary.leave_others
            data["balance_leave"] = (res.Leave_Summary.annual_leave - res.Leave_Summary.leave_taken) if (res.Leave_Summary.annual_leave != None and res.Leave_Summary.leave_taken != None) else 0
            data["leave_id"] = res.Leave_Application.leave_id
            data["user_id"] = res.Leave_Application.user_id
            data["from_date"] = "" if res.Leave_Application.from_date == '' else res.Leave_Application.from_date.strftime('%d-%m-%Y')
            data["to_date"] = "" if res.Leave_Application.to_date == '' else res.Leave_Application.to_date.strftime('%d-%m-%Y')
            data["days_of_leave"] = res.Leave_Application.days_of_leave
            data["leave_type_id"] = res.Leave_Application.leave_type
            data["leave_type_value"] = res.DropdownList.key_value_en
            data["join_date"] = "" if res.User.date_of_employment == '' or res.User.date_of_employment == None else res.User.date_of_employment.strftime('%d-%m-%Y')
            data["user_name"] = res.User.rkp_name if res.User.rkp_name != None and res.User.rkp_name != "" else res.User.first_name + (" " if res.User.last_name == None else res.User.last_name )
            data["last_log_in"] = ""
            data["last_log_off"] = ""
            data["violations"] = ""
            data["status"] = str(res.Leave_Application.status)
            data["reason"] = res.Leave_Application.reason
            data["rejection_reason"] = res.Leave_Application.rejection_reason if res.Leave_Application.rejection_reason else ""
            data["file_path"] = res.Leave_Application.file_path
            data["is_after_leave_taken"] = res.Leave_Application.is_after_leave_taken


        else:
            leave = db.session.query(Leave_Application, User,DropdownList) \
                .join(User, and_(Leave_Application.user_id == User.id)) \
                .join(DropdownList,and_(Leave_Application.leave_type == DropdownList.key_id, DropdownList.type == 'leave_type')) \
                .filter(Leave_Application.user_id == user_id,Leave_Application.leave_id == leave_id).first()

            data["leave_allocated"] = 0
            data["leave_taken"] = 0
            data["medical_leave"] = 0
            data["annual_leave"] = 0
            data["leave_others"] = 0
            data["balance_leave"] = 0
            data["leave_id"] = leave.Leave_Application.leave_id
            data["user_id"] = leave.Leave_Application.user_id
            data["from_date"] = "" if leave.Leave_Application.from_date == '' else leave.Leave_Application.from_date.strftime('%d-%m-%Y')
            data["to_date"] = "" if leave.Leave_Application.to_date == '' else leave.Leave_Application.to_date.strftime('%d-%m-%Y')
            data["days_of_leave"] = leave.Leave_Application.days_of_leave
            data["leave_type_id"] = leave.Leave_Application.leave_type
            data["leave_type_value"] = leave.DropdownList.key_value_en
            data["join_date"] = "" if leave.User.date_of_employment == '' or leave.User.date_of_employment == None else leave.User.date_of_employment.strftime('%d-%m-%Y')
            data["user_name"] = leave.User.rkp_name if leave.User.rkp_name != None and leave.User.rkp_name != "" else leave.User.first_name + (" " if leave.User.last_name == None else leave.User.last_name )
            data["last_log_in"] = ""
            data["last_log_off"] = ""
            data["violations"] = ""
            data["last_destination"] = ""
            data["total_duty_days"] = 0
            data["status"] = str(leave.Leave_Application.status)
            data["reason"] = leave.Leave_Application.reason
            data["rejection_reason"] = leave.Leave_Application.rejection_reason if leave.Leave_Application.rejection_reason else ""
            data["file_path"] = leave.Leave_Application.file_path
            data["is_after_leave_taken"] = leave.Leave_Application.is_after_leave_taken

        response_object = {
                "ErrorCode": "9999",
                "data": data

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


def approve_Leave(data):
    try:
        leave_id = data["leave_id"]
        type=""
        if "type" in data:
            type = data["type"] # Here type1 means its from HR and Type2 from operation
        # status = -2
        if data['status'] == 1:
            if type==2:
                status=3
            else:
                status = 2
        else:
            if type == 2:
                status = -3
            else:
                status = -2

        leave = Leave_Application.query.filter_by(leave_id=leave_id,isActive=1).first()

        if leave:
            if data['leave_type']!="":
                leave.leave_type = data['leave_type'],
            leave.status = status,
            leave.rejection_reason=data['rejection_reason']
            leave.rejected_by = type
            leave.updated_by = data["updated_by"],
            leave.updated_date = datetime.utcnow(),
            save_changes(leave)

            notification_parms={"notification_type":"",
                                "from_user":"",
                                "to_user":"",
                                "is_web":"",
                                "approve_status":"",
                                "table_name":"tbl_leave_application",
                                "table_detail_id":leave_id}


        if status == 3:
            day = datetime.utcnow()
            year = str(day.year)

            no_of_leave_days = int(leave.days_of_leave)

            leave_summary = Leave_Summary.query.filter_by(user_id=data["user_id"], year=year, isActive=1).first()

            if leave_summary and leave:

                current_leave_id = leave.leave_id
                start_date = leave.from_date
                end_date = leave.to_date

                delta = timedelta(days=1)

                while start_date <= end_date:

                    is_leave_applied = Leave_Application.query.filter_by(status=3,isActive=1) \
                        .filter(Leave_Application.from_date >= start_date,Leave_Application.to_date <= start_date,Leave_Application.leave_id != current_leave_id,Leave_Application.user_id == data["user_id"]).first()

                    if is_leave_applied:
                        no_of_leave_days = no_of_leave_days - 1

                    start_date += delta


                if data["leave_type"] == '2':
                    leave_summary.medical_leave = (0 if leave_summary.medical_leave == None else leave_summary.medical_leave) + no_of_leave_days
                elif data["leave_type"] == '3':
                    leave_summary.leave_others =  (0 if leave_summary.leave_others == None else leave_summary.leave_others)  + no_of_leave_days
                else:
                    leave_summary.leave_taken = (0 if leave_summary.leave_taken == None else leave_summary.leave_taken) + no_of_leave_days

                save_changes(leave_summary)

            elif leave:

                applied_year = leave.from_date.year

                previous_year = str(int(applied_year) - 1)
                previous_year_balance = 0

                pre_leave = Leave_Summary.query.filter_by(user_id=data['user_id'], year=previous_year, isActive=1).first()

                if pre_leave:
                    previous_year_balance = pre_leave.annual_leave - pre_leave.leave_taken

                leave_summary_info = Leave_Summary(
                    user_id=data['user_id'],
                    year=year,
                    previous_year_balance=previous_year_balance,
                    annual_leave=previous_year_balance,
                    created_by=data["user_id"],
                    created_date=datetime.utcnow(),
                    isActive=1
                )

                if data["leave_type"] == '2':
                    leave_summary_info.medical_leave = leave.days_of_leave
                elif data["leave_type"] == '3':
                    leave_summary_info.leave_others = leave.days_of_leave
                else:
                    leave_summary_info.leave_taken = leave.days_of_leave

                save_changes(leave_summary_info)

            response_obj = {
                "message": "Leave Approved Successfully",
                "Errorcode": 9999,
                "leave_id":leave_id
            }

            notification_parms["notification_type"]="Leave Approve2"
            notification_parms["from_user"]=data["updated_by"]
            notification_parms["to_user"]= data["user_id"]
            notification_parms["is_web"]=0
            notification_parms["approve_status"] =1

            send_notification_new(notification_parms)

        elif status == 2:
            response_obj = {
                "message": "Leave Approved By HR",
                "Errorcode": 9999,
                "leave_id": leave_id
            }
            notification_parms["notification_type"] = "Leave Approve1"
            notification_parms["from_user"] = data["updated_by"]
            notification_parms["to_user"] = data["user_id"]
            notification_parms["is_web"] = 0
            notification_parms["approve_status"] = 1

            #send to RKP
            send_notification_new(notification_parms)

            # send to Operation role.
            notification_parms["from_user"] = data["user_id"]
            notification_parms["to_user"] = ""
            notification_parms["is_web"] = 1

            send_notification_new(notification_parms)
        else:
            response_obj = {
                "message": "Leave Rejected Successfully",
                "Errorcode": 9999,
                "leave_id": leave_id
            }
            notification_parms["notification_type"] = "Leave Reject"
            notification_parms["from_user"] = data["user_id"]
            notification_parms["to_user"] = "HR"
            notification_parms["is_web"] = 1
            notification_parms["approve_status"] = -1
            notification_parms["content"] = data['rejection_reason']

            if status == -2:
                #send to Opeartion role
                send_notification_new(notification_parms)
            if status == -3:
                notification_parms["to_user"] = "OPERATION"
                # send to HR role
                send_notification_new(notification_parms)


            # send to RKP
            notification_parms["from_user"] = data["updated_by"]
            notification_parms["to_user"] = data["user_id"]
            notification_parms["is_web"] = 0
            send_notification_new(notification_parms)

        return response_obj


    except Exception as e:
        print("Leave Applied service error: " + str(e))
        logging.exception(e)
        response_obj = {
            "message": "Leave Applied Failed",
            "Errorcode": 9998,
            "leave_id": 0
        }
        return response_obj

def getuserlist(page, row):
    try:
        user_query = User.query
        user_query = user_query.filter_by(isActive=1)
        user_list_count = user_query.count()
        user_list = user_query.order_by(desc(User.id)).paginate(int(page), int(row), False).items
        user_list_rsp = []

        for usr in user_list:

            data = {}

            data["email"] = usr.email
            data["id"] = usr.id
            data["name"] = usr.first_name + " " + usr.last_name

            user_list_rsp.append(data)

        response_obj = {
            "data": user_list_rsp,
            "total_count": user_list_count
        }
        return response_obj
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')

def getuserInformation(user_id):
    try:
        user_info = {}
        user_query = User.query.filter_by(id=user_id,isActive=1).first()

        if user_query:
            user_info["email"] = user_query.email
            user_info["id"] = user_query.id
            user_info["name"] = user_query.first_name + " " + user_query.last_name
            user_info["image_path"] = user_query.image_path
            user_info["reg_no"] = user_query.reg_no
            user_info["no_tel"] = user_query.no_tel
            user_info["ic_no"] = user_query.no_kp_baru
            user_info["date_of_employment"] = "" if (user_query.date_of_employment == '' or user_query.date_of_employment == None ) else user_query.date_of_employment.to_date.strftime('%d-%m-%Y')
            user_info["status"] = user_query.status

        response_obj = {
            "data": user_info,
        }
        return response_obj
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')

def updateleavecount(data):
    try:

        previous_year = str(int(data['year']) - 1)
        previous_year_balance = 0

        leave = Leave_Summary.query.filter_by(user_id=data['user_id'], year=data['year'], isActive=1).first()

        if leave:

            leave.leave_allocated = data["entitle_leave"]
            leave.medical_leave_allocated = data["entitle_medical_leave"]
            leave.annual_leave = data["entitle_leave"] + (0 if (leave.previous_year_balance == '' or leave.previous_year_balance == None) else leave.previous_year_balance)
            leave.updated_by = data["user_id"],
            leave.updated_date = datetime.utcnow(),

            if (leave.previous_year_balance == '' or leave.previous_year_balance == None or  leave.previous_year_balance == 0) :
                pre_leave = Leave_Summary.query.filter_by(user_id=data['user_id'], year=previous_year, isActive=1).first()

                if pre_leave:
                    previous_year_balance = pre_leave.annual_leave - pre_leave.leave_taken
                    leave.previous_year_balance = previous_year_balance
                    leave.annual_leave = data["entitle_leave"] + (previous_year_balance if (leave.previous_year_balance == '' or leave.previous_year_balance == None) else leave.previous_year_balance)

            save_changes(leave)
        else:

            leave = Leave_Summary.query.filter_by(user_id=data['user_id'], year=previous_year, isActive=1).first()

            if leave:
                previous_year_balance = leave.annual_leave - leave.leave_taken


            leave_summary_info = Leave_Summary(
                user_id=data['user_id'],
                year=data['year'],
                previous_year_balance= previous_year_balance,
                leave_allocated= data["entitle_leave"],
                annual_leave= data["entitle_leave"] + previous_year_balance ,
                medical_leave_allocated=data["entitle_medical_leave"],
                medical_leave=0,
                leave_others=0,
                leave_taken=0,
                created_by=data["user_id"],
                created_date=datetime.utcnow(),
                isActive=1
            )
            save_changes(leave_summary_info)

        response_obj = {
            "message": "Leave Details Updated Successfully",
            "Errorcode": 9999,
        }
        return response_obj

    except Exception as e:
        print("Leave Count Updated service error: " + str(e))
        logging.exception(e)
        response_obj = {
            "message": "Leave Count Updated Failed",
            "Errorcode": 9998,
        }
        return response_obj


def getleavesummaryinfo(userid,year):

    try:
        summary_data = {}
        res = Leave_Summary.query.filter_by(user_id=userid, year=year, isActive=1).first()

        if res:
            summary_data["summary_id"] = res.summary_id
            summary_data["leave_allocated"] = 0 if res.leave_allocated == None else res.leave_allocated
            summary_data["leave_taken"] = 0 if res.leave_taken == None else res.leave_taken
            summary_data["leave_others"] = 0 if res.leave_others == None else res.leave_others
            summary_data["balance_leave"] = ( res.annual_leave - res.leave_taken) if (res.annual_leave != None and res.leave_taken != None) else (res.annual_leave  if res.annual_leave != None else 0)
            summary_data["medical_leave_allocated"] = 0 if res.medical_leave_allocated == None else res.medical_leave_allocated
            summary_data["medical_leave"] =  0 if  res.medical_leave ==None else res.medical_leave
            summary_data["medical_leave_balance"] =  (res.medical_leave_allocated - res.medical_leave) if (res.medical_leave_allocated != None and res.medical_leave != None) else 0
            summary_data["previous_year_balance"] = 0 if res.previous_year_balance == None else res.previous_year_balance
            summary_data["annual_leave"] = 0 if res.annual_leave == None else res.annual_leave

        response_object = {
                "ErrorCode": 9999,
                "summary_data": summary_data,
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


def getleaveappliedlist(user_id,year,type):
    try:
        lst = []

        leave_list = db.session.query(Leave_Application, User,DropdownList) \
            .join(User, and_(Leave_Application.updated_by == User.id)) \
            .join(DropdownList, and_(Leave_Application.leave_type == DropdownList.key_id,DropdownList.type == 'leave_type')) \
            .filter(extract('year', Leave_Application.from_date) == int(year)) \
            .filter(extract('year', Leave_Application.to_date) == int(year)) \
            .filter(Leave_Application.isActive ==1,Leave_Application.status ==3,Leave_Application.user_id == user_id)

        if type == '2':
            leave_list = leave_list.filter(Leave_Application.leave_type == '2')
        else:
            leave_list = leave_list.filter(Leave_Application.leave_type != '2')

        leave_list=leave_list.order_by(desc(Leave_Application.leave_id)).all()

        for leave in leave_list:
            data = {}
            data["from_date"] =  "" if (leave.Leave_Application.from_date == '' or leave.Leave_Application.from_date == None) else leave.Leave_Application.from_date.strftime('%d-%m-%Y')
            data["to_date"] =  "" if (leave.Leave_Application.to_date == '' or leave.Leave_Application.to_date == None) else leave.Leave_Application.to_date.strftime('%d-%m-%Y')
            data["approved_by"] = leave.User.rkp_name if leave.User.rkp_name != None and leave.User.rkp_name != "" else leave.User.first_name + (" " if leave.User.last_name == None else leave.User.last_name )
            data["leave_type"] = leave.DropdownList.key_value_en

            lst.append(data)

        response_obj = {
            "ErrorCode": 9999,
            "data": lst,
        }
        return response_obj

    except Exception as e:
        logging.exception(e)
        response_object = {
            "message": "Exception",
            "ErrorCode": "0000",
            "data": []
        }
        return response_object

def addmedicalclaim(data):
    try:
        day = datetime.utcnow()
        year = str(day.year)

        previous_claim_amount = 0

        claim = Medical_Claim.query.filter_by(claim_id=data["claim_id"], isActive=1).first()

        if claim:
            previous_claim_amount = claim.claim_amount
            claim.user_id = data["user_id"],
            claim.year = year,
            claim.claim_date = common.convertdmy_to_date2(data["medical_date"]),
            claim.claim_type = data["claim_type"],
            claim.claim_amount = data["claim_amount"],
            claim.clinic_name = data["clinic_name"],
            claim.ori_file_name = data["ori_file_name"],
            claim.uuid_file_name = data["uuid_file_name"],
            claim.updated_by = data["user_id"],
            claim.updated_date = datetime.utcnow(),

            save_changes(claim)
        else:
            medical_claim_info = Medical_Claim(
                user_id = data["user_id"],
                year = year,
                claim_date = common.convertdmy_to_date2(data["medical_date"]),
                claim_type =  data["claim_type"],
                claim_amount =  data["claim_amount"],
                clinic_name =  data["clinic_name"],
                ori_file_name = data["ori_file_name"],
                uuid_file_name = data["uuid_file_name"],
                created_by = data["user_id"],
                created_date = datetime.utcnow(),
                isActive = 1
            )
            save_changes(medical_claim_info)


        amount_claimed = Decimal(data["claim_amount"]) - previous_claim_amount


        medical_claim_info = Medical_Claim_Summary.query.filter_by(user_id=data["user_id"], year=year, isActive=1).first()

        if medical_claim_info:

            if data["claim_type"] == 'Medical' :
                total_claim = amount_claimed if (medical_claim_info.total_claim_medical == None or medical_claim_info.total_claim_medical == 0) else medical_claim_info.total_claim_medical + amount_claimed
                medical_claim_info.total_claim_medical = total_claim
                medical_claim_info.balance_claim_medical = 0 if ( medical_claim_info.entitle_claim == None or medical_claim_info.entitle_claim == 0) else medical_claim_info.entitle_claim - total_claim

            elif data["claim_type"] == 'Check Up' :
                total_claim = amount_claimed if (medical_claim_info.total_claim_checkup == None or medical_claim_info.total_claim_checkup == 0) else medical_claim_info.total_claim_checkup + amount_claimed
                medical_claim_info.total_claim_checkup = total_claim

            save_changes(medical_claim_info)

        else:
            medical_claim_summary_info = Medical_Claim_Summary(
                user_id=data['user_id'],
                year=year,
                entitle_claim=0,
                created_by=data["user_id"],
                created_date=datetime.utcnow(),
                isActive=1
            )
            if data["claim_type"] == 'Medical':
                medical_claim_summary_info.total_claim_medical = data["claim_amount"]

            elif data["claim_type"] == 'Check Up':
                medical_claim_summary_info.total_claim_checkup = data["claim_amount"]

            save_changes(medical_claim_summary_info)




        response_obj = {
            "message": "Medical Claim Added Successfully",
            "Errorcode": 9999,
        }
        return response_obj

    except Exception as e:
        print("Medical Claim Added service error: " + str(e))
        logging.exception(e)
        response_obj = {
            "message": "Medical Claim Added Failed",
            "Errorcode": 9998,
        }
        return response_obj


def getmedicalclaimlist(user_id,year):
    try:
        lst = []

        claim_list = db.session.query(Medical_Claim, User) \
            .join(User, and_(Medical_Claim.user_id == User.id)) \
            .filter(extract('year', Medical_Claim.claim_date) == int(year)) \
            .filter(Medical_Claim.isActive == 1,Medical_Claim.user_id == user_id)

        claim_list = claim_list.order_by(desc(Medical_Claim.claim_id)).all()

        for claim in claim_list:
            data = {}
            data["claim_id"] = claim.Medical_Claim.claim_id
            data["claim_date"] = "" if (claim.Medical_Claim.claim_date == '' or claim.Medical_Claim.claim_date == None) else claim.Medical_Claim.claim_date.strftime('%d-%m-%Y')
            data["claim_type"] = claim.Medical_Claim.claim_type
            data["claim_amount"] = float(claim.Medical_Claim.claim_amount)
            data["clinic_name"] = claim.Medical_Claim.clinic_name
            data["approved_by"] = claim.User.rkp_name if claim.User.rkp_name != None and claim.User.rkp_name != "" else claim.User.first_name + ("" if claim.User.last_name == None else claim.User.last_name )
            data["ori_file_name"] = claim.Medical_Claim.ori_file_name if claim.Medical_Claim.ori_file_name else ""
            data["uuid_file_name"] = claim.Medical_Claim.uuid_file_name if claim.Medical_Claim.uuid_file_name else ""
            lst.append(data)

        response_obj = {
            "ErrorCode": "9999",
            "data": lst,
        }
        return response_obj

    except Exception as e:
        logging.exception(e)
        response_object = {
            "message": "Exception",
            "ErrorCode": "0000",
            "data": []
        }
        return response_object

def getmedicalclaim(claim_id):
    try:
        data = {}
        claim = Medical_Claim.query.filter_by(claim_id=claim_id,isActive=1).first()

        if claim:
            data["claim_id"] = claim.claim_id
            data["claim_date"] = "" if (claim.claim_date == '' or claim.claim_date == None) else claim.claim_date.strftime('%d-%m-%Y')
            data["claim_type"] = claim.claim_type
            data["claim_amount"] = float(claim.claim_amount)
            data["clinic_name"] = claim.clinic_name
            data["ori_file_name"] = claim.ori_file_name
            data["uuid_file_name"] = claim.uuid_file_name


            response_obj = {
                    "ErrorCode": "9999",
                    "data": data,
            }
        else:
            response_obj = {
                "ErrorCode": "9998",
                "data": data,
            }
        return response_obj

    except Exception as e:
        logging.exception(e)
        response_object = {
            "message": "Exception",
            "ErrorCode": "0000",
            "data": []
        }
        return response_object

def delete_medicalclaim(data):
    try:
        claim = Medical_Claim.query.filter_by(isActive=1, claim_id=data["claim_id"]).first()

        if claim:
            claim.isActive = "0"
            claim.updated_by = data["user_id"]
            claim.updated_date = datetime.utcnow()

            save_changes(claim)

            medical_claim_info = Medical_Claim_Summary.query.filter_by(user_id=claim.user_id, year=claim.year,
                                                                       isActive=1).first()

            if medical_claim_info:

                if claim.claim_type == 'Medical':
                    medical_claim_info.total_claim_medical = medical_claim_info.total_claim_medical - claim.claim_amount
                    medical_claim_info.balance_claim_medical = medical_claim_info.balance_claim_medical + claim.claim_amount

                elif claim.claim_type == 'Check Up':
                    medical_claim_info.total_claim_checkup =  medical_claim_info.total_claim_checkup - claim.claim_amount

                save_changes(medical_claim_info)

            response_object = {
                "ErrorCode": "9999",
                "Status": "Medical Claim delete successfully"
            }

        else:
            response_object = {
                "ErrorCode": "9997",
                "Status": "Medical Claim not exists"
            }
        return response_object, 201

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Medical Claim delete failed"
        }

        return response_object, 201

def getmedicalclaimsummaryinfo(userid,year):

    try:
        summary_data = {}
        res = Medical_Claim_Summary.query.filter_by(user_id=userid, year=year, isActive=1).first()

        if res:
            summary_data["medical_summary_id"] = res.medical_summary_id
            summary_data["entitle_claim"] = 0 if res.entitle_claim == None else float(res.entitle_claim)
            summary_data["total_claim_medical"] = 0 if res.total_claim_medical == None else  float(res.total_claim_medical)
            summary_data["total_claim_checkup"] = 0 if res.total_claim_checkup == None else  float(res.total_claim_checkup)
            summary_data["balance_claim_medical"] = 0 if res.balance_claim_medical == None else  float(res.balance_claim_medical)

        response_object = {
                "ErrorCode": "9999",
                "summary_data": summary_data,
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

def updatemediclaimsummary(data):
    try:

        claim = Medical_Claim_Summary.query.filter_by(user_id=data['user_id'], year=data['year'], isActive=1).first()

        if claim:
            claim.entitle_claim = data["entitle_claim"],
            claim.updated_by = data["user_id"],
            claim.updated_date = datetime.utcnow(),
            save_changes(claim)
        else:

            medical_claim_summary_info = Medical_Claim_Summary(
                user_id=data['user_id'],
                year=data['year'],
                entitle_claim = data["entitle_claim"],
                created_by=data["user_id"],
                created_date=datetime.utcnow(),
                isActive=1
            )
            save_changes(medical_claim_summary_info)

        response_obj = {
            "message": "Medical Claim Updated Successfully",
            "Errorcode": 9999,
        }
        return response_obj

    except Exception as e:
        print("Leave Count Updated service error: " + str(e))
        logging.exception(e)
        response_obj = {
            "message": "Medical Claim Updated Failed",
            "Errorcode": 9998,
        }
        return response_obj


def userbalanceleavecount(page,row,search):

    try:
        lst = []
        day = datetime.utcnow()
        year = str(day.year)

        user_list = db.session.query(User,Leave_Summary ) \
            .outerjoin(Leave_Summary, and_(User.id == Leave_Summary.user_id,Leave_Summary.year == year)).filter(
            User.isActive == 1)


        if search != '' and search != "\"\"":
            search = "%{}%".format(search)
            user_list = user_list.filter(or_(User.rkp_name.ilike(search),User.first_name.ilike(search),User.last_name.ilike(search),User.rkp_ic_number.ilike(search),User.email.ilike(search)))

        count = user_list.count()
        user_list = user_list.order_by(desc(User.id)).paginate(int(page), int(row),False).items

        if user_list:

            for user in user_list:
                data = {}
                data['user_id'] = user.User.id
                data['user_name'] = user.User.rkp_name if user.User.rkp_name != None and user.User.rkp_name != "" else user.User.first_name + ("" if user.User.last_name == None else user.User.last_name )
                data["balance_medical_leave"] = 0 if user.Leave_Summary == None else  (user.Leave_Summary.medical_leave_allocated - user.Leave_Summary.medical_leave) if (user.Leave_Summary.medical_leave_allocated != None and user.Leave_Summary.medical_leave != None ) else 0
                data["balance_leave"] = 0 if user.Leave_Summary == None else (user.Leave_Summary.annual_leave - user.Leave_Summary.leave_taken) if user.Leave_Summary.annual_leave != None and user.Leave_Summary.leave_taken != None else 0

                lst.append(data)

        response_object = {
                "ErrorCode": "9999",
                "summary_data": lst,
                "count": count
            }

        return response_object
    except Exception as e:
        logging.exception(e)
        response_object = {
            "message": "Exception",
            "ErrorCode": "0000",
            "data": [],
            "Error": str(e)
        }
        return response_object


def getapprovedleavecount(month,year):

    try:
        lst = []
        total_approve_count = 0
        day = timedelta(days=1)
        date1 = datetime(int(year), int(month), 1)
        d = date1
        dates = []
        while d.month == int(month):
            dates.append(d.strftime('%d-%m-%Y'))
            d += day

        res = Leave_Application.query\
            .filter(extract('month', Leave_Application.from_date) == int(month))\
            .filter(extract('year', Leave_Application.from_date) == int(year)) \
            .filter(extract('month', Leave_Application.to_date) == int(month)) \
            .filter(extract('year', Leave_Application.to_date) == int(year)) \
            .filter(Leave_Application.isActive == 1).all()

        for day in dates:
            day = datetime.strptime(day, "%d-%m-%Y")
            approve_count = 0
            date_arr = {}

            for data in res:

                from_date = data.from_date
                to_date = data.to_date
                status = data.status

                if from_date <= day <= to_date :
                    if status == 2:
                        approve_count = approve_count + 1
                        total_approve_count = total_approve_count + 1

            if (approve_count > 0):
                date_arr['date'] = day.strftime('%d-%m-%Y')
                date_arr['approve_count'] = approve_count
                lst.append(date_arr)

        response_object = {
                "ErrorCode": "9999",
                "total_approve_count": total_approve_count,
                "data": lst

            }

        return response_object
    except Exception as e:
        logging.exception(e)
        response_object = {
            "ErrorCode": "0000",
            "total_approve_count": 0,
            "data": {}
        }
        return response_object

def approveduserlist(given_date):

    try:
        approve_list = []

        day = datetime.strptime(given_date, "%d-%m-%Y")
        month = day.month
        year = day.year

        res = Leave_Application.query \
            .filter(extract('month', Leave_Application.from_date) == int(month))\
            .filter(extract('year', Leave_Application.from_date) == int(year)) \
            .filter(extract('month', Leave_Application.to_date) == int(month)) \
            .filter(extract('year', Leave_Application.to_date) == int(year)) \
            .filter(Leave_Application.isActive == 1,Leave_Application.status != -1 ).all()

        for data in res:
            leave_data={}
            leave_id = data.leave_id
            userid = data.user_id
            from_date = data.from_date
            to_date = data.to_date
            status = data.status

            if from_date <= day <= to_date:
                user_name = ""
                user = User.query.filter_by(id=userid).first()
                if user:
                    user_name = str(user.first_name)+" "+(str(user.last_name) if user.last_name != None else "")

                if status == 2:
                    leave_data['leave_id'] = leave_id
                    leave_data['user_id'] = userid
                    leave_data['user_name'] = user_name
                    approve_list.append(leave_data)

        response_object = {
                "ErrorCode": "9999",
                "approve_list": approve_list,
            }

        return response_object

    except Exception as e:
        logging.exception(e)
        response_object = {
            "ErrorCode": "0000",
            "approve_list": [],
        }
        return response_object

def usermedicalclaimsummary(year,search,page,row):

    try:
        lst = []

        user_list = db.session.query(Medical_Claim_Summary, User) \
            .join(User, and_(Medical_Claim_Summary.user_id == User.id)).filter(User.isActive == 1,Medical_Claim_Summary.year == year)

        if search != '' and search != "\"\"":
            search = "%{}%".format(search)
            user_list = user_list.filter(or_(User.rkp_name.ilike(search), User.first_name.ilike(search), User.last_name.ilike(search),User.rkp_ic_number.ilike(search), User.email.ilike(search)))

        user_list = user_list.order_by(desc(User.id)).paginate(int(page), int(row), False).items

        if user_list:

            for user in user_list:
                data = {}
                data['user_id'] = user.User.id
                data['user_name'] = user.User.rkp_name if user.User.rkp_name != None and user.User.rkp_name != "" else user.User.first_name + ("" if user.User.last_name == None else user.User.last_name ) 
                data['user_location'] = user.User.location
                data["entitle_claim"] = float(user.Medical_Claim_Summary.entitle_claim) if user.Medical_Claim_Summary.entitle_claim != None else "0"
                data["total_claim_medical"] = float(user.Medical_Claim_Summary.total_claim_medical) if user.Medical_Claim_Summary.total_claim_medical != None else "0"
                data["balance_claim_medical"] = float(user.Medical_Claim_Summary.balance_claim_medical) if user.Medical_Claim_Summary.balance_claim_medical != None else "0"

                lst.append(data)

        response_object = {
                "ErrorCode": "9999",
                "summary_data": lst,
            }

        return response_object
    except Exception as e:
        logging.exception(e)
        response_object = {
            "message": "Exception",
            "ErrorCode": "0000",
            "data": []
        }
        return response_object

def usermedicalcheckupsummary(year,search,page,row):

    try:
        lst = []
        total_checkup_claim = 0

        mcheckup_date_sub_query = db.session.query(Medical_Claim.claim_date).select_from(Medical_Claim). \
            filter(Medical_Claim.user_id == User.id,Medical_Claim.year == year,Medical_Claim.claim_type == "Check Up").order_by(desc(Medical_Claim.claim_id)).limit(1).label("latest_claim_date")

        total_checkup_claim = db.session.query(func.sum(Medical_Claim_Summary.total_claim_checkup).label("total_checkup_claim")).select_from(Medical_Claim_Summary) \
            .filter(Medical_Claim_Summary.isActive == 1, Medical_Claim_Summary.year == year).first()

        total_checkup_claim = float(total_checkup_claim.total_checkup_claim) if total_checkup_claim.total_checkup_claim != None else "0"

        user_list = db.session.query(Medical_Claim_Summary, User,mcheckup_date_sub_query) \
            .join(User, and_(Medical_Claim_Summary.user_id == User.id)).filter(User.isActive == 1,Medical_Claim_Summary.year == year)

        if search != '' and search != "\"\"":
            search = "%{}%".format(search)
            user_list = user_list.filter(or_(User.rkp_name.ilike(search), User.first_name.ilike(search), User.last_name.ilike(search),User.rkp_ic_number.ilike(search), User.email.ilike(search)))


        user_list = user_list.order_by(desc(User.id)).paginate(int(page), int(row), False).items


        if user_list:

            for user in user_list:
                data = {}
                data['user_id'] = user.User.id
                data['user_name'] = user.User.rkp_name if user.User.rkp_name != None and user.User.rkp_name != "" else user.User.first_name + ("" if user.User.last_name == None else user.User.last_name )
                data['user_location'] = user.User.location
                data["last_medi_check_date"] = user.latest_claim_date.strftime('%d-%m-%Y') if user.latest_claim_date != None and user.latest_claim_date != "" else ""
                data["total_claim_checkup"] = float(user.Medical_Claim_Summary.total_claim_checkup) if user.Medical_Claim_Summary.total_claim_checkup != None else "0"

                lst.append(data)

        response_object = {
                "ErrorCode": "9999",
                "summary_data": lst,
                "total_checkup_claim":total_checkup_claim
            }

        return response_object
    except Exception as e:
        logging.exception(e)
        response_object = {
            "message": "Exception",
            "ErrorCode": "0000",
            "data": []
        }
        return response_object

def DocumentUpload(data):
    try:
        file=data.files['file']
        if file:
            org_filename = secure_filename(file.filename)
            ext = org_filename.split('.')[1].split('?')[0]
            uuid_file = str(uuid.uuid4())
            # uuid_filename = uuid_file+"_"+data.args['user_id']+ "." + ext
            uuid_filename = uuid_file + "." + ext
            directory = os.path.join(config.leave_docs)
            if not os.path.exists(directory):
                os.makedirs(directory)
            file.save(os.path.join(config.leave_docs, uuid_filename))

            response_obj = {
                "ErrorCode": 9999,
                "uuid_filename": uuid_filename,
                "org_filename": org_filename
            }
        else:
            response_obj = {
                "ErrorCode": 9998,
                "uuid_filename": "",
                "org_filename": ""
            }

    except Exception as e:
        print(e)
        logging.exception(str(e))
        print('Save file details error: ' + str(e))

        response_obj = {
            "ErrorCode": 0000,
            "uuid_filename": "",
            "org_filename": ""
        }

    return response_obj

def get_leave_document(filename):
    try:
        # uploads = os.path.join(config.doc_savedir, filename)
        return send_from_directory(directory=config.leave_docs, filename=filename)

    except Exception as e:
        print(e)


def DocumentUpload_Claim(file):
    try:
        if file:
            org_filename = secure_filename(file.filename)
            ext = org_filename.split('.')[1].split('?')[0]
            uuid_file = str(uuid.uuid4())
            uuid_filename = uuid_file + "." + ext
            directory = os.path.join(config.medical_claim_docs)
            if not os.path.exists(directory):
                os.makedirs(directory)
            file.save(os.path.join(config.medical_claim_docs, uuid_filename))

            response_obj = {
                "ErrorCode": 9999,
                "uuid_filename": uuid_filename,
                "org_filename": org_filename
            }
        else:
            response_obj = {
                "ErrorCode": 9998,
                "uuid_filename": "",
                "org_filename": ""
            }

    except Exception as e:
        print(e)
        logging.exception(str(e))
        print('Save file details error: ' + str(e))

        response_obj = {
            "ErrorCode": 0000,
            "uuid_filename": "",
            "org_filename": ""
        }

    return response_obj

def download_doc(file_name):
    try:
        directory = os.path.join(config.medical_claim_docs)
        # path = directory+"/"+file_name
        # return send_file(path, as_attachment=True)
        return send_from_directory(directory, file_name)
    except Exception as e:
        print(e)


def save_changes(data):
    db.session.add(data)
    db.session.commit()