# ScholarAI Auto-Dev Loop - Fixed Version
# Uses batch wrapper to avoid PowerShell argument issues

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

# Create wrapper batch file
$wrapperBat = @"
@echo off
set CLAUDE_PROJECT_DIR=D:\ai\fullstack-merged
type auto-prompt-current.txt | claude --print --dangerously-skip-permissions
"@

$wrapperBat | Out-File -FilePath "$ProjectDir\run-claude.bat" -Encoding ASCII

while ($CurrentIteration -lt $MaxIterations) {
    $CurrentIteration++
    $iterationStart = Get-Date
    $sessionId = "session-$(Get-Date -Format 'yyyy-MM-dd')-$($CurrentIteration.ToString('000'))"

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

    # Create prompt file
    $promptContent = @"
You are now a development assistant for ScholarAI project.

IMPORTANT: Work on ONE task at a time. Follow this workflow:

1. Read tasks.json from $ProjectDir
2. Select ONE PENDING task (priority=1 first)
3. Update task status to in_progress
4. Implement according to verification_steps
5. Use TDD: write tests first
6. Test your implementation
7. Commit to git with conventional format
8. Update task status to completed
9. Add completed_at timestamp
10. Write session summary to Progress-Logs folder

Project directory: $ProjectDir
Session ID: $sessionId

Start working now!
"@

    $promptFile = "$ProjectDir\auto-prompt-current.txt"
    $promptContent | Out-File -FilePath $promptFile -Encoding UTF8 -Force

    Write-Host "Starting Claude Code..." -ForegroundColor Blue
    Write-Host ""

    # Run wrapper batch
    Push-Location $ProjectDir
    try {
        $batPath = Join-Path $ProjectDir "run-claude.bat"
        $process = Start-Process -FilePath $batPath -Wait -NoNewWindow -PassThru
    }
    finally {
        Pop-Location
    }

    $iterationEnd = Get-Date
    $duration = $iterationEnd - $iterationStart
    $minutes = [int]$duration.TotalMinutes

    if ($process.ExitCode -eq 0) {
        Write-Host "  SUCCESS (${minutes}m $duration.Seconds s)" -ForegroundColor Green
    } else {
        Write-Host "  FAILED (Exit code: $($process.ExitCode))" -ForegroundColor Red
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
