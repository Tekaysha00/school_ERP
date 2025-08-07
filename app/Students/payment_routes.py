from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.fee_model import FeeRecord
from razorpay_config import razorpay_client
from app import db




payment_bp = Blueprint('payment_bp', __name__)

@payment_bp.route('/student/fee-structure/<month>', methods=['GET'])
@jwt_required()
def get_fee_structure(month):
    # Static structure for demo
    fee_data = {
        "school_fee": 1500,
        "sports_fee": 200,
        "other_fee": 150,
        "total": 1850
    }
    return jsonify(fee_data)

@payment_bp.route('/student/initiate-payment', methods=['POST'])
@jwt_required()
def initiate_payment():
    student_id = get_jwt_identity()
    data = request.json
    month = data['month']
    upi_id = data['upi_id']

    total_amount = 1850  # You can calculate dynamically

    razorpay_order = razorpay_client.order.create({
        "amount": total_amount * 100,  # in paise
        "currency": "INR",
        "payment_capture": 1
    })

    fee_record = FeeRecord(
        student_id=student_id,
        month=month,
        school_fee=1500,
        sports_fee=200,
        other_fee=150,
        total_amount=total_amount,
        upi_id=upi_id,
        razorpay_order_id=razorpay_order['id']
    )
    db.session.add(fee_record)
    db.session.commit()

    return jsonify({
        "order_id": razorpay_order['id'],
        "amount": total_amount,
        "currency": "INR",
        "upi_id": upi_id,
        "razorpay_key": "YOUR_RAZORPAY_KEY_ID"
    })

@payment_bp.route('/student/payment-status', methods=['POST'])
@jwt_required()
def update_payment_status():
    data = request.json
    order_id = data['order_id']
    status = data['status']  # 'Success' or 'Failed'

    record = FeeRecord.query.filter_by(razorpay_order_id=order_id).first()
    if record:
        record.payment_status = status
        db.session.commit()
        return jsonify({'message': 'Payment status updated'})
    return jsonify({'message': 'Order not found'}), 404
