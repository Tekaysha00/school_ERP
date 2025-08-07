from ..extensions import db  

class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    marked_by = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', back_populates='attendance_marked')

    def __repr__(self):
        return f'<Attendance {self.id} - User {self.user_id} - {self.status}>'
    


