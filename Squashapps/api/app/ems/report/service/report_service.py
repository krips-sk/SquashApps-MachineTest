import logging
from app.cura import db
from datetime import datetime,timedelta,time
from app.cura.user.model.user import User

from app.ems.leave_management.model.leave_application import Leave_Application
from app.ems.leave_management.model.leave_summary import Leave_Summary
from app.ems.predeparture.model.rkp_login import RKPLogin
from ..model.report_download import Report_Download
from sqlalchemy import extract, and_, desc
import json
import os
import uuid
from app.ems import config
import subprocess
from flask import send_from_directory
from app.ems.dropdown_list.model.dropdown import DropdownList


def leavesummary(month,year,page,row):

    try:
        lst = []

        day = timedelta(days=1)
        date1 = datetime(int(year), int(month), 1)
        d = date1
        dates = []
        while d.month == int(month):
            dates.append(d.strftime('%d-%m-%Y'))
            d += day


        user_list = db.session.query(User,Leave_Summary ) \
            .outerjoin(Leave_Summary, and_(User.id == Leave_Summary.user_id,Leave_Summary.year == year)).filter(User.isActive == 1)

        user_list = user_list.order_by(desc(User.id)).paginate(int(page), int(row), False).items

        if user_list:

            for user in user_list:
                data = {}
                data['user_id'] = user.User.id
                data['user_name'] = user.User.rkp_name if user.User.rkp_name != None and user.User.rkp_name != "" else user.User.first_name + ("" if user.User.last_name == None else user.User.last_name )
                data['user_location'] = user.User.location
                data['start_of_employment'] = "" if (user.User.employment_date == '' or user.User.employment_date == None) else user.User.employment_date.strftime('%d-%m-%Y')


                if user.Leave_Summary != None :
                    data['previous_year_balance'] = 0 if user.Leave_Summary.previous_year_balance == None else user.Leave_Summary.previous_year_balance
                    data['leave_allocated'] = 0 if user.Leave_Summary.leave_allocated == None else user.Leave_Summary.leave_allocated
                    data['annual_leave'] = 0 if user.Leave_Summary.annual_leave == None else user.Leave_Summary.annual_leave
                    data['leave_taken'] = 0 if user.Leave_Summary.leave_taken == None else user.Leave_Summary.leave_taken
                    data["balance_leave"] = 0 if user.Leave_Summary == None else (user.Leave_Summary.annual_leave - user.Leave_Summary.leave_taken) if user.Leave_Summary.annual_leave != None and user.Leave_Summary.leave_taken != None else 0
                    data['leave_others'] = 0 if user.Leave_Summary.leave_others == None else user.Leave_Summary.leave_others
                    data['medical_leave_allocated'] = 0 if  user.Leave_Summary.medical_leave_allocated == None else user.Leave_Summary.medical_leave_allocated
                    data['medical_leave'] = 0 if  user.Leave_Summary.medical_leave == None else user.Leave_Summary.medical_leave
                    data["balance_medical_leave"] = 0 if user.Leave_Summary == None else (
                                user.Leave_Summary.medical_leave_allocated - user.Leave_Summary.medical_leave) if (
                                user.Leave_Summary.medical_leave_allocated != None and user.Leave_Summary.medical_leave != None) else 0

                else:
                    data['previous_year_balance'] = 0
                    data['leave_allocated'] = 0
                    data['annual_leave'] = 0
                    data['leave_taken'] = 0
                    data["balance_leave"] = 0
                    data['leave_others'] = 0
                    data['medical_leave_allocated'] = 0
                    data['medical_leave'] = 0
                    data["balance_medical_leave"] = 0

                leave_applied = db.session.query(Leave_Application,DropdownList) \
                                .join(DropdownList,and_(Leave_Application.leave_type == DropdownList.key_id, DropdownList.type == 'leave_type')) \
                                .filter(extract('month', Leave_Application.from_date) == int(month))\
                                .filter(extract('year', Leave_Application.from_date) == int(year)) \
                                .filter(extract('month', Leave_Application.to_date) == int(month)) \
                                .filter(extract('year', Leave_Application.to_date) == int(year)) \
                                .filter(Leave_Application.user_id ==user.User.id, Leave_Application.status==3, Leave_Application.isActive==1).order_by(desc(Leave_Application.leave_id)).all()

                applied_leave_lst = []

                if leave_applied:
                    for day in dates:
                        day = datetime.strptime(day, "%d-%m-%Y")
                        date_arr = {}
                        leave_type = ''
                        is_date_matched = False
                        for leave in leave_applied:

                            from_date = leave.Leave_Application.from_date
                            to_date = leave.Leave_Application.to_date
                            leave_type = leave.DropdownList.key_value_en

                            if from_date <= day <= to_date:
                                is_date_matched = True
                                date_arr['date'] = day.strftime('%d-%m-%Y')
                                date_arr['type'] = leave_type

                        if not is_date_matched:
                            date_arr['date'] = day.strftime('%d-%m-%Y')
                            date_arr['type'] = ''

                        obj_already_exists = False
                        for obj in applied_leave_lst:
                            if obj['date'] == day.strftime('%d-%m-%Y'):
                                obj_already_exists = True

                        if not obj_already_exists:
                            applied_leave_lst.append(date_arr)
                else:
                    for day in dates:
                        day = datetime.strptime(day, "%d-%m-%Y")
                        date_arr = {}
                        date_arr['date'] = day.strftime('%d-%m-%Y')
                        date_arr['type'] = ''
                        applied_leave_lst.append(date_arr)

                data['applied_leave_lst'] = applied_leave_lst


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


def summary_report_download(month,year,type,userid):

    try:

        type_value=''

        if type == '1':
            type_value ="Leave_Summary"
        else:
            type_value = "Work_Summary"

        publicid = str(uuid.uuid4())
        new_report = Report_Download(
            public_id=publicid,
            month=month,
            year=year,
            type=type_value,
            status=0,
            created_by=userid,
            created_date=datetime.utcnow(),
            isActive=1

        )
        save_changes(new_report)

        if type == '1':
            service_path = os.path.abspath(os.path.dirname("jobs/LeaveSummary_Report/")) + "/service.py"
            run_dir = os.path.abspath(os.path.dirname("jobs/LeaveSummary_Report/"))
        else:
            service_path = os.path.abspath(os.path.dirname("jobs/WorkSummary_Report/")) + "/service.py"
            run_dir = os.path.abspath(os.path.dirname("jobs/WorkSummary_Report/"))

        logging.exception("Processing report Generation")

        logging.exception("running :" + service_path)
        #########################################################
        # Starting the process in background
        ##################################################################
        if os.name == 'nt':
            subprocess.run(
                [config.Python_Version, service_path,publicid])
        else:
            subprocess.Popen(
                ['nohup', config.Python_Version,
                 service_path,publicid],
                stdout=open('jobs.log', 'a'),
                stderr=open('logfile.log', 'a'),
                cwd=run_dir,
                preexec_fn=os.setpgrp)
        # subprocess.run([config.Python_Version, service_path, publicid])
        logging.exception("sub process started.")
        ##################################################################
        #########################################################

        response_object = {
            'status': 'success',
            'message': 'Successfully updated.',
            'publicid': publicid
        }
        return response_object, 200

    except Exception as e:
        logging.exception(e)
        response_object = {
            "message": "Exception",
            "ErrorCode": "0000",
            "data": []
        }
        return response_object


def workhoursummary(month,year,page,row):

    try:
        lst = []

        day = timedelta(days=1)
        date1 = datetime(int(year), int(month), 1)
        d = date1
        dates = []
        while d.month == int(month):
            dates.append(d.strftime('%d-%m-%Y'))
            d += day


        user_list = User.query.filter_by(isActive=1)

        user_list = user_list.order_by(desc(User.id)).paginate(int(page), int(row), False).items

        if user_list:

            for user in user_list:

                current_month_work_hrs = 0

                data = {}
                data['user_id'] = user.id
                data['user_name'] = user.rkp_name if user.rkp_name != None and user.rkp_name != "" else user.first_name + ("" if user.last_name == None else user.last_name )
                data['user_location'] = user.location
                data['start_of_employment'] = "" if (user.employment_date == '' or user.employment_date == None) else user.employment_date.strftime('%d-%m-%Y')
                data['accumulated_work_hrs'] = 0


                working_hrs_data = RKPLogin.query\
                                .filter(extract('month', RKPLogin.start_date) == int(month))\
                                .filter(extract('year', RKPLogin.start_date) == int(year)) \
                                .filter(extract('month', RKPLogin.stoped_date) == int(month)) \
                                .filter(extract('year', RKPLogin.stoped_date) == int(year)) \
                                .filter_by(user_id=user.id, rt_status=2, isActive=1).all()

                working_hrs_data_lst = []

                if working_hrs_data:

                    for day in dates:
                        day = datetime.strptime(day, "%d-%m-%Y")

                        last_hrs = datetime.combine(day, time.max)
                        first_hrs = datetime.combine(day, time.min)

                        for hrs_data in working_hrs_data:
                            start_date = hrs_data.start_date
                            stoped_date = hrs_data.stoped_date

                            mins_val = 0

                            if start_date.date() <= day.date() <= stoped_date.date():

                                if start_date.date() == day.date() and stoped_date.date() == day.date():
                                    difference_date = stoped_date - start_date
                                    mins = divmod(difference_date.total_seconds(), 60)
                                    mins_val = mins[0]

                                elif start_date.date() == day.date() and stoped_date.date() != day.date():
                                    difference_date = last_hrs - start_date
                                    mins = divmod(difference_date.total_seconds(), 60)
                                    mins_val = mins[0]

                                elif start_date.date() != day.date() and stoped_date.date() == day.date():
                                    difference_date =  stoped_date - first_hrs
                                    mins = divmod(difference_date.total_seconds(), 60)
                                    mins_val = mins[0]

                                else:
                                    mins = 1440
                                    mins_val = mins


                                obj_already_exists = False
                                if working_hrs_data_lst:

                                    for obj in working_hrs_data_lst:
                                        if obj['date'] == day.strftime('%d-%m-%Y'):
                                            obj_already_exists = True
                                            mins_data = obj['value'] if obj['value'] != '' else '0:00'
                                            val_diff = datetime.strptime(mins_data,"%H:%M") - datetime.strptime("0:00","%H:%M")
                                            val_mins = divmod(val_diff.total_seconds(),60)
                                            mins_data = int(val_mins[0])
                                            tot_mins = mins_data + mins_val
                                            obj['value'] = "{}:{}".format(*divmod(int(tot_mins), 60))

                                if not obj_already_exists:
                                    date_arr = {}
                                    date_arr['date'] = day.strftime('%d-%m-%Y')
                                    date_arr['value'] = "{}:{}".format(*divmod(int(mins_val), 60))
                                    working_hrs_data_lst.append(date_arr)

                                current_month_work_hrs = current_month_work_hrs+mins_val

                            else:
                                obj_already_exists = False
                                if working_hrs_data_lst:
                                    for obj in working_hrs_data_lst:
                                        if obj['date'] == day.strftime('%d-%m-%Y'):
                                            obj_already_exists = True

                                if not obj_already_exists:
                                    date_arr = {}
                                    date_arr['date'] = day.strftime('%d-%m-%Y')
                                    date_arr['value'] = ""
                                    working_hrs_data_lst.append(date_arr)
                else:
                    for day in dates:
                        day = datetime.strptime(day, "%d-%m-%Y")
                        date_arr = {}
                        date_arr['date'] = day.strftime('%d-%m-%Y')
                        date_arr['value'] = ""
                        working_hrs_data_lst.append(date_arr)

                data['working_hrs_lst'] = working_hrs_data_lst
                data['current_month_work_hrs'] = "{}:{}".format(*divmod(int(current_month_work_hrs), 60))
                data['total_work_hrs'] = "{}:{}".format(*divmod(int(current_month_work_hrs), 60))
                lst.append(data)

        response_object = {
                "ErrorCode": "9999",
                "summary_data": lst,
            }

        return response_object
    except Exception as e:
        logging.exception(e)
        response_object = {
            "message": str(e),
            "ErrorCode": "0000",

            "data": []
        }
        return response_object

def get_report_list(page,row,type):

    try:
        lst = []

        if type == '1':
            type_value = "Leave_Summary"
        else:
            type_value = "Work_Summary"

        report_list = Report_Download.query.filter_by(isActive=1,type=type_value)

        report_list = report_list.order_by(desc(Report_Download.download_id)).paginate(int(page), int(row), False).items

        if report_list:

            for report in report_list:
                data = {}

                data['download_id'] = report.download_id
                data['public_id'] = report.public_id
                data['type'] = report.type
                data['month'] = report.month
                data['year'] = report.year
                data['file_path'] = report.file_path
                data['status'] = int(report.status)
                data['created_date'] = report.created_date.strftime('%d/%m/%Y')

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

def get_report_status(public_id):

    try:
        report = Report_Download.query.filter_by(public_id=public_id,isActive=1).first()

        if report:
            data = {}
            data['download_id'] = report.download_id
            data['public_id'] = report.public_id
            data['type'] = report.type
            data['month'] = report.month
            data['year'] = report.year
            data['file_path'] = report.file_path
            data['status'] = int(report.status)

            response_object = {
                    "ErrorCode": "9999",
                    "summary_data": data,
                }
        else:
            response_object = {
                "ErrorCode": "9999",
                "summary_data": {},
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

def get_file(public_id):
    try:

        report = Report_Download.query.filter_by(public_id=public_id, isActive=1).first()

        if report:
            file_name = report.file_path
            directory = os.path.join(config.Download_File_Path+"/summary_report")
            return send_from_directory(directory,file_name, as_attachment=True)

    except Exception as e:
        logging.exception(e)
        response_object = {
            "message": "Exception",
            "ErrorCode": "0000",
            "data": []
        }
        return response_object

def save_changes(data):
    db.session.add(data)
    db.session.commit()