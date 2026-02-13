# ScholarAI Automation Loop (English Only - No Chinese Characters)
# This version uses ASCII-only to avoid PowerShell encoding issues

param(
    [Parameter(Mandatory=$true)]
    [int]$MaxIterations
)

$ProjectDir = $PSScriptRoot
$CurrentIteration = 0
$LogDir = "$ProjectDir\Progress-Logs"

# Create log directory
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$LogFile = Join-Path $LogDir "auto-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ScholarAI Automation Loop - $MaxIterations Tasks" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project: $ProjectDir" -ForegroundColor Gray
Write-Host ""

while ($CurrentIteration -lt $MaxIterations) {
    $CurrentIteration++
    $iterationStart = Get-Date

    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host "  Iteration #$CurrentIteration / $MaxIterations" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host ""

    # Get task stats using Python
    $stats = python "$ProjectDir\get-task-stats.py"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to get task stats" -ForegroundColor Red
        break
    }

    $parts = $stats -split '\|'
    $total = $parts[0]
    $completed = $parts[1]
    $pending = $parts[2]
    $percentage = $parts[3]

    Write-Host "Total: $total | Completed: $completed | Pending: $pending ($percentage%)" -ForegroundColor Yellow
    Write-Host ""

    if ($pending -eq 0) {
        Write-Host "All tasks completed!" -ForegroundColor Green
        break
    }

    # Display info
    Write-Host "Starting Claude Code..." -ForegroundColor Blue
    Write-Host ""

    # Prepare prompt in memory
    $promptText = @"
You are now the development assistant for ScholarAI project.

IMPORTANT: Work on ONE task at a time. Follow this workflow:

1. Read $ProjectDir\tasks.json
2. Select ONE PENDING task (priority=1 first)
3. Update task status to 'in_progress'
4. Implement according to verification_steps
5. Use TDD: write tests first
6. Test your implementation
7. Commit to git with conventional format
8. Update task status to 'completed'
9. Add completed_at timestamp
10. Write session summary to Progress-Logs folder

Project directory: $ProjectDir

Current progress: $completed/$total tasks completed ($percentage%)

Start working now!
"@

    # Start Claude Code
    Write-Host "  Running: claude --yes < prompt-text" -ForegroundColor Gray
    Write-Host ""

    $process = Start-Process -FilePath "claude" -ArgumentList "--yes", $promptText -Wait -NoNewWindow -PassThru

    $iterationEnd = Get-Date
    $duration = $iterationEnd - $iterationStart
    $exitCode = $process.ExitCode

    if ($exitCode -eq 0) {
        $minutes = [int]$duration.TotalMinutes
        $seconds = $duration.Seconds

        Write-Host ("=" * 60) -ForegroundColor Green
        Write-Host "  SUCCESS ($minutes min $seconds sec)" -ForegroundColor Green
        Write-Host ("=" * 60) -ForegroundColor Green
        Write-Host ""
    } else {
        $minutes = [int]$duration.TotalMinutes
        $seconds = $duration.Seconds

        Write-Host ("=" * 60) -ForegroundColor Red
        Write-Host "  FAILED (Exit code: $exitCode)" -ForegroundColor Red
        Write-Host ("=" * 60) -ForegroundColor Red
        Write-Host ""
        Write-Host "Press Enter to continue or Ctrl+C to exit..."
        Read-Host
    }

    # Short pause
    Start-Sleep -Seconds 2
}

# Final summary
Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "  Automation Complete" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""
Write-Host "Total iterations: $CurrentIteration" -ForegroundColor Gray
Write-Host "End time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""
