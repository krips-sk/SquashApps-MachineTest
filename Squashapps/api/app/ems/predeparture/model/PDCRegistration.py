from app.cura import db
import datetime

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import DECIMAL


class PDCRegistration(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblPDCRegistration"
    pdc_registration_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=True)
    vehicle_id = db.Column(db.Integer, nullable=True)
    schedule_id = db.Column(db.Integer, nullable=True)
    rt_licence_number = db.Column(db.String(250), nullable=True)
    owner_name = db.Column(db.String(250), nullable=True)
    date_of_registartion = db.Column(db.DateTime, nullable=True)
    date_of_expiry = db.Column(db.DateTime, nullable=True)
    rt_location = db.Column(db.String(250), nullable=True)
    rt_category = db.Column(db.String(250), nullable=True)
    rt_load = db.Column(db.String(250), nullable=True)
    rt_type = db.Column(db.String(250), nullable=True)
    inspection_category = db.Column(db.Integer, nullable=True)
    inspection_notes = db.Column(db.String(250), nullable=True)
    # Here approval related changes
    # 0 - saved
    # 1 - submitted / pending
    # 2 - Approved
    # 3 - Rejected
    approval_status = db.Column(db.DECIMAL(4,2), nullable=True)
    approved_date = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.Integer, nullable=True)
    approval_notes = db.Column(db.String(250), nullable=True)
    # approval ends

    brake_lining_pad_thickness_pm = db.Column(JSONB, nullable=True)
    brake_lining_pad_thickness_trailer = db.Column(JSONB, nullable=True)
    clutch_Details_info = db.Column(JSONB, nullable=True)
    date_in = db.Column(db.DateTime, nullable=True)
    date_out = db.Column(db.DateTime, nullable=True)
    mechanic = db.Column(db.String(250), nullable=True)
    supervisor = db.Column(db.String(250), nullable=True)
    mileage = db.Column(db.String(250), nullable=True)
    next_due = db.Column(db.String(250), nullable=True)
    rt_regn = db.Column(db.String(250), nullable=True)
    trailer_regn = db.Column(db.String(250), nullable=True)
    remarks = db.Column(db.String(500), nullable=True)
    inspection_type= db.Column(db.Integer, nullable=True)
    repair_overhaul = db.Column(db.String(250), nullable=True)
    welding_shop = db.Column(db.String(250), nullable=True)
    tyre_shop = db.Column(db.String(250), nullable=True)
    completed_status = db.Column(db.DECIMAL(10, 1), nullable=True)

    is_acknowledged = db.Column(db.Boolean, nullable=True)
    acknowledged_date = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
