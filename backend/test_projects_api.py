"""
ScholarAI - 项目API测试

测试项目CRUD API的所有端点。
运行方式:
    python test_projects_api.py
"""

import requests
import json
from datetime import datetime

# API配置
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "email": "test_projects@example.com",
    "password": "Test123456",
    "name": "Test User"
}


def print_section(title: str):
    """打印测试章节标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def print_test(name: str, passed: bool, details: str = ""):
    """打印测试结果"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"    {details}")


def register_and_login():
    """注册并登录测试用户"""
    print_section("Step 1: 用户注册与登录")

    # 尝试注册
    response = requests.post(f"{BASE_URL}/api/auth/register", json=TEST_USER)
    if response.status_code == 201:
        print_test("用户注册", True, f"用户 {TEST_USER['email']} 已创建")
    elif response.status_code == 409:
        print_test("用户已存在", True, "使用现有用户")
    else:
        print_test("用户注册", False, f"状态码: {response.status_code}, {response.text}")
        return None

    # 登录
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })

    if response.status_code == 200:
        data = response.json()
        token = data["data"]["access_token"]
        print_test("用户登录", True, f"获取到token: {token[:20]}...")
            return token
    else:
        print_test("用户登录", False, f"状态码: {response.status_code}, {response.text}")
        return None


def test_create_project(token: str):
    """测试创建项目"""
    print_section("Step 2: 创建项目")

    headers = {"Authorization": f"Bearer {token}"}
    project_data = {
        "name": "深度学习研究",
        "color": "#3B82F6",
        "description": "关于深度学习的最新研究进展",
        "tags": ["深度学习", "AI"]
    }

    response = requests.post(
        f"{BASE_URL}/api/projects",
        json=project_data,
        headers=headers
    )

    if response.status_code == 201:
        data = response.json()
        project = data["data"]["project"]
        print_test("创建项目", True, f"项目ID: {project['id']}")
        return project
    else:
        print_test("创建项目", False, f"状态码: {response.status_code}, {response.text}")
        return None


def test_get_projects(token: str):
    """测试获取项目列表"""
    print_section("Step 3: 获取项目列表")

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{BASE_URL}/api/projects",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        projects = data["data"]["projects"]
        print_test("获取项目列表", True, f"找到 {len(projects)} 个项目")
        return projects
    else:
        print_test("获取项目列表", False, f"状态码: {response.status_code}, {response.text}")
        return []


def test_get_project(project_id: str, token: str):
    """测试获取单个项目详情"""
    print_section("Step 4: 获取项目详情")

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{BASE_URL}/api/projects/{project_id}",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        project = data["data"]["project"]
        print_test("获取项目详情", True, f"项目: {project['name']}")
        return project
    else:
        print_test("获取项目详情", False, f"状态码: {response.status_code}, {response.text}")
        return None


def test_add_paper_to_project(project_id: str, token: str):
    """测试添加论文到项目"""
    print_section("Step 5: 添加论文到项目")

    headers = {"Authorization": f"Bearer {token}"}
    paper_data = {
        "paper_id": "2301.00001",
        "title": "Attention Is All You Need",
        "authors": ["Vaswani et al."],
        "status": "to_read"
    }

    response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/papers",
        json=paper_data,
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        project = data["data"]["project"]
        print_test("添加论文", True, f"论文数: {project['papers_count']}")
        return True
    else:
        print_test("添加论文", False, f"状态码: {response.status_code}, {response.text}")
        return False


def test_update_paper_status(project_id: str, token: str):
    """测试更新论文状态"""
    print_section("Step 6: 更新论文状态")

    headers = {"Authorization": f"Bearer {token}"}
    status_data = {"status": "in_progress"}

    response = requests.put(
        f"{BASE_URL}/api/projects/{project_id}/papers/2301.00001/status",
        json=status_data,
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        project = data["data"]["project"]
        progress = project["progress"]
        print_test("更新论文状态", True,
                  f"完成度: {progress['completion_rate']}%, "
                  f"进行中: {progress['in_progress_papers']}")
        return True
    else:
        print_test("更新论文状态", False, f"状态码: {response.status_code}, {response.text}")
        return False


def test_update_project(project_id: str, token: str):
    """测试更新项目"""
    print_section("Step 7: 更新项目")

    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "name": "深度学习与Transformer研究",
        "description": "更新后的描述",
        "tags": ["深度学习", "Transformer", "NLP"]
    }

    response = requests.put(
        f"{BASE_URL}/api/projects/{project_id}",
        json=update_data,
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        project = data["data"]["project"]
        print_test("更新项目", True, f"新名称: {project['name']}")
        return True
    else:
        print_test("更新项目", False, f"状态码: {response.status_code}, {response.text}")
        return False


def test_remove_paper_from_project(project_id: str, token: str):
    """测试从项目移除论文"""
    print_section("Step 8: 从项目移除论文")

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.delete(
        f"{BASE_URL}/api/projects/{project_id}/papers/2301.00001",
        headers=headers
    )

    if response.status_code == 200:
        print_test("移除论文", True, "论文已从项目中移除")
        return True
    else:
        print_test("移除论文", False, f"状态码: {response.status_code}, {response.text}")
        return False


def test_delete_project(project_id: str, token: str):
    """测试删除项目"""
    print_section("Step 9: 删除项目")

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.delete(
        f"{BASE_URL}/api/projects/{project_id}",
        headers=headers
    )

    if response.status_code == 200:
        print_test("删除项目", True, "项目已删除")

        # 验证删除
        response = requests.get(
            f"{BASE_URL}/api/projects/{project_id}",
            headers=headers
        )
        if response.status_code == 404:
            print_test("验证删除", True, "项目已不存在")
        else:
            print_test("验证删除", False, "项目仍然存在")
        return True
    else:
        print_test("删除项目", False, f"状态码: {response.status_code}, {response.text}")
        return False


def test_create_multiple_projects(token: str):
    """测试创建多个项目"""
    print_section("Step 10: 创建多个项目")

    headers = {"Authorization": f"Bearer {token}"}
    projects = [
        {"name": "计算机视觉", "color": "#EF4444", "tags": ["CV", "图像"]},
        {"name": "自然语言处理", "color": "#10B981", "tags": ["NLP", "文本"]},
        {"name": "强化学习", "color": "#F59E0B", "tags": ["RL", "强化学习"]}
    ]

    project_ids = []
    for project_data in projects:
        response = requests.post(
            f"{BASE_URL}/api/projects",
            json=project_data,
            headers=headers
        )
        if response.status_code == 201:
            data = response.json()
            project_id = data["data"]["project"]["id"]
            project_ids.append(project_id)
            print_test(f"创建项目: {project_data['name']}", True)
        else:
            print_test(f"创建项目: {project_data['name']}", False, response.text)

    return project_ids


def test_filter_and_sort_projects(token: str):
    """测试项目过滤和排序"""
    print_section("Step 11: 过滤和排序项目")

    headers = {"Authorization": f"Bearer {token}"}

    # 按名称排序
    response = requests.get(
        f"{BASE_URL}/api/projects?sort_by=name&order=asc",
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        projects = data["data"]["projects"]
        print_test("按名称排序", True, f"首个项目: {projects[0]['name'] if projects else 'N/A'}")
    else:
        print_test("按名称排序", False, response.text)

    # 按标签过滤
    response = requests.get(
        f"{BASE_URL}/api/projects?tags=NLP",
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        projects = data["data"]["projects"]
        print_test("按标签过滤", True, f"找到 {len(projects)} 个NLP相关项目")
    else:
        print_test("按标签过滤", False, response.text)


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  ScholarAI - 项目API测试套件")
    print("=" * 60)

    try:
        # Step 1: 注册/登录
        token = register_and_login()
        if not token:
            print("\n❌ 测试失败: 无法获取认证token")
            return

        # Step 2: 创建项目
        project = test_create_project(token)
        if not project:
            print("\n❌ 测试失败: 无法创建项目")
            return

        project_id = project["id"]

        # Step 3: 获取项目列表
        test_get_projects(token)

        # Step 4: 获取项目详情
        test_get_project(project_id, token)

        # Step 5: 添加论文
        test_add_paper_to_project(project_id, token)

        # Step 6: 更新论文状态
        test_update_paper_status(project_id, token)

        # Step 7: 更新项目
        test_update_project(project_id, token)

        # Step 8: 移除论文
        test_remove_paper_from_project(project_id, token)

        # Step 9: 删除项目
        test_delete_project(project_id, token)

        # Step 10: 创建多个项目
        project_ids = test_create_multiple_projects(token)

        # Step 11: 过滤和排序
        if project_ids:
            test_filter_and_sort_projects(token)

            # 清理测试项目
            print_section("清理测试项目")
            for pid in project_ids:
                requests.delete(f"{BASE_URL}/api/projects/{pid}", headers=headers)

        print_section("测试完成")
        print("✓ 所有测试执行完毕")

    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器")
        print(f"   请确保后端服务器正在运行: {BASE_URL}")
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {e}")


if __name__ == "__main__":
    run_all_tests()
