from app.cura import db
import datetime

class Medical_Claim_Summary(db.Model):
    __tablename__ = "tbl_medical_claim_summary"
    medical_summary_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=True)
    year = db.Column(db.String(100), nullable=True)
    entitle_claim = db.Column(db.DECIMAL(12,4), nullable=True)
    total_claim_medical = db.Column(db.DECIMAL(12, 4), nullable=True)
    total_claim_checkup = db.Column(db.DECIMAL(12, 4), nullable=True)
    balance_claim_medical = db.Column(db.DECIMAL(12, 4), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)