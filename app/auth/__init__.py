from .admin_auth import admin_auth_bp
from .user_auth import user_auth_bp


def register_auth_blueprints(app):
    app.register_blueprint(admin_auth_bp)
    app.register_blueprint(user_auth_bp)
