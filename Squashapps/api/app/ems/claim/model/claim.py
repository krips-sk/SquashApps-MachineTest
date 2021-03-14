from app.cura import db
import datetime
from sqlalchemy.dialects.postgresql import JSONB


class Claim(db.Model):
    """ Payroll model related details """
    __tablename__ = "tblclaim"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=True)
    claim_no = db.Column(db.String(250), nullable=True)
    emp_id = db.Column(db.String(250), nullable=True)
    loc = db.Column(db.String(250), nullable=True)
    department = db.Column(db.String(250), nullable=True)
    claim_type = db.Column(db.String(250), nullable=True)
    claim_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.DECIMAL(12, 2), nullable=True)
    grand_total = db.Column(db.DECIMAL(12, 2), nullable=True)
    paid_date = db.Column(db.DateTime, nullable=True)

    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isactive = db.Column(db.Integer, nullable=True, default=1)
