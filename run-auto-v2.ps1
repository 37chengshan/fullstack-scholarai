# ScholarAI Auto-Dev Loop - Fully Automated
# Based on working version with Read-Host removed

param(
    [Parameter(Mandatory=$true)]
    [int]$MaxIterations
)

$ProjectDir = "D:\ai\fullstack-merged"
$CurrentIteration = 0

Write-Host ""
$separator = "=" * 60
Write-Host $separator -ForegroundColor Cyan
Write-Host "  ScholarAI Automation - $MaxIterations Tasks"
Write-Host $separator -ForegroundColor Cyan
Write-Host ""
Write-Host "  Mode: Unattended (Auto-Yes)" -ForegroundColor Green
Write-Host "  Project: $ProjectDir" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================"

while ($CurrentIteration -lt $MaxIterations) {
    $CurrentIteration++

    Write-Host "  Iteration: $CurrentIteration / $MaxIterations"
    Write-Host "  Time: $(Get-Date -Format 'HH:mm:ss')"
    Write-Host ""

    # Get task stats
    $stats = python "$ProjectDir\get-task-stats.py"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Failed to get stats"
        break
    }

    $parts = $stats -split '\|'
    $total = $parts[0]
    $completed = $parts[1]
    $pending = $parts[2]
    $percentage = $parts[3]

    Write-Host "  Total: $total | Completed: $completed | Pending: $pending ($percentage%)"

    if ($pending -eq 0) {
        Write-Host "  All tasks completed!"
        Write-Host ""
        break
    }

    Write-Host ""
    Write-Host "Starting Claude Code..." -ForegroundColor Blue
    Write-Host ""

    $env:CLAUDE_PROJECT_DIR = $ProjectDir

    # Run Claude directly (method from working version)
    $process = Start-Process -FilePath "claude" -ArgumentList "-p", (Get-Content "$ProjectDir\claude-prompt-en.txt" -Raw), "--print", "--dangerously-skip-permissions" -Wait -NoNewWindow -PassThru

    $exitCode = $process.ExitCode

    $iterationEnd = Get-Date
    $duration = $iterationEnd - $iterationStart
    $minutes = [int]($duration.TotalSeconds / 60)
    $seconds = [int]$duration.TotalSeconds % 60

    if ($exitCode -eq 0) {
        Write-Host "  SUCCESS (${minutes}m ${seconds}s)" -ForegroundColor Green
    } else {
        Write-Host "  FAILED (Exit code: $exitCode)" -ForegroundColor Red
    }

    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host $separator -ForegroundColor Cyan
Write-Host "  Automation Complete"
Write-Host $separator -ForegroundColor Cyan
Write-Host ""
Write-Host "  Total iterations: $CurrentIteration" -ForegroundColor Gray
Write-Host ""
