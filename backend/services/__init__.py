"""
Services module initialization

This module provides external service integrations including:
- ArXiv paper reader (for PDF processing)
- OpenAlex paper search (primary, no rate limit, 250M+ papers)
- Zhipu AI client (for AI features)
"""

from .arxiv_reader import ArxivReader, analyze_paper
from .openalex_client import OpenAlexClient, get_openalex_client
from .zhipu_client import ZhipuClient, get_zhipu_client

__all__ = [
    'ArxivReader',
    'analyze_paper',
    'OpenAlexClient',
    'get_openalex_client',
    'ZhipuClient',
    'get_zhipu_client'
]
