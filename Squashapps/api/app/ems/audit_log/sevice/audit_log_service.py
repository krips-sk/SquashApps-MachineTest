# Name: audit_log_service.py
# Description: used for audit log related operation.
# Author: Mycura
# Created: 2020.12.14
# Copyright: © 2020 EMS . All Rights Reserved.
# Change History:
#                |2020.12.14

import datetime
from app.cura import db
import logging
from sqlalchemy import or_, desc, asc, and_
from app.cura.common import common
from app.ems.audit_log.model.audit_log import AuditLog
from app.cura.user.model.user import User
from sqlalchemy import func


def save_changes(data):
    db.session.add(data)
    db.session.commit()


def save_audit_log(data):
    try:
        audit_log = AuditLog(
            type=data["type"],
            sub_type=data["sub_type"],
            details=data["details"],
            created_by=data["created_by"],
            created_date=datetime.datetime.utcnow()
        )
        save_changes(audit_log)
        response_object = {
            "ErrorCode": "9999",
            "Status": "Audit Log added successfully"
        }

        return response_object

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "PDC save failed",
            "Error": str(e)
        }
        return response_object


#
#   feat - Used to get the list of audit logs
#
def get_audit_log_list(page, row, searchterm, tabindex, sortindex):
    try:
        # log_query = AuditLog.query.filter_by(isActive=1)
        user_query = db.session.query(func.concat(User.first_name, ' ', User.last_name)).\
            filter(AuditLog.created_by == User.id).label("user_name")
        log_query = db.session.query(AuditLog, user_query).filter(AuditLog.isActive == 1)

        if searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            log_query = log_query.filter(or_(AuditLog.type.ilike(search),
                                             AuditLog.sub_type.ilike(search),
                                             user_query.ilike(search)))

        # Sorting functionality
        if tabindex == 1:
            if sortindex == 1:
                log_query = log_query.order_by(asc(AuditLog.type))
            else:
                log_query = log_query.order_by(desc(AuditLog.type))
        elif tabindex == 2:
            if sortindex == 1:
                log_query = log_query.order_by(asc(AuditLog.sub_type))
            else:
                log_query = log_query.order_by(desc(AuditLog.sub_type))
        else:
            log_query = log_query.order_by(desc(AuditLog.audit_log_id))

        log_data = log_query.paginate(int(page), int(row), False).items
        count = log_query.count()

        auditlog_list = []
        if log_data:
            for log in log_data:
                item = {}
                item['audit_log_id'] = log.AuditLog.audit_log_id
                item['type'] = log.AuditLog.type
                item['sub_type'] = log.AuditLog.sub_type
                item['details'] = log.AuditLog.details
                item['created_by'] = log.AuditLog.created_by
                item['user_name'] = log.user_name
                item['date_time'] = (log.AuditLog.created_date + datetime.timedelta(hours=8)).strftime('%d-%m-%Y %H:%M:%S')
                auditlog_list.append(item)

            response_object = {
                "data": auditlog_list,
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
#   feat - Used to get the audit_log using the given id
#
def get_by_id(audit_log_id):
    try:
        audit_log = AuditLog.query.filter_by(isActive=1, audit_log_id=audit_log_id).first()
        return audit_log, 200

    except Exception as e:

        logging.exception(e)
        return {}, 201


#
#   feat - Used to delete the audit_log
#
def delete_audit_log(data):
    try:
        audit_log = AuditLog.query.filter_by(isActive=1,
                                                           audit_log_id=data["audit_log_id"]).first()

        if audit_log:
            audit_log.isActive = "0"
            audit_log.updated_by = data["userid"]
            audit_log.updated_date = datetime.datetime.utcnow()

            save_changes(audit_log)

            response_object = {
                "ErrorCode": "9999",
                "Status": "audit_log delete successfully"
            }

        else:
            response_object = {
                "ErrorCode": "9997",
                "Status": "audit_log not exists"
            }
        return response_object, 201

    except Exception as e:
        logging.exception(e)

        response_object = {
            "ErrorCode": "0000",
            "Status": "audit_log delete failed"
        }

        return response_object, 201
