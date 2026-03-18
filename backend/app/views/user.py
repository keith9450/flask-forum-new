"""
User profile views
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from ..models.models import db, User, Post, Comment

user_bp = Blueprint('user', __name__)


@user_bp.route('/user/<int:user_id>')
def profile(user_id):
    """User profile page"""
    user = User.query.get_or_404(user_id)

    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Get user's posts
    posts_query = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc())
    posts = posts_query.paginate(page=page, per_page=per_page, error_out=False)

    # Get post count and comment count
    post_count = Post.query.filter_by(user_id=user_id).count()
    comment_count = Comment.query.filter_by(user_id=user_id, is_deleted=False).count()

    return render_template('user_profile.html',
                           profile_user=user,
                           posts=posts,
                           post_count=post_count,
                           comment_count=comment_count)


@user_bp.route('/user/<int:user_id>/posts')
def user_posts(user_id):
    """User's posts list"""
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = 20

    posts_query = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc())
    posts = posts_query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('user_posts.html', profile_user=user, posts=posts)


@user_bp.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def settings_profile():
    """Update profile settings"""
    if request.method == 'POST':
        bio = request.form.get('bio', '').strip()[:500]

        current_user.bio = bio
        db.session.commit()

        flash('个人资料已更新', 'success')
        return redirect(url_for('user.profile', user_id=current_user.id))

    return render_template('settings_profile.html')


@user_bp.route('/settings/password', methods=['GET', 'POST'])
@login_required
def settings_password():
    """Change password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []

        if not current_user.check_password(current_password):
            errors.append('当前密码错误')

        if len(new_password) < 6:
            errors.append('新密码长度至少6位')

        if new_password != confirm_password:
            errors.append('两次输入的密码不一致')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('settings_password.html')

        current_user.set_password(new_password)
        db.session.commit()

        flash('密码修改成功！', 'success')
        return redirect(url_for('user.profile', user_id=current_user.id))

    return render_template('settings_password.html')
