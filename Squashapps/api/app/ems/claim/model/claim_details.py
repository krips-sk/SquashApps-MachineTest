from app.cura import db
import datetime
from sqlalchemy.dialects.postgresql import JSONB


class ClaimDetails(db.Model):
    """ Payroll model related details """
    __tablename__ = "tblclaim_details"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    claim_id = db.Column(db.Integer, nullable=True)
    item = db.Column(db.String(250), nullable=True)
    description = db.Column(db.String(250), nullable=True)
    company_name = db.Column(db.String(250), nullable=True)
    qty = db.Column(db.Integer, nullable=True)
    unit_price = db.Column(db.DECIMAL(12, 2), nullable=True)
    amount = db.Column(db.DECIMAL(12, 2), nullable=True)
    file_path = db.Column(db.String(250), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isactive = db.Column(db.Integer, nullable=True, default=1)
