"""
验证认证API实现

简单检查auth.py路由文件是否正确实现。
"""

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def verify_imports():
    """验证必要的模块是否可以导入"""
    print("🔍 验证模块导入...")

    try:
        from models.user import User, UserRole, UserStats
        print("  ✅ models.user")
    except Exception as e:
        print(f"  ❌ models.user: {e}")
        return False

    try:
        from middleware.auth import generate_token, jwt_required_custom
        print("  ✅ middleware.auth")
    except Exception as e:
        print(f"  ❌ middleware.auth: {e}")
        return False

    try:
        from config.database import get_collection
        print("  ✅ config.database")
    except Exception as e:
        print(f"  ❌ config.database: {e}")
        return False

    try:
        from routes.auth import auth_bp
        print("  ✅ routes.auth")
    except Exception as e:
        print(f"  ❌ routes.auth: {e}")
        return False

    try:
        from app import create_app
        print("  ✅ app")
    except Exception as e:
        print(f"  ❌ app: {e}")
        return False

    return True


def verify_routes():
    """验证路由是否正确注册"""
    print("\n🔍 验证路由注册...")

    try:
        from app import create_app
        app = create_app()

        # 获取所有路由
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes.append(f"{rule.methods} {rule.rule}")

        print("\n已注册的路由:")
        auth_routes = [r for r in routes if '/api/auth' in r]
        for route in sorted(auth_routes):
            print(f"  {route}")

        # 检查必需的路由
        required_routes = [
            'POST /api/auth/register',
            'POST /api/auth/login',
            'GET /api/auth/me',
            'POST /api/auth/logout',
            'POST /api/auth/verify-token'
        ]

        missing_routes = []
        for required in required_routes:
            method, path = required.split(' ', 1)
            # 检查路由是否存在
            found = False
            for route in auth_routes:
                if method in route and path in route:
                    found = True
                    break
            if not found:
                missing_routes.append(required)

        if missing_routes:
            print(f"\n❌ 缺少路由: {missing_routes}")
            return False
        else:
            print("\n✅ 所有必需的路由都已注册")

        return True

    except Exception as e:
        print(f"❌ 验证路由失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_user_model():
    """验证用户模型"""
    print("\n🔍 验证用户模型...")

    try:
        from models.user import User, UserRole, UserStats

        # 测试创建用户
        user = User(
            name="测试用户",
            email="test@test.com",
            password="Test1234"
        )
        print(f"  ✅ 创建用户实例: {user}")

        # 测试密码验证
        assert user.check_password("Test1234"), "密码验证失败"
        assert not user.check_password("wrong"), "错误密码应该返回False"
        print("  ✅ 密码验证功能正常")

        # 测试序列化
        user_dict = user.to_dict(include_sensitive=False)
        assert 'password_hash' not in user_dict, "不应包含密码哈希"
        assert 'id' in user_dict, "应包含用户ID"
        print("  ✅ 用户序列化功能正常")

        # 测试反序列化
        user2 = User.from_dict(user.to_dict(include_sensitive=True))
        assert user2.email == user.email, "反序列化失败"
        print("  ✅ 用户反序列化功能正常")

        return True

    except Exception as e:
        print(f"❌ 用户模型验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_jwt_functions():
    """验证JWT功能"""
    print("\n🔍 验证JWT功能...")

    try:
        from middleware.auth import generate_token

        # 测试token生成
        token = generate_token("test-user-123", {"role": "user"})
        print(f"  ✅ 生成Token: {token[:50]}...")

        return True

    except Exception as e:
        print(f"❌ JWT功能验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("="*60)
    print("🔍 验证认证API实现")
    print("="*60)

    results = []

    # 验证模块导入
    results.append(("模块导入", verify_imports()))

    # 验证用户模型
    results.append(("用户模型", verify_user_model()))

    # 验证JWT功能
    results.append(("JWT功能", verify_jwt_functions()))

    # 验证路由注册
    results.append(("路由注册", verify_routes()))

    # 打印结果
    print("\n" + "="*60)
    print("📊 验证结果")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")

    print("\n" + "="*60)
    print(f"总计: {passed}/{total} 验证通过")
    print("="*60)

    if passed == total:
        print("\n🎉 认证API实现验证通过！")
        print("\n下一步:")
        print("  1. 启动服务器: python backend/run.py")
        print("  2. 运行测试: python backend/test_auth_api.py")
        return True
    else:
        print("\n⚠️  部分验证失败，请检查错误信息")
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
