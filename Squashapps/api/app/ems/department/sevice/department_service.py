# Name: department_service.py
# Description: This is used to save the department and related operations
# Author: Thirumurthy
# Created: 2021.01.04
# Copyright: © 2020 MYCURA Technologies . All Rights Reserved.
# Change History:
#                 |2021.04.04 save department added
import uuid
from app.cura.user.model.user import User
from app.cura import db
from sqlalchemy import desc, or_
import logging
import pyqrcode
import json
import os
import datetime
from app.cura.config import image_savedir
from app.cura.common.common import getbase64image, goo_shorten_url

#
#   feat  Used to save the Company.
#
from app.ems.department.model.department import Department


def save_department(data):
    try:
        if data['public_id'] and data['public_id'] != '':
            # id exists so require to do update
            department = Department.query.filter(Department.public_id == data['public_id']).first()
            if department:
                e_department = Department.query.filter(Department.email_id == data['email_id'],
                                                       Department.isactive == 1).first()
                if e_department:
                    response_object = {
                        'status': 'fail',
                        'message': 'Email already exits.'
                    }
                else:
                    department.department_name = data['department_name']
                    department.department_location = data['department_location']
                    department.contact_number = data['contact_number']
                    department.email_id = data['email_id']
                    department.logo_path = data['logo_path']
                    department.updated_by = data['created_by']
                    # cmp.updated_date =
                    save_changes(department)
                    response_object = {
                        "Errorcode": 9999,
                        "status": "Success",
                        "message": "Department Updated successfully",
                        'public_id': department.public_id
                    }
        else:
            department = Department.query.filter(Department.email_id == data['email_id'],
                                                 Department.isactive == 1).first()
            if department:
                response_object = {
                    'status': 'fail',
                    'message': 'Email already exits.'
                }

            else:
                department = Department(
                    public_id=str(uuid.uuid4()),
                    department_name=data['department_name'],
                    department_location=data['department_location'],
                    contact_number=data['contact_number'],
                    email_id=data['email_id'],
                    logo_path=data['logo_path']
                )
                save_changes(department)
                response_object = {
                    'status': 'success',
                    'message': 'Successfully added.',
                    'public_id': department.public_id
                }
        return response_object, 200
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')


#
#   feat  get the Company by id.
#
def get_department_by_id(public_id):
    try:
        department = Department.query.filter_by(public_id=public_id).first()
        if department:
            return department, 200
        else:
            response_object = {
                'status': 'fail',
                'message': 'failed to get.'
            }
            return response_object, 200

    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')


#
#   feat  get the list of departments.
#
def get_department_list(user_id, page, row, searchterm):
    try:
        doc_list_query = Department.query.filter(Department.isactive == 1)
        if searchterm and searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            doc_list_query = doc_list_query.filter(
                or_(Department.department_name.ilike(search), Department.department_location.ilike(search)))
        doc_list = doc_list_query.order_by(desc(Department.id)).paginate(int(page), int(row), False).items
        doc_list_count = doc_list_query.count()
        response_obj = {
            "data": doc_list,
            "total_count": doc_list_count
        }
        return response_obj
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')


#
#   feat  get the list of departments.
#
def get_all_department_list():
    try:
        doc_list = Department.query.filter(Department.isactive == 1) \
            .order_by(desc(Department.id)).all()

        doc_list_count = Department.query.filter(Department.isactive == 1) \
            .order_by(desc(Department.id)).count()

        response_obj = {
            "data": doc_list,
            "total_count": doc_list_count
        }
        return response_obj
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')


#
#   feat  delete the Company information by using id
#
def delete_department_data(data):
    try:
        doc_data = Department.query.filter(Department.public_id == data['public_id'],
                                           Department.isactive == 1).first()
        if doc_data:
            doc_data.isactive = -2
            save_changes(doc_data)
            response_object = {
                "Errorcode": 9999,
                "status": "Success",
                "message": "department deleted successfully"
            }
        else:
            response_object = {
                "Errorcode": 9998,
                "status": "failure",
                "message": "department does not exists"
            }
        return response_object
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')
        return {
            "Errorcode": 9997,
            "status": "failure",
            "message": "Problem with deleting department"
        }


#
#   feat  Used to get the department Details by Public id.
#

def get_department_details(public_id):
    try:
        department_data = Department.query.filter(Department.public_id == public_id,
                                                  Department.isactive == 1).first()
        if department_data:

            return department_data
        else:
            return {"ErrorCode": "9997",
                    "URL": "",
                    "Message": "Department doesnot exists",
                    "Data": {}
                    }

    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')
        response_object = {
            "ErrorCode": 9998,
            "Message": "Unable to get info"
        }
        return response_object


def save_changes(data):
    db.session.add(data)
    db.session.commit()
