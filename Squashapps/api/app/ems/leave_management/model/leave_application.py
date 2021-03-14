from app.cura import db
import datetime

class Leave_Application(db.Model):
    __tablename__ = "tbl_leave_application"
    leave_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=True)
    from_date = db.Column(db.DateTime, nullable=True)
    to_date = db.Column(db.DateTime, nullable=True)
    days_of_leave = db.Column(db.String(500), nullable=True)
    leave_type = db.Column(db.String(500), nullable=True)
    status = db.Column(db.DECIMAL(10, 1), nullable=True)
    is_after_leave_taken =db.Column(db.Integer, nullable=True)
    file_path = db.Column(db.String(500), nullable=True)
    reason = db.Column(db.String(500), nullable=True)
    rejection_reason = db.Column(db.String(500), nullable=True)
    rejected_by = db.Column(db.String(500), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)