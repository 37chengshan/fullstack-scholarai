"""
统一论文搜索API路由
使用arXiv优先，失败时自动回退到OpenAlex
"""

from flask import Blueprint, request, jsonify
from services.unified_search import get_unified_search
import asyncio

# 创建蓝图
unified_papers_bp = Blueprint('unified_papers', __name__, url_prefix='/api/papers')


@unified_papers_bp.route('/search/unified', methods=['GET'])
def search_papers_unified():
    """
    统一论文搜索 - 自动回退机制

    优先使用arXiv，失败时自动切换到OpenAlex

    Query Parameters:
        query (str): 搜索关键词
        field (str, optional): arXiv领域过滤 (cs.AI, cs.CL等)
        year_min (int, optional): 最小年份
        year_max (int, optional): 最大年份
        venue (str, optional): 发表场所
        page (int, optional): 页码，默认1
        page_size (int, optional): 每页数量，默认10
        source (str, optional): 首选数据源 (arxiv, openalex, semantic_scholar)

    Returns:
        JSON响应，格式: {
            "success": true,
            "data": {
                "papers": [...],
                "total": 1000,
                "page": 1,
                "page_size": 10,
                "total_pages": 100,
                "source": "arxiv"  # 实际使用的数据源
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

        field = request.args.get('field')
        year_min = request.args.get('year_min', type=int)
        year_max = request.args.get('year_max', type=int)
        venue = request.args.get('venue')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        preferred_source = request.args.get('source')

        # 调用统一搜索服务
        search = get_unified_search()
        result = asyncio.run(search.search_papers(
            query=query,
            field=field,
            year_min=year_min,
            year_max=year_max,
            venue=venue,
            page=page,
            page_size=page_size,
            preferred_source=preferred_source
        ))

        if result.get('success'):
            return jsonify(result)
        else:
            # 所有数据源都失败了
            return jsonify(result), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'搜索失败: {str(e)}'
        }), 500


@unified_papers_bp.route('/unified/<paper_id>', methods=['GET'])
def get_paper_details_unified(paper_id):
    """
    统一获取论文详情

    Path Parameters:
        paper_id (str): 论文ID

    Query Parameters:
        source (str, optional): 数据源 (arxiv, openalex, semantic_scholar)，默认自动检测

    Returns:
        JSON响应，格式: {
            "success": true,
            "data": {
                ...,
                "source": "arxiv"
            }
        }
    """
    try:
        source = request.args.get('source')

        search = get_unified_search()
        result = asyncio.run(search.get_paper_details(paper_id, source=source))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取论文详情失败: {str(e)}'
        }), 500


@unified_papers_bp.route('/compare-sources', methods=['GET'])
def compare_sources():
    """
    比较所有数据源的搜索结果

    Query Parameters:
        query (str): 搜索关键词
        limit (int, optional): 每个数据源返回的数量，默认5

    Returns:
        JSON响应，包含所有数据源的搜索结果对比
    """
    try:
        query = request.args.get('query', '')
        if not query:
            return jsonify({
                'success': False,
                'error': '缺少query参数'
            }), 400

        limit = request.args.get('limit', 5, type=int)

        search = get_unified_search()
        result = asyncio.run(search.compare_sources(query=query, limit=limit))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'比较失败: {str(e)}'
        }), 500
