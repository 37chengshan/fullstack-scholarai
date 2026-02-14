"""
ScholarAI Flask Application
=========================
Main application factory for the ScholarAI backend.
"""

from flask import Flask, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import middleware
from middleware.auth import init_jwt, generate_token, jwt_required_custom, get_current_user_id

# Import database configuration
# from routes.pdf_preview import pdf_preview_bp  # Temporarily disabled due to syntax error
from config.database import init_db


def create_app(config_name='development'):
    """
    Application factory pattern.
    Creates and configures the Flask application.

    Args:
        config_name: Configuration name (development, testing, production)

    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)

    # Configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))
    app.config['MONGODB_URI'] = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/scholarai')
    app.config['ZHIPU_API_KEY'] = os.getenv('ZHIPU_API_KEY', '')  # For AI-enhanced paper analysis

    # Initialize extensions
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Initialize JWT using middleware (this also sets up JWTManager)
    jwt_manager = init_jwt(app)

    # Initialize database connection
    try:
        init_db(app)
    except Exception as e:
        app.logger.error(f"Failed to initialize database: {e}")
        # In development, continue anyway; in production, you might want to raise

    # Register blueprints
    from routes.auth import auth_bp
    from routes.paper_reader import paper_reader_bp
    from routes.papers import papers_bp
    from routes.papers_ai import papers_ai_bp
    from routes.ai import ai_bp
    from routes.projects import projects_bp
    from routes.settings import settings_bp
    from routes.favorites import favorites_bp
    from routes.upload import upload_bp

    app.register_blueprint(auth_bp)  # auth_bp already has url_prefix='/api/auth'
    app.register_blueprint(paper_reader_bp, url_prefix='/api/papers')
    app.register_blueprint(papers_bp)  # papers_bp already has url_prefix='/api/papers'
    app.register_blueprint(papers_ai_bp)  # papers_ai_bp already has url_prefix='/api/papers-ai'
    app.register_blueprint(ai_bp)  # ai_bp already has url_prefix='/api/ai'
    app.register_blueprint(projects_bp)  # projects_bp already has url_prefix='/api/projects'
    app.register_blueprint(settings_bp)  # settings_bp already has url_prefix='/api/settings'
    app.register_blueprint(favorites_bp)  # favorites_bp already has url_prefix='/api/favorites'
    app.register_blueprint(upload_bp)  # upload_bp already has url_prefix='/api/upload'

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'success': True, 'status': 'healthy', 'message': 'ScholarAI API is running'}

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'success': False, 'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'success': False, 'error': 'Internal server error'}, 500

    # Note: JWT error handlers are already configured in middleware/auth.py via init_jwt()

    return app


# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
