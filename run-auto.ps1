# ScholarAI 自动化开发循环
# 使用Python辅助，避免PowerShell兼容性问题

param(
    [Parameter(Mandatory=$true)]
    [int]$MaxIterations
)

$ProjectDir = $PSScriptRoot
$CurrentIteration = 0

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "  ScholarAI 自动化开发循环" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""
Write-Host "  计划迭代次数: $MaxIterations" -ForegroundColor Yellow
Write-Host "  项目目录: $ProjectDir" -ForegroundColor Gray
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

# 主循环
while ($CurrentIteration -lt $MaxIterations) {
    $CurrentIteration++

    Write-Host "  迭代 #$CurrentIteration / $MaxIterations" -ForegroundColor Cyan
    Write-Host ""

    # 获取任务统计
    $stats = python "$ProjectDir\get-task-stats.py"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  获取任务统计失败" -ForegroundColor Red
        break
    }

    $parts = $stats -split '\|'
    $total = $parts[0]
    $completed = $parts[1]
    $pending = $parts[2]
    $percentage = $parts[3]

    Write-Host "  总任务: $total | 已完成: $completed | 待办: $pending ($percentage%)" -ForegroundColor Yellow
    Write-Host ""

    if ($pending -eq 0) {
        Write-Host "  ✅ 所有任务已完成！" -ForegroundColor Green
        break
    }

    # 显示提示
    Write-Host "  即将启动 Claude Code..." -ForegroundColor Blue
    Write-Host "  按 Enter 键继续..."
    Read-Host

    # 准备提示词（从文件读取，避免中文编码问题）
    $prompt = Get-Content "$ProjectDir\claude-prompt-en.txt" -Raw

    # 启动Claude Code
    $env:CLAUDE_PROJECT_DIR = $ProjectDir

    $process = Start-Process -FilePath "claude" -ArgumentList $prompt -Wait -NoNewWindow -PassThru

    $exitCode = $process.ExitCode

    if ($exitCode -eq 0) {
        Write-Host "  ✓ 迭代完成" -ForegroundColor Green
    } else {
        Write-Host "  ✗ 迭代失败 (退出码: $exitCode)" -ForegroundColor Red
        Write-Host ""
        $continue = Read-Host "是否继续? (y/n)"
        if ($continue -ne 'y') {
            break
        }
    }

    Start-Sleep -Seconds 1
    Write-Host ""
}

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "  开发循环结束" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""
Write-Host "  总迭代次数: $CurrentIteration" -ForegroundColor Gray
Write-Host ""
Write-Host "提示: 使用 python check-progress.py 查看最新进度" -ForegroundColor Cyan
Write-Host ""
