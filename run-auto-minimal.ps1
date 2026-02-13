# ScholarAI Auto-Dev Loop (Minimal Version)
# Simplified to avoid PowerShell encoding issues

$ProjectDir = "D:\ai\fullstack-merged"
$MaxIterations = 19
$CurrentIteration = 0

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ScholarAI Automation - 19 Tasks" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Project: $ProjectDir" -ForegroundColor Gray
Write-Host ""

while ($CurrentIteration -lt $MaxIterations) {
    $CurrentIteration++
    $iterationStart = Get-Date

    Write-Host "  Iteration #$CurrentIteration / $MaxIterations" -ForegroundColor Cyan
    Write-Host ""

    # Get task stats
    $stats = python "$ProjectDir\get-task-stats.py"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Failed to get stats" -ForegroundColor Red
        break
    }

    $parts = $stats -split '\|'
    $total = $parts[0]
    $completed = $parts[1]
    $pending = $parts[2]
    $percentage = $parts[3]

    Write-Host "  Total: $total | Completed: $completed | Pending: $pending ($percentage%)" -ForegroundColor Yellow
    Write-Host ""

    if ($pending -eq 0) {
        Write-Host "  All tasks completed!" -ForegroundColor Green
        break
    }

    Write-Host "  Starting Claude Code..." -ForegroundColor Blue
    Write-Host ""

    # Start Claude Code (use English prompt file)
    $env:CLAUDE_PROJECT_DIR = $ProjectDir
    $process = Start-Process -FilePath "claude" -ArgumentList "$ProjectDir\claude-prompt-en.txt" -Wait -NoNewWindow -PassThru

    $duration = (Get-Date) - $iterationStart
    $minutes = [int]$duration.TotalMinutes

    if ($process.ExitCode -eq 0) {
        Write-Host "  SUCCESS (${minutes}m $duration.Seconds s)" -ForegroundColor Green
    } else {
        Write-Host "  FAILED (Exit: $($process.ExitCode))" -ForegroundColor Red
        $continue = Read-Host "Continue? (y/n)"
        if ($continue -ne "y") { break }
    }

    Start-Sleep -Seconds 1
    Write-Host ""
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Complete: $CurrentIteration iterations" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Remaining tasks: $pending" -ForegroundColor Gray
Write-Host ""
