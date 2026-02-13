"""
Semantic Scholar API Routes
提供Semantic Scholar论文搜索、详情、推荐、引用等API
"""

from flask import Blueprint, request, jsonify
from services.semantic_scholar_client import get_semantic_scholar_client
import asyncio

# 创建蓝图
semantic_scholar_bp = Blueprint('semantic_scholar', __name__, url_prefix='/api/semantic-scholar')


@semantic_scholar_bp.route('/search', methods=['GET'])
def search_papers():
    """
    搜索Semantic Scholar论文

    Query Parameters:
        query (str): 搜索关键词
        fields_of_study (str, optional): 领域过滤，多个用逗号分隔 (如: Computer Science,Medicine)
        year_min (int, optional): 最小年份
        year_max (int, optional): 最大年份
        venue (str, optional): 发表场所 (如: NeurIPS, ICML)
        publication_type (str, optional): 发表类型 (Conference, Journal)
        min_citation_count (int, optional): 最小引用数
        open_access_pdf (bool, optional): 是否只返回有开放获取PDF的论文
        page (int, optional): 页码，默认1
        page_size (int, optional): 每页数量，默认10，最大100

    Returns:
        JSON响应，格式: {
            "success": true,
            "data": {
                "papers": [...],
                "total": 1000,
                "page": 1,
                "page_size": 10,
                "total_pages": 100
            }
        }
    """
    try:
        # 获取查询参数
        query = request.args.get('query', '')
        if not query:
            return jsonify({
                'success': False,
                'error': '缺少query参数'
            }), 400

        # 可选参数
        fields_of_study_str = request.args.get('fields_of_study')
        fields_of_study = fields_of_study_str.split(',') if fields_of_study_str else None

        year_min = request.args.get('year_min', type=int)
        year_max = request.args.get('year_max', type=int)
        venue = request.args.get('venue')
        publication_type = request.args.get('publication_type')
        min_citation_count = request.args.get('min_citation_count', type=int)
        open_access_pdf = request.args.get('open_access_pdf')

        if open_access_pdf is not None:
            open_access_pdf = open_access_pdf.lower() in ('true', '1', 'yes')

        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)

        # 限制page_size
        page_size = min(page_size, 100)

        # 调用API
        client = get_semantic_scholar_client()
        result = asyncio.run(client.search_papers(
            query=query,
            fields_of_study=fields_of_study,
            year_min=year_min,
            year_max=year_max,
            venue=venue,
            publication_type=publication_type,
            min_citation_count=min_citation_count,
            open_access_pdf=open_access_pdf,
            page=page,
            page_size=page_size
        ))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'搜索失败: {str(e)}'
        }), 500


@semantic_scholar_bp.route('/paper/<paper_id>', methods=['GET'])
def get_paper_details(paper_id):
    """
    获取论文详情

    Path Parameters:
        paper_id (str): Semantic Scholar论文ID

    Returns:
        JSON响应，格式: {
            "success": true,
            "data": {...}
        }
    """
    try:
        client = get_semantic_scholar_client()
        result = asyncio.run(client.get_paper_details(paper_id))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 404 if '未找到' in result.get('error', '') else 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取论文详情失败: {str(e)}'
        }), 500


@semantic_scholar_bp.route('/paper/<paper_id>/pdf', methods=['GET'])
def get_paper_pdf(paper_id):
    """
    获取论文PDF下载链接

    Path Parameters:
        paper_id (str): Semantic Scholar论文ID

    Returns:
        JSON响应，格式: {
            "success": true,
            "data": {
                "paper_id": "...",
                "pdf_url": "...",
                "is_open_access": true
            }
        }
    """
    try:
        client = get_semantic_scholar_client()
        result = asyncio.run(client.get_paper_pdf_url(paper_id))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取PDF链接失败: {str(e)}'
        }), 500


@semantic_scholar_bp.route('/paper/<paper_id>/recommendations', methods=['GET'])
def get_recommendations(paper_id):
    """
    获取相关论文推荐

    Path Parameters:
        paper_id (str): 基准论文ID

    Query Parameters:
        limit (int, optional): 返回数量，默认10

    Returns:
        JSON响应，格式: {
            "success": true,
            "data": {
                "recommendations": [...]
            }
        }
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 100)  # 限制最大值

        client = get_semantic_scholar_client()
        result = asyncio.run(client.get_recommendations(paper_id, limit=limit))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取推荐失败: {str(e)}'
        }), 500


@semantic_scholar_bp.route('/paper/<paper_id>/citations', methods=['GET'])
def get_citations(paper_id):
    """
    获取引用该论文的论文列表

    Path Parameters:
        paper_id (str): 论文ID

    Query Parameters:
        limit (int, optional): 返回数量，默认100

    Returns:
        JSON响应，格式: {
            "success": true,
            "data": {
                "citations": [...],
                "total": 50
            }
        }
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        limit = min(limit, 1000)  # 限制最大值

        client = get_semantic_scholar_client()
        result = asyncio.run(client.get_citations(paper_id, limit=limit))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取引用列表失败: {str(e)}'
        }), 500


@semantic_scholar_bp.route('/compare-arxiv', methods=['GET'])
def compare_with_arxiv():
    """
    比较Semantic Scholar和arXiv搜索结果（可选功能）

    Query Parameters:
        query (str): 搜索关键词
        limit (int, optional): 每个API返回的数量，默认5

    Returns:
        JSON响应，包含两个API的搜索结果对比
    """
    try:
        query = request.args.get('query', '')
        if not query:
            return jsonify({
                'success': False,
                'error': '缺少query参数'
            }), 400

        limit = request.args.get('limit', 5, type=int)

        # 获取Semantic Scholar结果
        s2_client = get_semantic_scholar_client()
        s2_result = asyncio.run(s2_client.search_papers(
            query=query,
            page=1,
            page_size=limit
        ))

        # 获取arXiv结果
        from services.arxiv_client import get_arxiv_client
        arxiv_client = get_arxiv_client()
        arxiv_result = asyncio.run(arxiv_client.search_papers(
            query=query,
            page=1,
            page_size=limit
        ))

        return jsonify({
            'success': True,
            'data': {
                'semantic_scholar': {
                    'total': s2_result.get('data', {}).get('total', 0),
                    'papers': s2_result.get('data', {}).get('papers', [])[:limit]
                },
                'arxiv': {
                    'total': arxiv_result.get('data', {}).get('total', 0),
                    'papers': arxiv_result.get('data', {}).get('papers', [])[:limit]
                },
                'query': query
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'比较失败: {str(e)}'
        }), 500
