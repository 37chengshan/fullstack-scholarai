# ScholarAI 自动化开发循环（非交互版）
# 使用英文提示词，自动输入y，完全自动化

param(
    [Parameter(Mandatory=$true)]
    [int]$MaxIterations
)

$ProjectDir = $PSScriptRoot
$CurrentIteration = 0
$LogDir = "$ProjectDir\Progress-Logs"

# 创建日志目录
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$LogFile = Join-Path $LogDir "automation-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "  ScholarAI 自动化开发循环（非交互版）" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""
Write-Host "  计划迭代次数: $MaxIterations" -ForegroundColor Yellow
Write-Host "  项目目录: $ProjectDir" -ForegroundColor Gray
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "  完全自动化模式 - 无需手动输入" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

# 主循环
while ($CurrentIteration -lt $MaxIterations) {
    $CurrentIteration++

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    Add-Content -Path $LogFile -Value "========================================="
    Add-Content -Path $LogFile -Value "Iteration #$CurrentIteration / $MaxIterations"
    Add-Content -Path $LogFile -Value "Time: $timestamp"
    Add-Content -Path $LogFile -Value "========================================="

    Write-Host ""
    $separator = "  " + "=" * 58
    Write-Host $separator -ForegroundColor Cyan
    Write-Host "    迭代 #$CurrentIteration / $MaxIterations" -ForegroundColor Cyan
    Write-Host $separator -ForegroundColor Cyan

    # 获取任务统计
    $stats = python "$ProjectDir\get-task-stats.py"
    if ($LASTEXITCODE -ne 0) {
        Add-Content -Path $LogFile -Value "ERROR: Failed to get task stats"
        Write-Host "    获取任务统计失败" -ForegroundColor Red
        break
    }

    $parts = $stats -split '\|'
    $total = $parts[0]
    $completed = $parts[1]
    $pending = $parts[2]
    $percentage = $parts[3]

    Add-Content -Path $LogFile -Value "Total: $total, Completed: $completed, Pending: $pending ($percentage%)"
    Write-Host "    总任务: $total | 已完成: $completed | 待办: $pending ($percentage%)" -ForegroundColor Yellow
    Write-Host ""

    if ($pending -eq 0) {
        Add-Content -Path $LogFile -Value "SUCCESS: All tasks completed!"
        Write-Host "    ✅ 所有任务已完成！" -ForegroundColor Green
        Write-Host ""
        break
    }

    # 显示即将执行的操作
    Add-Content -Path $LogFile -Value "Starting Claude Code..."

    Write-Host "    即将启动 Claude Code..." -ForegroundColor Blue
    Write-Host "    会话ID: session-$(Get-Date -Format 'yyyy-MM-dd')-$($CurrentIteration.ToString('000'))" -ForegroundColor Gray

    # 准备提示词（使用英文版本）
    $promptFile = "$ProjectDir\claude-prompt-en.txt"
    if (-not (Test-Path $promptFile)) {
        Add-Content -Path $LogFile -Value "ERROR: Prompt file not found"
        break
    }

    $prompt = Get-Content $promptFile -Raw

    # 添加项目目录和会话ID到提示词
    $prompt = $prompt -replace "<PROJECT_DIR>", $ProjectDir
    $prompt = $prompt -replace "<SESSION_ID>", "session-$(Get-Date -Format 'yyyy-MM-dd')-$($CurrentIteration.ToString('000'))"

    # 启动Claude Code（自动回答y）
    $env:CLAUDE_PROJECT_DIR = $ProjectDir

    Add-Content -Path $LogFile -Value "Executing: claude --yes < prompt.txt"

    $process = Start-Process -FilePath "claude" -ArgumentList "--yes", $promptFile -Wait -NoNewWindow -PassThru -RedirectStandardInput "nul"

    $exitCode = $process.ExitCode
    $duration = (Get-Date) - $process.StartTime

    Add-Content -Path $LogFile -Value "Exit code: $exitCode"

    if ($exitCode -eq 0) {
        Add-Content -Path $LogFile -Value "Result: SUCCESS"
        $durationMsg = "Completed in $($duration.TotalMinutes) minutes"
        Write-Host "    ✓ 迭代完成 (耗时: $durationMsg)" -ForegroundColor Green
    } else {
        Add-Content -Path $LogFile -Value "Result: FAILED"
        $durationMsg = "Failed after $($duration.TotalMinutes) minutes"
        Write-Host "    ✗ 迭代失败 (退出码: $exitCode, 耗时: $durationMsg)" -ForegroundColor Red
        Add-Content -Path $LogFile -Value "ERROR: Claude Code failed with exit code $exitCode"
        Write-Host "    Claude Code执行失败，将重试..." -ForegroundColor Yellow
    }

    Add-Content -Path $LogFile -Value ""
    Write-Host ""

    # 短暂暂停
    Start-Sleep -Seconds 2
}

# 最终总结
Add-Content -Path $LogFile -Value ""
Add-Content -Path $LogFile -Value "========================================="
Add-Content -Path $LogFile -Value "Automation Loop Completed"
Add-Content -Path $LogFile -Value "Total iterations: $CurrentIteration"
Add-Content -Path $LogFile -Value "End time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Content -Path $LogFile -Value "========================================="

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "  开发循环结束" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""
Write-Host "  总迭代次数: $CurrentIteration" -ForegroundColor Gray
Write-Host ""

# 显示最终任务状态
$finalStats = python "$ProjectDir\get-task-stats.py"
if ($LASTEXITCODE -eq 0) {
    $parts = $finalStats -split '\|'
    $finalPending = $parts[2]
    "剩余未完成任务: $finalPending" | Out-File -FilePath $LogFile -Append -Encoding UTF8

    if ($finalPending -eq 0) {
        Write-Host "✅ 所有任务已完成！" -ForegroundColor Green
    } else {
        Write-Host "⚠️  还有 $finalPending 个任务待完成" -ForegroundColor Yellow
    }
} else {
    Write-Host "获取最终任务统计失败" -ForegroundColor Red
}

Write-Host ""
Write-Host "日志文件: $LogFile" -ForegroundColor Gray
Write-Host "提示: 使用 python check-progress.py 查看最新进度" -ForegroundColor Cyan
Write-Host ""
