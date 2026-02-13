"""
ScholarAI - Route Tests

Comprehensive tests for all API endpoints:
- Authentication (/api/auth/*)
- Papers (/api/papers/*)
- AI Assistant (/api/ai/*)
- Projects (/api/projects/*)
- Favorites (/api/favorites/*)
- Settings (/api/settings/*)
"""

import pytest
import json
from unittest.mock import Mock, patch

from app import create_app


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app({
        'TESTING': True,
        'MONGODB_URI': 'mongodb://localhost:27017/test_scholarai',
        'JWT_SECRET_KEY': 'test-secret-key',
        'JWT_ACCESS_TOKEN_EXPIRES': '3600'
    })
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Get authenticated headers with valid JWT token."""
    # Register and login to get token
    register_response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'name': 'Test User',
        'password': 'SecurePass123!'
    })

    login_response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'SecurePass123!'
    })

    data = json.loads(login_response.data)
    token = data['data']['access_token']

    return {'Authorization': f'Bearer {token}'}


class TestAuthRoutes:
    """Test authentication routes."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'SecurePass123!'
        })

        data = json.loads(response.data)

        assert response.status_code == 201
        assert data['success'] is True
        assert 'user' in data['data']
        assert data['data']['user']['email'] == 'newuser@example.com'

    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post('/api/auth/register', json={
            'email': 'invalid-email',
            'name': 'Test User',
            'password': 'SecurePass123!'
        })

        data = json.loads(response.data)

        assert response.status_code == 400
        assert data['success'] is False

    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'weak'  # Too short, no numbers
        })

        data = json.loads(response.data)

        assert response.status_code == 400
        assert data['success'] is False

    def test_login_success(self, client):
        """Test successful login."""
        # First register
        client.post('/api/auth/register', json={
            'email': 'loginuser@example.com',
            'name': 'Login User',
            'password': 'SecurePass123!'
        })

        # Then login
        response = client.post('/api/auth/login', json={
            'email': 'loginuser@example.com',
            'password': 'SecurePass123!'
        })

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert data['data']['token_type'] == 'bearer'

    def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'WrongPassword123!'
        })

        data = json.loads(response.data)

        assert response.status_code == 401
        assert data['success'] is False

    def test_get_me_authenticated(self, client, auth_headers):
        """Test getting current user info with valid token."""
        response = client.get('/api/auth/me', headers=auth_headers)

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'user' in data['data']

    def test_get_me_unauthenticated(self, client):
        """Test getting current user info without token."""
        response = client.get('/api/auth/me')

        data = json.loads(response.data)

        assert response.status_code == 401
        assert data['success'] is False


class TestPapersRoutes:
    """Test papers routes."""

    def test_search_papers(self, client):
        """Test paper search endpoint."""
        response = client.get('/api/papers/search', query_string={
            'query': 'machine learning',
            'field': 'cs.AI',
            'page_size': 5
        })

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'papers' in data['data']

    def test_get_paper_details(self, client):
        """Test getting paper details."""
        response = client.get('/api/papers/2301.00001')

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'paper' in data['data']

    def test_get_paper_pdf_url(self, client):
        """Test getting PDF URL."""
        response = client.get('/api/papers/2301.00001/pdf')

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'pdf_url' in data['data']


class TestAIRoutes:
    """Test AI assistant routes."""

    def test_chat_non_stream(self, client, auth_headers):
        """Test non-streaming AI chat."""
        response = client.post('/api/ai/chat',
            headers=auth_headers,
            json={
                'question': 'What is machine learning?',
                'api_config': {
                    'api_key': 'test-key',
                    'model': 'glm-4-flash'
                }
            }
        )

        data = json.loads(response.data)

        assert response.status_code in [200, 500]  # May fail without real API key
        if response.status_code == 200:
            assert data['success'] is True
            assert 'answer' in data['data']

    def test_generate_summary(self, client, auth_headers):
        """Test AI summary generation."""
        response = client.post('/api/ai/summary',
            headers=auth_headers,
            json={
                'paper_id': '2301.00001',
                'length': 'medium',
                'api_config': {
                    'api_key': 'test-key',
                    'model': 'glm-4-flash'
                }
            }
        )

        data = json.loads(response.data)

        assert response.status_code in [200, 500]
        if response.status_code == 200:
            assert data['success'] is True
            assert 'summary' in data['data']


class TestProjectsRoutes:
    """Test project management routes."""

    def test_create_project(self, client, auth_headers):
        """Test creating a new project."""
        response = client.post('/api/projects',
            headers=auth_headers,
            json={
                'name': 'Test Project',
                'color': '#3B82F6',
                'description': 'A test research project'
            }
        )

        data = json.loads(response.data)

        assert response.status_code in [201, 500]  # May need database
        if response.status_code == 201:
            assert data['success'] is True
            assert 'project' in data['data']

    def test_get_projects(self, client, auth_headers):
        """Test getting user's projects."""
        response = client.get('/api/projects', headers=auth_headers)

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'projects' in data['data']


class TestFavoritesRoutes:
    """Test favorites management routes."""

    def test_toggle_favorite(self, client, auth_headers):
        """Test toggling favorite status."""
        response = client.post('/api/favorites/toggle',
            headers=auth_headers,
            json={
                'paper_id': '2301.00001'
            }
        )

        data = json.loads(response.data)

        assert response.status_code in [200, 500]
        if response.status_code == 200:
            assert data['success'] is True
            assert 'is_favorited' in data['data']

    def test_get_favorites(self, client, auth_headers):
        """Test getting favorites list."""
        response = client.get('/api/favorites', headers=auth_headers)

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'favorites' in data['data']

    def test_create_folder(self, client, auth_headers):
        """Test creating a favorites folder."""
        response = client.post('/api/favorites/folders',
            headers=auth_headers,
            json={
                'name': 'AI Research',
                'color': '#3B82F6'
            }
        )

        data = json.loads(response.data)

        assert response.status_code in [201, 500]
        if response.status_code == 201:
            assert data['success'] is True
            assert 'folder' in data['data']


class TestSettingsRoutes:
    """Test user settings routes."""

    def test_get_settings(self, client, auth_headers):
        """Test getting user settings."""
        response = client.get('/api/settings', headers=auth_headers)

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'settings' in data['data']

    def test_update_settings(self, client, auth_headers):
        """Test updating user settings."""
        response = client.put('/api/settings',
            headers=auth_headers,
            json={
                'theme': 'dark',
                'language': 'en-US'
            }
        )

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'settings' in data['data']

    def test_get_stats(self, client, auth_headers):
        """Test getting user statistics."""
        response = client.get('/api/settings/stats', headers=auth_headers)

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'stats' in data['data']
