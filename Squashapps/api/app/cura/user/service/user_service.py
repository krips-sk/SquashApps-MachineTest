import uuid
from datetime import datetime
from app.cura import db
from app.cura.email.model.email import Email, ForgotPass
from app.cura.user.model.user import User
from app.cura.user.model.state import States
from app.cura.user.model.district import District

from app.cura.user.model.device import Device
import pathlib

from sqlalchemy import and_, or_, desc, cast, asc
from sqlalchemy.orm.attributes import flag_modified
import logging
from sqlalchemy import func
from threading import Thread
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.cura import config
import os
import uuid
import base64
from flask import send_from_directory
from app.cura.config import image_savedir
from werkzeug.utils import secure_filename
from app.cura.common import common

def add_user(data):
    try:
        if data['public_id']=="":
            user = User.query.filter_by(email=data['email']).filter_by(isActive=1).first()
            if not user:
                 new_user = User(
                    public_id=str(uuid.uuid4()),
                    email=data['email'],
                    password=data['password'],
                    roles=data['roles'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    image_path=data['image_path'],
                    gender=data['gender'],
                    licence_expiry=common.convertdmy_to_date2(data['license_expiry']),
                    created_by=data['created_by'],
                    created_date=datetime.utcnow(),
                    isActive='1',
                 )
                 save_changes(new_user)
                 # need to send email to the user.
                 response_object = {
                    "message": "success",
                    "Errorcode": 9999
                 }
                 return response_object, 200
            else:
                response_object = {
                    "status": "success",
                    "Errorcode": 9998,
                    "message":"email already exists"
                }
                return response_object, 200
        else:
            user = User.query.filter_by(public_id=data['public_id']).filter_by(isActive=1).first()
            if data.get('password', '') != '':
                if not user.check_password(data.get('old_password')):
                    response_object = {
                        'status': 'mismatch',
                        'message': 'Invalid Current Password.',
                    }
                    return response_object, 201
                user.password = data['password']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.roles = data['roles']
            user.updated_by = data['created_by']
            user.gender = data['gender']
            user.licence_expiry = common.convertdmy_to_date2(data['license_expiry'])

            save_changes(user)
            response_object = {
                "message": "success",
                "Errorcode": 9999
            }
            return response_object, 200
    except Exception as e:
        print(e)
        print('Handling run-time error:')

def save_user(data):
    try:
        if data['public_id']=="":
            user_rkp_id_number = User.query.filter_by(rkp_id_number=data['rkp_id_number']).filter_by(isActive=1).first()
            if user_rkp_id_number and data['rkp_id_number']!="":
                response_object = {
                    "status": "success",
                    "Errorcode": 9997,
                    "message": "rkp id number already exists"
                }
                return response_object, 200
            user = User.query.filter(func.lower(User.email)==func.lower(data['user_name'])).filter_by(isActive=1).first()

            if not user:
                 new_user = User(
                     public_id=str(uuid.uuid4()),
                     password=data['password'],
                     roles=data['roles'],
                     email=data['user_name'],
                     gender=data['gender'],
                     rkp_name=data['rkp_name'],
                     employment_date = datetime.strptime(data['employment_date'], "%d-%m-%Y").strftime('%Y-%m-%d') if data['employment_date']!="" and data['employment_date']!="null" else None,
                     employment_status = data['employment_status'],
                     licence_expiry =datetime.strptime(data['licence_expiry'], "%d-%m-%Y").strftime('%Y-%m-%d') if data['licence_expiry']!="" and data['licence_expiry']!="null" else None,
                     licence_number = data['licence_number'],
                     gdl_expiry = datetime.strptime(data['gdl_expiry'], "%d-%m-%Y").strftime('%Y-%m-%d') if data['gdl_expiry']!="" and data['licence_expiry']!="null" else None,
                     melaka_port_expiry =  datetime.strptime(data['melaka_port_expiry'], "%d-%m-%Y").strftime('%Y-%m-%d') if data['melaka_port_expiry']!="" and data['melaka_port_expiry']!="null" else None,
                     licence_type = data['licence_type'],
                     blood_type =data['blood_type'],
                     location = data['location'],
                     rkp_id_number = data['rkp_id_number'],
                     rkp_ic_number = data['rkp_ic_number'],
                     phone_number = data['phone_number'],
                     medical_expiry =  datetime.strptime(data['medical_expiry'], "%d-%m-%Y").strftime('%Y-%m-%d') if data['medical_expiry']!="" and data['medical_expiry']!="null" else None,
                     lpg_ptp_ogsp_expiry =  datetime.strptime(data['lpg_ptp_ogsp_expiry'], "%d-%m-%Y").strftime('%Y-%m-%d') if data['lpg_ptp_ogsp_expiry']!="" and data['lpg_ptp_ogsp_expiry']!="null" else None,
                     remark = data['remarks'],
                     file_path = data['file_path'],
                     address1 = data['address1'],
                     address2 = data['address2'],
                     district = data['district'],
                     state = data['state'],
                     post_code = data['post_code'],
                     image_path = data['image_path'],
                     created_by=data['created_by'],
                     created_date=datetime.utcnow(),
                     isActive=1,
                     passport_expiry_date=data['passport_expiry_date'],
                     last_working_date=data['last_working_date'],
                     category=data['category'],
                     capacity=data['capacity'],
                     branch=data['branch'],
                     user_status=data['user_status']
                 )
                 save_changes(new_user)
                 # need to send email to the user.
                 response_object = {
                    "public_id": new_user.public_id,
                    "message": "success",
                    "Errorcode": 9999
                 }
                 return response_object, 200
            else:
                response_object = {
                    "status": "success",
                    "Errorcode": 9998,
                    "message":"user name already exists"
                }
                return response_object, 200
        else:
            user = User.query.filter_by(public_id=data['public_id']).filter_by(isActive=1).first()
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
            user.gender= data['gender'],
            user.rkp_name=data['rkp_name'],
            user.employment_date = datetime.strptime(data['employment_date'], "%d-%m-%Y").strftime('%Y-%m-%d') if data['employment_date']!="" and data['employment_date']!="null" else None,
            user.employment_status = data['employment_status'],
            user.licence_expiry = datetime.strptime(data['licence_expiry'], "%d-%m-%Y").strftime('%Y-%m-%d') if data['licence_expiry']!="" and data['licence_expiry']!="null" else None,
            user.licence_number = data['licence_number'],
            user.gdl_expiry = datetime.strptime(data['gdl_expiry'], "%d-%m-%Y").strftime('%Y-%m-%d') if data['gdl_expiry']!="" and data['licence_expiry']!="null" else None,
            user.melaka_port_expiry = datetime.strptime(data['melaka_port_expiry'], "%d-%m-%Y").strftime('%Y-%m-%d') if data['melaka_port_expiry']!="" and data['melaka_port_expiry']!="null" else None,
            user.licence_type = data['licence_type'],
            user.blood_type = data['blood_type'],

            user.location = data['location'],
            user.rkp_id_number = data['rkp_id_number'],
            user.rkp_ic_number = data['rkp_ic_number'],
            user.phone_number = data['phone_number'],
            user.medical_expiry = datetime.strptime(data['medical_expiry'], "%d-%m-%Y").strftime('%Y-%m-%d') if data['medical_expiry']!="" and data['medical_expiry']!="null" else None,
            user.lpg_ptp_ogsp_expiry = datetime.strptime(data['lpg_ptp_ogsp_expiry'], "%d-%m-%Y").strftime('%Y-%m-%d') if data['lpg_ptp_ogsp_expiry']!="" and data['lpg_ptp_ogsp_expiry']!="null" else None,
            user.remark = data['remarks'],
            user.file_path = data['file_path'],
            user.address1 = data['address1'],
            user.address2 = data['address2'],
            user.district = data['district'],
            user.state = data['state'],
            user.post_code = data['post_code'],
            user.image_path = data['image_path'],
            user.passport_expiry_date = data['passport_expiry_date'],
            user.last_working_date = data['last_working_date'],
            user.category = data['category'],
            user.capacity = data['capacity'],
            user.branch = data['branch'],
            user.user_status = data['user_status']
            save_changes(user)
            response_object = {
                "public_id": user.public_id,
                "message": "success",
                "Errorcode": 9999
            }
            return response_object, 200
    except Exception as e:
        print(e)
        print('Handling run-time error:')

def get_user_dropdown(search,page,row):
    try:
        user_query = User.query
        user_query = user_query.filter_by(isActive=1)


        if search != '' and search != "\"\"":
            search = "%{}%".format(search)
            user_query = user_query.filter(or_(User.rkp_name.ilike(search),User.first_name.ilike(search),User.email.ilike(search),User.rkp_id_number.ilike(search)))

        user_list_count = user_query.count()

        user_list = user_query.order_by(desc(User.id)).paginate(int(page), int(row), False).items
        return_list=[]
        for item in user_list:
            temp={}
            # temp['rkp_name']=item.rkp_name
            temp['rkp_name'] = item.rkp_name if item.rkp_name != None and item.rkp_name != "" else item.first_name
            temp['user_id'] = item.id
            temp['rkp_id'] = item.rkp_id_number
            return_list.append(temp)
        response_object = {
            "message": "success",
            "Errorcode": 9999,
            "data":return_list,
            "user_list_count":user_list_count
        }
        return response_object, 200
    except Exception as e:
        print(e)
def getuserInformation(user_id):
    try:
        data = {}
        user = User.query.filter(User.id==user_id,User.isActive!=0).first()

        if user:
            data['public_id'] = user.public_id
            data['rkp_name'] = user.rkp_name
            data['user_name'] = user.email
            data['employment_date'] = "" if (user.employment_date == '' or user.employment_date == None) else user.employment_date.strftime('%d-%m-%Y')
            data['employment_status'] = user.employment_status
            data['licence_expiry'] = "" if (user.licence_expiry == '' or user.licence_expiry == None) else user.licence_expiry.strftime('%d-%m-%Y')
            data['licence_number'] = user.licence_number
            data['gdl_expiry']= "" if (user.gdl_expiry == '' or user.gdl_expiry == None) else user.gdl_expiry.strftime('%d-%m-%Y')
            data['melaka_port_expiry'] = "" if (user.melaka_port_expiry == '' or user.melaka_port_expiry == None) else user.melaka_port_expiry.strftime('%d-%m-%Y')
            data['licence_type']=user.licence_type
            data['blood_type'] = user.blood_type
            data['location'] = user.location
            data['rkp_id_number']=user.rkp_id_number
            data['rkp_ic_number'] = user.rkp_ic_number
            data['phone_number'] = user.phone_number
            data['medical_expiry'] = "" if (user.medical_expiry == '' or user.medical_expiry == None) else user.medical_expiry.strftime('%d-%m-%Y')
            data['lpg_ptp_ogsp_expiry'] = "" if (user.lpg_ptp_ogsp_expiry == '' or user.lpg_ptp_ogsp_expiry == None) else user.lpg_ptp_ogsp_expiry.strftime('%d-%m-%Y')
            data['remarks'] = user.remark
            data['file_path'] = user.file_path
            data['address1'] = user.address1
            data['address2'] = user.address2
            data['district'] = user.district
            data['state'] = user.state
            data['post_code'] = user.post_code
            data['image_path'] = user.image_path
            data['roles'] = user.roles
            data['gender'] = "0" if user.gender == None else user.gender
            data['active_status'] = user.isActive
            data['passport_expiry_date']=user.passport_expiry_date
            data['last_working_date']=user.last_working_date
            data['category']=user.category
            data['capacity']= user.capacity
            data['branch'] = user.branch
            data['user_status'] = user.user_status
        response_obj = {
            "Errorcode":9999,
            "data": data,
        }
        return response_obj
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')

def saveforgot(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        print(e)
        print('Handling run-time error:')


def update_user(data):
    try:
        user = User.query.filter_by(public_id=data['public_id']).first()
        if user:
            if data.get('password', '') != '':
                if not user.check_password(data.get('old_password')):
                    response_object = {
                        'status': 'mismatch',
                        'message': 'Invalid Current Password.',
                    }
                    return response_object, 201
                user.password = data['password']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.business_name = data['business_name']
            user.business_number = data['business_number']
            user.roles = data['roles']
            user.permission = data['permission']
            user.address=data['address']
            user.updated_by = data['updated_by']

            save_changes(user)
            return generate_token(user)
        else:
            response_object = {
                'status': 'fail',
                'message': 'User not exists.',
            }
            return response_object, 201
    except Exception as e:
        print(e)
        print('Handling run-time error:')


def update_user_password(data):
    try:
        user = User.query.filter_by(public_id=data['public_id']).first()
        if user:
            user.password = data['password']
            save_changes(user)
            response_object = {
                'ErrorCode': 9999,
                'message': 'Password Updated Successfully',
            }
            return response_object, 201
        else:
            response_object = {
                'ErrorCode': 9996,
                'message': 'Invalid User',
            }
            return response_object, 201

    except Exception as e:
        print(e)
        print('Handling run-time error:')


def delete_user(data,status):
    try:
        if status == '0':
            user = User.query.filter_by(public_id=data['public_id']).first()
            user.isActive = -2
            save_changes(user)

            # logging.info("Checking user role")
            # if 2 in user.roles:
            # # here require to delete all its company and its branch, users,..etc
            #     logging.info("Starting thread")
            #     thr = Thread(target=run_async_func, args=[user.id])
            #     thr.start()
            #     logging.info("Thread Started")

            return generate_token(user)
        else:
            logging.info("This is a test log")
            if status == '1':
                user = User.query.filter_by(public_id=data['public_id']).first()
                user.isActive = 1
                save_changes(user)
                return generate_token(user)
            else:
                user = User.query.filter_by(public_id=data['public_id']).first()
        if user:
            user.isActive = 0

            save_changes(user)
            return generate_token(user)
        else:
            response_object = {
                'status': 'fail',
                'message': 'User not exists.',
            }
            return response_object, 201
    except Exception as e:
        print(e)
        print('Handling run-time error:')


def get_all_users_bytype(searchterm, roles,page, row):
    try:
        user_query = User.query
        if searchterm != '\"\"':
            user_query = user_query.filter(
                                    and_(
                                        or_(
                                            User.email.ilike('%'+searchterm+'%'),
                                            User.first_name.ilike('%' + searchterm + '%'),
                                            User.last_name.ilike('%' + searchterm + '%'),

                                            ),
                                            User.isActive == 1

                                         ))
        else:
            user_query = user_query.filter_by(isActive=1)
        if roles !='\"\"':
            role_obj = { int(roles) }
            user_query = user_query.filter(User.roles == role_obj)
        user_list_count = user_query.count()
        user_list = user_query.order_by(desc(User.id)).paginate(int(page), int(row), False).items
        user_list_rsp = []
        for usr in user_list:
            slguser = { "email" : usr.email, "id" : usr.id , "first_name" : usr.first_name, "last_name" : usr.last_name,
                        "roles" : usr.roles,"public_id" : usr.public_id,"gender" : usr.gender, "licence_expiry": "" if usr.licence_expiry == None else usr.licence_expiry.strftime('%d-%m-%Y'),
                        "address" : usr.address, "created_date": str(usr.created_date), "updated_date": str(usr.updated_date), "isActive": usr.isActive}
            user_list_rsp.append(slguser)
        response_obj = {
            "data": user_list_rsp,
            "total_count": user_list_count
        }
        return response_obj
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')


def get_all_users_by_Role(RoleId):
    try:
        return User.query.filter_by(isActive=1).all()
    except Exception as e:
        print(e)
        print('Handling run-time error:')


def get_a_user(public_id):
    try:
        row = User.query.filter_by(public_id=public_id).first()
        item = {}
        item['address'] = row.address
        item['gender'] = str(row.gender)
        item['created_by'] = str(row.created_by)
        item['created_date'] = str(row.created_date)
        item['email'] = str(row.email)
        item['first_name'] = str(row.first_name)
        item['id'] = str(row.id)
        item['last_name'] = str(row.last_name)
        item['public_id'] = str(row.public_id)
        item['roles'] = row.roles
        item['licence_expiry'] = str(row.licence_expiry)
        item['isActive'] = str(row.isActive)
        return item
    except Exception as e:
        print(e)
        print('Handling run-time error:')


def get_a_user_Bybusiness(businessname):
    userlist = User.query.filter(func.lower(User.business_name) == func.lower(businessname)).filter(User.isActive==1).all()

            # and_(
            #     or_(User.email.ilike('%' + searchterm + '%'), User.first_name.ilike('%' + searchterm + '%'),
            #         User.last_name.ilike('%' + searchterm + '%'), User.business_name.ilike('%' + searchterm + '%')),
            #     User.isActive == 1
            # )
    #)
    list = [];
    for item in userlist:
        newObj = {"id": item.id,
                  "name":  str(item.first_name) + " " + str(item.last_name) };
                 # "name": item.business_name + " " + "(" + str(item.first_name) + " " + str(item.last_name) + ")"};
        list.append(newObj)
    return list

def generate_token(user):
    try:
        # generate the auth token
        # auth_token = User.encode_auth_token(user.id)
        response_object = {
            'status': 'success',
            'message': '',
            # 'Authorization': auth_token.decode(),
            'User id': user.id,
            'User Public id': user.public_id
        }
        return response_object, 201
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }
        return response_object, 201

def address_add(data):

        address = User.query.filter_by(public_id=data['public_id']).first()

        if address:
            if address.client_id == None:
                client_id_count = User.query.order_by(User.client_id.desc()).filter(User.client_id != None).first()
                if client_id_count == None:
                  count = 1000
                else:
                  count = int(client_id_count.client_id) + int(1)


                address.address = data["address_details"]
                address.first_name = data["first_name"]
                address.last_name = data["last_name"]
                address.business_name = data['business_name']
                address.client_id = count,
                address.business_number = data['business_number']
                address.two_factor_authentication = data['two_factor_authentication']
                address.provider = data['provider']
                address.contacts = [data["contact_details"][0]]
                address.tax_id = data['tax_id']
                # address.pricing_tier = pricing_tier
                address.show_price = data['show_price']
                flag_modified(address, "address")
                save_changes(address)
                response_object = {
                    'status': 'success',
                    'message': 'Successfully added.',
                    'address id': address.id
                }

                return response_object, 200
            else:
                address.address = data["address_details"]
                address.first_name = data["first_name"]
                address.last_name = data["last_name"]
                address.business_name = data['business_name']
                address.business_number = data['business_number']
                address.two_factor_authentication = data['two_factor_authentication']
                address.provider = data['provider']
                address.contacts = [data["contact_details"][0]]
                address.tax_id = data['tax_id']
                # address.pricing_tier = pricing_tier
                address.show_price = data['show_price']
                flag_modified(address, "address")
                save_changes(address)
                response_object = {
                    'status': 'success',
                    'message': 'Successfully added.',
                    'address id': address.id
                }

                return response_object, 200


def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        print(e)
        print('Handling run-time error:')


def forgotpassword(email):
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            response_object = {
                'status': 'fail',
                'message': 'Invalid Email',
                'errorcode':'9998'
            }
            return response_object, 201

        else:
            fid=str(uuid.uuid4())
            new_ForgotPass = ForgotPass(
                public_id=user.public_id,
                status=0,
                fid=fid,
                created_date=datetime.utcnow()

            )
            saveforgot(new_ForgotPass)

            template  = open(config.forgot_email_path)
            # read it
            src = template.read();
            localhost_url = config.host_url;
            # do the substitution
            REVIEW_URL = localhost_url + "forgotpass?fid=" + fid ;
            #REJECT_URL = localhost_url + "admin?url=newuser&public_id=" + user.public_id + "&status=0";
            src = src.replace('##ReceiverName##', user.first_name).replace('##URL##',REVIEW_URL)

            # src = src.replace('$logo_url', config.logo_url).replace('$REVIEW_URL', REVIEW_URL)
            subject = "Forgot Password"
            template=src
            new_Email = Email(
                public_id=user.public_id,
                to=user.email,
                fromemail=config.noreply_email,
                isSent=0,
                emailbody=template,
                ishtml=1,
            )
            save_changes(new_Email)
            sendingmail(new_Email, subject)
            response_object = {
                'status': 'success',
                'message': 'Saved successfully.',
                'errorcode':'9999'
            }
            return response_object, 201
    except Exception as e:
        print(e)
        print('Handling run-time error:')


def save_changefid(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        print(e)
        print('Handling run-time error:')

def get_userrejectedtemplate(receivername):
    try:
        filein = open(user_rejected_email_path)
        # read it
        src = filein.read();
        localhost_url = host_url;
        # do the substitution
        # ResetURL = localhost_url+"changepassword?fid="+fid;
        src = src.replace('$ReceiverName', receivername)
        src = src.replace('$logo_url', logo_url)
        # src = src.replace('$logo_url', logo_url).replace('$ResetURL', ResetURL).replace('$ResetURL', ResetURL)
        return src
    except Exception as e:
        print(e)
        print('Handling run-time error:')

def get_autocomplete_list(searchterm):
    userlist= User.query.order_by(asc(User.business_name)).filter(
        and_(
            or_(User.email.ilike('%' + searchterm + '%'), User.first_name.ilike('%' + searchterm + '%') , User.last_name.ilike('%' + searchterm + '%'),User.business_name.ilike('%' + searchterm + '%')),
            User.isActive == 1
        )
    ).all()
    list=[];
    for item in userlist:
        newObj={"id":item.public_id,"name":item.business_name+" "+"("+str(item.first_name)+" "+str(item.last_name)+ ")" };
        list.append(newObj)
    return list

def contact_us(data):
    try:
        role_id = 1
        adminuserlst = User.query.filter(User.roles.any(role_id)).filter_by(isActive=1).paginate(int(1), 3, False).items
        #properties = [221, 219]
        #adminuserlst = User.query.filter(
            #User.id.in_(properties)).all()
        template = get_template('contactus', data['message'], data['name'], data['number'])
        subject = "Contact_Us"
        for slguser in adminuserlst:
            new_Email = Email(
                public_id=slguser.public_id,
                to=slguser.email,
                fromemail=data['email'],
                isSent=0,
                emailbody=template,
                created_by=1,
                ishtml=1,
            )
            save_changes(new_Email)
            sendingmail(new_Email, subject)
        response_object = {
            'status': 'success',
            'message': 'Contact Form Submitted',
        }
        return response_object, 200
    except Exception as e:
        print(e)
        print('Handling run-time error:')


def get_approve_status(public_id):
    try:
        user = User.query.filter_by(public_id=public_id).first()
        if user:
            response_object = {
                'status': 'success',
                'message': 'Approved status',
                'data':user.is_Approved
            }
        return response_object
    except Exception as e:
        print(e)
        print('Handling run-time error:')

def sendingmail(data, subject):
    try:
       message = MIMEMultipart()
       message["From"] = data.fromemail
       message["To"] = data.to
       message["Subject"] = subject
       message.attach(MIMEText(data.emailbody, 'html'))
       text = message.as_string()
    #    msg = MIMEText(data.emailbody, 'html')
       mailServer = smtplib.SMTP(config.SMTP_Config , 587)
       mailServer.starttls()
       mailServer.login(config.noreply_email_config['send_mail_login'], config.noreply_email_config['send_mail_password'])
       mailServer.sendmail(data.fromemail, data.to , text)
       mailServer.quit()
       email_isSent = Email.query.filter_by(id=data.id).first()
       if email_isSent:
           email_isSent.isSent = 1
       save_changes(email_isSent)

    except Exception as e:
        print(e)
        print('Handling run-time error:')

def Validate_OTP(data):
    try:
        fid_data = ForgotPass.query.filter_by(public_id=data['public_id'],status=0,isactive=1).first()

        if fid_data:
            req_otp = fid_data.fid
            given_otp = data['otp']

            if req_otp == given_otp:

                fid_data.status = 1
                save_changes(fid_data)

                response_object = {
                    'ErrorCode': 9999,
                    'message': 'OTP is Valid',
                }
                return response_object, 201


            else:
                response_object = {
                    'ErrorCode': 9997,
                    'message': 'OTP is Invalid',
                }
                return response_object, 201
        else:
            response_object = {
                'ErrorCode': 9998,
                'message': 'Invalid User Request',
            }
            return response_object, 201
    except Exception as e:
        print(e)
        print('Handling run-time error:')

def profile_upload(inputtype,file):
    try:
        extension='.'+file.split('data:image/')[1].split(';base64')[0];
        newfilename = str(uuid.uuid4()) + extension
        directory = image_savedir
        if inputtype=='base64':
            imgdata = base64.b64decode(file.split(';base64,')[1])

        if not os.path.exists(directory):
            os.makedirs(directory)
        filepath=os.path.join(image_savedir,newfilename);
        with open(filepath, "wb") as fh:
         fh.write(imgdata)
         fh.close()
        response_object = {
                'filename':newfilename,
                # 'fileorgname':filename,
                'status': 'success',
                'message': 'file uploaded',
            }
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': e
        }
    return response_object, 200

def file_get(filename):
    try:
        if filename == "\"\"" or filename=="":
            filename=config.default_profile
        directory = os.path.join(image_savedir)
        return send_from_directory(directory, filename)
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': e
        }
    return response_object, 200

def update_lat_long(data):
    try:
        from app.ems.schedule.sevice.schedule_service import update_latlong
        user = User.query.filter_by(public_id=data["public_id"]).first()
        if user and data['latitude']!='' and data['longitude']!='':
            user.latitude=data['latitude']
            user.longitude=data['longitude']
            user.lat_long_updated_date=datetime.utcnow()
            response_object = {
                'status': 'success',
                'message': "updated successfully.",
                'error_code':"9999"
            }
            update_latlong(user.id,data['latitude'],data['longitude'])
            save_changes(user)
            return response_object
        else:
            response_object = {
                'status': 'fail',
                'message': "User not exists."
            }
            return response_object
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': e
        }
        return response_object

def update_device_token(data):
    try:
        if data['public_id']!="":
            update_lat_long(data)
        device = Device.query.filter_by(device_id=data["device_id"]).first()
        if device:
            device.notification_token=data['token']
            device.updated_date=datetime.utcnow()
            response_object = {
                'status': 'success',
                'message': "updated successfully.",
                'error_code':"9999",
                'device_config_id':device.id
            }
            save_changes(device)
            return response_object
        else:
            new_device=Device(
                device_id=data["device_id"],
                notification_token=data['token'],
                created_by=1,
                created_date=datetime.utcnow(),
                isActive=1
            )
            save_changes(new_device)
            response_object = {
                'status': 'success',
                'message': "updated successfully.",
                'error_code':"9999",
                'device_config_id': new_device.id
            }
            return response_object
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': e
        }
        return response_object

def getuserdocexpiry(location,page,row):
    try:
        user_query = User.query
        user_query = user_query.filter_by(isActive=1)

        if location != '' and location != "\"\"":
            search = "%{}%".format(location)
            user_query = user_query.filter(User.location.ilike(search))

        user_list_count = user_query.count()
        user_list = user_query.order_by(desc(User.id)).paginate(int(page), int(row), False).items
        return_list=[]
        for item in user_list:
            temp={}
            temp['rkp_name']=item.rkp_name
            temp['user_id'] = item.id
            temp['licence_expiry'] =  "" if (item.licence_expiry == '' or item.licence_expiry == None) else item.licence_expiry.strftime('%d-%m-%Y')
            temp['gdl_expiry'] =  "" if (item.gdl_expiry == '' or item.gdl_expiry == None) else item.gdl_expiry.strftime('%d-%m-%Y')
            temp['melaka_port_expiry'] =  "" if (item.melaka_port_expiry == '' or item.melaka_port_expiry == None) else item.melaka_port_expiry.strftime('%d-%m-%Y')
            temp['medical_expiry'] =  "" if (item.medical_expiry == '' or item.medical_expiry == None) else item.medical_expiry.strftime('%d-%m-%Y')
            temp['lpg_ptp_ogsp_expiry'] =  "" if (item.lpg_ptp_ogsp_expiry == '' or item.lpg_ptp_ogsp_expiry == None) else item.lpg_ptp_ogsp_expiry.strftime('%d-%m-%Y')
            return_list.append(temp)
        response_object = {
            "message": "success",
            "Errorcode": 9999,
            "data":return_list,
            "user_list_count":user_list_count
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


def yearlist():
    try:
        year_list = []

        for y in reversed(range(2010, (datetime.now().year)+1)):
            year_list.append({"year" : y})

        response_object = {
            "Errorcode": 9999,
            "data": year_list,
        }
        return response_object
    except Exception as e:
        logging.exception(e)
        response_object = {
            "ErrorCode": "0000",
            "data": [],
            "Error": str(e)
        }
        return response_object

def update_device_config_into_user(user_id,device_config_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        if user:
            user.device_table_id = device_config_id
            save_changes(user)
            response_object = {
                'message': "updated successfully.",
                'error_code': "9999",
            }
            return response_object
    except Exception as e:
        print(e)

def pdf_download(data):
    try:
        import pdfkit
        from flask import send_file, send_from_directory
        # data.replace("'","\"")
        user = User.query.filter_by(id=data['user_id']).first()
        if user:
            if not os.path.exists(config.pdf_path):
                os.makedirs(config.pdf_path)
            path = config.pdf_path + '/out.pdf'
            file_path=str(pathlib.Path(__file__).parent.parent.parent.absolute()) + "/emailTemplates/ea_form.html"
            f = open(file_path, "r")
            content=f.read()
            content=content.replace('##nama##',str(user.rkp_name)).replace('##jawatan##',"").replace('##no_kpbaru##',"").replace('##bilangan##', "")\
            .replace('##no_kakitangan##', "").replace('##no_pasport##', str(user.passport_expiry_date)).replace('##no_perkeso##', "").replace('##fi##', "")\
            .replace('##gaji_kasar##', "").replace('##tarikh_mula##', "").replace('##tarikh_berhebti##', "").replace('##tip_kasar##', "") \
            .replace('##cukai##', "").replace('##manfaat##', "").replace('##ganjaran##', "").replace('##butiran_a##', "").replace('##butiran_b##',"")\
            .replace('##butiran##', "").replace('##manfaat##', "").replace('##nilai##', "").replace('##bayaran##',"").replace('##pampasan##',"") \
            .replace('##pencen##', "").replace('##anuiti##', "").replace('##JUMLAH##', "").replace('##photogan##', "").replace('##arahan##', "") \
            .replace('##zakat##', "").replace('##pelepasan##', "").replace('##zakat##', "").replace('##jumlah1##', "").replace('##nama_kumpulan##', "") \
            .replace('##amaun##', "").replace('##PERKESO##', "").replace('##zakat##', "").replace('##jumlah1##',"").replace('##nama_kumpulan##', "").replace('##no_kwsp##', "")
            pdfkit.from_string(content, path)
            return send_file(path, as_attachment=True)
        else:
            response_object = {
                "ErrorCode": "9998",
                "message": "user not exists."
            }
        return response_object
    except Exception as e:
        response={"error":str(e)}
        return response
        print(e)

def DocumentUpload(file):
    try:
        if file:
            org_filename = secure_filename(file.filename)
            # org_filename="1610016062459-cropped.jpg"
            ext = org_filename.split('.')[1].split('?')[0]
            uuid_file = str(uuid.uuid4())
            uuid_filename = uuid_file + "." + ext
            directory = os.path.join(config.profile_files)
            if not os.path.exists(directory):
                os.makedirs(directory)
            file.save(os.path.join(config.profile_files, uuid_filename))

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

def get_states():
    try:
        state_list= States.query.filter_by(isActive=1).all()
        states=States.query.join(District,States.id==District.state_id).add_columns(District.id,District.district_name).filter_by(isActive=1).all()
        return_list=[]
        states_list=[]
        for state in state_list:
            temp_item={
                "state_id": state.id,
                "state_name": state.state_name
            }
            states_list.append(temp_item)
        for item in states:
            temp={
                "state_id": item.States.id,
                "state_name": item.States.state_name,
                "district_id": item.id,
                "district_name": item.district_name
            }
            return_list.append(temp)

        temp_data={
            "states": states_list,
            "district": return_list
        }
        response_object={
            "ErrorCode":9999,
            "status": "success",
            "data": temp_data,

        }
        return response_object
    except Exception as e:
        print(e)


def get_empid_dropdown(search,page,row):
    try:
        user_query = User.query
        user_query = user_query.filter_by(isActive=1)


        if search != '' and search != "\"\"":
            search = "%{}%".format(search)
            user_query = user_query.filter(or_(User.rkp_name.ilike(search),User.rkp_id_number.ilike(search),User.first_name.ilike(search),User.email.ilike(search)))

        user_list_count = user_query.count()

        user_list = user_query.order_by(desc(User.id)).paginate(int(page), int(row), False).items
        return_list=[]
        for item in user_list:

            temp={}
            # temp['rkp_name']=item.rkp_name
            rkp_name = item.rkp_name if item.rkp_name != None and item.rkp_name != "" else item.first_name
            temp['emp_id']=rkp_name+("_"+item.rkp_id_number if item.rkp_id_number != None and item.rkp_id_number != "" else "")
            temp['user_id'] = item.id
            return_list.append(temp)
        response_object = {
            "message": "success",
            "Errorcode": 9999,
            "data":return_list,
            "user_list_count":user_list_count
        }
        return response_object, 200
    except Exception as e:
        print(e)