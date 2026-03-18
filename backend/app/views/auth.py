"""
Authentication views
"""
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf.csrf import generate_csrf
from datetime import datetime
from ..models.models import db, User

auth_bp = Blueprint('auth', __name__)


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, '密码长度至少6位'
    if len(password) > 50:
        return False, '密码长度不能超过50位'
    return True, ''


@auth_bp.route('/')
def index():
    """Home page - redirect to forum home"""
    return redirect(url_for('posts.home'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('posts.home'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', 'off') == 'on'

        if not identifier or not password:
            flash('请输入用户名/邮箱和密码', 'error')
            return render_template('login.html', csrf_token=generate_csrf())

        # Find user by username or email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

        if user is None:
            flash('用户不存在', 'error')
            return render_template('login.html', csrf_token=generate_csrf())

        if not user.is_active:
            flash('账号已被禁用', 'error')
            return render_template('login.html', csrf_token=generate_csrf())

        if not user.check_password(password):
            flash('密码错误', 'error')
            return render_template('login.html', csrf_token=generate_csrf())

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        login_user(user, remember=remember)
        flash(f'欢迎回来，{user.username}！', 'success')

        # Redirect to next page or home
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('posts.home'))

    return render_template('login.html', csrf_token=generate_csrf())


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('posts.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        errors = []

        if not username or not email or not password:
            errors.append('所有字段都是必填的')
        elif len(username) < 3 or len(username) > 20:
            errors.append('用户名长度需在3-20个字符之间')
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('用户名只能包含字母、数字和下划线')
        elif not validate_email(email):
            errors.append('请输入有效的邮箱地址')
        else:
            valid, msg = validate_password(password)
            if not valid:
                errors.append(msg)
            elif password != confirm_password:
                errors.append('两次输入的密码不一致')

        # Check uniqueness
        if not errors:
            if User.query.filter_by(username=username).first():
                errors.append('用户名已被注册')
            if User.query.filter_by(email=email).first():
                errors.append('邮箱已被注册')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html', csrf_token=generate_csrf())

        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('注册成功！请登录', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', csrf_token=generate_csrf())


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('posts.home'))
