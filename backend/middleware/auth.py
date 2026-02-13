"""
ScholarAI - JWT认证中间件

提供JWT token生成、验证和用户认证功能。
"""

import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any, Callable

from flask import request, jsonify, g
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    verify_jwt_in_request
)
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# JWT配置
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))  # 默认1小时

# 全局JWT管理器实例（将在app/__init__.py中初始化）
jwt_manager = None


def init_jwt(app):
    """
    初始化JWT管理器

    参数:
        app: Flask应用实例

    返回:
        JWTManager: JWT管理器实例
    """
    global jwt_manager

    # 配置JWT
    app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRES)
    app.config['JWT_ERROR_MESSAGES'] = {
        'expired': "Token已过期，请重新登录",
        'invalid': "无效的Token",
        'missing': "缺少Token，请先登录"
    }

    jwt_manager = JWTManager(app)

    # JWT错误处理
    @jwt_manager.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Token过期回调"""
        return jsonify({
            'success': False,
            'error': 'Token已过期，请重新登录'
        }), 401

    @jwt_manager.invalid_token_loader
    def invalid_token_callback(error):
        """无效Token回调"""
        return jsonify({
            'success': False,
            'error': '无效的Token'
        }), 401

    @jwt_manager.unauthorized_loader
    def missing_token_callback(error):
        """缺少Token回调"""
        return jsonify({
            'success': False,
            'error': '缺少Token，请先登录'
        }), 401

    return jwt_manager


def generate_token(user_id: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
    """
    生成JWT access token

    参数:
        user_id: 用户ID
        additional_claims: 额外的声明信息（可选）

    返回:
        str: JWT access token

    示例:
        >>> token = generate_token("user-123", {"role": "admin"})
    """
    claims = {}
    if additional_claims:
        claims.update(additional_claims)

    token = create_access_token(
        identity=user_id,
        additional_claims=claims or None
    )
    return token


def get_current_user_id() -> Optional[str]:
    """
    从JWT token中获取当前用户ID

    返回:
        Optional[str]: 用户ID，如果未认证则返回None

    注意:
        此函数需要在jwt_required装饰器保护的路由中使用
    """
    try:
        return get_jwt_identity()
    except Exception:
        return None


def jwt_required_custom(optional: bool = False) -> Callable:
    """
    JWT认证装饰器（自定义版本）

    参数:
        optional: 是否可选认证（默认False）

    使用示例:
        >>> @app.route('/protected')
        >>> @jwt_required_custom()
        >>> def protected_route():
        >>>     user_id = get_current_user_id()
        >>>     return jsonify({'user_id': user_id})
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                if optional:
                    # 可选认证：尝试获取用户ID
                    try:
                        verify_jwt_in_request(optional=True)
                        g.user_id = get_jwt_identity()
                    except Exception:
                        g.user_id = None
                else:
                    # 必须认证
                    verify_jwt_in_request()
                    g.user_id = get_jwt_identity()

                return fn(*args, **kwargs)

            except Exception as e:
                # 处理所有认证错误
                return jsonify({
                    'success': False,
                    'error': str(e) or '认证失败'
                }), 401

        return wrapper
    return decorator


def get_user_from_token() -> Optional[str]:
    """
    从请求头中获取用户ID（不强制要求认证）

    返回:
        Optional[str]: 用户ID，如果Token无效或不存在则返回None

    注意:
        此函数用于可选认证的路由，不会抛出异常
    """
    try:
        verify_jwt_in_request(optional=True)
        return get_jwt_identity()
    except Exception:
        return None


# 便捷函数别名
jwt_required = jwt_required_custom
get_current_user = get_current_user_id


if __name__ == '__main__':
    # 测试代码
    print("JWT中间件模块")
    print(f"SECRET_KEY: {JWT_SECRET_KEY[:10]}...")
    print(f"TOKEN_EXPIRES: {JWT_ACCESS_TOKEN_EXPIRES}秒")
