from flask import Blueprint, request, jsonify
from app.extensions import db, bcrypt
from app.models.user_model import User
from app.models.student_model import Student
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask import render_template

student_register_bp = Blueprint('student_register_bp', __name__, url_prefix='/api/students')

@student_register_bp.route('/register-form', methods=['GET'])
@jwt_required()
def show_student_form():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    return render_template('register_student.html')



@student_register_bp.route('/register-student', methods=['POST'])
@jwt_required()
def register_student():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
   # class_name = request.args.get('className')
    #if class_name:
     #   student = Student.query.filter_by(className=class_name).all()
    else:
        student = Student.query.all()

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error':'No json error'})
    try:
       
        user = User(
            phone=data.get('phone'),
            password=bcrypt.generate_password_hash(data.get('dob')).decode('utf-8'),
            role='student'
        )
        db.session.add(user)
        db.session.flush()

        # Create student profile
        student = Student(
            FullName=data.get('Fullname'),
            phone=data.get('phone'),
            dob=data.get('dob'),
            gender=data.get('gender'),
            idMark=data.get('idMark'),
            bloodGroup=data.get('bloodGroup'),
            admissionNo=data.get('admissionNo'),
            fatherName=data.get('fatherName'),
            occupation=data.get('occupation'),
            village=data.get('village'),
            po=data.get('po'),
            ps=data.get('ps'),
            pinCode=data.get('pinCode'),
            district=data.get('district'),
            state=data.get('state'),
            classname=data.get('classname'),
            user_id=user.id
        )
        db.session.add(student)
        db.session.commit()

        return jsonify({
            'message': 'Student registered successfully',
            'student_id': student.id,
            'phone': student.phone
        }), 201
    


    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
