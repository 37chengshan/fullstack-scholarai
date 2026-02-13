@echo off
REM ScholarAI Automation Starter
REM Usage: start-auto.bat [number_of_iterations]

setlocal enabledelayedexpansion

if "%1"=="" (
    echo Usage: start-auto.bat [number_of_iterations]
    echo Example: start-auto.bat 5
    exit /b 1
)

set ITERATIONS=%1

echo ============================================================
echo   ScholarAI Automation Launcher
echo ============================================================
echo.
echo   Running %ITERATIONS% iterations...
echo   Press Ctrl+C to stop at any time
echo.
echo ============================================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0run-auto.ps1" -MaxIterations %ITERATIONS%

echo.
echo ============================================================
echo   Automation Complete
echo ============================================================
echo.
pause
