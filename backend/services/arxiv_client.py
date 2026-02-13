"""
arXiv API Client
实现arXiv论文搜索功能，支持关键词、领域、年份过滤和分页
"""

import feedparser
import requests
from typing import List, Dict, Optional
from datetime import datetime
import re


class ArxivClient:
    """arXiv API客户端"""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ScholarAI/1.0 (https://scholarai.example.com)'
        })

    def _build_query(
        self,
        query: str,
        field: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        venue: Optional[str] = None
    ) -> str:
        """
        构建arXiv搜索查询字符串

        Args:
            query: 搜索关键词
            field: 领域过滤 (如 cs.AI, cs.CL, cs.LG)
            year_min: 最小年份
            year_max: 最大年份
            venue: 发表场所 (如 NeurIPS, ICML, CVPR)

        Returns:
            arXiv查询字符串
        """
        query_parts = []

        # 1. 基础关键词搜索 (搜索title, abstract, author)
        if query:
            # 使用all:字段搜索title, abstract, authors
            query_parts.append(f'all:{query}')

        # 2. 领域过滤 (使用cat:字段)
        if field:
            query_parts.append(f'cat:{field}')

        # 3. 年份范围过滤
        if year_min or year_max:
            # arXiv使用submitted_date字段
            start_date = f"{year_min}-01-01" if year_min else "1900-01-01"
            end_date = f"{year_max}-12-31" if year_max else "2030-12-31"
            query_parts.append(f'submitted_date:[{start_date} TO {end_date}]')

        # 4. 发表场所过滤 (在title或abstract中搜索)
        if venue:
            query_parts.append(f'all:{venue}')

        # 组合查询 (使用AND连接)
        if query_parts:
            search_query = ' AND '.join(query_parts)
        else:
            # 如果没有任何过滤条件，返回最近的所有论文
            search_query = 'all:*'

        # URL编码空格为+
        return search_query.replace(' ', '+')

    def _parse_paper(self, entry) -> Dict:
        """
        解析单篇论文信息

        Args:
            entry: feedparser entry对象

        Returns:
            论文数据字典
        """
        # 提取作者信息
        authors = []
        if hasattr(entry, 'authors'):
            authors = [author.name for author in entry.authors]

        # 提取arXiv ID (从URL中提取)
        arxiv_id = ""
        if hasattr(entry, 'id'):
            # URL格式: http://arxiv.org/abs/2301.00001v1
            match = re.search(r'/(\d+\.\d+)', entry.id)
            if match:
                arxiv_id = match.group(1)

        # 提取分类
        categories = []
        if hasattr(entry, 'tags'):
            categories = [tag.term for tag in entry.tags if tag.term]

        # 主分类
        primary_category = categories[0] if categories else ""

        # 提取发表年份
        published_year = None
        if hasattr(entry, 'published'):
            published_year = entry.published.year if entry.published else None

        # 提取更新时间
        updated = None
        if hasattr(entry, 'updated'):
            updated = entry.updated.isoformat() if entry.updated else None

        # 提取PDF链接
        pdf_url = ""
        if hasattr(entry, 'links'):
            for link in entry.links:
                if link.type == 'application/pdf':
                    pdf_url = link.href
                    break

        return {
            'paper_id': arxiv_id,
            'title': entry.title if hasattr(entry, 'title') else "",
            'authors': authors,
            'summary': entry.summary if hasattr(entry, 'summary') else "",
            'published': entry.published.isoformat() if hasattr(entry, 'published') and entry.published else None,
            'published_year': published_year,
            'updated': updated,
            'categories': categories,
            'primary_category': primary_category,
            'pdf_url': pdf_url,
            'arxiv_url': entry.id if hasattr(entry, 'id') else "",
            'comment': entry.comment if hasattr(entry, 'comment') else "",
            'journal_ref': entry.journal_ref if hasattr(entry, 'journal_ref') else None
        }

    async def search_papers(
        self,
        query: str,
        field: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        venue: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict:
        """
        搜索arXiv论文

        Args:
            query: 搜索关键词
            field: 领域过滤 (如 cs.AI, cs.CL, cs.LG)
            year_min: 最小年份
            year_max: 最大年份
            venue: 发表场所 (如 NeurIPS, ICML, CVPR)
            page: 页码 (从1开始)
            page_size: 每页数量 (最大100)

        Returns:
            搜索结果字典
        """
        # 构建查询
        search_query = self._build_query(query, field, year_min, year_max, venue)

        # 计算起始位置 (arXiv API从0开始)
        start = (page - 1) * page_size

        # 构建请求参数
        params = {
            'search_query': search_query,
            'start': start,
            'max_results': page_size,
            'sortBy': 'submittedDate',  # 按提交时间排序
            'sortOrder': 'descending'     # 降序
        }

        try:
            # 发送请求
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            # 解析Atom feed
            feed = feedparser.parse(response.content)

            # 提取论文总数
            total_results = int(feed.feed.opensearch_totalresults) if hasattr(feed.feed, 'opensearch_totalresults') else 0

            # 解析论文列表
            papers = [self._parse_paper(entry) for entry in feed.entries]

            return {
                'success': True,
                'data': {
                    'papers': papers,
                    'total': total_results,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_results + page_size - 1) // page_size if total_results > 0 else 0
                }
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'arXiv API请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'解析arXiv响应失败: {str(e)}'
            }

    async def get_paper_details(self, paper_id: str) -> Dict:
        """
        获取论文详情

        Args:
            paper_id: arXiv论文ID (如 2301.00001)

        Returns:
            论文详情字典
        """
        # 构建查询
        search_query = f'id:{paper_id}'

        params = {
            'search_query': search_query,
            'max_results': 1
        }

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            if feed.entries:
                paper = self._parse_paper(feed.entries[0])
                return {
                    'success': True,
                    'data': paper
                }
            else:
                return {
                    'success': False,
                    'error': '论文未找到'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'获取论文详情失败: {str(e)}'
            }

    async def get_paper_pdf_url(self, paper_id: str) -> Dict:
        """
        获取论文PDF下载链接

        Args:
            paper_id: arXiv论文ID

        Returns:
            PDF URL字典
        """
        # arXiv PDF URL格式
        pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"

        return {
            'success': True,
            'data': {
                'paper_id': paper_id,
                'pdf_url': pdf_url
            }
        }


# 导出单例
_arxiv_client = None


def get_arxiv_client() -> ArxivClient:
    """获取arXiv客户端单例"""
    global _arxiv_client
    if _arxiv_client is None:
        _arxiv_client = ArxivClient()
    return _arxiv_client
