import logging
import smtplib
from app.cura import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
import requests
import json
from datetime import datetime


#
# feat Generic method to send the email for Kiah
#
def send_email(data, template, subject):
    try:
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = config.from_email
        message["To"] = data['email']
        message.attach(MIMEText(template, 'html'))
        text = message.as_string()
        mailServer = smtplib.SMTP(config.SMTP_Config, 587)
        # mailServer = smtplib.SMTP_SSL(SMTP_Config, 465)
        # mailServer.set_debuglevel(True)
        mailServer.starttls()
        mailServer.login(config.noreply_email_config['send_mail_login'],
                         config.noreply_email_config['send_mail_password'])
        mailServer.sendmail(config.from_email, data['email'], text)
        mailServer.quit()
        return 1
    except Exception as e:
        logging.exception("mail config error: " + e)
        print(e)
        return -1


#
# feat Generic method to convert base64 image to file
#
def save_base64_image_tofile(data, location):
    try:
        imagedata = data.split("base64,")[1]
        fh = open(location, "wb")
        fh.write(base64.b64decode(imagedata))
        fh.close()
        return 1
    except Exception as e:
        logging.exception("base64 conversion error: " + e)
        print(e)
        return -1


#
# feat Generic method to convert file to base64 image
#
def getbase64image(imagepath):
    try:
        with open(imagepath, "rb") as img_file:
            my_string = base64.b64encode(img_file.read())
        return my_string.decode('utf-8')
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')


#
# Feat   Used to convert the string to date
#
def convertdmy_to_date(strdate):
    try:
        return datetime.strptime(strdate, "%d/%m/%Y") if strdate else ""
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')


#
# Feat   Used to convert the string to date
#
def convertdmy_to_date2(strdate):
    try:
        strdate = strdate.replace(".", "-").replace("/", "-")
        return datetime.strptime(strdate, "%d-%m-%Y") if strdate else ""
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')

def convertdmy_to_date3(strdate):
    try:
        strdate = strdate.replace(".", "-").replace("/", "-")
        return datetime.strptime(strdate, "%d-%m-%Y %H:%M:%S") if strdate else ""
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')


def get_date_difference(source_date, dest_date=datetime.now()):
    if isinstance(source_date, str):
        source_date = datetime.strptime(source_date, "%Y-%m-%d %H:%M:%S")
    if source_date and dest_date:
        delta = source_date - dest_date
        return delta.days


#
# Feat   Used to convert the string to date
#
def convert_sql_strformat(date):
    try:
        return datetime.strftime(date, "%Y-%m-%d") if date else ""
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')


def hasNumbers(inputString):
    try:
        return any(char.isdigit() for char in inputString)
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')


#
# Feat   Used to convert the string to date and time
#
def convert_sql_str_format_time(date):
    try:
        return datetime.strptime(date, "%Y-%m-%d %H:%M:%S") if date else ""
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')


#
#   Used to shortern the URL using Google.
#
def goo_shorten_url(url):
    try:
        payload = config.Google_Short_Link_Payload.replace('##URL##', url)
        headers = {'content-type': 'application/json'}
        r = requests.post(config.Google_Short_Link_URL, data=payload, headers=headers)
        rsp = r.text if r.status_code == 200 else ""
        if rsp == '':
            return ''
        else:
            robj = json.loads(rsp)
            return robj.get('shortLink', '')
    except Exception as e:
        logging.exception(e)
        print(e)
        print('Handling run-time error:')
        return ""
