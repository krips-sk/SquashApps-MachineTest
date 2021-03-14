from app.cura import db
import datetime
from sqlalchemy import DECIMAL


class InspectionItem(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblInspectionItem"
    inspection_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reference_id = db.Column(db.Integer, nullable=True)
    # 1 - PDC
    # 2 - PJC
    # 3 - SCHEDULED MAINTENANCE
    # 4 - AD HOC
    # 5 -  BREAKDOWN
    inspection_type = db.Column(db.Integer, nullable=True)
    checklist_id = db.Column(db.Integer, nullable=True)
    findings = db.Column(db.String(250), nullable=True)
    inspection_status = db.Column(db.DECIMAL(4, 2), nullable=True)
    approval_category = db.Column(db.Integer, nullable=True)

    # workshop related changes
    supervisor = db.Column(db.String(250), nullable=True)
    mechanic = db.Column(db.String(250), nullable=True)
    inspections_defects = db.Column(db.String(250), nullable=True)
    technician_remarks = db.Column(db.String(250), nullable=True)  # or Workshop Actions
    workshop_status = db.Column(db.DECIMAL(4, 2), nullable=True)
    date_in = db.Column(db.DateTime, nullable=True)
    date_out = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
