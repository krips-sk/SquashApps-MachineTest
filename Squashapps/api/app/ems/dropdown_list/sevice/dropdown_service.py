# Name: dropdown_list_controller.py
# Description: This is used to save the Dropdown list values and related operations
# Author: Kumaresan A
# Created: 2021.01.25
# Copyright: © 2020 MYCURA Technologies . All Rights Reserved.
# Change History:
#                 |2021.01.25 save department added

import uuid
from app.cura.user.model.user import User
from app.cura import db
from sqlalchemy import desc, or_
import logging
import pyqrcode
import json
import os
import datetime
from app.cura import db
from ..model.dropdown import DropdownList
from sqlalchemy import and_, or_, desc, cast, asc

#
#   feat  Used to save the Company.
#
from app.ems.dropdown_list.model.dropdown import DropdownList


def save_dropdown(data):
    try:
        item= DropdownList.query.filter(DropdownList.id == data['id'],DropdownList.isactive==1).first()

        if item:

            item.key_value_en= data["key_value_en"]
            item.key_value_ma= data["key_value_ma"]
            item.updated_by = data["user_id"],
            item.updated_date = datetime.utcnow(),

            save_changes(item)
            response_object = {
                'ErrorCode':9999,
                'message': 'Successfully Updated',
                'id': item.id
            }
        else:
            key_id = 0
            key = DropdownList.query.filter(DropdownList.type == data["type"]).order_by(desc(DropdownList.key_id)).first()

            if key:
                key_id = int(key.key_id) + 1
            else:
                key_id = 1

            dropdown = DropdownList(
                key_id=key_id,
                key_value_en=data["key_value_en"],
                key_value_ma=data["key_value_ma"],
                type=data["type"],
                isactive=1,
                created_by = data["user_id"],
                created_date = datetime.utcnow(),
            )
            save_changes(dropdown)
            response_object = {
                'ErrorCode':9999,
                'message': 'Successfully Added',
                'id': dropdown.id
            }
        return response_object, 200

    except Exception as e:
        logging.exception(e)
        return {
            "ErrorCode": 0000,
            "Error": str(e)
        }


#
#   feat  get the list of departments.
#
def get_dropdown_list(type):
    try:
        dropdownlist = DropdownList.query.filter(DropdownList.type.ilike(type), DropdownList.isactive == 1).order_by(asc(DropdownList.id)).all()

        if dropdownlist:
            dropdown_list = []
            for item in dropdownlist:
                temp = {}
                temp['dropdown_id'] = item.id
                temp['key_id']= item.key_id
                temp['key_value_en'] = item.key_value_en
                temp['key_value_ma'] = item.key_value_ma
                temp['type'] = item.type
                dropdown_list.append(temp);
            response_obj= {
                "ErrorCode": 9999,
                "data": dropdown_list
            }
        else:
            response_obj= {
                "ErrorCode": 9999,
                "data": []
            }

        return response_obj, 200
    except Exception as e:
        logging.exception(e)
        return {
            "ErrorCode": 0000,
            "Error": str(e)
        }



def delete_dropdown_value(drop_id,user_id):
    try:
        item= DropdownList.query.filter(DropdownList.id == drop_id).first()

        if item:
            item.isactive = 0
            item.updated_by = user_id,
            item.updated_date = datetime.utcnow(),

            save_changes(item)
            response_object = {
                'ErrorCode':9999,
                'message': 'Deleted Successfully',
            }
        else:
            response_object = {
                'status': 9998,
                'message': 'DropDown Value does not exists',
            }
        return response_object, 200
    except Exception as e:
        logging.exception(e)
        return {
            "ErrorCode": 0000,
            "Error": str(e)
        }


def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        logging.exception(e)