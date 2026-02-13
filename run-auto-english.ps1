# ScholarAI Automation Loop (English Only)
# Fully unattended, auto-yes, English logging to avoid encoding issues

param(
    [Parameter(Mandatory=$true)]
    [int]$MaxIterations
)

$ProjectDir = $PSScriptRoot
$CurrentIteration = 0
$LogDir = "$ProjectDir\Progress-Logs"
$LogFile = "$LogDir\auto-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# Create log directory
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "  ScholarAI Automation Loop - 19 Tasks Remaining" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""
Write-Host "  Mode: Fully Unattended (Auto-Yes)" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""

while ($CurrentIteration -lt $MaxIterations) {
    $CurrentIteration++
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $sessionId = "session-$(Get-Date -Format 'yyyy-MM-dd')-$($CurrentIteration.ToString('000'))"

    Write-Host ""
    $separator = "  " + "=" * 58
    Write-Host $separator -ForegroundColor Cyan
    Write-Host "    Iteration #$CurrentIteration / $MaxIterations" -ForegroundColor Cyan
    Write-Host "    Time: $timestamp" -ForegroundColor Gray
    Write-Host "    Session: $sessionId" -ForegroundColor Gray
    Write-Host $separator -ForegroundColor Cyan

    # Get task stats
    $stats = python "$ProjectDir\get-task-stats.py"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    ERROR: Failed to get task stats" -ForegroundColor Red
        break
    }

    $parts = $stats -split '\|'
    $total = $parts[0]
    $completed = $parts[1]
    $pending = $parts[2]
    $percentage = $parts[3]

    Write-Host "    Total: $total | Done: $completed | Todo: $pending ($percentage%)" -ForegroundColor Yellow

    if ($pending -eq 0) {
        Write-Host "    All tasks completed!" -ForegroundColor Green
        Write-Host ""
        break
    }

    Write-Host "    Starting Claude Code..." -ForegroundColor Blue
    Write-Host ""

    # Prepare prompt
    $promptFile = "$ProjectDir\claude-prompt-en.txt"
    if (-not (Test-Path $promptFile)) {
        Write-Host "    ERROR: Prompt file not found: $promptFile" -ForegroundColor Red
        break
    }

    # Start Claude Code with auto-yes
    $env:CLAUDE_PROJECT_DIR = $ProjectDir

    $process = Start-Process -FilePath "claude" -ArgumentList "--yes", $promptFile -Wait -NoNewWindow -PassThru -RedirectStandardInput "nul"

    $exitCode = $process.ExitCode
    $duration = (Get-Date) - $process.StartTime

    if ($exitCode -eq 0) {
        $dur = "Duration: $duration.TotalMinutes min $duration.Seconds sec"
        Write-Host "    SUCCESS: $dur" -ForegroundColor Green
        Add-Content -Path $LogFile -Value "[$timestamp] Iteration #$CurrentIteration SUCCESS - $dur"
    } else {
        $dur = "Duration: $duration.TotalMinutes min $duration.Seconds sec"
        Write-Host "    FAILED: Exit code $exitCode, $dur" -ForegroundColor Red
        Add-Content -Path $LogFile -Value "[$timestamp] Iteration #$CurrentIteration FAILED - Exit code: $exitCode - $dur"
    }

    Write-Host ""
    Add-Content -Path $LogFile -Value "========================================="
    Start-Sleep -Seconds 2
}

# Final summary
Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "  Automation Complete" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""
Write-Host "  Total iterations: $CurrentIteration" -ForegroundColor Gray
Write-Host ""

# Show final stats
$finalStats = python "$ProjectDir\get-task-stats.py"
$parts2 = $finalStats -split '\|'
$finalPending = $parts2[2]
"Remaining: $finalPending" | Out-File -FilePath $LogFile -Append -Encoding UTF8

if ($finalPending -eq 0) {
    Write-Host "All tasks completed!" -ForegroundColor Green
} else {
    Write-Host "Tasks remaining: $finalPending" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Log file: $LogFile" -ForegroundColor Gray
Write-Host ""
