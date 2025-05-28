from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    subscription_type = db.Column(db.String(20), default='trial')
    trial_ends = db.Column(db.DateTime, nullable=False)
