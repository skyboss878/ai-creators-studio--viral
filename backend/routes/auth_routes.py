from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta
from models.user import User
from app import db

def register_auth_routes(app):

    @app.route('/api/signup', methods=['POST'])
    def signup():
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'User already exists'}), 400

        password_hash = generate_password_hash(password)
        user = User(
            email=email,
            name=name,
            password_hash=password_hash,
            trial_ends=datetime.utcnow() + timedelta(days=3)
        )

        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=user.id)

        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'subscription': user.subscription_type,
                'trial_ends': user.trial_ends.isoformat()
            }
        })

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid email or password'}), 401

        access_token = create_access_token(identity=user.id)

        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'subscription': user.subscription_type,
                'trial_ends': user.trial_ends.isoformat()
            }
        })
