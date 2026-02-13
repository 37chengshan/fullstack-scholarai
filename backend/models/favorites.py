"""
ScholarAI - 收藏夹数据模型

定义收藏夹、文件夹��相关操作。
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


class Folder:
    """
    文件夹数据模型

    属性:
        id: 文件夹唯一标识符
        name: 文件夹名称
        color: 文件夹颜色标识
        created_by: 创建者用户ID
        created_at: 创建时间
        updated_at: 更新时间
    """

    # 预定义颜色选项（与Project保持一致）
    COLORS = [
        "#3B82F6",  # 蓝色
        "#EF4444",  # 红色
        "#10B981",  # 绿色
        "#F59E0B",  # 橙色
        "#8B5CF6",  # 紫色
        "#EC4899",  # 粉色
        "#06B6D4",  # 青色
        "#84CC16",  # 黄绿色
    ]

    def __init__(
        self,
        name: str,
        created_by: str,
        color: Optional[str] = None,
        folder_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        初始化文件夹实例

        参数:
            name: 文件夹名称
            created_by: 创建者用户ID
            color: 文件夹颜色（可选，默认随机选择）
            folder_id: 文件夹ID（可选，新建时自动生成）
            created_at: 创建时间（可选）
            updated_at: 更新时间（可选）
        """
        import random

        self.id = folder_id or str(uuid.uuid4())
        self.name = name.strip()
        self.color = color or random.choice(self.COLORS)
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update(self, **kwargs) -> None:
        """
        更新文件夹信息

        参数:
            **kwargs: 要更新的字段
        """
        allowed_fields = {"name", "color"}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式

        返回:
            Dict: 文件夹信息字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Folder':
        """
        从字典创建文件夹实例

        参数:
            data: 文件夹数据字典

        返回:
            Folder: 文件夹实例
        """
        return Folder(
            name=data["name"],
            created_by=data["created_by"],
            color=data.get("color"),
            folder_id=data.get("id"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )

    def __repr__(self) -> str:
        """字符串表示"""
        return f"<Folder id={self.id} name={self.name} created_by={self.created_by}>"


class Favorite:
    """
    收藏项数据模型

    属性:
        id: 收藏项唯一标识符
        user_id: 用户ID
        paper_id: 论文ID（arXiv ID）
        folder_id: 文件夹ID（可选，None表示未分类）
        title: 论文标题（冗余存储，便于查询）
        authors: 作者列表（冗余存储）
        notes: 笔记
        tags: 标签
        created_at: 添加时间
    """

    def __init__(
        self,
        user_id: str,
        paper_id: str,
        title: str,
        authors: List[str],
        folder_id: Optional[str] = None,
        notes: str = "",
        tags: Optional[List[str]] = None,
        favorite_id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        """
        初始化收藏项实例

        参数:
            user_id: 用户ID
            paper_id: 论文ID
            title: 论文标题
            authors: 作者列表
            folder_id: 文件夹ID（可选）
            notes: 笔记（可选）
            tags: 标签（可选）
            favorite_id: 收藏项ID（可选，新建时自动生成）
            created_at: 创建时间（可选）
        """
        self.id = favorite_id or str(uuid.uuid4())
        self.user_id = user_id
        self.paper_id = paper_id
        self.title = title
        self.authors = authors or []
        self.folder_id = folder_id  # None表示未分类
        self.notes = notes
        self.tags = tags or []
        self.created_at = created_at or datetime.utcnow()

    def update(self, **kwargs) -> None:
        """
        更新收藏项信息

        参数:
            **kwargs: 要更新的字段
        """
        allowed_fields = {"folder_id", "notes", "tags"}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式

        返回:
            Dict: 收藏项信息字典
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "paper_id": self.paper_id,
            "folder_id": self.folder_id,
            "title": self.title,
            "authors": self.authors,
            "notes": self.notes,
            "tags": self.tags,
            "created_at": self.created_at.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Favorite':
        """
        从字典创建收藏项实例

        参数:
            data: 收藏项数据字典

        返回:
            Favorite: 收藏项实例
        """
        return Favorite(
            user_id=data["user_id"],
            paper_id=data["paper_id"],
            title=data["title"],
            authors=data.get("authors", []),
            folder_id=data.get("folder_id"),
            notes=data.get("notes", ""),
            tags=data.get("tags", []),
            favorite_id=data.get("id"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        )

    def __repr__(self) -> str:
        """字符串表示"""
        return f"<Favorite id={self.id} paper_id={self.paper_id} user_id={self.user_id}>"
