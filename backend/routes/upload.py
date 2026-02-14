"""
ScholarAI - 文件上传API路由

提供文件上传到知识库的API端点。
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from typing import Dict, Any
import os
from werkzeug.utils import secure_filename

from services.zhipu_client import ZhipuClient
from middleware.auth import jwt_required_custom, get_current_user_id
from config.database import get_db


# 创建蓝图
upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')


def handle_error(message: str, status_code: int = 400) -> tuple:
    """
    统一错误处理

    参数:
        message: 错误消息
        status_code: HTTP状态码

    返回:
        tuple: (JSON响应, 状态码)
    """
    return jsonify({
        "success": False,
        "error": message
    }), status_code


def get_user_collection():
    """获取用户集合"""
    db = get_db()
    return db["users"]


def serialize_mongo_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    序列化MongoDB文档（处理ObjectId和datetime）

    参数:
        doc: MongoDB文档

    返回:
        Dict: 序列化后的文档
    """
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc


# ============================================================================
# API端点
# ============================================================================

@upload_bp.route('/file', methods=['POST'])
@jwt_required_custom()
def upload_file():
    """
    上传文件（主要用于PDF论文）

    请求体:
        FormData:
            - file: 文件对象
            - knowledge_id?: 知识库ID（可选）
            - title?: 文档标题（可选）
            - type?: 文档类型（可选，默认1）

    返回:
        {
            "success": true,
            "data": {
                "file_id": str,  # 文件ID
                "filename": str,  # 文件名
                "size": int,  # 文件大小（字节）
                "upload_url": str  # 上传的URL
            }
        }
    """
    try:
        # 获取当前用户ID
        user_id = get_current_user_id()

        # 检查是否有文件
        if 'file' not in request.files:
            return handle_error("没有找到文件")

        file = request.files['file']

        # 获取其他参数
        knowledge_id = request.form.get('knowledge_id')
        title = request.form.get('title')
        knowledge_type = int(request.form.get('type', 1))  # 默认为1（文档）

        # 验证文件
        if not file or not file.filename:
            return handle_error("无效的文件")

        # 安全文件名
        filename = secure_filename(file.filename)

        # 创建智谱AI客户端
        client = ZhipuClient()

        # 如果没有提供知识库ID，创建一个新的
        if not knowledge_id:
            # 创建新知识库
            from datetime import datetime
            knowledge_name = f"{user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

            knowledge_id = client.create_knowledge(
                name=knowledge_name,
                description=f"用户 {user_id} 的知识库",
                permission="public_me"  # 仅自己可见
            )

            if not knowledge_id:
                return handle_error("创建知识库失败")

        # 上传文件到智谱AI知识库
        result = client.upload_document(
            knowledge_id=knowledge_id,
            file_path=file,  # Flask FileStorage对象
            knowledge_type=knowledge_type,
            parse_image=False  # 不解析图片
        )

        # 返回结果
        return jsonify({
            "success": True,
            "data": {
                "file_id": result.get("file_id", ""),
                "filename": filename,
                "size": file.content_length,
                "knowledge_id": knowledge_id,
                "upload_url": result.get("url", "")
            }
        }), 200

    except Exception as e:
        return handle_error(f"上传文件失败: {str(e)}", 500)


@upload_bp.route('/url', methods=['POST'])
@jwt_required_custom()
def upload_url():
    """
    通过URL上传文档到知识库

    请求体:
        {
            "url": str,  # 文档URL
            "knowledge_id": str,  # 知识库ID（可选）
            "type": int  # 文档类型（可选，默认1）
            "title": str  # 文档标题（可选）
        }

    返回:
        {
            "success": true,
            "data": {
                "file_id": str,
                "url": str,
                "knowledge_id": str
            }
        }
    """
    try:
        # 获取当前用户ID
        user_id = get_current_user_id()

        # 获取请求数据
        data = request.get_json()
        if not data:
            return handle_error("请求体不能为空")

        # 验证必填字段
        if 'url' not in data or not data['url']:
            return handle_error("URL是必填字段")

        url = data['url']
        knowledge_id = data.get('knowledge_id')
        title = data.get('title')
        knowledge_type = data.get('type', 1)  # 默认为1（文档）

        # 创建智谱AI客户端
        client = ZhipuClient()

        # 如果没有提供知识库ID，创建一个新的
        if not knowledge_id:
            from datetime import datetime
            knowledge_name = f"{user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

            knowledge_id = client.create_knowledge(
                name=knowledge_name,
                description=f"用户 {user_id} 的知识库",
                permission="public_me"  # 仅自己可见
            )

            if not knowledge_id:
                return handle_error("创建知识库失败")

        # 通过URL上传文档到智谱AI知识库
        result = client.upload_url_document(
            knowledge_id=knowledge_id,
            url=url,
            knowledge_type=knowledge_type
        )

        # 返回结果
        return jsonify({
            "success": True,
            "data": {
                "file_id": result.get("file_id", ""),
                "url": url,
                "knowledge_id": knowledge_id,
                "title": title
            }
        }), 200

    except Exception as e:
        return handle_error(f"上传URL失败: {str(e)}", 500)


@upload_bp.route('/knowledge', methods=['POST'])
@jwt_required_custom()
def create_knowledge():
    """
    创建新的知识库

    请求体:
        {
            "name": str,  # 知识库名称
            "description": str  # 描述
            "permission": str  # 权限（可选）
        }

    返回:
        {
            "success": true,
            "data": {
                "knowledge_id": str,
                "name": str,
                "description": str,
                "permission": str
            }
        }
    """
    try:
        # 获取当前用户ID
        user_id = get_current_user_id()

        # 获取请求数据
        data = request.get_json()
        if not data:
            return handle_error("请求体不能为空")

        # 验证必填字段
        if 'name' not in data or not data['name']:
            return handle_error("知识库名称是必填字段")

        name = data['name']
        description = data.get('description', '')
        permission = data.get('permission', 'public_me')

        # 创建智谱AI客户端
        client = ZhipuClient()

        # 创建知识库
        knowledge_id = client.create_knowledge(
            name=name,
            description=description,
            permission=permission
        )

        if not knowledge_id:
            return handle_error("创建知识库失败")

        # 返回结果
        return jsonify({
            "success": True,
            "data": {
                "knowledge_id": knowledge_id,
                "name": name,
                "description": description,
                "permission": permission
            }
        }), 201

    except Exception as e:
        return handle_error(f"创建知识库失败: {str(e)}", 500)


@upload_bp.route('/progress/<upload_id>', methods=['GET'])
@jwt_required_custom()
def get_upload_progress():
    """
    获取上传进度（占位端点，实际实现可能需要后台任务）

    参数:
        upload_id: 上传任务ID

    返回:
        {
            "success": true,
            "data": {
                "upload_id": str,
                "status": str,  # pending, uploading, completed, failed
                "progress": int,  # 0-100
                "uploaded_bytes": int,
                "total_bytes": int
            }
        }
    """
    try:
        # TODO: 实现真实的上传进度追踪
        # 当前返回模拟数据
        return jsonify({
            "success": True,
            "data": {
                "upload_id": upload_id,
                "status": "completed",
                "progress": 100,
                "uploaded_bytes": 0,
                "total_bytes": 0
            }
        }), 200

    except Exception as e:
        return handle_error(f"获取上传进度失败: {str(e)}", 500)
