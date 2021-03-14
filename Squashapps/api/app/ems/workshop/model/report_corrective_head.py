from sqlalchemy import DECIMAL

from app.cura import db
import datetime


class ReportCorrectiveHead(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblReportCorrectiveHead"
    report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    supplier_id = db.Column(db.Integer, nullable=True)
    report_date = db.Column(db.DateTime, nullable=True)
    department_id = db.Column(db.Integer, nullable=True)
    car_no = db.Column(db.String(250), nullable=True)
    quality = db.Column(db.Integer, nullable=True)
    environment = db.Column(db.Integer, nullable=True)
    safety = db.Column(db.Integer, nullable=True)
    health = db.Column(db.Integer, nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)