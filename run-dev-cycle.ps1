# ScholarAI ���动化开发循环脚本 (PowerShell版本)
#
# 用法:
#   .\run-dev-cycle.ps1              # 运行1个任务（默认）
#   .\run-dev-cycle.ps1 -Cycles 3    # 运行3个任务
#   .\run-dev-cycle.ps1 -Cycles 0    # 运行所有pending任务
#
# 功能:
# - 每次调用Claude Code执行一个完整的开发任务
# - 自动从tasks.json中选取pending任务
# - 完成后更新任务状态并提交Git commit
# - 显示详细进展日志

param(
    [Parameter(Mandatory=$false)]
    [int]$Cycles = 1
)

# ===========================================
# 颜色定义
# ===========================================
$colors = @{
    Info = 'Green'
    Success = 'Green'
    Warning = 'Yellow'
    Error = 'Red'
    Section = 'Cyan'
}

# ===========================================
# 日志函数
# ===========================================
function Log-Info {
    param([string]$Message)
    Write-Host "[INFO] $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Message" -ForegroundColor $colors.Info
}

function Log-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Message" -ForegroundColor $colors.Success
}

function Log-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Message" -ForegroundColor $colors.Warning
}

function Log-Error {
    param([string]$Message)
    Write-Host "[ERROR] $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Message" -ForegroundColor $colors.Error
}

function Log-Section {
    param([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor $colors.Section
    Write-Host "$Message" -ForegroundColor $colors.Section
    Write-Host "========================================" -ForegroundColor $colors.Section
}

# ===========================================
# 环境检查
# ===========================================
$ErrorActionPreference = "Stop"
$PROJECT_ROOT = $PSScriptRoot

if (-not (Test-Path $PROJECT_ROOT)) {
    $PROJECT_ROOT = Get-Location
}

Set-Location $PROJECT_ROOT
Log-Info "项目根目录: $PROJECT_ROOT"

# 检查Claude Code是否安装
try {
    $null = &claude --version 2>&1
} catch {
    Log-Error "Claude Code命令未找到！请确保已安装Claude Code CLI。"
    exit 1
}

# 检查tasks.json
if (-not (Test-Path "tasks.json")) {
    Log-Error "tasks.json文件不存在！"
    exit 1
}

# ===========================================
# 统计函数
# ===========================================
function Get-PendingCount {
    $tasks = Get-Content "tasks.json" -Raw -Encoding UTF8 | ConvertFrom-Json
    ($tasks.tasks | Where-Object { $_.status -eq "pending" }).Count
}

function Get-CompletedCount {
    $tasks = Get-Content "tasks.json" -Raw -Encoding UTF8 | ConvertFrom-Json
    ($tasks.tasks | Where-Object { $_.status -eq "completed" }).Count
}

function Get-TotalTasks {
    $tasks = Get-Content "tasks.json" -Raw -Encoding UTF8 | ConvertFrom-Json
    $tasks.tasks.Count
}

function Get-NextTask {
    $tasks = Get-Content "tasks.json" -Raw -Encoding UTF8 | ConvertFrom-Json
    $pending = $tasks.tasks | Where-Object { $_.status -eq "pending" } | Sort-Object -Property priority
    if ($pending.Count -gt 0) {
        return $pending[0].id
    }
    return "NONE"
}

function Get-TaskById {
    param([string]$TaskId)
    $tasks = Get-Content "tasks.json" -Raw -Encoding UTF8 | ConvertFrom-Json
    return $tasks.tasks | Where-Object { $_.id -eq $TaskId }
}

# ===========================================
# Git状态检查
# ===========================================
function Get-GitChanges {
    if (Test-Path ".git") {
        $status = git status --porcelain 2>&1
        if ($status) {
            return ($status -split "`n").Count
        }
    }
    return 0
}

# ===========================================
# 主流程
# ===========================================
Log-Section "ScholarAI 自动化开发流程启动"

# 初始化统计
$pendingBefore = Get-PendingCount
$completedBefore = Get-CompletedCount
$totalTasks = Get-TotalTasks

Log-Info "项目目录: $PROJECT_ROOT"
Log-Info "当前状态: $completedBefore/$totalTasks 已完成, $pendingBefore 待处理"

if ($pendingBefore -eq 0) {
    Log-Warning "没有待处理的任务！脚本退出。"
    exit 0
}

# 计算循环次数
if ($Cycles -eq 0) {
    # 运行所有pending任务
    $actualCycles = $pendingBefore
    Log-Info "将执行 $actualCycles 次循环（处理所有pending任务）"
} else {
    # 运行指定次数，但不超过pending任务数
    $actualCycles = [Math]::Min($Cycles, $pendingBefore)
    Log-Info "将执行 $actualCycles 次循环（最多处理 $actualCycles 个pending任务）"
}

for ($i = 1; $i -le $actualCycles; $i++) {
    Log-Section "循环 $i/$actualCycles"

    # 检查pending任务
    $pendingCurrent = Get-PendingCount
    if ($pendingCurrent -eq 0) {
        Log-Success "所有任务已完成！"
        break
    }

    # 获取下一个任务
    $nextTask = Get-NextTask
    Log-Info "下一个任务: $nextTask"

    # 获取任务详情
    $taskDetails = Get-TaskById -TaskId $nextTask
    $taskTitle = $taskDetails.title
    $taskDesc = $taskDetails.description

    # 构建prompt内容
    $promptContent = @"
你现在是ScholarAI项目的开发助手。请执行以下流程：

1. 读取当前项目状态：
   - 查看progress.json了解历史工作
   - 查看tasks.json了解待办任务
   - 查看git log了解最近的提交

2. 选择并开始任务：$nextTask
   标题：$taskTitle
   描述：$taskDesc

3. 实现任务：
   - 根据任务的verification_steps实现功能
   - 编写测试代码
   - 运行测试确保通过

4. 提交更改：
   - 使用git add添加修改的文件
   - 使用git commit提交（遵循conventional commits格式）
   - 更新tasks.json，将任务状态改为"completed"
   - 更新progress.json，记录本次会话的工作

5. 输出总结：
   - 完成的任务ID和标题
   - 修改的文件列表
   - 测试结果
   - 项目整体进度（X/总数）

注意：
- 一次只完成一个任务，不要贪多
- 遇到不确定的地方，优先选择最简单的实现
- 确保代码可以运行后再提交
"@

    # 执行开发流程
    Log-Info "启动Claude Code进行开发..."

    try {
        # 使用 -p 模式传递prompt
        $promptContent | &claude -p --permission-mode acceptEdits 2>&1
        $exitCode = $LASTEXITCODE
    } catch {
        Log-Error "循环 $i 失败！Claude Code返回错误: $_"
        $exitCode = 1
    }

    if ($exitCode -eq 0) {
        Log-Success "循环 $i 完成"

        # 检查Git状态
        $gitChanges = Get-GitChanges
        if ($gitChanges -gt 0) {
            Log-Warning "检测到未提交的更改，请手动检查"
        }

        # 更新统计
        $completedNow = Get-CompletedCount
        $pendingNow = Get-PendingCount
        Log-Info "进度更新: $completedNow/$totalTasks 已完成, $pendingNow 待处理"
    } else {
        Log-Error "循环 $i 失败！Claude Code返回错误代码: $exitCode"

        # 询问是否继续
        $continue = Read-Host "是否继续下一个循环？[y/N]"
        if ($continue -ne "y" -and $continue -ne "Y") {
            Log-Warning "用户选择停止脚本"
            exit 1
        }
    }

    # 短暂等待
    if ($i -lt $actualCycles -and $pendingNow -gt 0) {
        Log-Info "等待3秒后继续..."
        Start-Sleep -Seconds 3
    }
}

# ===========================================
# 最终总结
# ===========================================
Log-Section "开发流程完成"

$completedAfter = Get-CompletedCount
$pendingAfter = Get-PendingCount

Log-Success "执行总结:"
Log-Info "  - 计划循环: $actualCycles 次"
Log-Info "  - 实际执行: $i 次"
Log-Info "  - 完成任务: $($completedAfter - $completedBefore) 个"
Log-Info "  - 当前进度: $completedAfter/$totalTasks"
Log-Info "  - 剩余任务: $pendingAfter"

if ($pendingAfter -gt 0) {
    Log-Info "还有 $pendingAfter 个任务待完成，可再次运行脚本"
} else {
    Log-Success "🎉 所有任务已完成！"
}
