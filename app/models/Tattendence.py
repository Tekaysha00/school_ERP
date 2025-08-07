from app.extensions import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ = 'attendances'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    month = db.Column(db.String(20), nullable=False)
    present_days = db.Column(db.Integer, default=0)
    absent_days = db.Column(db.Integer, default=0)

    teacher = db.relationship('Teacher',backref='attendences')
