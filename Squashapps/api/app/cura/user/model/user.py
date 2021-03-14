from app.cura import db, flask_bcrypt
import datetime
from app.cura.config import key
import jwt
import logging
from sqlalchemy.dialects.postgresql import JSONB

class User(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tbluser"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id=db.Column(db.String(255), nullable=False)
    rkp_name = db.Column(db.String(255))
    employment_date = db.Column(db.DateTime, nullable=True)
    employment_status = db.Column(db.String(255))
    licence_expiry = db.Column(db.DateTime, nullable=True)
    licence_number = db.Column(db.String(255))
    gdl_expiry = db.Column(db.DateTime, nullable=True)
    melaka_port_expiry = db.Column(db.DateTime, nullable=True)
    licence_type = db.Column(db.String(255))
    blood_type = db.Column(db.String(255))

    location = db.Column(db.String(255))
    rkp_id_number = db.Column(db.String(255))
    rkp_ic_number = db.Column(db.String(255))
    phone_number = db.Column(db.String(255))
    medical_expiry = db.Column(db.DateTime, nullable=True)
    lpg_ptp_ogsp_expiry = db.Column(db.DateTime, nullable=True)
    remark = db.Column(db.TEXT, nullable=True)
    file_path =  db.Column(db.String(500))
    address1 = db.Column(db.String(255), nullable=True)
    address2 = db.Column(db.String(255), nullable=True)
    district = db.Column(db.String(255))
    state = db.Column(db.String(255))
    post_code = db.Column(db.String(255), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    user_status = db.Column(db.String(255), nullable=True)
    last_working_date = db.Column(db.DateTime, nullable=True)
    category = db.Column(db.String(255), nullable=True)
    capacity = db.Column(db.String(255), nullable=True)
    branch = db.Column(db.String(255), nullable=True)


    # old_columns
    email = db.Column(db.String(255), nullable=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    roles = db.Column(db.ARRAY(db.Integer), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.String(255), nullable=True)
    password_hash = db.Column(db.String(200))
    reg_no = db.Column(db.String(50))
    no_kp_baru = db.Column(db.String(50))
    join_date = db.Column(db.DateTime, nullable=True)
    no_tel = db.Column(db.String(255), nullable=True)
    license_expiry_date = db.Column(db.DateTime, nullable=True)
    gdl_expiry_date = db.Column(db.DateTime, nullable=True)
    no_lessen = db.Column(db.String(50), nullable=True)
    passport_expiry_date = db.Column(db.DateTime, nullable=True)
    base_pass_expiry_date = db.Column(db.DateTime, nullable=True)
    date_of_employment = db.Column(db.DateTime, nullable=True)
    lpg = db.Column(db.DateTime, nullable=True)
    medical_check_up = db.Column(db.DateTime, nullable=True)
    # remark = db.Column(db.TEXT, nullable=True)
    jenis_lesen = db.Column(db.String(50))
    # blood_type = db.Column(db.String(50))
    age = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50))
    latitude = db.Column(db.String(250), nullable=True)
    longitude = db.Column(db.String(250), nullable=True)
    lat_long_updated_date = db.Column(db.DateTime, nullable=True)
    device_table_id = db.Column(db.Integer, nullable=True)
    legal_doc = db.Column(db.Integer, nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)

    @property
    def password(self):
        try:
            raise AttributeError('password: write-only field')
        except Exception as e:
            print(e)
            print('Handling run-time error:')
    @password.setter
    def password(self, password):
        try:
            self.password_hash = flask_bcrypt.generate_password_hash(password).decode('utf-8')
        except Exception as e:
            print(e)
            print('Handling run-time error:')

    def check_password(self, password):
        try:
            logging.info("password : ")
            logging.info("sql password : " + password)
            return flask_bcrypt.check_password_hash(self.password_hash, password)
        except Exception as e:
            print(e)
            print('Handling run-time error:')

    @staticmethod
    def encode_auth_token(user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                key,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, key)
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    def __repr__(self):
        return "<User '{}'>".format(self.username)
