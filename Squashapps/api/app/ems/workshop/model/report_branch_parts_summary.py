from sqlalchemy import DECIMAL

from app.cura import db
import datetime


class ReportBranchPartsSummary(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblReportBranchPartsSummary"
    report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    report_date = db.Column(db.DateTime, nullable=True)
    branch_id = db.Column(db.Integer, nullable=True)
    branch_type = db.Column(db.DECIMAL(4, 2), nullable=True)
    description = db.Column(db.String(250), nullable=True)
    payment = db.Column(db.DECIMAL(12, 2), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
