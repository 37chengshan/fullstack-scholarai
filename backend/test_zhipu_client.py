"""
智谱AI客户端测试脚本
测试ZhipuClient的各项功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.zhipu_client import ZhipuClient, get_zhipu_client


async def test_connection():
    """测试1: API连接测试"""
    print("\n" + "="*60)
    print("测试1: API连接测试")
    print("="*60)

    try:
        client = get_zhipu_client()
        result = await client.test_connection()

        if result["success"]:
            print("✅ API连接成功")
            print(f"   模型: {result.get('model')}")
            return True
        else:
            print(f"❌ API连接失败: {result.get('message')}")
            return False

    except Exception as e:
        print(f"❌ 连接测试异常: {e}")
        return False


async def test_chat_completion():
    """测试2: 基础聊天补全"""
    print("\n" + "="*60)
    print("测试2: 基础聊天补全")
    print("="*60)

    try:
        client = get_zhipu_client()

        messages = [
            {"role": "system", "content": "你是一个专业的AI助手。"},
            {"role": "user", "content": "请用一句话介绍智谱AI。"}
        ]

        print(f"发送消息: {messages[-1]['content']}")

        result = await client.chat_completion(
            messages=messages,
            model="glm-4-flash",
            max_tokens=100
        )

        if result["success"]:
            content = result["data"]["choices"][0]["message"]["content"]
            print(f"✅ 聊天补全成功")
            print(f"   回复: {content}")
            return True
        else:
            print(f"❌ 聊天补全失败: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ 聊天补全异常: {e}")
        return False


async def test_stream_chat():
    """测试3: 流式聊天补全"""
    print("\n" + "="*60)
    print("测试3: 流式聊天补全")
    print("="*60)

    try:
        client = get_zhipu_client()

        messages = [
            {"role": "user", "content": "请数到5，每个数字之间用空格分隔。"}
        ]

        print(f"发送消息: {messages[-1]['content']}")
        print("流式回复: ", end="", flush=True)

        full_response = ""
        async for chunk in client.chat_completion_stream(messages=messages):
            print(chunk, end="", flush=True)
            full_response += chunk

        print(f"\n✅ 流式聊天成功")
        print(f"   完整回复: {full_response}")
        return True

    except Exception as e:
        print(f"\n❌ 流式聊天异常: {e}")
        return False


async def test_paper_analysis():
    """测试4: 论文分析场景"""
    print("\n" + "="*60)
    print("测试4: 论文分析场景")
    print("="*60)

    try:
        client = get_zhipu_client()

        # 模拟论文分析
        paper_abstract = """
        This paper proposes a novel deep learning architecture for natural language understanding.
        Our approach combines transformer-based models with graph neural networks to capture
        both local and global dependencies in text. Extensive experiments on benchmark
        datasets demonstrate state-of-the-art performance.
        """

        messages = [
            {
                "role": "system",
                "content": "你是一个专业的学术论文助手。请简洁地总结论文要点。"
            },
            {
                "role": "user",
                "content": f"请用中文总结以下论文摘要的核心贡献（不超过100字）：\n\n{paper_abstract}"
            }
        ]

        print(f"论文分析请求...")

        result = await client.chat_completion(
            messages=messages,
            model="glm-4-flash",
            temperature=0.3,  # 降低温度以获得更确定的输出
            max_tokens=200
        )

        if result["success"]:
            summary = result["data"]["choices"][0]["message"]["content"]
            print(f"✅ 论文分析成功")
            print(f"   摘要总结: {summary}")
            return True
        else:
            print(f"❌ 论文分析失败: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ 论文分析异常: {e}")
        return False


async def test_model_info():
    """测试5: 模型信息"""
    print("\n" + "="*60)
    print("测试5: 模型信息")
    print("="*60)

    try:
        client = get_zhipu_client()

        # 获取可用模型列表
        models = client.get_available_models()
        print(f"✅ 可用免费模型: {', '.join(models)}")

        # 检查特定模型
        test_model = "glm-4-flash"
        is_free = client.is_free_model(test_model)
        print(f"   {test_model} 是否免费: {is_free}")

        return True

    except Exception as e:
        print(f"❌ 获取模型信息异常: {e}")
        return False


async def test_error_handling():
    """测试6: 错误处理"""
    print("\n" + "="*60)
    print("测试6: 错误处理")
    print("="*60)

    try:
        client = get_zhipu_client()

        # 测试无效模型
        print("测试1: 无效模型名称")
        result = await client.chat_completion(
            messages=[{"role": "user", "content": "Hi"}],
            model="invalid-model-name"
        )

        if not result["success"]:
            print(f"✅ 正确处理了无效模型: {result.get('error', 'Unknown error')[:50]}...")
        else:
            print("⚠️  未能检测到无效模型")

        # 测试空消息
        print("\n测试2: 空消息列表")
        result = await client.chat_completion(messages=[])

        if not result["success"]:
            print(f"✅ 正确处理了空消息: {result.get('error', 'Unknown error')[:50]}...")
        else:
            print("⚠️  未能检测到空消息")

        return True

    except Exception as e:
        print(f"❌ 错误处理测试异常: {e}")
        return False


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("智谱AI客户端功能测试")
    print("="*60)

    tests = [
        ("API连接", test_connection),
        ("基础聊天补全", test_chat_completion),
        ("流式聊天", test_stream_chat),
        ("论文分析场景", test_paper_analysis),
        ("模型信息", test_model_info),
        ("错误处理", test_error_handling)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{name}' 发生未捕获异常: {e}")
            results.append((name, False))

    # 打印测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    print(f"\n通过率: {passed}/{total} ({passed*100//total}%)")

    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())
