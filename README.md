# ScholarAI - 全栈学术论文管理系统

## 项目概述

一个面向中国科研人员的学术论文搜索与管理系统，包含完整的论文管理、项目组织和收藏夹功能。

## 技术栈

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite 6
- **UI 库**: Radix UI + Lucide Icons
- **样式方案**: Tailwind CSS v4
- **路由管理**: React Router v7
- **状态管理**: React Hooks + LocalStorage
- **通知提示**: Sonner

### 后端
- **语言**: Python 3.10+
- **框架**: Flask
- **数据库**: MongoDB
- **API 风格**: RESTful API

## 项目结构

```
fullstack-merged/
├── tasks.json              # 任务清单
├── progress.json           # 进度记录
├── init.sh                # Unix/Linux 启动脚本
├── init.ps1               # Windows 启动脚本
├── backend/               # Python 后端
│   ├── app.py              # Flask 应用
│   ├── requirements.txt     # Python 依赖
│   └── venv/              # 虚拟环境
├── frontend/              # React 前端
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── services/
    │   └── ...
    └── package.json
```

## 功能列表

### 用户认证
- ✅ 用户注册
- ✅ 用户登录
- ✅ JWT 认证
- ✅ LocalStorage 持久化

### 论文搜索
- ✅ 关键词搜索
- ✅ 领域过滤
- ✅ 年份过滤
- ✅ 发表场所过滤
- ✅ 分页显示

### 项目管理
- ✅ 创建研究项目
- ✅ 查看项目详情
- ✅ 编辑项目信息
- ✅ 删除项目
- ✅ 项目统计

### 论文库
- ✅ 浏览所有论文
- ✅ 查看论文详情
- ✅ PDF 预览
- ✅ 添加到收藏夹
- ✅ 导出到 BibTeX
- ✅ 导出到 APA
- ✅ 导出到 MLA

### 收藏夹
- ✅ 查看收藏列表
- ✅ 添加到收藏夹
- ✅ 从收藏夹移除
- ✅ 创建文件夹
- ✅ 按时间排序

### 系统设置
- ✅ 主题切换
- ✅ API Key 配置
- ✅ 语言切换
- ✅ 界面设置

## 开发指南

### 环境准备

1. **安装 Python 3.10+**
   ```bash
   python3 --version
   ```

2. **创建虚拟环境**
   ```bash
   cd backend
   python3 -m venv venv
   ```

3. **安装后端依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **安装 Node.js 18+**
   ```bash
   node --version
   ```

5. **安装前端依赖**
   ```bash
   cd frontend
   npm install
   ```

### 启动开发服务器

#### Linux/macOS
```bash
./init.sh
```

#### Windows
```powershell
.\init.ps1
```

### 访问

- 后端 API: http://localhost:5000
- 前端界面: http://localhost:5173

## 工作流集成

本项目遵循 `D:/ai/CLAUDE.md` 中定义的前后端自动化开发工作流：

1. **任务追踪**: 使用 `tasks.json` 追踪所有功能实现
2. **进度记录**: 使用 `progress.json` 记录会话历史
3. **增量开发**: 每个会话完成一个功能
4. **E2E 测试**: 使用浏览器自动化工具验证
5. **清洁交接**: 每次会话结束时代码可运行

## 开发状态

- ✅ 前端: 已完成（基于 D:\ai\Search）
- ✅ 后端: 部分完成（基于 D:\ai\scholarai-backend）
- 🔄 集成: 进行中

## 自动化开发循环

本项目提供了自动化脚本，可以连续运行多次开发迭代，自动调用Claude Code完成任务。

### 快速开始

1. **查看当前进度**
   ```powershell
   # Windows PowerShell
   .\check-progress.ps1

   # Linux/macOS/Git Bash
   ./check-progress.sh
   ```

2. **运行自动化开发循环**
   ```powershell
   # 运行5次开发循环（推荐）
   .\run-dev-loop.ps1 5

   # Linux/macOS/Git Bash
   ./run-dev-loop.sh 5
   ```

### 工作原理

每次迭代自动执行以下流程：

1. ✅ 从 `tasks.json` 选择下一个未完成任务
2. 🤖 调用 Claude Code 完成该任务
3. 📝 自动提交代码到 Git
4. 📊 更新 `tasks.json` 任务状态
5. 📋 生成会话总结到 Progress Log 文件夹

### 脚本说明

| 脚本 | 说明 | 推荐环境 |
|-------|------|----------|
| `run-dev-loop.ps1` | PowerShell自动化循环 | Windows |
| `run-dev-loop.sh` | Bash自动化循环 | Linux/macOS/Git Bash |
| `run-dev-loop.bat` | 批处理自动化循环 | Windows (无PowerShell) |
| `check-progress.ps1` | PowerShell进度查看 | Windows |
| `check-progress.sh` | Bash进度查看 | Linux/macOS/Git Bash |

详细使用说明请参阅：[DEV_LOOP_README.md](DEV_LOOP_README.md)

### 示例输出

```
============================================================
  ScholarAI 项目进度报告
============================================================

📊 总体进度
  总任务数:    39
  已完成:      19 个
  进行中:      0 个
  待办:        20 个

  进度:        [████████████░░░░░░░░░░░░░░░░░░░░░░░░] 49%

📋 下一个待办任务 (按优先级)
  task-019 | 创建前端API服务层基础架构
    类别: api-service, 优先级: 1
  task-020 | 实现用户认证API集成
    类别: authentication, 优先级: 1
```

## 下一步

1. **查看当前进度**
   ```powershell
   .\check-progress.ps1
   ```

2. **运行自动化循环**
   ```powershell
   # 运行5次开发循环
   .\run-dev-loop.ps1 5
   ```

3. **查看日志**
   ```bash
   cat dev-loop.log
   ```

## 许可证

MIT License
