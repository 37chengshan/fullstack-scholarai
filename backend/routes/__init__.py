"""
Routes Package
==============
Blueprints are defined in their respective modules and imported here for easy access.
"""

# Import all blueprints from their modules
from .auth import auth_bp
from .paper_reader import paper_reader_bp
from .papers import papers_bp
from .papers_ai import papers_ai_bp
from .ai import ai_bp
from .projects import projects_bp
from .settings import settings_bp
from .favorites import favorites_bp

# Export all blueprints
__all__ = [
    'auth_bp',
    'paper_reader_bp',
    'papers_bp',
    'papers_ai_bp',
    'ai_bp',
    'projects_bp',
    'settings_bp',
    'favorites_bp'
]
