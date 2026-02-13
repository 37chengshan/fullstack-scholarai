"""
Quick verification script for arXiv API
快速验证arXiv API功能
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.arxiv_client import ArxivClient
import asyncio


def verify_arxiv_client():
    """验证arXiv客户端基础功能"""
    print("="*60)
    print("arXiv API Verification")
    print("="*60)

    # 创建客户端
    client = ArxivClient()

    async def test_search():
        print("\n测试 1: 基础搜索")
        print("-" * 60)

        result = await client.search_papers(
            query="artificial intelligence",
            page=1,
            page_size=3
        )

        if result['success']:
            data = result['data']
            print(f"✅ 搜索成功!")
            print(f"   总论文数: {data['total']}")
            print(f"   当前页: {data['page']}/{data['total_pages']}")
            print(f"\n前3篇论文:")

            for i, paper in enumerate(data['papers'], 1):
                print(f"\n{i}. {paper['title'][:80]}...")
                print(f"   ID: {paper['paper_id']}")
                print(f"   作者: {', '.join(paper['authors'][:2])}")
                print(f"   年份: {paper['published_year']}")
                print(f"   分类: {paper['primary_category']}")

            return True
        else:
            print(f"❌ 搜索失败: {result.get('error')}")
            return False

    async def test_paper_details():
        print("\n\n测试 2: 获取论文详情")
        print("-" * 60)

        # 使用固定的arXiv论文ID
        paper_id = "2301.00001"
        result = await client.get_paper_details(paper_id)

        if result['success']:
            paper = result['data']
            print(f"✅ 获取论文详情成功!")
            print(f"   论文ID: {paper['paper_id']}")
            print(f"   标题: {paper['title']}")
            print(f"   作者: {len(paper['authors'])} 位")
            print(f"   发表时间: {paper['published']}")
            print(f"   分类: {paper['primary_category']}")
            print(f"   PDF链接: {paper['pdf_url'][:60]}...")

            return True
        else:
            print(f"❌ 获取论文详情失败: {result.get('error')}")
            return False

    async def test_pdf_url():
        print("\n\n测试 3: 获取PDF URL")
        print("-" * 60)

        paper_id = "2301.00001"
        result = await client.get_paper_pdf_url(paper_id)

        if result['success']:
            pdf_url = result['data']['pdf_url']
            print(f"✅ 获取PDF URL成功!")
            print(f"   PDF URL: {pdf_url}")
            return True
        else:
            print(f"❌ 获取PDF URL失败: {result.get('error')}")
            return False

    # 运行测试
    async def run_all():
        test1 = await test_search()
        test2 = await test_paper_details()
        test3 = await test_pdf_url()

        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        passed = sum([test1, test2, test3])
        print(f"通过: {passed}/3")

        if passed == 3:
            print("\n✅ 所有测试通过! arXiv API集成成功!")
            return 0
        else:
            print(f"\n⚠️  {3-passed} 个测试失败")
            return 1

    return asyncio.run(run_all())


if __name__ == '__main__':
    exit_code = verify_arxiv_client()
    sys.exit(exit_code)
