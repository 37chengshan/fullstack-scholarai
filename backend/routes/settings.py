"""
ScholarAI - 用户设置与统计API路由

提供用户设置管理和使用统计相关的API端点。
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from typing import Dict, Any, Optional
import pymongo
from datetime import datetime
from bson import ObjectId
import os

from models.settings import UserSettings, Theme, Language, ApiConfig
from models.user import User, UserStats
from middleware.auth import jwt_required_custom, get_current_user_id
from config.database import get_db


# 创建蓝图
settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')


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


def get_user_settings_collection():
    """获取用户设置集合"""
    db = get_db()
    return db["user_settings"]


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

@settings_bp.route('', methods=['GET'])
@jwt_required_custom()
def get_settings():
    """
    获取用户设置

    Query参数:
        无

    返回:
        {
            "success": true,
            "data": {
                "user_id": str,
                "theme": str,  # "light" | "dark" | "system"
                "language": str,  # "zh-CN" | "en-US"
                "api_config": {
                    "provider": str,
                    "model": str,
                    "temperature": float,
                    "max_tokens": int,
                    "api_key_preview": str  # 只返回部分密钥
                },
                "notification_enabled": bool,
                "email_subscription": bool,
                "created_at": str,  # ISO 8601格式
                "updated_at": str   # ISO 8601格式
            }
        }
    """
    try:
        # 获取当前用户ID
        user_id = get_current_user_id()

        # 从数据库获取用户设置
        settings_collection = get_user_settings_collection()
        settings_doc = settings_collection.find_one({"user_id": user_id})

        if not settings_doc:
            # 如果设置不存在，创建默认设置
            user_settings = UserSettings(user_id=user_id)
            settings_dict = user_settings.to_db_dict()
            settings_dict["created_at"] = datetime.utcnow()
            settings_dict["updated_at"] = datetime.utcnow()

            # 插入数据库
            result = settings_collection.insert_one(settings_dict)
            settings_dict["id"] = str(result.inserted_id)
            settings_dict.pop("_id", None)

            # 序列化并返回（不包含API密钥）
            return jsonify({
                "success": True,
                "data": user_settings.to_dict(include_api_key=False)
            }), 200

        # 序列化现有设置
        settings_dict = serialize_mongo_doc(settings_doc)

        # 转换为UserSettings对象并返回（不包含API密钥）
        user_settings = UserSettings.from_dict(settings_dict)
        return jsonify({
            "success": True,
            "data": user_settings.to_dict(include_api_key=False)
        }), 200

    except Exception as e:
        return handle_error(f"获取用户设置失败: {str(e)}", 500)


@settings_bp.route('', methods=['PUT'])
@jwt_required_custom()
def update_settings():
    """
    更新用户设置

    请求体:
        {
            "theme"?: str,  # "light" | "dark" | "system"
            "language"?: str,  # "zh-CN" | "en-US"
            "api_config"?: {
                "provider"?: str,
                "api_key"?: str,
                "model"?: str,
                "temperature"?: float,
                "max_tokens"?: int
            },
            "notification_enabled"?: bool,
            "email_subscription"?: bool
        }

    返回:
        {
            "success": true,
            "data": {
                "user_id": str,
                "theme": str,
                "language": str,
                "api_config": {...},
                "notification_enabled": bool,
                "email_subscription": bool,
                "created_at": str,
                "updated_at": str
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

        # 从数据库获取现有设置
        settings_collection = get_user_settings_collection()
        settings_doc = settings_collection.find_one({"user_id": user_id})

        if settings_doc:
            # 更新现有设置
            settings_dict = serialize_mongo_doc(settings_doc)
            user_settings = UserSettings.from_dict(settings_dict)

            # 更新主题
            if "theme" in data:
                if data["theme"] not in [Theme.LIGHT, Theme.DARK, Theme.SYSTEM]:
                    return handle_error(f"无效的主题: {data['theme']}")
                user_settings.update_theme(data["theme"])

            # 更新语言
            if "language" in data:
                if data["language"] not in [Language.ZH_CN, Language.EN_US]:
                    return handle_error(f"无效的语言: {data['language']}")
                user_settings.update_language(data["language"])

            # 更新API配置
            if "api_config" in data:
                api_config_data = data["api_config"]
                api_config = ApiConfig.from_dict(api_config_data)
                user_settings.update_api_config(api_config)

            # 更新通知设置
            if "notification_enabled" in data:
                user_settings.notification_enabled = data["notification_enabled"]

            # 更新邮件订阅
            if "email_subscription" in data:
                user_settings.email_subscription = data["email_subscription"]

            # 更新时间戳
            user_settings.updated_at = datetime.utcnow()

            # 转换为数据库格式
            updated_dict = user_settings.to_db_dict()
            updated_dict["updated_at"] = datetime.utcnow()

            # 更新数据库
            settings_collection.update_one(
                {"user_id": user_id},
                {"$set": updated_dict}
            )

            return jsonify({
                "success": True,
                "data": user_settings.to_dict(include_api_key=False)
            }), 200

        else:
            # 创建新设置
            theme = data.get("theme", Theme.SYSTEM)
            language = data.get("language", Language.ZH_CN)

            if theme not in [Theme.LIGHT, Theme.DARK, Theme.SYSTEM]:
                return handle_error(f"无效的主题: {theme}")

            if language not in [Language.ZH_CN, Language.EN_US]:
                return handle_error(f"无效的语言: {language}")

            # 创建API配置
            api_config = None
            if "api_config" in data:
                api_config = ApiConfig.from_dict(data["api_config"])

            user_settings = UserSettings(
                user_id=user_id,
                theme=theme,
                language=language,
                api_config=api_config,
                notification_enabled=data.get("notification_enabled", True),
                email_subscription=data.get("email_subscription", False)
            )

            # 转换为数据库格式
            settings_dict = user_settings.to_db_dict()
            settings_dict["created_at"] = datetime.utcnow()
            settings_dict["updated_at"] = datetime.utcnow()

            # 插入数据库
            result = settings_collection.insert_one(settings_dict)

            return jsonify({
                "success": True,
                "data": user_settings.to_dict(include_api_key=False)
            }), 201

    except Exception as e:
        return handle_error(f"更新用户设置失败: {str(e)}", 500)


@settings_bp.route('/api-config', methods=['POST'])
@jwt_required_custom()
def save_api_config():
    """
    保存API配置（加密存储）

    请求体:
        {
            "provider": str,  # "zhipu" | "openai"
            "api_key": str,
            "model": str,
            "temperature"?: float,  # 默认0.7
            "max_tokens"?: int  # 默认2000
        }

    返回:
        {
            "success": true,
            "data": {
                "api_config": {
                    "provider": str,
                    "model": str,
                    "temperature": float,
                    "max_tokens": int,
                    "api_key_preview": str  # 只返回部分密钥用于显示
                }
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
        if "api_key" not in data or not data["api_key"]:
            return handle_error("api_key是必填字段")

        # 创建API配置
        api_config = ApiConfig(
            provider=data.get("provider", "zhipu"),
            api_key=data["api_key"],
            model=data.get("model", "glm-4-flash"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens", 2000)
        )

        # 从数据库获取现有设置
        settings_collection = get_user_settings_collection()
        settings_doc = settings_collection.find_one({"user_id": user_id})

        if settings_doc:
            # 更新现有设置的API配置
            settings_dict = serialize_mongo_doc(settings_doc)
            user_settings = UserSettings.from_dict(settings_dict)
            user_settings.update_api_config(api_config)
            user_settings.updated_at = datetime.utcnow()

            # 转换为数据库格式（包含加密的API密钥）
            updated_dict = user_settings.to_db_dict()
            updated_dict["updated_at"] = datetime.utcnow()

            # 更新数据库
            settings_collection.update_one(
                {"user_id": user_id},
                {"$set": updated_dict}
            )

            return jsonify({
                "success": True,
                "data": {
                    "api_config": api_config.to_dict(include_key=True)
                }
            }), 200

        else:
            # 创建新设置（只包含API配置）
            user_settings = UserSettings(
                user_id=user_id,
                api_config=api_config
            )

            # 转换为数据库格式
            settings_dict = user_settings.to_db_dict()
            settings_dict["created_at"] = datetime.utcnow()
            settings_dict["updated_at"] = datetime.utcnow()

            # 插入数据库
            settings_collection.insert_one(settings_dict)

            return jsonify({
                "success": True,
                "data": {
                    "api_config": api_config.to_dict(include_key=True)
                }
            }), 201

    except Exception as e:
        return handle_error(f"保存API配置失败: {str(e)}", 500)


@settings_bp.route('/stats', methods=['GET'])
@jwt_required_custom()
def get_user_statistics():
    """
    获取使用统计

    Query参数:
        无

    返回:
        {
            "success": true,
            "data": {
                "papers_searched": int,
                "favorites_count": int,
                "projects_count": int,
                "ai_queries_count": int,
                "last_active": str  # ISO 8601格式
            }
        }
    """
    try:
        # 获取当前用户ID
        user_id = get_current_user_id()

        # 从数据库获取用户信息（包含统计）
        users_collection = get_user_collection()
        user_doc = users_collection.find_one(
            {"id": user_id},
            {"password_hash": 0}  # 不返回密码哈希
        )

        if not user_doc:
            return handle_error("用户不存在", 404)

        # 序列化用户文档
        user_dict = serialize_mongo_doc(user_doc)

        # 提取统计信息
        stats = user_dict.get("stats", {})

        # 返回统计数据
        return jsonify({
            "success": True,
            "data": {
                "papers_searched": stats.get("papers_searched", 0),
                "favorites_count": stats.get("favorites_count", 0),
                "projects_count": stats.get("projects_count", 0),
                "ai_queries_count": stats.get("ai_queries_count", 0),
                "last_active": user_dict.get("updated_at", datetime.utcnow().isoformat())
            }
        }), 200

    except Exception as e:
        return handle_error(f"获取用户统计失败: {str(e)}", 500)
