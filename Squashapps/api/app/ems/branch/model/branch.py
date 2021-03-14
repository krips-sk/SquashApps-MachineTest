from app.cura import db
import datetime
from sqlalchemy.dialects.postgresql import JSONB


class Branch(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblbranch"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(100), unique=True)
    branch_name = db.Column(db.String(250), nullable=True)
    branch_location = db.Column(db.String(250), nullable=True)
    contact_number = db.Column(db.String(20), nullable=True)
    email_id = db.Column(db.String(250), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isactive = db.Column(db.Integer, nullable=True, default=1)
