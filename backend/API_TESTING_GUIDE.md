# 认证API端点测试指南

本文档提供详细的认证API端点测试说��。

## 前置条件

1. MongoDB数据库已启动并可访问
2. 已配置`.env`文件（包含MongoDB连接字符串和JWT密钥）
3. Python环境已安装所需依赖

## 启动服务器

```bash
cd backend
python run.py
```

服务器将在 `http://localhost:5000` 启动

## API端点列表

### 1. 健康检查
```
GET /api/health
```

**响应示例：**
```json
{
  "success": true,
  "status": "healthy",
  "message": "ScholarAI API is running"
}
```

---

### 2. 用户注册
```
POST /api/auth/register
```

**请求体：**
```json
{
  "name": "张三",
  "email": "zhangsan@example.com",
  "password": "Test1234"
}
```

**成功响应（201）：**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user-uuid",
      "email": "zhangsan@example.com",
      "name": "张三",
      "avatar": null,
      "role": "user",
      "is_active": true,
      "stats": {
        "papers_searched": 0,
        "favorites_count": 0,
        "projects_count": 0,
        "ai_queries_count": 0
      },
      "created_at": "2025-02-13T12:00:00",
      "updated_at": "2025-02-13T12:00:00"
    },
    "message": "注册成功"
  }
}
```

**错误响应示例：**

邮箱已存在（409）：
```json
{
  "success": false,
  "error": "该邮箱已被注册"
}
```

邮箱格式无效（400）：
```json
{
  "success": false,
  "error": "邮箱格式不正确"
}
```

密码太弱（400）：
```json
{
  "success": false,
  "error": "密码长度至少为8个字符"
}
```

**密码要求：**
- 最少8个字符
- 必须包含字母
- 必须包含数字

---

### 3. 用户登录
```
POST /api/auth/login
```

**请求体：**
```json
{
  "email": "zhangsan@example.com",
  "password": "Test1234"
}
```

**成功响应（200）：**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "user": {
      "id": "user-uuid",
      "email": "zhangsan@example.com",
      "name": "张三",
      "avatar": null,
      "role": "user",
      "is_active": true,
      "stats": { ... },
      "created_at": "2025-02-13T12:00:00",
      "updated_at": "2025-02-13T12:00:00"
    }
  }
}
```

**错误响应示例：**

邮箱或密码错误（401）：
```json
{
  "success": false,
  "error": "邮箱或密码错误"
}
```

账户被禁用（403）：
```json
{
  "success": false,
  "error": "账户已被禁用"
}
```

---

### 4. 获取当前用户信息
```
GET /api/auth/me
```

**请求头：**
```
Authorization: Bearer <access_token>
```

**成功响应（200）：**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user-uuid",
      "email": "zhangsan@example.com",
      "name": "张三",
      "avatar": null,
      "role": "user",
      "is_active": true,
      "stats": { ... },
      "created_at": "2025-02-13T12:00:00",
      "updated_at": "2025-02-13T12:00:00"
    }
  }
}
```

**错误响应示例：**

缺少Token（401）：
```json
{
  "success": false,
  "error": "缺少Token，请先登录"
}
```

Token无效（401）：
```json
{
  "success": false,
  "error": "无效的Token"
}
```

Token过期（401）：
```json
{
  "success": false,
  "error": "Token已过期，请重新登录"
}
```

---

### 5. 用户登出
```
POST /api/auth/logout
```

**请求头：**
```
Authorization: Bearer <access_token>
```

**成功响应（200）：**
```json
{
  "success": true,
  "data": {
    "message": "登出成功"
  }
}
```

**注意：** JWT是无状态的，实际登出由前端删除token完成。此端点主要用于记录日志或执行清理操作。

---

### 6. 验证Token
```
POST /api/auth/verify-token
```

**请求头：**
```
Authorization: Bearer <access_token>
```

**成功响应 - Token有效（200）：**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "user": {
      "id": "user-uuid",
      "email": "zhangsan@example.com",
      "name": "张三",
      ...
    }
  }
}
```

**响应 - Token无效（200）：**
```json
{
  "success": true,
  "data": {
    "valid": false,
    "user": null
  }
}
```

---

## 使用cURL测试

### 测试注册
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张三",
    "email": "zhangsan@example.com",
    "password": "Test1234"
  }'
```

### 测试登录
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhangsan@example.com",
    "password": "Test1234"
  }'
```

### 测试获取用户信息
```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 测试登出
```bash
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 使用Python测试脚本

已创建完整的测试脚本 `test_auth_api.py`，运行以下命令：

```bash
cd backend
python test_auth_api.py
```

测试脚本将自动执行以下测试：
1. 健康检查
2. 用户注册
3. 无效邮箱注册（应失败）
4. 弱密码注册（应失败）
5. 用户登录
6. 错误密码登录（应失败）
7. 获取当前用户信息
8. 无Token获取用户（应失败）
9. 无效Token获取用户（应失败）
10. 用户登出
11. Token验证

---

## 实现验证清单

- [x] POST /api/auth/register - 创建新用户
- [x] POST /api/auth/login - 用户登录并返回token
- [x] GET /api/auth/me - 验证token并返回用户信息
- [x] POST /api/auth/logout - 登出
- [x] 使用无效token返回401错误
- [x] 邮箱格式验证
- [x] 密码强度验证（至少8字符，包含字母和数字）
- [x] 邮箱唯一性检查
- [x] JWT token生成和验证
- [x] 错误处理和响应格式统一
- [x] MongoDB数据库集成
- [x] 用户模型序列化（不包含敏感信息）

---

## 常见问题

### 1. 无法连接到MongoDB
**错误：** `Failed to connect to MongoDB`

**解决方案：**
- 检查MongoDB服务是否运行
- 检查`.env`文件中的`MONGODB_URI`配置是否正确
- 确认网络连接和防火墙设置

### 2. JWT验证失败
**错误：** `Invalid token` 或 `Token has expired`

**解决方案：**
- 检查`.env`文件中的`JWT_SECRET_KEY`配置
- 确认Token未过期（默认1小时）
- 确认请求头格式正确：`Authorization: Bearer <token>`

### 3. CORS错误
**错误：** 浏览器控制台显示CORS错误

**解决方案：**
- 已在`app/__init__.py`中配置CORS
- 确认前端URL在允许的源列表中（localhost:5173, localhost:3000）

---

## 下一步

完成测试后，可以继续实现：
- task-007: arXiv API集成
- task-009: 智谱AI客户端封装
- 或其他待办任务

---

## 文件清单

本次实现创建/修改的文件：

1. **backend/routes/auth.py** - 认证路由实现（新增）
2. **backend/app/__init__.py** - 注册auth蓝图，初始化数据库（修改）
3. **backend/test_auth_api.py** - API测试脚本（新增）
4. **backend/verify_auth_api.py** - 实现验证脚本（新增）
5. **backend/API_TESTING_GUIDE.md** - 本测试指南（新增）

---

**创建时间：** 2025-02-13
**任务编号：** task-006
**状态：** ✅ 完成
