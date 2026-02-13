# ScholarAI 进度查看脚本 (PowerShell版本)

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

$ProjectDir = $PSScriptRoot
$TasksFile = Join-Path $ProjectDir "tasks.json"

# 检查任务文件
if (-not (Test-Path $TasksFile)) {
    Write-ColorOutput "错误: 找不到 tasks.json" "Red"
    exit 1
}

# 读取任务数据
try {
    $json = Get-Content $TasksFile -Raw -Encoding UTF8 | ConvertFrom-Json
} catch {
    Write-ColorOutput "错误: 无法解析 tasks.json" "Red"
    exit 1
}

# 统计任务
$allTasks = $json.tasks
$completedTasks = $allTasks | Where-Object { $_.status -eq "completed" }
$inProgressTasks = $allTasks | Where-Object { $_.status -eq "in_progress" }
$pendingTasks = $allTasks | Where-Object { $_.status -eq "pending" }

# 计算百分比
$total = $allTasks.Count
$completed = $completedTasks.Count
$pending = $pendingTasks.Count
$percentage = if ($total -gt 0) { [math]::Round(($completed / $total) * 100) } else { 0 }

# 显示标题
Write-Host ""
$separator = "=" * 60
Write-ColorOutput $separator "Cyan"
Write-ColorOutput "  ScholarAI 项目进度报告" "Cyan"
Write-ColorOutput $separator "Cyan"
Write-Host ""

# 显示总体进度
Write-ColorOutput "📊 总体进度" "Yellow"
Write-Host ("  总任务数:    {0}" -f $total)
Write-Host ("  已完成:      {0} 个" -f $completed) -ForegroundColor Green
Write-Host ("  进行中:      {0} 个" -f $inProgressTasks.Count) -ForegroundColor Yellow
Write-Host ("  待办:        {0} 个" -f $pending) -ForegroundColor Gray
Write-Host ""

# 进度条
$progressWidth = 50
$filled = [math]::Round(($completed / $total) * $progressWidth)
$empty = $progressWidth - $filled
$progressBar = "█" * $filled + "░" * $empty
Write-Host ("  进度:        [{0}] {1}%" -f $progressBar, $percentage)
Write-Host ""

# 显示进行中的任务
if ($inProgressTasks.Count -gt 0) {
    Write-ColorOutput "🔄 进行中的任务" "Yellow"
    foreach ($task in $inProgressTasks) {
        Write-Host ("  {0} | {1}" -f $task.id, $task.title)
        Write-Host ("    类别: {0}, 优先级: {1}" -f $task.category, $task.priority) -ForegroundColor Gray
    }
    Write-Host ""
}

# 显示最近的已完成任务（最多5个）
$recentCompleted = $completedTasks |
    Sort-Object { $_.completed_at } -Descending |
    Select-Object -First 5

if ($recentCompleted.Count -gt 0) {
    Write-ColorOutput "✅ 最近的已完成任务 (最多5个)" "Green"
    foreach ($task in $recentCompleted) {
        $time = if ($task.completed_at) {
            $dt = [DateTime]::Parse($task.completed_at)
            $dt.ToString("MM-dd HH:mm")
        } else { "未知" }
        Write-Host ("  {0} | {1}" -f $task.id, $task.title)
        Write-Host ("    完成时间: {0}" -f $time) -ForegroundColor Gray
    }
    Write-Host ""
}

# 显示下一个待办��务（按优先级）
$nextPending = $pendingTasks |
    Sort-Object { $_.priority }, { $_.id } |
    Select-Object -First 5

if ($nextPending.Count -gt 0) {
    Write-ColorOutput "📋 下一个待办任务 (按优先级)" "Cyan"
    foreach ($task in $nextPending) {
        Write-Host ("  {0} | {1}" -f $task.id, $task.title)
        Write-Host ("    类别: {0}, 优先级: {1}" -f $task.category, $task.priority) -ForegroundColor Gray
    }
    Write-Host ""
}

# Git状态（如果在git仓库中）
if (Test-Path (Join-Path $ProjectDir ".git")) {
    Write-ColorOutput "🔧 Git 状态" "Gray"

    Push-Location $ProjectDir
    try {
        # 最近5次提交
        $commits = git log --oneline -5 2>$null
        if ($commits) {
            Write-Host "  最近5次提交:"
            $commits | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
        }

        # 当前分支
        $branch = git branch --show-current 2>$null
        if ($branch) {
            Write-Host ("  当前分支: {0}" -f $branch)
        }

        # 未提交更改
        $status = git status --short 2>$null
        if ($status) {
            Write-Host "  未提交更改:" -ForegroundColor Yellow
            $status | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
        } else {
            Write-Host "  工作目录干净" -ForegroundColor Green
        }
    } finally {
        Pop-Location
    }
    Write-Host ""
}

Write-ColorOutput $separator "Cyan"
Write-ColorOutput "  完成度: $percentage%" $(if ($percentage -ge 80) { "Green" } elseif ($percentage -ge 50) { "Yellow" } else { "Red" })
Write-ColorOutput $separator "Cyan"
Write-Host ""
