"""
Flask Application Factory
"""
import os
from flask import Flask
from flask_login import LoginManager

from .models.models import db, init_db

login_manager = LoginManager()


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, template_folder='../../frontend/templates', static_folder='../../frontend/static')

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # 开发环境禁用CSRF避免令牌问题
    app.config['WTF_CSRF_ENABLED'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录后再进行操作'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        from .models.models import User
        return User.query.get(int(user_id))

    # Register blueprints
    from .views.auth import auth_bp
    from .views.posts import posts_bp
    from .views.user import user_bp
    from .views.admin import admin_bp
    from .views.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Create database tables
    init_db(app)

    return app
