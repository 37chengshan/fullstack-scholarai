"""
Paper Reader Routes

API endpoints for arXiv paper deep reading and analysis.
"""

from flask import Blueprint, request, jsonify, current_app
from services.arxiv_reader import ArxivReader
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
paper_reader_bp = Blueprint('paper_reader', __name__)


@paper_reader_bp.route('/reader/<paper_id>', methods=['GET'])
def get_paper_analysis(paper_id: str):
    """
    Get deep analysis of a paper

    Query Parameters:
        use_ai (bool): Whether to use Zhipu AI for enhanced analysis (default: false)

    Returns:
        JSON response with paper analysis including:
        - Metadata (title, authors, categories, etc.)
        - Content (abstract, key contributions)
        - Reading time estimates
        - Difficulty assessment
        - AI-enhanced analysis (if use_ai=true)
    """
    try:
        # Get request parameters
        use_ai = request.args.get('use_ai', 'false').lower() == 'true'

        logger.info(f"Analyzing paper {paper_id} with AI={use_ai}")

        # Get Zhipu API key from config if AI analysis requested
        zhipu_api_key = None
        if use_ai:
            zhipu_api_key = current_app.config.get('ZHIPU_API_KEY')
            if not zhipu_api_key:
                logger.warning("Zhipu AI requested but API key not configured")

        # Initialize reader
        reader = ArxivReader(zhipu_api_key=zhipu_api_key)

        # Analyze paper
        analysis = reader.analyze_paper(paper_id, use_zhipu_ai=use_ai)

        return jsonify({
            'success': True,
            'data': analysis
        }), 200

    except ValueError as e:
        logger.error(f"Value error in paper analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error in paper analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze paper. Please try again later.'
        }), 500


@paper_reader_bp.route('/reader/<paper_id>/versions', methods=['GET'])
def get_paper_versions(paper_id: str):
    """
    Get all versions of a paper

    Returns:
        JSON response with version information
    """
    try:
        logger.info(f"Fetching versions for paper {paper_id}")

        reader = ArxivReader()
        versions = reader.fetch_paper_versions(paper_id)

        return jsonify({
            'success': True,
            'data': {
                'paper_id': paper_id,
                'versions': versions,
                'count': len(versions)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching versions: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch paper versions'
        }), 500


@paper_reader_bp.route('/reader/<paper_id>/metadata', methods=['GET'])
def get_paper_metadata(paper_id: str):
    """
    Get paper metadata only (faster, no analysis)

    Returns:
        JSON response with paper metadata
    """
    try:
        logger.info(f"Fetching metadata for paper {paper_id}")

        reader = ArxivReader()
        metadata = reader.fetch_paper_metadata(paper_id)

        return jsonify({
            'success': True,
            'data': metadata
        }), 200

    except ValueError as e:
        logger.error(f"Value error fetching metadata: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error fetching metadata: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch paper metadata'
        }), 500


@paper_reader_bp.route('/reader/analyze', methods=['POST'])
def analyze_paper_post():
    """
    Analyze a paper via POST (for flexible paper ID specification)

    Request Body:
        {
            "paper_id": string (required),
            "use_ai": boolean (optional, default false)
        }

    Returns:
        JSON response with paper analysis
    """
    try:
        data = request.get_json()

        if not data or not data.get('paper_id'):
            return jsonify({
                'success': False,
                'error': 'paper_id is required'
            }), 400

        paper_id = data['paper_id']
        use_ai = data.get('use_ai', False)

        logger.info(f"Analyzing paper {paper_id} with AI={use_ai}")

        # Get Zhipu API key if AI analysis requested
        zhipu_api_key = None
        if use_ai:
            zhipu_api_key = current_app.config.get('ZHIPU_API_KEY')

        # Initialize reader and analyze
        reader = ArxivReader(zhipu_api_key=zhipu_api_key)
        analysis = reader.analyze_paper(paper_id, use_zhipu_ai=use_ai)

        return jsonify({
            'success': True,
            'data': analysis
        }), 200

    except Exception as e:
        logger.error(f"Error in paper analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze paper'
        }), 500


# Error handlers
@paper_reader_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Paper not found'
    }), 404


@paper_reader_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
