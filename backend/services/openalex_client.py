"""
OpenAlex API Client
实现OpenAlex论文搜索功能，完全免费无限制
API文档: https://docs.openalex.org/
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import re
import time


class OpenAlexClient:
    """OpenAlex API客户端"""

    # 基础API URL
    API_BASE = "https://api.openalex.org"

    # OpenAlex API完全免费，但建议设置邮箱以获得更好的服务
    # 可以在环境变量中设置 OPENALEX_EMAIL
    EMAIL = None  # 从环境变量读取

    def __init__(self, email: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ScholarAI/1.0 (https://scholarai.example.com)',
            'Accept': 'application/json'
        })

        # 设置邮箱（推荐，以获得更好的服务）
        self.email = email or self.EMAIL
        if self.email:
            # OpenAlex推荐在User-Agent中包含邮箱
            self.session.headers.update({
                'User-Agent': f'ScholarAI/1.0 (mailto:{self.email})'
            })

        # 请求速率限制（礼貌使用）
        self.last_request_time = 0
        self.min_request_interval = 0.01  # 每秒最多100次请求

    def _rate_limit(self):
        """简单的速率限制"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    def _parse_paper(self, work: Dict) -> Dict:
        """
        解析OpenAlex论文数据

        Args:
            work: OpenAlex返回的论文数据

        Returns:
            标准化的论文数据字典
        """
        # 提取作者信息
        authors = []
        authorships = work.get('authorships', [])
        for authorship in authorships:
            author = authorship.get('author', {})
            if author.get('display_name'):
                authors.append(author['display_name'])

        # 提取年份
        published_year = work.get('publication_year')
        if not published_year:
            # 从publication_date中提取年份
            pub_date = work.get('publication_date')
            if pub_date:
                date_match = re.search(r'(\d{4})', pub_date)
                if date_match:
                    published_year = int(date_match.group(1))

        # 提取发表时间
        published = work.get('publication_date')

        # 提取更新时间
        updated = work.get('updated_date')

        # 提取PDF链接
        pdf_url = ""
        best_location = work.get('best_location') or {}
        if isinstance(best_location, dict):
            if best_location.get('pdf_url'):
                pdf_url = best_location['pdf_url']
            elif best_location.get('landing_page_url'):
                pdf_url = best_location['landing_page_url']

        # 获取主要分类
        primary_topic = work.get('primary_topic') or {}
        primary_category = primary_topic.get('display_name', '') if isinstance(primary_topic, dict) else ''

        # 获取所有分类
        concepts = work.get('concepts', [])
        categories = [c.get('display_name', '') for c in concepts if c.get('display_name')]

        # 获取来源（期刊/会议）
        primary_location = work.get('primary_location') or {}
        source = primary_location.get('source') or {} if isinstance(primary_location, dict) else {}
        venue = source.get('display_name', '') if isinstance(source, dict) else ''

        # 提取摘要
        summary = work.get('abstract', '') or ''
        if summary and summary.startswith('<'):
            # 移除JATS XML标签
            summary = re.sub(r'<jats:[^>]+>', '', summary)
            summary = re.sub(r'</jats:[^>]+>', '', summary)
            summary = re.sub(r'<[^>]+>', '', summary)
            # 解码HTML实体
            summary = summary.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

        # 获取开放获取状态
        is_open_access = work.get('open_access', {}).get('is_oa', False)

        # 获取引用数
        citation_count = work.get('cited_by_count', 0)

        # 获取影响力分数（安全处理None值）
        cited_by_percentile = work.get('cited_by_percentile_year') or {}
        influential_citation_count = cited_by_percentile.get('min', 0) if isinstance(cited_by_percentile, dict) else 0

        return {
            'paper_id': work.get('id', '').replace('https://openalex.org/', ''),
            'title': work.get('title', ''),
            'authors': authors,
            'summary': summary,
            'published': published,
            'published_year': published_year,
            'updated': updated,
            'categories': categories,
            'primary_category': primary_category,
            'pdf_url': pdf_url,
            'arxiv_url': work.get('id', ''),
            'comment': '',
            'journal_ref': venue,
            # 前端兼容字段
            'citations': citation_count,  # 前端使用citations字段
            'year': published_year,  # 前端使用year字段
            # OpenAlex特有字段
            'citation_count': citation_count,
            'influential_citation_count': influential_citation_count,
            'venue': venue,
            'publication_type': work.get('type', ''),
            'publication_date': published,
            'is_open_access': is_open_access,
            'doi': work.get('doi', ''),
            'pmid': work.get('pmid', ''),
            'concepts': concepts,
            'topics': [work.get('primary_topic', {})] if work.get('primary_topic') else [],
        }

    async def search_papers(
        self,
        query: str,
        filter_fields: Optional[Dict] = None,
        page: int = 1,
        page_size: int = 10,
        sort: Optional[str] = None
    ) -> Dict:
        """
        搜索OpenAlex论文

        Args:
            query: 搜索关键词
            filter_fields: 过滤条件，如 {
                'publication_year': '>2020',
                'concepts': ['Computer Science'],
                'type': 'journal-article',
                'has_fulltext': true
            }
            page: 页码（从1开始）
            page_size: 每页数量（默认200，OpenAlex支持per-page=200）
            sort: 排序方式，如 'cited_by_count:desc', 'publication_date:desc'

        Returns:
            搜索结果字典
        """
        self._rate_limit()

        # 构建查询参数
        params = {
            'search': query,
            'per-page': min(page_size, 200),  # OpenAlex最大200
            'page': page,
        }

        # 添加排序
        if sort:
            params['sort'] = sort

        # 添加过滤条件
        if filter_fields:
            filters = []
            for key, value in filter_fields.items():
                if isinstance(value, list):
                    # For date ranges, use comma separator (e.g., from_publication_year:2020,to_publication_year:2024)
                    if key in ['from_publication_year', 'to_publication_year']:
                        from urllib.parse import quote_plus
                        # Manually construct filter without colons to avoid double URL-encoding
                        filters.append(f"{key}:{value}")
                    else:
                        filters.append(f"{key}:{','.join(str(v) for v in value)}")
                else:
                    filters.append(f"{key}:{value}")
            if filters:
                # Encode the entire filter string manually to avoid double URL-encoding
                from urllib.parse import urlencode
                filter_string = ','.join(filters)
                params['filter'] = filter_string

        try:
            # 发送请求
            # Construct full URL manually to avoid double URL-encoding
            url = f"{self.API_BASE}/works"
            query_params = []
            if params:
                for key, value in params.items():
                    if isinstance(value, list):
                        query_params.append(f"{key}={','.join(str(v) for v in value)}")
                    else:
                        query_params.append(f"{key}={value}")
            
            if query_params:
                url += '?' + '&'.join(query_params)
            
            response = self.session.get(
                url,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            # 提取论文列表
            papers = [self._parse_paper(work) for work in data.get('results', [])]

            # 提取元数据
            meta = data.get('meta', {})
            total_results = meta.get('count', 0)
            per_page = meta.get('per_page', page_size)

            # 计算总页数
            total_pages = (total_results + per_page - 1) // per_page if total_results > 0 else 0

            # 调试信息
            print(f"DEBUG: meta={meta}, total_results={total_results}, per_page={per_page}, len(papers)={len(papers)}")

            return {
                'success': True,
                'data': {
                    'papers': papers,
                    'total': total_results,
                    'page': page,
                    'page_size': per_page,
                    'total_pages': total_pages
                }
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'OpenAlex API请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'解析OpenAlex响应失败: {str(e)}'
            }

    async def get_paper_details(self, paper_id: str) -> Dict:
        """
        获取论文详情

        Args:
            paper_id: OpenAlex论文ID（可以是完整URL或ID部分）

        Returns:
            论文详情字典
        """
        self._rate_limit()

        # 如果是完整URL，提取ID部分
        if paper_id.startswith('http'):
            paper_id = paper_id.replace('https://openalex.org/', '')

        try:
            response = self.session.get(
                f"{self.API_BASE}/works/{paper_id}",
                timeout=30
            )
            response.raise_for_status()

            work = response.json()

            return {
                'success': True,
                'data': self._parse_paper(work)
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'获取论文详情失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'解析论文详情失败: {str(e)}'
            }

    async def get_paper_pdf_url(self, paper_id: str) -> Dict:
        """
        获取论文PDF下载链接

        Args:
            paper_id: OpenAlex论文ID

        Returns:
            PDF URL字典
        """
        result = await self.get_paper_details(paper_id)

        if result.get('success'):
            paper_data = result.get('data', {})
            return {
                'success': True,
                'data': {
                    'paper_id': paper_id,
                    'pdf_url': paper_data.get('pdf_url', ''),
                    'is_open_access': paper_data.get('is_open_access', False),
                    'landing_url': paper_data.get('arxiv_url', '')
                }
            }
        else:
            return result

    async def get_paper_by_arxiv_id(self, arxiv_id: str) -> Dict:
        """
        通过arXiv ID获取论文详情（用于arXiv API回退）

        Args:
            arxiv_id: arXiv论文ID (如 2301.00001)

        Returns:
            论文详情字典
        """
        self._rate_limit()

        try:
            response = self.session.get(
                f"{self.API_BASE}/works",
                params={
                    'filter': f'has_arxiv_id:{arxiv_id}',
                    'per-page': 1
                },
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if data.get('results') and len(data['results']) > 0:
                work = data['results'][0]
                return {
                    'success': True,
                    'data': self._parse_paper(work)
                }
            else:
                return {
                    'success': False,
                    'error': f'OpenAlex中未找到arXiv ID为 {arxiv_id} 的论文'
                }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'OpenAlex API请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'解析OpenAlex响应失败: {str(e)}'
            }

    async def get_random_papers(self, count: int = 10) -> Dict:
        """
        获取随机论文（OpenAlex特有功能）

        Args:
            count: 返回数量（最大50）

        Returns:
            随机论文列表
        """
        self._rate_limit()

        try:
            response = self.session.get(
                f"{self.API_BASE}/works",
                params={
                    'per-page': min(count, 50),
                    'sort': 'cited_by_count:desc'  # 按引用数排序
                },
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            papers = [self._parse_paper(work) for work in data.get('results', [])]

            return {
                'success': True,
                'data': {
                    'papers': papers,
                    'total': len(papers)
                }
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'获取随机论文失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'解析随机论文失败: {str(e)}'
            }

    async def get_concepts(self, limit: int = 100) -> Dict:
        """
        获取所有概念/领域列表（OpenAlex特有功能）

        Args:
            limit: 返回数量

        Returns:
            概念列表
        """
        self._rate_limit()

        try:
            response = self.session.get(
                f"{self.API_BASE}/concepts",
                params={
                    'per-page': min(limit, 200),
                    'sort': 'works_count:desc'  # 按论文数量排序
                },
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            concepts = [
                {
                    'id': c.get('id', '').replace('https://openalex.org/', ''),
                    'name': c.get('display_name', ''),
                    'level': c.get('level', 0),
                    'works_count': c.get('works_count', 0),
                    'description': c.get('description', ''),
                }
                for c in data.get('results', [])
            ]

            return {
                'success': True,
                'data': {
                    'concepts': concepts,
                    'total': data.get('meta', {}).get('count', 0)
                }
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'获取概念列表失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'解析概念列表失败: {str(e)}'
            }


# 导出单例
_openalex_client = None


def get_openalex_client() -> OpenAlexClient:
    """获取OpenAlex客户端单例"""
    global _openalex_client
    if _openalex_client is None:
        # 从环境变量读取邮箱（可选，用于获得更好的服务）
        import os
        email = os.environ.get('OPENALEX_EMAIL')
        _openalex_client = OpenAlexClient(email=email)
    return _openalex_client
