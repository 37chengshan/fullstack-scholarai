# ScholarAI 自动化开发流程脚本 (PowerShell版本)
# 用法: .\run-dev-loop.ps1 <次数>

param(
    [Parameter(Mandatory=$true)]
    [int]$MaxIterations
)

# 颜色输出函数
function Write-ColorLog {
    param(
        [string]$Level,
        [string]$Message,
        [string]$Color = "White"
    )
    $timestamp = Get-Date -Format "HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage -ForegroundColor $Color
    Add-Content -Path $ProgressLog -Value $logMessage
}

# 参数验证
if ($MaxIterations -le 0) {
    Write-Host "错误: 迭代次数必须大于0" -ForegroundColor Red
    exit 1
}

# 初始化变量
$ProjectDir = $PSScriptRoot
$TasksFile = Join-Path $ProjectDir "tasks.json"
$ProgressLog = Join-Path $ProjectDir "dev-loop.log"
$CurrentIteration = 0
$SessionStart = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"

# 创建日��文件
$separator = "=" * 40
$separator | Out-File -FilePath $ProgressLog -Encoding UTF8
"开发循环开始: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -FilePath $ProgressLog -Encoding UTF8 -Append
"项目目录: $ProjectDir" | Out-File -FilePath $ProgressLog -Encoding UTF8 -Append
"计划迭代次数: $MaxIterations" | Out-File -FilePath $ProgressLog -Encoding UTF8 -Append
$separator | Out-File -FilePath $ProgressLog -Encoding UTF8 -Append

# 检查任务文件
if (-not (Test-Path $TasksFile)) {
    Write-ColorLog "ERROR" "找不到 tasks.json 文件" "Red"
    exit 1
}

# 获取任务数据
function Get-TasksData {
    $json = Get-Content $TasksFile -Raw -Encoding UTF8 | ConvertFrom-Json
    return $json
}

# 获取未完成任务数量
function Get-PendingCount {
    $data = Get-TasksData
    $pending = ($data.tasks | Where-Object { $_.status -eq "pending" | Measure-Object).Count
    return $pending
}

# 获取下一个任务
function Get-NextTask {
    $data = Get-TasksData
    $pending = $data.tasks | Where-Object { $_.status -eq "pending" } |
              Sort-Object { $_.priority }, { $_.id }

    if ($pending.Count -eq 0) {
        return $null
    }

    $task = $pending[0]
    return "$($task.id) | $($task.title) | Priority: $($task.priority)"
}

# 主循环
while ($CurrentIteration -lt $MaxIterations) {
    $CurrentIteration++
    $sessionId = "session-$(Get-Date -Format 'yyyy-MM-dd')-$($CurrentIteration.ToString('000'))"

    Write-Host ""
    $separator | Out-File -FilePath $ProgressLog -Encoding UTF8 -Append
    Write-ColorLog "INFO" "迭代 #$CurrentIteration / $MaxIterations" "Cyan"
    $separator | Out-File -FilePath $ProgressLog -Encoding UTF8 -Append

    # 检查未完成任务
    $pendingCount = Get-PendingCount
    Write-ColorLog "INFO" "剩余未完成任务: $pendingCount" "Yellow"

    if ($pendingCount -eq 0) {
        Write-ColorLog "SUCCESS" "所有任务已完成！" "Green"
        Write-Host "🎉 恭喜！所有任务已完成！" -ForegroundColor Green
        break
    }

    # 获取下一个任务
    $nextTask = Get-NextTask
    if ($null -eq $nextTask) {
        Write-ColorLog "ERROR" "无法获取下一个任务" "Red"
        break
    }

    Write-ColorLog "INFO" "下一个任务: $nextTask" "Yellow"

    # 构建Claude提示词
    $prompt = @"
你现在是ScholarAI项目的开发助手。请按照以下流程工作：

1. 读取 $ProjectDir\CLAUDE.md 了解开发流程
2. 读取 $ProjectDir\tasks.json 查看任务清单
3. 请从 tasks.json 中选择一个新的未完成任务来执行。$nextTask
4. 按照CLAUDE.md中定义的Coding Agent工作流程执行：
   - 获取上下文（git log, progress.json, tasks.json）
   - 验证现有功能（启动服务，测试）
   - 实现功能（编码）
   - 端到端测试
   - 更新状态（tasks.json, progress.json）
   - 提交代码（git commit）
   - 会话总结到 Progress Log 文件夹

重要规则：
- 每次只完成一个任务
- 使用TDD方法，先写测试
- 完成后更新tasks.json中任务的status为completed
- 提交git commit，使用规范的commit message
- 将会话总结写入到 Progress Log 文件夹，文件名包含任务编号
- 确保代码能正常运行，不要留下半成品
- 使用前端npm run dev和后端python run.py启动服务进行测试

当前会话ID: $sessionId
项目目录: $ProjectDir
开始工作！
"@

    Write-ColorLog "INFO" "调用Claude Code..." "Blue"
    Write-Host ""
    Write-Host $separator
    Write-Host "Claude提示词:" -ForegroundColor Blue
    Write-Host $prompt
    Write-Host $separator
    Write-Host ""

    # 记录开始时间
    $iterationStart = Get-Date

    # 调用Claude Code
    # 注意：根据实际Claude Code CLI调整参数
    # --yes: 自动确认所有提示
    $claudeArgs = @($prompt, "--yes")

    Write-ColorLog "INFO" "执行中..." "Gray"

    try {
        $process = Start-Process -FilePath "claude" -ArgumentList $claudeArgs -Wait -PassThru -NoNewWindow

        if ($process.ExitCode -eq 0) {
            $duration = (Get-Date) - $iterationStart
            Write-ColorLog "SUCCESS" "迭代完成 (耗时: $($duration.TotalSeconds.ToString('F0'))秒)" "Green"
        } else {
            $duration = (Get-Date) - $iterationStart
            Write-ColorLog "ERROR" "迭代失败 (耗时: $($duration.TotalSeconds.ToString('F0'))秒)" "Red"
            Write-Host "Claude执行出错，请检查日志" -ForegroundColor Red

            # 询问是否继续
            $continue = Read-Host "是否继续下一次迭代? (y/n)"
            if ($continue -ne "y") {
                Write-ColorLog "INFO" "用户中断执行" "Yellow"
                break
            }
        }
    } catch {
        Write-ColorLog "ERROR" "执行Claude失败: $_" "Red"
        break
    }

    # 短暂暂停
    Start-Sleep -Seconds 2
}

# 最终总结
Write-Host ""
$separator | Out-File -FilePath $ProgressLog -Encoding UTF8 -Append
Write-ColorLog "INFO" "开发循环结束" "Cyan"
$separator | Out-File -FilePath $ProgressLog -Encoding UTF8 -Append
"总迭代次数: $CurrentIteration" | Out-File -FilePath $ProgressLog -Encoding UTF8 -Append
"结束时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -FilePath $ProgressLog -Encoding UTF8 -Append

Write-Host "总迭代次数: $CurrentIteration"
Write-Host "结束时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# 显示最终任务状态
$finalPending = Get-PendingCount
"剩余未完成任务: $finalPending" | Out-File -FilePath $ProgressLog -Encoding UTF8 -Append
Write-Host "剩余未完成任务: $finalPending"

if ($finalPending -eq 0) {
    Write-Host "✅ 所有任务已完成！" -ForegroundColor Green
} else {
    Write-Host "⚠️  还有 $finalPending 个任务待完成" -ForegroundColor Yellow
}

Write-Host "详细日志: $ProgressLog"
$separator | Out-File -FilePath $ProgressLog -Encoding UTF8 -Append
