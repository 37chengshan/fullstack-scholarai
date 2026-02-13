"""
ScholarAI - 认证API路由

提供用户注册、登录、获取用户信息等认证相关的API端点。
"""

import re
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from functools import wraps

from models.user import User, UserRole
from middleware.auth import generate_token, get_current_user_id, jwt_required_custom
from config.database import get_collection

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# MongoDB集合
users_collection = None


def get_users_collection():
    """获取用户集合（延迟初始化）"""
    global users_collection
    if users_collection is None:
        users_collection = get_collection('users')
        # 创建email唯一索引
        users_collection.create_index('email', unique=True, sparse=True)
    return users_collection


def validate_email(email: str) -> bool:
    """
    验证邮箱格式

    参数:
        email: 邮箱地址

    返回:
        bool: 邮箱格式是否有效
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """
    验证密码强度

    参数:
        password: 密码

    返回:
        tuple[bool, str]: (是否有效, 错误消息)
    """
    if len(password) < 8:
        return False, "密码长度至少为8个字符"

    if not re.search(r'[A-Za-z]', password):
        return False, "密码必须包含字母"

    if not re.search(r'\d', password):
        return False, "密码必须包含数字"

    return True, ""


def serialize_user(user: User) -> dict:
    """
    序列化用户对象（排除敏感信息）

    参数:
        user: 用户实例

    返回:
        dict: 用户信息字典
    """
    return user.to_dict(include_sensitive=False)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册

    请求体:
        {
            "name": "用户名",
            "email": "user@example.com",
            "password": "password123"
        }

    响应:
        {
            "success": true,
            "data": {
                "user": {用户信息}
            }
        }
    """
    try:
        data = request.get_json()

        # 验证必填字段
        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400

        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        # 验证字段
        if not name:
            return jsonify({
                'success': False,
                'error': '用户名不能为空'
            }), 400

        if not email:
            return jsonify({
                'success': False,
                'error': '邮箱不能为空'
            }), 400

        if not validate_email(email):
            return jsonify({
                'success': False,
                'error': '邮箱格式不正确'
            }), 400

        if not password:
            return jsonify({
                'success': False,
                'error': '密码不能为空'
            }), 400

        # 验证密码强度
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400

        # 检查邮箱是否已存在
        collection = get_users_collection()
        existing_user = collection.find_one({'email': email})
        if existing_user:
            return jsonify({
                'success': False,
                'error': '该邮箱已被注册'
            }), 409

        # 创建新用户
        new_user = User(
            name=name,
            email=email,
            password=password
        )

        # 保存到数据库
        user_dict = new_user.to_dict(include_sensitive=True)
        user_dict['_id'] = user_dict.pop('id')  # 将id字段作为_id
        collection.insert_one(user_dict)

        # 返回用户信息（不包含敏感信息）
        return jsonify({
            'success': True,
            'data': {
                'user': serialize_user(new_user),
                'message': '注册成功'
            }
        }), 201

    except Exception as e:
        # 处理重复键错误（邮箱已存在）
        if 'duplicate key' in str(e):
            return jsonify({
                'success': False,
                'error': '该邮箱已被注册'
            }), 409

        return jsonify({
            'success': False,
            'error': f'注册失败: {str(e)}'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录

    请求体:
        {
            "email": "user@example.com",
            "password": "password123"
        }

    响应:
        {
            "success": true,
            "data": {
                "access_token": "JWT token",
                "token_type": "Bearer",
                "user": {用户信息}
            }
        }
    """
    try:
        data = request.get_json()

        # 验证必填字段
        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({
                'success': False,
                'error': '邮箱和密码不能为空'
            }), 400

        # 验证邮箱格式
        if not validate_email(email):
            return jsonify({
                'success': False,
                'error': '邮箱格式不正确'
            }), 400

        # 查找用户
        collection = get_users_collection()
        user_dict = collection.find_one({'email': email})

        if not user_dict:
            return jsonify({
                'success': False,
                'error': '邮箱或密码错误'
            }), 401

        # 验证密码
        user_dict['id'] = str(user_dict.pop('_id'))
        user = User.from_dict(user_dict)

        if not user.check_password(password):
            return jsonify({
                'success': False,
                'error': '邮箱或密码错误'
            }), 401

        # 检查账户是否激活
        if not user.is_active:
            return jsonify({
                'success': False,
                'error': '账户已被禁用'
            }), 403

        # 生成JWT token
        token = generate_token(
            user_id=user.id,
            additional_claims={
                'role': user.role,
                'email': user.email
            }
        )

        # 更新最后登录时间
        collection.update_one(
            {'_id': user_dict['_id']},
            {'$set': {'updated_at': datetime.utcnow().isoformat()}}
        )

        # 返回token和用户信息
        return jsonify({
            'success': True,
            'data': {
                'access_token': token,
                'token_type': 'Bearer',
                'user': serialize_user(user)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'登录失败: {str(e)}'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required_custom()
def get_current_user():
    """
    获取当前登录用户信息

    请求头:
        Authorization: Bearer <token>

    响应:
        {
            "success": true,
            "data": {
                "user": {用户信息}
            }
        }
    """
    try:
        # 从JWT token中获取用户ID
        user_id = get_current_user_id()

        if not user_id:
            return jsonify({
                'success': False,
                'error': '无法获取用户信息'
            }), 401

        # 查找用户
        collection = get_users_collection()
        user_dict = collection.find_one({'_id': user_id})

        if not user_dict:
            return jsonify({
                'success': False,
                'error': '用户不存在'
            }), 404

        # 转换为User对象
        user_dict['id'] = str(user_dict.pop('_id'))
        user = User.from_dict(user_dict)

        return jsonify({
            'success': True,
            'data': {
                'user': serialize_user(user)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取用户信息失败: {str(e)}'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required_custom()
def logout():
    """
    用户登出

    注意: JWT是无状态的，实际登出由前端删除token完成
    此端点主要用于记录登出日志或执行其他清理操作

    请求头:
        Authorization: Bearer <token>

    响应:
        {
            "success": true,
            "data": {
                "message": "登出成功"
            }
        }
    """
    try:
        # 获取用户ID（可选，用于记录日志）
        user_id = get_current_user_id()

        # 在实际应用中，这里可以：
        # 1. 将token加入黑名单（如果实现了黑名单机制）
        # 2. 记录登出日志
        # 3. 清除服务器端缓存
        # 4. 执行其他清理操作

        return jsonify({
            'success': True,
            'data': {
                'message': '登出成功'
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'登出失败: {str(e)}'
        }), 500


@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """
    验证JWT token是否有效

    请求头:
        Authorization: Bearer <token>

    响应:
        {
            "success": true,
            "data": {
                "valid": true,
                "user": {用户信息}
            }
        }
    """
    try:
        # 使用可选认证，如果token无效则返回valid=false
        from middleware.auth import verify_jwt_in_request
        from flask_jwt_extended import get_jwt_identity

        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()

        if not user_id:
            return jsonify({
                'success': True,
                'data': {
                    'valid': False,
                    'user': None
                }
            }), 200

        # 获取用户信息
        collection = get_users_collection()
        user_dict = collection.find_one({'_id': user_id})

        if not user_dict:
            return jsonify({
                'success': True,
                'data': {
                    'valid': False,
                    'user': None
                }
            }), 200

        user_dict['id'] = str(user_dict.pop('_id'))
        user = User.from_dict(user_dict)

        return jsonify({
            'success': True,
            'data': {
                'valid': True,
                'user': serialize_user(user)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': True,
            'data': {
                'valid': False,
                'user': None,
                'error': str(e)
            }
        }), 200


if __name__ == '__main__':
    print("认证路由模块")
    print("可用端点:")
    print("  POST /api/auth/register - 用户注册")
    print("  POST /api/auth/login - 用户登录")
    print("  GET  /api/auth/me - 获取当前用户")
    print("  POST /api/auth/logout - 用户登出")
    print("  POST /api/auth/verify-token - 验证Token")
