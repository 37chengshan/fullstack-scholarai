#!/bin/bash

# ScholarAI 自动化 Claude Code 开发循环脚本
# 这个脚本会启动独立的 Claude Code 进程来完成任务

set -e

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
    echo "示例: $0 5  # 运行5次Claude Code会话"
    exit 1
fi

MAX_ITERATIONS=$1
CURRENT_ITERATION=0
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASKS_FILE="$PROJECT_DIR/tasks.json"
PROGRESS_LOG="$PROJECT_DIR/claude-loop.log"
SESSION_START=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# 创建日志文件
{
    echo "========================================"
    echo "Claude Code 自动化开发循环"
    echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "项目目录: $PROJECT_DIR"
    echo "计划迭代次数: $MAX_ITERATIONS"
    echo "========================================"
    echo ""
} | tee -a "$PROGRESS_LOG"

# 检查任务文件
if [ ! -f "$TASKS_FILE" ]; then
    echo -e "${RED}错误: 找不到 tasks.json${NC}" | tee -a "$PROGRESS_LOG"
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
    in_progress = sum(1 for t in data['tasks'] if t['status'] == 'in_progress')
    print(f'{pending}|{in_progress}')
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
"
}

# 获取任务摘要
get_task_summary() {
    python3 -c "
import json
try:
    with open('$TASKS_FILE', 'r', encoding='utf-8') as f:
        data = json.load(f)
    total = len(data['tasks'])
    completed = sum(1 for t in data['tasks'] if t['status'] == 'completed')
    pending = sum(1 for t in data['tasks'] if t['status'] == 'pending')
    percentage = int(completed / total * 100) if total > 0 else 0
    print(f'{total}|{completed}|{pending}|{percentage}')
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
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

# 固定的 Claude Code 提示词
CLAUDE_PROMPT="你现在是ScholarAI项目的开发助手。请严格按照以下流程工作：

## 第一步：获取上下文
1. 读取 $PROJECT_DIR/CLAUDE.md 了解开发工作流程
2. 读取 $PROJECT_DIR/tasks.json 查看所有任务
3. 运行以下命令查看最近的工作：
   cd $PROJECT_DIR && git log --oneline -5
4. 运行以下命令查看当前分支和状态：
   cd $PROJECT_DIR && git status

## 第二步：选择任务
5. 从 tasks.json 中选择一个**未完成的任务**来执行
   - 优先选择 priority=1 的任务
   - 跳过所有 status='completed' 的任务
   - 如果有 status='in_progress' 的任务，继续完成它
   - 更新任务的 status 为 'in_progress'

## 第三步：实现功能
6. 按照任务的 verification_steps 逐步实现
7. 使用 TDD 方法：先写测试，再实现功能
8. 如果需要，启动开发服务器测试：
   - 后端: cd $PROJECT_DIR/backend && python run.py
   - 前端: cd $PROJECT_DIR/frontend && npm run dev

## 第四步：测试和提交
9. 完成后进行端到端测试
10. 更新 tasks.json：
    - 将完成的任务 status 改为 'completed'
    - 添加 completed_at 时间戳
    - 更新 session_id
11. 提交代码到 Git：
    - git add 所有修改的文件
    - 使用规范的 commit message
    - 格式: <type>: <description>
    - 类型: feat, fix, refactor, docs, test, chore

## 第五步：会话总结
12. 将本次会话的总结写入到 Progress Log 文件夹
13. 文件名格式: task-<任务编号>-<简短标题>.md
14. 内容包括：完成的任务、修改的文件、测试结果

**重要规则**：
- ✅ 每次只完成一个任务
- ✅ 代码必须能正常运行，不要留下半成品
- ✅ 提交前确保没有 console.log 或调试代码
- ✅ 遵循项目的编码规范（见 CLAUDE.md）
- ✅ 完成后必须更新 tasks.json

**项目技术栈**：
- 前端: React 18 + TypeScript + Vite 6
- 后端: Python Flask + MongoDB
- 当前任务总数: 39
- 已完成: 约 19 个

现在开始工作！选择一个未完成的任务并完成它。"

# 主循环
while [ $CURRENT_ITERATION -lt $MAX_ITERATIONS ]; do
    CURRENT_ITERATION=$((CURRENT_ITERATION + 1))
    SESSION_ID="session-$(date +%Y-%m-%d)-$(printf %03d $CURRENT_ITERATION)"

    echo ""
    echo "========================================" | tee -a "$PROGRESS_LOG"
    echo -e "${CYAN} Claude Code 迭代 #$CURRENT_ITERATION / $MAX_ITERATIONS${NC}" | tee -a "$PROGRESS_LOG"
    echo "========================================" | tee -a "$PROGRESS_LOG"

    # 检查未完成任务
    STATS=$(get_pending_count)
    PENDING_COUNT=$(echo $STATS | cut -d'|' -f1)
    IN_PROGRESS_COUNT=$(echo $STATS | cut -d'|' -f2)

    log "INFO" "未完成: ${YELLOW}$PENDING_COUNT${NC} | 进行中: ${YELLOW}$IN_PROGRESS_COUNT${NC}"

    if [ "$PENDING_COUNT" -eq 0 ]; then
        log "SUCCESS" "${GREEN}所有任务已完成！${NC}"
        echo -e "${GREEN}🎉 恭喜！所有任务已完成！${NC}"
        break
    fi

    # 获取总体进度
    SUMMARY=$(get_task_summary)
    TOTAL=$(echo $SUMMARY | cut -d'|' -f1)
    COMPLETED=$(echo $SUMMARY | cut -d'|' -f2)
    PERCENTAGE=$(echo $SUMMARY | cut -d'|' -f4)

    log "INFO" "总进度: ${COMPLETED}/${TOTAL} (${PERCENTAGE}%)"

    # 记录开始时间
    ITERATION_START=$(date +%s)

    # 显示即将执行的命令
    log "INFO" "启动 Claude Code..."
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  即将启动 Claude Code 进程...${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}提示词预览:${NC}"
    echo -e "${YELLOW}→ 从 tasks.json 选择未完成任务${NC}"
    echo -e "${YELLOW}→ 按照开发流程实现功能${NC}"
    echo -e "${YELLOW}→ 提交代码并更新任务状态${NC}"
    echo ""
    echo -e "${CYAN}Claude Code 将在新窗口/进程中运行${NC}"
    echo -e "${CYAN}当前窗口仅显示日志，不会交互${NC}"
    echo ""
    read -p "按 Enter 键启动 Claude Code (或 Ctrl+C 退出)..."
    echo ""

    # 调用 Claude Code
    # 使用 --yes 自动接受所有操作
    # 其他可能的参数: --no-input, --allow-dangerous
    log "INFO" "执行中..."

    if claude --yes <<'EOF'; then
        ITERATION_END=$(date +%s)
        DURATION=$((ITERATION_END - ITERATION_START))
        MINUTES=$((DURATION / 60))
        SECONDS=$((DURATION % 60))

        log "SUCCESS" "${GREEN}迭代完成 (耗时: ${MINUTES}分${SECONDS}秒)${NC}"
        echo ""
        echo -e "${GREEN}✓ 迭代 #$CURRENT_ITERATION 完成${NC}"
        echo -e "${GREEN}  耗时: ${MINUTES}分${SECONDS}秒${NC}"
        echo ""
    else
        ITERATION_END=$(date +%s)
        DURATION=$((ITERATION_END - ITERATION_START))
        MINUTES=$((DURATION / 60))
        SECONDS=$((DURATION % 60))

        log "ERROR" "${RED}迭代失败 (耗时: ${MINUTES}分${SECONDS}秒)${NC}"
        echo ""
        echo -e "${RED}✗ Claude Code 执行出错${NC}" | tee -a "$PROGRESS_LOG"
        echo -e "${RED}  耗时: ${MINUTES}分${SECONDS}秒${NC}"
        echo ""

        # 询问是否继续
        read -p "是否继续下一次迭代? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "INFO" "用户中断执行"
            break
        fi
    fi

    # 短暂暂停，让用户看到结果
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    sleep 2

    # 检查是否应该继续
    if [ $CURRENT_ITERATION -ge $MAX_ITERATIONS ]; then
        log "INFO" "达到最大迭代次数"
        break
    fi
done

# 最终总结
echo ""
echo "========================================" | tee -a "$PROGRESS_LOG"
echo -e "${CYAN}开发循环结束${NC}" | tee -a "$PROGRESS_LOG"
echo "========================================" | tee -a "$PROGRESS_LOG"
echo "总迭代次数: $CURRENT_ITERATION" | tee -a "$PROGRESS_LOG"
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$PROGRESS_LOG"

# 显示最终任务状态
FINAL_STATS=$(get_pending_count)
FINAL_PENDING=$(echo $FINAL_STATS | cut -d'|' -f1)
echo "剩余未完成任务: $FINAL_PENDING" | tee -a "$PROGRESS_LOG"

if [ $FINAL_PENDING -eq 0 ]; then
    echo -e "${GREEN}✅ 所有任务已完成！${NC}" | tee -a "$PROGRESS_LOG"
else
    echo -e "${YELLOW}⚠️  还有 $FINAL_PENDING 个任务待完成${NC}" | tee -a "$PROGRESS_LOG"
fi

echo "详细日志: $PROGRESS_LOG" | tee -a "$PROGRESS_LOG"
echo "========================================" | tee -a "$PROGRESS_LOG"
echo ""
echo -e "${CYAN}提示: 使用 'python check-progress.py' 查看最新进度${NC}"
echo ""
