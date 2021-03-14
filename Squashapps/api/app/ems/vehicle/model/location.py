from app.cura import db
import datetime
from sqlalchemy.dialects.postgresql import JSONB
class Location(db.Model):
    __tablename__ = "tbl_location"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)