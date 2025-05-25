from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import random
import datetime

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a strong, random key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use SQLite for simplicity; consider PostgreSQL or MySQL for production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email Configuration (for OTP)
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587  # Or 465 for SSL
app.config['MAIL_USE_TLS'] = True  # Or False if using SSL
app.config['MAIL_USERNAME'] = 'your-email@example.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'your-email-password'  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@example.com'

db = SQLAlchemy(app)
mail = Mail(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Store hashed passwords
    is_verified = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.email}>'

class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    expiry = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(10), nullable=False) # e.g., 'signup', 'reset'

    def __repr__(self):
        return f'<OTP for {self.email}>'

# Helper Functions
def send_email(to, subject, body):
    """Sends an email using Flask-Mail."""
    msg = Message(subject, recipients=[to], body=body)
    try:
        mail.send(msg)
        print(f"Email sent to {to}")  # Keep this for debugging, but remove in production
    except Exception as e:
        print(f"Error sending email: {e}") # Log the error
        return False  # Indicate failure
    return True

def generate_otp():
    """Generates a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def validate_password(password):
    """
    Validates password strength.
    Returns True if the password is strong enough, False otherwise.
    """
    if len(password) < 8:
        return False
    # Add more checks as needed (e.g., for uppercase, lowercase, digits, special characters)
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(char in "!@#$%^&*()" for char in password) # Add more special characters
    return has_upper and has_lower and has_digit and has_special

# Routes

@app.route('/api/signup', methods=['POST'])
def signup():
    """Handles user signup."""
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # 1. Server-side validation
    if not name or not email or not password:
        return jsonify({'error': 'All fields are required.'}), 400
    if not validate_password(password):
        return jsonify({'error': 'Password must be at least 8 characters long and contain uppercase, lowercase, digits and special characters.'}), 400
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email): #Added regex
        return jsonify({'error': 'Invalid email address'}), 400

    # 2. Check if email exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already exists.'}), 409  # 409 Conflict

    # 3. Hash the password
    hashed_password = generate_password_hash(password)

    # 4. Create new user
    new_user = User(name=name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # 5. Generate and store OTP
    otp = generate_otp()
    otp_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    new_otp = OTP(email=email, otp=otp, expiry=otp_expiry, type='signup')
    db.session.add(new_otp)
    db.session.commit()

    # 6. Send OTP email
    if not send_email(email, 'Verify your email', f'Your OTP is: {otp}'):
        return jsonify({'error': 'Failed to send OTP. Please try again.'}), 500

    return jsonify({'message': 'OTP sent. Please verify your email.', 'email': email}), 200 #Do not return email in real app

import re
@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    """Handles OTP verification for signup."""
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    # 1. Validate
    if not email or not otp:
        return jsonify({'error': 'Email and OTP are required.'}), 400

    # 2. Retrieve the stored OTP
    otp_record = OTP.query.filter_by(email=email, otp=otp, type='signup').first()
    if not otp_record:
        return jsonify({'error': 'Invalid OTP.'}), 400

    # 3. Check if OTP has expired
    if otp_record.expiry < datetime.datetime.utcnow():
        db.session.delete(otp_record)
        db.session.commit()
        return jsonify({'error': 'OTP has expired.'}), 400

    # 4. Mark email as verified
    user = User.query.filter_by(email=email).first()
    user.is_verified = True
    db.session.delete(otp_record)  # Delete used OTP
    db.session.commit()

    return jsonify({'message': 'Email verified. Account created!'}), 200

@app.route('/api/login', methods=['POST'])
def login():
    """Handles user login."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # 1. Server-side validation
    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    # 2. Retrieve user from database
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid credentials.'}), 401  # 401 Unauthorized

    # 3. Check if the user is verified
    if not user.is_verified:
        return jsonify({'error': 'Email not verified.'}), 403  # 403 Forbidden

    # 4. Compare password
    if not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials.'}), 401

    # 5. Generate a token (simplified - replace with a proper JWT implementation)
    #  In a real application, use a library like PyJWT
    token = f'mock-token-{user.id}-{datetime.datetime.utcnow()}'
    return jsonify({'message': 'Login successful.', 'token': token}), 200

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """Handles forgot password requests."""
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email is required.'}), 400

    # 1. Check if email exists
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Email not found.'}), 404

    # 2. Generate and store OTP
    reset_otp = generate_otp()
    otp_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    new_otp = OTP(email=email, otp=reset_otp, expiry=otp_expiry, type='reset')
    db.session.add(new_otp)
    db.session.commit()

    # 3. Send OTP email
    if not send_email(email, 'Password Reset OTP', f'Your password reset OTP is: {reset_otp}'):
        return jsonify({'error': 'Failed to send OTP. Please try again.'}), 500

    return jsonify({'message': 'Password reset OTP sent.', 'email': email}), 200 #dont return email

@app.route('/api/verify-reset-otp', methods=['POST'])
def verify_reset_otp():
    """Handles OTP verification for password reset."""
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    # 1. Validate
    if not email or not otp:
        return jsonify({'error': 'Email and OTP are required.'}), 400

    # 2. Retrieve the stored OTP
    otp_record = OTP.query.filter_by(email=email, otp=otp, type='reset').first()
    if not otp_record:
        return jsonify({'error': 'Invalid OTP.'}), 400

    # 3. Check if OTP has expired
    if otp_record.expiry < datetime.datetime.utcnow():
        db.session.delete(otp_record)
        db.session.commit()
        return jsonify({'error': 'OTP has expired.'}), 400

    db.session.delete(otp_record)  # Delete used OTP
    db.session.commit()
    return jsonify({'message': 'OTP verified.'}), 200

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """Handles resetting the user's password."""
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('newPassword')

    # 1. Validate
    if not email or not new_password:
        return jsonify({'error': 'Email and new password are required.'}), 400
    if not validate_password(new_password):
        return jsonify({'error': 'Password must be at least 8 characters long and contain uppercase, lowercase, digits and special characters.'}), 400

    # 2. Hash the new password
    hashed_new_password = generate_password_hash(new_password)

    # 3. Update the user's password
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Email not found.'}), 404
    user.password = hashed_new_password
    db.session.commit()

    return jsonify({'message': 'Password reset successful.'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)  # Remove debug=True in production
