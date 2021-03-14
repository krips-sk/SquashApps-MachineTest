# Name: product_list_controller.py
# Description: This is used to save the Product list values and related operations
# Author: Kumaresan A
# Created: 2021.01.25
# Copyright: © 2020 MYCURA Technologies . All Rights Reserved.
# Change History:
#                 |2021.02.18 save department added

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
from sqlalchemy import and_, or_, desc, cast, asc

from app.ems.dropdown_list.model.product import Product


#
#   feat  Used to save the Company.
#
def save_Product(data):
    try:
        if( data["product_id"] == 0 ):
            item = Product.query.filter(
                and_(Product.type.ilike(data["type"]), Product.product_value.ilike(data["product_value"]),
                     Product.isActive == 1)
            ).first()
            if not item:
                product = Product(
                    product_name=data["product_name"],
                    product_value=data["product_value"],
                    type=data["type"],
                    isActive=1
                )
                save_changes(product)
                response_object = {
                    'status': 'success',
                    'message': 'Successfully added.',
                    'id': product.product_id
                }
            else:
                response_object = {
                    'status': 'fail',
                    'message': 'Already Exists.'
                }
        else:
            item = Product.query.filter(product_id=data["product_id"], isActive=1).first()
            if not item:
                response_object= {
                    'status': 'fail',
                    'message': 'Product update failed.'
                }
            else:
                item.product_name= data["product_name"]
                item.product_value= data["product_value"]
                item.type= data["type"]
                save_changes(item)
                response_object = {
                    'status': 'success',
                    'message': 'Successfully updated.'
                }
        return response_object, 200
    except Exception as e:
        logging.exception(e)
        print(e)
        return {
            'ErrorCode': '0000',
            'message': 'Product save failed.'
        }


#
#   feat  get the list of Product.
#
def get_product_list(type):
    try:
        productlist = Product.query.order_by(asc(Product.product_id)).filter(Product.type.ilike(type),
                                                                             Product.isActive == 1).all()

        if productlist:
            product_list = []
            for item in productlist:
                temp = {}
                temp['product_id'] = item.product_id
                temp['product_name'] = item.product_name
                temp['product_value'] = item.product_value
                temp['type'] = item.type
                product_list.append(temp);
            response_obj = {
                "ErrorCode": 9999,
                "data": product_list
            }
        else:
            response_obj = {
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


def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        logging.exception(e)
