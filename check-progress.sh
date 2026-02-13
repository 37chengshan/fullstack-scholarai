#!/bin/bash

# ScholarAI 进度查看脚本 (Bash版本)

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASKS_FILE="$PROJECT_DIR/tasks.json"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# 检查任务文件
if [ ! -f "$TASKS_FILE" ]; then
    echo -e "${RED}错误: 找不到 tasks.json${NC}"
    exit 1
fi

# 使用Python解析JSON
get_task_stats() {
    python3 -c "
import json
import sys
try:
    with open('$TASKS_FILE', 'r', encoding='utf-8') as f:
        data = json.load(f)
    tasks = data['tasks']
    completed = [t for t in tasks if t['status'] == 'completed']
    in_progress = [t for t in tasks if t['status'] == 'in_progress']
    pending = [t for t in tasks if t['status'] == 'pending']

    # 统计
    total = len(tasks)
    completed_count = len(completed)
    in_progress_count = len(in_progress)
    pending_count = len(pending)
    percentage = int((completed_count / total * 100)) if total > 0 else 0

    print(f'{total}|{completed_count}|{in_progress_count}|{pending_count}|{percentage}')

except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
"
}

get_in_progress_tasks() {
    python3 -c "
import json
try:
    with open('$TASKS_FILE', 'r', encoding='utf-8') as f:
        data = json.load(f)
    in_progress = [t for t in data['tasks'] if t['status'] == 'in_progress']
    for task in in_progress:
        print(f'{task[\"id\"]}|{task[\"title\"]}|{task[\"category\"]}|{task[\"priority\"]}')
except:
    pass
"
}

get_recent_completed() {
    python3 -c "
import json
from datetime import datetime
try:
    with open('$TASKS_FILE', 'r', encoding='utf-8') as f:
        data = json.load(f)
    completed = [t for t in data['tasks'] if t['status'] == 'completed']
    # 按完成时间排序，取前5个
    completed.sort(key=lambda x: x.get('completed_at', ''), reverse=True)
    for task in completed[:5]:
        completed_at = task.get('completed_at', '未知')
        if completed_at and completed_at != '未知':
            try:
                dt = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                completed_at = dt.strftime('%m-%d %H:%M')
            except:
                pass
        print(f'{task[\"id\"]}|{task[\"title\"]}|{completed_at}')
except:
    pass
"
}

get_next_pending() {
    python3 -c "
import json
try:
    with open('$TASKS_FILE', 'r', encoding='utf-8') as f:
        data = json.load(f)
    pending = [t for t in data['tasks'] if t['status'] == 'pending']
    # 按优先级和ID排序
    pending.sort(key=lambda x: (x['priority'], x['id']))
    for task in pending[:5]:
        print(f'{task[\"id\"]}|{task[\"title\"]}|{task[\"category\"]}|{task[\"priority\"]}')
except:
    pass
"
}

# 绘制进度条
draw_progress_bar() {
    local percentage=$1
    local width=50
    local filled=$((percentage * width / 100))
    local empty=$((width - filled))

    echo -n "  ["
    printf "${GREEN}%${NC}s" "$(printf '█%.0s' $(seq 1 $filled))"
    printf "${GRAY}%${NC}s" "$(printf '░%.0s' $(seq 1 $empty))"
    echo -n "]"
}

# 主函数
main() {
    echo ""
    local separator="============================================================"
    echo -e "${CYAN}${separator}${NC}"
    echo -e "${CYAN}  ScholarAI 项目进度报告${NC}"
    echo -e "${CYAN}${separator}${NC}"
    echo ""

    # 获取统计信息
    stats=$(get_task_stats)
    IFS='|' read -r total completed in_progress pending percentage <<< "$stats"

    # 总体进度
    echo -e "${YELLOW}📊 总体进度${NC}"
    echo "  总任务数:    $total"
    echo -e "  已完成:      ${GREEN}${completed}${NC} 个"
    echo -e "  进行中:      ${YELLOW}${in_progress}${NC} 个"
    echo -e "  待办:        ${GRAY}${pending}${NC} 个"
    echo ""

    # 进度条
    echo -n "  进度:        "
    draw_progress_bar "$percentage"
    echo " $percentage%"
    echo ""

    # 进行中的任务
    in_progress_tasks=$(get_in_progress_tasks)
    if [ -n "$in_progress_tasks" ]; then
        echo -e "${YELLOW}🔄 进行中的任务${NC}"
        while IFS='|' read -r id title category priority; do
            echo "  $id | $title"
            echo -e "    类别: $category, 优先级: $priority" "${GRAY}"
        done <<< "$in_progress_tasks"
        echo ""
    fi

    # 最近的已完成任务
    recent_completed=$(get_recent_completed)
    if [ -n "$recent_completed" ]; then
        echo -e "${GREEN}✅ 最近的已完成任务 (最多5个)${NC}"
        while IFS='|' read -r id title completed_at; do
            echo "  $id | $title"
            echo -e "    完成时间: $completed_at" "${GRAY}"
        done <<< "$recent_completed"
        echo ""
    fi

    # 下一个待办任务
    next_pending=$(get_next_pending)
    if [ -n "$next_pending" ]; then
        echo -e "${CYAN}📋 下一个待办任务 (按优先级)${NC}"
        while IFS='|' read -r id title category priority; do
            echo "  $id | $title"
            echo -e "    类别: $category, 优先级: $priority" "${GRAY}"
        done <<< "$next_pending"
        echo ""
    fi

    # Git状态
    if [ -d "$PROJECT_DIR/.git" ]; then
        echo -e "${GRAY}🔧 Git 状态${NC}"

        cd "$PROJECT_DIR" || exit 1

        # 最近5次提交
        commits=$(git log --oneline -5 2>/dev/null)
        if [ -n "$commits" ]; then
            echo "  最近5次提交:"
            echo "$commits" | while read -r line; do
                echo -e "    $line" "${GRAY}"
            done
        fi

        # 当前分支
        branch=$(git branch --show-current 2>/dev/null)
        if [ -n "$branch" ]; then
            echo "  当前分支: $branch"
        fi

        # 未提交更改
        status=$(git status --short 2>/dev/null)
        if [ -n "$status" ]; then
            echo -e "  未提交更改:" "${YELLOW}"
            echo "$status" | while read -r line; do
                echo -e "    $line" "${YELLOW}"
            done
        else
            echo -e "  工作目录干净" "${GREEN}"
        fi

        cd - > /dev/null || exit 1
        echo ""
    fi

    # 底部信息
    echo -e "${CYAN}${separator}${NC}"

    # 根据完成度选择颜色
    if [ "$percentage" -ge 80 ]; then
        echo -e "${CYAN}  完成度: ${GREEN}${percentage}%${NC}"
    elif [ "$percentage" -ge 50 ]; then
        echo -e "${CYAN}  完成度: ${YELLOW}${percentage}%${NC}"
    else
        echo -e "${CYAN}  完成度: ${RED}${percentage}%${NC}"
    fi

    echo -e "${CYAN}${separator}${NC}"
    echo ""
}

main
