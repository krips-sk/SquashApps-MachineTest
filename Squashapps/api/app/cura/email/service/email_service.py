from app.cura import db
from app.cura.email.model.email import Email, ForgotPass
from app.cura.user.model.user import User
from app.cura.user.model.device import Device
from app.cura.common.common import send_email
from app.cura.config import forgot_password_subject
from string import Template
from app.cura.config import host_url, forgot_email_path_otp, from_email,noreply_email, noreply_email_config, logo_url,SMTP_Config
from app.cura import  config
import os.path
import uuid
import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import json
import requests
from app.cura.email.model.email import Notification
import datetime
def sendemail(data):
    try:
        user = User.query.filter_by(email=data['email']).first()
        if user:
            fid = random.randint(1000, 9999)
            public_id= user.public_id
            id= user.id
            update_status_unused_mail(public_id)
            template= get_template(data['templatename'], data['email'], fid)
            new_ForgotPass = ForgotPass(
                public_id= public_id,
                fid= fid,
                status= 0,
                created_by= id,
            )

            new_Email = Email(
                public_id= public_id,
                to= data['email'],
                fromemail=noreply_email,
                isSent=0,
                emailbody=template,
                created_by= id,
                ishtml = 1,
            )

            saveforgot(new_ForgotPass)
            saveemail(new_Email)
            # send_email(data, template, forgot_password_subject )
            sendingmail(new_Email)
            return generate_success(user)
        else:
            response_object = {
                'status': 'fail',
                'message': 'Email not exists.',
            }
            return response_object, 201
    except Exception as e:
        print(e)
        print('Handling run-time error:')

def update_status_unused_mail(public_id):
    try:
        fid_data = ForgotPass.query.filter_by(public_id=public_id, status=0).all()

        if fid_data:
            for res in fid_data:
                res.isactive = 0,
                save_changes(res)

    except Exception as e:
        print(e)
        print('Handling run-time error:')

def get_template(name, email, fid):
    try:
        switcher = {
           'forgotpassword': forgotpassword1(email, fid),
        }

        return switcher.get(name, lambda: "Invalid month")
    except Exception as e:
        print(e)
        print('Handling run-time error:')


def verify_emaillink(data):
    try:
        fid = ForgotPass.query.filter_by(fid=data['fid']).first()
        if fid.status == 1:
            return geneate_linksuccess(fid)
        else:
            response_object = {
                'status': 'fail',
                'message': 'This link is not Expired',
            }
            return response_object, 201
    except Exception as e:
        print(e)
        print('Handling run-time error:')       


def forgotpassword1(email, fid):
    try:
        user = User.query.filter_by(email=email).first()
        filein=open(forgot_email_path_otp)
        src = filein.read();
        # localhost_url=host_url;
        # do the substitution
        # URL= localhost_url+"changepassword?fid="+fid;
        OTP = fid
        src = src.replace('$OTP', str(OTP)).replace('$ReceiverName', user.first_name.title()+" "+user.last_name.title())
        return src
    except Exception as e:
        print(e)
        print('Handling run-time error:')


def saveforgot(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        print(e)
        print('Handling run-time error:')

def saveemail(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        print(e)
        print('Handling run-time error:')

def generate_success(user):
    try:
        # generate the auth token
        # auth_token = User.encode_auth_token(user.id)
        response_object = {
            'status': 'success',
            'message': 'Mail send successfully.',
            # 'Authorization': auth_token.decode(),
            'user_id': user.id,
            'user_public_id': user.public_id
        }
        return response_object, 201
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }
        return response_object, 201

def geneate_linksuccess(user):
    try:
        # generate the auth token
        # auth_token = User.encode_auth_token(user.id)
        response_object = {
            'status': 'success',
            'message': 'This link is Expired.',
            # 'Authorization': auth_token.decode(),
        }
        return response_object, 201
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': 'This link is not Expired.'
        }
        return response_object, 201

def sendingmail(data):
    try:
        message = MIMEMultipart()
        message["From"] = data.fromemail
        message["To"] = data.to
        message["Subject"] = "Forgot Password"
        message.attach(MIMEText(data.emailbody, 'html'))
        text = message.as_string()
        #    msg = MIMEText(data.emailbody, 'html')
        mailServer = smtplib.SMTP(SMTP_Config, 587)
        mailServer.starttls()
        mailServer.login(noreply_email_config['send_mail_login'], noreply_email_config['send_mail_password'])
        mailServer.sendmail(data.fromemail, data.to, text)
        mailServer.quit()
    except Exception as e:
        print(e)
        print('Handling run-time error:')
def send_notification(notification_type,from_user,to_user,is_web,approve_status,table_name,table_detail_id):
    try:
        sender = User.query.filter(User.id == from_user, User.isActive == 1).first()
        receivers=[]

        if notification_type==1:
            content=sender.first_name+' has submitted PDC'
            title='PDC Request'
            receivers = User.query.join(Device,Device.id==User.device_table_id).add_columns(User.id,Device.notification_token).filter(User.roles=='{10}',User.isActive==1).all()

        if notification_type == 2:
            message=' has approved your PDC'
            if approve_status==-1:
                message =' has rejected your PDC'
            content = sender.first_name+ message
            title='Approval Status'
            receivers = User.query.join(Device,Device.id==User.device_table_id).add_columns(User.id,Device.notification_token).filter(User.id==to_user,User.isActive==1).all()

        if notification_type == 'PJC Submit':
            message=' New PJC repair status has arrived'
            content = sender.first_name+ message
            title=' PJC Submit '
            receivers = User.query.filter(User.roles=='{6}',User.isActive==1).all()

        if notification_type == 'PDC Approve':
            # message=' New PDC repair status has arrived'
            content = ' New PDC repair status has arrived'
            title=' PDC Approve '
            receivers = User.query.filter(User.roles=='{6}',User.isActive==1).all()

        if notification_type == 'Document Upload':
            message=' Document Upload'
            content = sender.first_name+ message
            title=' Document Upload '
            receivers = User.query.filter(User.roles=='{9}',User.isActive==1).all()

        if notification_type == 'Leave Request':
            message=' has requested for leave'

            content = sender.first_name+ message
            title=' Leave Request '
            receivers = User.query.filter(User.roles=='{9}',User.isActive==1).all()

        if notification_type == 'Leave Approve1':
            message=' Leave Approve'
            content = sender.first_name+ message
            title=' Leave Approve '
            if is_web==1:
                message = ' has requested for leave'
                content = sender.first_name + message
                title = ' HR Leave Request '
                receivers = User.query.filter(User.roles=='{2}',User.isActive==1).all()
            else:
                receivers = User.query.join(Device,Device.id==User.device_table_id).add_columns(User.id,Device.notification_token).filter(User.id==to_user,User.isActive==1).all()

        if notification_type == 'Leave Approve2':
            message = ' Leave Approve'
            content = sender.first_name + message
            title = ' Leave Approve '
            receivers = User.query.join(Device, Device.id == User.device_table_id).add_columns(User.id,
                Device.notification_token).filter(User.id == to_user, User.isActive == 1).all()

        if notification_type == 'Leave Reject':
            message=' Leave Reject'
            content = sender.first_name + message
            title=' Leave Reject '
            if to_user=='OPERATION':
                message = ' Leave Rejected By Operator'
                receivers = User.query.filter(User.roles == '{9}', User.isActive == 1).all()
            elif to_user=='HR':
                message = ' Leave Rejected By HR'
                receivers = User.query.filter(User.roles=='{2}',User.isActive==1).all()
            else:
                receivers = User.query.join(Device,Device.id==User.device_table_id).add_columns(User.id,Device.notification_token).filter(User.id==to_user,User.isActive==1).all()

        if notification_type == 'Schedule Add':
            message = ' has Added a Schedule'
            content = sender.first_name + message
            title = ' Schedule Add '
            receivers = User.query.join(Device, Device.id == User.device_table_id).add_columns(User.id,
                Device.notification_token).filter(User.id == to_user, User.isActive == 1).all()

        url = 'https://fcm.googleapis.com/fcm/send'
        for item in receivers:
            insert_id=insert_notifiction(0,1,content,from_user,item.id,is_web,title,table_name,table_detail_id)
            if is_web==0:
                payload = {"to": item.notification_token,
                           "priority": "normal",
                           "delay_while_idle": True,
                           "dry_run": False,
                           "time_to_live": 3600,
                           "content_available": True,
                           "notification": {
                               "title": title,
                               "body": content,
                               "mutable_content": True,
                               "sound": "Tri-tone",
                               "badge": 1,
                               "click_action": "FCM_PLUGIN_ACTIVITY"
                           },
                           "data": {
                               "url": "https://localhost:5000/user/get_profile_image/0",
                               "dl": title
                           }
                           }
                headers = {
                    "content-type": "application/json",
                    "Authorization": "key="+config.fcm_key
                }
                r = requests.post(url, data=json.dumps(payload), headers=headers)
                encoding = 'utf-8'
                responsedata = json.loads(r.content.decode(encoding))
                status=-1
                if responsedata=="success":
                    status=2
                insert_notifiction(insert_id, status, content, from_user, item.id, is_web,notification_type,table_name,table_detail_id)

    except Exception as e:
        print(e)

def send_notification_new(data):
    try:
        sender = User.query.filter(User.id == data['from_user'], User.isActive == 1).first()
        receivers=[]

        if data['notification_type']==1:
            content=str(sender.rkp_name) +' has submitted PDC'
            title='PDC Request'
            receivers = User.query.join(Device,Device.id==User.device_table_id).add_columns(User.id,Device.notification_token).filter(User.roles=='{10}',User.isActive==1).all()

        if data['notification_type'] == 2:
            message=' has approved your PDC'
            if data['approve_status']==-1:
                message =' has rejected your PDC '
            content = str(sender.rkp_name) + str(message)
            title='Approval Status'
            receivers = User.query.join(Device,Device.id==User.device_table_id).add_columns(User.id,Device.notification_token).filter(User.id==data['to_user'],User.isActive==1).all()

        if data['notification_type'] == 'PJC Submit':
            message=' New PJC repair status has arrived '
            content = str(sender.rkp_name) + str(message)
            title=' PJC Submit '
            receivers = User.query.filter(User.roles=='{6}',User.isActive==1).all()

        if data['notification_type'] == 'PDC Approve':
            # message=' New PDC repair status has arrived'
            content = ' New PDC repair status has arrived'
            title=' PDC Approve '
            receivers = User.query.filter(User.roles=='{6}',User.isActive==1).all()

        if data['notification_type'] == 'Document Upload':
            message=' Document Upload '
            content = str(sender.rkp_name) + str(message)
            title=' Document Upload '
            receivers = User.query.filter(User.roles=='{9}',User.isActive==1).all()

        if data['notification_type'] == 'Leave Request':
            message=' has requested for leave '

            content = str(sender.rkp_name) + str(message)
            title=' Leave Request '
            receivers = User.query.filter(User.roles=='{9}',User.isActive==1).all()

        if data['notification_type'] == 'Leave Approve1 ':
            message=' Leave Approve'
            content = str(sender.rkp_name) + str(message)
            title=' Leave Approve '
            if data['is_web']==1:
                message = ' has requested for leave '
                content = str(sender.rkp_name) + str(message)
                title = ' HR Leave Request '
                receivers = User.query.filter(User.roles=='{2}',User.isActive==1).all()
            else:
                receivers = User.query.join(Device,Device.id==User.device_table_id).add_columns(User.id,Device.notification_token).filter(User.id==data['to_user'],User.isActive==1).all()

        if data['notification_type'] == 'Leave Approve2':
            message = ' Leave Approve'
            content = str(sender.rkp_name) + str(message)
            title = ' Leave Approve '
            receivers = User.query.join(Device, Device.id == User.device_table_id).add_columns(User.id,
                Device.notification_token).filter(User.id == data['to_user'], User.isActive == 1).all()

        if data['notification_type'] == 'Leave Reject':
            message = ' Leave Reject '
            content = str(sender.rkp_name)  + message
            title = ' Leave Reject '
            if data['to_user'] == 'OPERATION':
                message = ' Leave Rejected By Operator. '+data['content']
                content = str(sender.rkp_name) + message
                receivers = User.query.filter(User.roles == '{9}', User.isActive == 1).all()
            elif data['to_user'] == 'HR':
                message = ' Leave Rejected By HR. '+data['content']
                content = str(sender.rkp_name) + message
                receivers = User.query.filter(User.roles == '{2}', User.isActive == 1).all()
            else:
                receivers = User.query.join(Device,Device.id==User.device_table_id).add_columns(User.id,Device.notification_token).filter(User.id==data['to_user'],User.isActive==1).all()

        if data['notification_type'] == 'Schedule Add':
            message = ' has Added a Schedule'
            content = str(sender.rkp_name) + message
            title = ' Schedule Add '
            receivers = User.query.join(Device, Device.id == User.device_table_id).add_columns(User.id,
                Device.notification_token).filter(User.id == data['to_user'], User.isActive == 1).all()

        url = 'https://fcm.googleapis.com/fcm/send'
        for item in receivers:
            insert_id=insert_notifiction(0,1,content,data['from_user'],item.id,data['is_web'],title,data['table_name'],data['table_detail_id'])
            if data['is_web']==0:
                payload = {"to": item.notification_token,
                           "priority": "normal",
                           "delay_while_idle": True,
                           "dry_run": False,
                           "time_to_live": 3600,
                           "content_available": True,
                           "notification": {
                               "title": title,
                               "body": content,
                               "mutable_content": True,
                               "sound": "Tri-tone",
                               "badge": 1,
                               "click_action": "FCM_PLUGIN_ACTIVITY"
                           },
                           "data": {
                               "url": "https://localhost:5000/user/get_profile_image/0",
                               "dl": title
                           }
                           }
                headers = {
                    "content-type": "application/json",
                    "Authorization": "key="+config.fcm_key
                }
                r = requests.post(url, data=json.dumps(payload), headers=headers)
                encoding = 'utf-8'
                responsedata = json.loads(r.content.decode(encoding))
                status=-1
                if responsedata=="success":
                    status=2
                insert_notifiction(insert_id, status, content, data['from_user'], item.id, data['is_web'],data['notification_type'],data['table_name'],data['table_detail_id'])

    except Exception as e:
        print(e)

def insert_notifiction(id,status,content,from_user,to_user,is_web,notification_type,table_name,table_detail_id):
    try:
        if table_detail_id == '':
            table_detail_id = 0
        if id==0:
            new_notification=Notification(
                to=to_user,
                from_user=from_user,
                isSent= status if is_web==0 else 2,
                body=content,
                is_web=is_web,
                isViewed=0,
                notification_type = notification_type,
                table_name = table_name,
                table_detail_id = table_detail_id,
                created_date=datetime.datetime.utcnow(),
                isactive=1
            )
            save_changes(new_notification)
        else:
            new_notification=Notification.query.filter(Notification.id==id).first()
            new_notification.isSent=2

        return new_notification.id
    except Exception as e:
        print(e)
def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        print(e)
        print('Handling run-time error:')