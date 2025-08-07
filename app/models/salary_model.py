from app.extensions import db
from datetime import datetime

class Salary(db.Model):
    __tablename__ = 'salaries'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    month = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='unpaid')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    teacher = db.relationship('Teacher', backref='salaries')
