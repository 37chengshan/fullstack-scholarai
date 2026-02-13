"""
JWT认证中间件测试

测试JWT token生成、验证和用户认证功能。
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def test_generate_token():
    """测试JWT token生成"""
    from middleware.auth import generate_token

    user_id = "test-user-123"
    additional_claims = {"role": "admin", "email": "test@example.com"}

    # 生成token
    token = generate_token(user_id, additional_claims)

    print("✅ 测试1: JWT Token生成")
    print(f"   用户ID: {user_id}")
    print(f"   额外声明: {additional_claims}")
    print(f"   Token前50字符: {token[:50]}...")
    print(f"   Token长度: {len(token)}")

    # 验证token不为空
    assert token, "Token生成失败"
    assert len(token) > 100, "Token长度异常"
    print("   ✓ Token生成成功\n")

    return token


def test_init_jwt():
    """测试JWT管理器初始化"""
    from flask import Flask
    from middleware.auth import init_jwt

    app = Flask(__name__)

    print("✅ 测试2: JWT管理器初始化")
    jwt_manager = init_jwt(app)

    assert jwt_manager is not None, "JWT管理器初始化失败"
    assert app.config['JWT_SECRET_KEY'], "JWT_SECRET_KEY未设置"
    print("   ✓ JWT管理器初始化成功")
    print(f"   ✓ SECRET_KEY已配置: {app.config['JWT_SECRET_KEY'][:10]}...")
    print(f"   ✓ TOKEN过期时间: {app.config['JWT_ACCESS_TOKEN_EXPIRES']}\n")

    return app


def test_jwt_protected_route(app, token):
    """测试受保护的路由"""
    from flask import request
    from middleware.auth import jwt_required_custom, get_current_user_id

    @app.route('/protected')
    @jwt_required_custom()
    def protected_route():
        user_id = get_current_user_id()
        return {'user_id': user_id, 'message': '访问成功'}

    @app.route('/optional')
    @jwt_required_custom(optional=True)
    def optional_route():
        user_id = get_current_user_id()
        return {'user_id': user_id, 'message': '可选认证路由'}

    print("✅ 测试3: JWT保护的路由")

    # 测试不带token的请求
    with app.test_client() as client:
        # 受保护路由 - 无token
        response = client.get('/protected')
        assert response.status_code == 401, "未认证请求应返回401"
        print("   ✓ 受保护路由：无token返回401")

        # 受保护路由 - 有token
        response = client.get(
            '/protected',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200, "有效token应返回200"
        data = response.get_json()
        assert data['user_id'] == "test-user-123", "用户ID不匹配"
        print("   ✓ 受保护路由：有效token返回200")
        print(f"   ✓ 用户ID正确: {data['user_id']}")

        # 可选认证路由 - 无token
        response = client.get('/optional')
        assert response.status_code == 200, "可选认证路由应返回200"
        data = response.get_json()
        assert data['user_id'] is None, "无token时用户ID应为None"
        print("   ✓ 可选认证路由：无token正常访问")

        # 可选认证路由 - 有token
        response = client.get(
            '/optional',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200, "可选认证路由应返回200"
        data = response.get_json()
        assert data['user_id'] == "test-user-123", "用户ID不匹配"
        print("   ✓ 可选认证路由：有token正常访问")
        print()


def test_jwt_errors(app):
    """测试JWT错误处理"""
    print("✅ 测试4: JWT错误处理")

    with app.test_client() as client:
        # 无效token
        response = client.get(
            '/protected',
            headers={'Authorization': 'Bearer invalid-token-12345'}
        )
        assert response.status_code == 401, "无效token应返回401"
        print("   ✓ 无效token返回401")

        # 错误的Authorization格式
        response = client.get(
            '/protected',
            headers={'Authorization': 'InvalidFormat token'}
        )
        assert response.status_code in [401, 422], "错误格式应返回错误"
        print("   ✓ 错误的Authorization格式返回错误")

        # 缺少Authorization头
        response = client.get('/protected')
        assert response.status_code == 401, "缺少Authorization应返回401"
        print("   ✓ 缺少Authorization头返回401")
        print()


def test_utility_functions():
    """测试工具函数"""
    from middleware.auth import get_user_from_token

    print("✅ 测试5: 工具函数")
    print("   ✓ get_user_from_token函数已定义")
    print("   ✓ jwt_required装饰器已定义")
    print("   ✓ generate_token函数已定义")
    print("   ✓ get_current_user_id函数已定义")
    print()


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("JWT认证中间件 - 测试套件")
    print("=" * 60)
    print()

    try:
        # 测试1: Token生成
        token = test_generate_token()

        # 测试2: JWT初始化
        app = test_init_jwt()

        # 测试3: 受保护路由
        test_jwt_protected_route(app, token)

        # 测试4: 错误处理
        test_jwt_errors(app)

        # 测试5: 工具函数
        test_utility_functions()

        print("=" * 60)
        print("✅ 所有测试通过!")
        print("=" * 60)

        return True

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
