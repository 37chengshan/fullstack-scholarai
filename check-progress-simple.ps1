# ScholarAI Progress Checker (Simple Version)
# Usage: .\check-progress-simple.ps1

$ProjectDir = $PSScriptRoot
$TasksFile = Join-Path $ProjectDir "tasks.json"

# Check tasks file
if (-not (Test-Path $TasksFile)) {
    Write-Host "Error: tasks.json not found" -ForegroundColor Red
    exit 1
}

# Read tasks
try {
    $json = Get-Content $TasksFile -Raw | ConvertFrom-Json
} catch {
    Write-Host "Error: Cannot parse tasks.json" -ForegroundColor Red
    exit 1
}

# Count tasks
$allTasks = $json.tasks
$completedTasks = $allTasks | Where-Object { $_.status -eq "completed" }
$inProgressTasks = $allTasks | Where-Object { $_.status -eq "in_progress" }
$pendingTasks = $allTasks | Where-Object { $_.status -eq "pending" }

# Calculate percentage
$total = $allTasks.Count
$completed = $completedTasks.Count
$pending = $pendingTasks.Count
$percentage = if ($total -gt 0) { [math]::Round(($completed / $total) * 100) } else { 0 }

# Display header
Write-Host ""
$separator = "=" * 60
Write-Host $separator -ForegroundColor Cyan
Write-Host "  ScholarAI Project Progress" -ForegroundColor Cyan
Write-Host $separator -ForegroundColor Cyan
Write-Host ""

# Display overall progress
Write-Host "Overall Progress:" -ForegroundColor Yellow
Write-Host "  Total tasks:     $total"
Write-Host "  Completed:       $completed" -ForegroundColor Green
Write-Host "  In progress:     $($inProgressTasks.Count)" -ForegroundColor Yellow
Write-Host "  Pending:         $pending" -ForegroundColor Gray
Write-Host ""

# Progress bar
$progressWidth = 50
$filled = [math]::Round(($completed / $total) * $progressWidth)
$empty = $progressWidth - $filled
$progressBar = "#" * $filled + "-" * $empty
Write-Host "  Progress:        [$progressBar] $percentage%"
Write-Host ""

# Next pending tasks (by priority)
$nextPending = $pendingTasks |
    Sort-Object { $_.priority }, { $_.id } |
    Select-Object -First 5

if ($nextPending.Count -gt 0) {
    Write-Host "Next Pending Tasks (by priority):" -ForegroundColor Cyan
    foreach ($task in $nextPending) {
        Write-Host "  $($task.id) | $($task.title)"
        Write-Host "    Category: $($task.category), Priority: $($task.priority)" -ForegroundColor Gray
    }
    Write-Host ""
}

# Recent completed tasks (last 5)
$recentCompleted = $completedTasks |
    Sort-Object { $_.completed_at } -Descending |
    Select-Object -First 5

if ($recentCompleted.Count -gt 0) {
    Write-Host "Recently Completed (last 5):" -ForegroundColor Green
    foreach ($task in $recentCompleted) {
        $time = if ($task.completed_at) {
            $dt = [DateTime]::Parse($task.completed_at)
            $dt.ToString("MM-dd HH:mm")
        } else { "Unknown" }
        Write-Host "  $($task.id) | $($task.title)"
        Write-Host "    Completed: $time" -ForegroundColor Gray
    }
    Write-Host ""
}

# Git status (if in git repo)
if (Test-Path (Join-Path $ProjectDir ".git")) {
    Write-Host "Git Status:" -ForegroundColor Gray

    Push-Location $ProjectDir
    try {
        # Recent commits
        $commits = git log --oneline -5 2>$null
        if ($commits) {
            Write-Host "  Recent 5 commits:"
            $commits | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
        }

        # Current branch
        $branch = git branch --show-current 2>$null
        if ($branch) {
            Write-Host "  Current branch: $branch"
        }

        # Uncommitted changes
        $status = git status --short 2>$null
        if ($status) {
            Write-Host "  Uncommitted changes:" -ForegroundColor Yellow
            $status | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
        } else {
            Write-Host "  Working directory clean" -ForegroundColor Green
        }
    } finally {
        Pop-Location
    }
    Write-Host ""
}

Write-Host $separator -ForegroundColor Cyan

# Color based on completion
if ($percentage -ge 80) {
    Write-Host "  Completion: $percentage%" -ForegroundColor Green
} elseif ($percentage -ge 50) {
    Write-Host "  Completion: $percentage%" -ForegroundColor Yellow
} else {
    Write-Host "  Completion: $percentage%" -ForegroundColor Red
}

Write-Host $separator -ForegroundColor Cyan
Write-Host ""
