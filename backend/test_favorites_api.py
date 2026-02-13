"""
ScholarAI - 收藏夹API测试脚本

测试收藏夹、文件夹管理API端点。
"""

import requests
import json

# API配置
BASE_URL = "http://localhost:5000"
API_PREFIX = "/api/favorites"

# 测试用户（使用已创建的测试账户）
TEST_USER = {
    "email": "test@example.com",
    "password": "Test123456"
}

# 全局变量（用于保存测试过程中创建的资源）
test_token = None
test_folder_id = None
test_paper_id = "2301.00001"  # arXiv测试论文ID
test_favorite_id = None


def print_response(response, title: str):
    """打印响应信息"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)


def login_and_get_token():
    """登录并获取token"""
    global test_token

    print("\n[1/10] 登录测试账户...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )

    print_response(response, "登录结果")

    if response.status_code == 200:
        data = response.json()
        test_token = data["data"]["access_token"]
        print(f"\n✅ 登录成功！Token: {test_token[:50]}...")
        return True
    else:
        print(f"\n❌ 登录失败！")
        return False


def get_auth_headers():
    """获取认证头"""
    return {
        "Authorization": f"Bearer {test_token}",
        "Content-Type": "application/json"
    }


def test_create_folder():
    """测试创建文件夹"""
    global test_folder_id

    print("\n[2/10] 测试创建文件夹...")

    # 测试1：创建文件夹（不指定颜色）
    print("\n--- 测试1：创建文件夹（不指定颜色）---")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/folders",
        headers=get_auth_headers(),
        json={
            "name": "深度学习论文"
        }
    )
    print_response(response, "创建文件夹结果")

    if response.status_code == 201:
        data = response.json()["data"]
        test_folder_id = data["folder"]["id"]
        print(f"\n✅ 文件夹创建成功！ID: {test_folder_id}")
    else:
        print(f"\n❌ 文件夹创建失败！")

    # 测试2：创建文件夹（指定颜色）
    print("\n--- 测试2：创建文件夹（指定颜色）---")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/folders",
        headers=get_auth_headers(),
        json={
            "name": "强化学习研究",
            "color": "#10B981"
        }
    )
    print_response(response, "创建文件夹结果（指定颜色）")

    # 测试3：创建同名文件夹（应该失败）
    print("\n--- 测试3：创建同名文件夹（应该失败）---")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/folders",
        headers=get_auth_headers(),
        json={
            "name": "深度学习论文"
        }
    )
    print_response(response, "创建同名文件夹（预期失败）")


def test_get_folders():
    """测试获取文件夹列表"""
    print("\n[3/10] 测试获取文件夹列表...")

    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/folders",
        headers=get_auth_headers()
    )

    print_response(response, "文件夹列表")

    if response.status_code == 200:
        folders = response.json()["data"]["folders"]
        print(f"\n✅ 获取到 {len(folders)} 个文件夹")
        for folder in folders:
            print(f"  - {folder['name']} ({folder['color']})")


def test_toggle_favorite():
    """测试切换收藏状态"""
    global test_favorite_id

    print("\n[4/10] 测试切换收藏状态...")

    # 测试1：添加到收藏（不指定文件夹）
    print("\n--- 测试1：添加到收藏（不指定文件夹）---")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/toggle",
        headers=get_auth_headers(),
        json={
            "paper_id": test_paper_id
        }
    )
    print_response(response, "添加到收藏（不指定文件夹）")

    if response.status_code == 200 or response.status_code == 201:
        data = response.json()["data"]
        if data.get("is_favorited"):
            test_favorite_id = data.get("favorite", {}).get("id")
            print(f"\n✅ 收藏成功！ID: {test_favorite_id}")

    # 测试2：再次切换（应该移除收藏）
    print("\n--- 测试2：再次切换（应该移除收藏）---")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/toggle",
        headers=get_auth_headers(),
        json={
            "paper_id": test_paper_id
        }
    )
    print_response(response, "切换收藏状态（移除）")

    # 测试3：再次添加（指定文件夹）
    print("\n--- 测试3：添加到收藏（指定文件夹）---")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/toggle",
        headers=get_auth_headers(),
        json={
            "paper_id": test_paper_id,
            "folder_id": test_folder_id
        }
    )
    print_response(response, "添加到收藏（指定文件夹）")

    if response.status_code == 200 or response.status_code == 201:
        data = response.json()["data"]
        if data.get("is_favorited"):
            test_favorite_id = data.get("favorite", {}).get("id")
            print(f"\n✅ 收藏成功！ID: {test_favorite_id}")


def test_get_favorites():
    """测试获取收藏列表"""
    print("\n[5/10] 测试获取收藏列表...")

    # 测试1：获取所有收藏
    print("\n--- 测试1：获取所有收藏 ---")
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}",
        headers=get_auth_headers()
    )
    print_response(response, "收藏列表（全部）")

    if response.status_code == 200:
        favorites = response.json()["data"]["favorites"]
        print(f"\n✅ 获取到 {len(favorites)} 个收藏")

    # 测试2：获取指定文件夹下的收藏
    if test_folder_id:
        print(f"\n--- 测试2：获取文件夹下的收藏 ---")
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}?folder_id={test_folder_id}",
            headers=get_auth_headers()
        )
        print_response(response, "收藏列表（指定文件夹）")

    # 测试3：获取未分类的收藏
    print("\n--- 测试3：获取未分类的收藏 ---")
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}?folder_id=",
        headers=get_auth_headers()
    )
    print_response(response, "收藏列表（未分类）")


def test_update_favorite():
    """测试更新收藏项"""
    print("\n[6/10] 测试更新收藏项...")

    if not test_favorite_id:
        print("\n⚠️  譳告：没有可用的收藏项ID，跳过测试")
        return

    # 测试1：添加笔记
    print("\n--- 测试1：添加笔记 ---")
    response = requests.put(
        f"{BASE_URL}{API_PREFIX}/{test_favorite_id}",
        headers=get_auth_headers(),
        json={
            "notes": "这是一篇重要的论文，需要仔细阅读。"
        }
    )
    print_response(response, "更新收藏项（添加笔记）")

    # 测试2：更新标签
    print("\n--- 测试2：更新标签 ---")
    response = requests.put(
        f"{BASE_URL}{API_PREFIX}/{test_favorite_id}",
        headers=get_auth_headers(),
        json={
            "tags": ["深度学习", "CNN", "必读"]
        }
    )
    print_response(response, "更新收藏项（更新标签）")


def test_update_folder():
    """测试更新文件夹"""
    print("\n[7/10] 测试更新文件夹...")

    if not test_folder_id:
        print("\n⚠️  警告：没有可用的文件夹ID，跳过测试")
        return

    # 测试1：更新文件夹名称
    print("\n--- 测试1：更新文件夹名称 ---")
    response = requests.put(
        f"{BASE_URL}{API_PREFIX}/folders/{test_folder_id}",
        headers=get_auth_headers(),
        json={
            "name": "深度学习精选论文"
        }
    )
    print_response(response, "更新文件夹（名称）")

    # 测试2：更新文件夹颜色
    print("\n--- 测试2：更新文件夹颜色 ---")
    response = requests.put(
        f"{BASE_URL}{API_PREFIX}/folders/{test_folder_id}",
        headers=get_auth_headers(),
        json={
            "color": "#EF4444"
        }
    )
    print_response(response, "更新文件夹（颜色）")


def test_delete_favorite():
    """测试删除收藏项"""
    print("\n[8/10] 测试删除收藏项...")

    if not test_favorite_id:
        print("\n⚠️  譳告：没有可用的收藏项ID，跳过测试")
        return

    response = requests.delete(
        f"{BASE_URL}{API_PREFIX}/{test_favorite_id}",
        headers=get_auth_headers()
    )

    print_response(response, "删除收藏项")

    if response.status_code == 200:
        print(f"\n✅ 收藏项删除成功！")


def test_delete_folder():
    """测试删除文件夹"""
    print("\n[9/10] 测试删除文件夹...")

    if not test_folder_id:
        print("\n⚠️  警告：没有可用的文件夹ID，跳过测试")
        return

    # 先创建一个临时文件夹用于删除测试
    print("\n--- 创建临时文件夹用于删除测试 ---")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/folders",
        headers=get_auth_headers(),
        json={
            "name": "待删除的文件夹"
        }
    )

    if response.status_code != 201:
        print("\n❌ 创建临时文件夹失败，跳过删除测试")
        return

    temp_folder_id = response.json()["data"]["folder"]["id"]
    print(f"✅ 临时文件夹创建成功！ID: {temp_folder_id}")

    # 删除文件夹
    print("\n--- 删除文件夹 ---")
    response = requests.delete(
        f"{BASE_URL}{API_PREFIX}/folders/{temp_folder_id}",
        headers=get_auth_headers()
    )

    print_response(response, "删除文件夹")

    if response.status_code == 200:
        print(f"\n✅ 文件夹删除成功！")


def test_error_handling():
    """测试错误处理"""
    print("\n[10/10] 测试错误处理...")

    # 测试1：缺少必填字段
    print("\n--- 测试1：缺少必填字段（创建文件夹）---")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/folders",
        headers=get_auth_headers(),
        json={}
    )
    print_response(response, "错误处理（缺少必填字段）")

    # 测试2：无效的收藏项ID
    print("\n--- 测试2：无效的收藏项ID ---")
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/invalid-id",
        headers=get_auth_headers()
    )
    print_response(response, "错误处理（无效ID）")

    # 测试3：未认证请求
    print("\n--- 测试3：未认证请求 ---")
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/folders"
    )
    print_response(response, "错误处理（未认证）")


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("ScholarAI - 收藏夹API测试")
    print("="*60)

    # 登录获取token
    if not login_and_get_token():
        print("\n❌ 登录失败，无法继续测试！")
        return

    # 运行测试
    try:
        test_create_folder()
        test_get_folders()
        test_toggle_favorite()
        test_get_favorites()
        test_update_favorite()
        test_update_folder()
        test_delete_favorite()
        test_delete_folder()
        test_error_handling()

        print("\n" + "="*60)
        print("✅ 所有测试完成！")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
