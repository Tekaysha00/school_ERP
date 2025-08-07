from flask import Blueprint, render_template

demo_bp = Blueprint('demo_bp', __name__)

@demo_bp.route('/test-login')
def test_login():
    return render_template('login.html')

