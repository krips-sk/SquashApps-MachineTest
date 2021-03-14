from app.cura import db
import datetime

class Medical_Claim(db.Model):
    __tablename__ = "tbl_medical_claim"
    claim_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=True)
    year = db.Column(db.String(100), nullable=True)
    claim_date = db.Column(db.DateTime, nullable=True)
    claim_type = db.Column(db.String(100), nullable=True)
    claim_amount = db.Column(db.DECIMAL(12,4), nullable=True)
    clinic_name = db.Column(db.String(500), nullable=True)
    ori_file_name = db.Column(db.String(500), nullable=True)
    uuid_file_name = db.Column(db.String(500), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)