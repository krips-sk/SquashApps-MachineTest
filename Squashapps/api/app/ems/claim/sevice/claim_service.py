# Name: dropdown_list_controller.py
# Description: This is used to save the Dropdown list values and related operations
# Author: Kumaresan A
# Created: 2021.01.25
# Copyright: © 2020 MYCURA Technologies . All Rights Reserved.
# Change History:
#                 |2021.01.25 save department added

import uuid

import logging

from app.cura import db
from sqlalchemy import and_, or_, desc, cast, asc

from datetime import datetime
from app.ems.claim.model.claim import Claim
from app.ems.claim.model.claim_details import  ClaimDetails
from werkzeug.utils import secure_filename
from app.ems import config
import os
from app.ems.dropdown_list.model.dropdown import DropdownList
from flask import send_file
from sqlalchemy.sql import operators, extract
from sqlalchemy import func
from app.cura.user.model.user import User

def save_claim(data):
    try:
        claim = Claim.query.filter(Claim.id == data['claim_id'], Claim.isactive == 1).first()
        if data['claim_id'] == '0' or claim is None:
            claim_no = ""
            claim = Claim(
                user_id=data['user_id'],
                claim_no=claim_no,
                emp_id=data['emp_id'],
                loc=data['loc'],
                department=data['department'],
                claim_type=data['claim_type'],
                claim_date=data['claim_date'],
                status=data['status'],
                grand_total=data['grand_total'],
                created_by=data['created_by'],
                created_date=datetime.utcnow(),
                isactive =1
            )


        else:
                claim.user_id=data['user_id'],
                claim.emp_id=data['emp_id'],
                claim.loc=data['loc'],
                claim.department=data['department'],
                claim.claim_type=data['claim_type'],
                claim.claim_date=data['claim_date'],
                claim.status=data['status'],
                claim.grand_total=data['grand_total'],
                claim.updated_by=data['created_by'],
                claim.updated_date=datetime.utcnow()
        save_changes(claim)

        for item in data['claim_details']:
            details=ClaimDetails.query.filter(ClaimDetails.id==item['detail_id'],ClaimDetails.isactive==1).first()
            if item['detail_id']=='0' or details is None:
                details = ClaimDetails(
                    claim_id=claim.id,
                    item=item['item'],
                    description=item['description'],
                    company_name=item['company_name'],
                    qty=item['qty'],
                    unit_price=item['unit_price'],
                    amount=item['amount'],
                    file_path=item['file_path'],
                    created_by=data['created_by'],
                    created_date=datetime.utcnow(),
                    isactive=1
                )

            else:
                details.claim_id=claim.id,
                details.item=item['item'],
                details.description=item['description'],
                details.company_name=item['company_name'],
                details.qty=item['qty'],
                details.unit_price=item['unit_price'],
                details.amount=item['amount'],
                details.file_path=item['file_path'],
                details.updated_by=data['created_by'],
                details.updated_date=datetime.utcnow()

            save_changes(details)

        response_object = {
            "ErrorCode": 9999,
            'status': 'success',
            'message': 'Successfully added.',
            'claim_id': claim.id
        }
        return response_object, 200
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')


def get_claim_details(claim_id):
    try:
        data = {}
        claim_details = db.session.query(Claim, ClaimDetails,DropdownList) \
            .join(ClaimDetails, and_(ClaimDetails.claim_id == Claim.id)) \
            .join(DropdownList, and_(Claim.claim_type == DropdownList.key_id, DropdownList.type == 'claim_type')) \
            .filter(Claim.id==claim_id,Claim.isactive==1,ClaimDetails.isactive == 1).order_by(desc(ClaimDetails.id)).all()

        # claim_details = ClaimDetails.query.order_by(desc(ClaimDetails.id)).filter(ClaimDetails.id==claim_id,ClaimDetails.isactive == 1).all()

        if claim_details:
            data['claim_type'] = claim_details[0].Claim.claim_type
            data['claim_date'] = claim_details[0].Claim.claim_date.strftime('%d-%m-%Y')
            data['claim_no'] = claim_details[0].Claim.claim_no
            data['grand_total'] = str(claim_details[0].Claim.grand_total)


            details_list = []
            for item in claim_details:
                temp = {}
                temp['claim_detail_id'] = item.ClaimDetails.id
                temp['item'] = item.ClaimDetails.item
                temp['description']= item.ClaimDetails.description
                temp['company_name'] = item.ClaimDetails.company_name
                temp['qty'] = item.ClaimDetails.qty
                temp['unit_price'] = str(item.ClaimDetails.unit_price)
                temp['amount'] = str(item.ClaimDetails.amount)
                temp['file_path'] = item.ClaimDetails.file_path
                details_list.append(temp);

            data['details_list'] = details_list


            response_obj= {
                "ErrorCode": 9999,
                "data": data
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


def get_claim_list(user_id):
    try:
        claimlist = Claim.query.order_by(desc(Claim.id)).filter(Claim.user_id==user_id,Claim.isactive == 1).all()
        if claimlist:
            claim_list = []
            for item in claimlist:
                temp = {}
                temp['claim_id'] = item.id
                temp['user_id'] = item.user_id
                temp['claim_no'] = item.claim_no
                temp['emp_id'] = item.emp_id
                temp['loc'] = item.loc
                temp['department'] = item.department
                temp['claim_type'] = item.claim_type
                temp['claim_date'] = str(item.claim_date)
                temp['grand_total'] = str(float(item.grand_total))
                temp['status'] =  str(float(item.status))
                claim_list.append(temp);
            response_obj = {
                "ErrorCode": 9999,
                "data": claim_list
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


def DocumentUpload(file):
    try:
        if file:
            org_filename = secure_filename(file.filename)
            # org_filename="1610016062459-cropped.jpg"
            ext = org_filename.split('.')[1].split('?')[0]
            uuid_file = str(uuid.uuid4())
            uuid_filename = uuid_file + "." + ext
            directory = os.path.join(config.claim_docs)
            if not os.path.exists(directory):
                os.makedirs(directory)
            file.save(os.path.join(config.claim_docs, uuid_filename))

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
        directory = os.path.join(config.claim_docs)
        path = directory+"/"+file_name
        return send_file(path, as_attachment=True)
    except Exception as e:
        print(e)
def get_claim_type_count(year,month):
    try:
        claim_type={'1':'Wages','2':'Medical','3':'Purchases','4':'Utilities'}
        claimlist = db.session.query(func.sum(Claim.grand_total),Claim.claim_type).filter(Claim.isactive == 1)\
           .filter(extract('year', Claim.claim_date) == year) .filter(extract('month', Claim.claim_date) == month).group_by(Claim.claim_type).all()
        send_data={"Wages":0,"Medical":0,"Purchases":0,"Utilities":0}
        if claimlist:
            for item in claimlist:
                send_data[claim_type.get(item.claim_type)]=str(item[0])
            response_obj = {
                "ErrorCode": 9999,
                "data": send_data
            }
        else:
          response_obj = {
            "ErrorCode": 9999,
            "data": {}
         }
        return response_obj
    except Exception as e:
        print(e)
def get_dashboard_list(year,month):
    try:
        claimlist = Claim.query.join(User,User.id==Claim.user_id).add_columns(User.rkp_name).filter(Claim.isactive == 1).filter(extract('year', Claim.claim_date) == year)\
            .filter(extract('month', Claim.claim_date) == month,User.isActive==1).all()
        return_list=[]
        if claimlist:
            for obj in claimlist:
                send_data={}
                send_data['rkp_name'] = obj.rkp_name
                for field in [x for x in dir(obj.Claim) if not x.startswith('_') and x != 'metadata']:
                    if field != 'query' and field !='query_class':
                        send_data[field] = str(obj.Claim.__getattribute__(field))
                return_list.append(send_data)
            response_obj = {
                "ErrorCode": 9999,
                "data": return_list
            }
        else:
          response_obj = {
            "ErrorCode": 9999,
            "data": return_list
         }
        return response_obj
    except Exception as e:
        print(e)

def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        logging.exception(e)

