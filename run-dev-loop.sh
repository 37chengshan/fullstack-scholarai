#!/bin/bash

# ScholarAI 自动化开发流程脚本
# 用法: ./run-dev-loop.sh <次数>

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 参数检查
if [ $# -ne 1 ]; then
    echo -e "${RED}错误: 请指定循环次数${NC}"
    echo "用法: $0 <次数>"
    echo "示例: $0 5  # 运行5次开发循环"
    exit 1
fi

MAX_ITERATIONS=$1
CURRENT_ITERATION=0
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASKS_FILE="$PROJECT_DIR/tasks.json"
PROGRESS_LOG="$PROJECT_DIR/dev-loop.log"
SESSION_START=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# 创建日志文件
echo "========================================" | tee -a "$PROGRESS_LOG"
echo "开发循环开始: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$PROGRESS_LOG"
echo "项目目录: $PROJECT_DIR" | tee -a "$PROGRESS_LOG"
echo "计划迭代次数: $MAX_ITERATIONS" | tee -a "$PROGRESS_LOG"
echo "========================================" | tee -a "$PROGRESS_LOG"

# 检查任务文件
if [ ! -f "$TASKS_FILE" ]; then
    echo -e "${RED}错误: 找不到 tasks.json 文件${NC}" | tee -a "$PROGRESS_LOG"
    exit 1
fi

# 获取未完成任务数量
get_pending_count() {
    python3 -c "
import json
import sys
try:
    with open('$TASKS_FILE', 'r', encoding='utf-8') as f:
        data = json.load(f)
    pending = sum(1 for t in data['tasks'] if t['status'] == 'pending')
    print(pending)
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
"
}

# 获取当前进行中的任务
get_in_progress_task() {
    python3 -c "
import json
import sys
try:
    with open('$TASKS_FILE', 'r', encoding='utf-8') as f:
        data = json.load(f)
    in_progress = [t for t in data['tasks'] if t['status'] == 'in_progress']
    if in_progress:
        task = in_progress[0]
        print(f'{task[\"id\"]} | {task[\"title\"]}')
    else:
        print('None')
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
"
}

# 获取下一个待处理任务
get_next_task() {
    python3 -c "
import json
import sys
try:
    with open('$TASKS_FILE', 'r', encoding='utf-8') as f:
        data = json.load(f)
    pending = [t for t in data['tasks'] if t['status'] == 'pending']
    if pending:
        # 按优先级排序，然后按ID排序
        pending.sort(key=lambda x: (x['priority'], x['id']))
        task = pending[0]
        print(f'{task[\"id\"]} | {task[\"title\"]} | Priority: {task[\"priority\"]}')
    else:
        print('None')
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
"
}

# 打印带时间戳的日志
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$PROGRESS_LOG"
}

# 主循环
while [ $CURRENT_ITERATION -lt $MAX_ITERATIONS ]; do
    CURRENT_ITERATION=$((CURRENT_ITERATION + 1))
    SESSION_ID="session-$(date +%Y-%m-%d)-$(printf %03d $CURRENT_ITERATION)"

    echo ""
    echo "========================================" | tee -a "$PROGRESS_LOG"
    echo -e "${CYAN}迭代 #$CURRENT_ITERATION / $MAX_ITERATIONS${NC}" | tee -a "$PROGRESS_LOG"
    echo "========================================" | tee -a "$PROGRESS_LOG"

    # 检查未完成任务
    PENDING_COUNT=$(get_pending_count)
    log "INFO" "剩余未完成任务: ${YELLOW}$PENDING_COUNT${NC}"

    if [ "$PENDING_COUNT" -eq 0 ]; then
        log "SUCCESS" "${GREEN}所有任务已完成！${NC}"
        echo -e "${GREEN}🎉 恭喜！所有任务已完成！${NC}" | tee -a "$PROGRESS_LOG"
        break
    fi

    # 检查是否有进行中的任务
    IN_PROGRESS=$(get_in_progress_task)
    if [ "$IN_PROGRESS" != "None" ]; then
        log "INFO" "发现进行中的任务: ${YELLOW}$IN_PROGRESS${NC}"
        NEXT_TASK_MSG="继续完成当前任务: $IN_PROGRESS"
    else
        # 获取下一个任务
        NEXT_TASK=$(get_next_task)
        if [ "$NEXT_TASK" = "None" ]; then
            log "ERROR" "${RED}无法获取下一个任务${NC}"
            break
        fi
        log "INFO" "下一个任务: ${YELLOW}$NEXT_TASK${NC}"
        NEXT_TASK_MSG="请从 tasks.json 中选择一个新的未完成任务来执行。$NEXT_TASK"
    fi

    # 构建Claude提示词
    PROMPT="你现在是ScholarAI项目的开发助手。请按照以下流程工作：

1. 读取 $PROJECT_DIR/CLAUDE.md 了解开发流程
2. 读取 $PROJECT_DIR/tasks.json 查看任务清单
3. $NEXT_TASK_MSG
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

当前会话ID: $SESSION_ID
项目目录: $PROJECT_DIR
开始工作！"

    log "INFO" "调用Claude Code..."
    echo -e "${BLUE}Claude提示词:${NC}" | tee -a "$PROGRESS_LOG"
    echo "$PROMPT" | tee -a "$PROGRESS_LOG"
    echo ""

    # 记录开始时间
    ITERATION_START=$(date +%s)

    # 调用Claude Code
    # 注意：根据实际Claude Code CLI参数调整
    # --yes: 自动确认所有提示
    # --no-input: 非交互模式
    # 其他可能的参数：--allow-dangerous, --bypass-permissions 等
    log "INFO" "执行中..."

    if claude "$PROMPT" --yes 2>&1 | tee -a "$PROGRESS_LOG"; then
        ITERATION_END=$(date +%s)
        DURATION=$((ITERATION_END - ITERATION_START))
        log "SUCCESS" "${GREEN}迭代完成 (耗时: ${DURATION}秒)${NC}"
    else
        ITERATION_END=$(date +%s)
        DURATION=$((ITERATION_END - ITERATION_START))
        log "ERROR" "${RED}迭代失败 (耗时: ${DURATION}秒)${NC}"
        echo -e "${RED}Claude执行出错，请检查日志${NC}" | tee -a "$PROGRESS_LOG"

        # 询问是否继续
        read -p "是否继续下一次迭代? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "INFO" "用户中断执行"
            break
        fi
    fi

    # 短暂暂停，让用户看到结果
    sleep 2
done

# 最终总结
echo ""
echo "========================================" | tee -a "$PROGRESS_LOG"
echo -e "${CYAN}开发循环结束${NC}" | tee -a "$PROGRESS_LOG"
echo "========================================" | tee -a "$PROGRESS_LOG"
echo "总迭代次数: $CURRENT_ITERATION" | tee -a "$PROGRESS_LOG"
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$PROGRESS_LOG"

# 显示最终任务状态
PENDING_COUNT=$(get_pending_count)
echo "剩余未完成任务: $PENDING_COUNT" | tee -a "$PROGRESS_LOG"

if [ $PENDING_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ 所有任务已完成！${NC}" | tee -a "$PROGRESS_LOG"
else
    echo -e "${YELLOW}⚠️  还有 $PENDING_COUNT 个任务待完成${NC}" | tee -a "$PROGRESS_LOG"
fi

echo "详细日志: $PROGRESS_LOG" | tee -a "$PROGRESS_LOG"
echo "========================================" | tee -a "$PROGRESS_LOG"
