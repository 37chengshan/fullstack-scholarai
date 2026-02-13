"""
Pytest configuration and fixtures for ScholarAI backend tests.
"""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock
from pymongo import MongoClient

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def mock_db():
    """Mock MongoDB database."""
    db = MagicMock()

    # Mock collections
    db.users = MagicMock()
    db.projects = MagicMock()
    db.favorites = MagicMock()
    db.folders = MagicMock()

    return db


@pytest.fixture
def mock_mongo_client(mock_db):
    """Mock MongoDB client."""
    client = MagicMock()
    client.__getitem__ = Mock(return_value=mock_db)
    return client


@pytest.fixture
def mock_app():
    """Mock Flask app for testing."""
    from app import create_app

    app = create_app({
        'TESTING': True,
        'MONGODB_URI': 'mongodb://localhost:27017/test_scholarai',
        'JWT_SECRET_KEY': 'test-secret-key',
        'JWT_ACCESS_TOKEN_EXPIRES': 3600
    })

    return app


@pytest.fixture
def client(mock_app):
    """Flask test client."""
    return mock_app.test_client()


@pytest.fixture
def headers(mock_app):
    """Create authenticated headers with JWT token."""
    # Create a test user and generate token
    from middleware.auth import generate_token

    test_user_id = 'test_user_123'
    token = generate_token(test_user_id)

    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        'id': 'test_user_123',
        'email': 'test@example.com',
        'name': 'Test User',
        'password': 'SecurePass123!',
        'role': 'user',
        'is_active': True
    }


@pytest.fixture
def sample_paper_data():
    """Sample paper data for testing."""
    return {
        'paper_id': '2301.00001',
        'title': 'Test Paper Title',
        'authors': ['Author One', 'Author Two'],
        'summary': 'This is a test abstract for the paper.',
        'published': '2023-01-01',
        'categories': ['cs.AI'],
        'pdf_url': 'https://arxiv.org/pdf/2301.00001v1.pdf'
    }


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        'name': 'Test Project',
        'color': '#3B82F6',
        'description': 'A test research project',
        'created_by': 'test_user_123',
        'tags': ['machine-learning', 'nlp']
    }


@pytest.fixture
def sample_favorite_data():
    """Sample favorite data for testing."""
    return {
        'paper_id': '2301.00001',
        'title': 'Test Paper Title',
        'authors': ['Author One', 'Author Two'],
        'folder_id': None,
        'notes': 'Interesting paper about AI',
        'tags': ['deep-learning']
    }


@pytest.fixture(scope="session")
def test_database():
    """
    Real test database connection.
    Use this for integration tests that need a real database.
    """
    # Check if test database URI is configured
    test_uri = os.environ.get('MONGODB_TEST_URI')

    if not test_uri:
        pytest.skip("MONGODB_TEST_URI not configured, skipping integration tests")

    client = MongoClient(test_uri)
    db = client.scholarai_test

    yield db

    # Cleanup: drop test database
    client.drop_database('scholarai_test')
    client.close()


@pytest.fixture
def monkeypatch_env(monkeypatch):
    """Monkeypatch environment variables for testing."""
    env_vars = {
        'MONGODB_URI': 'mongodb://localhost:27017/test_scholarai',
        'JWT_SECRET_KEY': 'test-secret-key',
        'JWT_ACCESS_TOKEN_EXPIRES': '3600',
        'ZHIPU_API_KEY': 'test-zhipu-api-key'
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars
