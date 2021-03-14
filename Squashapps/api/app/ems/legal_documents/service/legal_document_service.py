import logging
import os
import json
import uuid
from app.cura import db
from datetime import datetime
from app.ems import config
from werkzeug.utils import secure_filename
from flask import send_file,send_from_directory

from app.cura.user.model.user import User

from app.cura.email.service.email_service import send_notification
from ..model.legal_document import Legal_Document
from flask import send_from_directory
from app.cura.common import common


def DocumentUpload(file):
    try:
        if file:
            org_filename = secure_filename(file.filename)
            # org_filename="1610016062459-cropped.jpg"
            ext = org_filename.split('.')[1].split('?')[0]
            uuid_file = str(uuid.uuid4())
            uuid_filename = uuid_file + "." + ext
            directory = os.path.join(config.UploadFilePath)
            if not os.path.exists(directory):
                os.makedirs(directory)
            file.save(os.path.join(config.UploadFilePath, uuid_filename))

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

def get_document(filename):
    try:
        # uploads = os.path.join(config.doc_savedir, filename)
        return send_from_directory(directory=config.UploadFilePath, filename=filename)

    except Exception as e:
        print(e)


def get_document_data(userid):
    try:
        notice_content = ''
        files = []
        user = User.query.filter_by(id=userid,isActive=1).first()
        legal_document = Legal_Document.query.filter_by(document_status=0,user_id=userid, isActive=1).all()
        if legal_document:
            for doc in legal_document:
                file = {}
                notice_content = doc.notice_content
                file['original_file_name'] = doc.original_file_name
                file['uuid_file_name'] = doc.uuid_file_name
                file['doc_id'] = doc.document_id
                files.append(file)

        if user:
            data = {}
            data["license_expiry_date"] = "" if (user.licence_expiry == '' or user.licence_expiry == None ) else user.licence_expiry.strftime('%d-%m-%Y')
            data["gdl_expiry_date"] = "" if (user.gdl_expiry == '' or user.gdl_expiry == None ) else user.gdl_expiry.strftime('%d-%m-%Y')
            data["medical_check_up"] = "" if (user.medical_expiry == '' or user.medical_expiry == None ) else user.medical_expiry .strftime('%d-%m-%Y')
            data["passport_expiry_date"] = "" if (user.passport_expiry_date == '' or user.passport_expiry_date == None ) else datetime.strptime(user.passport_expiry_date,"%Y-%m-%d").strftime('%d-%m-%Y')
            data["base_pass_expiry_date"] = "" if (user.base_pass_expiry_date == '' or user.base_pass_expiry_date == None ) else user.base_pass_expiry_date.strftime('%d-%m-%Y')
            data["original_file_names"] = files
            data["notice_content"] = notice_content

            response_object = {
                "ErrorCode": "9999",
                "data": data
            }
        else:
            response_object = {
                "message": "User not exists",
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

def Savelegaldocument(data):
    try:
        document_id = 0
        document_status=0
        if data["document_type"]==2:
            document_status=1
        index=0
        for doc_name in data["uuid_doc_name"]:
            doc=data["original_doc_name"][index]
            document_id = doc['doc_id']
            legal_doc=Legal_Document.query.filter_by(document_id=doc['doc_id']).first()
            if doc['doc_id']==0:
                save_document = Legal_Document(
                    user_id=data["user_id"],
                    document_type=data["document_type"],
                    notice_content=data["notice_content"],
                    original_file_name=data["original_doc_name"][index]['doc_org_name'],
                    uuid_file_name=doc_name,
                    document_status=document_status,
                    created_by=data["user_id"],
                    created_date=datetime.utcnow(),
                    isActive=1
                )
                save_changes(save_document)

                document_id = save_document.document_id
            else:
                legal_doc.document_type=data["document_type"],
                legal_doc.notice_content=data["notice_content"],
                legal_doc.original_file_name= doc['doc_org_name'],
                legal_doc.uuid_file_name=doc_name,
                legal_doc.document_status=document_status
                save_changes(legal_doc)
            index=index+1
        #update in user table

        user = User.query.filter_by(id=data["user_id"], isActive=1).first()
        if user:
            user.legal_doc= 1 if document_status==0 else -1
            save_changes(user)
        response_obj = {
            "message": "Legal Document Upload Successfully",
            "Errorcode": 9999
        }

        if data["document_type"] == 2:
            send_notification('Document Upload',data["user_id"], '', 1, 1, 'tbl_legal_document', document_id)

        return response_obj

    except Exception as e:
        print("Legal Document Upload service error: " + str(e))
        logging.exception(e)
        response_obj = {
            "message": "Legal Document Upload Failed",
            "Errorcode": 9998
        }
        return response_obj


def get_admin_approve_docs():
    try:
        from sqlalchemy import desc
        user_list = User.query.filter(User.isActive==1,User.legal_doc==1).all()
        return_data=[]
        if user_list:
            for item in user_list:
                doc_list=Legal_Document.query.filter_by(user_id=item.id,isActive=1).all()
                temp={}
                temp['document_count']=len(doc_list)
                temp['first_name']=item.rkp_name
                temp['last_name'] = ""
                temp['user_id'] = item.id
                temp['license_expiry_date'] = "" if item.licence_expiry == None else item.licence_expiry.strftime('%d-%m-%Y')
                temp['passport_expiry_date'] = "" if item.passport_expiry_date == None else datetime.strptime(item.passport_expiry_date, "%Y-%m-%d").strftime('%d-%m-%Y')
                temp['gdl_expiry_date'] = "" if item.gdl_expiry == None else item.gdl_expiry.strftime('%d-%m-%Y')
                return_data.append(temp)
        response_object={
            "status":"success",
            "ErrorCode":9999,
            "data":return_data
        }
        return response_object

    except Exception as e:
        print(e)
        return { 'ErrorCode': '0000', 'status': 'fail', 'error': str(e) }

def Update_approver_status(data):
    try:
        user= User.query.filter_by(id=data['user_id'],isActive=1).first()
        if user:
            doc_status = 2  if data['approval_status'] == 1  else -1
            db.session.query(Legal_Document).filter(Legal_Document.user_id == data['user_id']
                                                    ,Legal_Document.document_status==0,Legal_Document.isActive==1).\
                update({Legal_Document.document_status: doc_status,Legal_Document.approved_by: data['approved_by'],Legal_Document.approval_notes: data['approval_notes'],Legal_Document.approved_date:datetime.utcnow(),Legal_Document.updated_date:datetime.utcnow()}, synchronize_session=False)

            # update in user table
            if data.get('password', '') != '':
                if not user.check_password(data.get('old_password')):
                    response_object = {
                        "Errorcode": 9996,
                        'status': 'mismatch',
                        'message': 'Invalid Current Password.',
                    }
                    return response_object, 201
                user.password = data['password']
            user.roles = data['roles'],
            user.gender = data['gender'],
            user.rkp_name = data['rkp_name'],
            user.employment_date = datetime.strptime(data['employment_date'], "%d-%m-%Y").strftime('%Y-%m-%d') if data[
                                                                                                                      'employment_date'] != "" and \
                                                                                                                  data[
                                                                                                                      'employment_date'] != "null" else None,
            user.employment_status = data['employment_status'],
            user.licence_expiry = datetime.strptime(data['licence_expiry'], "%d-%m-%Y").strftime('%Y-%m-%d') if data[
                                                                                                                    'licence_expiry'] != "" and \
                                                                                                                data[
                                                                                                                    'licence_expiry'] != "null" else None,
            user.licence_number = data['licence_number'],
            user.gdl_expiry = datetime.strptime(data['gdl_expiry'], "%d-%m-%Y").strftime('%Y-%m-%d') if data[
                                                                                                            'gdl_expiry'] != "" and \
                                                                                                        data[
                                                                                                            'licence_expiry'] != "null" else None,
            user.melaka_port_expiry = datetime.strptime(data['melaka_port_expiry'], "%d-%m-%Y").strftime('%Y-%m-%d') if \
                                          data['melaka_port_expiry'] != "" and data[
                                              'melaka_port_expiry'] != "null" else None,
            user.licence_type = data['licence_type'],
            user.blood_type = data['blood_type'],

            user.location = data['location'],
            user.rkp_id_number = data['rkp_id_number'],
            user.rkp_ic_number = data['rkp_ic_number'],
            user.phone_number = data['phone_number'],
            user.medical_expiry = datetime.strptime(data['medical_expiry'], "%d-%m-%Y").strftime('%Y-%m-%d') if data[
                                                                                                                    'medical_expiry'] != "" and \
                                                                                                                data[
                                                                                                                    'medical_expiry'] != "null" else None,
            user.lpg_ptp_ogsp_expiry = datetime.strptime(data['lpg_ptp_ogsp_expiry'], "%d-%m-%Y").strftime(
                '%Y-%m-%d') if \
                                           data['lpg_ptp_ogsp_expiry'] != "" and data[
                                               'lpg_ptp_ogsp_expiry'] != "null" else None,
            user.remark = data['remarks'],
            user.file_path = data['file_path'],
            user.address1 = data['address1'],
            user.address2 = data['address2'],
            user.district = data['district'],
            user.state = data['state'],
            user.post_code = data['post_code'],
            user.image_path = data['image_path'],
            user.passport_expiry_date =  datetime.strptime(data['passport_expiry_date'], "%d-%m-%Y").strftime('%Y-%m-%d') \
                                             if data['passport_expiry_date'] != "" and  data['passport_expiry_date'] != "null" else None,
            user.base_pass_expiry_date = datetime.strptime(data['base_pass_expiry_date'], "%d-%m-%Y").strftime('%Y-%m-%d') \
                                             if data['base_pass_expiry_date'] != "" and  data['base_pass_expiry_date'] != "null" else None,
            user.legal_doc = -1
            save_changes(user)

            response_obj = {
                "message": "Legal Document Approved Successfully",
                "Errorcode": 9999
            }
        else:
            response_obj = {
                "message": "Legal Document Approve failed",
                "Errorcode": 9998
            }
        return response_obj

    except Exception as e:
        print("Legal Document Upload service error: " + str(e))
        logging.exception(e)
        response_obj = {
            "message": "Legal Document Upload Failed",
            "Errorcode": 9998
        }
        return response_obj
def download_doc(file_name):
    try:
        directory = os.path.join(config.UploadFilePath)
        path = directory+"/"+file_name
        return send_file(path, as_attachment=True)
    except Exception as e:
        print(e)
def save_changes(data):
    db.session.add(data)
    db.session.commit()