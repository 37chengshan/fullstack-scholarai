@echo off
REM ScholarAI 自动化开发流程脚本 (Windows批处理版本)
REM 用法: run-dev-loop.bat <次数>

setlocal enabledelayedexpansion

REM 参数检查
if "%1"=="" (
    echo [错误] 请指定循环次数
    echo 用法: %~nx0 ^<次数^>
    echo 示例: %~nx0 5
    exit /b 1
)

set MAX_ITERATIONS=%1
set CURRENT_ITERATION=0
set PROJECT_DIR=%~dp0
set TASKS_FILE=%PROJECT_DIR%tasks.json
set PROGRESS_LOG=%PROJECT_DIR%dev-loop.log
set SESSION_START=%date% %time%

REM 创建日志文件
echo ======================================== > "%PROGRESS_LOG%"
echo 开发循环开始: %date% %time% >> "%PROGRESS_LOG%"
echo 项目目录: %PROJECT_DIR% >> "%PROGRESS_LOG%"
echo 计划迭代次数: %MAX_ITERATIONS% >> "%PROGRESS_LOG%"
echo ======================================== >> "%PROGRESS_LOG%"

REM 检查任务文件
if not exist "%TASKS_FILE%" (
    echo [错误] 找不到 tasks.json 文件 >> "%PROGRESS_LOG%"
    exit /b 1
)

REM Python脚本：获取未完成任务数量
set GET_PENDING=import json; data=json.load(open(r'%TASKS_FILE%', 'r', encoding='utf-8')); pending=sum(1 for t in data['tasks'] if t['status']=='pending'); print(pending)

REM Python脚本：获取下一个任务
set GET_NEXT=import json; data=json.load(open(r'%TASKS_FILE%', 'r', encoding='utf-8')); pending=[t for t in data['tasks'] if t['status']=='pending']; pending.sort(key=lambda x: (x['priority'], x['id'])); print(pending[0]['id'] + ' | ' + pending[0]['title'] + ' | Priority: ' + str(pending[0]['priority'])) if pending else print('None')

REM 主循环
:loop
if %CURRENT_ITERATION% geq %MAX_ITERATIONS% goto endloop

set /a CURRENT_ITERATION+=1
set SESSION_ID=session-%date:~0,4%-%date:~5,2%-%date:~8,2%-!CURRENT_ITERATION!

echo.
echo ======================================== >> "%PROGRESS_LOG%"
echo 迭代 #%CURRENT_ITERATION% / %MAX_ITERATIONS% >> "%PROGRESS_LOG%"
echo ======================================== >> "%PROGRESS_LOG%"

REM 检查未完成任务
for /f %%i in ('python -c "%GET_PENDING%"') do set PENDING_COUNT=%%i
echo [INFO] 剩余未完成任务: %PENDING_COUNT% >> "%PROGRESS_LOG%"
echo [INFO] 剩余未完成任务: %PENDING_COUNT%

if %PENDING_COUNT%==0 (
    echo [SUCCESS] 所有任务已完成！ >> "%PROGRESS_LOG%"
    echo 恭喜！所有任务已完成！
    goto endloop
)

REM 获取下一个任务
for /f "tokens=*" %%i in ('python -c "%GET_NEXT%"') do set NEXT_TASK=%%i
echo [INFO] 下一个任务: %NEXT_TASK% >> "%PROGRESS_LOG%"
echo [INFO] 下一个任务: %NEXT_TASK%

REM 构建Claude提示词
set PROMPT=你现在是ScholarAI项目的开发助手。请按照以下流程工作：^^^ ^^\
1. 读取 %PROJECT_DIR%CLAUDE.md 了解开发流程^^^ ^^\
2. 读取 %PROJECT_DIR%tasks.json 查看任务清单^^^ ^^\
3. 请从 tasks.json 中选择一个新的未完成任务来执行。%NEXT_TASK%^^^ ^^\
4. 按照CLAUDE.md中定义的Coding Agent工作流程执行：^^^ ^^\
   - 获取上下文（git log, progress.json, tasks.json）^^^ ^^\
   - 验证现有功能（启动服务，测试）^^^ ^^\
   - 实现功能（编码）^^^ ^^\
   - 端到端测试^^^ ^^\
   - 更新状态（tasks.json, progress.json）^^^ ^^\
   - 提交代码（git commit）^^^ ^^\
   - 会话总结到 Progress Log 文件夹^^^ ^^\
重要规则：^^^ ^^\
- 每次只完成一个任务^^^ ^^\
- 使用TDD方法，先写测试^^^ ^^\
- 完成后更新tasks.json中任务的status为completed^^^ ^^\
- 提交git commit，使用规范的commit message^^^ ^^\
- 将会话总结写入到 Progress Log 文件夹，文件名包含任务编号^^^ ^^\
- 确保代码能正常运行，不要留下半成品^^^ ^^\
当前会话ID: %SESSION_ID%^^^ ^^\
项目目录: %PROJECT_DIR%^^^ ^^\
开始工作！

REM 记录开始时间
set ITERATION_START=%time%

echo [INFO] 调用Claude Code... >> "%PROGRESS_LOG%"
echo.
echo ========================================
echo 调用Claude Code...
echo ========================================
echo.

REM 调用Claude Code
REM 注意：根据实际Claude Code CLI调整参数
claude "%PROMPT%" --yes

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] 迭代完成 >> "%PROGRESS_LOG%"
    echo 迭代完成
) else (
    echo [ERROR] 迭代失败 >> "%PROGRESS_LOG%"
    echo 迭代失败，请检查日志
    set /p CONTINUE="是否继续下一次迭代? (y/n): "
    if /i not "!CONTINUE!"=="y" goto endloop
)

echo.
timeout /t 2 >nul
goto loop

:endloop
echo.
echo ======================================== >> "%PROGRESS_LOG%"
echo 开发循环结束 >> "%PROGRESS_LOG%"
echo ======================================== >> "%PROGRESS_LOG%"
echo 总迭代次数: %CURRENT_ITERATION% >> "%PROGRESS_LOG%"
echo 结束时间: %date% %time% >> "%PROGRESS_LOG%"
echo 总迭代次数: %CURRENT_ITERATION%
echo 结束时间: %date% %time%

REM 显示最终任务状态
for /f %%i in ('python -c "%GET_PENDING%"') do set FINAL_PENDING=%%i
echo 剩余未完成任务: %FINAL_PENDING% >> "%PROGRESS_LOG%"
echo 剩余未完成任务: %FINAL_PENDING%

if %FINAL_PENDING%==0 (
    echo 所有任务已完成！
) else (
    echo 还有 %FINAL_PENDING% 个任务待完成
)
echo 详细日志: %PROGRESS_LOG%
echo ======================================== >> "%PROGRESS_LOG%"

endlocal
