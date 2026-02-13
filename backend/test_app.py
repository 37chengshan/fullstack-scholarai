"""
Flask Application Startup Test
============================
Simple script to verify Flask app can be imported and configured correctly.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("ScholarAI Backend - Environment Check")
print("=" * 60)

# Check Python version
print(f"\n✓ Python Version: {sys.version}")

# Check if .env exists
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    print(f"✓ Environment file found: {env_file}")
else:
    print(f"⚠ Environment file not found: {env_file}")

# Try to import Flask
try:
    import flask
    print(f"✓ Flask installed: {flask.__version__}")
except ImportError:
    print("✗ Flask not installed")
    sys.exit(1)

# Try to import other dependencies
dependencies = [
    ('flask_cors', 'Flask-CORS'),
    ('flask_jwt_extended', 'Flask-JWT-Extended'),
    ('pymongo', 'PyMongo'),
    ('dotenv', 'python-dotenv'),
    ('werkzeug', 'Werkzeug'),
    ('requests', 'Requests'),
]

for module_name, display_name in dependencies:
    try:
        __import__(module_name)
        print(f"✓ {display_name} installed")
    except ImportError:
        print(f"✗ {display_name} not installed")

# Try to import and create the app
print("\n" + "=" * 60)
print("Creating Flask Application...")
print("=" * 60)

try:
    from app import create_app
    app = create_app()
    print("✓ Flask application created successfully")
    print(f"✓ Registered blueprints: {list(app.blueprints.keys())}")
    print(f"✓ Health check endpoint: /api/health")
except Exception as e:
    print(f"✗ Failed to create Flask application: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("All checks passed! Ready to run: python run.py")
print("=" * 60)
