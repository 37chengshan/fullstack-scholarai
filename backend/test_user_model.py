"""
ScholarAI - 用户模型测试

测试用户模型的创建、密码哈希和验证功能。
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user import User, UserStats, UserRole


def test_user_creation():
    """测试用户创建"""
    print("测试 1: 用户创建...")
    user = User(
        email="test@example.com",
        name="Test User",
        password="SecurePass123!"
    )

    assert user.id is not None, "用户ID应该被自动生成"
    assert user.email == "test@example.com", "邮箱应该被正确存储"
    assert user.name == "Test User", "名称应该被正确存储"
    assert user.password_hash is not None, "密码哈希应该被生成"
    assert user.role == UserRole.USER, "默认角色应该是user"
    assert user.is_active is True, "默认状态应该是激活"

    print("  ✅ 用户创建测试通过")
    return user


def test_password_hashing():
    """测试密码哈希"""
    print("\n测试 2: 密码哈希...")
    user = User(
        email="hash@example.com",
        name="Hash Test",
        password="MyPassword123!"
    )

    # 密码哈希不应该等于明文密码
    assert user.password_hash != "MyPassword123!", "密码哈希不应该等于明文密码"

    # 验证密码
    assert user.check_password("MyPassword123!") is True, "正确密码应该通过验证"
    assert user.check_password("WrongPassword") is False, "错误密码应该验证失败"

    print("  ✅ 密码哈希测试通过")


def test_password_update():
    """测试密码更新"""
    print("\n测试 3: 密码更新...")
    user = User(
        email="update@example.com",
        name="Update Test",
        password="OldPassword123!"
    )

    old_hash = user.password_hash

    # 更新密码
    user.set_password("NewPassword456!")

    # 新密码哈希应该不同
    assert user.password_hash != old_hash, "新密码哈希应该不同于旧哈希"
    assert user.check_password("NewPassword456!") is True, "新密码应该可用"
    assert user.check_password("OldPassword123!") is False, "旧密码应该不可用"

    print("  ✅ 密码更新测试通过")


def test_user_stats():
    """测试用户统计"""
    print("\n测试 4: 用户统计...")
    stats = UserStats(
        papers_searched=10,
        favorites_count=5,
        projects_count=2,
        ai_queries_count=15
    )

    user = User(
        email="stats@example.com",
        name="Stats Test",
        password="StatsPassword123!",
        stats=stats
    )

    # 检查统计信息
    assert user.stats.papers_searched == 10, "论文搜索数应该正确"
    assert user.stats.favorites_count == 5, "收藏数应该正确"
    assert user.stats.projects_count == 2, "项目数应该正确"
    assert user.stats.ai_queries_count == 15, "AI查询数应该正确"

    # 更新统计
    user.update_stats(papers_searched=20, favorites_count=10)
    assert user.stats.papers_searched == 20, "统计应该被更新"
    assert user.stats.favorites_count == 10, "统计应该被更新"
    assert user.stats.ai_queries_count == 15, "未更新的统计应该保持不变"

    print("  ✅ 用户统计测试通过")


def test_user_to_dict():
    """测试用户转换为字典"""
    print("\n测试 5: 用户转字典...")
    user = User(
        email="dict@example.com",
        name="Dict Test",
        password="DictPassword123!",
        avatar="https://example.com/avatar.jpg"
    )

    # 转换为字典（不包含敏感信息）
    data = user.to_dict(include_sensitive=False)

    assert data["email"] == "dict@example.com", "邮箱应该在字典中"
    assert data["name"] == "Dict Test", "名称应该在字典中"
    assert "password_hash" not in data, "密码哈希不应该在字典中"
    assert data["avatar"] == "https://example.com/avatar.jpg", "头像应该在字典中"

    # 转换为字典（包含敏感信息）
    data_sensitive = user.to_dict(include_sensitive=True)
    assert "password_hash" in data_sensitive, "密码哈希应该在敏感字典中"

    print("  ✅ 用户转字典测试通过")


def test_user_from_dict():
    """测试从字典创建用户"""
    print("\n测试 6: 从字典创建用户...")
    user_dict = {
        "id": "test-id-123",
        "email": "fromdict@example.com",
        "name": "From Dict Test",
        "password_hash": "hashed_password_value",
        "avatar": "https://example.com/avatar.jpg",
        "role": UserRole.PREMIUM,
        "is_active": True,
        "stats": {
            "papers_searched": 100,
            "favorites_count": 50,
            "projects_count": 10,
            "ai_queries_count": 200
        },
        "created_at": "2025-02-13T12:00:00Z",
        "updated_at": "2025-02-13T12:30:00Z"
    }

    user = User.from_dict(user_dict)

    assert user.id == "test-id-123", "ID应该正确"
    assert user.email == "fromdict@example.com", "邮箱应该正确"
    assert user.name == "From Dict Test", "名称应该正确"
    assert user.password_hash == "hashed_password_value", "密码哈希应该正确"
    assert user.role == UserRole.PREMIUM, "角色应该正确"
    assert user.is_active is True, "激活状态应该正确"
    assert user.stats.papers_searched == 100, "统计应该正确"

    print("  ✅ 从字典创建用户测试通过")


def test_email_normalization():
    """测试邮箱标准化"""
    print("\n测试 7: 邮箱标准化...")
    user1 = User(
        email="  TEST@Example.COM  ",
        name="Email Test",
        password="EmailPassword123!"
    )

    assert user1.email == "test@example.com", "邮箱应该被转换为小写和去除空格"

    print("  ✅ 邮箱标准化测试通过")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("ScholarAI - 用户模型测试")
    print("=" * 60)

    try:
        test_user_creation()
        test_password_hashing()
        test_password_update()
        test_user_stats()
        test_user_to_dict()
        test_user_from_dict()
        test_email_normalization()

        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
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


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
