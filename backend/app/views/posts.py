"""
Post views
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import desc, or_
from datetime import datetime
from ..models.models import db, Post, Category, Comment, PostLike, Announcement

posts_bp = Blueprint('posts', __name__)


@posts_bp.route('/home')
def home():
    """Home page with posts list"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', 'latest')

    # Base query
    query = Post.query

    # Filter by category
    if category_id:
        query = query.filter_by(category_id=category_id)

    # Search
    if search:
        query = query.filter(
            or_(Post.title.contains(search), Post.content.contains(search))
        )

    # Sort
    if sort == 'latest':
        query = query.order_by(Post.is_pinned.desc(), Post.created_at.desc())
    elif sort == 'hot':
        query = query.order_by(Post.is_pinned.desc(), Post.view_count.desc())
    elif sort == 'essence':
        query = query.filter_by(is_essence=True).order_by(Post.created_at.desc())

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    posts = pagination.items

    # Get categories
    categories = Category.query.order_by(Category.sort_order).all()

    # Get announcements
    announcements = Announcement.query.filter_by(is_pinned=True).all()

    return render_template('index.html',
                           posts=posts,
                           pagination=pagination,
                           categories=categories,
                           announcements=announcements,
                           current_category=category_id,
                           search=search,
                           sort=sort)


@posts_bp.route('/post/<int:post_id>')
def view_post(post_id):
    """View single post"""
    post = Post.query.get_or_404(post_id)

    # Increment view count
    post.view_count += 1
    db.session.commit()

    # Get comments
    comments = Comment.query.filter_by(post_id=post_id, parent_id=None, is_deleted=False)\
        .order_by(Comment.created_at).all()

    # Check if user liked
    user_liked = False
    if current_user.is_authenticated:
        like = PostLike.query.filter_by(post_id=post_id, user_id=current_user.id).first()
        user_liked = like is not None

    return render_template('post_detail.html', post=post, comments=comments, user_liked=user_liked)


@posts_bp.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create new post"""
    categories = Category.query.order_by(Category.sort_order).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category_id = request.form.get('category_id', type=int)

        errors = []
        if not title or len(title) < 5:
            errors.append('标题长度至少5个字符')
        if len(title) > 200:
            errors.append('标题长度不能超过200个字符')
        if not content or len(content) < 10:
            errors.append('内容长度至少10个字符')
        if not category_id:
            errors.append('请选择分类')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('create_post.html', categories=categories, csrf_token='')

        post = Post(title=title, content=content, category_id=category_id, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()

        flash('发帖成功！', 'success')
        return redirect(url_for('posts.view_post', post_id=post.id))

    return render_template('create_post.html', categories=categories, csrf_token='')


@posts_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit post"""
    post = Post.query.get_or_404(post_id)

    # Check permission
    if post.user_id != current_user.id and not current_user.is_admin():
        abort(403)

    categories = Category.query.order_by(Category.sort_order).all()

    if request.method == 'POST':
        post.title = request.form.get('title', '').strip()
        post.content = request.form.get('content', '').strip()
        post.category_id = request.form.get('category_id', type=int)
        post.updated_at = datetime.utcnow()
        db.session.commit()

        flash('修改成功！', 'success')
        return redirect(url_for('posts.view_post', post_id=post.id))

    return render_template('edit_post.html', post=post, categories=categories)


@posts_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete post"""
    post = Post.query.get_or_404(post_id)

    # Check permission
    if post.user_id != current_user.id and not current_user.is_admin():
        abort(403)

    db.session.delete(post)
    db.session.commit()

    flash('帖子已删除', 'success')
    return redirect(url_for('posts.home'))


@posts_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add comment to post"""
    post = Post.query.get_or_404(post_id)

    if post.is_locked:
        flash('该帖子已锁定，无法评论', 'warning')
        return redirect(url_for('posts.view_post', post_id=post_id))

    content = request.form.get('content', '').strip()
    parent_id = request.form.get('parent_id', type=int)

    if not content or len(content) < 1:
        flash('评论内容不能为空', 'error')
        return redirect(url_for('posts.view_post', post_id=post_id))

    comment = Comment(content=content, post_id=post_id, user_id=current_user.id, parent_id=parent_id)
    db.session.add(comment)
    db.session.commit()

    flash('评论成功！', 'success')
    return redirect(url_for('posts.view_post', post_id=post_id))


@posts_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    """Like/unlike post"""
    post = Post.query.get_or_404(post_id)

    like = PostLike.query.filter_by(post_id=post_id, user_id=current_user.id).first()

    if like:
        db.session.delete(like)
        db.session.commit()
        action = 'unliked'
    else:
        like = PostLike(post_id=post_id, user_id=current_user.id)
        db.session.add(like)
        db.session.commit()
        action = 'liked'

    return {'success': True, 'action': action, 'like_count': post.likes.count()}
