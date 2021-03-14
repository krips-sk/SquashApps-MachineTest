from sqlalchemy import DECIMAL

from app.cura import db
import datetime


class ReportTracker(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblReportTracker"
    report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    report_date = db.Column(db.DateTime, nullable=True)
    report_type = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Integer, nullable=True)
    org_filename = db.Column(db.String(250), nullable=True)
    uuid_filename = db.Column(db.String(250), nullable=True)
    full_path = db.Column(db.String(250), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
