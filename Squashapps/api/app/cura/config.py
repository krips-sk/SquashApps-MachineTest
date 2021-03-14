import os
import os.path
from elasticsearch import Elasticsearch

# uncomment the line below for postgres database url from environment variable
postgres_local_base = "postgresql://appuser:vgy7*uhb@103.160.144.108:5432/ems_stg"

es = Elasticsearch(['http://108.161.131.238:9200/'])

Python_Version = 'python'
host_url="http://localhost:8080/#/"
forgot_email_path = os.path.abspath(os.path.dirname("app/cura/emailTemplates/forgotpassword.html/"))
forgot_email_path_otp = os.path.abspath(os.path.dirname("app/cura/emailTemplates/forgotpassword_otp.html/"))
image_savedir = os.path.abspath(os.path.dirname("../uploads/profile_images/"))
profile_files = os.path.abspath(os.path.dirname("../uploads/profile_files/"))
disciplinary_files = os.path.abspath(os.path.dirname("../uploads/disciplinary_files/"))
pdf_path = os.path.abspath(os.path.dirname("../uploads/pdf/"))

default_profile="d010bc85-f42f-43e5-885f-a6e094f53174.jpeg"
from_email="celcomproject2019@gmail.com"
noreply_email_config = {("send_mail_login"):'dev@mycura.com',("send_mail_password"):"zse45rdx"}

logo_url = ""
host_url="http://localhost:8080/#/"
template_path=""
#   email configs
from_email="dev@mycura.com"
noreply_email="dev@mycura.com"
SMTP_Config="smtp.gmail.com"
noreply_email_config = {("send_mail_login"):'dev@mycura.com',("send_mail_password"):"zse45rdx"}
forgot_password_subject = 'Forgot Password - EMS'
fcm_key='AAAAPgXcDg0:APA91bGYSWsZ3u341dNEIHXkyNDO7Dc9jE6URb5UG_XtZna9ME0ZXmYCLD0Tbi05bR0FNhJztgO5G1UdOmcWWGgGc3l9qy0e969D9fpsqjo7vfEx58tvs1FbjUjGubSBSaCoxM461TiM'


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious_secret_key')
    DEBUG = False


class DevelopmentConfig(Config):
    # uncomment the line below to use postgres
    SQLALCHEMY_DATABASE_URI = postgres_local_base
    DEBUG = True
#    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'flask_boilerplate_main.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
  #  SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'flask_boilerplate_test.db')
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False
    # uncomment the line below to use postgres
    SQLALCHEMY_DATABASE_URI = postgres_local_base


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

key = Config.SECRET_KEY
