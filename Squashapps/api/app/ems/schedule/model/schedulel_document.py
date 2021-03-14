from app.cura import db
import datetime

class Schedule_Document(db.Model):
    __tablename__ = "tbl_schedule_document"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_path = db.Column(db.String(500), nullable=True)
    original_file_name = db.Column(db.String(100), nullable=True)
    uuid_file_name = db.Column(db.String(500), nullable=True)
    document_status = db.Column(db.DECIMAL(2,2), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)