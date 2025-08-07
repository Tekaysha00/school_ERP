from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..extensions import db, bcrypt
from app.models.teacher_model import Teacher
from app.models.user_model import User
from app.models.student_model import StudentAttendance
from app.models.student_model import Student
from app.models.assignment_model import Assignment
from app.models.Tattendence import Attendance
import os
from werkzeug.utils import secure_filename
from app.models.salary_model import Salary



teacher_bp_view = Blueprint('teacher_bp_view', __name__, url_prefix='/api/teachers')
UPLOAD_FOLDER = 'static/uploads'



@teacher_bp_view.route('/register', methods=['POST'])
def register_teacher():
    data = request.json
    mobile = data.get('mobile')
    password = data.get('password')

    if User.query.filter_by(mobile=mobile).first():
        return jsonify({'message': 'User already exists'}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=data.get('full_name'), mobile=mobile, password=hashed_pw, role='teacher')
    db.session.add(user)
    db.session.commit()

    teacher = Teacher(**data, user_id=user.id)
    db.session.add(teacher)
    db.session.commit()

    return jsonify({'message': 'Teacher registered successfully'}), 201

@teacher_bp_view.route('/login', methods=['POST'])
def teacher_login():
    data = request.json
    mobile = data.get('mobile')
    password = data.get('password')

    user = User.query.filter_by(mobile=mobile, role='teacher').first()
    if user and bcrypt.check_password_hash(user.password, password):
        token = create_access_token(identity={'id': user.id, 'role': user.role})
        return jsonify({'token': token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@teacher_bp_view.route('/<int:teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({'message': 'Teacher not found'}), 404

    return jsonify({
        'id': teacher.id,
        'full_name': teacher.full_name,
        'mobile': teacher.mobile,
        'District': teacher.District
    })

@teacher_bp_view.route('', methods=['GET'])
def get_all_teachers():
    teachers = Teacher.query.all()
    return jsonify([{
        'id': t.id,
        'full_name': t.full_name,
        'mobile': t.mobile,
        'District': t.District
    } for t in teachers])


@teacher_bp_view.route('/teacher/details/<int:teacher_id>', methods=['GET'])
@jwt_required()
def get_teacher_details(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"message": "Teacher not found"}), 404

    return jsonify({
        "name": teacher.name,
        "phone_primary": teacher.phone_primary,
        "phone_secondary": teacher.phone_secondary,
        "email": teacher.email,
        "dob": teacher.dob,
        "admission_no": teacher.admission_no,
        "gender": teacher.gender,
        "id_mark": teacher.id_mark,
        "blood_group": teacher.blood_group,
        "address": {
            "village": teacher.village,
            "post_office": teacher.post_office,
            "police_station": teacher.police_station,
            "pin_code": teacher.pin_code,
            "district": teacher.district,
            "state": teacher.state
        }
    })

@teacher_bp_view.route('/teacher/class-students', methods=['GET'])
@jwt_required()
def get_students_by_class():
    class_id = request.args.get('class_id')
    students = Student.query.filter_by(class_id=class_id).all()
    data = [{"id": s.id, "roll_no": s.roll_no, "name": s.name} for s in students]
    return jsonify(data)


@teacher_bp_view.route('/teacher/submit-attendance', methods=['POST'])
@jwt_required()
def submit_attendance():
    data = request.get_json()
    class_id = data.get('class_id')
    month = data.get('month')
    attendance_list = data.get('attendance')  # List of {"student_id": 1, "status": "Present"}

    for entry in attendance_list:
        record = StudentAttendance(
            student_id=entry['student_id'],
            class_id=class_id,
            month=month,
            status=entry['status']
        )
        db.session.add(record)
    db.session.commit()
    return jsonify({"message": "Attendance submitted successfully"})

#-------Assignment - upload -------- 

@teacher_bp_view.route('/assign-work', methods=['POST'])
@jwt_required()
def assign_work():
    current_user_id = get_jwt_identity()
    teacher = User.query.get(current_user_id)

    if teacher.role != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 403

    title = request.form.get('title')
    subject = request.form.get('subject')
    description = request.form.get('description')
    class_name = request.form.get('class_name')
    file = request.files.get('file')

    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    assignment = Assignment(
        title=title,
        subject=subject,
        description=description,
        filename=filename,
        class_name=class_name,
        teacher_id=teacher.id
    )
    db.session.add(assignment)
    db.session.commit()

    return jsonify({'message': 'Assignment uploaded successfully'})

# ------ Attendence -----

@teacher_bp_view.route('/teacher/attendance', methods=['GET'])
@jwt_required()
def view_teacher_attendance():
    teacher_id = get_jwt_identity()
    month = request.args.get('month')

    records = Attendance.query.filter_by(teacher_id=teacher_id, month=month).all()
    total_days = len(records)
    present_days = sum(1 for r in records if r.status == 'Present')
    percent = round((present_days / total_days) * 100, 2) if total_days > 0 else 0

    data = {
        "month": month,
        "percentage": f"{percent}%",
        "records": [{"date": r.date.strftime("%Y-%m-%d"), "status": r.status} for r in records]
    }
    return jsonify(data)


# ----- TEACHER-VIEW-SALARY------

@teacher_bp_view.route('/teacher/salary', methods=['GET'])
@jwt_required()
def view_salary():
    teacher_id = get_jwt_identity()
    salaries = Salary.query.filter_by(teacher_id=teacher_id).all()

    total_earned = sum(s.amount for s in salaries if s.status == 'Paid')
    total_due = sum(s.amount for s in salaries if s.status == 'Due')

    history = []
    for s in salaries:
        history.append({
            "month": s.month,
            "amount": s.amount,
            "payment_date": s.payment_date.strftime("%Y-%m-%d") if s.payment_date else "Pending",
            "status": s.status
        })

    return jsonify({
        "total_earned": total_earned,
        "total_due": total_due,
        "salary_history": history
    })
