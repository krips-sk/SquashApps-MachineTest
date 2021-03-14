from sqlalchemy import DECIMAL

from app.cura import db
import datetime


class WorkshopWorkAction(db.Model):
    """ Workshop Work Action Model for storing user related details """
    __tablename__ = "tblWorkshopWorkAction"
    action_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pdcregistration_reference_id = db.Column(db.Integer)
    inspection_reference_id = db.Column(db.Integer)
    regn_no = db.Column(db.String(250), nullable=True)
    description = db.Column(db.String(250), nullable=True)
    status = db.Column(db.String(250), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
