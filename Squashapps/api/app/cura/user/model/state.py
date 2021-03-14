from app.cura import db, flask_bcrypt
import datetime


class States(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblstate"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    state_name = db.Column(db.String(250), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)