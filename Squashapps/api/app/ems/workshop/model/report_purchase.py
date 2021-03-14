from sqlalchemy import DECIMAL

from app.cura import db
import datetime


class ReportWorkshopPurchase(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblReportWorkshopPurchase"
    report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    report_date = db.Column(db.DateTime, nullable=True)
    supplier_id = db.Column(db.Integer, nullable=True)
    payment = db.Column(db.DECIMAL(12, 2), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
