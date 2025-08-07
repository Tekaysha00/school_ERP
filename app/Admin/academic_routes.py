from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.assignment_model import Assignment

academic_bp = Blueprint('academic_bp', __name__)
UPLOAD_FOLDER = 'static/uploads/academic'

@academic_bp.route('/admin/upload-academic', methods=['POST'])
@jwt_required()
def upload_academic():
    data = request.form
    student_id = data['student_id']
    exam_name = data['exam_name']
    score = float(data['score'])

    result_file = request.files.get('result_file')
    admit_file = request.files.get('admit_card_file')

    result_filename = secure_filename(result_file.filename)
    admit_filename = secure_filename(admit_file.filename)

    result_path = os.path.join(UPLOAD_FOLDER, result_filename)
    admit_path = os.path.join(UPLOAD_FOLDER, admit_filename)

    result_file.save(result_path)
    admit_file.save(admit_path)

    record = Assignment(
        student_id=student_id,
        exam_name=exam_name,
        score=score,
        result_file=result_filename,
        admit_card_file=admit_filename
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({'message': 'Academic record uploaded successfully'})
