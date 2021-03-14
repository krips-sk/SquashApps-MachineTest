from app.cura import db
import datetime
from sqlalchemy.dialects.postgresql import JSONB
class Insurance(db.Model):
    __tablename__ = "tbl_insurance"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(255), nullable=False)
    vehicle_id = db.Column(db.Integer, nullable=True)
    policy =  db.Column(db.String(300), nullable=True)
    loc = db.Column(db.String(300), nullable=True)
    ref_no =  db.Column(db.String(300), nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    bank_or_insurer = db.Column(db.String(300), nullable=True)
    amount = db.Column(db.DECIMAL(12,4), nullable=True)
    remarks = db.Column(db.String(300), nullable=True)
    types = db.Column(db.String(300), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)