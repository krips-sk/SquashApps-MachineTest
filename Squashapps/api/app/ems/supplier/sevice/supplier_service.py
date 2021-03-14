# Name: supplier_service.py
# Description: This is used to save the supplier and related operations
# Author: Thirumurthy
# Created: 2020.12.31
# Copyright: © 2020 MYCURA Technologies . All Rights Reserved.
# Change History:
#                 |2020.12.31 save supplier added
import uuid
from app.cura import db
from sqlalchemy import desc, or_
import logging


#
#   feat  Used to save the Company.
#
from app.ems.supplier.model.supplier import Supplier


def save_supplier(data):
    try:
        if data['public_id'] and data['public_id'] != '':
            # id exists so require to do update
            supplier = Supplier.query.filter(Supplier.public_id == data['public_id']).first()
            if supplier:
                e_supplier = Supplier.query.filter(Supplier.email_id == data['email_id'], Supplier.isactive == 1).first()
                if e_supplier:
                    response_object = {
                        'status': 'fail',
                        'message': 'Email already exits.'
                    }
                else:
                    supplier.supplier_name = data['supplier_name']
                    supplier.supplier_location = data['supplier_location']
                    supplier.contact_number = data['contact_number']
                    supplier.email_id = data['email_id']
                    supplier.logo_path = data['logo_path']
                    supplier.updated_by = data['created_by']
                    # cmp.updated_date =
                    save_changes(supplier)
                    response_object = {
                        "Errorcode": 9999,
                        "status": "Success",
                        "message": "supplier Updated successfully",
                        'public_id': supplier.public_id
                    }
        else:
            supplier = Supplier.query.filter(Supplier.email_id == data['email_id'], Supplier.isactive == 1).first()
            if supplier:
                response_object = {
                    'status': 'fail',
                    'message': 'Email already exits.'
                }

            else:
                supplier = Supplier(
                    public_id=str(uuid.uuid4()),
                    supplier_name=data['supplier_name'],
                    supplier_location=data['supplier_location'],
                    contact_number=data['contact_number'],
                    email_id=data['email_id'],
                    logo_path=data['logo_path']
                )
                save_changes(supplier)
                response_object = {
                    'status': 'success',
                    'message': 'Successfully added.',
                    'public_id': supplier.public_id
                }
        return response_object, 200
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')


#
#   feat  get the Company by id.
#
def get_supplier_by_id(public_id):
    try:
        supplier = Supplier.query.filter_by(public_id=public_id).first()
        if supplier:
            return supplier, 200
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
#   feat  get the list of suppliers.
#
def get_supplier_list(user_id, page, row, searchterm):
    try:
        doc_list_query = Supplier.query.filter(Supplier.isactive == 1)
        if searchterm and searchterm != '' and searchterm != "\"\"":
            search = "%{}%".format(searchterm)
            doc_list_query = doc_list_query.filter(
                or_(Supplier.supplier_name.ilike(search), Supplier.supplier_location.ilike(search)))
        doc_list = doc_list_query.order_by(desc(Supplier.id)).paginate(int(page), int(row), False).items
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
#   feat  get the list of suppliers.
#
def get_all_supplier_list():
    try:
        doc_list = Supplier.query.filter(Supplier.isactive == 1) \
            .order_by(desc(Supplier.id)).all()

        doc_list_count = Supplier.query.filter(Supplier.isactive == 1) \
            .order_by(desc(Supplier.id)).count()

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
def delete_supplier_data(data):
    try:
        doc_data = Supplier.query.filter(Supplier.public_id == data['public_id'], Supplier.isactive == 1).first()
        if doc_data:
            doc_data.isactive = -2
            save_changes(doc_data)
            response_object = {
                "Errorcode": 9999,
                "status": "Success",
                "message": "supplier deleted successfully"
            }
        else:
            response_object = {
                "Errorcode": 9998,
                "status": "failure",
                "message": "supplier does not exists"
            }
        return response_object
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')
        return {
            "Errorcode": 9997,
            "status": "failure",
            "message": "Problem with deleting supplier"
        }


#
#   feat  Used to get the company Details by Public id.
#

def get_supplier_details(public_id):
    try:
        supplier_data = Supplier.query.filter(Supplier.public_id == public_id, Supplier.isactive == 1).first()
        if supplier_data:

            return supplier_data
        else:
            return {"ErrorCode": "9997",
                    "URL": "",
                    "Message": "supplier doesnot exists",
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
