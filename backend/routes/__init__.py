"""
Routes Package
==============
Blueprint registration for all API routes.
"""

from flask import Blueprint

# Authentication routes
auth_bp = Blueprint('auth', __name__)

# Papers routes
papers_bp = Blueprint('papers', __name__)

# AI routes
ai_bp = Blueprint('ai', __name__)

# Projects routes
projects_bp = Blueprint('projects', __name__)

# Favorites routes
favorites_bp = Blueprint('favorites', __name__)

# Settings routes
settings_bp = Blueprint('settings', __name__)

# Import route handlers (will be implemented in task-006, task-007, etc.)
# Placeholder imports to prevent circular import errors
