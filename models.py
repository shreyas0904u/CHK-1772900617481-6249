from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Gamification Stats
    points = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)
    last_login = db.Column(db.String(20), nullable=True) # YYYY-MM-DD format for easy streak logic
    certificates = db.Column(db.Text, default='[]') # JSON string of unlocked certs

    def get_certificates(self):
        try:
            return json.loads(self.certificates)
        except:
            return []

    def add_certificate(self, cert_name):
        certs = self.get_certificates()
        if cert_name not in certs:
            certs.append(cert_name)
            self.certificates = json.dumps(certs)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    amount_required = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
