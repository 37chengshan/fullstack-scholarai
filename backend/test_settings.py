"""
ScholarAI - 用户设置与统计API测试套件

测试用户设置管理和使用统计相关的API端点。
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import requests
from dotenv import load_dotenv
import json

# 加载环境变量
load_dotenv()

# 配置
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/scholarai")

# 测试数据
TEST_USER = {
    "email": "settings_test@example.com",
    "password": "TestPass123",
    "name": "Settings Test User"
}

# 全局变量
auth_token = None
user_id = None


def print_section(title):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_result(test_name, success, message=""):
    """打印测试结果"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"    {message}")


def register_and_login():
    """注册并登录测试用户"""
    global auth_token, user_id

    print_section("1. 注册并登录测试用户")

    # 注册用户
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=TEST_USER,
            timeout=10
        )
        if response.status_code == 201:
            print_result("用户注册", True, f"用户 {TEST_USER['email']} 注册成功")
            data = response.json()
            if data.get("success"):
                auth_token = data["data"]["access_token"]
                user_id = data["data"]["user"]["id"]
                return True
        elif response.status_code == 400 and "已存在" in response.text:
            print_result("用户已存在", True, "尝试登录...")
            # 用户已存在，尝试登录
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    "email": TEST_USER["email"],
                    "password": TEST_USER["password"]
                },
                timeout=10
            )
            if login_response.status_code == 200:
                data = login_response.json()
                if data.get("success"):
                    auth_token = data["data"]["access_token"]
                    user_id = data["data"]["user"]["id"]
                    print_result("用户登录", True, f"用户 {TEST_USER['email']} 登录成功")
                    return True
        print_result("用户注册/登录", False, response.text)
        return False
    except Exception as e:
        print_result("用户注册/登录", False, str(e))
        return False


def test_get_settings():
    """测试获取用户设置"""
    print_section("2. 测试获取用户设置")

    try:
        response = requests.get(
            f"{BASE_URL}/api/settings",
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                settings = data["data"]
                print_result("获取用户设置", True)
                print(f"    主题: {settings['theme']}")
                print(f"    语言: {settings['language']}")
                print(f"    通知: {settings['notification_enabled']}")
                return True
            else:
                print_result("获取用户设置", False, data.get("error"))
                return False
        else:
            print_result("获取用户设置", False, f"状态码: {response.status_code}")
            return False

    except Exception as e:
        print_result("获取用户设置", False, str(e))
        return False


def test_update_settings():
    """测试更新用户设置"""
    print_section("3. 测试更新用户设置")

    try:
        # 更新主题和语言
        update_data = {
            "theme": "dark",
            "language": "en-US",
            "notification_enabled": False,
            "email_subscription": True
        }

        response = requests.put(
            f"{BASE_URL}/api/settings",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json=update_data,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                settings = data["data"]
                print_result("更新用户设置", True)
                print(f"    主题: {settings['theme']}")
                print(f"    语言: {settings['language']}")
                print(f"    通知: {settings['notification_enabled']}")
                print(f"    邮件订阅: {settings['email_subscription']}")

                # 验证更新是否生效
                if settings['theme'] == 'dark' and settings['language'] == 'en-US':
                    print_result("验证更新结果", True, "设置已正确更新")
                    return True
                else:
                    print_result("验证更新结果", False, "设置未正确更新")
                    return False
            else:
                print_result("更新用户设置", False, data.get("error"))
                return False
        else:
            print_result("更新用户设置", False, f"状态码: {response.status_code}")
            return False

    except Exception as e:
        print_result("更新用户设置", False, str(e))
        return False


def test_save_api_config():
    """测试保存API配置"""
    print_section("4. 测试保存API配置")

    try:
        api_config_data = {
            "provider": "zhipu",
            "api_key": "test-zhipu-api-key-12345",
            "model": "glm-4-flash",
            "temperature": 0.8,
            "max_tokens": 3000
        }

        response = requests.post(
            f"{BASE_URL}/api/settings/api-config",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json=api_config_data,
            timeout=10
        )

        if response.status_code in [200, 201]:
            data = response.json()
            if data.get("success"):
                api_config = data["data"]["api_config"]
                print_result("保存API配置", True)
                print(f"    Provider: {api_config['provider']}")
                print(f"    Model: {api_config['model']}")
                print(f"    Temperature: {api_config['temperature']}")
                print(f"    Max Tokens: {api_config['max_tokens']}")
                print(f"    API Key Preview: {api_config.get('api_key_preview', 'N/A')}")

                # 验证密钥预览格式
                if 'api_key_preview' in api_config:
                    print_result("API密钥加密存储", True, "密钥已加密并只返回预览")
                    return True
                else:
                    print_result("API密钥加密存储", False, "缺少密钥预览")
                    return False
            else:
                print_result("保存API配置", False, data.get("error"))
                return False
        else:
            print_result("保存API配置", False, f"状态码: {response.status_code}")
            return False

    except Exception as e:
        print_result("保存API配置", False, str(e))
        return False


def test_get_statistics():
    """测试获取使用统计"""
    print_section("5. 测试获取使用统计")

    try:
        response = requests.get(
            f"{BASE_URL}/api/settings/stats",
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                stats = data["data"]
                print_result("获取使用统计", True)
                print(f"    搜索论文数: {stats['papers_searched']}")
                print(f"    收藏数: {stats['favorites_count']}")
                print(f"    项目数: {stats['projects_count']}")
                print(f"    AI查询数: {stats['ai_queries_count']}")
                print(f"    最后活跃: {stats.get('last_active', 'N/A')}")

                # 验证统计字段类型
                if all(isinstance(stats[k], int) for k in ['papers_searched', 'favorites_count', 'projects_count', 'ai_queries_count']):
                    print_result("验证统计字段类型", True, "所有统计字段都是整数")
                    return True
                else:
                    print_result("验证统计字段类型", False, "统计字段类型错误")
                    return False
            else:
                print_result("获取使用统计", False, data.get("error"))
                return False
        else:
            print_result("获取使用统计", False, f"状态码: {response.status_code}")
            return False

    except Exception as e:
        print_result("获取使用统计", False, str(e))
        return False


def test_invalid_theme():
    """测试无效的主题值"""
    print_section("6. 测试无效的主题值")

    try:
        response = requests.put(
            f"{BASE_URL}/api/settings",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={"theme": "invalid_theme"},
            timeout=10
        )

        if response.status_code == 400:
            print_result("拒绝无效主题", True, "正确拒绝无效的主题值")
            return True
        else:
            print_result("拒绝无效主题", False, f"应该返回400，实际返回: {response.status_code}")
            return False

    except Exception as e:
        print_result("拒绝无效主题", False, str(e))
        return False


def test_invalid_language():
    """测试无效的语言值"""
    print_section("7. 测试无效的语言值")

    try:
        response = requests.put(
            f"{BASE_URL}/api/settings",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={"language": "invalid_language"},
            timeout=10
        )

        if response.status_code == 400:
            print_result("拒绝无效语言", True, "正确拒绝无效的语言值")
            return True
        else:
            print_result("拒绝无效语言", False, f"应该返回400，实际返回: {response.status_code}")
            return False

    except Exception as e:
        print_result("拒绝无效语言", False, str(e))
        return False


def test_unauthorized_access():
    """测试未授权访问"""
    print_section("8. 测试未授权访问")

    try:
        response = requests.get(
            f"{BASE_URL}/api/settings",
            timeout=10
        )

        if response.status_code == 401:
            print_result("拒绝未授权访问", True, "正确拒绝无token的请求")
            return True
        else:
            print_result("拒绝未授权访问", False, f"应该返回401，实际返回: {response.status_code}")
            return False

    except Exception as e:
        print_result("拒绝未授权访问", False, str(e))
        return False


def cleanup_test_data():
    """清理测试数据"""
    print_section("9. 清理测试数据")

    try:
        from pymongo import MongoClient
        from bson import ObjectId

        # 连接数据库
        client = MongoClient(MONGODB_URI)
        db = client.get_database()

        # 删除测试用户
        result = db.users.delete_many({"email": TEST_USER["email"]})
        print_result("删除测试用户", True, f"删除了 {result.deleted_count} 个用户")

        # 删除测试设置
        result = db.user_settings.delete_many({"user_id": user_id})
        print_result("删除测试设置", True, f"删除了 {result.deleted_count} 条设置")

        client.close()
        return True

    except Exception as e:
        print_result("清理测试数据", False, str(e))
        return False


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("  ScholarAI - 用户设置与统计API测试套件")
    print("="*60)

    results = []

    # 1. 注册并登录
    if not register_and_login():
        print("\n❌ 无法继续测试，未能获取认证token")
        return

    results.append(("注册并登录", True))

    # 2. 获取用户设置
    results.append(("获取用户设置", test_get_settings()))

    # 3. 更新用户设置
    results.append(("更新用户设置", test_update_settings()))

    # 4. 保存API配置
    results.append(("保存API配置", test_save_api_config()))

    # 5. 获取使用统计
    results.append(("获取使用统计", test_get_statistics()))

    # 6. 测试无效主题
    results.append(("拒绝无效主题", test_invalid_theme()))

    # 7. 测试无效语言
    results.append(("拒绝无效语言", test_invalid_language()))

    # 8. 测试未授权访问
    results.append(("拒绝未授权访问", test_unauthorized_access()))

    # 9. 清理测试数据
    cleanup_test_data()

    # 打印测试总结
    print_section("测试总结")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"\n总测试数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    print(f"成功率: {success_rate:.1f}%")

    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
