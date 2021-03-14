from app.cura import db
import datetime
from sqlalchemy import DECIMAL


class AuditLog(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblAuditLog"
    audit_log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(250), nullable=True)
    sub_type = db.Column(db.String(250), nullable=True)
    details = db.Column(db.JSON, nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
