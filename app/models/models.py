''' from ..extensions import db

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone_no = db.Column(db.String(20))
    email = db.Column(db.String(100))
    student_class = db.Column(db.String(10))
    DOB = db.Column(db.String(20))
    admission_no = db.Column(db.String(50), unique=True)
    gender = db.Column(db.String(10))
    id_mark = db.Column(db.String(100))
    blood_group = db.Column(db.String(5))
    village = db.Column(db.String(100))
    po = db.Column(db.String(100))
    ps = db.Column(db.String(100))
    pin_code = db.Column(db.String(10))
    district = db.Column(db.String(100))
    state = db.Column(db.String(100)) '''
