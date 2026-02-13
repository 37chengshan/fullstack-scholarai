"""
ScholarAI - 项目API验证脚本

快速验证项目API端点是否正常工作。
"""

import sys
import os

# 添加backend路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.project import Project, ProjectPaper, ProjectProgress


def test_project_model():
    """测试项目模型"""
    print("Testing Project Model...")

    # 创建项目
    project = Project(
        name="测试项目",
        created_by="user123",
        color="#3B82F6",
        description="这是一个测试项目",
        tags=["测试", "AI"]
    )

    # 添加论文
    project.add_paper(
        paper_id="2301.00001",
        title="Test Paper",
        authors=["Author 1", "Author 2"],
        status="to_read"
    )

    # 更新论文状态
    project.update_paper_status("2301.00001", "in_progress")

    # 添加笔记
    project.add_note_to_paper("2301.00001", "这是我的笔记")

    # 测试序列化
    data = project.to_dict()
    assert data["name"] == "测试项目"
    assert data["created_by"] == "user123"
    assert data["papers_count"] == 1
    assert data["progress"]["in_progress_papers"] == 1
    assert data["progress"]["notes_count"] == 1

    # 测试反序列化
    project2 = Project.from_dict(data)
    assert project2.id == project.id
    assert project2.name == project.name

    print("✓ Project model tests passed")

    # 测试论文状态更新
    project.update_paper_status("2301.00001", "completed")
    assert project.progress.completed_papers == 1
    assert project.progress.in_progress_papers == 0
    assert project.progress.completion_rate == 100.0

    print("✓ Progress calculation tests passed")

    # 测试移除论文
    removed = project.remove_paper("2301.00001")
    assert removed == True
    assert project.papers_count == 0

    print("✓ Paper removal tests passed")


def test_project_paper_model():
    """测试论文模型"""
    print("\nTesting ProjectPaper Model...")

    paper = ProjectPaper(
        paper_id="2301.00002",
        title="Another Test Paper",
        authors=["Author"],
        status="to_read",
        tags=["tag1", "tag2"]
    )

    # 测试序列化
    data = paper.to_dict()
    assert data["paper_id"] == "2301.00002"
    assert data["status"] == "to_read"

    # 测试反序列化
    paper2 = ProjectPaper.from_dict(data)
    assert paper2.paper_id == paper.paper_id
    assert paper2.title == paper.title

    print("✓ ProjectPaper model tests passed")


def test_project_progress_model():
    """测试进度模型"""
    print("\nTesting ProjectProgress Model...")

    progress = ProjectProgress(
        total_papers=10,
        completed_papers=5,
        in_progress_papers=3,
        notes_count=7
    )

    # 测试完成率计算
    assert progress.completion_rate == 50.0

    # 测试序列化
    data = progress.to_dict()
    assert data["total_papers"] == 10
    assert data["completion_rate"] == 50.0

    # 测试反序列化
    progress2 = ProjectProgress.from_dict(data)
    assert progress2.total_papers == progress.total_papers

    # 测试边界情况
    empty_progress = ProjectProgress()
    assert empty_progress.completion_rate == 0.0

    print("✓ ProjectProgress model tests passed")


def test_validation():
    """测试验证逻辑"""
    print("\nTesting Validation...")

    project = Project(
        name="验证项目",
        created_by="user123"
    )

    # 测试重复添加论文
    project.add_paper("2301.00001", "Paper", ["Author"])
    try:
        project.add_paper("2301.00001", "Paper", ["Author"])
        assert False, "Should raise ValueError for duplicate paper"
    except ValueError as e:
        assert "already exists" in str(e)

    print("✓ Validation tests passed")


def test_default_values():
    """测试默认值"""
    print("\nTesting Default Values...")

    project = Project(
        name="默认项目",
        created_by="user123"
    )

    # 测试默认颜色
    assert project.color in Project.COLORS

    # 测试默认进度
    assert project.progress.total_papers == 0
    assert project.progress.completed_papers == 0

    # 测试默认值
    assert project.description == ""
    assert project.is_public == False
    assert project.tags == []

    print("✓ Default values tests passed")


if __name__ == "__main__":
    print("=" * 60)
    print("ScholarAI - 项目模型验证")
    print("=" * 60)

    try:
        test_project_model()
        test_project_paper_model()
        test_project_progress_model()
        test_validation()
        test_default_values()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
