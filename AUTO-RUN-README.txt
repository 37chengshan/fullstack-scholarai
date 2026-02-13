ScholarAI Automation - Quick Start Guide
========================================

## How to Run Automation

### Method 1: Batch File (Recommended)
Double-click `start-auto.bat` or run from command line:

    start-auto.bat 5

### Method 2: PowerShell Direct
    .\run-auto.ps1 5

Replace "5" with the number of iterations you want.

## What It Does

For each iteration:
1. Reads tasks.json
2. Selects next pending task (priority=1 first)
3. Calls Claude Code with development workflow
4. Waits for completion
5. Shows success/failure status
6. Continues to next iteration

## Check Progress

Run this command to see current status:

    python get-task-stats.py

Or check tasks.json directly.

## Troubleshooting

If automation fails:
1. Ensure Claude Code CLI is installed: claude --version
2. Check tasks.json exists and is valid JSON
3. Verify Python is installed for get-task-stats.py

## Stopping Automation

Press Ctrl+C to stop at any time.

## Files

- run-auto.ps1: Main automation script (PowerShell)
- start-auto.bat: Easy launcher (Windows)
- get-task-stats.py: Progress checker
- auto-prompt.txt: Claude Code prompt template
