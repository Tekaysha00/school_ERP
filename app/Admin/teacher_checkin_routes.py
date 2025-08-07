from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Teacher, Attendance, Salary, User
from app.extensions import db
from datetime import datetime

teacher_checkin_bp = Blueprint('teacher_checkin_bp', __name__, url_prefix='/admin')

# 🔹 List all teachers
@teacher_checkin_bp.route('/teachers', methods=['GET'])
@jwt_required()
def list_teachers():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    teachers = Teacher.query.all()
    return jsonify([{
        'id': t.id,
        'name': t.full_name
    } for t in teachers])

# 🔹 Get teacher details + attendance
@teacher_checkin_bp.route('/teacher/<int:teacher_id>', methods=['GET'])
@jwt_required()
def get_teacher_checkin_data(teacher_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    teacher = Teacher.query.get_or_404(teacher_id)

    # Attendance calculation
    records = Attendance.query.filter_by(marked_by=teacher.user_id).all()
    present = sum(1 for r in records if r.status == 'present')
    total = len(records)
    percentage = round((present / total) * 100) if total > 0 else 0

    return jsonify({
        'personal_info': {
            'dob': teacher.dob,
            'admission_no': teacher.admission_no,
            'gender': teacher.gender,
            'id_mark': teacher.id_mark,
            'blood_group': teacher.blood_group
        },
        'address': {
            'village': teacher.village,
            'po': teacher.po,
            'ps': teacher.ps,
            'pin_code': teacher.pin_code,
            'district': teacher.district,
            'state': teacher.State
        },
        'attendance': {
            'rate': f"{percentage}%"
        }
    })


# 🔹 Mark teacher attendance
@teacher_checkin_bp.route('/teacher/<int:teacher_id>/mark-attendance', methods=['POST'])
@jwt_required()
def mark_teacher_attendance(teacher_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    status = data.get('status')  # 'present' or 'absent'

    attendance = Attendance(
        student_id=None,
        date=datetime.utcnow().date(),
        status=status,
        marked_by=teacher_id  # using teacher's user_id
    )
    db.session.add(attendance)
    db.session.commit()

    return jsonify({'message': 'Attendance marked'})

# 🔹 Pay salary
@teacher_checkin_bp.route('/teacher/<int:teacher_id>/pay-salary', methods=['POST'])
@jwt_required()
def pay_teacher_salary(teacher_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    month = data.get('month')
    amount = data.get('amount')

    if not month or not amount:
        return jsonify({'error': 'Month and amount required'}), 400

    salary = Salary(
        teacher_id=teacher_id,
        month=month,
        amount=amount,
        status='paid'
    )
    db.session.add(salary)
    db.session.commit()

    return jsonify({'message': 'Salary marked as paid'})


@teacher_checkin_bp.route('/teacher/salary-lookup', methods=['GET'])
@jwt_required()
def salary_lookup():
    salaries = Salary.query.all()
    data = []
    for s in salaries:
        data.append({
            "teacher_name": s.teacher.name,
            "status": s.status,
            "amount": s.amount,
            "month": s.month
        })
    return jsonify(data)

@teacher_checkin_bp.route('/teacher/attendance-lookup', methods=['GET'])
@jwt_required()
def attendance_lookup():
    attendances = Attendance.query.all()
    data = []
    for a in attendances:
        total = a.present_days + a.absent_days
        percent = round((a.present_days / total) * 100, 2) if total > 0 else 0
        data.append({
            "teacher_name": a.teacher.name,
            "present": a.present_days,
            "absent": a.absent_days,
            "percentage": f"{percent}%"
        })
    return jsonify(data)
