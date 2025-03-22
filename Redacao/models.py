from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)

    password_hash = db.Column(db.Text, nullable=False)


    credits = db.Column(db.Integer, default=1)  # Inicia com 1 crédito
    
    essays = db.relationship('Essay', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Essay(db.Model):
    __tablename__ = 'essays'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    text = db.Column(db.Text, nullable=False)
    feedback = db.Column(db.JSON, nullable=True)  # Armazena feedback em formato JSON
    score_total = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Notas por competência (0-200)
    comp1_score = db.Column(db.Integer, nullable=True)
    comp2_score = db.Column(db.Integer, nullable=True)
    comp3_score = db.Column(db.Integer, nullable=True)
    comp4_score = db.Column(db.Integer, nullable=True)
    comp5_score = db.Column(db.Integer, nullable=True)
