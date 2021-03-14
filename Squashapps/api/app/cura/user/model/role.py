from app.cura import db, flask_bcrypt
import datetime


class Role(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblrole"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_Id = db.Column(db.Integer, nullable=True)
    role_Name=db.Column(db.String(100), nullable=True)
    permission = db.Column(db.ARRAY(db.Integer), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)