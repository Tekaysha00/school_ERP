from flask import Blueprint, request, redirect, render_template, session
from app.models.user_model import User
from app.extensions import db, bcrypt

admin_auth_bp = Blueprint('admin_auth_bp', __name__, url_prefix='/admin')

@admin_auth_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, role='admin').first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['admin_id'] = user.id
            return redirect('/admin/dashboard')  
        else:
            error = 'Invalid credentials'
            return render_template('admin_login.html', error=error), 401

    return render_template('admin_login.html')  


# Optional: Create default admin
def create_default_admin():
    username = "admin"
    password = "adminpass"

    if not User.query.filter_by(username=username).first():
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        admin = User(username=username, password=hashed, role='admin')
        db.session.add(admin)
        db.session.commit()
        print(f"Default Admin Created → Username: {username}, Password: {password}")
