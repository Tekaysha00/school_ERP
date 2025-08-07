from app import db
from datetime import datetime

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(200))
    class_name = db.Column(db.String(20))  # e.g., 'Class IX'
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    teacher = db.relationship('User', backref='assignments')
