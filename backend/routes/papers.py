"""
Papers API Routes
实现论文搜索和论文详情API端点
"""

from flask import Blueprint, request, jsonify
from services.arxiv_client import get_arxiv_client
import logging

# 创建蓝图
papers_bp = Blueprint('papers', __name__, url_prefix='/api/papers')
logger = logging.getLogger(__name__)


@papers_bp.route('/search', methods=['GET'])
def search_papers():
    """
    搜索arXiv论文

    Query Parameters:
        query: 搜索关键词 (必填)
        field: 领域过滤 (可选, 如 cs.AI, cs.CL, cs.LG)
        year_min: 最小年份 (可选)
        year_max: 最大年份 (可选)
        venue: 发表场所 (可选, 如 NeurIPS, ICML, CVPR)
        page: 页码 (可选, 默认1)
        page_size: 每页数量 (可选, 默认10, 最大100)

    Returns:
        JSON响应包含论文列表和分页信息
    """
    try:
        # 获取查询参数
        query = request.args.get('query', '').strip()
        field = request.args.get('field', '').strip() or None
        year_min = request.args.get('year_min', type=int) or None
        year_max = request.args.get('year_max', type=int) or None
        venue = request.args.get('venue', '').strip() or None
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)

        # 验证必填参数
        if not query:
            return jsonify({
                'success': False,
                'error': '搜索关键词不能为空'
            }), 400

        # 验证page_size范围
        if page_size < 1 or page_size > 100:
            return jsonify({
                'success': False,
                'error': 'page_size必须在1-100之间'
            }), 400

        # 验证page范围
        if page < 1:
            return jsonify({
                'success': False,
                'error': 'page必须大于0'
            }), 400

        # 验证年份范围
        if year_min and year_max and year_min > year_max:
            return jsonify({
                'success': False,
                'error': 'year_min不能大于year_max'
            }), 400

        # 获取arXiv客户端
        client = get_arxiv_client()

        # 搜索论文
        import asyncio
        result = asyncio.run(client.search_papers(
            query=query,
            field=field,
            year_min=year_min,
            year_max=year_max,
            venue=venue,
            page=page,
            page_size=page_size
        ))

        if result['success']:
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '搜索失败')
            }), 500

    except Exception as e:
        logger.error(f"搜索论文失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


@papers_bp.route('/<paper_id>', methods=['GET'])
def get_paper_details(paper_id):
    """
    获取论文详情

    Path Parameters:
        paper_id: arXiv论文ID (如 2301.00001)

    Returns:
        JSON响应包含论文详情
    """
    try:
        if not paper_id:
            return jsonify({
                'success': False,
                'error': '论文ID不能为空'
            }), 400

        # 获取arXiv客户端
        client = get_arxiv_client()

        # 获取论文详情
        import asyncio
        result = asyncio.run(client.get_paper_details(paper_id))

        if result['success']:
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '获取论文详情失败')
            }), 404

    except Exception as e:
        logger.error(f"获取论文详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


@papers_bp.route('/<paper_id>/pdf', methods=['GET'])
def get_paper_pdf(paper_id):
    """
    获取论文PDF下载链接

    Path Parameters:
        paper_id: arXiv论文ID (如 2301.00001)

    Returns:
        JSON响应包含PDF URL
    """
    try:
        if not paper_id:
            return jsonify({
                'success': False,
                'error': '论文ID不能为空'
            }), 400

        # 获取arXiv客户端
        client = get_arxiv_client()

        # 获取PDF URL
        import asyncio
        result = asyncio.run(client.get_paper_pdf_url(paper_id))

        if result['success']:
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '获取PDF链接失败')
            }), 500

    except Exception as e:
        logger.error(f"获取PDF链接失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500
