from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from datetime import datetime
from app.models.user_model import User
from app.models.teacher_model import Teacher
from ..extensions import jwt, bcrypt
from app.extensions import db
from app.models.Tattendence import Attendance


attendance_bp = Blueprint('attendance_bp', __name__)

@attendance_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username, role='admin').first()
    
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity={
            'id': user.id,
            'username': user.username,
            'role': user.role
        })
        return jsonify({'message': 'Login successful', 'access_token': access_token, 'role': user.role}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@attendance_bp.route('/admin/mark-attendance', methods=['POST'])
@jwt_required()
def mark_teacher_attendance():
    data = request.get_json()
    teacher_id = data['teacher_id']
    month = data['month']
    records = data['records']  # List of {"date": "2025-08-01", "status": "Present"}

    for record in records:
        attendance = attendance(
            teacher_id=teacher_id,
            date=datetime.strptime(record['date'], "%Y-%m-%d").date(),
            status=record['status'],
            month=month
        )
        db.session.add(attendance)
    db.session.commit()
    return jsonify({'message': 'Attendance marked successfully'})

    new_attendance = Attendance(
        teacher_id=teacher_id,
        attendance_date=today,
        status=status,
        marked_by=current_user['id']
    )
    db.session.add(new_attendance)
    db.session.commit()

    return jsonify({
        'message': 'Attendance marked successfully!',
        'teacher_name': teacher.name,
        'date': today,
        'status': status
    })

@attendance_bp.route('/teachers', methods=['GET'])
@jwt_required()
def get_all_teachers():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    teachers = Teacher.query.all()
    result = [{'id': t.id, 'name': t.name, 'mobile': t.mobile} for t in teachers]
    return jsonify({'teachers': result})

@attendance_bp.route('/attendance', methods=['GET'])
@jwt_required()
def get_attendance():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    date_filter = request.args.get('date')
    query = Attendance.query
    if date_filter:
        query = query.filter_by(attendance_date=date_filter)

    all_data = query.all()
    result = []
    for record in all_data:
        teacher = Teacher.query.get(record.teacher_id)
        marked_by = User.query.get(record.marked_by)
        result.append({
            'teacher_id': record.teacher_id,
            'teacher_name': teacher.name if teacher else 'Unknown',
            'date': record.attendance_date,
            'status': record.status,
            'marked_by': marked_by.username if marked_by else 'System'
        })
    return jsonify(result)
