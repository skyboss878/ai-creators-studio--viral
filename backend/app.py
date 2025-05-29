from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)
# Load your OpenAI key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime, timedelta

@app.route('/api/paypal/webhook', methods=['POST'])
def paypal_webhook():
    try:
        data = request.get_json()
        subscription_id = data.get('subscriptionID')

        if not subscription_id:
            return jsonify({'error': 'Missing subscription ID'}), 400

        # Optional: Authenticate the request with a shared secret or token

        # Here’s how you might handle the subscription:
        # For demo: just store in a user record manually
        # In production: you’d verify with PayPal API using client_id & secret

        # Example: look up the latest user (You should really tie this to a logged-in user or token)
        user = User.query.order_by(User.id.desc()).first()  # Placeholder

        if user:
            user.subscription_type = 'premium'
            user.subscription_ends = datetime.utcnow() + timedelta(days=30)  # 1-month sub
            db.session.commit()
            return jsonify({'success': True, 'message': 'Subscription activated'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/')
def home():
    return jsonify({"message": "AI Creators Studio backend is running."})

@app.route('/generate_caption', methods=['POST'])
def generate_caption():
    data = request.get_json()
    topic = data.get('topic', '')
    prompt = f"Write a short, viral caption for a video about: {topic}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        caption = response.choices[0].message['content'].strip()
        return jsonify({'caption': caption})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_hashtags', methods=['POST'])
def generate_hashtags():
    data = request.get_json()
    topic = data.get('topic', '')
    prompt = f"Generate 10 viral, trending hashtags for: {topic}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        hashtags = response.choices[0].message['content'].strip()
        return jsonify({'hashtags': hashtags})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_music', methods=['POST'])
def generate_music():
    # Simulate music track selection for now
    topic = request.get_json().get('topic', '')
    tracks = [
        "Upbeat Pop - Royalty Free",
        "Trap Bass Energy",
        "Epic Build-Up",
        "Lo-Fi Chill Vibes",
        "Fast-Paced EDM Drop"
    ]
    return jsonify({'tracks': tracks})

@app.route('/generate_video', methods=['POST'])
def generate_video():
    data = request.get_json()
    topic = data.get('topic', '')
    return jsonify({
        "message": f"Simulated video generated for: {topic}",
        "download_url": f"https://cdn.fakevideo.ai/{topic.replace(' ', '_')}.mp4"
    })
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "AI Creators Studio backend is running!"})

if __name__ == '__main__':
    app.run(debug=True)

