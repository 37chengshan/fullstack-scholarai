"""
ScholarAI - 用户设置与统计API验证脚本

快速验证API端点是否正常工作。
"""

import requests
import json
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")


def print_json(data):
    """打印格式化的JSON"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def verify_get_settings(token):
    """验证获取用户设置"""
    print("\n### 1. GET /api/settings - 获取用户设置")
    print("-" * 50)

    response = requests.get(
        f"{BASE_URL}/api/settings",
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ 成功")
        print_json(data)
        return data["data"]
    else:
        print("❌ 失败")
        print(response.text)
        return None


def verify_update_settings(token):
    """验证更新用户设置"""
    print("\n### 2. PUT /api/settings - 更新用户设置")
    print("-" * 50)

    update_data = {
        "theme": "dark",
        "language": "en-US",
        "notification_enabled": False
    }

    print(f"请求数据: {json.dumps(update_data, indent=2)}")

    response = requests.put(
        f"{BASE_URL}/api/settings",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=update_data
    )

    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ 成功")
        print_json(data)
        return data["data"]
    else:
        print("❌ 失败")
        print(response.text)
        return None


def verify_save_api_config(token):
    """验证保存API配置"""
    print("\n### 3. POST /api/settings/api-config - 保存API配置")
    print("-" * 50)

    api_config = {
        "provider": "zhipu",
        "api_key": "test-api-key-12345",
        "model": "glm-4-flash",
        "temperature": 0.7,
        "max_tokens": 2000
    }

    print(f"请求数据: {json.dumps(api_config, indent=2)}")

    response = requests.post(
        f"{BASE_URL}/api/settings/api-config",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=api_config
    )

    print(f"状态码: {response.status_code}")
    if response.status_code in [200, 201]:
        data = response.json()
        print("✅ 成功")
        print_json(data)
        return data["data"]
    else:
        print("❌ 失败")
        print(response.text)
        return None


def verify_get_stats(token):
    """验证获取使用统计"""
    print("\n### 4. GET /api/settings/stats - 获取使用统计")
    print("-" * 50)

    response = requests.get(
        f"{BASE_URL}/api/settings/stats",
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ 成功")
        print_json(data)
        return data["data"]
    else:
        print("❌ 失败")
        print(response.text)
        return None


def main():
    """主验证函数"""
    print("=" * 60)
    print("  ScholarAI - 用户设置与统计API验证")
    print("=" * 60)

    # 登录获取token
    print("\n### 0. 登录获取认证Token")
    print("-" * 50)

    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": "settings_test@example.com",
            "password": "TestPass123"
        }
    )

    if login_response.status_code != 200:
        print("❌ 登录失败，请确保测试用户存在")
        print("\n提示: 可以先运行 test_settings.py 创建测试用户")
        return

    token = login_response.json()["data"]["access_token"]
    print("✅ 登录成功")
    print(f"Token: {token[:20]}...")

    # 验证各个端点
    verify_get_settings(token)
    verify_update_settings(token)
    verify_save_api_config(token)
    verify_get_stats(token)

    print("\n" + "=" * 60)
    print("  验证完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
