"""
ScholarAI - 用户数据模型

定义用户数据结构和相关操作。
"""

from datetime import datetime
from typing import Optional, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


class UserRole:
    """用户角色枚举"""
    USER = "user"
    ADMIN = "admin"
    PREMIUM = "premium"


class UserStats:
    """用户统计信息"""
    def __init__(
        self,
        papers_searched: int = 0,
        favorites_count: int = 0,
        projects_count: int = 0,
        ai_queries_count: int = 0
    ):
        self.papers_searched = papers_searched
        self.favorites_count = favorites_count
        self.projects_count = projects_count
        self.ai_queries_count = ai_queries_count

    def to_dict(self) -> Dict[str, int]:
        """转换为字典"""
        return {
            "papers_searched": self.papers_searched,
            "favorites_count": self.favorites_count,
            "projects_count": self.projects_count,
            "ai_queries_count": self.ai_queries_count
        }

    @staticmethod
    def from_dict(data: Dict[str, int]) -> 'UserStats':
        """从字典创建实例"""
        return UserStats(
            papers_searched=data.get("papers_searched", 0),
            favorites_count=data.get("favorites_count", 0),
            projects_count=data.get("projects_count", 0),
            ai_queries_count=data.get("ai_queries_count", 0)
        )


class User:
    """
    用户数据模型

    属性:
        id: 用户唯一标识符
        email: 用户邮箱（唯一）
        name: 用户名称
        password_hash: 密码哈希值
        avatar: 头像URL
        role: 用户角色
        is_active: 账户是否激活
        stats: 用户统计信息
        created_at: ���建时间
        updated_at: 更新时间
    """

    def __init__(
        self,
        email: str,
        name: str,
        password: str,
        avatar: Optional[str] = None,
        role: str = UserRole.USER,
        is_active: bool = True,
        stats: Optional[UserStats] = None,
        user_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        初始化用户实例

        参数:
            email: 用户邮箱
            name: 用户名称
            password: 明文密码（将被自动哈希）
            avatar: 头像URL（可选）
            role: 用户角色（默认为user）
            is_active: 账户是否激活（默认为True）
            stats: 用户统计信息（可选）
            user_id: 用户ID（可选，新建时自动生成）
            created_at: 创建时间（可选）
            updated_at: 更新时间（可选）
        """
        self.id = user_id or str(uuid.uuid4())
        self.email = email.lower().strip()
        self.name = name.strip()
        self.password_hash = generate_password_hash(password)
        self.avatar = avatar
        self.role = role
        self.is_active = is_active
        self.stats = stats or UserStats()
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def set_password(self, password: str) -> None:
        """
        设置新密码

        参数:
            password: 明文密码
        """
        self.password_hash = generate_password_hash(password)
        self.updated_at = datetime.utcnow()

    def check_password(self, password: str) -> bool:
        """
        验证密码

        参数:
            password: 明文密码

        返回:
            bool: 密码是否正确
        """
        return check_password_hash(self.password_hash, password)

    def update_stats(self, **kwargs) -> None:
        """
        更新用户统计信息

        参数:
            **kwargs: 要更新的统计字段
        """
        for key, value in kwargs.items():
            if hasattr(self.stats, key):
                setattr(self.stats, key, value)
        self.updated_at = datetime.utcnow()

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        转换为字典格式

        参数:
            include_sensitive: 是否包含敏感信息（如密码哈希）

        返回:
            Dict: 用户信息字典
        """
        data = {
            "email": self.email,
            "name": self.name,
            "avatar": self.avatar,
            "role": self.role,
            "is_active": self.is_active,
            "stats": self.stats.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

        if include_sensitive:
            data["password_hash"] = self.password_hash

        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'User':
        """
        从字典创建用户实例

        参数:
            data: 用户数据字典

        返回:
            User: 用户实例
        """
        # 注意：从数据库加载时，密码已经是哈希值，不需要重新哈希
        user = User(
            email=data["email"],
            name=data["name"],
            password="",  # 密码将在下面直接设置
            avatar=data.get("avatar"),
            role=data.get("role", UserRole.USER),
            is_active=data.get("is_active", True),
            stats=UserStats.from_dict(data.get("stats", {})),
            user_id=data.get("id"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )

        # 直接设置密码哈希（不重新哈希）
        if "password_hash" in data:
            user.password_hash = data["password_hash"]
        elif "password" in data:
            # 如果有明文密码（通常只在注册时），则进行哈希
            user.password_hash = generate_password_hash(data["password"])

        return user

    def __repr__(self) -> str:
        """字符串表示"""
        return f"<User id={self.id} email={self.email} name={self.name}>"
