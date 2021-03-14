from app.cura import db
import datetime


class RKPDisciplinary(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tbl_rkp_disciplinary"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=True)
    violation_date = db.Column(db.DateTime, nullable=True)
    rt_number = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    client_name = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
