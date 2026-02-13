"""
ScholarAI - 项目数据模型

定义项目数据结构和相关操作。
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


class ProjectProgress:
    """项目进度追踪"""

    def __init__(
        self,
        total_papers: int = 0,
        completed_papers: int = 0,
        in_progress_papers: int = 0,
        notes_count: int = 0
    ):
        self.total_papers = total_papers
        self.completed_papers = completed_papers
        self.in_progress_papers = in_progress_papers
        self.notes_count = notes_count

    def to_dict(self) -> Dict[str, int]:
        """转换为字典"""
        return {
            "total_papers": self.total_papers,
            "completed_papers": self.completed_papers,
            "in_progress_papers": self.in_progress_papers,
            "notes_count": self.notes_count,
            "completion_rate": self.completion_rate
        }

    @property
    def completion_rate(self) -> float:
        """计算完成率"""
        if self.total_papers == 0:
            return 0.0
        return round((self.completed_papers / self.total_papers) * 100, 2)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ProjectProgress':
        """从字典创建实例"""
        return ProjectProgress(
            total_papers=data.get("total_papers", 0),
            completed_papers=data.get("completed_papers", 0),
            in_progress_papers=data.get("in_progress_papers", 0),
            notes_count=data.get("notes_count", 0)
        )


class ProjectPaper:
    """项目论文关联"""

    def __init__(
        self,
        paper_id: str,
        title: str,
        authors: List[str],
        status: str = "to_read",  # to_read, in_progress, completed
        notes: str = "",
        tags: List[str] = None,
        added_at: Optional[datetime] = None
    ):
        self.paper_id = paper_id
        self.title = title
        self.authors = authors or []
        self.status = status
        self.notes = notes
        self.tags = tags or []
        self.added_at = added_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": self.authors,
            "status": self.status,
            "notes": self.notes,
            "tags": self.tags,
            "added_at": self.added_at.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ProjectPaper':
        """从字典创建实例"""
        return ProjectPaper(
            paper_id=data["paper_id"],
            title=data["title"],
            authors=data.get("authors", []),
            status=data.get("status", "to_read"),
            notes=data.get("notes", ""),
            tags=data.get("tags", []),
            added_at=datetime.fromisoformat(data["added_at"]) if data.get("added_at") else None
        )


class Project:
    """
    项目数据模型

    属性:
        id: 项目唯一标识符
        name: 项目名称
        color: 项目颜色标识（十六进制颜色代码）
        description: 项目描述
        created_by: 创建者用户ID
        papers: 项目中的论文列表
        progress: 项目进度统计
        tags: 项目标签
        is_public: 是否公开
        created_at: 创建时间
        updated_at: 更新时间
    """

    # 预定义颜色选项
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
        description: Optional[str] = None,
        papers: Optional[List[ProjectPaper]] = None,
        progress: Optional[ProjectProgress] = None,
        tags: Optional[List[str]] = None,
        is_public: bool = False,
        project_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        初始化项目实例

        参数:
            name: 项目名称
            created_by: 创建者用户ID
            color: 项目颜色（可选，默认随机选择）
            description: 项目描述（可选）
            papers: 项目中的论文列表（可选）
            progress: 项目进度（可选）
            tags: 项目标签（可选）
            is_public: 是否公开（默认为False）
            project_id: 项目ID（可选，新建时自动生成）
            created_at: 创建时间（可选）
            updated_at: 更新时间（可选）
        """
        import random

        self.id = project_id or str(uuid.uuid4())
        self.name = name.strip()
        self.color = color or random.choice(self.COLORS)
        self.description = description or ""
        self.created_by = created_by
        self.papers = papers or []
        self.progress = progress or ProjectProgress()
        self.tags = tags or []
        self.is_public = is_public
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def add_paper(
        self,
        paper_id: str,
        title: str,
        authors: List[str],
        status: str = "to_read"
    ) -> None:
        """
        添加论文到项目

        参数:
            paper_id: 论文ID（arXiv ID）
            title: 论文标题
            authors: 作者列表
            status: 论文状态（to_read, in_progress, completed）
        """
        # 检查论文是否已存在
        for paper in self.papers:
            if paper.paper_id == paper_id:
                raise ValueError(f"Paper {paper_id} already exists in project")

        paper = ProjectPaper(
            paper_id=paper_id,
            title=title,
            authors=authors,
            status=status
        )
        self.papers.append(paper)
        self._update_progress()
        self.updated_at = datetime.utcnow()

    def remove_paper(self, paper_id: str) -> bool:
        """
        从项目移除论文

        参数:
            paper_id: 论文ID

        返回:
            bool: 是否成功移除
        """
        original_length = len(self.papers)
        self.papers = [p for p in self.papers if p.paper_id != paper_id]

        if len(self.papers) < original_length:
            self._update_progress()
            self.updated_at = datetime.utcnow()
            return True
        return False

    def update_paper_status(self, paper_id: str, status: str) -> bool:
        """
        更新论文状态

        参数:
            paper_id: 论文ID
            status: 新状态（to_read, in_progress, completed）

        返回:
            bool: 是否成功更新
        """
        for paper in self.papers:
            if paper.paper_id == paper_id:
                paper.status = status
                self._update_progress()
                self.updated_at = datetime.utcnow()
                return True
        return False

    def add_note_to_paper(self, paper_id: str, note: str) -> bool:
        """
        为论文添加笔记

        参数:
            paper_id: 论文ID
            note: 笔记内容

        返回:
            bool: 是否成功添加
        """
        for paper in self.papers:
            if paper.paper_id == paper_id:
                paper.notes += f"\n\n{note}" if paper.notes else note
                self.progress.notes_count += 1
                self.updated_at = datetime.utcnow()
                return True
        return False

    def _update_progress(self) -> None:
        """更新项目进度统计"""
        self.progress.total_papers = len(self.papers)
        self.progress.completed_papers = sum(
            1 for p in self.papers if p.status == "completed"
        )
        self.progress.in_progress_papers = sum(
            1 for p in self.papers if p.status == "in_progress"
        )

    def update(self, **kwargs) -> None:
        """
        更新项目信息

        参数:
            **kwargs: 要更新的字段
        """
        allowed_fields = {"name", "color", "description", "tags", "is_public"}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def to_dict(self, include_papers: bool = True) -> Dict[str, Any]:
        """
        转换为字典格式

        参数:
            include_papers: 是否包含论文列表

        返回:
            Dict: 项目信息字典
        """
        data = {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "description": self.description,
            "created_by": self.created_by,
            "progress": self.progress.to_dict(),
            "tags": self.tags,
            "is_public": self.is_public,
            "papers_count": len(self.papers),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

        if include_papers:
            data["papers"] = [paper.to_dict() for paper in self.papers]

        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Project':
        """
        从字典创建项目实例

        参数:
            data: 项目数据字典

        返回:
            Project: 项目实例
        """
        papers = [
            ProjectPaper.from_dict(p) for p in data.get("papers", [])
        ] if "papers" in data else None

        return Project(
            name=data["name"],
            created_by=data["created_by"],
            color=data.get("color"),
            description=data.get("description"),
            papers=papers,
            progress=ProjectProgress.from_dict(data.get("progress", {}))
                if data.get("progress") else None,
            tags=data.get("tags"),
            is_public=data.get("is_public", False),
            project_id=data.get("id"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )

    def __repr__(self) -> str:
        """字符串表示"""
        return f"<Project id={self.id} name={self.name} created_by={self.created_by}>"
