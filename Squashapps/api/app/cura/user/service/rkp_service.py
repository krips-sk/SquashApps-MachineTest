import uuid
import logging

from app.cura import db
from app.cura.user.model.rkp_disciplinary import RKPDisciplinary
from app.cura.user.model.rolemenu import RoleMenu
from app.cura.user.model.role import Role
from app.cura.user.model.user import User
from sqlalchemy import asc, and_, desc
import datetime
from werkzeug.utils import secure_filename
from app.cura import config
import os
import uuid
import base64
def add_disciplinary(data):
    try:
         new_user = RKPDisciplinary(
            user_id=data['user_id'],
            violation_date=datetime.datetime.strptime(data['violation_date'], "%d-%m-%Y").strftime('%Y-%m-%d') if data['violation_date']!="" and data['violation_date']!="null" else None,
            rt_number=data['rt_number'],
            location=data['location'],
            client_name=data['client_name'],
            file_path=data['file_path'],
            description=data['description'],
            created_by=data['created_by'],
            created_date=datetime.datetime.utcnow(),
            isActive=1,
         )
         save_changes(new_user)
         response_object = {
            "status": "success",
            "Errorcode": 9999
            
         }
         return response_object, 200

    except Exception as e:
        print(e)
        print('Handling run-time error:')


def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        print(e)
        print('Handling run-time error:')


def get_rkp_discipline(user_id):
    try:
        disciplinary_list = RKPDisciplinary.query.filter(RKPDisciplinary.user_id==user_id,RKPDisciplinary.isActive==1).all()
        return_list = []

        for data in disciplinary_list:
            data1 = {}
            data1["id"] = data.id
            data1["violation_date"] = "" if data.violation_date == None else data.violation_date.strftime('%d-%m-%Y')
            data1["rt_number"] = data.rt_number
            data1["location"] = data.location
            data1['client_name'] = data.client_name
            data1['file_path'] = data.file_path
            data1['description'] = data.description
            return_list.append(data1)

        response_object = {
            'data': return_list,
            'ErrorCode': '9999'
        }
        return response_object

    except Exception as e:
        logging.exception(e)
        response_object = {
            'main_menu_list': [],
            'TotalCount': 0,
            'ErrorCode': '9997',
            'components': ''
        }
        return response_object

def get_disciplinary_list(user_id,page,row):
    try:
        count = RKPDisciplinary.query.filter(RKPDisciplinary.isActive==1,RKPDisciplinary.user_id==user_id).count()
        disciplinary_list = RKPDisciplinary.query.filter(RKPDisciplinary.isActive==1,RKPDisciplinary.user_id==user_id).order_by(desc(RKPDisciplinary.id)).paginate(int(page), int(row),False).items
        return_list = []

        for data in disciplinary_list:
            data1 = {}
            data1["id"] = data.id
            data1["date"] = "" if data.violation_date == '' else data.violation_date.strftime('%d-%m-%Y')
            data1["rt_no"] = data.rt_number
            data1["location"] = data.location
            data1['client'] = data.client_name
            data1['view_records'] = data.file_path
            data1['description'] = data.description
            return_list.append(data1)
        response_object = {
            'data': return_list,
            'ErrorCode': '9999'
        }
        return response_object

    except Exception as e:
        logging.exception(e)
        response_object = {
            'main_menu_list': [],
            'TotalCount': 0,
            'ErrorCode': '9997',
            'components': ''
        }
        return response_object


def get_all_disciplinary_list(page,row):
    try:
        count = RKPDisciplinary.query.filter(RKPDisciplinary.isActive==1).count()

        disciplinary_list = db.session.query(RKPDisciplinary, User) \
            .join(User, and_(RKPDisciplinary.user_id == User.id)).filter(RKPDisciplinary.isActive==1,User.isActive == 1 ).order_by(desc(RKPDisciplinary.id)).paginate(int(page), int(row),False).items
        return_list = []

        for data in disciplinary_list:
            data1 = {}
            data1["id"] = data.RKPDisciplinary.id
            data1["date"] = "" if data.RKPDisciplinary.violation_date == '' else data.RKPDisciplinary.violation_date.strftime('%d-%m-%Y')
            data1["rt_no"] = data.RKPDisciplinary.rt_number
            data1["location"] = data.RKPDisciplinary.location
            data1['client'] = data.RKPDisciplinary.client_name
            data1['view_records'] = data.RKPDisciplinary.file_path
            data1['description'] = data.RKPDisciplinary.description
            data1['rkp_name'] =  data.User.rkp_name if data.User.rkp_name != None and data.User.rkp_name != "" else data.User.first_name + (" " if data.User.last_name == None else data.User.last_name )
            return_list.append(data1)
        response_object = {
            'data': return_list,
            'ErrorCode': '9999',
            'count': count
        }
        return response_object

    except Exception as e:
        logging.exception(e)
        response_object = {
            'main_menu_list': [],
            'TotalCount': 0,
            'ErrorCode': '9997',
            'components': ''
        }
        return response_object


def DocumentUpload(file):
    try:
        if file:
            org_filename = secure_filename(file.filename)
            # org_filename="1610016062459-cropped.jpg"
            ext = org_filename.split('.')[1].split('?')[0]
            uuid_file = str(uuid.uuid4())
            uuid_filename = uuid_file + "." + ext
            directory = os.path.join(config.disciplinary_files)
            if not os.path.exists(directory):
                os.makedirs(directory)
            file.save(os.path.join(config.disciplinary_files, uuid_filename))

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