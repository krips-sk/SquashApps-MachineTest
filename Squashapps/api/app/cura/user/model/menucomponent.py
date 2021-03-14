from app.cura import db
import datetime


class MenuComponent(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblMenuComponent"

    menu_component_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    component_name = db.Column(db.String(250), nullable=True)
    menu_id = db.Column(db.Integer, nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)