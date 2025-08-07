from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.student_model import Student  

student_dashboard_bp = Blueprint('student_dashboard_bp', __name__)

@student_dashboard_bp.route('/api/students/<int:id>', methods=['GET'])
@jwt_required()
def get_student(id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'student' or current_user['id'] != id:
        return jsonify({'error': 'Access denied'}), 403

    student_data = Student.query.get(id)
    if student_data:
        return jsonify({
            'name': student_data.name,
            'email': student_data.email,
            'phone_no': student_data.phone_no,
            'student_class': student_data.student_class,
            'DOB': student_data.DOB.strftime("%Y-%m-%d"),
            'admission_no': student_data.admission_no,
            'gender': student_data.gender,
            'id_mark': student_data.id_mark,
            'blood_group': student_data.blood_group,
            'village': student_data.village,
            'po': student_data.po,
            'ps': student_data.ps,
            'pin_code': student_data.pin_code,
            'district': student_data.district,
            'state': student_data.state
        })
    return jsonify({'error': 'Student not found'}), 404

@student_dashboard_bp.route('/api/students/register', methods=['POST'])
@jwt_required()
def register_student():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.json
    required_fields = ['name', 'phone_no', 'email', 'student_class', 'DOB', 'admission_no']
    if not all(data.get(f) for f in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    new_student = Student(
        name=data['name'],
        phone_no=data['phone_no'],
        email=data['email'],
        student_class=data['student_class'],
        DOB=data['DOB'],  
        admission_no=data['admission_no'],
        gender=data.get('gender', ''),
        id_mark=data.get('id_mark', ''),
        blood_group=data.get('blood_group', ''),
        village=data.get('village', ''),
        po=data.get('po', ''),
        ps=data.get('ps', ''),
        pin_code=data.get('pin_code', ''),
        district=data.get('district', ''),
        state=data.get('state', '')
    )

    db.session.add(new_student)
    db.session.commit()

    return jsonify({
        'message': 'Student registered successfully',
        'student_id': new_student.id,
        'admission_no': new_student.admission_no
    }), 201
