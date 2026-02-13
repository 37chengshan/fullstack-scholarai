"""
OpenAlex API Routes
提供OpenAlex论文搜索功能，完全免费无限制
"""

from flask import Blueprint, request, jsonify
from services.openalex_client import get_openalex_client
import asyncio

# 创建蓝图
openalex_bp = Blueprint('openalex', __name__, url_prefix='/api/openalex')


@openalex_bp.route('/search', methods=['GET'])
def search_papers():
    """
    搜索OpenAlex论文

    Query Parameters:
        query (str): 搜索关键词
        publication_year (str, optional): 年份过滤，如 '>2020', '2020-2023'
        concepts (str, optional): 概念/领域过滤，多个用逗号分隔
        type (str, optional): 论文类型 (journal-article, conference-proceedings, etc.)
        has_fulltext (bool, optional): 是否只返回有全文的论文
        has_abstract (bool, optional): 是否只返回有摘要的论文
        open_access (bool, optional): 是否只返回开放获取的论文
        sort (str, optional): 排序方式，如 cited_by_count:desc, publication_date:desc
        page (int, optional): 页码，默认1
        page_size (int, optional): 每页数量，默认10，最大200

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

        # 构建过滤条件
        filter_fields = {}

        # 年份过滤
        publication_year = request.args.get('publication_year')
        if publication_year:
            filter_fields['publication_year'] = publication_year

        # 概念/领域过滤
        concepts = request.args.get('concepts')
        if concepts:
            filter_fields['concepts'] = concepts.split(',')

        # 论文类型
        paper_type = request.args.get('type')
        if paper_type:
            filter_fields['type'] = paper_type

        # 全文过滤
        has_fulltext = request.args.get('has_fulltext')
        if has_fulltext is not None:
            filter_fields['has_fulltext'] = has_fulltext.lower() in ('true', '1', 'yes')

        # 摘要过滤
        has_abstract = request.args.get('has_abstract')
        if has_abstract is not None:
            filter_fields['has_abstract'] = has_abstract.lower() in ('true', '1', 'yes')

        # 开放获取过滤
        open_access = request.args.get('open_access')
        if open_access is not None:
            filter_fields['is_oa'] = open_access.lower() in ('true', '1', 'yes')

        # 分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)

        # 排序
        sort = request.args.get('sort')

        # 调用API
        client = get_openalex_client()
        result = asyncio.run(client.search_papers(
            query=query,
            filter_fields=filter_fields if filter_fields else None,
            page=page,
            page_size=page_size,
            sort=sort
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


@openalex_bp.route('/paper/<paper_id>', methods=['GET'])
def get_paper_details(paper_id):
    """
    获取论文详情

    Path Parameters:
        paper_id (str): OpenAlex论文ID

    Returns:
        JSON响应，格式: {
            "success": true,
            "data": {...}
        }
    """
    try:
        client = get_openalex_client()
        result = asyncio.run(client.get_paper_details(paper_id))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取论文详情失败: {str(e)}'
        }), 500


@openalex_bp.route('/paper/<paper_id>/pdf', methods=['GET'])
def get_paper_pdf(paper_id):
    """
    获取论文PDF下载链接

    Path Parameters:
        paper_id (str): OpenAlex论文ID

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
        client = get_openalex_client()
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


@openalex_bp.route('/random', methods=['GET'])
def get_random_papers():
    """
    获取随机论文（探索功能）

    Query Parameters:
        count (int, optional): 返回数量，默认10，最大50

    Returns:
        JSON响应，格式: {
            "success": true,
            "data": {
                "papers": [...],
                "total": 10
            }
        }
    """
    try:
        count = request.args.get('count', 10, type=int)
        count = min(count, 50)  # 限制最大值

        client = get_openalex_client()
        result = asyncio.run(client.get_random_papers(count=count))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取随机论文失败: {str(e)}'
        }), 500


@openalex_bp.route('/concepts', methods=['GET'])
def get_concepts():
    """
    获取所有概念/领域列表（用于筛选器）

    Query Parameters:
        limit (int, optional): 返回数量，默认100

    Returns:
        JSON响应，格式: {
            "success": true,
            "data": {
                "concepts": [...],
                "total": 1000
            }
        }
    """
    try:
        limit = request.args.get('limit', 100, type=int)

        client = get_openalex_client()
        result = asyncio.run(client.get_concepts(limit=limit))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取概念列表失败: {str(e)}'
        }), 500


@openalex_bp.route('/compare-all', methods=['GET'])
def compare_all_apis():
    """
    比较所有可用的论文搜索API（arXiv, OpenAlex, Semantic Scholar）

    Query Parameters:
        query (str): 搜索关键词
        limit (int, optional): 每个API返回的数量，默认5

    Returns:
        JSON响应，包含所有API的搜索结果对比
    """
    try:
        query = request.args.get('query', '')
        if not query:
            return jsonify({
                'success': False,
                'error': '缺少query参数'
            }), 400

        limit = request.args.get('limit', 5, type=int)

        results = {}

        # 1. OpenAlex（无限制）
        openalex_client = get_openalex_client()
        openalex_result = asyncio.run(openalex_client.search_papers(
            query=query,
            page=1,
            page_size=limit
        ))
        results['openalex'] = {
            'total': openalex_result.get('data', {}).get('total', 0),
            'papers': openalex_result.get('data', {}).get('papers', [])[:limit],
            'rate_limit': '无限制（建议每秒<100次）'
        }

        # 2. arXiv（无限制）
        from services.arxiv_client import get_arxiv_client
        arxiv_client = get_arxiv_client()
        arxiv_result = asyncio.run(arxiv_client.search_papers(
            query=query,
            page=1,
            page_size=limit
        ))
        results['arxiv'] = {
            'total': arxiv_result.get('data', {}).get('total', 0),
            'papers': arxiv_result.get('data', {}).get('papers', [])[:limit],
            'rate_limit': '无限制'
        }

        # 3. Semantic Scholar（可能有频率限制）
        try:
            from services.semantic_scholar_client import get_semantic_scholar_client
            s2_client = get_semantic_scholar_client()
            s2_result = asyncio.run(s2_client.search_papers(
                query=query,
                page=1,
                page_size=limit
            ))
            results['semantic_scholar'] = {
                'total': s2_result.get('data', {}).get('total', 0),
                'papers': s2_result.get('data', {}).get('papers', [])[:limit],
                'rate_limit': '免费版: 100次/分钟 | 有API Key: 5000次/分钟'
            }
        except Exception as e:
            results['semantic_scholar'] = {
                'error': str(e),
                'rate_limit': '免费版: 100次/分钟 | 有API Key: 5000次/分钟'
            }

        return jsonify({
            'success': True,
            'data': {
                'results': results,
                'query': query
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'比较失败: {str(e)}'
        }), 500
