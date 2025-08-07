from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from ..extensions import db, jwt
import razorpay
import os
import datetime
from app.models.attendance_model import Attendance
from app.models.user_model import User
from app.models.payment_model import Payment

checkin_bp = Blueprint('checkin_bp', __name__, url_prefix='/admin')

# Razorpay setup
RAZORPAY_KEY_ID = "rzp_test_20tkfyOZteuJyu"
RAZORPAY_KEY_SECRET = "bMrRXLvsfNu2ij51fcn3UZPu"
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Upload folder setup
UPLOAD_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'static', 'uploads')
RESULT_FOLDER = os.path.join(UPLOAD_ROOT, 'result')
ADMIT_FOLDER = os.path.join(UPLOAD_ROOT, 'admit_card')


os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(ADMIT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Payment model


# Upload result (Admin only)
@checkin_bp.route('/upload/result', methods=['POST'])
@jwt_required()
def upload_result():
    current_user = get_jwt_identity()

    if current_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    file = request.files.get('file')
    student_id = request.form.get('student_id')

    if not file or not student_id:
        return jsonify({'error': 'Missing file or student_id'}), 400

    if allowed_file(file.filename):
        filename = secure_filename(f"{student_id}_result.{file.filename.rsplit('.', 1)[1]}")
        file.save(os.path.join(RESULT_FOLDER, filename))
        return jsonify({'message': 'Result uploaded successfully'})
    return jsonify({'error': 'Invalid file type'}), 400

# Upload admit card
@checkin_bp.route('/upload/admit', methods=['POST'])
@jwt_required()
def upload_admit():
    current_user = get_jwt_identity()

    if current_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    file = request.files.get('file')
    student_id = request.form.get('student_id')

    if not file or not student_id:
        return jsonify({'error': 'Missing file or student_id'}), 400

    if allowed_file(file.filename):
        filename = secure_filename(f"{student_id}_admit.{file.filename.rsplit('.', 1)[1]}")
        file.save(os.path.join(ADMIT_FOLDER, filename))
        return jsonify({'message': 'Admit card uploaded successfully'})
    return jsonify({'error': 'Invalid file type'}), 400

# Mark payment manually
@checkin_bp.route('/mark-paid', methods=['POST'])
@jwt_required()
def mark_paid():
    current_user = get_jwt_identity()

    if current_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.json
    student_id = data.get("student_id")
    amount = data.get("amount")

    if not student_id or not amount:
        return jsonify({'error': 'Missing student_id or amount'}), 400

    payment = Payment(student_id=student_id, amount=amount, status="paid", mode="cash")
    db.session.add(payment)
    db.session.commit()

    return jsonify({"message": "Marked as paid (cash)"})

# Create Razorpay order
@checkin_bp.route('/create-order', methods=['POST'])
def create_order():
    data = request.json
    amount = data.get('amount')
    student_id = data.get('student_id')

    if not amount or not student_id:
        return jsonify({'error': 'Missing amount or student_id'}), 400

    order = client.order.create(dict(amount=amount * 100, currency="INR", payment_capture="1"))
    payment = Payment(student_id=student_id, amount=amount, status="unpaid", mode="razorpay")
    db.session.add(payment)
    db.session.commit()

    return jsonify({
        'order_id': order['id'],
        'razorpay_key': RAZORPAY_KEY_ID,
        'amount': amount,
        'student_id': student_id
    })

# Verify Razorpay payment
@checkin_bp.route('/verify-payment', methods=['POST'])
def verify_payment():
    data = request.json
    student_id = data.get("student_id")

    payment = Payment.query.filter_by(student_id=student_id).order_by(Payment.id.desc()).first()
    if payment:
        payment.status = "paid"
        db.session.commit()
        return jsonify({"message": "Payment verified and updated"})
    return jsonify({"error": "Payment record not found"}), 404

# Check latest payment status
@checkin_bp.route('/payment-status/<student_id>', methods=['GET'])
def check_status(student_id):
    payment = Payment.query.filter_by(student_id=student_id).order_by(Payment.id.desc()).first()
    if payment:
        return jsonify({
            "status": payment.status,
            "mode": payment.mode,
            "amount": payment.amount,
            "timestamp": payment.timestamp.strftime("%Y-%m-%d %H:%M")
        })
    return jsonify({"status": "unpaid"})

# -------- Student-checkin--------
@checkin_bp.route('/check-in', methods=['POST'])
@jwt_required()
def check_in_student():
    current_user = get_jwt_identity()
    data = request.get_json()
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({'success': False, 'message': 'Student ID required'}), 400

    try:
        attendance = Attendance(
            student_id=student_id,
            date=datetime.utcnow().date(),
            status='present',
            marked_by=current_user['id']
        )
        db.session.add(attendance)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Student {student_id} checked in',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    

@checkin_bp.route('/attendance/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_attendance(student_id):
    records = Attendance.query.filter_by(student_id=student_id).all()
    return jsonify([{
        'date': r.date.strftime('%Y-%m-%d'),
        'status': r.status,
        'marked_by': User.query.get(r.marked_by).username if r.marked_by else 'System'
    } for r in records])

def get_attendance_stats(student_id):
    records = Attendance.query.filter_by(student_id=student_id).all()
    if not records:
        return None

    present = sum(1 for r in records if r.status == 'present')
    absent = sum(1 for r in records if r.status == 'absent')
    total = present + absent
    percentage = round((present / total) * 100) if total > 0 else 0

    return {
        'present': present,
        'absent': absent,
        'percentage': f"{percentage}%"
    }