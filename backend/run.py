"""
ScholarAI Backend Server
=======================
Development server entry point.
Usage: python run.py
"""

import os
import sys
from app import create_app

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main entry point for the development server."""
    app = create_app()

    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print("=" * 60)
    print("ScholarAI Backend Server")
    print("=" * 60)
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print("=" * 60)
    print("\nStarting server...\n")

    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
