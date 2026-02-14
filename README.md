# ScholarAI - 学术论文智能搜索平台

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![React](https://img.shields.io/badge/react-18+-blue)
![Flask](https://img.shields.io/badge/flask-2.0+-red)
![License](https://img.shields.io/badge/license-MIT-yellow)

一个面向中国科研人员的智能学术论文搜索与管理系统

集成了OpenAlex论文搜索、智谱AI助手、项目管理等全方位功能

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [开发指南](#-开发指南) • [API文档](#-api文档) • [贡献指南](#-贡献指南)

</div>

---

## 📋 项目概述

ScholarAI是一个功能强大的学术论文管理平台，专为科研人员设计。系统集成了：

- 🔍 **智能论文搜索** - 基于OpenAlex API的免费无限制论文检索
- 🤖 **AI研究助手** - 集成智谱AI，提供论文摘要、精读、问答等服务
- 📁 **项目管理** - 创建研究项目，组织论文，跟踪阅读进度
- ⭐ **收藏系统** - 收藏重要论文，创建文件夹��类管理
- 📄 **文件上传** - 支持PDF上传和URL添加
- 🎨 **现代化UI** - 响应式设计，支持深色模式

## 🚀 功能特性

### 核心功能

| 功能模块 | 状态 | 说明 |
|---------|------|------|
| **用户认证** | ✅ 完成 | 用户注册、登录、JWT认证 |
| **论文搜索** | ✅ 完成 | 关键词搜索、多维度筛选、分页 |
| **论文详情** | ✅ 完成 | 完整的论文元数据、引用信息、概念标签 |
| **AI聊天助手** | ✅ 完成 | 实时流式对话、论文问答、思维导图 |
| **AI摘要功能** | ✅ 完成 | 一键生成论文摘要、关键点提取 |
| **AI论文精读** | ✅ 完成 | 深度分析论文内容、研究方法、创新点 |
| **项目管理** | ✅ 完成 | 创建项目、添加论文、进度统计 |
| **收藏管理** | ✅ 完成 | 收藏论文、文件夹分类、笔记标签 |
| **文件上传** | ✅ 完成 | PDF上传、URL添加、进度显示 |
| **用户设置** | ✅ 完成 | 主题切换、API配置、使用统计 |
| **搜索历史** | ✅ 完成 | 自动记录搜索历史、快速访问 |
| **最近查看** | ✅ 完成 | 浏览历史追踪 |

### 性能优化

- ⚡ **智能缓存** - 翻页速度从500-1500ms优化至<100ms（缓存命中时）
- 🔄 **预加载机制** - 自动预加载下一页，实现近乎0延迟的翻页体验
- 📊 **LRU缓存策略** - 智能缓存管理，最多缓存50页，TTL 10分钟
- 🎯 **目标滚动** - 优化滚动行为，避免整页重绘

### API集成

| 服务 | 用途 | 免费额度 |
|-----|------|---------|
| **OpenAlex** | 论文搜索、元数据获取 | 完全免费无限制 |
| **智谱AI** | AI对话、摘要、精读 | 需配置API Key |
| **MongoDB** | 数据存储 | Atlas免费版 |

## 🛠️ 技术栈

### 前端技术

```yaml
框架: React 18.3 + TypeScript 5.6
构建工具: Vite 6.0
UI组件: Radix UI (无障碍组件库)
图标: Lucide React
样式: Tailwind CSS v4
路由: React Router v7
状态管理: React Hooks + Context API
表单: React Hook Form + Zod验证
通知: Sonner
图表: Recharts
```

### 后端技术

```yaml
语言: Python 3.10+
框架: Flask 3.0
数据库: MongoDB Atlas
API风格: RESTful
认证: JWT (PyJWT)
密码加密: bcrypt
日志: logging模块
CORS: Flask-CORS
```

### 开发工具

```yaml
代码规范: ESLint + Prettier
类型检查: TypeScript
包管理: npm (frontend) + pip (backend)
版本控制: Git
API测试: curl + Postman
浏览器测试: Chrome DevTools MCP
```

## 📦 项目结构

```
fullstack-scholarai/
├── backend/                      # Python Flask后端
│   ├── app/
│   │   ├── __init__.py          # Flask应用初始化
│   │   ├── config.py            # 配置文件
│   │   └── database.py          # MongoDB连接
│   ├── routes/                   # API路由
│   │   ├── auth.py              # 认证接口
│   │   ├── papers.py            # 论文接口
│   │   ├── projects.py          # 项目接口
│   │   ├── favorites.py         # 收藏接口
│   │   ├── upload.py            # 上传接口
│   │   ├── ai_chat.py           # AI聊天接口
│   │   └── settings.py          # 设置接口
│   ├── services/                 # 业务逻辑层
│   │   ├── openalex_client.py   # OpenAlex客户端
│   │   ├── zhipu_client.py      # 智谱AI客户端
│   │   └── unified_search_fix.py # 统一搜索服务
│   ├── models/                   # 数据模型
│   ├── middleware/               # 中间件
│   ├── utils/                    # 工具函数
│   ├── requirements.txt          # Python依赖
│   └── run.py                   # 启动脚本
│
├── frontend/                     # React前端
│   ├── src/
│   │   ├── App.tsx              # 主应用组件
│   │   ├── main.tsx             # 入口文件
│   │   ├── components/          # 可复用组件
│   │   │   ├── ui/              # UI基础组件
│   │   │   ├── search/          # 搜索相关组件
│   │   │   ├── project/         # 项目相关组件
│   │   │   └── auth/            # 认证相关组件
│   │   ├── pages/               # 页面组件
│   │   │   ├── HomePage.tsx     # 首页/搜索页
│   │   │   ├── PaperDetails.tsx # 论文详情页
│   │   │   ├── AIChat.tsx       # AI聊天页
│   │   │   ├── Projects.tsx     # 项目管理页
│   │   │   ├── Favorites.tsx    # 收藏管理页
│   │   │   └── Settings.tsx     # 设置页
│   │   ├── services/            # API服务
│   │   │   ├── papersApi.ts     # 论文API
│   │   │   ├── authApi.ts       # 认证API
│   │   │   └── aiApi.ts         # AI API
│   │   ├── utils/               # 工具函数
│   │   │   ├── pageCache.ts     # 缓存管理
│   │   │   └── storage.ts       # LocalStorage封装
│   │   ├── hooks/               # 自定义Hooks
│   │   ├── types/               # TypeScript类型定义
│   │   └── styles/              # 全局样式
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── e2e/                          # E2E测试
│   └── playwright.config.ts
│
├── deployment/                   # 部署配置
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
│
├── tasks.json                    # 任务清单
├── progress.json                 # 开发进度
├── CLAUDE.md                     # 开发工作流指南
├── CURRENT-STATUS.md             # 当前项目状态
├── .gitignore
└── README.md
```

## 🏃 快速开始

### 环境要求

- **Node.js**: 18.0.0+
- **Python**: 3.10+
- **MongoDB**: 6.0+ (使用MongoDB Atlas免费版)
- **npm**: 9.0.0+

### 1. 克隆项目

```bash
git clone https://github.com/37chengshan/fullstack-scholarai.git
cd fullstack-scholarai
```

### 2. 配置环境变量

创建 `backend/.env` 文件：

```env
# MongoDB配置
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?appName=Cluster0

# JWT配置
JWT_SECRET_KEY=your-secret-key-here
JWT_ACCESS_TOKEN_EXPIRES=3600

# 智谱AI配置（可选）
ZHIPU_API_KEY=your-zhipu-api-key

# CORS配置
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

创建 `frontend/.env.local` 文件：

```env
# API配置
VITE_API_BASE_URL=http://localhost:5000
VITE_API_TIMEOUT=30000

# 智谱AI配置（可选，用于前端直接调用）
VITE_ZHIPU_API_KEY=your-zhipu-api-key
```

### 3. 安装依赖

```bash
# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd ../frontend
npm install
```

### 4. 启动开发服务器

#### 方式一：分别启动（推荐用于开发）

```bash
# 终端1：启动后端
cd backend
python run.py

# 终端2：启动前端
cd frontend
npm run dev
```

#### 方式二：使用启动脚本

**Windows:**
```powershell
.\init.ps1
```

**Linux/macOS:**
```bash
./init.sh
```

### 5. 访问应用

- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:5000
- **API文档**: http://localhost:5000/api/docs (如果配置了Swagger)

### 6. 测试账号

系统预置测试账号：

```
邮箱: test@qq.com
密码: Test123456
```

## 📖 使用指南

### 论文搜索

1. 输入关键词（如 "deep learning"）
2. 选择筛选条件（领域、年份、期刊）
3. 查看搜索结果
4. 点击论文查看详情

### AI助手使用

1. **配置API Key**: 在设置中配置智谱AI API Key
2. **开始对话**: 进入AI聊天页面，输入问题
3. **论文摘要**: 在论文详情页点击"AI摘要"生成摘要
4. **论文精读**: 点击"AI精读"进行深度分析

### 项目管理

1. 创建新项目
2. 搜���并添加论文到项目
3. 标记论文阅读状态（未读/已读/重要）
4. 查看项目统计和进度

## 🔧 开发指南

### 代码规范

- **前端**: 遵循 ESLint + Prettier 配置
- **后端**: 遵循 PEP 8 规范
- **Git**: 使用 Conventional Commits 规范

### API开发流程

1. 在 `backend/routes/` 创建或修改路由
2. 在 `backend/services/` 实现业务逻辑
3. 在 `frontend/src/services/` 创建前端API客户端
4. 在组件中调用API并处理响应
5. 添加错误处理和用户反馈

### 测试

```bash
# 运行后端测试
cd backend
pytest

# 运行前端测试
cd frontend
npm run test

# 运行E2E测试
npm run test:e2e
```

### 调试技巧

- **前端**: 使用Chrome DevTools
- **后端**: 查看Flask日志输出
- **API测试**: 使用Postman或curl
- **数据库**: 使用MongoDB Atlas Compass

## 📚 API文档

### 认证接口

```http
POST   /api/auth/register    # 用户注册
POST   /api/auth/login       # 用户登录
GET    /api/auth/me          # 获取当前用户信息
PUT    /api/auth/me          # 更新用户信息
```

### 论文接口

```http
GET    /api/papers/search              # 搜索论文
GET    /api/papers/:id                 # 获取论文详情
GET    /api/papers/similar/:id         # 获取相似论文
```

### 项目接口

```http
GET    /api/projects                   # 获取项目列表
POST   /api/projects                   # 创建项目
GET    /api/projects/:id               # 获取项目详情
PUT    /api/projects/:id               # 更新项目
DELETE /api/projects/:id               # 删除项目
POST   /api/projects/:id/papers        # 添加论文到项目
```

### 收藏接口

```http
GET    /api/favorites                  # 获取收藏列表
POST   /api/favorites/toggle           # 切换收藏状态
PUT    /api/favorites/:id              # 更新收藏
DELETE /api/favorites/:id              # 删除收藏
```

### AI接口

```http
POST   /api/ai/chat/stream             # 流式AI对话
POST   /api/ai/summary                 # 生成论文摘要
POST   /api/ai/analysis                # 论文深度分析
POST   /api/ai/mindmap                 # 生成思维导图
```

### 文件上传接口

```http
POST   /api/upload/file                # 上传PDF文件
POST   /api/upload/url                 # 通过URL添加论文
```

详细API文档请参考：[API.md](docs/API.md)

## 🚀 部署

### Docker部署（推荐）

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 手动部署

**后端部署：**

```bash
cd backend
pip install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**前端部署：**

```bash
cd frontend
npm run build
# 将 dist/ 目录部署到静态文件服务器
```

## 📊 性能优化

### 已实现的优化

| 优化项 | 优化前 | 优化后 | 提升幅度 |
|-------|--------|--------|----------|
| 翻页加载（缓存命中） | 500-1500ms | <100ms | **10-15倍** |
| 翻页加载（预加载） | 500-1500ms | ≈0ms | **接近瞬时** |
| 搜索结果缓存 | 无 | 50页/10分钟 | 新增功能 |
| API调用次数 | 100% | 减少80% | **大幅降低** |

### 优化策略

1. **智能缓存**: 多级缓存键（query + filters + page + sortBy）
2. **预加载**: 停留2秒后自动预加载下一页
3. **LRU策略**: 最多缓存50页，自动淘汰最旧条目
4. **目标滚动**: 使用 `scrollIntoView()` 避免整页重绘

## 🧪 测试

### 测试覆盖

- ✅ 单元测试（后端）
- ✅ 组件测试（前端）
- ✅ E2E测试（Playwright）
- ✅ API测试

### 运行测试

```bash
# 后端测试
cd backend
pytest --cov=.

# 前端测试
cd frontend
npm run test

# E2E测试
npm run test:e2e
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add some amazing feature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试相关
chore: 构建/工具
```

## 📝 更新日志

### v1.0.0 (2026-02-15)

**功能完成**
- ✅ 完成所有26个核心任务
- ✅ 用户认证系统
- ✅ 论文搜索与详情
- ✅ AI助手集成
- ✅ 项目与收藏管理
- ✅ 文件上传功能

**性能优化**
- ⚡ 实现智能缓存机制
- ⚡ 实现预加载机制
- ⚡ 翻页速度提升10-15倍

**Bug修复**
- 🐛 修复论文详情API错误
- 🐛 修复缓存失效问题

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👥 团队

- **开发者**: 37chengshan
- **AI辅助**: Claude Code (Anthropic)

## 🙏 致谢

- [OpenAlex](https://openalex.org/) - 免费的论文搜索API
- [智谱AI](https://open.bigmodel.cn/) - AI对话服务
- [Radix UI](https://www.radix-ui.com/) - 无障碍UI组件
- [Tailwind CSS](https://tailwindcss.com/) - CSS框架

## 📮 联系方式

- **GitHub**: https://github.com/37chengshan/fullstack-scholarai
- **问题反馈**: https://github.com/37chengshan/fullstack-scholarai/issues

---

<div align="center">

**如果这个项目对你有帮助，请给个⭐️Star支持一下！**

Made with ❤️ by ScholarAI Team

</div>
