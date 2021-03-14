from app.cura import db
import datetime

class Leave_Summary(db.Model):
    __tablename__ = "tbl_leave_summary"
    summary_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=True)
    year = db.Column(db.String(100), nullable=True)
    previous_year_balance = db.Column(db.Integer, nullable=True)
    leave_allocated = db.Column(db.Integer, nullable=True)
    annual_leave = db.Column(db.Integer, nullable=True)
    medical_leave_allocated = db.Column(db.Integer, nullable=True)
    medical_leave = db.Column(db.Integer, nullable=True)
    leave_others = db.Column(db.Integer, nullable=True)
    leave_taken = db.Column(db.DECIMAL(2,2), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)