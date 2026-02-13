"""
测试认证API端点

测试用户注册、登录、获取用户信息等功能。
"""

import requests
import json
from typing import Optional

# API基础URL
BASE_URL = 'http://localhost:5000'

# 测试用户数据
TEST_USER = {
    'name': '测试用户',
    'email': 'test@example.com',
    'password': 'Test1234'
}


def print_response(response, title: str):
    """
    打印响应结果

    参数:
        response: requests.Response对象
        title: 响应标题
    """
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    print(f"响应内容:")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(response.text)


def test_health_check():
    """测试健康检查端点"""
    print("\n🔍 测试健康检查端点...")
    response = requests.get(f'{BASE_URL}/api/health')
    print_response(response, "健康检查")
    return response.status_code == 200


def test_register():
    """测试用户注册"""
    print("\n🔍 测试用户注册...")
    response = requests.post(
        f'{BASE_URL}/api/auth/register',
        json=TEST_USER
    )
    print_response(response, "用户注册")

    if response.status_code == 201:
        print("✅ 注册成功")
        return True
    elif response.status_code == 409:
        print("ℹ️  用户已存在（这是正常的）")
        return True
    else:
        print("❌ 注册失败")
        return False


def test_register_invalid_email():
    """测试无效邮箱注册"""
    print("\n🔍 测试无效邮箱注册...")
    response = requests.post(
        f'{BASE_URL}/api/auth/register',
        json={
            'name': '测试用户2',
            'email': 'invalid-email',
            'password': 'Test1234'
        }
    )
    print_response(response, "无效邮箱注册")
    return response.status_code == 400


def test_register_weak_password():
    """测试弱密码注册"""
    print("\n🔍 测试弱密码注册...")
    response = requests.post(
        f'{BASE_URL}/api/auth/register',
        json={
            'name': '测试用户3',
            'email': 'test3@example.com',
            'password': 'weak'
        }
    )
    print_response(response, "弱密码注册")
    return response.status_code == 400


def test_login():
    """测试用户登录"""
    print("\n🔍 测试用户登录...")
    response = requests.post(
        f'{BASE_URL}/api/auth/login',
        json={
            'email': TEST_USER['email'],
            'password': TEST_USER['password']
        }
    )
    print_response(response, "用户登录")

    if response.status_code == 200:
        data = response.json()
        if data.get('success') and 'data' in data:
            token = data['data'].get('access_token')
            print(f"✅ 登录成功，获得Token: {token[:50]}...")
            return token
        else:
            print("❌ 登录失败：响应格式错误")
            return None
    else:
        print("❌ 登录失败")
        return None


def test_login_wrong_password():
    """测试错误密码登录"""
    print("\n🔍 测试错误密码登录...")
    response = requests.post(
        f'{BASE_URL}/api/auth/login',
        json={
            'email': TEST_USER['email'],
            'password': 'WrongPassword123'
        }
    )
    print_response(response, "错误密码登录")
    return response.status_code == 401


def test_get_current_user(token: str):
    """测试获取当前用户信息"""
    print("\n🔍 测试获取当前用户信息...")
    response = requests.get(
        f'{BASE_URL}/api/auth/me',
        headers={
            'Authorization': f'Bearer {token}'
        }
    )
    print_response(response, "获取当前用户")

    if response.status_code == 200:
        data = response.json()
        if data.get('success') and 'data' in data:
            user = data['data'].get('user')
            print(f"✅ 获取用户信息成功: {user.get('name')} ({user.get('email')})")
            return True
        else:
            print("❌ 获取用户信息失败：响应格式错误")
            return False
    else:
        print("❌ 获取用户信息失败")
        return False


def test_get_current_user_no_token():
    """测试无Token获取用户信息"""
    print("\n🔍 测试无Token获取用户信息...")
    response = requests.get(f'{BASE_URL}/api/auth/me')
    print_response(response, "无Token获取用户")
    return response.status_code == 401


def test_get_current_user_invalid_token():
    """测试无效Token获取用户信息"""
    print("\n🔍 测试无效Token获取用户信息...")
    response = requests.get(
        f'{BASE_URL}/api/auth/me',
        headers={
            'Authorization': 'Bearer invalid_token_12345'
        }
    )
    print_response(response, "无效Token获取用户")
    return response.status_code == 401


def test_logout(token: str):
    """测试用户登出"""
    print("\n🔍 测试用户登出...")
    response = requests.post(
        f'{BASE_URL}/api/auth/logout',
        headers={
            'Authorization': f'Bearer {token}'
        }
    )
    print_response(response, "用户登出")
    return response.status_code == 200


def test_verify_token(token: str):
    """测试Token验证"""
    print("\n🔍 测试Token验证...")
    response = requests.post(
        f'{BASE_URL}/api/auth/verify-token',
        headers={
            'Authorization': f'Bearer {token}'
        }
    )
    print_response(response, "Token验证")
    return response.status_code == 200


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 开始测试认证API端点")
    print("="*60)

    results = []

    # 1. 健康检查
    results.append(("健康检查", test_health_check()))

    # 2. 注册测试
    results.append(("用户注册", test_register()))
    results.append(("无效邮箱注册", test_register_invalid_email()))
    results.append(("弱密码注册", test_register_weak_password()))

    # 3. 登录测试
    token = test_login()
    results.append(("用户登录", token is not None))
    results.append(("错误密码登录", test_login_wrong_password()))

    # 如果登录成功，继续测试需要认证的端点
    if token:
        # 4. 获取用户信息测试
        results.append(("获取当前用户", test_get_current_user(token)))
        results.append(("无Token获取用户", test_get_current_user_no_token()))
        results.append(("无效Token获取用户", test_get_current_user_invalid_token()))

        # 5. 登出测试
        results.append(("用户登出", test_logout(token)))

        # 6. Token验证测试
        results.append(("Token验证", test_verify_token(token)))
    else:
        print("\n⚠️  由于登录失败，跳过需要认证的测试")

    # 打印测试结果汇总
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

    print("\n" + "="*60)
    print(f"总计: {passed}/{total} 测试通过 ({passed*100//total}%)")
    print("="*60)

    return passed == total


if __name__ == '__main__':
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器")
        print("请确保后端服务器正在运行: python backend/run.py")
        exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
