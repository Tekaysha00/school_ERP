from flask import Flask
from flask_cors import CORS
from .extensions import db, bcrypt, jwt, cors
from .Admin.checkin_routes import checkin_bp
from .Admin.attendance_routes import attendance_bp
#from app.Students.dashboard import student_dashboard_bp
from app.Admin.routes import class_bp
from config import Config
#from app.Students.register_routes import student_register_bp #new added
from app.auth.admin_auth import admin_auth_bp #new added
from app.auth.user_auth import user_auth_bp #new added
from app.auth.demo_routes import demo_bp
from app.auth.user_auth import student_auth_bp
from app.Students.register_routes import student_register_bp
from app.Students.dashboard import student_dashboard_bp
from app.Admin.routes import admin_core_bp
from .Admin.students_routes import student_bp_admin
from app.Admin.teacher_checkin_routes import teacher_checkin_bp
from app.models.student_model import Student
from app.Students.student_routes import student_bp_view
from app.Teachers.routes import teacher_bp_view




def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)


    cors.init_app(app,
        origins=["http://localhost:5173", "http://192.168.43.96:5173"],
        methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True
    )

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, supports_credentials=True)

    # Register Blueprints
    app.register_blueprint(checkin_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(admin_auth_bp)
    app.register_blueprint(user_auth_bp)
    app.register_blueprint(class_bp)
    app.register_blueprint(student_auth_bp)
    app.register_blueprint(demo_bp)
    app.register_blueprint(student_register_bp)
    app.register_blueprint(student_dashboard_bp)
    app.register_blueprint(admin_core_bp)
    app.register_blueprint(student_bp_admin)
    app.register_blueprint(teacher_checkin_bp)
    app.register_blueprint(teacher_bp_view, url_prefix='/teacher')
    app.register_blueprint(student_bp_view, url_prefix='/student')






    # Create DB tables
    with app.app_context():
        db.create_all()

    @app.route('/api/test')
    def test_api():
        return {'message': 'API is working!'}
    



    return app





