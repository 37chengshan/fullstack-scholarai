"""
ScholarAI - 收藏夹管理API路由

提供收藏夹、文件夹管理API端点。
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, g
from models.favorites import Favorite, Folder
from middleware.auth import get_current_user_id, jwt_required_custom
from config.database import get_collection

# 创建收藏夹蓝图
favorites_bp = Blueprint('favorites', __name__, url_prefix='/api/favorites')

# MongoDB集合
favorites_collection = None
folders_collection = None


def get_favorites_collection():
    """获取收藏集合（延迟初始化）"""
    global favorites_collection
    if favorites_collection is None:
        favorites_collection = get_collection('favorites')
        # 创建复合索引：用户ID + 论文ID（同一用户对同一论文只能收藏一次）
        favorites_collection.create_index([('user_id', 1), ('paper_id', 1)], unique=True)
        # 创建用户ID + 文件夹ID索引（用于获取文件夹下的收藏）
        favorites_collection.create_index([('user_id', 1), ('folder_id', 1)])
        # 创建用户ID索引（用于获取用户所有收藏）
        favorites_collection.create_index('user_id', 1)
        # 创建添加时间索引（用于排序）
        favorites_collection.create_index('created_at', -1)
    return favorites_collection


def get_folders_collection():
    """获取文件夹集合（延迟初始化）"""
    global folders_collection
    if folders_collection is None:
        folders_collection = get_collection('folders')
        # 创建复合索引：用户ID + 文件夹名称（同一用户下文件夹名唯一）
        folders_collection.create_index([('created_by', 1), ('name', 1)], unique=True)
        # 创建创建时间索引（用于排序）
        folders_collection.create_index('created_at', -1)
    return folders_collection


def serialize_favorite(favorite: Favorite) -> dict:
    """
    序列化收藏项对象

    参数:
        favorite: 收藏项实例

    返回:
        dict: 收藏项信息字典
    """
    return favorite.to_dict()


def favorite_to_document(favorite: Favorite) -> dict:
    """
    将收藏项对象转换为MongoDB文档

    参数:
        favorite: 收藏项实例

    返回:
        dict: MongoDB文档
    """
    return favorite.to_dict()


def document_to_favorite(doc: dict) -> Favorite:
    """
    将MongoDB文档转换为收藏项对象

    参数:
        doc: MongoDB文档

    返回:
        Favorite: 收藏项实例
    """
    return Favorite.from_dict(doc)


def serialize_folder(folder: Folder) -> dict:
    """
    序列化文件夹对象

    参数:
        folder: 文件夹实例

    返回:
        dict: 文件夹信息字典
    """
    return folder.to_dict()


def folder_to_document(folder: Folder) -> dict:
    """
    将文件夹对象转换为MongoDB文档

    参数:
        folder: 文件夹实例

    返回:
        dict: MongoDB文档
    """
    return folder.to_dict()


def document_to_folder(doc: dict) -> Folder:
    """
    将MongoDB文档转换为文件夹对象

    参数:
        doc: MongoDB文档

    返回:
        Folder: 文件夹实例
    """
    return Folder.from_dict(doc)


# ==================== 收藏项端点 ====================

@favorites_bp.route('', methods=['GET'])
@jwt_required_custom
def get_favorites():
    """
    获取用户收藏列表

    查询参数:
        folder_id: 文件夹ID（可选，不传则获取所有收藏）
        sort_by: 排序字段（created_at, title）
        order: 排序方向（asc, desc）

    响应:
        {
            "success": true,
            "data": {
                "favorites": [...]
            }
        }
    """
    try:
        user_id = get_current_user_id()
        collection = get_favorites_collection()

        # 获取查询参数
        folder_id = request.args.get('folder_id')
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc')

        # 构建查询条件
        query = {'user_id': user_id}

        # 文件夹过滤
        if folder_id:
            query['folder_id'] = folder_id
        else:
            # 如果folder_id为空字符串，查询未分类的收藏
            if folder_id == '':
                query['folder_id'] = None

        # 排序
        sort_order = 1 if order == 'asc' else -1
        sort_field = sort_by if sort_by in ['created_at', 'title'] else 'created_at'

        # 查询收藏
        docs = collection.find(query).sort(sort_field, sort_order)
        favorites = [document_to_favorite(doc) for doc in docs]

        return jsonify({
            'success': True,
            'data': {
                'favorites': [serialize_favorite(f) for f in favorites]
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取收藏列表失败: {str(e)}'
        }), 500


@favorites_bp.route('/toggle', methods=['POST'])
@jwt_required_custom
def toggle_favorite():
    """
    切换收藏状态（添加或移除）

    请求体:
        {
            "paper_id": "2301.00001",
            "folder_id": "folder-uuid"  // 可选，不传则不分类
        }

    响应:
        {
            "success": true,
            "data": {
                "is_favorited": true,
                "favorite": {...}  // 如果是添加操作
            }
        }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        # 验证必填字段
        if not data or not data.get('paper_id'):
            return jsonify({
                'success': False,
                'error': '缺少必填字段: paper_id'
            }), 400

        paper_id = data['paper_id'].strip()
        folder_id = data.get('folder_id')

        # 从arXiv获取论文基本信息（用于冗余存储）
        from services.arxiv_client import get_arxiv_client
        arxiv_client = get_arxiv_client()

        try:
            paper_data = arxiv_client.get_paper_details(paper_id)
            if not paper_data.get('success'):
                return jsonify({
                    'success': False,
                    'error': f'获取论文信息失败: {paper_data.get("error", "未知错误")}'
                }), 404

            paper_info = paper_data['data']
            title = paper_info.get('title', 'Unknown')
            authors = [a.get('name', '') for a in paper_info.get('authors', [])]
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'获取论文信息失败: {str(e)}'
            }), 404

        collection = get_favorites_collection()

        # 检查是否已收藏
        existing = collection.find_one({'user_id': user_id, 'paper_id': paper_id})

        if existing:
            # 已收藏，移除收藏
            collection.delete_one({'user_id': user_id, 'paper_id': paper_id})
            return jsonify({
                'success': True,
                'data': {
                    'is_favorited': False,
                    'message': '已移除收藏'
                }
            }), 200
        else:
            # 未收藏，添加收藏
            favorite = Favorite(
                user_id=user_id,
                paper_id=paper_id,
                title=title,
                authors=authors,
                folder_id=folder_id
            )

            collection.insert_one(favorite_to_document(favorite))

            return jsonify({
                'success': True,
                'data': {
                    'is_favorited': True,
                    'favorite': serialize_favorite(favorite),
                    'message': '已添加到收藏'
                }
            }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'切换收藏状态失败: {str(e)}'
        }), 500


@favorites_bp.route('/<favorite_id>', methods=['DELETE'])
@jwt_required_custom
def delete_favorite(favorite_id: str):
    """
    移除收藏

    参数:
        favorite_id: 收藏项ID

    响应:
        {
            "success": true,
            "data": {
                "message": "收藏已移除"
            }
        }
    """
    try:
        user_id = get_current_user_id()
        collection = get_favorites_collection()

        # 删除收藏（用户只能删除自己的收藏）
        result = collection.delete_one({'id': favorite_id, 'user_id': user_id})

        if result.deleted_count > 0:
            return jsonify({
                'success': True,
                'data': {
                    'message': '收藏已移除'
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '收藏项不存在或无权删除'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'移除收藏失败: {str(e)}'
        }), 500


@favorites_bp.route('/<favorite_id>', methods=['PUT'])
@jwt_required_custom
def update_favorite(favorite_id: str):
    """
    更新收藏项（移动文件夹、添加笔记、更新标签）

    请求体:
        {
            "folder_id": "new-folder-id",  // 可选
            "notes": "笔记内容",  // 可选
            "tags": ["标签1", "标签2"]  // 可选
        }

    响应:
        {
            "success": true,
            "data": {
                "favorite": {...}
            }
        }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400

        collection = get_favorites_collection()

        # 查询收藏项
        doc = collection.find_one({'id': favorite_id, 'user_id': user_id})
        if not doc:
            return jsonify({
                'success': False,
                'error': '收藏项不存在或无权修改'
            }), 404

        favorite = document_to_favorite(doc)

        # 更新字段
        favorite.update(**data)

        # 保存到数据库
        collection.update_one(
            {'id': favorite_id},
            {'$set': favorite_to_document(favorite)}
        )

        return jsonify({
            'success': True,
            'data': {
                'favorite': serialize_favorite(favorite)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'更新收藏项失败: {str(e)}'
        }), 500


# ==================== 文件夹端点 ====================

@favorites_bp.route('/folders', methods=['GET'])
@jwt_required_custom
def get_folders():
    """
    获取用户文件夹列表

    响应:
        {
            "success": true,
            "data": {
                "folders": [...]
            }
        }
    """
    try:
        user_id = get_current_user_id()
        collection = get_folders_collection()

        # 查询用户的所有文件夹（按创建时间倒序）
        docs = collection.find({'created_by': user_id}).sort('created_at', -1)
        folders = [document_to_folder(doc) for doc in docs]

        return jsonify({
            'success': True,
            'data': {
                'folders': [serialize_folder(f) for f in folders]
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取文件夹列表失败: {str(e)}'
        }), 500


@favorites_bp.route('/folders', methods=['POST'])
@jwt_required_custom
def create_folder():
    """
    创建文件夹

    请求体:
        {
            "name": "文件夹名称",
            "color": "#3B82F6"  // 可选
        }

    响应:
        {
            "success": true,
            "data": {
                "folder": {...}
            }
        }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        # 验证必填字段
        if not data or not data.get('name'):
            return jsonify({
                'success': False,
                'error': '缺少必填字段: name'
            }), 400

        name = data['name'].strip()
        color = data.get('color')

        collection = get_folders_collection()

        # 检查文件夹名是否已存在
        existing = collection.find_one({'created_by': user_id, 'name': name})
        if existing:
            return jsonify({
                'success': False,
                'error': '文件夹名已存在'
            }), 409

        # 创建文件夹
        folder = Folder(name=name, created_by=user_id, color=color)

        collection.insert_one(folder_to_document(folder))

        return jsonify({
            'success': True,
            'data': {
                'folder': serialize_folder(folder)
            }
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'创建文件夹失败: {str(e)}'
        }), 500


@favorites_bp.route('/folders/<folder_id>', methods=['PUT'])
@jwt_required_custom
def update_folder(folder_id: str):
    """
    更新文件夹

    请求体:
        {
            "name": "新名称",  // 可选
            "color": "#EF4444"  // 可选
        }

    响应:
        {
            "success": true,
            "data": {
                "folder": {...}
            }
        }
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400

        collection = get_folders_collection()

        # 查询文件夹
        doc = collection.find_one({'id': folder_id, 'created_by': user_id})
        if not doc:
            return jsonify({
                'success': False,
                'error': '文件夹不存在或无权修改'
            }), 404

        folder = document_to_folder(doc)

        # 如果要更新名称，检查新名称是否已存在
        if 'name' in data and data['name'].strip() != folder.name:
            existing = collection.find_one({
                'created_by': user_id,
                'name': data['name'].strip(),
                'id': {'$ne': folder_id}
            })
            if existing:
                return jsonify({
                    'success': False,
                    'error': '文件夹名已存在'
                }), 409

        # 更新字段
        folder.update(**data)

        # 保存到数据库
        collection.update_one(
            {'id': folder_id},
            {'$set': folder_to_document(folder)}
        )

        return jsonify({
            'success': True,
            'data': {
                'folder': serialize_folder(folder)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'更新文件夹失败: {str(e)}'
        }), 500


@favorites_bp.route('/folders/<folder_id>', methods=['DELETE'])
@jwt_required_custom
def delete_folder(folder_id: str):
    """
    删除文件夹（及其下的所有收藏项）

    参数:
        folder_id: 文件夹ID

    响应:
        {
            "success": true,
            "data": {
                "message": "文件夹已删除"
            }
        }
    """
    try:
        user_id = get_current_user_id()
        folders_collection = get_folders_collection()
        favorites_collection = get_favorites_collection()

        # 查询文件夹
        doc = folders_collection.find_one({'id': folder_id, 'created_by': user_id})
        if not doc:
            return jsonify({
                'success': False,
                'error': '文件夹不存在或无权删除'
            }), 404

        # 删除文件夹
        folders_collection.delete_one({'id': folder_id, 'created_by': user_id})

        # 删除该文件夹下的所有收藏项（或者将它们的folder_id设为None）
        favorites_collection.update_many(
            {'user_id': user_id, 'folder_id': folder_id},
            {'$set': {'folder_id': None}}
        )

        return jsonify({
            'success': True,
            'data': {
                'message': '文件夹已删除，相关收藏已移至未分类'
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'删除文件夹失败: {str(e)}'
        }), 500
