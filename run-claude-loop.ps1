# ScholarAI 自��化 Claude Code 开发循环脚本 (PowerShell版本)
# 这个脚本会启动独立的 Claude Code 进程来完成任务

param(
    [Parameter(Mandatory=$true)]
    [int]$MaxIterations
)

# 初始化变量
$CurrentIteration = 0
$ProjectDir = $PSScriptRoot
$TasksFile = Join-Path $ProjectDir "tasks.json"
$ProgressLog = Join-Path $ProjectDir "claude-loop.log"
$SessionStart = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"

# 创建日志目录
$logDir = Join-Path $ProjectDir "Progress Log"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# 写入日志函数
function Write-Log {
    param(
        [string]$Level,
        [string]$Message,
        [string]$Color = "White"
    )
    $timestamp = Get-Date -Format "HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage -ForegroundColor $Color
    Add-Content -Path $ProgressLog -Value $logMessage
}

# 检查任务文件
if (-not (Test-Path $TasksFile)) {
    Write-Log "ERROR" "找不到 tasks.json" "Red"
    exit 1
}

# 获取未完成任务统计
function Get-PendingStats {
    try {
        $data = Get-Content $TasksFile -Raw -Encoding UTF8 | ConvertFrom-Json
        $pending = ($data.tasks | Where-Object { $_.status -eq "pending" | Measure-Object).Count
        $inProgress = ($data.tasks | Where-Object { $_.status -eq "in_progress" | Measure-Object).Count
        return "$pending|$inProgress"
    } catch {
        Write-Log "ERROR" "无法解析 tasks.json" "Red"
        return "0|0"
    }
}

# 获取任务摘要
function Get-TaskSummary {
    try {
        $data = Get-Content $TasksFile -Raw -Encoding UTF8 | ConvertFrom-Json
        $total = $data.tasks.Count
        $completed = ($data.tasks | Where-Object { $_.status -eq "completed" | Measure-Object).Count
        $pending = ($data.tasks | Where-Object { $_.status -eq "pending" | Measure-Object).Count
        $percentage = if ($total -gt 0) { [math]::Round(($completed / $total) * 100) } else { 0 }
        return "$total|$completed|$pending|$percentage"
    } catch {
        return "0|0|0|0"
    }
}

# 创建Claude提示词文件
$ClaudePromptFile = Join-Path $ProjectDir "claude-prompt.txt"

@"
你现在是ScholarAI项目的开发助手。请严格按照以下流程工作：

## 第一步：获取上下文
1. 读取 $ProjectDir\CLAUDE.md 了解开发工作流程
2. 读取 $ProjectDir\tasks.json 查看所有任务
3. 运行以下命令查看最近的工作：
   cd $ProjectDir
   git log --oneline -5

4. 运行以下命令查看当前分支和状态：
   cd $ProjectDir
   git status

## 第二步：选择任务
5. 从 tasks.json 中选择一个**未完成的任务**来执行
   - 优先选择 priority=1 的任务
   - 跳过所有 status='completed' 的任务
   - 如果有 status='in_progress' 的任务，继续完成它
   - 更新任务的 status 为 'in_progress'

## 第三步：实现功能
6. 按照任务的 verification_steps 逐步实现
7. 使用 TDD 方法：先写测试，再实现功能
8. 如果需要，启动开发服务器测试：
   - 后端: cd $ProjectDir\backend && python run.py
   - 前端: cd $ProjectDir\frontend && npm run dev

## 第四步：测试和提交
9. 完成后进行端到端测试
10. 更新 tasks.json：
    - 将完成的任务 status 改为 'completed'
    - 添加 completed_at 时间戳（ISO 8601格式）
    - 更新 session_id

11. 提交代码到 Git：
    - git add 所有修改的文件
    - 使用规范的 commit message
    - 格式: <type>: <description>
    - 类型: feat, fix, refactor, docs, test, chore

## 第五步：会话总结
12. 将本次会话的总结写入到 Progress Log 文件夹
13. 文件名格式: task-<任务编号>-<简短标题>.md
14. 内容包括：
    - 完成的任务编号和标题
    - 修改的文件列表
    - 实现的主要功能
    - 测试结果和验证
    - 遇到的问题和解决方案

**重要规则**：
- ✅ 每次只完成一个任务
- ✅ 代码必须能正常运行，不要留下半成品
- ✅ 提交前确保没有 console.log 或调试代码
- ✅ 遵循项目的编码规范（见 CLAUDE.md）
- ✅ 完成后必须更新 tasks.json

**项目技术栈**：
- 前端: React 18 + TypeScript + Vite 6
- 后端: Python Flask + MongoDB
- 当前会话ID: session-$(Get-Date -Format 'yyyy-MM-dd')-XXX
- 项目目录: $ProjectDir

现在开始工作！选择一个未完成的任务并完成它。
"@ | Out-File -FilePath $ClaudePromptFile -Encoding UTF8

# 主循环
while ($CurrentIteration -lt $MaxIterations) {
    $CurrentIteration++
    $sessionId = "session-$(Get-Date -Format 'yyyy-MM-dd')-$($CurrentIteration.ToString('000'))"

    Write-Host ""
    $separator = "=" * 60
    Write-Host $separator -ForegroundColor Cyan
    Write-Log "INFO" "Claude Code 迭代 #$CurrentIteration / $MaxIterations" "Cyan"
    Write-Host $separator -ForegroundColor Cyan

    # 检查未完成任务
    $stats = Get-PendingStats
    $pendingCount = ($stats -split '\|')[0]
    $inProgressCount = ($stats -split '\|')[1]

    Write-Log "INFO" "未完成: $pendingCount | 进行中: $inProgressCount" "Yellow"

    if ($pendingCount -eq 0) {
        Write-Log "SUCCESS" "所有任务已完成！" "Green"
        Write-Host "🎉 恭喜！所有任务已完成！" -ForegroundColor Green
        break
    }

    # 获取总体进度
    $summary = Get-TaskSummary
    $total = ($summary -split '\|')[0]
    $completed = ($summary -split '\|')[1]
    $percentage = ($summary -split '\|')[3]

    Write-Log "INFO" "总进度: $completed/$total ($percentage%)"

    # 记录开始时间
    $iterationStart = Get-Date

    # 显示即将执行的信息
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Blue
    Write-Log "INFO" "即将启动 Claude Code..."
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host "  即将启动 Claude Code 进程..." -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host ""
    Write-Host "  提示词预览:" -ForegroundColor Yellow
    Write-Host "  → 从 tasks.json 选择未完成任务" -ForegroundColor Gray
    Write-Host "  → 按照开发流程实现功能" -ForegroundColor Gray
    Write-Host "  → 提交代码并更新任务状态" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Claude Code 将在新窗口/进程中运行" -ForegroundColor Cyan
    Write-Host "  当前窗口仅显示日志，不会交互" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "按 Enter 键启动 Claude Code (或 Ctrl+C 退出)..."

    # 执行Claude Code
    Write-Log "INFO" "执行中..."

    # 使用 Start-Process 启动独立的 Claude Code 进程
    # -Wait 参数会等待进程完成
    $processInfo = Start-Process -FilePath "claude" -ArgumentList "--yes", $ClaudePromptFile -Wait -PassThru -NoNewWindow

    $iterationEnd = Get-Date
    $duration = $iterationEnd - $iterationStart
    $minutes = [int]$duration.TotalMinutes
    $seconds = $duration.Seconds

    if ($processInfo.ExitCode -eq 0) {
        Write-Log "SUCCESS" "迭代完成 (耗时: ${minutes}分${seconds}秒)" "Green"
        Write-Host ""
        Write-Host ("=" * 60) -ForegroundColor Green
        Write-Host "✓ 迭代 #$CurrentIteration 完成" -ForegroundColor Green
        Write-Host "  耗时: ${minutes}分${seconds}秒" -ForegroundColor Green
        Write-Host ("=" * 60) -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Log "ERROR" "迭代失败 (耗时: ${minutes}分${seconds}秒)" "Red"
        Write-Host ""
        Write-Host ("=" * 60) -ForegroundColor Red
        Write-Host "✗ Claude Code 执行出错" -ForegroundColor Red
        Write-Host "  耗时: ${minutes}分${seconds}秒" -ForegroundColor Red
        Write-Host ("=" * 60) -ForegroundColor Red
        Write-Host "" | tee -a "$ProgressLog"

        # 询问是否继续
        $continue = Read-Host "是否继续下一次迭代? (y/n)"
        if ($continue -ne "y") {
            Write-Log "INFO" "用户中断执行" "Yellow"
            break
        }
    }

    # 短暂暂停
    Start-Sleep -Seconds 2

    # 检查是否应该继续
    if ($CurrentIteration -ge $MaxIterations) {
        Write-Log "INFO" "达到最大迭代次数"
        break
    }
}

# 最终总结
Write-Host ""
$separator = "=" * 60
Write-Host $separator -ForegroundColor Cyan
Write-Log "INFO" "开发循环结束" "Cyan"
Write-Host $separator -ForegroundColor Cyan
"总迭代次数: $CurrentIteration" | Out-File -FilePath $ProgressLog -Append -Encoding UTF8
"结束时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -FilePath $ProgressLog -Append -Encoding UTF8

Write-Host "总迭代次数: $CurrentIteration"
Write-Host "结束时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# 显示最终任务状态
$finalStats = Get-PendingStats
$finalPending = ($finalStats -split '\|')[0]
"剩余未完成任务: $finalPending" | Out-File -FilePath $ProgressLog -Append -Encoding UTF8

Write-Host "剩余未完成任务: $finalPending"

if ($finalPending -eq 0) {
    Write-Host "✅ 所有任务已完成！" -ForegroundColor Green
} else {
    Write-Host "⚠️  还有 $finalPending 个任务待完成" -ForegroundColor Yellow
}

Write-Host "详细日志: $ProgressLog" -ForegroundColor Gray
Write-Host $separator -ForegroundColor Cyan
Write-Host ""
Write-Host "提示: 使用 'python check-progress.py' 查看最新进度" -ForegroundColor Cyan
Write-Host ""
