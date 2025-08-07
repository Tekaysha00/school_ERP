from flask import Blueprint, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.student_model import Student
from app.models.assignment_model import Assignment
from app.models.user_model import User


student_bp_view = Blueprint('student_bp_view', __name__)
UPLOAD_FOLDER = 'static/uploads'


@student_bp_view.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    identity = get_jwt_identity()
    student = Student.query.get(identity['id'])

    return jsonify({
        "FullName": student.FullName,
        "phone": student.phone,
        "dob": student.dob,
        "fatherName": student.fatherName,
        "admissionNo": student.admissionNo,
        "bloodGroup": student.bloodGroup,
        "village": student.village,
        "state": student.state,
        "district": student.district
    })

# ------- HOMEWORK-DOWNLOAD ------ 

@student_bp_view.route('/homework', methods=['GET'])
@jwt_required()
def view_homework():
    current_user_id = get_jwt_identity()
    student = User.query.get(current_user_id)

    if student.role != 'student':
        return jsonify({'error': 'Unauthorized'}), 403

    assignments = Assignment.query.filter_by(class_name=student.class_name).all()
    result = []
    for a in assignments:
        result.append({
            'title': a.title,
            'subject': a.subject,
            'description': a.description,
            'download_url': f'/download/{a.filename}'
        })
    return jsonify(result)

@student_bp_view.route('/download/<filename>', methods=['GET'])
def download_assignment(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ----- ADMIN-RESULT-DOWNLOAD ------- 
@student_bp_view.route('/student/academic', methods=['GET'])
@jwt_required()
def view_academic():
    student_id = get_jwt_identity()
    record = Assignment.query.filter_by(student_id=student_id).first()

    if not record:
        return jsonify({'message': 'No academic record found'}), 404

    student = Student.query.get(student_id)
    total_attendance = getattr(student, 'attendance_percent', None)  # assuming it's stored or calculated

    return jsonify({
        "exam_name": record.exam_name,
        "score": record.score,
        "result_download": f"/student/download/{record.result_file}",
        "admit_download": f"/student/download/{record.admit_card_file}",
        "attendance_percent": f"{total_attendance}%" if total_attendance else "N/A"
    })

@student_bp_view.route('/student/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)