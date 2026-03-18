"""
Main entry point for the Forum application
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("\n" + "="*50)
    print("论坛系统启动中...")
    print("="*50)
    print("\n默认账号信息：")
    print("-" * 40)
    print("管理员: ForumAdmin2024 / Xk9#mP2$vL7@nQ4w")
    print("演示用户: DemoUser2024 / Demo@Pass456")
    print("-" * 40)
    print("\n访问地址: http://localhost:5000")
    print("管理后台: http://localhost:5000/admin")
    print("="*50 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
