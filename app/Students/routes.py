from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models.attendance_model import StudentAttendance

students_bp = Blueprint('students_bp', __name__)




@students_bp.route('/student/attendance-status/<int:student_id>', methods=['GET'])
@jwt_required()
def view_attendance(student_id):
    records = StudentAttendance.query.filter_by(student_id=student_id).all()
    data = []
    for r in records:
        data.append({
            "month": r.month,
            "status": r.status,
            "class_id": r.class_id
        })
    return jsonify(data)
