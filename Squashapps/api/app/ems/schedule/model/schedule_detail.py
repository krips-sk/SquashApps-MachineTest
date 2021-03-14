from app.cura import db
import datetime
from sqlalchemy import DECIMAL


class ScheduleDetail(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "tblScheduleDetail"
    schedule_detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=True)
    schedule_id = db.Column(db.Integer, nullable=True)
    document_id = db.Column(db.Integer, nullable=True)
    rt_regn = db.Column(db.String(250), nullable=True)
    shipment_no = db.Column(db.String(250), nullable=True)
    delivery_note_no = db.Column(db.String(250), nullable=True)
    client= db.Column(db.String(250), nullable=True)
    ship_to_party = db.Column(db.String(250), nullable=True)
    loc = db.Column(db.String(250), nullable=True)
    product = db.Column(db.String(250), nullable=True)
    dist = db.Column(db.DECIMAL(12, 2), nullable=True)
    payment = db.Column(db.DECIMAL(12, 2), nullable=True)
    schedule_category = db.Column(db.String(250), nullable=True)
    schedule_type = db.Column(db.String(250), nullable=True)
    qty = db.Column(db.DECIMAL(12, 2), nullable=True)
    pld_time = db.Column(db.String(250), nullable=True)
    rg = db.Column(db.String(250), nullable=True)

    plnt = db.Column(db.String(250), nullable=True)
    sc = db.Column(db.String(250), nullable=True)
    trans_pln_date = db.Column(db.DateTime, nullable=True)
    dlvr = db.Column(db.String(250), nullable=True)
    s = db.Column(db.String(250), nullable=True)
    t = db.Column(db.String(250), nullable=True)
    act_st_ldt = db.Column(db.String(250), nullable=True)
    maximum_volume = db.Column(db.String(250), nullable=True)
    eta_time= db.Column(db.String(250), nullable=True)
    sold_to= db.Column(db.String(250), nullable=True)
    shty= db.Column(db.String(250), nullable=True)

    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    updated_date = db.Column(db.DateTime, nullable=True, default=datetime.datetime.utcnow())
    isActive = db.Column(db.Integer, nullable=True, default=1)
