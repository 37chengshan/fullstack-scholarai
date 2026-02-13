"""
AI聊天与思维导图API测试套件
测试AI问答、流式聊天和思维导图生成功能
"""

import sys
import os
import json
import time
import asyncio

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
from services.zhipu_client import ZhipuClient, get_zhipu_client


class AIChatAPITester:
    """AI聊天API测试器"""

    def __init__(self, base_url="http://localhost:5000/api"):
        """
        初始化测试器

        Args:
            base_url: API基础URL
        """
        self.base_url = base_url
        self.session = requests.Session()

        # 测试用户凭据（需要先注册）
        self.test_user = {
            "email": "ai_test@example.com",
            "password": "TestPass123!",
            "name": "AI Test User"
        }

        # 访问token
        self.access_token = None
        self.user_id = None

    def setup(self):
        """
        测试前准备：注册用户并登录获取token

        Returns:
            bool: 准备是否成功
        """
        print("\n========== 测试前准备 ==========")

        # 尝试注册测试用户
        register_response = self.session.post(
            f"{self.base_url}/auth/register",
            json=self.test_user,
            timeout=10
        )

        if register_response.status_code in [200, 201]:
            print(f"✅ 用户注册成功: {self.test_user['email']}")
        elif register_response.status_code == 400:
            error_data = register_response.json()
            if "email" in str(error_data.get("error", "")) and "已存在" in str(error_data.get("error", "")):
                print("ℹ️  用户已存在，跳过注册")
            else:
                print(f"❌ 注册失败: {error_data}")
                return False
        else:
            print(f"❌ 注册失败: {register_response.status_code}")
            print(register_response.text)
            return False

        # 登录获取token
        login_response = self.session.post(
            f"{self.base_url}/auth/login",
            json={
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            },
            timeout=10
        )

        if login_response.status_code == 200:
            data = login_response.json()
            if data.get("success"):
                self.access_token = data["data"]["access_token"]
                self.user_id = data["data"]["user"]["id"]
                print(f"✅ 登录成功，获取token: {self.access_token[:50]}...")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                return True
            else:
                print(f"❌ 登录失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 登录失败: {login_response.status_code}")
            print(login_response.text)
            return False

    def cleanup(self):
        """测试后清理"""
        print("\n========== 测试后清理 ==========")
        # 这里可以添加清理逻辑，比如删除测试用户
        print("ℹ️  清理完成")

    # ==================== 测试用例 ====================

    def test_non_streaming_chat(self):
        """
        测试1：非流式AI聊天

        场景：用户向AI提问关于Transformer的问题
        预期：返回完整的AI回答，包含usage信息
        """
        print("\n========== 测试1: 非流式AI聊天 ==========")

        request_data = {
            "question": "什么是Transformer模型？",
            "chat_history": [],
            "api_config": {
                "model": "glm-4-flash",
                "temperature": 0.7,
                "max_tokens": 500
            }
        }

        print(f"📤 发送请求: POST {self.base_url}/ai/chat")
        print(f"📝 问题: {request_data['question']}")

        start_time = time.time()
        response = self.session.post(
            f"{self.base_url}/ai/chat",
            json=request_data,
            timeout=30
        )
        elapsed = time.time() - start_time

        print(f"⏱️  响应时间: {elapsed:.2f}秒")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                answer = data["data"]["answer"]
                usage = data["data"]["usage"]

                print("✅ 测试通过")
                print(f"📄 回答长度: {len(answer)} 字符")
                print(f"📊 Token使用:")
                print(f"   - Prompt: {usage['prompt_tokens']}")
                print(f"   - Completion: {usage['completion_tokens']}")
                print(f"   - Total: {usage['total_tokens']}")
                print(f"📦 模型: {data['data']['model']}")
                print(f"\n📝 AI回答预览: {answer[:200]}...")
                return True
            else:
                print(f"❌ 测试失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 测试失败: HTTP {response.status_code}")
            print(response.text)
            return False

    def test_chat_with_paper_context(self):
        """
        测试2：基于论文上下文的AI聊天

        场景：用户针对特定论文提问
        预期：AI基于论文内容给出回答
        """
        print("\n========== 测试2: 论文上下文聊天 ==========")

        request_data = {
            "question": "这篇论文的主要贡献是什么？",
            "paper_id": "2301.00001v1",  # 使用示例论文ID
            "chat_history": [],
            "api_config": {
                "model": "glm-4-flash",
                "max_tokens": 500
            }
        }

        print(f"📤 发送请求: POST {self.base_url}/ai/chat")
        print(f"📄 问题: {request_data['question']}")
        print(f"📄 论文ID: {request_data['paper_id']}")

        response = self.session.post(
            f"{self.base_url}/ai/chat",
            json=request_data,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                answer = data["data"]["answer"]
                print("✅ 测试通过")
                print(f"📝 AI回答预览: {answer[:200]}...")
                return True
            else:
                print(f"❌ 测试失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 测试失败: HTTP {response.status_code}")
            print(response.text)
            return False

    def test_chat_with_history(self):
        """
        测试3：带对话历史的聊天

        场景：用户继续之前的对话
        预期：AI理解上下文并给出相关回答
        """
        print("\n========== 测试3: 对话历史聊天 ==========")

        request_data = {
            "question": "那它和LSTM有什么区别？",
            "chat_history": [
                {"role": "user", "content": "什么是Transformer模型？"},
                {"role": "assistant", "content": "Transformer是一种基于自注意力机制的深度学习模型..."}
            ],
            "api_config": {
                "model": "glm-4-flash",
                "max_tokens": 500
            }
        }

        print(f"📤 发送请求: POST {self.base_url}/ai/chat")
        print(f"📄 问题: {request_data['question']}")
        print(f"📜 对话历史: {len(request_data['chat_history'])}条消息")

        response = self.session.post(
            f"{self.base_url}/ai/chat",
            json=request_data,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                answer = data["data"]["answer"]
                print("✅ 测试通过")
                print(f"📝 AI回答预览: {answer[:200]}...")
                return True
            else:
                print(f"❌ 测试失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 测试失败: HTTP {response.status_code}")
            print(response.text)
            return False

    def test_streaming_chat(self):
        """
        测试4：流式AI聊天

        场景：用户请求流式输出，实时看到AI回答
        预期：返回SSE格式的流式数据
        """
        print("\n========== 测试4: 流式AI聊天 ==========")

        request_data = {
            "question": "请详细解释注意力机制的原理",
            "chat_history": [],
            "api_config": {
                "model": "glm-4-flash",
                "max_tokens": 300
            }
        }

        print(f"📤 发送请求: POST {self.base_url}/ai/chat/stream")
        print(f"📄 问题: {request_data['question']}")

        try:
            response = self.session.post(
                f"{self.base_url}/ai/chat/stream",
                json=request_data,
                timeout=30,
                stream=True
            )

            if response.status_code == 200:
                print("✅ 连接成功，开始接收流式数据...")

                chunks_received = 0
                full_answer = ""

                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')

                        # SSE格式
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]

                            if data_str.strip() == '[DONE]':
                                print("✅ 流式传输完成")
                                break

                            try:
                                chunk_data = json.loads(data_str)
                                if "content" in chunk_data:
                                    chunk = chunk_data["content"]
                                    chunks_received += 1
                                    full_answer += chunk
                                    print(chunk, end='', flush=True)
                            except json.JSONDecodeError:
                                continue

                print(f"\n\n✅ 测试通过")
                print(f"📊 接收chunks: {chunks_received}")
                print(f"📝 完整回答长度: {len(full_answer)} 字符")
                return True
            else:
                print(f"❌ 测试失败: HTTP {response.status_code}")
                print(response.text)
                return False

        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            return False

    def test_mindmap_generation(self):
        """
        测试5：思维导图生成

        场景：用户请求为特定论文生成思维导图
        预期：返回结构化的思维导图JSON
        """
        print("\n========== 测试5: 思维导图生成 ==========")

        request_data = {
            "paper_id": "2301.00001v1",  # 使用示例论文ID
            "api_config": {
                "model": "glm-4-flash"
            }
        }

        print(f"📤 发送请求: POST {self.base_url}/ai/mindmap")
        print(f"📄 论文ID: {request_data['paper_id']}")

        response = self.session.post(
            f"{self.base_url}/ai/mindmap",
            json=request_data,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                mindmap = data["data"]["mindmap"]
                format_type = data["data"]["format"]

                print("✅ 测试��过")
                print(f"📊 导图格式: {format_type}")

                # 验证思维导图结构
                if "id" in mindmap and "label" in mindmap:
                    print(f"📌 根节点: {mindmap['label']}")
                    if "children" in mindmap:
                        print(f"🌿 分支数: {len(mindmap['children'])}")

                        # 打印结构预览
                        print(f"\n📝 思维导图结构:")
                        print_mindmap_structure(mindmap, indent=2)

                    return True
                else:
                    print("❌ 思维导图结构无效")
                    return False
            else:
                print(f"❌ 测试失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 测试失败: HTTP {response.status_code}")
            print(response.text)
            return False

    def test_mindmap_with_topic(self):
        """
        测试6：基于主题的思维导图生成

        场景：用户提供自定义主题
        预期：返回主题相关的思维导图
        """
        print("\n========== 测试6: 主题思维导图生成 ==========")

        request_data = {
            "topic": "深度学习",
            "api_config": {
                "model": "glm-4-flash"
            }
        }

        print(f"📤 发送请求: POST {self.base_url}/ai/mindmap")
        print(f"📄 主题: {request_data['topic']}")

        response = self.session.post(
            f"{self.base_url}/ai/mindmap",
            json=request_data,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                mindmap = data["data"]["mindmap"]
                print("✅ 测试通过")
                print(f"📌 根节点: {mindmap['label']}")
                if "children" in mindmap:
                    print(f"🌿 分支数: {len(mindmap['children'])}")
                return True
            else:
                print(f"❌ 测试失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 测试失败: HTTP {response.status_code}")
            print(response.text)
            return False

    def test_error_handling(self):
        """
        测试7：错误处理

        场景：发送无效请求，验证错误处理
        预期：返回合适的错误消息
        """
        print("\n========== 测试7: 错误处理 ==========")

        # 测试1: 空问题
        print("\n7.1 测试空问题...")
        response = self.session.post(
            f"{self.base_url}/ai/chat",
            json={"question": ""},
            timeout=10
        )
        if response.status_code == 400:
            print("✅ 空问题错误处理正确")
        else:
            print(f"❌ 空问题错误处理失败: {response.status_code}")
            return False

        # 测试2: 无效paper_id
        print("\n7.2 测试无效论文ID...")
        response = self.session.post(
            f"{self.base_url}/ai/chat",
            json={
                "question": "总结这篇论文",
                "paper_id": "invalid-id"
            },
            timeout=10
        )
        # 应该返回成功，但可能在获取论文时失败
        print(f"✅ 无效论文ID响应: {response.status_code}")

        # 测试3: mindmap缺少必要参数
        print("\n7.3 测试mindmap缺少参数...")
        response = self.session.post(
            f"{self.base_url}/ai/mindmap",
            json={},
            timeout=10
        )
        if response.status_code == 400:
            print("✅ 缺少参数错误处理正确")
            return True
        else:
            print(f"❌ 缺少参数错误处理失败: {response.status_code}")
            return False

    # ==================== 运行所有测试 ====================

    def run_all_tests(self):
        """
        运行所有测试用例

        Returns:
            dict: 测试结果统计
        """
        print("\n" + "="*60)
        print("AI聊天与思维导图API测试")
        print("="*60)

        # 准备
        if not self.setup():
            print("\n❌ 测试准备失败，退出测试")
            return {"total": 0, "passed": 0, "failed": 0}

        # 运行测试
        tests = [
            ("非流式AI聊天", self.test_non_streaming_chat),
            ("论文上下文聊天", self.test_chat_with_paper_context),
            ("对话历史聊天", self.test_chat_with_history),
            ("流式AI聊天", self.test_streaming_chat),
            ("思维导图生成（论文）", self.test_mindmap_generation),
            ("思维导图生成（主题）", self.test_mindmap_with_topic),
            ("错误处理", self.test_error_handling)
        ]

        results = {"total": len(tests), "passed": 0, "failed": 0, "tests": []}

        for test_name, test_func in tests:
            try:
                result = test_func()
                results["tests"].append({
                    "name": test_name,
                    "result": "PASS" if result else "FAIL"
                })
                if result:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                print(f"\n❌ 测试异常: {str(e)}")
                results["tests"].append({
                    "name": test_name,
                    "result": f"ERROR: {str(e)}"
                })
                results["failed"] += 1

        # 清理
        self.cleanup()

        # 打印结果统计
        print("\n" + "="*60)
        print("测试结果统计")
        print("="*60)
        print(f"总测试数: {results['total']}")
        print(f"✅ 通过: {results['passed']}")
        print(f"❌ 失败: {results['failed']}")
        print(f"📊 通过率: {results['passed']/results['total']*100:.1f}%")

        print("\n详细结果:")
        for test in results["tests"]:
            symbol = "✅" if test["result"] == "PASS" else "❌"
            print(f"  {symbol} {test['name']}: {test['result']}")

        return results


def print_mindmap_structure(node, indent=0):
    """
    辅助函数：打印思维导图结构

    Args:
        node: 思维导图节点
        indent: 缩进层级
    """
    prefix = "  " * indent
    print(f"{prefix}- {node.get('label', node.get('id', '?'))}")

    if "children" in node:
        for child in node["children"]:
            print_mindmap_structure(child, indent + 1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI聊天API测试")
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:5000/api",
        help="API基础URL"
    )

    args = parser.parse_args()

    tester = AIChatAPITester(base_url=args.url)
    results = tester.run_all_tests()

    # 根据测试结果设置退出码
    sys.exit(0 if results["failed"] == 0 else 1)
