"""
统一搜索服务修复 - 彻底解决 OpenAlex API 问题

问题分析：
1. OpenAlex API 返回 400 Bad Request
2. 错误 URL: filter=publication_year:2020,2024
3. 原因：年份过滤器格式不正确
4. backend\services\openalex_client.py 使用了错误的过滤器构建逻辑

修复策略：
1. 直接在 unified_search.py 中调用 openalex_client
2. 绕过 unified_search.py 的 filter_fields 转换
3. 确保使用正确的 OpenAlex 过滤器格式
"""

import asyncio
import logging
from typing import Dict, Optional

from services.openalex_client import get_openalex_client
from services.arxiv_client import get_arxiv_client
from services.semantic_scholar_client import get_semantic_scholar_client

logger = logging.getLogger(__name__)


class FixedPaperSearch:
    """修复后的统一论文搜索服务"""

    def __init__(self):
        self.openalex_client = get_openalex_client()
        self.arxiv_client = get_arxiv_client()
        self.semantic_scholar_client = get_semantic_scholar_client()

    def _normalize_paper(self, paper: Dict, source: str) -> Dict:
        """
        标准化论文数据格式（不同API返回的数据结构略有不同）
        """
        # 添加���据源标识
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
        统一论文搜索接口 - 修复版本

        优先使用arXiv，失败时自动回退到OpenAlex
        """
        # 确定数据源优先级
        if preferred_source and preferred_source in self.SOURCES:
            sources = [preferred_source] + [s for s in self.SOURCES if s != preferred_source]
        else:
            sources = self.SOURCES

        logger.info(f"搜索关键词: {query}")
        logger.info(f"数据源: {sources}")

        # 优先使用arXiv，失败时自动回退到OpenAlex
        sources_to_try = ['arxiv', 'openalex', 'semantic_scholar']

        last_error = None
        results = {}

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
                        results['arxiv'] = result
                        last_error = None
                        break

                elif source == 'openalex':
                    # 直接调用 OpenAlex，不经过 unified_search
                    logger.info("使用 OpenAlex 搜索...")

                    # 构建OpenAlex过滤器 - 使用正确的格式
                    openalex_filters = {}
                    if year_min or year_max:
                        # OpenAlex API 格式：使用 from_publication_year 和 to_publication_year
                        if year_min and year_max:
                            # 使用 from_publication_year 而不是 from_publication_year
                            openalex_filters['from_publication_year'] = f'{year_min}'
                            openalex_filters['to_publication_year'] = f'{year_max}'
                        elif year_min:
                            openalex_filters['from_publication_year'] = f'>{year_min}'
                        elif year_max:
                            openalex_filters['to_publication_year'] = f'<{year_max}'

                    logger.info(f"OpenAlex 过滤器: {openalex_filters}")

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
                        results['openalex'] = result
                        last_error = None
                        break

                elif source == 'semantic_scholar':
                    result = await self.semantic_scholar_client.search_papers(
                        query=query,
                        fields_of_study=[field] if field else None,
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
                        results['semantic_scholar'] = result
                        last_error = None
                        break

            except Exception as e:
                logger.error(f"{source} 搜索异常: {e}")
                last_error = str(e)
                logger.warning(f"尝试 {source} 失败，准备尝试下一个数据源")

        # 所有数据源都失败
        if not results:
            return {
                'success': False,
                'error': f'所有数据源搜索失败。最后错误: {last_error}',
                'tried_sources': sources
            }

        # 按照优先级返回结果（arXiv优先）
        if results.get('arxiv'):
            return results['arxiv']
        elif results.get('openalex'):
            return results['openalex']
        elif results.get('semantic_scholar'):
            return results['semantic_scholar']

        # 比较结果
        if len(results) > 1:
            # 有多个数据源成功
            comparison = {
                'arxiv': results.get('arxiv', {}).get('data', {}).get('total', 0),
                'openalex': results.get('openalex', {}).get('data', {}).get('total', 0),
                'semantic_scholar': results.get('semantic_scholar', {}).get('data', {}).get('total', 0)
            }

            return {
                'success': True,
                'data': {
                    'query': query,
                    'comparison': comparison,
                    'results': results,
                    'tried_sources': sources
                }
            }


# 导出单例
_fixed_paper_search = None

def get_fixed_paper_search() -> FixedPaperSearch:
    """获取修复后的统一搜索服务单例"""
    global _fixed_paper_search
    if _fixed_paper_search is None:
        _fixed_paper_search = FixedPaperSearch()
        logger.info("创建了修复后的统一搜索服务单例")
    return _fixed_paper_search


async def test_openalex_search():
    """测试 OpenAlex 搜索功能"""
    search = get_fixed_paper_search()

    # 测试1: 简单搜索
    print("\n=== 测试 1: 简单搜索 ===")
    result = await search.search_papers(
        query='machine learning',
        page=1,
        page_size=5
    )

    print(f"结果: {result['success']}")
    if result.get('success'):
        data = result.get('data', {})
        if data.get('papers'):
            print(f"找到 {len(data['papers'])} 篇论文")
            for i, paper in enumerate(data['papers'][:3]):
                print(f"{i+1}. {paper.get('title', 'N/A')[:80]}")
                print(f"数据源: {data.get('source')}")
                print(f"总数: {data.get('total', 0)}")
    else:
            print(f"错误: {data.get('error')}")

    # 测试2: 年份过滤
    print("\n=== 测试 2: 年份过滤 ===")
    result = await search.search_papers(
        query='machine learning',
        year_min=2020,
        year_max=2024,
        page=1,
        page_size=5
    )

    print(f"结果: {result['success']}")
    if result.get('success'):
        data = result.get('data', {})
        if data.get('papers'):
            print(f"找到 {len(data['papers'])} 篇论文")
            for i, paper in enumerate(data['papers'][:3]):
                print(f"{i+1}. {paper.get('title', 'N/A')[:80]}")
                print(f"数据源: {data.get('source')}")
                print(f"总数: {data.get('total', 0)}")
    else:
            print(f"错误: {data.get('error')}")


if __name__ == '__main__':
    """测试脚本"""
    import asyncio
    import sys
    import os

    # 添加当前目录到 Python 路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from services.unified_search_fix import test_openalex_search, get_fixed_paper_search

    async def main():
        """主测试函数"""
        print("ScholarAI 统一搜索服务修复测试")
        print("=" * 60)

        # 测试 OpenAlex 搜索
        await test_openalex_search()

        print("\n测试完成！")
        print("=" * 60)
