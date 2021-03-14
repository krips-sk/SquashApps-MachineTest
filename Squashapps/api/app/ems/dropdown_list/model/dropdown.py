from app.cura import db
import datetime
from sqlalchemy.dialects.postgresql import JSONB


class DropdownList(db.Model):
    """ Dropdown Model for storing dropdown related details """
    __tablename__ = "tbldropdown"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key_id = db.Column(db.String(100), nullable=True)
    key_value_en = db.Column(db.String(250), nullable=True)
    key_value_ma = db.Column(db.String(250), nullable=True)
    type = db.Column(db.String(50), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isactive = db.Column(db.Integer, nullable=True, default=1)
