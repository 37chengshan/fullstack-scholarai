# ScholarAI Auto-Dev Loop - Final Working Version
# Uses direct prompt string to avoid pipe issues

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

function Invoke-Claude {
    param([string]$Prompt)

    # Save prompt to temp env var to avoid argument length issues
    $env:CLAUDE_PROMPT = $Prompt

    # Create inline batch to execute
    $batchScript = @"
@echo off
setlocal
set PROMPT=%CLAUDE_PROMPT%
claude -p "%PROMPT%" --print --dangerously-skip-permissions
endlocal
"@
    $tempBat = [IO.Path]::GetTempFileName() + ".bat"
    $batchScript | Out-File -FilePath $tempBat -Encoding ASCII -Force

    try {
        & $tempBat
        return $LASTEXITCODE
    }
    finally {
        Remove-Item $tempBat -ErrorAction SilentlyContinue
    }
}

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

    # Create prompt
    $promptContent = "You are now a development assistant for ScholarAI project.`n`nIMPORTANT: Work on ONE task at a time. Follow this workflow:`n`n1. Read tasks.json from $ProjectDir`n2. Select ONE PENDING task (priority=1 first)`n3. Update task status to in_progress`n4. Implement according to verification_steps`n5. Use TDD: write tests first`n6. Test your implementation`n7. Commit to git with conventional format`n8. Update task status to completed`n9. Add completed_at timestamp`n10. Write session summary to Progress-Logs folder`n`nProject directory: $ProjectDir`nSession ID: $sessionId`n`nStart working now!"

    Write-Host "Starting Claude Code..." -ForegroundColor Blue
    Write-Host ""

    $env:CLAUDE_PROJECT_DIR = $ProjectDir

    # Run Claude
    $exitCode = Invoke-Claude -Prompt $promptContent

    $iterationEnd = Get-Date
    $duration = $iterationEnd - $iterationStart
    $minutes = [int]$duration.TotalMinutes

    if ($exitCode -eq 0) {
        Write-Host "  SUCCESS (${minutes}m $duration.Seconds s)" -ForegroundColor Green
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
