"""
智谱AI API客户端
封装智谱AI的Chat Completions API、Agent API和知识库API调用
基于智谱AI官方API文档实现
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any, Generator
from datetime import datetime
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZhipuClient:
    """智谱AI客户端"""

    # API端点配置
    API_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
    CHAT_ENDPOINT = f"{API_BASE_URL}/chat/completions"
    AGENT_ENDPOINT = f"{API_BASE_URL}/agents"

    # 可用的免费模型
    FREE_MODELS = [
        "glm-4-flash",
        "glm-4-flashx",
        "glm-4-air"
    ]

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化智谱AI客户端

        Args:
            api_key: 智谱AI API密钥 (格式: id.secret)
                    如果不提供，将从环境变量ZHIPU_API_KEY读取
        """
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY")
        if not self.api_key:
            raise ValueError("智谱AI API密钥未设置，请提供api_key或设置ZHIPU_API_KEY环境变量")

        # 验证API密钥格式
        if "." not in self.api_key:
            raise ValueError("智谱AI API密钥格式错误，应为 'id.secret' 格式")

        # 初始化session
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

        logger.info("智谱AI客户端初始化成功")

    def _parse_api_key(self) -> tuple[str, str]:
        """
        解析API密钥，提取ID和Secret

        Returns:
            (api_id, api_secret)
        """
        parts = self.api_key.split(".")
        if len(parts) != 2:
            raise ValueError("API密钥格式错误")

        return parts[0], parts[1]

    def _handle_response(self, response: requests.Response) -> Dict:
        """
        处理API响应

        Args:
            response: HTTP响应对象

        Returns:
            响应数据字典
        """
        try:
            response.raise_for_status()
            data = response.json()

            # 检查智谱AI的错误响应
            if "error" in data:
                error_msg = data["error"].get("message", "未知错误")
                error_code = data["error"].get("code", "unknown")
                logger.error(f"智谱AI API错误: {error_code} - {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "error_code": error_code
                }

            return {
                "success": True,
                "data": data
            }

        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP错误: {e.response.status_code}"
            try:
                error_data = e.response.json()
                if "error" in error_data:
                    error_msg = error_data["error"].get("message", error_msg)
            except:
                pass

            logger.error(f"HTTP错误: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "status_code": e.response.status_code
            }

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return {
                "success": False,
                "error": f"响应解析失败: {str(e)}"
            }

        except Exception as e:
            logger.error(f"处理响应时发生错误: {e}")
            return {
                "success": False,
                "error": f"处理响应失败: {str(e)}"
            }

    def _retry_request(
        self,
        func,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Dict:
        """
        重试请求逻辑

        Args:
            func: 请求函数
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）

        Returns:
            响应数据字典
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.warning(f"请求失败，{retry_delay}秒后重试 ({attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    logger.error(f"请求失败，已达最大重试次数: {str(e)}")

        return {
            "success": False,
            "error": f"请求失败: {str(last_error)}"
        }

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "glm-4-flash",
        stream: bool = False,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: Optional[int] = None,
        custom_variables: Optional[Dict] = None
    ) -> Dict:
        """
        调用智谱AI聊天补全API

        Args:
            messages: 消息列表，格式: [{"role": "user", "content": "..."}]
            model: 模型名称 (默认: glm-4-flash)
            stream: 是否使用流式输出
            temperature: 温度参数 (0-1)
            top_p: top_p参数 (0-1)
            max_tokens: 最大生成token数
            custom_variables: 自定义变量 (用于Agent API)

        Returns:
            响应数据字典
        """
        def make_request():
            # 构建请求体
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream,
                "temperature": temperature,
                "top_p": top_p
            }

            if max_tokens:
                payload["max_tokens"] = max_tokens

            if custom_variables:
                payload["custom_variables"] = custom_variables

            logger.info(f"发送聊天请求，模型: {model}")

            response = self.session.post(
                self.CHAT_ENDPOINT,
                json=payload,
                timeout=60
            )

            return self._handle_response(response)

        return self._retry_request(make_request)

    def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "glm-4-flash",
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: Optional[int] = None,
        custom_variables: Optional[Dict] = None
    ) -> Generator[str, None, None]:
        """
        流式聊天补全

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            top_p: top_p参数
            max_tokens: 最大生成token数
            custom_variables: 自定义变量

        Yields:
            str: 每次生成的文本片段
        """
        # 构建请求体
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "temperature": temperature,
            "top_p": top_p
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        if custom_variables:
            payload["custom_variables"] = custom_variables

        try:
            logger.info(f"发送流式聊天请求，模型: {model}")

            response = self.session.post(
                self.CHAT_ENDPOINT,
                json=payload,
                stream=True,
                timeout=120
            )

            response.raise_for_status()

            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')

                    # SSE格式: data: {...}
                    if line.startswith('data: '):
                        data_str = line[6:]  # 移除 "data: " 前缀

                        # 检查结束标记
                        if data_str.strip() == '[DONE]':
                            break

                        try:
                            data = json.loads(data_str)

                            # 提取内容
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content

                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"流式请求失败: {e}")
            yield f"错误: {str(e)}"

    async def upload_document(
        self,
        knowledge_id: str,
        file_path: str,
        knowledge_type: int = 1,
        parse_image: bool = False,
        custom_separator: Optional[str] = None
    ) -> Dict:
        """
        上传文档到知识库

        Args:
            knowledge_id: 知识库ID
            file_path: 文件路径
            knowledge_type: 知识库类型 (1: FAQ, 2: 长文档, 3: 网页)
            parse_image: 是否解析图片 (OCR)
            custom_separator: 自定义分隔符

        Returns:
            上传结果字典
        """
        def make_request():
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")

            # 准备文件
            files = {
                'file': (os.path.basename(file_path), open(file_path, 'rb'))
            }

            data = {
                'knowledge_id': knowledge_id,
                'knowledge_type': knowledge_type,
                'parse_image': str(parse_image).lower()
            }

            if custom_separator:
                data['custom_separator'] = custom_separator

            logger.info(f"上传文档到知识库: {knowledge_id}")

            # 注意: 知识库API的端点可能不同，这里使用通用端点
            url = f"{self.API_BASE_URL}/knowledge/document"

            response = self.session.post(
                url,
                files=files,
                data=data,
                timeout=300  # 5分钟超时（上传大文件）
            )

            return self._handle_response(response)

        return self._retry_request(make_request, max_retries=2, retry_delay=2.0)

    async def upload_url_document(
        self,
        knowledge_id: str,
        url: str,
        knowledge_type: int = 1,
        parse_image: bool = False
    ) -> Dict:
        """
        通过URL上传文档到知识库

        Args:
            knowledge_id: 知识库ID
            url: 文档URL
            knowledge_type: 知识库类型
            parse_image: 是否解析图片

        Returns:
            上传结果字典
        """
        def make_request():
            payload = {
                'knowledge_id': knowledge_id,
                'url': url,
                'knowledge_type': knowledge_type,
                'parse_image': parse_image
            }

            logger.info(f"通过URL上传文档到知识库: {knowledge_id}")

            api_url = f"{self.API_BASE_URL}/knowledge/url-document"
            response = self.session.post(
                api_url,
                json=payload,
                timeout=60
            )

            return self._handle_response(response)

        return self._retry_request(make_request, max_retries=2, retry_delay=2.0)

    async def create_knowledge(
        self,
        name: str,
        description: Optional[str] = None,
        permission: int = 1
    ) -> Dict:
        """
        创建知识库

        Args:
            name: 知识库名称
            description: 知识库描述
            permission: 权限设置 (1: 私有, 2: 公开)

        Returns:
            创建结果字典
        """
        def make_request():
            payload = {
                'name': name,
                'permission': permission
            }

            if description:
                payload['description'] = description

            logger.info(f"创建知识库: {name}")

            api_url = f"{self.API_BASE_URL}/knowledge"
            response = self.session.post(
                api_url,
                json=payload,
                timeout=30
            )

            return self._handle_response(response)

        return self._retry_request(make_request)

    async def get_conversation_history(
        self,
        agent_id: str,
        conversation_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """
        获取对话历史

        Args:
            agent_id: Agent ID
            conversation_id: 对话ID
            page: 页码
            page_size: 每页数量

        Returns:
            对话历史字典
        """
        def make_request():
            params = {
                'page': page,
                'page_size': page_size
            }

            logger.info(f"获取对话历史: {conversation_id}")

            api_url = f"{self.AGENT_ENDPOINT}/{agent_id}/conversations/{conversation_id}/messages"
            response = self.session.get(
                api_url,
                params=params,
                timeout=30
            )

            return self._handle_response(response)

        return self._retry_request(make_request)

    async def create_agent(
        self,
        name: str,
        prompt: str,
        model: str = "glm-4-flash",
        tools: Optional[List[Dict]] = None
    ) -> Dict:
        """
        创建Agent

        Args:
            name: Agent名称
            prompt: 系统提示词
            model: 使用的模型
            tools: 工具列表

        Returns:
            Agent创建结果
        """
        def make_request():
            payload = {
                'name': name,
                'prompt': prompt,
                'model': model
            }

            if tools:
                payload['tools'] = tools

            logger.info(f"创建Agent: {name}")

            response = self.session.post(
                self.AGENT_ENDPOINT,
                json=payload,
                timeout=30
            )

            return self._handle_response(response)

        return self._retry_request(make_request)

    async def test_connection(self) -> Dict:
        """
        测试API连接

        Returns:
            测试结果字典
        """
        try:
            # 发送简单的测试请求
            messages = [{"role": "user", "content": "Hi"}]

            result = await self.chat_completion(
                messages=messages,
                max_tokens=10
            )

            if result.get("success"):
                return {
                    "success": True,
                    "message": "智谱AI API连接成功",
                    "model": result["data"].get("model", "unknown")
                }
            else:
                return {
                    "success": False,
                    "message": result.get("error", "连接失败")
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"连接测试失败: {str(e)}"
            }

    def is_free_model(self, model: str) -> bool:
        """
        检查是否为免费模型

        Args:
            model: 模型名称

        Returns:
            是否为免费模型
        """
        return model in self.FREE_MODELS

    def get_available_models(self) -> List[str]:
        """
        获取可用的免费模型列表

        Returns:
            免费模型名称列表
        """
        return self.FREE_MODELS.copy()


# 导出单例
_zhipu_client = None


def get_zhipu_client() -> ZhipuClient:
    """获取智谱AI客户端单例"""
    global _zhipu_client
    if _zhipu_client is None:
        _zhipu_client = ZhipuClient()
    return _zhipu_client
