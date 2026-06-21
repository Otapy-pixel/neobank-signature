import psycopg2_binary as psycopg2
import sys
sys.modules['psycopg2'] = psycopg2

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
import secrets
from datetime import datetime

app = Flask(__name__)

db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float, default=1000.0)
    token = db.Column(db.String(255), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def generate_token(self):
        self.token = secrets.token_hex(32)
        return self.token

@app.route('/')
def hello():
    return jsonify({"status": "OK", "message": "Neobank Signature API"})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email + password requis"}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email déjà utilisé"}), 400
    
    new_user = User(email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "Compte créé", "id": new_user.id, "balance": new_user.balance}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({"error": "Email ou password invalide"}), 401
    
    token = user.generate_token()
    db.session.commit()
    
    return jsonify({"message": "Connecté", "token": token, "balance": user.balance})

def get_user_by_token(token):
    return User.query.filter_by(token=token).first()

@app.route('/balance', methods=['GET'])
def balance():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Token manquant"}), 401
    
    user = get_user_by_token(token)
    if not user:
        return jsonify({"error": "Token invalide"}), 401
    
    return jsonify({"email": user.email, "balance": user.balance})

@app.route('/transfer', methods=['POST'])
def transfer():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Token manquant"}), 401
    
    sender = get_user_by_token(token)
    if not sender:
        return jsonify({"error": "Token invalide"}), 401
    
    data = request.get_json()
    receiver_email = data.get('to_email')
    amount = float(data.get('amount', 0))
    
    if amount <= 0:
        return jsonify({"error": "Montant invalide"}), 400
    
    if sender.balance < amount:
        return jsonify({"error": "Solde insuffisant"}), 400
    
    receiver = User.query.filter_by(email=receiver_email).first()
    if not receiver:
        return jsonify({"error": "Destinataire introuvable"}), 404
    
    sender.balance -= amount
    receiver.balance += amount
    db.session.commit()
    
    return jsonify({
        "message": "Virement effectué",
        "sent": amount,
        "to": receiver_email,
        "your_new_balance": sender.balance
    })

with app.app_context():
    db.create_all()
