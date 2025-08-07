from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from ..extensions import db, bcrypt
from app.models.user_model import User

# routes.py
admin_core_bp = Blueprint('admin_core_bp', __name__, url_prefix='/admin')
class_bp = Blueprint('class_bp', __name__, url_prefix='/api/classes')

@admin_core_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    phone = data.get('phone')
    password = data.get('password')

    user = User.query.filter_by(phone=phone, role='admin').first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity={'id': user.id, 'role': user.role})
        return jsonify({'token': access_token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

def create_default_admin():
    phone = '9999999999'
    if not User.query.filter_by(phone=phone).first():
        admin = User(
            username='admin',
            phone=phone,
            mobile='9999999999',
            role='admin',
            password=bcrypt.generate_password_hash('adminpass').decode('utf-8')
        )
        db.session.add(admin)
        db.session.commit()



@class_bp.route('/list', methods=['GET'])
def list_classes():
    classes = [
        {"id": 1, "name": "Class 1"},
        {"id": 2, "name": "Class 2"},
        {"id": 3, "name": "Class 3"}
    ]
    return jsonify({"classes": classes})