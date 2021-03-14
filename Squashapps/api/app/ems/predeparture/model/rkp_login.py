from app.cura import db
import datetime
from sqlalchemy import DECIMAL


class RKPLogin(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblRKP_login"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=True)
    user_pubic_id = db.Column(db.String(250), nullable=True)
    rt_status = db.Column(db.Integer, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    stoped_date = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)