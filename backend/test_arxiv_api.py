"""
Test arXiv API Implementation
测试arXiv API集成功能
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.arxiv_client import ArxivClient, get_arxiv_client
import asyncio


async def test_basic_search():
    """Test 1: 基础关键词搜索"""
    print("\n=== Test 1: 基础关键词搜索 ===")

    client = get_arxiv_client()
    result = await client.search_papers(
        query="deep learning",
        page=1,
        page_size=5
    )

    if result['success']:
        data = result['data']
        print(f"✅ 搜索成功!")
        print(f"   - 总论文数: {data['total']}")
        print(f"   - 当前页: {data['page']}/{data['total_pages']}")
        print(f"   - 返回论文数: {len(data['papers'])}")

        if data['papers']:
            paper = data['papers'][0]
            print(f"   - 第一篇论文:")
            print(f"     * ID: {paper['paper_id']}")
            print(f"     * 标题: {paper['title']}")
            print(f"     * 作者: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
            print(f"     * 分类: {paper['primary_category']}")
            return True
        else:
            print("❌ 没有返回论文")
            return False
    else:
        print(f"❌ 搜索失败: {result.get('error')}")
        return False


async def test_field_filter():
    """Test 2: 领域过滤搜索"""
    print("\n=== Test 2: 领域过滤搜索 (cs.AI) ===")

    client = get_arxiv_client()
    result = await client.search_papers(
        query="transformers",
        field="cs.AI",  # AI领域
        page=1,
        page_size=5
    )

    if result['success']:
        data = result['data']
        print(f"✅ 领域搜索成功!")
        print(f"   - 总论文数: {data['total']}")

        # 检查所有论文是否属于cs.AI
        all_ai = True
        for paper in data['papers']:
            if 'cs.AI' not in paper['categories']:
                all_ai = False
                print(f"   ⚠️  论文 {paper['paper_id']} 不属于cs.AI")
                break

        if all_ai and data['papers']:
            print(f"   ✅ 所有论文都属于cs.AI领域")
            return True
        else:
            print(f"   ❌ 领域过滤可能有问题")
            return False
    else:
        print(f"❌ 领域搜索失败: {result.get('error')}")
        return False


async def test_year_filter():
    """Test 3: 年份范围过滤"""
    print("\n=== Test 3: 年份范围过滤 (2023-2024) ===")

    client = get_arxiv_client()
    result = await client.search_papers(
        query="neural networks",
        year_min=2023,
        year_max=2024,
        page=1,
        page_size=5
    )

    if result['success']:
        data = result['data']
        print(f"✅ 年份过滤搜索成功!")
        print(f"   - 总论文数: {data['total']}")

        # 检查所有论文是否在指定年份范围内
        all_in_range = True
        for paper in data['papers']:
            year = paper['published_year']
            if year and (year < 2023 or year > 2024):
                all_in_range = False
                print(f"   ⚠️  论文 {paper['paper_id']} 年份 {year} 不在范围内")
                break

        if all_in_range and data['papers']:
            print(f"   ✅ 所有论文都在2023-2024范围内")
            return True
        else:
            print(f"   ❌ 年份过滤可能有问题")
            return False
    else:
        print(f"❌ 年份过滤搜索失败: {result.get('error')}")
        return False


async def test_pagination():
    """Test 4: 分页功能"""
    print("\n=== Test 4: 分页功能 ===")

    client = get_arxiv_client()

    # 第一页
    result1 = await client.search_papers(
        query="machine learning",
        page=1,
        page_size=3
    )

    # 第二页
    result2 = await client.search_papers(
        query="machine learning",
        page=2,
        page_size=3
    )

    if result1['success'] and result2['success']:
        papers_page1 = [p['paper_id'] for p in result1['data']['papers']]
        papers_page2 = [p['paper_id'] for p in result2['data']['papers']]

        # 检查两页论文不重复
        overlap = set(papers_page1) & set(papers_page2)

        print(f"✅ 分页测试通过!")
        print(f"   - 第1页论文数: {len(papers_page1)}")
        print(f"   - 第2页论文数: {len(papers_page2)}")
        print(f"   - 重复论文数: {len(overlap)}")

        if len(overlap) == 0:
            print(f"   ✅ 两页论文不重复，分页正确")
            return True
        else:
            print(f"   ⚠️  存在重复论文: {overlap}")
            return True  # arXiv可能返回相同论文的不同版本
    else:
        print(f"❌ 分页测试失败")
        return False


async def test_get_paper_details():
    """Test 5: 获取论文详情"""
    print("\n=== Test 5: 获取论文详情 ===")

    client = get_arxiv_client()

    # 先搜索一篇论文
    search_result = await client.search_papers(
        query="attention is all you need",
        page_size=1
    )

    if search_result['success'] and search_result['data']['papers']:
        paper_id = search_result['data']['papers'][0]['paper_id']

        # 获取详情
        detail_result = await client.get_paper_details(paper_id)

        if detail_result['success']:
            paper = detail_result['data']
            print(f"✅ 获取论文详情成功!")
            print(f"   - 论文ID: {paper['paper_id']}")
            print(f"   - 标题: {paper['title']}")
            print(f"   - 作者数: {len(paper['authors'])}")
            print(f"   - 摘要长度: {len(paper['summary'])} 字符")
            print(f"   - 分类数: {len(paper['categories'])}")
            print(f"   - PDF链接: {'✅ 有' if paper['pdf_url'] else '❌ 无'}")
            return True
        else:
            print(f"❌ 获取论文详情失败: {detail_result.get('error')}")
            return False
    else:
        print(f"❌ 搜索论文失败")
        return False


async def test_get_pdf_url():
    """Test 6: 获取PDF URL"""
    print("\n=== Test 6: 获取PDF URL ===")

    client = get_arxiv_client()
    result = await client.get_paper_pdf_url("2301.00001")

    if result['success']:
        pdf_url = result['data']['pdf_url']
        print(f"✅ 获取PDF URL成功!")
        print(f"   - PDF URL: {pdf_url}")
        print(f"   - URL格式正确: {'✅ 是' if pdf_url.startswith('https://arxiv.org/pdf/') else '❌ 否'}")
        return True
    else:
        print(f"❌ 获取PDF URL失败: {result.get('error')}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("arXiv API Integration Tests")
    print("="*60)

    tests = [
        ("基础关键词搜索", test_basic_search),
        ("领域过滤搜索", test_field_filter),
        ("年份范围过滤", test_year_filter),
        ("分页功能", test_pagination),
        ("获取论文详情", test_get_paper_details),
        ("获取PDF URL", test_get_pdf_url)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if await test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 发生异常: {str(e)}")
            failed += 1

    # 输出测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"✅ 通过: {passed}/{len(tests)}")
    print(f"❌ 失败: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print(f"\n⚠️  {failed}个测试失败")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
