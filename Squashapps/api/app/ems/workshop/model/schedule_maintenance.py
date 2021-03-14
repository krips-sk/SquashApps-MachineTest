from app.cura import db
import datetime
from sqlalchemy import DECIMAL


class ScheduledMaintenance(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblScheduledMaintenance"
    scheduled_maintenance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_in = db.Column(db.DateTime, nullable=True)
    mechanic = db.Column(db.String(250), nullable=True)
    supervisor = db.Column(db.String(250), nullable=True)
    mileage = db.Column(db.String(250), nullable=True)
    next_due = db.Column(db.String(250), nullable=True)
    rt_regn = db.Column(db.String(250), nullable=True)
    trailer_regn = db.Column(db.String(250), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
