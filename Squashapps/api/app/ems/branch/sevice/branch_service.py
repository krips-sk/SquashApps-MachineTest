# Name: branch_service.py
# Description: This is used to save the Branch and related operations
# Author: Thirumurthy
# Created: 2020.12.23
# Copyright: © 2020 MYCURA Technologies . All Rights Reserved.
# Change History:
#                 |2020.12.23 save Branch added
import uuid
from app.ems.branch.model.branch import Branch
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
def save_branch(data):
    try:
        if data['public_id'] and data['public_id'] != '':
            # id exists so require to do update
            branch = Branch.query.filter(Branch.public_id == data['public_id']).first()
            if branch:
                e_branch = Branch.query.filter(Branch.email_id == data['email_id'], Branch.isactive == 1).first()
                if e_branch:
                    response_object = {
                        'status': 'fail',
                        'message': 'Email already exits.'
                    }
                else:
                    branch.branch_name = data['branch_name']
                    branch.branch_location = data['branch_location']
                    branch.contact_number = data['contact_number']
                    branch.email_id = data['email_id']
                    branch.logo_path = data['logo_path']
                    branch.updated_by = data['created_by']
                    # cmp.updated_date =
                    save_changes(branch)
                    response_object = {
                        "Errorcode": 9999,
                        "status": "Success",
                        "message": "Branch Updated successfully",
                        'public_id': branch.public_id
                    }
        else:
            branch = Branch.query.filter(Branch.email_id == data['email_id'], Branch.isactive == 1).first()
            if branch:
                response_object = {
                    'status': 'fail',
                    'message': 'Email already exits.'
                }

            else:
                branch = Branch(
                    public_id=str(uuid.uuid4()),
                    branch_name=data['branch_name'],
                    branch_location=data['branch_location'],
                    contact_number=data['contact_number'],
                    email_id=data['email_id'],
                    logo_path=data['logo_path']
                )
                save_changes(branch)
                response_object = {
                    'status': 'success',
                    'message': 'Successfully added.',
                    'public_id': branch.public_id
                }
        return response_object, 200
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')


#
#   feat  get the Company by id.
#
def get_branch_by_id(public_id):
    try:
        branch = Branch.query.filter_by(public_id=public_id).first()
        if branch:
            return branch, 200
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
#   feat  get the list of Branches.
#
def get_branchlist(user_id, page, row, searchterm):
    try:
        doc_list_query = Branch.query.filter(Branch.isactive == 1)
        if searchterm and searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            doc_list_query = doc_list_query.filter(
                or_(Branch.branch_name.ilike(search), Branch.branch_location.ilike(search)))
        doc_list = doc_list_query.order_by(desc(Branch.id)).paginate(int(page), int(row), False).items
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
#   feat  get the list of Branches.
#
def get_allbranchlist():
    try:
        doc_list = Branch.query.filter(Branch.isactive == 1) \
            .order_by(desc(Branch.id)).all()

        doc_list_count = Branch.query.filter(Branch.isactive == 1) \
            .order_by(desc(Branch.id)).count()

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
def delete_branchdata(data):
    try:
        doc_data = Branch.query.filter(Branch.public_id == data['public_id'], Branch.isactive == 1).first()
        if doc_data:
            doc_data.isactive = -2
            save_changes(doc_data)
            response_object = {
                "Errorcode": 9999,
                "status": "Success",
                "message": "Branch deleted successfully"
            }
        else:
            response_object = {
                "Errorcode": 9998,
                "status": "failure",
                "message": "Branch does not exists"
            }
        return response_object
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')
        return {
            "Errorcode": 9997,
            "status": "failure",
            "message": "Problem with deleting Branch"
        }


#
#   feat  Used to get the company Details by Public id.
#

def get_branch_details(public_id):
    try:
        branch_data = Branch.query.filter(Branch.public_id == public_id, Branch.isactive == 1).first()
        if branch_data:

            return branch_data
        else:
            return {"ErrorCode": "9997",
                    "URL": "",
                    "Message": "Branch doesnot exists",
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
