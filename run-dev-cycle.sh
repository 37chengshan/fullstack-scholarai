#!/bin/bash
#
# ScholarAI 自动化开发循环脚本
#
# 用法: ./run-dev-cycle.sh <次数>
# 示例: ./run-dev-cycle.sh 5  # 运行5次开发循环
#
# 功能:
# - 每次调用Claude Code执行一个完整的开发任务
# - 自动从tasks.json中选取pending任务
# - 完成后更新任务状态并提交Git commit
# - 显示详细进展日志
#

set -e  # 遇到错误立即退出

# ===========================================
# 颜色定义
# ===========================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ===========================================
# 日志函数
# ===========================================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_section() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

# ===========================================
# 参数检查
# ===========================================
if [ -z "$1" ]; then
    log_error "缺少参数！"
    echo "用法: $0 <循环次数>"
    echo "示例: $0 5  # 运行5次开发循环"
    exit 1
fi

CYCLES=$1
if ! [[ "$CYCLES" =~ ^[0-9]+$ ]]; then
    log_error "参数必须是正整数！"
    exit 1
fi

# ===========================================
# 环境检查
# ===========================================
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

log_info "项目根目录: $PROJECT_ROOT"

# 检查claude命令是否可用
if ! command -v claude &> /dev/null; then
    log_error "Claude Code命令未找到！请确保已安装Claude Code CLI。"
    exit 1
fi

# 检查tasks.json是否存在
if [ ! -f "tasks.json" ]; then
    log_error "tasks.json文件不存在！"
    exit 1
fi

# ===========================================
# 统计函数
# ===========================================
get_pending_count() {
    node -e "
    const tasks = require('./tasks.json');
    const pending = tasks.tasks.filter(t => t.status === 'pending');
    console.log(pending.length);
    " 2>/dev/null || echo "0"
}

get_completed_count() {
    node -e "
    const tasks = require('./tasks.json');
    const completed = tasks.tasks.filter(t => t.status === 'completed');
    console.log(completed.length);
    " 2>/dev/null || echo "0"
}

get_next_task() {
    node -e "
    const tasks = require('./tasks.json');
    const pending = tasks.tasks
        .filter(t => t.status === 'pending')
        .sort((a, b) => a.priority - b.priority);
    if (pending.length > 0) {
        console.log(pending[0].id);
    } else {
        console.log('NONE');
    }
    " 2>/dev/null || echo "NONE"
}

# ===========================================
# Git状态检查
# ===========================================
check_git_status() {
    if [ -d ".git" ]; then
        local status=$(git status --porcelain 2>/dev/null | wc -l)
        echo "$status"
    else
        echo "0"
    fi
}

# ===========================================
# 主循环
# ===========================================
log_section "ScholarAI 自动化开发流程启动"
log_info "计划运行 $CYCLES 次开发循环"
log_info "项目目录: $PROJECT_ROOT"

PENDING_BEFORE=$(get_pending_count)
COMPLETED_BEFORE=$(get_completed_count)
TOTAL_TASKS=$(node -e "console.log(require('./tasks.json').tasks.length)" 2>/dev/null || echo "0")

log_info "当前状态: $COMPLETED_BEFORE/$TOTAL_TASKS 已完成, $PENDING_BEFORE 待处理"

if [ "$PENDING_BEFORE" -eq 0 ]; then
    log_warning "没有待处理的任务！脚本退出。"
    exit 0
fi

# 实际运行次数（不超过pending任务数）
ACTUAL_CYCLES=$((CYCLES < PENDING_BEFORE ? CYCLES : PENDING_BEFORE))
log_info "将执行 $ACTUAL_CYCLES 次循环（最多处理所有pending任务）"

for ((i=1; i<=ACTUAL_CYCLES; i++)); do
    log_section "循环 $i/$ACTUAL_CYCLES"

    # 检查是否还有pending任务
    PENDING_CURRENT=$(get_pending_count)
    if [ "$PENDING_CURRENT" -eq 0 ]; then
        log_success "所有任务已完成！"
        break
    fi

    # 获取下一个任务
    NEXT_TASK=$(get_next_task)
    log_info "下一个任务: $NEXT_TASK"

    # 执行开发流程
    log_info "启动Claude Code进行开发..."

    # 构建Claude Code命令
    # 使用--accept-all自动接受所有permission
    # 传递固定的prompt让Claude从tasks.json取任务
    cat > /tmp/claude_prompt_$$.txt << 'EOF'
你现在是ScholarAI项目的开发助手。请执行以下流程：

1. 读取当前项目状态：
   - 查看progress.json了解历史工作
   - 查看tasks.json了解待办任务
   - 查看git log了解最近的提交

2. 选择一个任务：
   - 从tasks.json中选择优先级最高且依赖已满足的pending任务
   - 将任务状态从"pending"改为"in_progress"

3. 实现任务：
   - 根据任务的verification_steps实现功能
   - 编写测试代码
   - 运行测试确保通过

4. 提交更改：
   - 使用git add添加修改的文件
   - 使用git commit提交（遵循conventional commits格式）
   - 更新tasks.json，将任务状态改为"completed"
   - 更新progress.json，记录本次会话的工作

5. 输出总结：
   - 完成的任务ID和标题
   - 修改的文件列表
   - 测试结果
   - 项目整体进度（X/总数）

注意：
- 一次只完成一个任务，不要贪多
- 遇到不确定的地方，优先选择最简单的实现
- 确保代码可以运行后再提交
EOF

    # 调用Claude Code
    # 使用--permission-mode=acceptEdits自动接受编辑和工具使用
    log_info "执行命令: claude --permission-mode acceptEdits --prompt-file /tmp/claude_prompt_$$.txt"

    if claude --permission-mode acceptEdits --prompt-file /tmp/claude_prompt_$$.txt; then
        log_success "循环 $i 完成"

        # 检查Git状态
        GIT_CHANGES=$(check_git_status)
        if [ "$GIT_CHANGES" -gt 0 ]; then
            log_warning "检测到未提交的更改，请手动检查"
        fi

        # 更新统计
        COMPLETED_NOW=$(get_completed_count)
        PENDING_NOW=$(get_pending_count)
        log_info "进度更新: $COMPLETED_NOW/$TOTAL_TASKS 已完成, $PENDING_NOW 待处理"
    else
        log_error "循环 $i 失败！Claude Code返回错误。"

        # 询问是否继续
        read -p "是否继续下一个循环？[y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_warning "用户选择停止脚本"
            exit 1
        fi
    fi

    # 清理临时文件
    rm -f /tmp/claude_prompt_$$.txt

    # 短暂等待，避免过快连续调用
    if [ $i -lt $ACTUAL_CYCLES ]; then
        log_info "等待3秒后继续..."
        sleep 3
    fi
done

# ===========================================
# 最终总结
# ===========================================
log_section "开发流程完成"

COMPLETED_AFTER=$(get_completed_count)
PENDING_AFTER=$(get_pending_count)

log_success "执行总结:"
log_info "  - 计划循环: $CYCLES 次"
log_info "  - 实际执行: $ACTUAL_CYCLES 次"
log_info "  - 完成任务: $((COMPLETED_AFTER - COMPLETED_BEFORE)) 个"
log_info "  - 当前进度: $COMPLETED_AFTER/$TOTAL_TASKS"
log_info "  - 剩余任务: $PENDING_AFTER"

if [ "$PENDING_AFTER" -gt 0 ]; then
    log_info "还有 $PENDING_AFTER 个任务待完成，可再次运行脚本"
else
    log_success "🎉 所有任务已完成！"
fi
