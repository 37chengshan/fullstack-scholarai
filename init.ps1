# ScholarAI 全栈应用 - Windows 启动脚本
# 包含前端和后端

$ErrorActionPreference = "Stop"

# ==================== 环境检查 ====================

Write-Host "🚀 初始化 ScholarAI 全栈开发环境..." -ForegroundColor Cyan

# 检查 Python 环境
Write-Host "📦 检查 Python 环境..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion -match "3\.10\.")) {
        Write-Host "   ✅ Python 版本: $($pythonVersion)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Python 版本过低，需要 3.10+" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Python 未安装" -ForegroundColor Red
    Write-Host "   💡 请安装 Python 3.10+: https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# 检查 Node.js 环境
Write-Host "📦 检查 Node.js 环境..." -ForegroundColor Cyan
try {
    $nodeVersion = node --version 2>$null
    Write-Host "   ✅ Node.js 版本: $($nodeVersion)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Node.js 未安装" -ForegroundColor Red
    Write-Host "   💡 请安装 Node.js 18+: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# ==================== 后端设置 ====================

Write-Host ""
Write-Host "🔧 配置后端环境..." -ForegroundColor Cyan

$BackendDir = "backend"
if (-not (Test-Path "$BackendDir")) {
    Write-Host "   ❌ 后端目录不存在: $BackendDir" -ForegroundColor Red
    exit 1
}

# 检查虚拟环境
Write-Host "🐍 检查虚拟环境..." -ForegroundColor Cyan
if (-not (Test-Path "$BackendDir\venv")) {
    Write-Host "   创建虚拟环境..." -ForegroundColor Yellow
    python3 -m venv venv | Out-Null
    Write-Host "   ✅ 虚拟环境已创建" -ForegroundColor Green
}

# 安装依赖
Write-Host "📦 安装后端依赖..." -ForegroundColor Cyan
Push-Location $BackendDir
try {
    pip install -r requirements.txt
    Write-Host "   ✅ 后端依赖安装完成" -ForegroundColor Green
} catch {
    Write-Host "   ❌ 依赖安装失败" -ForegroundColor Red
    exit 1
}

# 配置环境变量
Write-Host "🔧 配置环境变量..." -ForegroundColor Cyan
if (-not (Test-Path "$BackendDir\.env")) {
    Copy-Item "$BackendDir\.env.example" "$BackendDir\.env"
    Write-Host "   ✅ .env 文件已创建" -ForegroundColor Green
    Write-Host "   ⚠️  请配置 .env 文件" -ForegroundColor Yellow
}

# ==================== 前端设置 ====================

Write-Host ""
Write-Host "🎨 配置前端环境..." -ForegroundColor Cyan

$FrontendDir = "frontend"
if (-not (Test-Path "$FrontendDir")) {
    Write-Host "   ❌ 前端目录不存在: $FrontendDir" -ForegroundColor Red
    exit 1
}

# 安装依赖
Write-Host "📦 安装前端依赖..." -ForegroundColor Cyan
Push-Location $FrontendDir
try {
    npm install
    Write-Host "   ✅ 前端依赖安装完成" -ForegroundColor Green
} catch {
    Write-Host "   ❌ 依赖安装失败" -ForegroundColor Red
    exit 1
}

# ==================== 启动服务 ====================

Write-Host ""
Write-Host "🚀 启动开发服务器..." -ForegroundColor Cyan

# 启动后端
Write-Host "📝 启动后端服务..." -ForegroundColor Cyan
try {
    $BackendProcess = Start-Process -FilePath "python" -ArgumentList "app.py" -WorkingDirectory $BackendDir -PassThru -NoNewWindow -ErrorAction Stop
    Write-Host "   ✅ 后端服务已启动 (PID: $($BackendProcess.Id))" -ForegroundColor Green
    $GLOBAL:BackendPID = $BackendProcess.Id
} catch {
    Write-Host "   ❌ 后端启动失败: $_" -ForegroundColor Red
}

# 启动前端
Write-Host "🎨 启动前端服务..." -ForegroundColor Cyan
Push-Location $FrontendDir
try {
    $FrontendProcess = Start-Process npm -ArgumentList "run" -ArgumentList "dev" -WorkingDirectory $FrontendDir -PassThru -NoNewWindow -ErrorAction Stop
    Write-Host "   ✅ 前端服务已启动 (PID: $($FrontendProcess.Id))" -ForegroundColor Green
    $GLOBAL:FrontendPID = $FrontendProcess.Id
} catch {
    Write-Host "   ❌ 前端启动失败: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ 开发环境启动完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📍 后端 API: http://localhost:5000" -ForegroundColor Cyan
Write-Host "📍 前端界面: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 提示：" -ForegroundColor Yellow
Write-Host "   • 按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host "   • 使用新终端窗口以获得最佳体验" -ForegroundColor Yellow
Write-Host ""

# 等待用户中断
Write-Host "按任意键停止..." -ForegroundColor Gray
Read-Host

# 清理进程
if ($GLOBAL:BackendPID) {
    Stop-Process -Id $GLOBAL:BackendPID -ErrorAction SilentlyContinue
    Write-Host "   ✅ 后端服务已停止" -ForegroundColor Green
}

if ($GLOBAL:FrontendPID) {
    Stop-Process -Id $GLOBAL:FrontendPID -ErrorAction SilentlyContinue
    Write-Host "   ✅ 前端服务已停止" -ForegroundColor Green
}
