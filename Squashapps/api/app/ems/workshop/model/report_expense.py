from sqlalchemy import DECIMAL

from app.cura import db
import datetime


class ReportExpense(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblReportExpense"
    report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    report_date = db.Column(db.DateTime, nullable=True)
    rt_regn = db.Column(db.String(250), nullable=True)
    repair_cost = db.Column(db.DECIMAL(12, 2), nullable=True)
    new_tyre = db.Column(db.DECIMAL(12, 2), nullable=True)
    recamic_tyre = db.Column(db.DECIMAL(12, 2), nullable=True)
    battery = db.Column(db.DECIMAL(12, 2), nullable=True)
    lube = db.Column(db.DECIMAL(12, 2), nullable=True)
    spare_battery_lube = db.Column(db.DECIMAL(12, 2), nullable=True)
    total_from_irs = db.Column(db.DECIMAL(12, 2), nullable=True)
    remarks = db.Column(db.String(250), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
