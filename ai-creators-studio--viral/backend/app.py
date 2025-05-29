from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
import requests
import json
from datetime import datetime, timedelta
import uuid
from PIL import Image
import io
import base64
import hashlib
import random
from werkzeug.utils import secure_filename
import hmac
import hashlib as hl

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///creators.db')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(128))
    subscription_type = db.Column(db.String(20), default='trial')
    trial_ends = db.Column(db.DateTime)
    subscription_ends = db.Column(db.DateTime)
    total_generations = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    stripe_customer_id = db.Column(db.String(100))
    paypal_subscription_id = db.Column(db.String(100))  # Add PayPal subscription ID here

class GeneratedContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_type = db.Column(db.String(20), default='video')
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    hashtags = db.Column(db.Text)  # JSON string
    music_track = db.Column(db.String(200))
    file_path = db.Column(db.String(255))
    thumbnail_path = db.Column(db.String(255))
    style = db.Column(db.String(50))
    platform = db.Column(db.String(50))
    has_watermark = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stripe_subscription_id = db.Column(db.String(100))
    paypal_subscription_id = db.Column(db.String(100))  # Added for PayPal
    status = db.Column(db.String(20))  # active, canceled, past_due
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ... [Your existing helper functions and API routes here, unchanged] ...



### PAYPAL SUBSCRIPTION INTEGRATION ###

# PAYPAL WEBHOOK VERIFY FUNCTION
def verify_paypal_webhook(req):
    """
    Verify PayPal webhook using transmission id, timestamp, webhook id, and transmission signature.
    For simplicity, this is a placeholder. 
    Ideally, verify with PayPal API endpoint /v1/notifications/verify-webhook-signature.
    """
    # In production, implement actual verification via PayPal API as per
    # https://developer.paypal.com/docs/api/webhooks/v1/#verify-webhook-signature_post
    # For now, assume valid for testing.
    return True

@app.route('/api/paypal-webhook', methods=['POST'])
def paypal_webhook():
    try:
        webhook_event = request.get_json()

        # Verify webhook authenticity - implement real verification for production!
        if not verify_paypal_webhook(request):
            return jsonify({'error': 'Invalid webhook signature'}), 400
        
        event_type = webhook_event.get('event_type')
        resource = webhook_event.get('resource', {})

        # Handle subscription activated or updated
        if event_type in ['BILLING.SUBSCRIPTION.ACTIVATED', 'BILLING.SUBSCRIPTION.UPDATED', 'BILLING.SUBSCRIPTION.RE-ACTIVATED']:
            subscription_id = resource.get('id')
            status = resource.get('status')
            subscriber_email = resource.get('subscriber', {}).get('email_address')

            # Find user by email
            user = User.query.filter_by(email=subscriber_email.lower()).first()
            if not user:
                return jsonify({'error': 'User not found for subscription'}), 404
            
            # Update user subscription info
            user.subscription_type = 'premium' if status == 'ACTIVE' else 'trial'
            user.subscription_ends = datetime.strptime(resource.get('billing_info', {}).get('next_billing_time', ''), '%Y-%m-%dT%H:%M:%SZ') if resource.get('billing_info', {}).get('next_billing_time') else None
            user.paypal_subscription_id = subscription_id

            # Update or create subscription record
            subscription = Subscription.query.filter_by(paypal_subscription_id=subscription_id).first()
            if not subscription:
                subscription = Subscription(user_id=user.id, paypal_subscription_id=subscription_id)
            subscription.status = status
            if resource.get('billing_info', {}).get('last_payment', {}).get('time'):
                subscription.current_period_start = datetime.strptime(resource['billing_info']['last_payment']['time'], '%Y-%m-%dT%H:%M:%SZ')
            if resource.get('billing_info', {}).get('next_billing_time'):
                subscription.current_period_end = datetime.strptime(resource['billing_info']['next_billing_time'], '%Y-%m-%dT%H:%M:%SZ')

            db.session.add(user)
            db.session.add(subscription)
            db.session.commit()

            return jsonify({'success': True, 'message': 'Subscription updated'}), 200
        
        elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
            subscription_id = resource.get('id')
            subscription = Subscription.query.filter_by(paypal_subscription_id=subscription_id).first()
            if subscription:
                subscription.status = 'CANCELLED'
                user = User.query.get(subscription.user_id)
                if user:
                    user.subscription_type = 'trial'
                    user.subscription_ends = None
                    user.paypal_subscription_id = None
                    db.session.add(user)
                db.session.add(subscription)
                db.session.commit()

            return jsonify({'success': True, 'message': 'Subscription cancelled'}), 200
        
        else:
            # For other events, just acknowledge
            return jsonify({'success': True, 'message': 'Event ignored'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Optional: Endpoint for frontend to check subscription status
@app.route('/api/subscription-status', methods=['GET'])
@jwt_required()
def subscription_status():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({
            'subscription_type': user.subscription_type,
            'subscription_ends': user.subscription_ends.isoformat() if user.subscription_ends else None,
            'paypal_subscription_id': user.paypal_subscription_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
