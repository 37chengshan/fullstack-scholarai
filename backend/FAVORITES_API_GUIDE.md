# 收藏夹API指南

## API端点总览

### 收藏项端点

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/api/favorites` | GET | 获取用户收藏列表 | ✅ |
| `/api/favorites/toggle` | POST | 切换收藏状态 | ✅ |
| `/api/favorites/<favorite_id>` | PUT | 更新收藏项 | ✅ |
| `/api/favorites/<favorite_id>` | DELETE | 删除收藏项 | ✅ |

### 文件夹端点

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/api/favorites/folders` | GET | 获取用户文件夹列表 | ✅ |
| `/api/favorites/folders` | POST | 创建文件夹 | ✅ |
| `/api/favorites/folders/<folder_id>` | PUT | 更新文件夹 | ✅ |
| `/api/favorites/folders/<folder_id>` | DELETE | 删除文件夹 | ✅ |

---

## API使用示例

### 1. 获取收藏列表

```bash
curl -X GET "http://localhost:5000/api/favorites" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

查询参数:
- `folder_id` (可选): 文件夹ID，不传则获取所有收藏
- `sort_by` (可选): 排序字段（created_at, title），默认created_at
- `order` (可选): 排序方向（asc, desc），默认desc

### 2. 切换收藏状态

```bash
curl -X POST "http://localhost:5000/api/favorites/toggle" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "paper_id": "2301.00001",
    "folder_id": "folder-uuid"  // 可选，不传则不分类
  }'
```

### 3. 更新收藏项

```bash
curl -X PUT "http://localhost:5000/api/favorites/favorite-id" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_id": "new-folder-id",  // 可选
    "notes": "笔记内容",  // 可选
    "tags": ["标签1", "标签2"]  // 可选
  }'
```

### 4. 删除收藏项

```bash
curl -X DELETE "http://localhost:5000/api/favorites/favorite-id" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. 获取文件夹列表

```bash
curl -X GET "http://localhost:5000/api/favorites/folders" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. 创建文件夹

```bash
curl -X POST "http://localhost:5000/api/favorites/folders" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "深度学习论文",
    "color": "#3B82F6"  // 可选
  }'
```

### 7. 更新文件夹

```bash
curl -X PUT "http://localhost:5000/api/favorites/folders/folder-id" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "新名称",  // 可选
    "color": "#EF4444"  // 可选
  }'
```

### 8. 删除文件夹

```bash
curl -X DELETE "http://localhost:5000/api/favorites/folders/folder-id" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 数据模型

### Folder（文件夹）

```json
{
  "id": "folder-uuid",
  "name": "文件夹名称",
  "color": "#3B82F6",
  "created_by": "user-id",
  "created_at": "2025-02-13T10:00:00Z",
  "updated_at": "2025-02-13T10:00:00Z"
}
```

### Favorite（收藏项）

```json
{
  "id": "favorite-uuid",
  "user_id": "user-id",
  "paper_id": "2301.00001",
  "folder_id": "folder-id",  // 可选，null表示未分类
  "title": "论文标题",
  "authors": ["作者1", "作者2"],
  "notes": "笔记内容",
  "tags": ["标签1", "标签2"],
  "created_at": "2025-02-13T10:00:00Z"
}
```

---

## 测试检查清单

### 收藏项功能

- [ ] GET /api/favorites - 获取所有收藏
- [ ] GET /api/favorites?folder_id=xxx - 获取指定文件夹下的收藏
- [ ] GET /api/favorites?folder_id= - 获取未分类收藏
- [ ] POST /api/favorites/toggle - 添加收藏（无文件夹）
- [ ] POST /api/favorites/toggle - 添加收藏（指定文件夹）
- [ ] POST /api/favorites/toggle - 移除收藏（再次切换）
- [ ] PUT /api/favorites/{id} - 更新笔记
- [ ] PUT /api/favorites/{id} - 更新标签
- [ ] PUT /api/favorites/{id} - 移动到其他文件夹
- [ ] DELETE /api/favorites/{id} - 删除收藏
- [ ] 错误处理：无效论文ID（404）
- [ ] 错误处理：重复收藏（201，返回已存在）
- [ ] 错误处理：未认证请求（401）

### 文件夹功能

- [ ] GET /api/favorites/folders - 获取所有文件夹
- [ ] POST /api/favorites/folders - 创建文件夹（不指定颜色）
- [ ] POST /api/favorites/folders - 创建文件夹（指定颜色）
- [ ] POST /api/favorites/folders - 创建同名文件夹（409错误）
- [ ] PUT /api/favorites/folders/{id} - 更新名称
- [ ] PUT /api/favorites/folders/{id} - 更新颜色
- [ ] PUT /api/favorites/folders/{id} - 同名冲突检测（409）
- [ ] DELETE /api/favorites/folders/{id} - 删除文件夹
- [ ] DELETE /api/favorites/folders/{id} - 收藏项移至未分类
- [ ] 错误处理：无效文件夹ID（404）
- [ ] 错误处理：权限检查（用户只能操作自己的资源）

---

## MongoDB索引

### favorites集合

```javascript
{
  "user_id": 1,        // 用户ID索引
  "paper_id": 1,        // 论文ID索引
  "folder_id": 1,        // 文件夹ID索引
  "created_at": -1       // 创建时间索引（倒序）
}
```

复合唯一索引：
- `user_id + paper_id` (唯一，防止重复收藏）

### folders集合

```javascript
{
  "created_by": 1,       // 创建者索引
  "name": 1,            // 名称索引
  "created_at": -1       // 创建时间索引（倒序）
}
```

复合唯一索引：
- `created_by + name` (唯一，同一用户下文件夹名唯一）

---

## 响应格式

### 成功响应

```json
{
  "success": true,
  "data": {
    // 响应数据
  }
}
```

### 错误响应

```json
{
  "success": false,
  "error": "错误描述"
}
```

常见HTTP状态码：
- `200` - OK
- `201` - Created（创建成功）
- `400` - Bad Request（请求参数错误）
- `401` - Unauthorized（未认证或token无效）
- `404` - Not Found（资源不存在）
- `409` - Conflict（资源冲突，如重复创建）
- `500` - Internal Server Error（服务器错误）

---

## 集成说明

收藏夹API依赖于：
1. **认证中间件** (`middleware/auth.py`) - JWT认证
2. **数据库配置** (`config/database.py`) - MongoDB连接
3. **arXiv客户端** (`services/arxiv_client.py`) - 获取论文信息

数据库集合：
- `favorites` - 收藏项集合
- `folders` - 文件夹集合

蓝图注册：
- 已在 `app/__init__.py` 中注册
- URL前缀：`/api/favorites`
