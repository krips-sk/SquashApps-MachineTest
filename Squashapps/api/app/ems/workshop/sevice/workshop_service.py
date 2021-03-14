# Name: workshop_service.py
# Description: used for workshop related operation.
# Author: Mycura
# Created: 2020.12.16
# Copyright: © 2020 EMS . All Rights Reserved.
# Change History:
#                |2020.12.16

import datetime
import os
import subprocess
import uuid

from werkzeug.utils import secure_filename

from app.cura import db
import logging
from sqlalchemy import or_, desc, asc, and_, case, func, extract, literal_column, func
from app.cura.common import common
from app.ems import config
from app.ems.audit_log.model.audit_log import AuditLog
from app.ems.branch.model.branch import Branch
from app.ems.department.model.department import Department
from app.ems.predeparture.model.CheckList import Checklist
from app.ems.predeparture.model.InspectionItem import InspectionItem
from app.ems.supplier.model.supplier import Supplier
from app.ems.workshop.model.adhoc_breakdown import AdhocBreakdown
from app.ems.workshop.model.report_branch_parts import ReportBranchParts
from app.ems.workshop.model.report_branch_parts_summary import ReportBranchPartsSummary
from app.ems.workshop.model.report_corrective_detail import ReportCorrectiveDetail
from app.ems.workshop.model.report_corrective_head import ReportCorrectiveHead
from app.ems.workshop.model.report_expense import ReportExpense
from app.ems.workshop.model.report_purchase import ReportWorkshopPurchase
from app.ems.workshop.model.report_tracker import ReportTracker
from app.ems.workshop.model.schedule_maintenance import ScheduledMaintenance
from ...workshop.model.workshop_parts import  WorkshopParts
from ...workshop.model.workshop_workaction import  WorkshopWorkAction

from app.cura.user.model.user import User
from app.ems.predeparture.model.PDCRegistration import PDCRegistration
from app.ems.vehicle.model.vehicle import Vehicle


def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        print(e)


def save_inspection_item(full_data, reference_id, created_by, inspection_type):
    pdc_item_res = []
    try:
        for data in full_data:
            new_adc_item = InspectionItem(
                reference_id=reference_id,
                inspection_type=inspection_type,
                inspections_defects=data["inspections_defects"],
                technician_remarks=data["technician_remarks"],
                workshop_status=data["workshop_status"],
                created_by=created_by,
                created_date=datetime.datetime.utcnow()
            )
            save_changes(new_adc_item)
            response_object = {
                "ErrorCode": "9999",
                "Status": "Adhoc added successfully",
                "inspection_id": new_adc_item.reference_id
            }
            pdc_item_res.append(response_object)

        return pdc_item_res

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Adhoc save failed",
            "Error": str(e)
        }
        pdc_item_res.append(response_object)
        return pdc_item_res


#
#   feat - Used to add/update the PDC Registration
#
def save_adhoc(data):
    try:
        if data["adhoc_breakdown_id"] == 0:
            new_adc = AdhocBreakdown(
                date_in=common.convertdmy_to_date2(data["date_in"]),
                mechanic=data["mechanic"],
                supervisor=data["supervisor"],
                mileage=data["mileage"],
                next_due=common.convertdmy_to_date2(data["next_due"]),
                rt_regn=data["rt_regn"],
                trailer_regn=data["trailer_regn"],
                created_by=data["created_by"],
                created_date=datetime.datetime.utcnow()
            )
            save_changes(new_adc)
            log_details = {"description": "Adhoc added successfully",
                           "reference_id": new_adc.adhoc_breakdown_id}
            audit_log = AuditLog(
                type='Workshop',
                sub_type='Adhoc',
                details=log_details,
                created_by=new_adc.created_by,
                created_date=datetime.datetime.utcnow()
            )
            save_changes(audit_log)
            adc_item_res = save_inspection_item(data["inspection"],
                                                new_adc.adhoc_breakdown_id,
                                                data["created_by"], 4)
            response_object = {
                "ErrorCode": "9999",
                "Status": "Adhoc added successfully",
                "adhoc_breakdown_id": new_adc.adhoc_breakdown_id,
                "adc_item_res": adc_item_res
            }
        else:
            exists_adc = AdhocBreakdown.query.filter(AdhocBreakdown.isActive == 1,
                                                     AdhocBreakdown.adhoc_breakdown_id == data["adhoc_breakdown_id"]
                                                     ).first()
            if exists_adc:
                exists_adc.date_in = common.convertdmy_to_date2(data["date_in"])
                exists_adc.mechanic = data["mechanic"]
                exists_adc.supervisor = data["supervisor"]
                exists_adc.mileage = data["mileage"]
                exists_adc.next_due = common.convertdmy_to_date2(data["next_due"])
                exists_adc.rt_regn = data["rt_regn"]
                exists_adc.updated_by = data["created_by"]
                exists_adc.updated_date = datetime.datetime.utcnow()
                save_changes(exists_adc)
                adc_item_res = save_inspection_item(data["pdc_inspection"],
                                                    exists_adc.adhoc_breakdown_id,
                                                    data["created_by"], 4)
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Adhoc updated successfully",
                    "adhoc_breakdown_id": exists_adc.adhoc_breakdown_id,
                    "adc_item_res": adc_item_res
                }

            else:
                response_object = {
                    "ErrorCode": "9997",
                    "Status": "PDC not exists",
                    "pdc_registration_id": 0,
                    "pdc_item_res": []
                }

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
#   feat - Used to get the list of adhoc
#
def get_adhoc_list(page, row, searchterm, tabindex, sortindex):
    try:
        adhoc_query = AdhocBreakdown.query.filter_by(isActive=1)

        if searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            adhoc_query = adhoc_query.filter(or_(AdhocBreakdown.type.ilike(search),
                                                 AdhocBreakdown.sub_type.ilike(search)))

        # Sorting functionality
        if tabindex == 1:
            if sortindex == 1:
                adhoc_query = adhoc_query.order_by(asc(AdhocBreakdown.type))
            else:
                adhoc_query = adhoc_query.order_by(desc(AdhocBreakdown.type))
        elif tabindex == 2:
            if sortindex == 1:
                adhoc_query = adhoc_query.order_by(asc(AdhocBreakdown.sub_type))
            else:
                adhoc_query = adhoc_query.order_by(desc(AdhocBreakdown.sub_type))
        else:
            adhoc_query = adhoc_query.order_by(desc(AdhocBreakdown.audit_log_id))

        adhoc_data = adhoc_query.paginate(int(page), int(row), False).items
        count = adhoc_query.count()

        if adhoc_data:
            response_object = {
                "data": adhoc_data,
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
#   feat - Used to get the adhoc using the given id
#
def get_by_id(adhoc_breakdown_id):
    try:
        adhoc_breakdown = AdhocBreakdown.query.filter_by(isActive=1, adhoc_breakdown_id=adhoc_breakdown_id).first()
        return adhoc_breakdown, 200

    except Exception as e:

        logging.exception(e)
        return {}, 201


#
#   feat - Used to delete the adhoc
#
def delete_adhoc(data):
    try:
        adhoc = AdhocBreakdown.query.filter_by(isActive=1,
                                               adhoc_breakdown_id=data["adhoc_breakdown_id"]).first()

        if adhoc:
            adhoc.isActive = "0"
            adhoc.updated_by = data["userid"]
            adhoc.updated_date = datetime.datetime.utcnow()

            save_changes(adhoc)

            response_object = {
                "ErrorCode": "9999",
                "Status": "adhoc delete successfully"
            }

        else:
            response_object = {
                "ErrorCode": "9997",
                "Status": "adhoc not exists"
            }
        return response_object, 201

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "adhoc delete failed"
        }

        return response_object, 201


#
#   feat - Used to add/update the schedule maintenance
#
def save_schedule_maintenance(data):
    try:
        if data["scheduled_maintenance_id"] == 0:
            new_sch = ScheduledMaintenance(
                date_in=common.convertdmy_to_date2(data["date_in"]),
                mechanic=data["mechanic"],
                supervisor=data["supervisor"],
                mileage=data["mileage"],
                next_due=common.convertdmy_to_date2(data["next_due"]),
                rt_regn=data["rt_regn"],
                trailer_regn=data["trailer_regn"],
                created_by=data["created_by"],
                created_date=datetime.datetime.utcnow()
            )
            save_changes(new_sch)
            log_details = {"description": "Scheduled Maintenance added successfully",
                           "reference_id": new_sch.scheduled_maintenance_id}
            audit_log = AuditLog(
                type='Workshop',
                sub_type='ScheduledMaintenance',
                details=log_details,
                created_by=new_sch.created_by,
                created_date=datetime.datetime.utcnow()
            )
            save_changes(audit_log)
            sch_item_res = save_inspection_item(data["inspection"],
                                                new_sch.scheduled_maintenance_id,
                                                data["created_by"], 3)
            response_object = {
                "ErrorCode": "9999",
                "Status": "Scheduled Maintenance added successfully",
                "scheduled_maintenance_id": new_sch.scheduled_maintenance_id,
                "sch_item_res": sch_item_res
            }
        else:
            exists_sch = ScheduledMaintenance.query.filter(ScheduledMaintenance.isActive == 1,
                                                           ScheduledMaintenance.scheduled_maintenance_id == data[
                                                               "scheduled_maintenance_id"]
                                                           ).first()
            if exists_sch:
                exists_sch.date_in = common.convertdmy_to_date2(data["date_in"])
                exists_sch.mechanic = data["mechanic"]
                exists_sch.supervisor = data["supervisor"]
                exists_sch.mileage = data["mileage"]
                exists_sch.next_due = common.convertdmy_to_date2(data["next_due"])
                exists_sch.rt_regn = data["rt_regn"]
                exists_sch.updated_by = data["created_by"]
                exists_sch.updated_date = datetime.datetime.utcnow()
                save_changes(exists_sch)
                sch_item_res = save_inspection_item(data["inspection"],
                                                    exists_sch.scheduled_maintenance_id,
                                                    data["created_by"], 3)
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Scheduled Maintenance updated successfully",
                    "scheduled_maintenance_id": exists_sch.scheduled_maintenance_id,
                    "sch_item_res": sch_item_res
                }

            else:
                response_object = {
                    "ErrorCode": "9997",
                    "Status": "Scheduled Maintenance not exists",
                    "scheduled_maintenance_id": 0,
                    "sch_item_res": []
                }

        return response_object

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Scheduled Maintenance save failed",
            "sch_item_res": [],
            "Error": str(e)
        }

        return response_object


def get_dashboard_daily_downtime(page,row,date_in,date_out,search):
    try:
        # start_date = datetime.date.today() - datetime.timedelta(days=3)       func.date(InspectionItem.created_date) == start_date),

        rkp_sub_query = db.session.query(User.first_name).filter(PDCRegistration.created_by == User.id).label("rkp")
        mentor_sub_query = db.session.query(User.first_name).filter(PDCRegistration.approved_by == User.id).label("mentor")
        down_query = db.session.query(PDCRegistration, InspectionItem, Checklist, Vehicle, rkp_sub_query, mentor_sub_query) \
            .join(InspectionItem, and_(PDCRegistration.pdc_registration_id == InspectionItem.reference_id)) \
            .outerjoin(Checklist, and_(Checklist.checklist_id == InspectionItem.checklist_id)) \
            .outerjoin(Vehicle, and_(Vehicle.id == PDCRegistration.vehicle_id)) \
            .filter(and_(PDCRegistration.isActive == 1, InspectionItem.isActive == 1),
                    or_(and_(InspectionItem.inspection_type == 1, InspectionItem.inspection_status == 2),
                        InspectionItem.inspection_type > 1)
                    )

        if ( date_in != "" and date_in != "\"\"" ) and ( date_in != "" and date_in != "\"\"" ):
            down_query = down_query.filter(and_(InspectionItem.date_in >= date_in, InspectionItem.date_out <= date_out))
        elif ( date_in != "" and date_in != "\"\"" ):
            date_in = common.convertdmy_to_date2(date_in)
            down_query = down_query.filter(InspectionItem.date_in == date_in )
        elif date_in != "" and date_in != "\"\"":
            date_out = common.convertdmy_to_date2(date_out)
            down_query = down_query.filter(InspectionItem.date_in == date_out)

        if search != "" and search != "\"\"":
            search = "%{}%".format(search)
            down_query = down_query.filter(or_(Vehicle.regn_no.ilike(search), Checklist.item_description.ilike(search), InspectionItem.findings.ilike(search),
                                               case(
                                                   [
                                                       (
                                                           InspectionItem.inspection_type == 1,
                                                           literal_column("'PDC'")
                                                       ),
                                                       (
                                                           InspectionItem.inspection_type == 2,
                                                           literal_column("'PJC'")
                                                       ),
                                                       (
                                                           InspectionItem.inspection_type == 3,
                                                           literal_column("'SCHEDULED MAINTENANCE'")
                                                       ),
                                                       (
                                                           InspectionItem.inspection_type == 4,
                                                           literal_column("'AD HOC'")
                                                       ),
                                                       (
                                                           InspectionItem.inspection_type == 5,
                                                           literal_column("'BREAKDOWN'")
                                                       )
                                                   ]
                                               ).ilike(search)
                                               ))

        count = down_query.count()
        down_query = down_query.order_by(desc(PDCRegistration.pdc_registration_id)).paginate(int(page), int(row), False).items

        down_list = []
        if down_query:
            for dt in down_query:
                data_obj = {
                    "date_in": "" if dt.InspectionItem.date_in == '' or dt.InspectionItem.date_in is None else dt.InspectionItem.date_in.strftime(
                        '%d-%m-%Y'),
                    "date_in_time_out": "" if dt.InspectionItem.date_in == '' or dt.InspectionItem.date_in is None else dt.InspectionItem.date_in.strftime(
                        '%d-%m-%Y %H:%M:%S'),
                    "date_out": "" if dt.InspectionItem.date_out == '' or dt.InspectionItem.date_in is None else dt.InspectionItem.date_out.strftime(
                        '%d-%m-%Y'),
                    "date_out_time_out": "" if dt.InspectionItem.date_in == '' or dt.InspectionItem.date_in is None else dt.InspectionItem.date_in.strftime(
                        '%d-%m-%Y %H:%M:%S'),
                    "mileage": "",
                    "inspection_type": dt.PDCRegistration.inspection_type,
                    "repair_status_id": dt.PDCRegistration.pdc_registration_id,
                    "workshop_status": str(dt.InspectionItem.workshop_status),
                    "rkp": dt.rkp,
                    "mentor": dt.mentor,
                    "mechanic": dt.PDCRegistration.mechanic if dt.PDCRegistration.mechanic else "",
                    "supervisor": dt.PDCRegistration.supervisor if dt.PDCRegistration.supervisor else ""
                }


                if dt.PDCRegistration.inspection_type == 5:
                    data_obj["maint"]= "BREAKDOWN"
                elif dt.PDCRegistration.inspection_type == 4:
                    data_obj["maint"]= "AD HOC"
                elif dt.PDCRegistration.inspection_type == 3:
                    data_obj["maint"]= "SCHEDULED MAINTENANCE"
                elif dt.PDCRegistration.inspection_type == 2:
                    data_obj["maint"]= "PJC"
                elif dt.PDCRegistration.inspection_type == 1:
                    data_obj["maint"]= "PDC"
                else:
                    data_obj["maint"] = ""


                if dt.InspectionItem.inspection_type <= 2:
                    data_obj["rt_issue"] = dt.Checklist.item_description
                    data_obj["remarks"] = dt.InspectionItem.findings
                    data_obj["rt_no"] = dt.Vehicle.regn_no

                if dt.InspectionItem.inspection_type > 2:
                    data_obj["rt_issue"] = dt.InspectionItem.inspections_defects
                    data_obj["remarks"] = dt.InspectionItem.technician_remarks
                    data_obj["rt_no"] = dt.PDCRegistration.rt_regn

                down_list.append(data_obj)
            response_object = {
                "ErrorCode": "9999",
                "data": down_list,
                "count":count
            }
        else:
            response_object = {
                "ErrorCode": "9997",
                "data": [],
                "count": 0
            }
        return response_object
    except Exception as e:
        logging.exception(e)
        response_object = {
            "ErrorCode": "0000",
            "data": [],
            "count": 0,
            "Error": str(e)
        }

        return response_object


def get_pdc_defects_list(page, row, search, date_in_search, date_out_search, reference_id):
    try:
        lst = []
        rkp_sub_query = db.session.query(User.first_name).filter(PDCRegistration.created_by == User.id).label("rkp")
        mentor_sub_query = db.session.query(User.first_name).filter(PDCRegistration.approved_by == User.id).label("mentor")
        pdc_defect_list = db.session.query(PDCRegistration, InspectionItem, Checklist, Vehicle, rkp_sub_query, mentor_sub_query) \
            .join(InspectionItem, and_(PDCRegistration.pdc_registration_id == InspectionItem.reference_id)) \
            .join(Checklist, and_(InspectionItem.checklist_id == Checklist.checklist_id)) \
            .join(Vehicle, and_(PDCRegistration.vehicle_id == Vehicle.id))

        if reference_id!=0:
            pdc_defect_list = pdc_defect_list.filter(InspectionItem.reference_id == reference_id)
        else:
            pdc_defect_list = pdc_defect_list.filter(
                PDCRegistration.isActive == 1, InspectionItem.isActive == 1, InspectionItem.inspection_type == 1, PDCRegistration.approval_status == 2,
                InspectionItem.inspection_status == 2, func.coalesce(InspectionItem.workshop_status, 0) != 2
                # or_( InspectionItem.InspectionItem == None, InspectionItem.workshop_status == 1 )
            )

        if search != '' and search != "\"\"":
            search = "%{}%".format(search)
            pdc_defect_list = pdc_defect_list.filter(or_(Vehicle.regn_no.ilike(search), Checklist.item_description.ilike(search)))

        if date_in_search != '' and date_in_search != "\"\"":
            pdc_defect_list = pdc_defect_list.filter(
                func.date(InspectionItem.date_in) == common.convertdmy_to_date2(date_in_search).date())

        if date_out_search != '' and date_out_search != "\"\"":
            pdc_defect_list = pdc_defect_list.filter(
                func.date(InspectionItem.date_out) == common.convertdmy_to_date2(date_out_search).date())

        pdc_pjc_total_count = pdc_defect_list.count()
        pdc_defect_list = pdc_defect_list.order_by(desc(InspectionItem.created_date)).paginate(int(page), int(row),
                                                                                               False).items

        if pdc_defect_list:

            for pdc_list in pdc_defect_list:
                data = {}
                data['inspection_id'] = pdc_list.InspectionItem.inspection_id
                data['pdc_reference_id'] = pdc_list.InspectionItem.reference_id
                data['inspection'] = pdc_list.Checklist.item_description
                data[
                    'date_in'] = "" if pdc_list.InspectionItem.date_in == '' or pdc_list.InspectionItem.date_in is None else pdc_list.InspectionItem.date_in.strftime(
                    '%d-%m-%Y %H:%M:%S')
                data[
                    'date_out'] = "" if pdc_list.InspectionItem.date_out == '' or pdc_list.InspectionItem.date_out is None else pdc_list.InspectionItem.date_out.strftime(
                    '%d-%m-%Y %H:%M:%S')
                data['approval_category'] = "0" if pdc_list.InspectionItem.approval_category == '' or pdc_list.InspectionItem.approval_category == None else str(pdc_list.InspectionItem.approval_category)
                data['inspection_status'] = float(pdc_list.InspectionItem.inspection_status)
                data['inspections_defects'] = "" if pdc_list.InspectionItem.inspections_defects == None else pdc_list.InspectionItem.inspections_defects
                data['regn_no'] = pdc_list.Vehicle.regn_no
                data['rkp'] = pdc_list.rkp
                data['mentor'] = pdc_list.mentor
                data['workshop_action'] = "" if pdc_list.InspectionItem.technician_remarks == None else pdc_list.InspectionItem.technician_remarks
                data['workshop_status'] = "1" if pdc_list.InspectionItem.workshop_status == '' or pdc_list.InspectionItem.workshop_status == None else str(int(pdc_list.InspectionItem.workshop_status))
                data['mechanic'] = pdc_list.InspectionItem.mechanic if pdc_list.InspectionItem.mechanic else ""
                data['supervisor'] = pdc_list.InspectionItem.supervisor if pdc_list.InspectionItem.supervisor else ""
                lst.append(data)

        response_object = {
            "ErrorCode": "9999",
            "count": pdc_pjc_total_count,
            "data": lst,
        }

        return response_object, 200

    except Exception as e:

        logging.exception(e)
        response_object = {
            "ErrorCode": "0000",
            "data": [],
            "Error": str(e)
        }
        return response_object


def get_pdc_defects_by_id(id):
    try:
        lst = []
        rkp_sub_query = db.session.query(User.first_name).filter(PDCRegistration.created_by == User.id).label("rkp")
        mentor_sub_query = db.session.query(User.first_name).filter(PDCRegistration.approved_by == User.id).label("mentor")
        pdc_defect_list = db.session.query(PDCRegistration, InspectionItem, Checklist, Vehicle, rkp_sub_query, mentor_sub_query) \
            .join(InspectionItem, and_(PDCRegistration.pdc_registration_id == InspectionItem.reference_id)) \
            .join(Checklist, and_(InspectionItem.checklist_id == Checklist.checklist_id)) \
            .join(Vehicle, and_(PDCRegistration.vehicle_id == Vehicle.id))

        pdc_pjc_total_count = pdc_defect_list.count()
        pdc_defect_list = pdc_defect_list.filter(InspectionItem.reference_id == id).all()

        if pdc_defect_list:

            for pdc_list in pdc_defect_list:
                data = {}
                data['inspection_id'] = pdc_list.InspectionItem.inspection_id
                data['pdc_reference_id'] = pdc_list.InspectionItem.reference_id
                data['inspection'] = pdc_list.Checklist.item_description
                data[
                    'date_in'] = "" if pdc_list.InspectionItem.date_in == '' or pdc_list.InspectionItem.date_in is None else pdc_list.InspectionItem.date_in.strftime(
                    '%d-%m-%Y %H:%M:%S')
                data[
                    'date_out'] = "" if pdc_list.InspectionItem.date_out == '' or pdc_list.InspectionItem.date_out is None else pdc_list.InspectionItem.date_out.strftime(
                    '%d-%m-%Y %H:%M:%S')
                data['approval_category'] = "0" if pdc_list.InspectionItem.approval_category == '' or pdc_list.InspectionItem.approval_category == None else str(pdc_list.InspectionItem.approval_category)
                data['inspection_status'] = float(pdc_list.InspectionItem.inspection_status)
                data['inspections_defects'] = "" if pdc_list.InspectionItem.inspections_defects == None else pdc_list.InspectionItem.inspections_defects
                data['regn_no'] = pdc_list.Vehicle.regn_no
                data['rkp'] = pdc_list.rkp
                data['mentor'] = pdc_list.mentor
                data['workshop_action'] = "" if pdc_list.InspectionItem.technician_remarks == None else pdc_list.InspectionItem.technician_remarks
                data['workshop_status'] = "1" if pdc_list.InspectionItem.workshop_status == '' or pdc_list.InspectionItem.workshop_status == None else str(int(pdc_list.InspectionItem.workshop_status))
                data['mechanic'] = pdc_list.InspectionItem.mechanic if pdc_list.InspectionItem.mechanic else ""
                data['supervisor'] = pdc_list.InspectionItem.supervisor if pdc_list.InspectionItem.supervisor else ""
                lst.append(data)

        response_object = {
            "ErrorCode": "9999",
            "count": pdc_pjc_total_count,
            "data": lst,
        }

        return response_object, 200

    except Exception as e:

        logging.exception(e)
        response_object = {
            "ErrorCode": "0000",
            "data": [],
            "Error": str(e)
        }
        return response_object



def repair_status_save(data):
    try:
        if data["repair_status_id"] == 0:
            new_repair_status = PDCRegistration(
                date_in=datetime.datetime.utcnow() if data["date_in"] == '' else common.convertdmy_to_date2(data["date_in"]),
                date_out=datetime.datetime.utcnow() if data["date_out"] == '' else common.convertdmy_to_date2(data["date_out"]),
                mechanic=data["mechanic"],
                supervisor=data["supervisor"],
                mileage=data["mileage"],
                next_due=data["next_due"],
                rt_regn=data["rt_regn"],
                trailer_regn=data["trailer_regn"],
                created_by=data["created_by"],
                created_date=datetime.datetime.utcnow(),
                brake_lining_pad_thickness_pm=data['brake_lining_pad_thickness_pm'],
                brake_lining_pad_thickness_trailer=data['brake_lining_pad_thickness_trailer'],
                clutch_Details_info=data['clutch_Details_info'],
                repair_overhaul=data["repair_overhaul"],
                welding_shop=data["welding_shop"],
                tyre_shop=data["tyre_shop"],
                inspection_type=data['repair_status_type'],
                completed_status=0,
            )

            save_changes(new_repair_status)
            log_details = {"description": "Repair Status added successfully",
                           "reference_id": new_repair_status.pdc_registration_id}
            audit_log = AuditLog(
                type='Workshop',
                sub_type='Repair Status',
                details=log_details,
                created_by=new_repair_status.created_by,
                created_date=datetime.datetime.utcnow()
            )
            save_changes(audit_log)
            repair_item_res = save_repair_status_item(data["inspection"],
                                                      new_repair_status.pdc_registration_id,
                                                      data["created_by"], data['repair_status_type'], data["date_in"], data["date_out"])
            response_object = {
                "ErrorCode": "9999",
                "Status": "Repair Status successfully",
                "repair_status_id": new_repair_status.pdc_registration_id,
                "repair_item_res": repair_item_res
            }
        else:
            exists_adc = PDCRegistration.query.filter(PDCRegistration.isActive == 1,
                                                      PDCRegistration.pdc_registration_id == data["repair_status_id"]
                                                      ).first()
            if exists_adc:
                exists_adc.date_in = datetime.datetime.utcnow() if data["date_in"] == '' else common.convertdmy_to_date2(data["date_in"]),
                exists_adc.date_out = datetime.datetime.utcnow() if data["date_out"] == '' else common.convertdmy_to_date2(data["date_out"])
                exists_adc.mechanic = data["mechanic"]
                exists_adc.supervisor = data["supervisor"]
                exists_adc.mileage = data["mileage"]
                exists_adc.next_due = data["next_due"]
                exists_adc.rt_regn = data["rt_regn"]
                exists_adc.updated_by = data["created_by"]
                exists_adc.updated_date = datetime.datetime.utcnow()
                exists_adc.brake_lining_pad_thickness_pm = data['brake_lining_pad_thickness_pm'],
                exists_adc.brake_lining_pad_thickness_trailer = data['brake_lining_pad_thickness_trailer'],
                exists_adc.clutch_Details_info = data['clutch_Details_info'],
                exists_adc.repair_overhaul = data["repair_overhaul"],
                exists_adc.welding_shop = data["welding_shop"],
                exists_adc.tyre_shop = data["tyre_shop"],
                exists_adc.inspection_type = data['repair_status_type'],
                exists_adc.completed_status = 0,

                save_changes(exists_adc)
                repair_item_res = save_repair_status_item(data["inspection"], exists_adc.pdc_registration_id, data["created_by"],
                                                            data['repair_status_type'], data["date_in"], data["date_out"])
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Repair Status updated successfully",
                    "repair_status_id": exists_adc.pdc_registration_id,
                    "repair_item_res": repair_item_res
                }

            else:
                response_object = {
                    "ErrorCode": "9997",
                    "Status": "Repair Status not exists",
                    "repair_status_id": 0,
                    "repair_item_res": []
                }

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


def save_repair_status_item(full_data, reference_id, created_by, inspection_type, date_in, date_out):
    pdc_item_res = []
    try:
        for data in full_data:
            item = InspectionItem.query.filter(InspectionItem.isActive == 1,
                                               InspectionItem.inspection_id == data["inspection_id"]
                                               ).first()
            if item:
                item.inspection_type = inspection_type,
                item.inspections_defects = data["inspections_defects"],
                item.technician_remarks = data["technician_remarks"],
                item.workshop_status = data["workshop_status"],
                item.updated_by = created_by,
                item.updated_date = datetime.datetime.utcnow()
                if date_in != '':
                    item.date_in = common.convertdmy_to_date2(date_in),
                if date_out != '':
                    item.date_out = common.convertdmy_to_date2(date_out),

                save_changes(item)
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Repair Status Item Added successfully",
                    "inspection_id": item.reference_id
                }
            else:
                new_item = InspectionItem(
                    reference_id=reference_id,
                    inspection_type=inspection_type,
                    inspections_defects=data["inspections_defects"],
                    technician_remarks=data["technician_remarks"],
                    workshop_status=data["workshop_status"],
                    created_by=created_by,
                    created_date=datetime.datetime.utcnow()
                )
                if date_in != '':
                    new_item.date_in = common.convertdmy_to_date2(date_in),
                if date_out != '':
                    new_item.date_out = common.convertdmy_to_date2(date_out),

                save_changes(new_item)
                response_object = {
                    "ErrorCode": "9999",
                    "Status": "Repair Status Item Added successfully",
                    "inspection_id": new_item.reference_id
                }

            pdc_item_res.append(response_object)

        wp_count = InspectionItem.query.filter(InspectionItem.isActive == 1,
                                               InspectionItem.reference_id == reference_id,
                                               InspectionItem.workshop_status == 2).count()
        if wp_count == 0:
            reg_pdc = PDCRegistration.query.filter(PDCRegistration.isActive == 1,
                                                   PDCRegistration.pdc_registration_id == reference_id).first()

            if reg_pdc:
                reg_pdc.completed_status = 1
                # reg_pdc.approval_status = 2
                save_changes(reg_pdc)

        return pdc_item_res

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "Repair Status Item save failed",
            "Error": str(e)
        }
        pdc_item_res.append(response_object)
        return pdc_item_res


def get_repair_status_by_headId(head_id):
    try:

        repair_status = PDCRegistration.query.join(InspectionItem,
                                                   PDCRegistration.pdc_registration_id == InspectionItem.reference_id).add_columns(
            InspectionItem.inspection_id, InspectionItem.inspection_type, InspectionItem.inspections_defects,
            InspectionItem.technician_remarks, InspectionItem.workshop_status).filter(
            PDCRegistration.pdc_registration_id == head_id).all()
        data = {}
        if repair_status:

            data['date_in'] = "" if repair_status[0].PDCRegistration.date_in == '' or repair_status[
                0].PDCRegistration.date_in == None else repair_status[0].PDCRegistration.date_in.strftime('%d-%m-%Y')
            data['date_out'] = "" if repair_status[0].PDCRegistration.date_out == '' or repair_status[
                0].PDCRegistration.date_out == None else repair_status[0].PDCRegistration.date_out.strftime('%d-%m-%Y')
            data['mechanic'] = repair_status[0].PDCRegistration.mechanic
            data['supervisor'] = repair_status[0].PDCRegistration.supervisor
            data['mileage'] = repair_status[0].PDCRegistration.mileage
            data['next_due'] = repair_status[0].PDCRegistration.next_due
            data['rt_regn'] = repair_status[0].PDCRegistration.rt_regn
            data['trailer_regn'] = repair_status[0].PDCRegistration.trailer_regn
            data['created_by'] = repair_status[0].PDCRegistration.created_by
            data['brake_lining_pad_thickness_pm'] = repair_status[0].PDCRegistration.brake_lining_pad_thickness_pm
            data['brake_lining_pad_thickness_trailer'] = repair_status[
                0].PDCRegistration.brake_lining_pad_thickness_trailer
            data['clutch_Details_info'] = repair_status[0].PDCRegistration.clutch_Details_info
            data['repair_status_id'] = repair_status[0].PDCRegistration.pdc_registration_id
            data['remarks'] = repair_status[0].PDCRegistration.remarks

            data["repair_overhaul"] = repair_status[0].PDCRegistration.repair_overhaul
            data["welding_shop"] = repair_status[0].PDCRegistration.welding_shop
            data["tyre_shop"] = repair_status[0].PDCRegistration.tyre_shop

            inspection_list = []
            for status in repair_status:
                inspection = {}
                inspection['inspection_id'] = status.inspection_id
                inspection['inspections_defects'] = status.inspections_defects
                inspection['technician_remarks'] = status.technician_remarks
                inspection['workshop_status'] = str(
                    status.workshop_status) if status.workshop_status != None or status.workshop_status != '' else ""

                inspection_list.append(inspection)

            data['inspection_list'] = inspection_list

        response_object = {
            "data": data,
            "ErrorCode": "9999"
        }

        return response_object, 200

    except Exception as e:

        logging.exception(e)
        response_object = {
            "ErrorCode": "0000",
            "data": {},
            "Error": str(e)
        }
        return response_object


def update_pdc_defects(pdc_data):
    try:

        for data in pdc_data['inspection_defects']:
            item = InspectionItem.query.filter(InspectionItem.isActive == 1,
                                               InspectionItem.inspection_id == data["inspection_id"]
                                               ).first()
            if item:
                item.technician_remarks = data["workshop_action"],
                item.approval_category = data["approval_category"],
                item.workshop_status = data["workshop_status"],
                item.supervisor = data["supervisor"],
                item.mechanic = data["mechanic"],
                item.updated_by = pdc_data["updated_by"],
                item.updated_date = datetime.datetime.utcnow()
                if data["date_in"] != "":
                    item.date_in = datetime.datetime.strptime(data["date_in"], "%d-%m-%Y %H:%M:%S")
                if data["date_out"] != "":
                    item.date_out = datetime.datetime.strptime(data["date_out"], "%d-%m-%Y %H:%M:%S")

                save_changes(item)

        response_object = {
            "ErrorCode": "9999",
            "Status": "PDC Defects Updated Sucessfully"
        }
        return response_object

    except Exception as e:
        logging.exception(e)
        response_object = {
            "ErrorCode": "0000",
            "Error": str(e)
        }
        return response_object


def upload_excel(file, file_date, user_id, report_type):
    try:
        report_date_obj = common.convertdmy_to_date2(file_date)
        if file:
            org_filename = secure_filename(file.filename)
            ext = org_filename.split('.')[1]
            uuid_file = str(uuid.uuid4())
            uuid_filename = uuid_file + "." + ext
            directory = os.path.join(config.ReportUploadFilePath)
            if not os.path.exists(directory):
                os.makedirs(directory)
            full_path = os.path.join(config.ReportUploadFilePath, uuid_filename)
            file.save(full_path)

            rpt = ReportTracker(
                isActive=1,
                report_date=report_date_obj,
                status=0,
                uuid_filename=uuid_filename,
                full_path=full_path,
                created_by=user_id,
                created_date=datetime.datetime.utcnow(),
                report_type=report_type
            )
            save_changes(rpt)
            service_path, run_dir = '', ''
            if report_type == 1:
                service_path = os.path.abspath(os.path.dirname("jobs/workshop_parts/")) + "/service.py"
                run_dir = os.path.abspath(os.path.dirname("jobs/workshop_parts/"))
            elif report_type == 2:
                service_path = os.path.abspath(os.path.dirname("jobs/workshop_purchase/")) + "/service.py"
                run_dir = os.path.abspath(os.path.dirname("jobs/workshop_purchase/"))
            elif report_type == 4:
                service_path = os.path.abspath(os.path.dirname("jobs/workshop_expense/")) + "/service.py"
                run_dir = os.path.abspath(os.path.dirname("jobs/workshop_expense/"))
            # here require to generate report...
            # logging.info("Starting thread")
            # thr = Thread(target=process_report, args=[report_date, user_id])
            # thr.start()
            # logging.info("Thread Started")
            logging.exception("Processing report Generation")

            logging.exception("running :" + service_path)
            #########################################################
            # Starting the process in background
            ##################################################################
            if os.name == 'nt':
                subprocess.run(
                    [config.Python_Version, service_path])
            else:
                subprocess.Popen(
                    ['nohup', config.Python_Version,
                     service_path],
                    stdout=open('jobs.log', 'a'),
                    stderr=open('logfile.log', 'a'),
                    cwd=run_dir,
                    preexec_fn=os.setpgrp)
            logging.exception("sub process started.")
            ##################################################################
            #########################################################

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
        logging.exception(str(e))
        response_obj = {
            "ErrorCode": "0000",
            "uuid_filename": "",
            "org_filename": ""
        }
    return response_obj


#
#   Get the report Status
#
def get_report_status(report_type, report_date, user_id):
    try:
        report_date_obj = common.convertdmy_to_date2(report_date)
        rpt = ReportTracker.query.filter_by(isActive=1, report_date=report_date_obj, report_type=report_type). \
            order_by(asc(ReportTracker.status), desc(ReportTracker.report_id)).first()
        if rpt:
            response_object = {
                "ErrorCode": "9999",
                "status": rpt.status
            }
        else:
            response_object = {
                "ErrorCode": "9997",
                "status": 4
            }
        return response_object, 200

    except Exception as e:

        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "status": 4
        }

        return response_object, 200


#
#   Used to get the PARTS DELIVERED TO RESPECTIVE BRANCHES FOR THE YEAR
#
def get_parts_report(user_id, report_date):
    try:
        report_date_obj = common.convertdmy_to_date2(report_date)
        branch_data = Branch.query.filter_by(isactive=1).order_by(asc(Branch.id)).all()
        branch_list = []
        for branch in branch_data:
            branch_list.append({
                "id": branch.id,
                "branch_name": branch.branch_name
            })
        branch_sub_query = db.session.query(Branch.branch_name).select_from(Branch). \
            filter(Branch.id == ReportBranchParts.branch_id).label("branch_name")
        parts_query = (db.session.query(ReportBranchParts, branch_sub_query)
            .select_from(ReportBranchParts)
            .filter(
            extract('year', ReportBranchParts.report_date) == report_date_obj.year,
            ReportBranchParts.isActive == 1
        ))
        parts_data = parts_query.order_by(asc(ReportBranchParts.report_date),
                                          asc(ReportBranchParts.branch_id)).all()
        parts_list = []
        for data in parts_data:
            parts_list.append({
                "report_year": data.ReportBranchParts.report_date.strftime("%Y"),
                "report_month": data.ReportBranchParts.report_date.strftime("%m"),
                "branch_id": data.ReportBranchParts.branch_id,
                "branch_name": data.branch_name,
                "payment_delivered": str(data.ReportBranchParts.payment_delivered),
                "payment_sale": str(data.ReportBranchParts.payment_sale)
            })

        response_object = {
            "ErrorCode": "9999",
            "data": parts_list,
            "count": len(parts_list),
            "branch": branch_list
        }
        return response_object, 200

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "data": [],
            "error": str(e),
            "branch": []
        }
        return response_object, 201


#
#   Used to get the PARTS summary report
#
def get_parts_report_summary(user_id, report_year):
    try:
        branch_data = Branch.query.filter_by(isactive=1).order_by(asc(Branch.id)).all()
        branch_list = []
        for branch in branch_data:
            branch_list.append({
                "id": branch.id,
                "branch_name": branch.branch_name
            })
        branch_sub_query = db.session.query(Branch.branch_name).select_from(Branch). \
            filter(Branch.id == ReportBranchPartsSummary.branch_id).label("branch_name")
        parts_query = (db.session.query(ReportBranchPartsSummary, branch_sub_query)
            .select_from(ReportBranchPartsSummary)
            .filter(
            extract('year', ReportBranchPartsSummary.report_date) == report_year,
            ReportBranchPartsSummary.isActive == 1
        ))
        parts_data = parts_query.order_by(asc(ReportBranchPartsSummary.report_date),
                                          asc(ReportBranchPartsSummary.branch_id)).all()
        parts_list = []
        for data in parts_data:
            parts_list.append({
                "branch_type": str(data.ReportBranchPartsSummary.branch_type),
                "description": data.ReportBranchPartsSummary.description,
                "branch_id": data.ReportBranchPartsSummary.branch_id,
                "branch_name": data.branch_name,
                "payment": str(data.ReportBranchPartsSummary.payment)
            })

        response_object = {
            "ErrorCode": "9999",
            "data": parts_list,
            "count": len(parts_list),
            "branch": branch_list
        }
        return response_object, 200

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "data": [],
            "error": str(e),
            "branch": []
        }
        return response_object, 201


#
#   Used to get the purchase report for the particular year
#
def get_purchase_report(user_id, report_date):
    try:
        report_date_obj = common.convertdmy_to_date2(report_date)
        supplier_data = Supplier.query.filter_by(isactive=1).order_by(asc(Supplier.id)).all()
        supplier_list = []
        for supplier in supplier_data:
            supplier_list.append({
                "id": supplier.id,
                "supplier_name": supplier.supplier_name
            })
        supplier_sub_query = db.session.query(Supplier.supplier_name).select_from(Supplier). \
            filter(Supplier.id == ReportWorkshopPurchase.supplier_id).label("supplier_name")
        purchase_query = (db.session.query(ReportWorkshopPurchase, supplier_sub_query)
            .select_from(ReportWorkshopPurchase)
            .filter(
            extract('year', ReportWorkshopPurchase.report_date) == report_date_obj.year,
            ReportWorkshopPurchase.isActive == 1
        ))
        purchase_data = purchase_query.order_by(asc(ReportWorkshopPurchase.supplier_id),
                                                asc(ReportWorkshopPurchase.report_date)
                                                ).all()
        purchase_list = []
        for data in purchase_data:
            purchase_list.append({
                "report_year": data.ReportWorkshopPurchase.report_date.strftime("%Y"),
                "report_month": data.ReportWorkshopPurchase.report_date.strftime("%m"),
                "supplier_id": data.ReportWorkshopPurchase.supplier_id,
                "supplier_name": data.supplier_name,
                "report_id": str(data.ReportWorkshopPurchase.report_id),
                "payment": str(data.ReportWorkshopPurchase.payment)
            })

        response_object = {
            "ErrorCode": "9999",
            "data": purchase_list,
            "count": len(purchase_list),
            "supplier": supplier_list
        }
        return response_object, 200

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "data": [],
            "error": str(e),
            "supplier": []
        }
        return response_object, 201


#
#   Used to get the expense report
#
def get_expense_report(user_id, report_date):
    try:
        report_date_obj = common.convertdmy_to_date2(report_date)
        expense_query = (db.session.query(ReportExpense)
                         .select_from(ReportExpense)
                         .filter(ReportExpense.report_date == report_date_obj,
                                 ReportExpense.isActive == 1
                                 ))
        expense_data = expense_query.order_by(asc(ReportExpense.report_id)).all()
        expense_list = []
        for data in expense_data:
            expense_list.append({
                "repair_cost": str(data.repair_cost),
                "rt_regn": data.rt_regn,
                "new_tyre": str(data.new_tyre),
                "recamic_tyre": str(data.recamic_tyre),
                "battery": str(data.battery),
                "lube": str(data.lube),
                "spare_battery_lube": str(data.spare_battery_lube),
                "total_from_irs": str(data.total_from_irs),
                "remarks": str(data.remarks)
            })

        response_object = {
            "ErrorCode": "9999",
            "data": expense_list,
            "count": len(expense_list)
        }
        return response_object, 200

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "data": [],
            "error": str(e)
        }
        return response_object, 201


#
#   Used to get the corrective action report
#
def get_corrective_action_report(data):
    try:
        supplier_sub_query = db.session.query(Supplier.supplier_name).select_from(Supplier). \
            filter(Supplier.id == ReportCorrectiveHead.supplier_id).label("supplier_name")

        department_sub_query = db.session.query(Department.department_name).select_from(Department). \
            filter(Department.id == ReportCorrectiveHead.department_id).label("department_name")

        report_query = db.session.query(ReportCorrectiveHead, ReportCorrectiveDetail, supplier_sub_query,
                                        department_sub_query). \
            select_from(ReportCorrectiveHead) \
            .join(ReportCorrectiveDetail, and_(ReportCorrectiveHead.report_id == ReportCorrectiveDetail.head_id)) \
            .filter(and_(ReportCorrectiveHead.isActive == 1, ReportCorrectiveDetail.isActive == 1))
        if data['report_date']:
            report_date_obj = common.convertdmy_to_date2(data['report_date'])
            report_query = report_query.filter(ReportCorrectiveHead.report_date == report_date_obj)
        if data['supplier_id'] > 0:
            report_query = report_query.filter(ReportCorrectiveHead.supplier_id == data['supplier_id'])
        if data['department_id'] > 0:
            report_query = report_query.filter(ReportCorrectiveHead.department_id)
        if data['description'] and data['description'] != '' and data['description'] != "\"\"":
            search = "%{}%".format(data['description'])
            report_query = report_query.filter(
                or_(ReportCorrectiveDetail.description.ilike(search)))

        report_data = report_query.order_by(asc(ReportCorrectiveHead.report_id)).all()
        report_list = []
        for rpt in report_data:
            report_list.append({
                "department_id": data.ReportCorrectiveHead.department_id,
                "supplier_id": data.ReportCorrectiveHead.supplier_id,
                "report_id": data.ReportCorrectiveHead.report_id,
                "car_no": data.ReportCorrectiveHead.car_no,
                "report_date": "" if data.ReportCorrectiveHead.report_date == '' or \
                                     data.ReportCorrectiveHead.report_date is None \
                    else data.ReportCorrectiveHead.report_date.strftime('%d-%m-%Y'),
                "environment": data.ReportCorrectiveHead.environment,
                "health": data.ReportCorrectiveHead.health,
                "safety": data.ReportCorrectiveHead.safety,
                "quality": data.ReportCorrectiveHead.quality,
                "description": data.ReportCorrectiveDetail.description,
                "qty": str(data.ReportCorrectiveDetail.qty),
                "part_no": str(data.ReportCorrectiveDetail.part_no),
                "price": str(data.ReportCorrectiveDetail.price),
                "total": str(data.ReportCorrectiveDetail.total),
                "supplier_name": rpt.supplier_name,
                "department_name": rpt.department_name
            })

        response_object = {
            "ErrorCode": "9999",
            "data": report_list,
            "count": len(report_list)
        }
        return response_object, 200

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "data": [],
            "error": str(e)
        }
        return response_object, 201


def get_dashboard_count():
    try:
        data_count = {}

        adhhov_count = 0
        pdc_count = 0
        pjc_count = 0
        breakdown_count = 0

        category_a_count = InspectionItem.query.filter(InspectionItem.isActive == 1,
                                                       InspectionItem.approval_category == 1).count()
        category_b_count = InspectionItem.query.filter(InspectionItem.isActive == 1,
                                                       InspectionItem.approval_category == 2).count()
        category_c_count = InspectionItem.query.filter(InspectionItem.isActive == 1,
                                                       InspectionItem.approval_category == 3).count()
        category_d_count = InspectionItem.query.filter(InspectionItem.isActive == 1,
                                                       InspectionItem.approval_category == 4).count()

        adhhov_list = PDCRegistration.query.outerjoin(InspectionItem,
                                                      PDCRegistration.pdc_registration_id == InspectionItem.reference_id) \
            .filter(InspectionItem.inspection_type == 4, PDCRegistration.isActive == 1).distinct(
            PDCRegistration.pdc_registration_id).all()

        pdc_list = PDCRegistration.query.outerjoin(InspectionItem,
                                                   PDCRegistration.pdc_registration_id == InspectionItem.reference_id) \
            .filter(InspectionItem.inspection_type == 1, PDCRegistration.isActive == 1).distinct(
            PDCRegistration.pdc_registration_id).all()

        pjc_list = PDCRegistration.query.outerjoin(InspectionItem,
                                                   PDCRegistration.pdc_registration_id == InspectionItem.reference_id) \
            .filter(InspectionItem.inspection_type == 2, PDCRegistration.isActive == 1).distinct(
            PDCRegistration.pdc_registration_id).all()

        breakdown_list = PDCRegistration.query.outerjoin(InspectionItem,
                                                         PDCRegistration.pdc_registration_id == InspectionItem.reference_id) \
            .filter(InspectionItem.inspection_type == 5, PDCRegistration.isActive == 1).distinct(
            PDCRegistration.pdc_registration_id).all()

        adhhov_breakdown_month_count = PDCRegistration.query.outerjoin(InspectionItem,
                                                                       PDCRegistration.pdc_registration_id == InspectionItem.reference_id) \
            .filter(PDCRegistration.isActive == 1,
                    and_(or_(InspectionItem.inspection_type == 5, InspectionItem.inspection_type == 4))).distinct(
            PDCRegistration.pdc_registration_id).count()
        pdc_pjc_month_count = PDCRegistration.query.outerjoin(InspectionItem,
                                                              PDCRegistration.pdc_registration_id == InspectionItem.reference_id) \
            .filter(PDCRegistration.isActive == 1,
                    and_(or_(InspectionItem.inspection_type == 1, InspectionItem.inspection_type == 2))).distinct(
            PDCRegistration.pdc_registration_id).count()

        if adhhov_list:
            for list in adhhov_list:
                wp_count = InspectionItem.query.filter(InspectionItem.isActive == 1,
                                                       InspectionItem.reference_id == list.pdc_registration_id,
                                                       InspectionItem.workshop_status == 1).count()
                if wp_count > 0:
                    adhhov_count = adhhov_count + 1

        if pdc_list:
            for list in pdc_list:
                wp_count = InspectionItem.query.filter(InspectionItem.isActive == 1,
                                                       InspectionItem.reference_id == list.pdc_registration_id,
                                                       InspectionItem.workshop_status == 1).count()
                if wp_count > 0:
                    pdc_count = pdc_count + 1

        if pjc_list:
            for list in pjc_list:
                wp_count = InspectionItem.query.filter(InspectionItem.isActive == 1,
                                                       InspectionItem.reference_id == list.pdc_registration_id,
                                                       InspectionItem.workshop_status == 1).count()
                if wp_count > 0:
                    pjc_count = pjc_count + 1

        if breakdown_list:
            for list in breakdown_list:
                wp_count = InspectionItem.query.filter(InspectionItem.isActive == 1,
                                                       InspectionItem.reference_id == list.pdc_registration_id,
                                                       InspectionItem.workshop_status == 1).count()
                if wp_count > 0:
                    breakdown_count = breakdown_count + 1

        data_count["category_a_count"] = category_a_count
        data_count["category_b_count"] = category_b_count
        data_count["category_c_count"] = category_c_count
        data_count["category_d_count"] = category_d_count

        data_count["adhhov_count"] = adhhov_count
        data_count["pdc_count"] = pdc_count
        data_count["pjc_count"] = pjc_count
        data_count["breakdown_count"] = breakdown_count

        data_count["adhhov_breakdown_month_count"] = adhhov_breakdown_month_count
        data_count["pdc_pjc_month_count"] = pdc_pjc_month_count

        response_object = {
            "ErrorCode": "9999",
            "data": data_count,
        }
        return response_object, 200

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "data": {},
            "error": str(e)
        }
        return response_object, 201


def total_defect_category(date_in, date_out, search):
    try:
        data_count = {}

        data_count["category_a_count"] = 0
        data_count["category_b_count"] = 0
        data_count["category_c_count"] = 0
        data_count["category_d_count"] = 0

        list_query = db.session.query(db.func.count(InspectionItem.approval_category), InspectionItem.approval_category).\
            filter( InspectionItem.isActive == 1, InspectionItem.approval_category != 0, InspectionItem.approval_category.isnot(None))\
            .group_by(InspectionItem.approval_category)

        if (date_in != '' and date_in != "\"\"") and (date_out != '' and date_out != "\"\""):
            list_query = list_query.filter(
                or_(and_(InspectionItem.date_in >= common.convertdmy_to_date2(date_in), InspectionItem.date_in <= common.convertdmy_to_date2(date_out)),
                    and_(InspectionItem.date_out >= common.convertdmy_to_date2(date_in), InspectionItem.date_out <= common.convertdmy_to_date2(date_out)))
            )
        elif date_in != '' and date_in != "\"\"":
            list_query = list_query.filter( InspectionItem.date_in == common.convertdmy_to_date2(date_in) )
        elif date_out != '' and date_out != "\"\"":
            list_query = list_query.filter( InspectionItem.date_out == common.convertdmy_to_date2(date_out) )



        # list_query = db.session.query(PDCRegistration, InspectionItem, User, Vehicle).add_columns(db.func.count(InspectionItem.approval_category), InspectionItem.approval_category) \
        #     .join(InspectionItem, and_(PDCRegistration.pdc_registration_id == InspectionItem.reference_id) ) \
        #     .join(User, and_(User.id == PDCRegistration.user_id) ) \
        #     .join(Vehicle, and_(Vehicle.regn_no == PDCRegistration.rt_regn) ) \
        #     .filter( InspectionItem.isActive == 1, InspectionItem.approval_category != 0, InspectionItem.approval_category.isnot(None),
        #              or_(and_(InspectionItem.date_in >= common.convertdmy_to_date2(date_in), InspectionItem.date_in <= common.convertdmy_to_date2(date_out)),
        #                  and_(InspectionItem.date_out >= common.convertdmy_to_date2(date_in), InspectionItem.date_out <= common.convertdmy_to_date2(date_out)))
        #         ) \
        #     .group_by(InspectionItem.approval_category, InspectionItem.inspection_id, PDCRegistration.pdc_registration_id, User.id, Vehicle.id)

        # search = "%{}%".format(searchterm)

        list_query = list_query.all()

        if list_query:
            for item in list_query:
                if (item.approval_category == 1):
                    data_count["category_a_count"] = item[0]
                elif (item.approval_category == 2):
                    data_count["category_b_count"] = item[0]
                elif (item.approval_category == 3):
                    data_count["category_c_count"] = item[0]
                elif (item.approval_category == 4):
                    data_count["category_d_count"] = item[0]

        response_object = {
            "ErrorCode": "9999",
            "data": data_count,
        }
        return response_object, 200

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "data": {},
            "error": str(e)
        }
        return response_object, 201


def total_repair_count(date_in, date_out, search):
    try:
        data_count = {}

        adhhov_count = PDCRegistration.query.filter(PDCRegistration.isActive == 1, PDCRegistration.inspection_type == 4, PDCRegistration.completed_status == 0)
        pdc_count = PDCRegistration.query.filter(PDCRegistration.isActive == 1, PDCRegistration.inspection_type == 1, PDCRegistration.completed_status == 0)
        pjc_count = PDCRegistration.query.filter(PDCRegistration.isActive == 1, PDCRegistration.inspection_type == 2, PDCRegistration.completed_status == 0)
        breakdown_count = PDCRegistration.query.filter(PDCRegistration.isActive == 1, PDCRegistration.inspection_type == 5, PDCRegistration.completed_status == 0)

        pdc_pjc_month_count = PDCRegistration.query.filter(PDCRegistration.isActive == 1,
                                                           and_(or_(PDCRegistration.inspection_type == 1,
                                                                    PDCRegistration.inspection_type == 2)))

        adhhov_breakdown_month_count = PDCRegistration.query.filter(PDCRegistration.isActive == 1,
                                                                    and_(or_(PDCRegistration.inspection_type == 4,
                                                                             PDCRegistration.inspection_type == 5)))

        schedule_monthly = PDCRegistration.query.filter(PDCRegistration.isActive == 1, PDCRegistration.inspection_type == 3)

        schedule_current = PDCRegistration.query.filter(PDCRegistration.isActive == 1, InspectionItem.inspection_type == 3)             # func.DATE( InspectionItem.created_date ) == day
        schedule_planned = PDCRegistration.query.filter(PDCRegistration.isActive == 1, InspectionItem.inspection_type == 3)

        total_work_open = PDCRegistration.query.filter(PDCRegistration.isActive == 1, PDCRegistration.completed_status == 0)
        total_work_closed = PDCRegistration.query.filter(PDCRegistration.isActive == 1, PDCRegistration.completed_status == 1)

        repair_overhaul_count = PDCRegistration.query.filter(PDCRegistration.isActive == 1, PDCRegistration.repair_overhaul == '1', PDCRegistration.completed_status == 0)
        welding_shop_count = PDCRegistration.query.filter(PDCRegistration.isActive == 1, PDCRegistration.welding_shop == '1', PDCRegistration.completed_status == 0)
        tyre_shop_count = PDCRegistration.query.filter(PDCRegistration.isActive == 1, PDCRegistration.tyre_shop == '1', PDCRegistration.completed_status == 0)


    #Date filter Section
        if (date_in != '' and date_in != "\"\"") and (date_out != '' and date_out != "\"\""):
            date_in = common.convertdmy_to_date2(date_in)
            date_out = common.convertdmy_to_date2(date_out)
            adhhov_count = adhhov_count.filter(
                or_(and_(PDCRegistration.date_in >= date_in, PDCRegistration.date_in <= date_out),
                    and_(PDCRegistration.date_out >= date_in, PDCRegistration.date_out <= date_out))
            )
            pdc_count = pdc_count.filter(
                or_(and_(PDCRegistration.date_in >= date_in, PDCRegistration.date_in <= date_out),
                    and_(PDCRegistration.date_out >= date_in, PDCRegistration.date_out <= date_out))
            )
            pjc_count = pjc_count.filter(
                or_(and_(PDCRegistration.date_in >= date_in, PDCRegistration.date_in <= date_out),
                    and_(PDCRegistration.date_out >= date_in, PDCRegistration.date_out <= date_out))
            )
            breakdown_count = breakdown_count.filter(
                or_(and_(PDCRegistration.date_in >= date_in, PDCRegistration.date_in <= date_out),
                    and_(PDCRegistration.date_out >= date_in, PDCRegistration.date_out <= date_out))
            )
            schedule_current = schedule_current.filter(
                and_(PDCRegistration.created_date >= date_in, PDCRegistration.created_date <= date_out)
            )
            schedule_planned = schedule_planned.filter(
                (PDCRegistration.created_date >= date_out)
            )
            total_work_open = total_work_open.filter(
                PDCRegistration.created_date >= date_in, PDCRegistration.created_date <= date_out
            )
            total_work_closed = total_work_closed.filter(
                PDCRegistration.created_date >= date_in, PDCRegistration.created_date <= date_out
            )
            repair_overhaul_count = repair_overhaul_count.filter(
                PDCRegistration.created_date >= date_in, PDCRegistration.created_date <= date_out
            )
            welding_shop_count = welding_shop_count.filter(
                PDCRegistration.created_date >= date_in, PDCRegistration.created_date <= date_out
            )
            tyre_shop_count = tyre_shop_count.filter(
                PDCRegistration.created_date >= date_in, PDCRegistration.created_date <= date_out
            )
            pdc_pjc_month_count = pdc_pjc_month_count.filter(
                extract('year', PDCRegistration.created_date) >= date_in.year,
                extract('year', PDCRegistration.created_date) <= date_out.year,
                extract('month', PDCRegistration.created_date) >= date_in.month,
                extract('month', PDCRegistration.created_date) <= date_out.month
            )
            adhhov_breakdown_month_count = adhhov_breakdown_month_count.filter(
                extract('year', PDCRegistration.created_date) >= date_in.year,
                extract('year', PDCRegistration.created_date) <= date_out.year,
                extract('month', PDCRegistration.created_date) >= date_in.month,
                extract('month', PDCRegistration.created_date) <= date_out.month,
            )
            schedule_monthly = schedule_monthly.filter(
                extract('year', PDCRegistration.created_date) >= date_in.year,
                extract('year', PDCRegistration.created_date) <= date_out.year,
                extract('month', PDCRegistration.created_date) >= date_in.month,
                extract('month', PDCRegistration.created_date) <= date_out.month,
            )
        elif date_in != '' and date_in != "\"\"":
            date_in = common.convertdmy_to_date2(date_in)
            adhhov_count = adhhov_count.filter(func.DATE(PDCRegistration.date_in) == date_in.day)
            pdc_count = pdc_count.filter(func.DATE(PDCRegistration.date_in) == date_in.day)
            pjc_count = pjc_count.filter(func.DATE(PDCRegistration.date_in) == date_in.day)
            breakdown_count = breakdown_count.filter(func.DATE(PDCRegistration.date_in.day) == date_in.day)
            schedule_current = schedule_current.filter(func.DATE(PDCRegistration.created_date) == date_in.day)
            schedule_planned = schedule_planned.filter(func.DATE(PDCRegistration.created_date) > date_in.day)
            total_work_open = total_work_open.filter(func.DATE(PDCRegistration.created_date) == date_in.day)
            total_work_closed = total_work_closed.filter(func.DATE(PDCRegistration.created_date) == date_in.day)
            repair_overhaul_count = repair_overhaul_count.filter(func.DATE(PDCRegistration.created_date) == date_in.day)
            welding_shop_count = welding_shop_count.filter(func.DATE(PDCRegistration.created_date) == date_in.day)
            tyre_shop_count = tyre_shop_count.filter(func.DATE(PDCRegistration.created_date) == date_in.day)
            pdc_pjc_month_count = pdc_pjc_month_count.filter(
                extract('year', PDCRegistration.created_date) == date_in.year,
                extract('month', PDCRegistration.created_date) == date_in.month,
            )
            adhhov_breakdown_month_count = pdc_pjc_month_count.filter(
                extract('year', PDCRegistration.created_date) == date_in.year,
                extract('month', PDCRegistration.created_date) == date_in.month,
            )
            schedule_monthly = pdc_pjc_month_count.filter(
                extract('year', PDCRegistration.created_date) == date_in.year,
                extract('month', PDCRegistration.created_date) == date_in.month,
            )
        elif date_out != '' and date_out != "\"\"":
            date_out = common.convertdmy_to_date2(date_out)
            adhhov_count = adhhov_count.filter(PDCRegistration.date_out == date_out)
            pdc_count = pdc_count.filter(PDCRegistration.date_out == date_out)
            pjc_count = pjc_count.filter(PDCRegistration.date_out == date_out)
            breakdown_count = breakdown_count.filter(PDCRegistration.date_out == date_out)
            schedule_current = schedule_current.filter(PDCRegistration.created_date == date_out)
            schedule_planned = schedule_planned.filter(PDCRegistration.created_date > date_out)
            total_work_open = total_work_open.filter(PDCRegistration.created_date == date_out)
            total_work_closed = total_work_closed.filter(PDCRegistration.created_date == date_out)
            repair_overhaul_count = repair_overhaul_count.filter(PDCRegistration.created_date == date_out)
            welding_shop_count = welding_shop_count.filter(PDCRegistration.created_date == date_out)
            tyre_shop_count = tyre_shop_count.filter(PDCRegistration.created_date == date_out)
            pdc_pjc_month_count = pdc_pjc_month_count.filter(
                extract('year', PDCRegistration.created_date) == date_out.year,
                extract('month', PDCRegistration.created_date) == date_out.month,
            )
            adhhov_breakdown_month_count = pdc_pjc_month_count.filter(
                extract('year', PDCRegistration.created_date) == date_out.year,
                extract('month', PDCRegistration.created_date) == date_out.month,
            )
            schedule_monthly = pdc_pjc_month_count.filter(
                extract('year', PDCRegistration.created_date) == date_out.year,
                extract('month', PDCRegistration.created_date) == date_out.month,
            )



    # Get Count from table Section
        data_count["ad_hoc_count"] = adhhov_count.count()
        data_count["pdc_count"] = pdc_count.count()
        data_count["pjc_count"] = pjc_count.count()
        data_count["breakdown_count"] = breakdown_count.count()

        data_count["adhoc_breakdown_count"] = adhhov_breakdown_month_count.count()
        data_count["pdc_pjc_count"] = pdc_pjc_month_count.count()

        data_count["schedule_monthly"] = schedule_monthly.count()
        data_count["schedule_current"] = schedule_current.count()
        data_count["schedule_planned"] = schedule_planned.count()

        data_count["total_wip"] = total_work_open.count()
        data_count["total_work_clsd"] = total_work_closed.count()

        data_count["repair_overhaul_count"] = repair_overhaul_count.count()
        data_count["welding_shop_count"] = welding_shop_count.count()
        data_count["tyre_shop_count"] = tyre_shop_count.count()

        response_object = {
            "ErrorCode": "9999",
            "data": data_count,
        }
        return response_object, 200

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "data": {},
            "error": str(e)
        }
        return response_object, 201


def saveWorkShopActions(data):
    try:
        for parts in data["workshop_parts"]:
            parts_query = WorkshopParts.query.filter(WorkshopParts.parts_id == parts["parts_id"]).first()
            if parts_query:
                parts_query.parts = parts["parts"]
                parts_query.parts_no = parts["parts_no"]
                parts_query.quantity = parts["quantity"]
                parts_query.isActive = int(parts["isActive"])
                parts_query.updated_by = data["updated_by"]
                save_changes(parts_query)
            else:
                new_parts = WorkshopParts(
                    pdcregistration_reference_id= data["pdcregistration_reference_id"],
                    inspection_reference_id= data["inspection_id"],
                    regn_no= data["regn_no"],
                    parts= parts["parts"],
                    parts_no= parts["parts_no"],
                    quantity= parts["quantity"],
                    updated_by= data["updated_by"],
                    isActive= int(parts["isActive"])
                )
                save_changes(new_parts)

        for action in data["workshop_actions"]:
            actions_query = WorkshopWorkAction.query.filter(WorkshopWorkAction.action_id == action["action_id"]).first()
            if actions_query:
                actions_query.description = action["description"]
                actions_query.status = action["status"]
                actions_query.updated_by = data["updated_by"]
                actions_query.isActive = int(action["isActive"])
                save_changes(actions_query)
            else:
                actions_query = WorkshopWorkAction(
                    pdcregistration_reference_id= data["pdcregistration_reference_id"],
                    inspection_reference_id= data["inspection_id"],
                    regn_no= data["regn_no"],
                    description= action["description"],
                    status= action["status"],
                    updated_by= data["updated_by"],
                    isActive= int(action["isActive"])
                )
                save_changes(actions_query)

        response_object = {
            "ErrorCode": "9999",
            "status": "success",
            "message": "Parts and Actions data saved successfully."
        }
        return response_object, 200
    except Exception as e:
        logging.exception(e)
        return {
            "ErrorCode": "9999",
            "data": [],
            "error": str(e)
        }, 201


def get_workshop_parts_action_list(rt_regn):
    try:
        returned_data = {}
        parts_count = WorkshopParts.query.filter(WorkshopParts.regn_no == str(rt_regn), WorkshopParts.isActive==1 ).count()
        parts_query = WorkshopParts.query.filter(WorkshopParts.regn_no == str(rt_regn), WorkshopParts.isActive==1 ).all()
        if parts_query:
            returned_data["parts_list"]= parts_query
        else:
            returned_data["parts_list"]= []

        actions_count = WorkshopWorkAction.query.filter(WorkshopWorkAction.regn_no == str(rt_regn), WorkshopWorkAction.isActive==1).count()
        actions_query = WorkshopWorkAction.query.filter(WorkshopWorkAction.regn_no == str(rt_regn), WorkshopWorkAction.isActive==1).all()
        if actions_query:
            returned_data["actions_list"]= actions_query
        else:
            returned_data["actions_list"]= []

        response_object = {
            "ErrorCode": "9999",
            "parts_count": parts_count,
            "actions_count": actions_count,
            "data": returned_data
        }
        return response_object, 200
    except Exception as e:
        logging.exception(e)
        return {
            "ErrorCode": "0000",
            "data": {},
            "error": str(e)
        }, 201