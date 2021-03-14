from app.cura import db
import datetime
from sqlalchemy import DECIMAL


class Checklist(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblChecklist"
    checklist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module = db.Column(db.Integer, nullable=True)
    sub_module = db.Column(db.Integer, nullable=True)
    zone = db.Column(db.Integer, nullable=True)
    item_description = db.Column(db.String(250), nullable=True)
    icon_name = db.Column(db.String(250), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
