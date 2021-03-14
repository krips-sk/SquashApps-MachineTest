from app.cura import db
import datetime
from sqlalchemy import DECIMAL


class PDCRegistrationInspection(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblPDCRegistrationInspection"
    pdc_registration_inspection_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pdc_registration_id = db.Column(db.Integer, nullable=True)
    checklist_id = db.Column(db.Integer, nullable=True)
    findings = db.Column(db.String(250), nullable=True)
    inspection_status = db.Column(db.DECIMAL(4,2), nullable=True)
    approval_category = db.Column(db.Integer, nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
