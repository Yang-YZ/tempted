from flask import Flask, request, jsonify
from flask_cors import CORS
from models import init_db, User, Message
from scheduler import start_scheduler, process_emails
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, EMAIL_ADDRESS
import atexit

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize database
init_db()

# Start email scheduler
scheduler = start_scheduler()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route('/')
def index():
    """Health check endpoint."""
    return jsonify({
        'status': 'running',
        'message': 'Emotional Support Bot API'
    })


@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()

    # Validate required fields
    required_fields = ['email', 'name', 'occupation', 'interests', 'hobbies', 'personality']
    for field in required_fields:
        if field not in data or not data[field].strip():
            return jsonify({
                'success': False,
                'error': f'Missing required field: {field}'
            }), 400

    # Check if user already exists
    if User.exists(data['email']):
        return jsonify({
            'success': False,
            'error': 'Email already registered'
        }), 409

    # Create user
    success = User.create(
        email=data['email'].lower().strip(),
        name=data['name'].strip(),
        occupation=data['occupation'].strip(),
        interests=data['interests'].strip(),
        hobbies=data['hobbies'].strip(),
        personality=data['personality'].strip()
    )

    if success:
        return jsonify({
            'success': True,
            'message': f'Registration successful! You can now send emails to your support partner to start your conversation.'
        }), 201
    else:
        return jsonify({
            'success': False,
            'error': 'Registration failed'
        }), 500


@app.route('/api/user/<email>', methods=['GET'])
def get_user(email):
    """Get user information."""
    user = User.get(email.lower().strip())

    if user:
        return jsonify({
            'success': True,
            'user': user
        })
    else:
        return jsonify({
            'success': False,
            'error': 'User not found'
        }), 404


@app.route('/api/history/<email>', methods=['GET'])
def get_history(email):
    """Get conversation history for a user."""
    # Check if user exists
    if not User.exists(email.lower().strip()):
        return jsonify({
            'success': False,
            'error': 'User not found'
        }), 404

    # Get message history
    messages = Message.get_history(email.lower().strip())

    return jsonify({
        'success': True,
        'messages': messages
    })


@app.route('/api/check-emails', methods=['POST'])
def manual_email_check():
    """Manually trigger email check (for testing)."""
    try:
        process_emails()
        return jsonify({
            'success': True,
            'message': 'Email check completed'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("Emotional Support Bot - Backend Server")
    print(f"Server running on http://{FLASK_HOST}:{FLASK_PORT}")
    print(f"Bot email: {EMAIL_ADDRESS}")

    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)

