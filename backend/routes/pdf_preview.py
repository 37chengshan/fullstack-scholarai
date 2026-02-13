"""
PDF Preview Routes
增强PDF预览功能，解决CORS和跨域问题
"""

from flask import Blueprint, request, jsonify, Response, stream
from services.openalex_client import get_openalex_client
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
pdf_preview_bp = Blueprint('pdf_preview', __name__)


@pdf_preview_bp.route('/preview/pdf', methods=['POST'])
def preview_pdf():
    """
    获取PDF预览URL和元数据（增强版）

    Request body:
        pdf_url: PDF链接
        title: 论文标题
        source: 数据源（openalex, arxiv, doi, direct）
    """
    try:
        data = request.get_json()

        if not data.get('pdf_url'):
            return jsonify({
                'success': False,
                'error': 'PDF URL is required'
            }), 400

        pdf_url = data['pdf_url']
        title = data.get('title', 'PDF Preview')

        logger.info(f"Previewing PDF: {pdf_url}")

        # 尝试多种方式获取PDF
        preview_options = []

        # 方式1: 直接预览（优先）
        can_preview = False
        if pdf_url.startswith(('http://', 'https://')):
            # 检查是否是常见的可直接预览的PDF托管域名
            preview_domains = [
                'arxiv.org/pdf',
                'openalex.org',
                'sci-hub.org/pdf',
                'researchgate.net/pdf',
                'acm.org/pdf',
                'springer.com/pdf',
                'ieee.org/pdf',
                'nature.com/pdf',
                'cell.com/pdf',
                'science.org/pdf'
            ]

            for domain in preview_domains:
                if domain in pdf_url:
                    can_preview = True
                    preview_options.append({
                        'method': 'direct',
                        'url': pdf_url,
                        'confidence': 'high'
                    })
                    logger.info(f"Direct preview available from domain: {domain}")
                    break

        # 方式2: 通过DOI解析
        if not can_preview and 'doi' in data or '10.' in pdf_url:
            # 尝试从PDF URL提取DOI
            import re
            doi_match = re.search(r'doi\.org/10\.\+/i', pdf_url)
            if doi_match or '10.' in pdf_url:
                doi = doi_match.group(0) if doi_match else re.search(r'10\.\d{4,5}/', pdf_url)

                # 构建DOI直链
                if doi:
                    doi_url = f"https://doi.org/{doi.lower()}"
                    preview_options.append({
                        'method': 'doi_landing',
                        'url': doi_url,
                        'confidence': 'medium',
                        'note': f'DOI: {doi}'
                    })
                    logger.info(f"DOI found: {doi}, landing page: {doi_url}")

        # 方式3: arXiv ID解析
        if not can_preview and 'arxiv_id' in data:
            arxiv_id = data.get('arxiv_id')
            if arxiv_id:
                # 构建arXiv PDF直链
                arxiv_pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                preview_options.append({
                        'method': 'arxiv_direct',
                        'url': arxiv_pdf_url,
                        'confidence': 'high'
                    })
                logger.info(f"arXiv ID found: {arxiv_id}")

        # 方式4: 代理预览（最后手段）
        if not can_preview:
            # 使用我们的代理端点
            proxy_url = f"http://localhost:5000/api/pdf_preview/direct?url={pdf_url}"
            preview_options.append({
                        'method': 'proxy',
                        'url': proxy_url,
                        'confidence': 'low',
                        'note': '通过代理预览'
                    })
            logger.info("Using proxy preview as fallback")

        # 选择最佳预览方式
        if preview_options:
            # 选择置信度最高的方法
            best_option = max(preview_options, key=lambda x: x['confidence'])
            selected_method = best_option['method']
            preview_url = best_option['url']

            logger.info(f"Selected preview method: {selected_method}, URL: {preview_url}")

            return jsonify({
                'success': True,
                'data': {
                    'title': title,
                    'pdf_url': pdf_url,
                    'preview_method': selected_method,
                    'preview_url': preview_url,
                    'available_methods': [
                        {
                            'method': opt['method'],
                            'url': opt['url'],
                            'confidence': opt['confidence'],
                            'note': opt.get('note', '')
                        }
                        for opt in preview_options
                    ]
                }
            }), 200

    except Exception as e:
        logger.error(f"Error in PDF preview: {e}")
        return jsonify({
                'success': False,
                'error': f'Failed to analyze PDF URL: {str(e)}'
            }), 500


@pdf_preview_bp.route('/preview/direct', methods=['GET'])
def preview_direct():
    """
    直接预览PDF（用于在iframe中加载）

    Query Parameters:
        url: PDF URL（必须以http开头）
    """
    pdf_url = request.args.get('url', '')

    if not pdf_url:
        return jsonify({
                'success': False,
                'error': 'URL parameter is required'
            }), 400

    # 验证URL必须以http或https开头
    if not (pdf_url.startswith('http://') or pdf_url.startswith('https://')):
        return jsonify({
                'success': False,
                'error': 'URL must start with http:// or https://'
            }), 400

    logger.info(f"Direct preview requested for: {pdf_url}")

    # 设置CORS头，允许iframe嵌入
    response = Response()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Security-Policy'] = 'default-src *'
    response.headers['Cross-Origin-Resource-Policy'] = 'cross-origin'

    # 尝试代理PDF内容
    try:
        import requests
        pdf_response = requests.get(pdf_url, timeout=10, stream=True)
        if pdf_response.status_code == 200:
            return Response(
                stream=pdf_response.content,
                headers=response.headers,
                status=200,
                content_type='application/pdf'
            )
        else:
            logger.error(f"Failed to fetch PDF: {pdf_response.status_code}")
            return jsonify({
                'success': False,
                'error': f'PDF not accessible (status {pdf_response.status_code})'
            }), 502
    except Exception as e:
        logger.error(f"Error fetching PDF: {e}")
        return jsonify({
                'success': False,
                'error': f'Failed to fetch PDF: {str(e)}'
            }), 500


@pdf_preview_bp.route('/preview/iframe', methods=['POST'])
def preview_in_iframe():
    """
    通过iframe代理预览PDF（处理CORS问题）

    Request body:
        pdf_url: PDF链接
    """
    try:
        data = request.get_json()

        if not data.get('pdf_url'):
            return jsonify({
                'success': False,
                'error': 'PDF URL is required'
            }), 400

        pdf_url = data['pdf_url']

        logger.info(f"Previewing PDF in iframe: {pdf_url}")

        # 构建代理URL
        proxy_url = f"http://localhost:5000/api/pdf_preview/direct?url={pdf_url}"

        # 尝试获取PDF内容
        try:
            import requests
            pdf_response = requests.get(pdf_url, timeout=10, stream=True)

            if pdf_response.status_code == 200:
                # 获取内容类型
                content_type = pdf_response.headers.get('Content-Type', 'application/octet-stream')
                content_length = pdf_response.headers.get('Content-Length', '0')

                # 返回预览信息
                return jsonify({
                    'success': True,
                    'data': {
                        'proxy_url': proxy_url,
                        'content_type': content_type,
                        'content_length': content_length,
                        'size_mb': round(int(content_length) / (1024 * 1024), 2) if content_length else 0
                    }
                    }
                }), 200
            else:
                logger.error(f"Failed to fetch PDF: {pdf_response.status_code}")
                return jsonify({
                    'success': False,
                    'error': f'PDF not accessible (status {pdf_response.status_code})'
                    }), 502

        except Exception as e:
            logger.error(f"Error in iframe preview: {e}")
            return jsonify({
                    'success': False,
                    'error': f'Failed to preview PDF: {str(e)}'
            }), 500
