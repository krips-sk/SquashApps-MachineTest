from app.cura import db
import datetime


class RoleMenu(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblRoleMenu"

    role_menu_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, nullable=True)
    menu_id = db.Column(db.Integer, nullable=True)
    is_view = db.Column(db.Integer, nullable=True)
    is_add = db.Column(db.Integer, nullable=True)
    is_edit = db.Column(db.Integer, nullable=True)
    is_delete = db.Column(db.Integer, nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
