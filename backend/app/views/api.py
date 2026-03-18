"""
API views for AJAX requests
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ..models.models import db, Category, Post, Comment, PostLike

api_bp = Blueprint('api', __name__)


@api_bp.route('/categories')
def get_categories():
    """Get all categories"""
    categories = Category.query.order_by(Category.sort_order).all()
    return jsonify([cat.to_dict() for cat in categories])


@api_bp.route('/posts')
def get_posts():
    """Get posts list"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category', type=int)

    query = Post.query
    if category_id:
        query = query.filter_by(category_id=category_id)

    posts = query.order_by(Post.is_pinned.desc(), Post.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'posts': [post.to_dict() for post in posts.items],
        'total': posts.total,
        'pages': posts.pages,
        'current_page': posts.page
    })


@api_bp.route('/posts/<int:post_id>')
def get_post(post_id):
    """Get single post"""
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict(include_content=True))


@api_bp.route('/posts/<int:post_id>/comments')
def get_comments(post_id):
    """Get post comments"""
    comments = Comment.query.filter_by(post_id=post_id, parent_id=None, is_deleted=False)\
        .order_by(Comment.created_at).all()
    return jsonify([comment.to_dict() for comment in comments])


@api_bp.route('/posts/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    """Toggle like status"""
    post = Post.query.get_or_404(post_id)

    like = PostLike.query.filter_by(post_id=post_id, user_id=current_user.id).first()

    if like:
        db.session.delete(like)
        liked = False
    else:
        like = PostLike(post_id=post_id, user_id=current_user.id)
        db.session.add(like)
        liked = True

    db.session.commit()

    return jsonify({
        'success': True,
        'liked': liked,
        'like_count': post.likes.count()
    })


@api_bp.route('/user/check')
def check_user():
    """Check if user is logged in"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        })
    return jsonify({'authenticated': False})
