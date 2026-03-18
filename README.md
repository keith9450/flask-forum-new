# Flask Forum - 论坛系统

一个基于 Flask 的轻量级论坛系统，支持用户管理、帖子发布、评论互动和管理员后台。

## 功能特性

### 用户系统
- 用户注册与登录
- 个人资料管理
- 修改密码
- 头像展示

### 论坛功能
- 帖子发布、编辑、删除
- 评论与回复
- 帖子点赞
- 分类筛选
- 搜索功能
- 帖子置顶、加精

### 管理后台
- 仪表盘统计
- 用户管理（角色设置、禁用账号）
- 帖子管理（置顶、加精、锁定、删除）
- 分类管理
- 公告管理

### 安全特性
- 密码 bcrypt 哈希加密
- CSRF 防护
- 输入验证与过滤
- 角色权限控制

## 技术栈

- **后端**: Flask 3.0
- **数据库**: SQLite (SQLAlchemy)
- **前端**: HTML5 + CSS3 + JavaScript
- **认证**: Flask-Login
- **表单**: Flask-WTF

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/keith9450/flask-forum.git
cd flask-forum
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行应用
```bash
cd backend
python main.py
```

### 4. 访问应用
- 论坛首页: http://localhost:5000
- 管理后台: http://localhost:5000/admin

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | ForumAdmin2024 | Xk9#mP2$vL7@nQ4w |
| 用户 | DemoUser2024 | Demo@Pass456 |

> ⚠️ **安全提示**: 首次使用后请登录管理后台修改密码！

## 项目结构

```
flask-forum/
├── backend/
│   ├── app/
│   │   ├── models/     # 数据模型
│   │   └── views/       # 路由视图
│   ├── main.py          # 入口文件
│   └── requirements.txt # 依赖
├── frontend/
│   ├── templates/       # HTML模板
│   └── static/          # 静态资源
├── docs/                # 文档
├── .gitignore
├── README.md
└── requirements.txt
```

## 部署

### 本地部署
```bash
cd backend
export FLASK_ENV=production
python main.py
```

### 生产环境
建议使用 Gunicorn + Nginx 部署：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

## 许可证

MIT License
