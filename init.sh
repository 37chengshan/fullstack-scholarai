#!/bin/bash

# ScholarAI 全栈应用 - 环境启动脚本
# 包含前端和后端的启动

set -e  # 遇到错误立即退出

echo "🚀 初始化 ScholarAI 全栈开发环境..."

# ==================== 后端环境设置 ====================

echo "📦 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "   ❌ Python 3 未安装"
    echo "   💡 请安装 Python 3.10+"
    exit 1
fi

PYTHON_CMD=python3

echo "   ✅ Python 环境检查通过"
echo "🗄️  检查并创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv > /dev/null
    echo "   ✅ 虚拟环境已创建"
else
    echo "   ℹ️  虚拟环境已存在"
fi

echo "🔧 配置环境变量..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   ⚠️  请配置 .env 文件"
fi

echo "📦 安装后端依赖..."
cd backend || exit 1
pip install -r requirements.txt || exit 1

echo "✅ 后端依赖安装完成"

# ==================== 前端环境设置 ====================

echo "📦 检查 Node.js 环境..."
if ! command -v node &> /dev/null; then
    echo "   ❌ Node.js 未安装"
    echo "   💡 请安装 Node.js 18+"
    exit 1
fi

NODE_CMD=node

echo "   ✅ Node.js 环境检查通过"

echo "🎨 安装前端依赖..."
cd frontend || exit 1
npm install || exit 1

echo "✅ 前端依赖安装完成"

# ==================== 启动开发服务器 ====================

echo ""
echo "🚀 启动开发服务器..."
echo "📝 后端 API 服务器"
echo "📝 前端开发服务器"
echo ""

# 检查端口占用
echo "📊 检查端口占用情况..."
netstat -ano | findstr :5000 > /dev/null || echo "   ⚠️  端口 5000 未被占用"
netstat -ano | findstr :5173 > /dev/null || echo "   ⚠️  端口 5173 未被占用"

# 启动后端
echo "📡 启动后端服务..."
cd backend || exit 1
nohup gunicorn app:app &
BACKEND_PID=$!
echo "   ✅ 后端服务已启动 (PID: $BACKEND_PID)"

# 启动前端
echo "🌐 启动前端服务..."
cd frontend || exit 1
nohup > dev/null 2>&1 &
npm run dev &
FRONTEND_PID=$!
echo "   ✅ 前端服务已启动 (PID: $FRONTEND_PID)"

echo ""
echo "✅ 开发环境启动完成！"
echo ""
echo "📍 后端 API: http://localhost:5000"
echo "📍 前端界面: http://localhost:5173"
echo ""
echo "💡 提示："
echo "   • 按 Ctrl+C 停止服务器"
echo "   • 使用全新终端窗口以获得最佳体验"
echo ""

# 等待用户中断
wait
