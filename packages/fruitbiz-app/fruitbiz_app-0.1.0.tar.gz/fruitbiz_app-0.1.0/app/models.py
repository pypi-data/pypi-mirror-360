from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class FarmerPurchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_name = db.Column(db.String(100), nullable=False)
    fruit_name = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, default=datetime.now())
    vehicle_no = db.Column(db.String(20))
    village = db.Column(db.String(100))
    total_lungar = db.Column(db.Integer)
    notes = db.Column(db.Text)
    board_no = db.Column(db.String(20))
    quality = db.Column(db.String(50))
    bill_no = db.Column(db.Integer, unique=True, index=True)


class SellerSale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_name = db.Column(db.String(100), nullable=False)
    quality = db.Column(db.String(100))
    weight = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    commission_rate = db.Column(db.Float, default=0)
    total_commission = db.Column(db.Float, nullable=True)
    labour_charge = db.Column(db.Float, default=0)
    mandi_charge = db.Column(db.Float, default=0)
    tax = db.Column(db.Float, default=0)
    total_price = db.Column(db.Float)
    date = db.Column(db.Date, default=datetime.now())