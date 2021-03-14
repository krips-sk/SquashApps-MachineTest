from app.cura import db
import datetime

class Legal_Document(db.Model):
    __tablename__ = "tbl_legal_document"
    document_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=True)
    document_type = db.Column(db.String(500), nullable=True)
    notice_content = db.Column(db.String(1000), nullable=True)
    original_file_name =db.Column(db.String(500), nullable=True)
    uuid_file_name = db.Column(db.String(500), nullable=True)
    document_status = db.Column(db.DECIMAL(4,2), nullable=True)
    # Here approval related changes
    approval_status = db.Column(db.DECIMAL(4, 2), nullable=True)
    approved_date = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.Integer, nullable=True)
    approval_notes = db.Column(db.String(250), nullable=True)
    # approval ends
    is_viewed = db.Column(db.Integer, nullable=True)
    last_upload_date = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)