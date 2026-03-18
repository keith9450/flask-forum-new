"""
Admin views
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from ..models.models import db, User, Post, Category, Comment, Announcement

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/admin')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Statistics
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_comments = Comment.query.filter_by(is_deleted=False).count()

    # Recent registrations
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()

    # Recent posts
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()

    # Popular posts (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    popular_posts = Post.query.filter(Post.created_at >= week_ago)\
        .order_by(Post.view_count.desc()).limit(5).all()

    # Posts by category
    category_stats = []
    for cat in Category.query.all():
        category_stats.append({
            'name': cat.name,
            'count': cat.posts.count()
        })

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_posts=total_posts,
                           total_comments=total_comments,
                           recent_users=recent_users,
                           recent_posts=recent_posts,
                           popular_posts=popular_posts,
                           category_stats=category_stats)


# ============ User Management ============

@admin_bp.route('/admin/users')
@login_required
@admin_required
def users():
    """User management"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '').strip()
    role_filter = request.args.get('role', '')

    query = User.query

    if search:
        query = query.filter(
            (User.username.contains(search)) | (User.email.contains(search))
        )

    if role_filter:
        query = query.filter_by(role=role_filter)

    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('admin/users.html', users=users, search=search, role_filter=role_filter)


@admin_bp.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user"""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        role = request.form.get('role', 'user')
        is_active = request.form.get('is_active', 'on') == 'on'

        if role not in ['user', 'moderator', 'admin']:
            flash('无效的角色', 'error')
            return render_template('admin/edit_user.html', edit_user=user)

        user.role = role
        user.is_active = is_active
        db.session.commit()

        flash(f'用户 {user.username} 已更新', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/edit_user.html', edit_user=user)


@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('不能删除自己', 'error')
        return redirect(url_for('admin.users'))

    username = user.username
    db.session.delete(user)
    db.session.commit()

    flash(f'用户 {username} 已删除', 'success')
    return redirect(url_for('admin.users'))


# ============ Post Management ============

@admin_bp.route('/admin/posts')
@login_required
@admin_required
def posts():
    """Post management"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '').strip()

    query = Post.query

    if search:
        query = query.filter(
            (Post.title.contains(search)) | (Post.content.contains(search))
        )

    posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('admin/posts.html', posts=posts, search=search)


@admin_bp.route('/admin/posts/<int:post_id>/pin', methods=['POST'])
@login_required
@admin_required
def toggle_pin(post_id):
    """Toggle post pinned status"""
    post = Post.query.get_or_404(post_id)
    post.is_pinned = not post.is_pinned
    db.session.commit()
    flash(f'帖子已{"置顶" if post.is_pinned else "取消置顶"}', 'success')
    return redirect(request.referrer or url_for('admin.posts'))


@admin_bp.route('/admin/posts/<int:post_id>/essence', methods=['POST'])
@login_required
@admin_required
def toggle_essence(post_id):
    """Toggle post essence status"""
    post = Post.query.get_or_404(post_id)
    post.is_essence = not post.is_essence
    db.session.commit()
    flash(f'帖子已{"加精" if post.is_essence else "取消加精"}', 'success')
    return redirect(request.referrer or url_for('admin.posts'))


@admin_bp.route('/admin/posts/<int:post_id>/lock', methods=['POST'])
@login_required
@admin_required
def toggle_lock(post_id):
    """Toggle post locked status"""
    post = Post.query.get_or_404(post_id)
    post.is_locked = not post.is_locked
    db.session.commit()
    flash(f'帖子已{"锁定" if post.is_locked else "解锁"}', 'success')
    return redirect(request.referrer or url_for('admin.posts'))


@admin_bp.route('/admin/posts/<int:post_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_post(post_id):
    """Delete post"""
    post = Post.query.get_or_404(post_id)
    title = post.title
    db.session.delete(post)
    db.session.commit()
    flash(f'帖子 "{title}" 已删除', 'success')
    return redirect(url_for('admin.posts'))


# ============ Category Management ============

@admin_bp.route('/admin/categories')
@login_required
@admin_required
def categories():
    """Category management"""
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/admin/categories/create', methods=['POST'])
@login_required
@admin_required
def create_category():
    """Create category"""
    name = request.form.get('name', '').strip()
    slug = request.form.get('slug', '').strip()
    description = request.form.get('description', '').strip()
    icon = request.form.get('icon', 'folder')
    sort_order = request.form.get('sort_order', 0, type=int)

    if not name or not slug:
        flash('分类名称和别名必填', 'error')
        return redirect(url_for('admin.categories'))

    # Check uniqueness
    if Category.query.filter_by(slug=slug).first():
        flash('分类别名已存在', 'error')
        return redirect(url_for('admin.categories'))

    category = Category(name=name, slug=slug, description=description, icon=icon, sort_order=sort_order)
    db.session.add(category)
    db.session.commit()

    flash(f'分类 "{name}" 已创建', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/admin/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    """Edit category"""
    category = Category.query.get_or_404(category_id)

    if request.method == 'POST':
        category.name = request.form.get('name', '').strip()
        category.slug = request.form.get('slug', '').strip()
        category.description = request.form.get('description', '').strip()
        category.icon = request.form.get('icon', 'folder')
        category.sort_order = request.form.get('sort_order', 0, type=int)
        db.session.commit()

        flash('分类已更新', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/edit_category.html', category=category)


@admin_bp.route('/admin/categories/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    """Delete category"""
    category = Category.query.get_or_404(category_id)

    # Check if category has posts
    if category.posts.count() > 0:
        flash('该分类下有帖子，无法删除', 'error')
        return redirect(url_for('admin.categories'))

    name = category.name
    db.session.delete(category)
    db.session.commit()

    flash(f'分类 "{name}" 已删除', 'success')
    return redirect(url_for('admin.categories'))


# ============ Announcement Management ============

@admin_bp.route('/admin/announcements')
@login_required
@admin_required
def announcements():
    """Announcement management"""
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', announcements=announcements)


@admin_bp.route('/admin/announcements/create', methods=['POST'])
@login_required
@admin_required
def create_announcement():
    """Create announcement"""
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    is_pinned = request.form.get('is_pinned', 'off') == 'on'

    if not title or not content:
        flash('标题和内容必填', 'error')
        return redirect(url_for('admin.announcements'))

    announcement = Announcement(title=title, content=content, is_pinned=is_pinned)
    db.session.add(announcement)
    db.session.commit()

    flash('公告已发布', 'success')
    return redirect(url_for('admin.announcements'))


@admin_bp.route('/admin/announcements/<int:announcement_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_announcement(announcement_id):
    """Delete announcement"""
    announcement = Announcement.query.get_or_404(announcement_id)
    db.session.delete(announcement)
    db.session.commit()
    flash('公告已删除', 'success')
    return redirect(url_for('admin.announcements'))
