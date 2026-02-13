# ScholarAI 自动化开发循环脚本 (简化版)
# 使用Python处理JSON，避免PowerShell兼容性问题

param(
    [Parameter(Mandatory=$true)]
    [int]$MaxIterations
)

$ProjectDir = $PSScriptRoot
$ProgressLog = Join-Path $ProjectDir "claude-simple.log"
$CurrentIteration = 0

# 创建进度日志目录
$logDir = Join-Path $ProjectDir "Progress-Logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# 写入日志函数
function Write-Log {
    param(
        [string]$Level,
        [string]$Message
    )
    $timestamp = Get-Date -Format "HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path $ProgressLog -Value $logMessage
}

# 初始化
Write-Log "INFO" "========================================"
Write-Log "INFO" "ScholarAI 自动化开发循环启动"
Write-Log "INFO" "项目目录: $ProjectDir"
Write-Log "INFO" "计划迭代次数: $MaxIterations"
Write-Log "INFO" "========================================"

# 使用Python获取任务统计
function Get-TaskStats {
    $pythonCode = @"
import json
import sys
try:
    with open('tasks.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    total = len(data['tasks'])
    completed = sum(1 for t in data['tasks'] if t['status'] == 'completed')
    pending = sum(1 for t in data['tasks'] if t['status'] == 'pending')
    in_progress = sum(1 for t in data['tasks'] if t['status'] == 'in_progress')
    percentage = int(completed / total * 100) if total > 0 else 0
    print(f'{total}|{completed}|{pending}|{percentage}')
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
"@
    $result = python -c $pythonCode
    if ($LASTEXITCODE -eq 0) {
        return $result
    } else {
        Write-Log "ERROR" "获取任务统计失败: $result"
        return "0|0|0|0"
    }
}

# 主循环
while ($CurrentIteration -lt $MaxIterations) {
    $CurrentIteration++
    $sessionId = "session-$(Get-Date -Format 'yyyy-MM-dd')-$($CurrentIteration.ToString('000'))"

    Write-Host ""
    $separator = "=" * 60
    Write-Host $separator -ForegroundColor Cyan
    Write-Log "INFO" "迭代 #$CurrentIteration / $MaxIterations"
    Write-Host $separator -ForegroundColor Cyan

    # 获取任务统计
    $stats = Get-TaskStats
    $total = ($stats -split '\|')[0]
    $completed = ($stats -split '\|')[1]
    $pending = ($stats -split '\|')[2]
    $percentage = ($stats -split '\|')[3]

    Write-Log "INFO" "总任务: $total, 已完成: $completed, 待办: $pending ($percentage%)"

    if ($pending -eq 0) {
        Write-Log "SUCCESS" "所有任务已完成！"
        Write-Host "🎉 恭喜！所有任务已完成！" -ForegroundColor Green
        break
    }

    # 显示即将执行的命令
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Blue
    Write-Log "INFO" "即将启动 Claude Code..."
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host "  即将启动 Claude Code 进程..." -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
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

    # 记录开始时间
    $iterationStart = Get-Date

    # 调用 Claude Code
    Write-Log "INFO" "执行中..."

    # 构建Claude提示词
    $prompt = @"
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
    - 添加 completed_at 时间戳
    - 更新 session_id

11. 提交代码到 Git：
    - git add 所有修改的文件
    - 使用规范的 commit message
    - 格式: <type>: <description>
    - 类型: feat, fix, refactor, docs, test, chore

## 第五步：会话总结
12. 将本次会话的总结写入到 Progress-Logs 文件夹
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
- 当前会话ID: $sessionId
- 项目目录: $ProjectDir

现在开始工作！选择一个未完成的任务并完成它。
"@

    # 启动 Claude Code（在新窗口）
    $processInfo = Start-Process -FilePath "claude" -ArgumentList @($prompt) -Wait -NoNewWindow -PassThru

    $iterationEnd = Get-Date
    $duration = $iterationEnd - $iterationStart
    $minutes = [int]$duration.TotalMinutes
    $seconds = $duration.Seconds

    if ($processInfo.ExitCode -eq 0) {
        Write-Log "SUCCESS" "迭代完成 (耗时: ${minutes}分${seconds}秒)"
        Write-Host ""
        Write-Host ("=" * 60) -ForegroundColor Green
        Write-Host "✓ 迭代 #$CurrentIteration 完成" -ForegroundColor Green
        Write-Host "  耗时: ${minutes}分${seconds}秒" -ForegroundColor Green
        Write-Host ("=" * 60) -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Log "ERROR" "迭代失败 (耗时: ${minutes}分${seconds}秒)"
        Write-Host ""
        Write-Host ("=" * 60) -ForegroundColor Red
        Write-Host "✗ Claude Code 执行出错" -ForegroundColor Red
        Write-Host "  耗时: ${minutes}分${seconds}秒" -ForegroundColor Red
        Write-Host ("=" * 60) -ForegroundColor Red
        Write-Host "" | tee -a "$ProgressLog"

        # 询问是否继续
        $continue = Read-Host "是否继续下一次迭代? (y/n)"
        if ($continue -ne "y") {
            Write-Log "INFO" "用户中断执行"
            break
        }
    }

    # 短暂暂停
    Start-Sleep -Seconds 2
}

# 最终总结
Write-Host ""
$separator = "=" * 60
Write-Host $separator -ForegroundColor Cyan
Write-Log "INFO" "开发循环结束"
Write-Host $separator -ForegroundColor Cyan
"总迭代次数: $CurrentIteration" | Out-File -FilePath $ProgressLog -Append -Encoding UTF8
"结束时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -FilePath $ProgressLog -Append -Encoding UTF8

Write-Host "总迭代次数: $CurrentIteration"
Write-Host "结束时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# 显示最终任务状态
$finalStats = Get-TaskStats
$finalPending = ($finalStats -split '\|')[2]
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
