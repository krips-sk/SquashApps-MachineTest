from sqlalchemy import DECIMAL

from app.cura import db
import datetime


class ReportCorrectiveDetail(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblReportCorrectiveDetail"
    detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    head_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(250), nullable=True)
    part_no = db.Column(db.String(250), nullable=True)
    qty = db.Column(db.DECIMAL(12, 2), nullable=True)
    price = db.Column(db.DECIMAL(12, 2), nullable=True)
    total = db.Column(db.DECIMAL(12, 2), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
