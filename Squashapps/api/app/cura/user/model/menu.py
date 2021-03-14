from app.cura import db
import datetime


class Menuitem(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblmenuitem"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    menu_name = db.Column(db.String(100), nullable=True)
    display_name = db.Column(db.String(100), nullable=True)
    order_no = db.Column(db.Integer, nullable=True)
    parent_id = db.Column(db.Integer, nullable=False)
    menu_code = db.Column(db.Integer, nullable=True)
    # 1 = Default menu,  2 = Sheet Menu, 3 = Country Menu
    submenu_type = db.Column(db.Integer, nullable=True, default=1)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
