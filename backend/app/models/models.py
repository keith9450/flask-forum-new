"""
Forum Database Models
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), default='/static/images/default-avatar.png')
    bio = db.Column(db.String(500))
    role = db.Column(db.String(20), default='user')  # user, moderator, admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic', foreign_keys='Post.user_id')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_moderator(self):
        return self.role in ['admin', 'moderator']

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'bio': self.bio,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Category(db.Model):
    """Category model"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    icon = db.Column(db.String(50), default='folder')
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship('Post', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'post_count': self.posts.count()
        }


class Post(db.Model):
    """Post model"""
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    view_count = db.Column(db.Integer, default=0)
    is_pinned = db.Column(db.Boolean, default=False)
    is_essence = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('PostLike', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_content=False):
        data = {
            'id': self.id,
            'title': self.title,
            'user_id': self.user_id,
            'author': self.author.username if self.author else None,
            'author_avatar': self.author.avatar if self.author else None,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'view_count': self.view_count,
            'comment_count': self.comments.count(),
            'like_count': self.likes.count(),
            'is_pinned': self.is_pinned,
            'is_essence': self.is_essence,
            'is_locked': self.is_locked,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_content:
            data['content'] = self.content
        return data


class Comment(db.Model):
    """Comment model"""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    # Self-referential relationship for replies
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'author': self.author.username if self.author else None,
            'author_avatar': self.author.avatar if self.author else None,
            'parent_id': self.parent_id,
            'reply_count': self.replies.filter_by(is_deleted=False).count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_deleted': self.is_deleted
        }


class PostLike(db.Model):
    """Post like model"""
    __tablename__ = 'post_likes'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='unique_post_like'),)


class Announcement(db.Model):
    """Announcement model"""
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'is_pinned': self.is_pinned,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def init_db(app):
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()

        # Check if data already exists
        if User.query.first() is None:
            # Create admin user
            admin = User(
                username='ForumAdmin2024',
                email='admin@forum.com',
                role='admin'
            )
            admin.set_password('Xk9#mP2$vL7@nQ4w')

            # Create sample categories
            categories = [
                Category(name='综合讨论', slug='general', description='综合话题讨论', icon='comments', sort_order=1),
                Category(name='技术支持', slug='tech', description='技术问题与解答', icon='code', sort_order=2),
                Category(name='资源共享', slug='resources', description='分享优质资源', icon='share', sort_order=3),
                Category(name='建议反馈', slug='feedback', description='产品建议与问题反馈', icon='lightbulb', sort_order=4),
            ]

            # Create sample user
            user = User(
                username='DemoUser2024',
                email='demo@forum.com',
                role='user'
            )
            user.set_password('Demo@Pass456')

            # Create sample post
            sample_post = Post(
                title='欢迎来到论坛！',
                content='欢迎大家来到我们的论坛！这里可以讨论各种话题，分享知识和经验。',
                user_id=1,
                category_id=1,
                is_pinned=True
            )

            # Create sample announcement
            announcement = Announcement(
                title='论坛上线公告',
                content='欢迎使用我们的论坛系统！请遵守社区规则，文明发言。',
                is_pinned=True
            )

            db.session.add_all([admin, user] + categories + [sample_post, announcement])
            db.session.commit()

            print("Database initialized with sample data!")
