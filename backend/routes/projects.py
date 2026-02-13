"""
ScholarAI - 项目管理API路由

提供项目创建、读取、更新、删除等API端点。
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, g
from models.project import Project, ProjectPaper, ProjectProgress
from middleware.auth import get_current_user_id, jwt_required_custom
from config.database import get_collection

# 创建项目蓝图
projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')

# MongoDB集合
projects_collection = None


def get_projects_collection():
    """获取项目集合（延迟初始化）"""
    global projects_collection
    if projects_collection is None:
        projects_collection = get_collection('projects')
        # 创建复合索引：用户ID + 项目名称（同一用户下项目名唯一）
        projects_collection.create_index([('created_by', 1), ('name', 1)], unique=True)
        # 创建创建时间索引（用于排序）
        projects_collection.create_index('created_at', -1)
    return projects_collection


def serialize_project(project: Project, include_papers: bool = False) -> dict:
    """
    序列化项目对象

    参数:
        project: 项目实例
        include_papers: 是否包含论文列表

    返回:
        dict: 项目信息字典
    """
    return project.to_dict(include_papers=include_papers)


def project_to_document(project: Project) -> dict:
    """
    将项目对象转换为MongoDB文档

    参数:
        project: 项目实例

    返回:
        dict: MongoDB文档
    """
    return project.to_dict(include_papers=True)


def document_to_project(doc: dict) -> Project:
    """
    将MongoDB文档转换为项目对象

    参数:
        doc: MongoDB文档

    返回:
        Project: 项目实例
    """
    return Project.from_dict(doc)


@projects_bp.route('', methods=['GET'])
@jwt_required_custom()
def get_projects():
    """
    获取用户所有项目

    查询参数:
        sort_by: 排序字段（created_at, updated_at, name）
        order: 排序方向（asc, desc）
        tags: 过滤标签（逗号分隔）
        is_public: 是否只看公开项目（true/false）

    响应:
        {
            "success": true,
            "data": {
                "projects": [...]
            }
        }
    """
    try:
        user_id = get_current_user_id()
        collection = get_projects_collection()

        # 获取查询参数
        sort_by = request.args.get('sort_by', 'updated_at')
        order = request.args.get('order', 'desc')
        tags_filter = request.args.get('tags')
        is_public_filter = request.args.get('is_public')

        # 构建查询条件
        query = {'created_by': user_id}

        # 公开项目过滤
        if is_public_filter is not None:
            query['is_public'] = is_public_filter.lower() == 'true'

        # 标签过滤
        if tags_filter:
            tags_list = [tag.strip() for tag in tags_filter.split(',')]
            query['tags'] = {'$in': tags_list}

        # 排序
        sort_order = 1 if order == 'asc' else -1
        sort_field = sort_by if sort_by in ['created_at', 'updated_at', 'name'] else 'updated_at'

        # 查询项目
        docs = collection.find(query).sort(sort_field, sort_order)
        projects = [document_to_project(doc) for doc in docs]

        return jsonify({
            'success': True,
            'data': {
                'projects': [serialize_project(p, include_papers=False) for p in projects]
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取项目列表失败: {str(e)}'
        }), 500


@projects_bp.route('', methods=['POST'])
@jwt_required_custom()
def create_project():
    """
    创建新项目

    请求体:
        {
            "name": "项目名称",
            "color": "#3B82F6",  // 可选
            "description": "项目描述",  // 可选
            "tags": ["标签1", "标签2"]  // 可选
        }

    响应:
        {
            "success": true,
            "data": {
                "project": {项目信息}
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
                'error': '项目名称不能为空'
            }), 400

        name = data['name'].strip()
        if len(name) > 100:
            return jsonify({
                'success': False,
                'error': '项目名称不能超过100个字符'
            }), 400

        color = data.get('color')
        if color and color.startswith('#'):
            # 简单验证十六进制颜色
            if len(color) != 7 or not all(c in '01234567899ABCDEFabcdef#' for c in color):
                return jsonify({
                    'success': False,
                    'error': '无效的颜色代码'
                }), 400

        # 创建项目
        project = Project(
            name=name,
            created_by=user_id,
            color=color,
            description=data.get('description', ''),
            tags=data.get('tags', [])
        )

        # 保存到数据库
        collection = get_projects_collection()
        doc = project_to_document(project)
        doc['_id'] = project.id
        collection.insert_one(doc)

        return jsonify({
            'success': True,
            'data': {
                'project': serialize_project(project, include_papers=False)
            }
        }), 201

    except Exception as e:
        # 检查是否是重复键错误
        if 'duplicate key' in str(e):
            return jsonify({
                'success': False,
                'error': '项目名称已存在'
            }), 409

        return jsonify({
            'success': False,
            'error': f'创建项目失败: {str(e)}'
        }), 500


@projects_bp.route('/<project_id>', methods=['GET'])
@jwt_required_custom()
def get_project(project_id: str):
    """
    获取项目详情

    参数:
        project_id: 项目ID

    响应:
        {
            "success": true,
            "data": {
                "project": {项目详情}
            }
        }
    """
    try:
        user_id = get_current_user_id()
        collection = get_projects_collection()

        doc = collection.find_one({'_id': project_id})
        if not doc:
            return jsonify({
                'success': False,
                'error': '项目不存在'
            }), 404

        project = document_to_project(doc)

        # 验证权限
        if project.created_by != user_id and not project.is_public:
            return jsonify({
                'success': False,
                'error': '无权访问此项目'
            }), 403

        return jsonify({
            'success': True,
            'data': {
                'project': serialize_project(project, include_papers=True)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取项目详情失败: {str(e)}'
        }), 500


@projects_bp.route('/<project_id>', methods=['PUT'])
@jwt_required_custom()
def update_project(project_id: str):
    """
    更新项目

    参数:
        project_id: 项目ID

    请求体:
        {
            "name": "新项目名称",  // 可选
            "color": "#EF4444",  // 可选
            "description": "新描述",  // 可选
            "tags": ["新标签"]  // 可选
        }

    响应:
        {
            "success": true,
            "data": {
                "project": {更新后的项目信息}
            }
        }
    """
    try:
        user_id = get_current_user_id()
        collection = get_projects_collection()

        doc = collection.find_one({'_id': project_id})
        if not doc:
            return jsonify({
                'success': False,
                'error': '项目不存在'
            }), 404

        project = document_to_project(doc)

        # 验证权限
        if project.created_by != user_id:
            return jsonify({
                'success': False,
                'error': '无权修改此项目'
            }), 403

        # 获取更新数据
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请提供要更新的字段'
            }), 400

        # 更新字段
        update_data = {}
        if 'name' in data:
            name = data['name'].strip()
            if len(name) == 0:
                return jsonify({
                    'success': False,
                    'error': '项目名称不能为空'
                }), 400
            if len(name) > 100:
                return jsonify({
                    'success': False,
                    'error': '项目名称不能超过100个字符'
                }), 400
            update_data['name'] = name

        if 'color' in data:
            color = data['color']
            if color and not (color.startswith('#') and len(color) == 7):
                return jsonify({
                    'success': False,
                    'error': '无效的颜色代码'
                }), 400
            update_data['color'] = color

        if 'description' in data:
            update_data['description'] = data['description']

        if 'tags' in data:
            if not isinstance(data['tags'], list):
                return jsonify({
                    'success': False,
                    'error': 'tags必须是数组'
                }), 400
            update_data['tags'] = data['tags']

        if 'is_public' in data:
            if not isinstance(data['is_public'], bool):
                return jsonify({
                    'success': False,
                    'error': 'is_public必须是布尔值'
                }), 400
            update_data['is_public'] = data['is_public']

        # 更新项目对象
        project.update(**update_data)
        project.updated_at = datetime.utcnow()

        # 保存到数据库
        doc = project_to_document(project)
        collection.update_one(
            {'_id': project_id},
            {'$set': doc}
        )

        return jsonify({
            'success': True,
            'data': {
                'project': serialize_project(project, include_papers=False)
            }
        }), 200

    except Exception as e:
        if 'duplicate key' in str(e):
            return jsonify({
                'success': False,
                'error': '项目名称已存在'
            }), 409

        return jsonify({
            'success': False,
            'error': f'更新项目失败: {str(e)}'
        }), 500


@projects_bp.route('/<project_id>', methods=['DELETE'])
@jwt_required_custom()
def delete_project(project_id: str):
    """
    删除项目

    参数:
        project_id: 项目ID

    响应:
        {
            "success": true,
            "data": {
                "message": "项目已删除"
            }
        }
    """
    try:
        user_id = get_current_user_id()
        collection = get_projects_collection()

        doc = collection.find_one({'_id': project_id})
        if not doc:
            return jsonify({
                'success': False,
                'error': '项目不存在'
            }), 404

        project = document_to_project(doc)

        # 验证权限
        if project.created_by != user_id:
            return jsonify({
                'success': False,
                'error': '无权删除此项目'
            }), 403

        # 删除项目
        collection.delete_one({'_id': project_id})

        return jsonify({
            'success': True,
            'data': {
                'message': '项目已删除'
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'删除项目失败: {str(e)}'
        }), 500


@projects_bp.route('/<project_id>/papers', methods=['POST'])
@jwt_required_custom()
def add_paper_to_project(project_id: str):
    """
    添加论文到项目

    参数:
        project_id: 项目ID

    请求体:
        {
            "paper_id": "2301.00001",
            "title": "论文标题",
            "authors": ["作者1", "作者2"],
            "status": "to_read"  // 可选: to_read, in_progress, completed
        }

    响应:
        {
            "success": true,
            "data": {
                "project": {项目信息}
            }
        }
    """
    try:
        user_id = get_current_user_id()
        collection = get_projects_collection()

        doc = collection.find_one({'_id': project_id})
        if not doc:
            return jsonify({
                'success': False,
                'error': '项目不存在'
            }), 404

        project = document_to_project(doc)

        # 验证权限
        if project.created_by != user_id:
            return jsonify({
                'success': False,
                'error': '无权修改此项目'
            }), 403

        # 获取论文数据
        data = request.get_json()
        if not data or not data.get('paper_id') or not data.get('title'):
            return jsonify({
                'success': False,
                'error': '论文ID和标题为必填字段'
            }), 400

        # 添加论文
        project.add_paper(
            paper_id=data['paper_id'],
            title=data['title'],
            authors=data.get('authors', []),
            status=data.get('status', 'to_read')
        )

        # 保存到数据库
        doc = project_to_document(project)
        collection.update_one(
            {'_id': project_id},
            {'$set': doc}
        )

        return jsonify({
            'success': True,
            'data': {
                'project': serialize_project(project, include_papers=False)
            }
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'添加论文失败: {str(e)}'
        }), 500


@projects_bp.route('/<project_id>/papers/<paper_id>', methods=['DELETE'])
@jwt_required_custom()
def remove_paper_from_project(project_id: str, paper_id: str):
    """
    从项目移除论文

    参数:
        project_id: 项目ID
        paper_id: 论文ID

    响应:
        {
            "success": true,
            "data": {
                "message": "论文已移除"
            }
        }
    """
    try:
        user_id = get_current_user_id()
        collection = get_projects_collection()

        doc = collection.find_one({'_id': project_id})
        if not doc:
            return jsonify({
                'success': False,
                'error': '项目不存在'
            }), 404

        project = document_to_project(doc)

        # 验证权限
        if project.created_by != user_id:
            return jsonify({
                'success': False,
                'error': '无权修改此项目'
            }), 403

        # 移除论文
        if not project.remove_paper(paper_id):
            return jsonify({
                'success': False,
                'error': '论文不存在于项目中'
            }), 404

        # 保存到数据库
        doc = project_to_document(project)
        collection.update_one(
            {'_id': project_id},
            {'$set': doc}
        )

        return jsonify({
            'success': True,
            'data': {
                'message': '论文已移除'
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'移除论文失败: {str(e)}'
        }), 500


@projects_bp.route('/<project_id>/papers/<paper_id>/status', methods=['PUT'])
@jwt_required_custom()
def update_paper_status(project_id: str, paper_id: str):
    """
    更新项目中的论文状态

    参数:
        project_id: 项目ID
        paper_id: 论文ID

    请求体:
        {
            "status": "in_progress"  // to_read, in_progress, completed
        }

    响应:
        {
            "success": true,
            "data": {
                "project": {项目信息}
            }
        }
    """
    try:
        user_id = get_current_user_id()
        collection = get_projects_collection()

        doc = collection.find_one({'_id': project_id})
        if not doc:
            return jsonify({
                'success': False,
                'error': '项目不存在'
            }), 404

        project = document_to_project(doc)

        # 验证权限
        if project.created_by != user_id:
            return jsonify({
                'success': False,
                'error': '无权修改此项目'
            }), 403

        # 获取状态
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'error': 'status字段为必填项'
            }), 400

        status = data['status']
        if status not in ['to_read', 'in_progress', 'completed']:
            return jsonify({
                'success': False,
                'error': '无效的状态值'
            }), 400

        # 更新状态
        if not project.update_paper_status(paper_id, status):
            return jsonify({
                'success': False,
                'error': '论文不存在于项目中'
            }), 404

        # 保存到数据库
        doc = project_to_document(project)
        collection.update_one(
            {'_id': project_id},
            {'$set': doc}
        )

        return jsonify({
            'success': True,
            'data': {
                'project': serialize_project(project, include_papers=False)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'更新论文状态失败: {str(e)}'
        }), 500
