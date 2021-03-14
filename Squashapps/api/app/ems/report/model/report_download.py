from app.cura import db
import datetime

class Report_Download(db.Model):
    __tablename__ = "tbl_report_downloads"
    download_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(100), nullable=True)
    type = db.Column(db.String(100), nullable=True)
    month = db.Column(db.String(100), nullable=True)
    year = db.Column(db.String(100), nullable=True)
    file_path = db.Column(db.String(500), nullable=True)
    status = db.Column(db.DECIMAL(10, 1), nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)