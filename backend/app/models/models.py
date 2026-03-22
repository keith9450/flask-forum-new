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
    avatar = db.Column(db.String(255), default='/static/images/admin-avatar.png')
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
                role='admin',
                avatar='/static/images/admin-avatar.png',
                bio='热爱动漫的论坛管理员，喜欢结交志同道合的朋友~'
            )
            admin.set_password('Xk9#mP2$vL7@nQ4w')

            # Create sample user
            user = User(
                username='DemoUser2024',
                email='demo@forum.com',
                role='user',
                avatar='/static/images/user-avatar.png',
                bio='动漫爱好者一枚，追番中~'
            )
            user.set_password('Demo@Pass456')

            # Create more sample users
            user2 = User(
                username='Sakura_Anime',
                email='sakura@forum.com',
                role='user',
                avatar='/static/images/user-avatar.png',
                bio='樱花粉的忠实粉丝！二次元冲冲冲！'
            )
            user2.set_password('Sakura123')

            user3 = User(
                username='Otaku_King',
                email='otaku@forum.com',
                role='moderator',
                avatar='/static/images/moderator-avatar.png',
                bio='资深二次元，欢迎讨论番剧！'
            )
            user3.set_password('Otaku123')

            # Create sample categories
            categories = [
                Category(name='综合讨论', slug='general', description='综合话题讨论', icon='comments', sort_order=1),
                Category(name='技术支持', slug='tech', description='技术问题与解答', icon='code', sort_order=2),
                Category(name='资源共享', slug='resources', description='分享优质资源', icon='share', sort_order=3),
                Category(name='建议反馈', slug='feedback', description='产品建议与问题反馈', icon='lightbulb', sort_order=4),
                Category(name='番剧推荐', slug='anime', description='推荐好看的动漫作品', icon='star', sort_order=5),
                Category(name='二次元同人', slug='fanart', description='同人创作与分享', icon='heart', sort_order=6),
            ]

            # Create sample posts
            sample_post = Post(
                title='欢迎来到动漫论坛！🎉',
                content='欢迎大家来到我们的动漫论坛！这里可以讨论各种动漫话题，分享番剧推荐，结交志同道合的朋友。\n\n希望大家在社区里和谐相处，共同维护一个良好的交流环境！',
                user_id=1,
                category_id=1,
                is_pinned=True,
                view_count=520
            )

            post2 = Post(
                title='【推荐】2026年必看番剧清单',
                content='给大家整理了一下2026年值得期待的番剧：\n\n1. 《紫罗兰永恒花园》续作 - 感人至深的治愈系作品\n2. 《鬼灭之刃》第三季 - 热度依旧不减\n3. 《进击的巨人》完结篇 - 必看神作\n4. 《咒术回战》第二季 - 热血战斗番\n5. 《夏日大作战》重制版 - 经典重映\n\n大家最期待哪一部呢？',
                user_id=2,
                category_id=5,
                is_essence=True,
                view_count=888
            )

            post3 = Post(
                title='新手求助：如何开始学习动漫制作？',
                content='最近对动漫制作很感兴趣，但是不知道从何学起。有没有大佬能推荐一下学习路线？\n\n目前会一点PS和AI，想学习原画和动画制作。',
                user_id=3,
                category_id=2,
                view_count=256
            )

            post4 = Post(
                title='分享一些免费的动漫素材网站',
                content='收集了一些好用的免费动漫素材网站，分享给大家：\n\n1. Pixiv - 画师交流平台\n2. Anime Backgrounds - 免费动漫背景素材\n3. OpenMoji - 开源表情包\n4. Kenney - 游戏素材（包含动漫风格）\n\n都是我自己常用的，良心推荐！',
                user_id=4,
                category_id=3,
                view_count=1024
            )

            # Create sample comments
            comment1 = Comment(
                content='太棒了！这个论坛界面好好看！粉粉的主题超级喜欢~',
                post_id=1,
                user_id=2
            )

            comment2 = Comment(
                content='终于找到了一个动漫爱好者聚集地！开心！',
                post_id=1,
                user_id=3
            )

            comment3 = Comment(
                content='谢谢整理！我最期待《咒术回战》第二季，已经等不及了！',
                post_id=2,
                user_id=4
            )

            comment4 = Comment(
                content='《进击的巨人》确实神作！结局太震撼了...',
                post_id=2,
                user_id=1
            )

            comment5 = Comment(
                content='建议先学习绘画基础，然后再学习软件操作。推荐Proko的课程！',
                post_id=3,
                user_id=1
            )

            comment6 = Comment(
                content='这些素材网站太实用了！已收藏！',
                post_id=4,
                user_id=2
            )

            # Create sample announcement
            announcement = Announcement(
                title='🎊 动漫论坛正式上线！',
                content='欢迎使用我们的动漫论坛系统！请遵守社区规则，文明发言，共同维护和谐的讨论氛围~',
                is_pinned=True
            )

            db.session.add_all([
                admin, user, user2, user3
            ] + categories + [
                sample_post, post2, post3, post4,
                comment1, comment2, comment3, comment4, comment5, comment6,
                announcement
            ])
            db.session.commit()

            print("Database initialized with sample data and anime theme!")
