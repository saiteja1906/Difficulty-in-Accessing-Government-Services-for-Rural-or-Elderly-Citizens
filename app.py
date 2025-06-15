from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from db import init_db, add_user, add_feedback, get_feedback, get_user, update_user_status
from services.intent_detection import detect_intent
from datetime import datetime, timedelta
import jwt
import os
from functools import wraps

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing
app.secret_key = 'super-secret-key-12345'  # Fixed secret key for session management
init_db()  # Initialize the database

# JWT token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token.split()[1], app.secret_key, algorithms=["HS256"])
            current_user = get_user(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register-user', methods=['POST'])
def register_user():
    """Register a new user."""
    try:
        data = request.json
        user_id = add_user(data['name'], data['age'], data['address'], data['phone'])
        return jsonify({"message": "User registered successfully!", "user_id": user_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/detect-intent', methods=['POST'])
def handle_intent():
    """Handle user query and detect intent."""
    try:
        query = request.json['query']
        response = detect_intent(query)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback."""
    try:
        data = request.json
        add_feedback(data['name'], data['rating'], data['comment'])
        return jsonify({"message": "Feedback submitted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/get-feedback', methods=['GET'])
def get_all_feedback():
    """Retrieve all feedback."""
    try:
        feedback = get_feedback()
        return jsonify(feedback)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/', methods=['GET'])
def root():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    try:
        if request.is_json:
            data = request.get_json()
            aadhaar = data.get('aadhaar')
            dob = data.get('dob')
        else:
            aadhaar = request.form.get('aadhaar')
            dob = request.form.get('dob')
        print(f"Login attempt: Aadhaar={aadhaar}, DOB={dob}")
        user = get_user(aadhaar, dob)
        print(f"User found: {user}")
        if user:
            token = jwt.encode({
                'user_id': str(user['id']),
                'exp': datetime.utcnow() + timedelta(days=1)
            }, app.secret_key)
            # If form, redirect to main page with session
            if not request.is_json:
                session['token'] = token
                session['user'] = {'name': user['name'], 'aadhaar': user['aadhaar']}
                return redirect(url_for('root'))
            # If API, return JSON
            return jsonify({
                'token': token,
                'user': {
                    'name': user['name'],
                    'aadhaar': user['aadhaar']
                }
            })
        error_msg = 'Invalid Aadhaar or Date of Birth'
        print(error_msg)
        if request.is_json:
            return jsonify({'error': error_msg}), 401
        return render_template('login.html', error=error_msg)
    except Exception as e:
        print(f"Login error: {e}")
        if request.is_json:
            return jsonify({'error': str(e)}), 400
        return render_template('login.html', error=str(e))

@app.route('/services', methods=['GET'])
@token_required
def get_services(current_user):
    """Get available government services."""
    services = [
        {
            'id': 'pension',
            'name': 'Pension Services',
            'description': 'Check pension status and apply for new pension',
            'requirements': ['Aadhaar Card', 'Bank Account']
        },
        {
            'id': 'ration',
            'name': 'Ration Card Services',
            'description': 'Apply for ration card or check status',
            'requirements': ['Aadhaar Card', 'Address Proof']
        },
        {
            'id': 'health',
            'name': 'Health Insurance',
            'description': 'Apply for health insurance schemes',
            'requirements': ['Aadhaar Card', 'Income Certificate']
        }
    ]
    return jsonify(services)

@app.route('/service-status/<service_id>', methods=['GET'])
@token_required
def get_service_status(current_user, service_id):
    """Get status of a specific service for the user."""
    try:
        status = update_user_status(current_user['id'], service_id)
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/apply-service', methods=['POST'])
@token_required
def apply_service(current_user):
    """Apply for a new government service."""
    try:
        data = request.json
        service_id = data['service_id']
        documents = data.get('documents', [])
        
        # Validate required documents
        required_docs = {
            'pension': ['aadhaar', 'bank_account'],
            'ration': ['aadhaar', 'address_proof'],
            'health': ['aadhaar', 'income_certificate']
        }
        
        if not all(doc in documents for doc in required_docs.get(service_id, [])):
            return jsonify({'error': 'Missing required documents'}), 400
            
        # Process application
        application_id = add_service_application(current_user['id'], service_id, documents)
        return jsonify({
            'message': 'Application submitted successfully',
            'application_id': application_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/chat', methods=['POST'])
@token_required
def handle_chat(current_user):
    """Handle chat messages with the virtual assistant."""
    try:
        message = request.json['message']
        response = detect_intent(message)
        
        # Store chat history
        add_chat_history(current_user['id'], message, response)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/accessibility', methods=['GET'])
def get_accessibility_options():
    """Get accessibility options for elderly users."""
    return jsonify({
        'font_size': ['normal', 'large', 'extra_large'],
        'contrast': ['normal', 'high'],
        'text_to_speech': True,
        'voice_input': True,
        'languages': ['English', 'Hindi', 'Telugu', 'Bengali', 'Tamil', 'Marathi', 'Gujarati', 'Kannada', 'Malayalam']
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
