"""
Papers API Routes
使用OpenAlex API实现论文搜索和详情查询（完全免费无限制）
"""

from flask import Blueprint, request, jsonify
from services.openalex_client import get_openalex_client
import logging

# 创建蓝图
papers_bp = Blueprint('papers', __name__, url_prefix='/api/papers')
logger = logging.getLogger(__name__)


@papers_bp.route('/search', methods=['GET'])
def search_papers():
    """
    使用OpenAlex搜索论文

    Query Parameters:
        query: 搜索关键词 (必填)
        field: 领域过滤 (可选)
        year_min: 最小年份 (可选)
        year_max: 最大年份 (可选)
        venue: 发表场所 (可选)
        page: 页码 (可选, 默认1)
        page_size: 每页数量 (可选, 默认20, 最大200)

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
        page_size = request.args.get('page_size', 20, type=int)

        # 验证必填参数
        if not query:
            return jsonify({
                'success': False,
                'error': '搜索关键词不能为空'
            }), 400

        # 验证page_size范围
        if page_size < 1 or page_size > 200:
            page_size = 20

        # 获取OpenAlex客户端
        client = get_openalex_client()

        # 构建过滤条件
        filter_fields = {}
        if year_min:
            filter_fields['from_publication_year'] = year_min
        if year_max:
            filter_fields['to_publication_year'] = year_max
        if venue:
            # OpenAlex使用venue filter
            filter_fields['venue'] = venue

        # 调用OpenAlex搜索
        import asyncio
        result = asyncio.run(client.search_papers(
            query=query,
            filter_fields=filter_fields,
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
    获取论文详情（使用OpenAlex）

    Path Parameters:
        paper_id: 论文ID (支持OpenAlex ID或arXiv ID)

    Returns:
        JSON响应包含论文详情
    """
    try:
        if not paper_id:
            return jsonify({
                'success': False,
                'error': '论文ID不能为空'
            }), 400

        # 获取OpenAlex客户端
        client = get_openalex_client()

        # 获取论文详情
        import asyncio

        # 检测是否为arXiv ID格式 (YYMM.NNNNN)
        import re
        arxiv_pattern = r'^\d{4}\.\d{5}(v\d+)?$'

        if bool(re.match(arxiv_pattern, paper_id)):
            # 使用arXiv ID查找
            result = asyncio.run(client.get_paper_by_arxiv_id(paper_id))
        else:
            # 使用OpenAlex ID查找
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
        paper_id: 论文ID

    Returns:
        JSON响应包含PDF URL
    """
    try:
        if not paper_id:
            return jsonify({
                'success': False,
                'error': '论文ID不能为空'
            }), 400

        # 获取OpenAlex客户端
        client = get_openalex_client()

        # 获取PDF URL
        import asyncio
        result = asyncio.run(client.get_paper_pdf_url(paper_id))

        if result['success']:
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '获取PDF链接失败')
            }), 404

    except Exception as e:
        logger.error(f"获取PDF链接失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


@papers_bp.route('/fields', methods=['GET'])
def get_fields():
    """
    获取研究领域列表（OpenAlex Concepts）

    Returns:
        JSON响应包含领域列表
    """
    try:
        client = get_openalex_client()
        import asyncio
        result = asyncio.run(client.get_concepts(limit=50))

        if result['success']:
            return jsonify(result)
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '获取领域列表失败')
            }), 500

    except Exception as e:
        logger.error(f"获取领域列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500
