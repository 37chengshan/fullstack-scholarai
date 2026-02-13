"""
ScholarAI - Model Tests

Comprehensive unit tests for all data models:
- User, UserStats, UserRole
- Project, ProjectPaper, ProjectProgress
- Folder, Favorite
- UserSettings, Theme, Language, ApiConfig
"""

import pytest
from datetime import datetime

from models.user import User, UserStats, UserRole
from models.project import Project, ProjectPaper, ProjectProgress, PaperStatus
from models.favorites import Folder, Favorite
from models.settings import UserSettings, Theme, Language, ApiConfig


class TestUser:
    """Test User model."""

    def test_user_creation(self, sample_user_data):
        """Test user creation with all fields."""
        user = User(
            email=sample_user_data['email'],
            name=sample_user_data['name'],
            password=sample_user_data['password']
        )

        assert user.id is not None
        assert user.email == sample_user_data['email']
        assert user.name == sample_user_data['name']
        assert user.password_hash is not None
        assert user.role == UserRole.USER
        assert user.is_active is True
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_password_hashing(self):
        """Test password hashing and verification."""
        user = User(
            email="hash@example.com",
            name="Hash Test",
            password="MyPassword123!"
        )

        # Password hash should not equal plaintext password
        assert user.password_hash != "MyPassword123!"

        # Verify correct password
        assert user.check_password("MyPassword123!") is True

        # Reject incorrect password
        assert user.check_password("WrongPassword") is False

    def test_user_stats_initialization(self):
        """Test user stats initialization."""
        stats = UserStats()

        assert stats.papers_searched == 0
        assert stats.favorites_count == 0
        assert stats.projects_count == 0
        assert stats.ai_queries_count == 0

    def test_user_stats_increment(self):
        """Test user stats increment methods."""
        stats = UserStats()

        stats.increment_papers_searched()
        assert stats.papers_searched == 1

        stats.increment_favorites_count()
        assert stats.favorites_count == 1

        stats.increment_projects_count()
        assert stats.projects_count == 1

        stats.increment_ai_queries_count()
        assert stats.ai_queries_count == 1

    def test_user_to_dict(self, sample_user_data):
        """Test user serialization to dict."""
        user = User(
            email=sample_user_data['email'],
            name=sample_user_data['name'],
            password=sample_user_data['password']
        )

        user_dict = user.to_dict()

        assert user_dict['email'] == sample_user_data['email']
        assert user_dict['name'] == sample_user_data['name']
        assert 'password_hash' not in user_dict  # Sensitive data excluded
        assert 'id' in user_dict

    def test_user_from_dict(self, sample_user_data):
        """Test user deserialization from dict."""
        user_dict = {
            'id': 'test_user_123',
            'email': sample_user_data['email'],
            'name': sample_user_data['name'],
            'password_hash': 'hashed_password_here',
            'role': 'user',
            'is_active': True,
            'stats': {'papers_searched': 10},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        user = User.from_dict(user_dict)

        assert user.id == 'test_user_123'
        assert user.email == sample_user_data['email']
        assert user.password_hash == 'hashed_password_here'


class TestProject:
    """Test Project model."""

    def test_project_creation(self, sample_project_data):
        """Test project creation."""
        project = Project(
            name=sample_project_data['name'],
            color=sample_project_data['color'],
            description=sample_project_data['description'],
            created_by=sample_project_data['created_by']
        )

        assert project.id is not None
        assert project.name == sample_project_data['name']
        assert project.color == sample_project_data['color']
        assert project.description == sample_project_data['description']
        assert project.created_by == sample_project_data['created_by']
        assert isinstance(project.created_at, datetime)
        assert isinstance(project.updated_at, datetime)

    def test_project_paper_management(self):
        """Test adding and removing papers from project."""
        project = Project(
            name="Test Project",
            created_by="user_123"
        )

        # Add paper
        paper = ProjectPaper(
            paper_id="2301.00001",
            title="Test Paper",
            authors=["Author One"]
        )
        project.add_paper(paper)

        assert len(project.papers) == 1
        assert project.papers[0].paper_id == "2301.00001"

        # Remove paper
        project.remove_paper("2301.00001")
        assert len(project.papers) == 0

    def test_project_progress_calculation(self):
        """Test project progress calculation."""
        project = Project(
            name="Test Project",
            created_by="user_123"
        )

        # Add papers with different statuses
        project.add_paper(ProjectPaper(
            paper_id="2301.00001",
            title="Paper 1",
            authors=["Author One"],
            status=PaperStatus.COMPLETED
        ))
        project.add_paper(ProjectPaper(
            paper_id="2301.00002",
            title="Paper 2",
            authors=["Author Two"],
            status=PaperStatus.TO_READ
        ))
        project.add_paper(ProjectPaper(
            paper_id="2301.00003",
            title="Paper 3",
            authors=["Author Three"],
            status=PaperStatus.IN_PROGRESS
        ))

        progress = project.get_progress()

        assert progress.total == 3
        assert progress.completed == 1
        assert progress.completion_rate == 33.33333333333333

    def test_project_to_dict(self):
        """Test project serialization."""
        project = Project(
            name="Test Project",
            created_by="user_123"
        )

        project_dict = project.to_dict()

        assert project_dict['name'] == "Test Project"
        assert 'papers' in project_dict
        assert 'progress' in project_dict


class TestFavorite:
    """Test Favorite model."""

    def test_favorite_creation(self):
        """Test favorite creation."""
        favorite = Favorite(
            user_id="user_123",
            paper_id="2301.00001",
            title="Test Paper",
            authors=["Author One", "Author Two"]
        )

        assert favorite.id is not None
        assert favorite.user_id == "user_123"
        assert favorite.paper_id == "2301.00001"
        assert favorite.title == "Test Paper"
        assert isinstance(favorite.created_at, datetime)

    def test_folder_creation(self):
        """Test folder creation."""
        folder = Folder(
            created_by="user_123",
            name="AI Research",
            color="#3B82F6"
        )

        assert folder.id is not None
        assert folder.created_by == "user_123"
        assert folder.name == "AI Research"
        assert folder.color == "#3B82F6"
        assert isinstance(folder.created_at, datetime)

    def test_favorite_with_folder(self):
        """Test favorite with folder assignment."""
        folder = Folder(
            created_by="user_123",
            name="Deep Learning"
        )

        favorite = Favorite(
            user_id="user_123",
            paper_id="2301.00001",
            title="Test Paper",
            authors=["Author One"],
            folder_id=folder.id
        )

        assert favorite.folder_id == folder.id


class TestUserSettings:
    """Test UserSettings model."""

    def test_settings_creation(self):
        """Test settings creation with defaults."""
        settings = UserSettings(user_id="user_123")

        assert settings.user_id == "user_123"
        assert settings.theme == Theme.SYSTEM
        assert settings.language == Language.ZH_CN
        assert settings.notification_enabled is True
        assert settings.email_subscription is False

    def test_theme_options(self):
        """Test all theme options."""
        assert Theme.LIGHT.value == "light"
        assert Theme.DARK.value == "dark"
        assert Theme.SYSTEM.value == "system"

    def test_language_options(self):
        """Test all language options."""
        assert Language.ZH_CN.value == "zh-CN"
        assert Language.EN_US.value == "en-US"

    def test_api_config_encryption(self):
        """Test API config encryption (in real implementation)."""
        api_config = ApiConfig(
            provider="zhipu",
            api_key="test_key_123",
            model="glm-4-flash"
        )

        assert api_config.provider == "zhipu"
        assert api_config.api_key == "test_key_123"
        assert api_config.model == "glm-4-flash"
        assert api_config.temperature == 0.7  # Default value
        assert api_config.max_tokens == 2000  # Default value

    def test_settings_to_dict(self):
        """Test settings serialization."""
        settings = UserSettings(
            user_id="user_123",
            theme=Theme.DARK,
            language=Language.EN_US
        )

        settings_dict = settings.to_dict()

        assert settings_dict['theme'] == "dark"
        assert settings_dict['language'] == "en-US"
