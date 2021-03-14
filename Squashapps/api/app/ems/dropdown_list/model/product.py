from app.cura import db
import datetime
from sqlalchemy.dialects.postgresql import JSONB


class Product(db.Model):
    """ Product Model for storing product related details """
    __tablename__ = "tblproduct"
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(250), nullable=True)
    product_value = db.Column(db.String(250), nullable=True)
    type = db.Column(db.String(50), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
