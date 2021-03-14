from app.cura import db
import datetime



class Email(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblemail"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(100))
    to = db.Column(db.String(300), nullable=True)
    fromemail = db.Column(db.String(300), nullable=True)
    isSent = db.Column(db.Integer, nullable=True)
    emailbody = db.Column(db.Text, nullable=True)
    ishtml= db.Column(db.Integer, nullable=True)
    referenceid= db.Column(db.Integer, nullable=True)
    referenceTable= db.Column(db.String(300), nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    created_by = db.Column(db.Integer, nullable=True)
    isactive = db.Column(db.Integer, nullable=True, default=1)

class ForgotPass(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblforgotpassword"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fid = db.Column(db.String(100), unique=True)
    public_id = db.Column(db.String(100))
    status = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    created_by = db.Column(db.Integer, nullable=True)
    isactive = db.Column(db.Integer, nullable=True, default=1)

class Notification(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tbl_notification"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    to = db.Column(db.String(300), nullable=True)
    from_user = db.Column(db.String(300), nullable=True)
    isSent = db.Column(db.Integer, nullable=True)
    body = db.Column(db.Text, nullable=True)
    is_web = db.Column(db.Integer, nullable=True)
    isViewed = db.Column(db.Integer, nullable=True)
    notification_type = db.Column(db.String(300), nullable=True)
    table_name = db.Column(db.String(300), nullable=True)
    table_detail_id = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    created_by = db.Column(db.Integer, nullable=True)
    isactive = db.Column(db.Integer, nullable=True, default=1)
