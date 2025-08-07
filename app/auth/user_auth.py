from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.user_model import User
from app.extensions import bcrypt,db


user_auth_bp = Blueprint('user_auth_bp', __name__, url_prefix='/api/users')

@user_auth_bp.route('/login2', methods=['POST'])
def user_login():
    data = request.get_json()
    phone = data.get('phone')
    dob = data.get('dob')  # Used as password

    user = User.query.filter_by(phone=phone).first()

    if user and user.role in ['student', 'teacher'] and bcrypt.check_password_hash(user.password, dob):
        token = create_access_token(identity={
            'id': user.id,
            'role': user.role,
            'username': user.username
        })
        return jsonify({"message": "Login successful", "role": user.role, "token": token}), 200

    return jsonify({"error": "Invalid credentials"}), 401

# ------------------DUMMYuser-------------

student_auth_bp = Blueprint('student_auth_bp', __name__, url_prefix='/api/students')

@student_auth_bp.route('/create-dummy-user', methods=['GET'])
def create_dummy_user():
    existing = User.query.filter_by(username='testuser').first()
    if existing:
        return jsonify({"message": "Dummy user already exists"}), 200

    hashed = bcrypt.generate_password_hash('testpass').decode('utf-8')
    dummy_user = User(username='testuser', password=hashed, role='student')
    db.session.add(dummy_user)
    db.session.commit()
    return jsonify({"message": "Dummy user created"}), 201