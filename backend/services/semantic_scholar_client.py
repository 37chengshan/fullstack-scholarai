"""
Semantic Scholar API Client
实现Semantic Scholar论文搜索功能，提供更丰富的元数据（引用数、影响力等）
API文档: https://api.semanticscholar.org/api-docs/
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import re


class SemanticScholarClient:
    """Semantic Scholar API客户端"""

    # 基础API URL
    GRAPH_API_BASE = "https://api.semanticscholar.org/graph/v1"
    RECOMMENDATIONS_API = "https://api.semanticscholar.org/recommendations/v1"

    # Semantic Scholar API Key (可选，提高速率限制)
    # 免费版：每分钟100次请求
    # 有API Key：每分钟5000次请求
    API_KEY = None  # 可在环境变量中配置 S2_API_KEY

    def __init__(self, api_key: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ScholarAI/1.0 (https://scholarai.example.com)'
        })

        # 设置API Key（提高速率限制）
        self.api_key = api_key or self.API_KEY
        if self.api_key:
            self.session.headers.update({
                'x-api-key': self.api_key
            })

    def _parse_paper(self, paper: Dict) -> Dict:
        """
        解析Semantic Scholar论文数据

        Args:
            paper: Semantic Scholar返回的论文数据

        Returns:
            标准化的论文数据字典
        """
        # 提取作者信息
        authors = []
        if 'authors' in paper:
            authors = [
                author.get('name', '')
                for author in paper['authors']
                if author.get('name')
            ]

        # 提取年份
        published_year = None
        if 'year' in paper:
            published_year = paper['year']
        elif 'publicationDate' in paper:
            date_match = re.search(r'(\d{4})', paper['publicationDate'])
            if date_match:
                published_year = int(date_match.group(1))

        # 提取发表时间
        published = None
        if 'publicationDate' in paper:
            published = paper['publicationDate']
        elif 'year' in paper:
            published = f"{paper['year']}-01-01"

        # 提取更新��间
        updated = None
        if 'updateDate' in paper:
            updated = paper['updateDate']

        # 提取PDF链接
        pdf_url = ""
        if 'openAccessPdf' in paper and paper['openAccessPdf']:
            pdf_url = paper['openAccessPdf'].get('url', '')

        # 获取主要分类（Semantic Scholar不提供arXiv风格分类，使用venue）
        primary_category = ""
        if 'venue' in paper:
            primary_category = paper['venue']

        # 提取摘要（移除HTML标签）
        summary = paper.get('abstract', '')
        if summary:
            # 移除常见的JATS标签
            summary = re.sub(r'<jats[^>]*>', '', summary)
            summary = re.sub(r'</jats[^>]*>', '', summary)
            summary = re.sub(r'<[^>]+>', '', summary)

        return {
            'paper_id': paper.get('paperId', ''),
            'title': paper.get('title', ''),
            'authors': authors,
            'summary': summary,
            'published': published,
            'published_year': published_year,
            'updated': updated,
            'categories': [primary_category] if primary_category else [],
            'primary_category': primary_category,
            'pdf_url': pdf_url,
            'arxiv_url': paper.get('url', ''),
            'comment': '',
            'journal_ref': paper.get('journal', {}).get('name') if paper.get('journal') else None,
            # Semantic Scholar特有字段
            'citation_count': paper.get('citationCount', 0),
            'influential_citation_count': paper.get('influentialCitationCount', 0),
            'venue': paper.get('venue', ''),
            'publication_types': paper.get('publicationTypes', []),
            'publication_date': paper.get('publicationDate', ''),
            'is_open_access': paper.get('isOpenAccess', False),
            'external_ids': paper.get('externalIds', {}),
            's2_fields_of_study': paper.get('s2FieldsOfStudy', []),
        }

    async def search_papers(
        self,
        query: str,
        fields_of_study: Optional[List[str]] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        venue: Optional[str] = None,
        publication_type: Optional[str] = None,
        min_citation_count: Optional[int] = None,
        open_access_pdf: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict:
        """
        搜索Semantic Scholar论文

        Args:
            query: 搜索关键词
            fields_of_study: 领域过滤（如 Computer Science, Medicine）
            year_min: 最小年份
            year_max: 最大年份
            venue: 发表场所（如 NeurIPS, ICML）
            publication_type: 发表类型（如 Conference, Journal）
            min_citation_count: 最小引用数
            open_access_pdf: 是否只返回有开放获取PDF的论文
            page: 页码（从1开始）
            page_size: 每页数量（最大100）

        Returns:
            搜索结果字典
        """
        # 构建查询参数
        params = {
            'query': query,
            'offset': (page - 1) * page_size,
            'limit': min(page_size, 100),
            'fields': ','.join([
                'paperId',
                'title',
                'abstract',
                'authors',
                'year',
                'publicationDate',
                'updateDate',
                'venue',
                'publicationTypes',
                'openAccessPdf',
                'url',
                'journal',
                'citationCount',
                'influentialCitationCount',
                'isOpenAccess',
                'externalIds',
                's2FieldsOfStudy'
            ])
        }

        # 添加过滤条件
        if year_min or year_max:
            year_filter = f"year:"
            if year_min and year_max:
                year_filter += f"{year_min}-{year_max}"
            elif year_min:
                year_filter += f"{year_min}-"
            elif year_max:
                year_filter += f"-{year_max}"
            params['year'] = year_filter

        if venue:
            params['venue'] = venue

        if publication_type:
            params['publicationType'] = publication_type

        if min_citation_count is not None:
            params['minCitationCount'] = min_citation_count

        if open_access_pdf is not None:
            params['openAccessPdf'] = open_access_pdf

        if fields_of_study:
            # Semantic Scholar使用fieldsOfStudy参数
            params['fieldsOfStudy'] = ','.join(fields_of_study)

        try:
            # 发送请求
            response = self.session.get(
                f"{self.GRAPH_API_BASE}/paper/search",
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            # 提取论文列表
            papers = [self._parse_paper(paper) for paper in data.get('data', [])]

            # 提取总数
            total_results = data.get('total', 0)

            # 计算总页数
            total_pages = (total_results + page_size - 1) // page_size if total_results > 0 else 0

            return {
                'success': True,
                'data': {
                    'papers': papers,
                    'total': total_results,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': total_pages
                }
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Semantic Scholar API请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'解析Semantic Scholar响应失败: {str(e)}'
            }

    async def get_paper_details(self, paper_id: str) -> Dict:
        """
        获取论文详情

        Args:
            paper_id: Semantic Scholar论文ID

        Returns:
            论文详情字典
        """
        # 构建请求参数
        params = {
            'fields': ','.join([
                'paperId',
                'externalIds',
                'url',
                'title',
                'abstract',
                'authors',
                'venue',
                'publicationVenue',
                'year',
                'date',
                'journal',
                'citationCount',
                'influentialCitationCount',
                'isOpenAccess',
                'openAccessPdf',
                'fieldsOfStudy',
                's2FieldsOfStudy',
                'publicationTypes',
                'publicationDate',
                'references',
                'citations'
            ])
        }

        try:
            response = self.session.get(
                f"{self.GRAPH_API_BASE}/paper/{paper_id}",
                params=params,
                timeout=30
            )
            response.raise_for_status()

            paper = response.json()

            return {
                'success': True,
                'data': self._parse_paper(paper)
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
            paper_id: Semantic Scholar论文ID

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
                    'is_open_access': paper_data.get('is_open_access', False)
                }
            }
        else:
            return result

    async def get_recommendations(
        self,
        paper_id: str,
        limit: int = 10
    ) -> Dict:
        """
        获取相关论文推荐

        Args:
            paper_id: 基准论文ID
            limit: 返回数量

        Returns:
            推荐论文列表
        """
        try:
            response = self.session.get(
                f"{self.RECOMMENDATIONS_API}/papers/{paper_id}/relatedpapers",
                params={'limit': limit},
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            # 解析推荐论文
            recommendations = [
                {
                    'paper_id': item.get('paperId', ''),
                    'title': item.get('title', ''),
                    'abstract': item.get('abstract', ''),
                    'authors': [a.get('name', '') for a in item.get('authors', [])],
                    'year': item.get('year'),
                    'citation_count': item.get('citationCount', 0),
                    'interest': item.get('interest', 0),  # 相关性分数
                    'similarity': item.get('similarity', 0),
                }
                for item in data.get('relatedPapers', [])
            ]

            return {
                'success': True,
                'data': {
                    'recommendations': recommendations
                }
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'获取推荐失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'解析推荐失败: {str(e)}'
            }

    async def get_citations(
        self,
        paper_id: str,
        limit: int = 100
    ) -> Dict:
        """
        获取引用该论文的论文列表

        Args:
            paper_id: 论文ID
            limit: 返回数量

        Returns:
            引用论文列表
        """
        try:
            response = self.session.get(
                f"{self.GRAPH_API_BASE}/paper/{paper_id}/citations",
                params={'limit': limit, 'fields': 'paperId,title,authors,year,citationCount,abstract'},
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            citations = [
                {
                    'paper_id': item.get('paperId', {}).get('paperId', ''),
                    'title': item.get('paperId', {}).get('title', ''),
                    'authors': [a.get('name', '') for a in item.get('paperId', {}).get('authors', [])],
                    'year': item.get('paperId', {}).get('year'),
                    'citation_count': item.get('paperId', {}).get('citationCount', 0),
                    'abstract': item.get('paperId', {}).get('abstract', ''),
                    'context': item.get('context', ''),  # 引用上下文（如果有）
                    'intention': item.get('intention', ''),  # 引用意图（如果有）
                }
                for item in data.get('data', [])
            ]

            return {
                'success': True,
                'data': {
                    'citations': citations,
                    'total': data.get('total', 0)
                }
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'获取引用列表失败: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'解析引用列表失败: {str(e)}'
            }


# 导出单例
_semantic_scholar_client = None


def get_semantic_scholar_client() -> SemanticScholarClient:
    """获取Semantic Scholar客户端单例"""
    global _semantic_scholar_client
    if _semantic_scholar_client is None:
        # 从环境变量读取API Key（可选）
        api_key = None  # 可以从os.environ.get('S2_API_KEY')读取
        _semantic_scholar_client = SemanticScholarClient(api_key=api_key)
    return _semantic_scholar_client
