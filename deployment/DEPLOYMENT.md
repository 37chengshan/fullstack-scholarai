# ScholarAI 部署指南

本文档提供 ScholarAI ���用的完整部署指南，包括后端（Flask + MongoDB）和前端（React + Vite）。

## 目录

- [环境准备](#环境准备)
- [后端部署](#后端部署)
- [前端部署](#前端部署)
- [Docker 部署](#docker-部署)
- [云平台部署](#云平台部署)

---

## 环境准备

### 系统要求

- **Node.js**: 18.x 或更高版本
- **Python**: 3.9 或更高版本
- **MongoDB**: 4.4 或更高版本（推荐使用 MongoDB Atlas）
- **Git**: 最新版本

### 必需的 API 密钥

1. **MongoDB Atlas**: https://www.mongodb.com/cloud/atlas
2. **智谱 AI API**: https://open.bigmodel.cn/usercenter/apikeys

---

## 后端部署

### 1. 安装 Python 依赖

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 创建 .env 文件
cd backend
cp ../deployment/.env.production.example .env

# 编辑 .env 文件，填入实际配置
notepad .env  # Windows
nano .env     # Linux/Mac
```

**必须配置的变量**：
- `MONGODB_URI` - MongoDB 连接字符串
- `JWT_SECRET_KEY` - JWT 密钥（生成方法：`python -c "import secrets; print(secrets.token_urlsafe(32))"`）
- `ZHIPU_API_KEY` - 智谱 AI API 密钥

### 3. 运行后端服务器

**开发环境**：
```bash
python run.py
```

**生产环境**（使用 Gunicorn）：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 4. 验证后端部署

访问健康检查端点：
```bash
curl http://localhost:5000/api/health
```

预期响应：
```json
{
  "status": "healthy",
  "timestamp": "2025-02-13T10:00:00Z",
  "database": "connected",
  "version": "1.0.0"
}
```

---

## 前端部署

### 1. 安装 Node.js 依赖

```bash
cd frontend
npm install
```

### 2. 配置 API 端点

编辑 `frontend/src/config/api.ts`，确保 API_BASE_URL 指向正确的后端地址：

```typescript
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
```

### 3. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

### 4. 本地预览构建结果

```bash
npm run preview
```

### 5. 使用静态服务器部署

```bash
# 全局安装 serve
npm install -g serve

# 部署
serve -s dist -l 5173
```

---

## Docker 部署

### 使用 Docker Compose（推荐）

1. **创建 docker-compose.yml**：

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - MONGODB_URI=${MONGODB_URI}
      - ZHIPU_API_KEY=${ZHIPU_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - FLASK_ENV=production
    depends_on:
      - mongodb
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:80"
    depends_on:
      - backend
    restart: unless-stopped

  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped

volumes:
  mongodb_data:
```

2. **启动服务**：

```bash
docker-compose up -d
```

3. **查看日志**：

```bash
docker-compose logs -f
```

4. **停止服务**：

```bash
docker-compose down
```

---

## 云平台部署

### Vercel（前端）

1. **连接 GitHub 仓库**：
   - 访问 https://vercel.com
   - 导入项目：`37chengshan/fullstack-scholarai`
   - 选择 `frontend` 目录作为根目录

2. **配置环境变量**：
   ```
   VITE_API_URL=https://your-backend-url.com/api
   ```

3. **部署**：
   - Vercel 会自动部署
   - 每次推送到 main 分支都会触发部署

### Railway（后端）

1. **连接 GitHub 仓库**：
   - 访问 https://railway.app
   - 新建项目 → 选择 `backend` 目录

2. **配置环境变量**：
   - `MONGODB_URI`
   - `ZHIPU_API_KEY`
   - `JWT_SECRET_KEY`
   - `FLASK_ENV=production`

3. **部署**：
   - Railway 会自动检测 Flask 应用并部署

### Render（全栈）

1. **Web Services**：
   - 后端：选择 `backend` 目录
   - 前端：选择 `frontend/dist` 目录

2. **环境变量**：
   - 同上

3. **部署**：
   - Render 提供 SSL 和自定义域名

---

## 监控和维护

### 日志

**后端日志位置**：
- 开发环境：控制台输出
- 生产环境：`/var/log/scholarai/app.log`

**查看实时日志**：
```bash
# Docker
docker-compose logs -f backend

# Railway
railway logs

# Render
# 查看 dashboard 中的 logs
```

### 健康检查

定期检查后端健康状态：
```bash
curl https://your-domain.com/api/health
```

### 备份

**MongoDB 备份**（如果使用 Atlas）：
- 自动备份已启用
- 可在 Atlas Dashboard 中配置备份策略

---

## 故障排查

### 常见问题

1. **CORS 错误**
   - 确保 `ALLOWED_ORIGINS` 包含前端域名
   - 检查后端 CORS 配置

2. **MongoDB 连接失败**
   - 检查 `MONGODB_URI` 是否正确
   - 确保 IP 白名单包含服务器 IP

3. **AI API 调用失败**
   - 验证 `ZHIPU_API_KEY` 是否有效
   - 检查 API 额度是否用完

4. **前端构建失败**
   - 删除 `node_modules` 和 `package-lock.json`
   - 重新运行 `npm install`

---

## 安全建议

1. **永远不要提交 `.env` 文件到 Git**
2. **使用强密码和随机密钥**
3. **定期更新依赖包**
4. **启用 HTTPS**
5. **配置防火墙规则**
6. **定期备份数据库**

---

## 联系支持

如有部署问题，请查看：
- GitHub Issues: https://github.com/37chengshan/fullstack-scholarai/issues
- 文档: README.md
