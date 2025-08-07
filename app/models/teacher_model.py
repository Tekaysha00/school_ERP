from ..extensions import db
from app.extensions import db


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    mobile = db.Column(db.String(15), unique=True)
    dob = db.Column(db.String(10))
    gender = db.Column(db.String(10))
    id_mark = db.Column(db.String(50))
    blood_group = db.Column(db.String(10))
    village = db.Column(db.String(100))
    po = db.Column(db.String(100))
    ps = db.Column(db.String(100))
    pin_code = db.Column(db.String(50))
    district = db.Column(db.String(100))
    State = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Checkteacher(db.Model):
    __tablename__ = 'checkteachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    salaries = db.relationship('Salary', backref='checkteacher', lazy=True)
    attendances = db.relationship('Attendance', backref='checkteacher', lazy=True)
