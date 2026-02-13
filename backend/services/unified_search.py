"""
统一论文搜索服务
实现arXiv优先，失败时自动回退到OpenAlex
"""

import asyncio
import logging
from typing import Dict, Optional, List
from services.arxiv_client import get_arxiv_client
from services.openalex_client import get_openalex_client
from services.semantic_scholar_client import get_semantic_scholar_client

logger = logging.getLogger(__name__)


class UnifiedPaperSearch:
    """统一论文搜索服务，支持多数据源和自动回退"""

    # 数据源优先级
    SOURCES = ['arxiv', 'openalex', 'semantic_scholar']

    def __init__(self):
        self.arxiv_client = get_arxiv_client()
        self.openalex_client = get_openalex_client()
        self.semantic_scholar_client = get_semantic_scholar_client()

    def _normalize_paper(self, paper: Dict, source: str) -> Dict:
        """
        标准化论文数据格式（不同API返回的数据结构略有不同）

        Args:
            paper: 原始论文数据
            source: 数据源名称

        Returns:
            标准化的论文数据
        """
        # 添加数据源标识
        paper['source'] = source

        # OpenAlex有更多字段，确保与arXiv格式一致
        if source == 'openalex':
            # OpenAlex已经返回标准化格式，只需添加source
            pass
        elif source == 'semantic_scholar':
            # Semantic Scholar也已经是标准化格式
            pass
        elif source == 'arxiv':
            # arXiv已经是标准化格式
            pass

        return paper

    async def search_papers(
        self,
        query: str,
        field: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        venue: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        preferred_source: Optional[str] = None
    ) -> Dict:
        """
        统一论文搜索接口

        优先使用arXiv，如果失败则回退到OpenAlex

        Args:
            query: 搜索关键词
            field: 领域过滤（arXiv使用）
            year_min: 最小年份
            year_max: 最大年份
            venue: 发表场所
            page: 页码
            page_size: 每页数量
            preferred_source: 首选数据源 ('arxiv', 'openalex', 'semantic_scholar')

        Returns:
            搜索结果字典
        """
        # 确定数据源优先级
        if preferred_source and preferred_source in self.SOURCES:
            sources = [preferred_source] + [s for s in self.SOURCES if s != preferred_source]
        else:
            sources = self.SOURCES

        # 构建OpenAlex过滤条件
        openalex_filters = {}
        if year_min or year_max:
            if year_min and year_max:
                openalex_filters['publication_year'] = f'{year_min}-{year_max}'
            elif year_min:
                openalex_filters['publication_year'] = f'>{year_min}'
            elif year_max:
                openalex_filters['publication_year'] = f'<{year_max}'

        # 按优先级尝试数据源
        last_error = None

        for source in sources:
            try:
                logger.info(f"尝试使用 {source} 搜索: {query}")

                if source == 'arxiv':
                    result = await self.arxiv_client.search_papers(
                        query=query,
                        field=field,
                        year_min=year_min,
                        year_max=year_max,
                        venue=venue,
                        page=page,
                        page_size=page_size
                    )

                    if result.get('success') and result.get('data', {}).get('papers'):
                        logger.info(f"arXiv搜索成功，找到 {len(result['data']['papers'])} 篇论文")
                        # 标准化并添加数据源标识
                        result['data']['papers'] = [
                            self._normalize_paper(p, 'arxiv')
                            for p in result['data']['papers']
                        ]
                        result['data']['source'] = 'arxiv'
                        return result
                    else:
                        last_error = result.get('error', 'arXiv搜索失败')
                        logger.warning(f"arXiv搜索失败: {last_error}")

                elif source == 'openalex':
                    result = await self.openalex_client.search_papers(
                        query=query,
                        filter_fields=openalex_filters if openalex_filters else None,
                        page=page,
                        page_size=page_size,
                        sort='cited_by_count:desc'  # 按引用数排序
                    )

                    if result.get('success') and result.get('data', {}).get('papers'):
                        logger.info(f"OpenAlex搜索成功，找到 {len(result['data']['papers'])} 篇论文")
                        # 标准化并添加数据源标识
                        result['data']['papers'] = [
                            self._normalize_paper(p, 'openalex')
                            for p in result['data']['papers']
                        ]
                        result['data']['source'] = 'openalex'
                        return result
                    else:
                        last_error = result.get('error', 'OpenAlex搜索失败')
                        logger.warning(f"OpenAlex搜索失败: {last_error}")

                elif source == 'semantic_scholar':
                    # Semantic Scholar使用不同的参数名
                    fields_of_study = [field] if field else None

                    result = await self.semantic_scholar_client.search_papers(
                        query=query,
                        fields_of_study=fields_of_study,
                        year_min=year_min,
                        year_max=year_max,
                        venue=venue,
                        page=page,
                        page_size=page_size
                    )

                    if result.get('success') and result.get('data', {}).get('papers'):
                        logger.info(f"Semantic Scholar搜索成功，找到 {len(result['data']['papers'])} 篇论文")
                        # 标准化并添加数据源标识
                        result['data']['papers'] = [
                            self._normalize_paper(p, 'semantic_scholar')
                            for p in result['data']['papers']
                        ]
                        result['data']['source'] = 'semantic_scholar'
                        return result
                    else:
                        last_error = result.get('error', 'Semantic Scholar搜索失败')
                        logger.warning(f"Semantic Scholar搜索失败: {last_error}")

            except Exception as e:
                last_error = str(e)
                logger.error(f"{source} 搜索异常: {e}")
                continue

        # 所有数据源都失败了
        return {
            'success': False,
            'error': f'所有数据源搜索失败。最后错误: {last_error}',
            'tried_sources': sources
        }

    async def get_paper_details(self, paper_id: str, source: str = None) -> Dict:
        """
        获取论文详情（支持自动回退）

        Args:
            paper_id: 论文ID
            source: 数据源（如果为None则自动检测并回退）

        Returns:
            论文详情字典
        """
        # 如果没有指定数据源，尝试自动检测并确定回退顺序
        if not source:
            # OpenAlex ID格式
            if 'W' in paper_id and len(paper_id) >= 10:
                sources = ['openalex', 'semantic_scholar']
            # Semantic Scholar ID格式
            elif paper_id.isdigit() or len(paper_id) == 27:
                sources = ['semantic_scholar', 'openalex']
            # arXiv ID格式 (YYMM.NNNNN) - 默认arXiv优先，但可以回退到OpenAlex
            else:
                sources = ['arxiv', 'openalex']
        else:
            sources = [source]

        last_error = None
        is_arxiv_id = self._is_arxiv_id(paper_id)

        # 尝试从各个数据源获取论文详情
        for src in sources:
            try:
                if src == 'arxiv':
                    result = await self.arxiv_client.get_paper_details(paper_id)
                elif src == 'openalex':
                    # 如果是arXiv ID，使用专门的方法查找
                    if is_arxiv_id:
                        result = await self.openalex_client.get_paper_by_arxiv_id(paper_id)
                    else:
                        result = await self.openalex_client.get_paper_details(paper_id)
                elif src == 'semantic_scholar':
                    result = await self.semantic_scholar_client.get_paper_details(paper_id)
                else:
                    continue

                if result.get('success') and result.get('data'):
                    result['data']['source'] = src
                    logger.info(f"成功从 {src} 获取论文详情: {paper_id}")
                    return result
                else:
                    last_error = result.get('error', '未知错误')

            except Exception as e:
                last_error = str(e)
                logger.warning(f"从 {src} 获取论文详情失败: {e}")
                continue

        # 所有数据源都失败
        return {
            'success': False,
            'error': f'所有数据源获取论文详情失败。最后错误: {last_error}',
            'tried_sources': sources
        }

    def _is_arxiv_id(self, paper_id: str) -> bool:
        """
        检测是否为arXiv ID格式

        Args:
            paper_id: 论文ID

        Returns:
            是否为arXiv ID
        """
        # arXiv ID格式: YYMM.NNNNN 或 YYMM.NNNNNV
        # 例如: 2301.00001, 2301.00001v1
        import re
        arxiv_pattern = r'^\d{4}\.\d{5}(v\d+)?$'
        return bool(re.match(arxiv_pattern, paper_id))

    async def compare_sources(
        self,
        query: str,
        limit: int = 5
    ) -> Dict:
        """
        比较所有数据源的搜索结果

        Args:
            query: 搜索关键词
            limit: 每个数据源返回的论文数

        Returns:
            比较结果字典
        """
        results = {}

        # arXiv
        try:
            arxiv_result = await self.arxiv_client.search_papers(
                query=query,
                page=1,
                page_size=limit
            )
            results['arxiv'] = {
                'success': arxiv_result.get('success', False),
                'total': arxiv_result.get('data', {}).get('total', 0),
                'papers': arxiv_result.get('data', {}).get('papers', [])[:limit]
            }
        except Exception as e:
            results['arxiv'] = {'success': False, 'error': str(e)}

        # OpenAlex
        try:
            openalex_result = await self.openalex_client.search_papers(
                query=query,
                page=1,
                page_size=limit
            )
            results['openalex'] = {
                'success': openalex_result.get('success', False),
                'total': openalex_result.get('data', {}).get('total', 0),
                'papers': openalex_result.get('data', {}).get('papers', [])[:limit]
            }
        except Exception as e:
            results['openalex'] = {'success': False, 'error': str(e)}

        # Semantic Scholar
        try:
            s2_result = await self.semantic_scholar_client.search_papers(
                query=query,
                page=1,
                page_size=limit
            )
            results['semantic_scholar'] = {
                'success': s2_result.get('success', False),
                'total': s2_result.get('data', {}).get('total', 0),
                'papers': s2_result.get('data', {}).get('papers', [])[:limit]
            }
        except Exception as e:
            results['semantic_scholar'] = {'success': False, 'error': str(e)}

        return {
            'success': True,
            'data': {
                'query': query,
                'results': results
            }
        }


# 导出单例
_unified_search = None


def get_unified_search() -> UnifiedPaperSearch:
    """获取统一搜索服务单例"""
    global _unified_search
    if _unified_search is None:
        _unified_search = UnifiedPaperSearch()
    return _unified_search
