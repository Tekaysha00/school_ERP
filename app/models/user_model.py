from ..extensions import db
from app.models.attendance_model import Attendance  

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True)
    mobile = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    teacher_id = db.Column(db.Integer)

    attendance_marked = db.relationship(
        'Attendance',
        back_populates='user',
        lazy=True,
        foreign_keys=[Attendance.user_id]  
    )
