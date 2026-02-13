# 自动化开发循环脚本使用指南

## 概述

`run-dev-cycle.sh` 和 `run-dev-cycle.ps1` 是为 ScholarAI 项目设计的自动化开发脚本。它们可以：

1. 自动从 `tasks.json` 选择下一个待办任务
2. 调用 Claude Code 执行完整的开发流程
3. 自动提交代码并更新任务状态
4. 显示详细的进度日志
5. 支持多次循环运行

## 前提条件

### 必需
- Claude Code CLI 已安装并配置
- Git 已初始化
- `tasks.json` 文件存在
- `progress.json` 文件存在

### Claude Code CLI 配置

确保 `claude` 命令可用：
```bash
# 检查安装
claude --version

# 如果未安装，参考官方文档安装
```

## 使用方法

### Linux / macOS / Git Bash

```bash
# 运行5次开发循环
./run-dev-cycle.sh 5

# 运行10次
./run-dev-cycle.sh 10

# 先添加执行权限（首次运行）
chmod +x run-dev-cycle.sh
```

### Windows PowerShell

```powershell
# 运行5次开发循环
.\run-dev-cycle.ps1 -Cycles 5

# 运行10次
.\run-dev-cycle.ps1 -Cycles 10
```

## 工作流程

每次循环执行以下步骤：

```
┌─────────────────────────────────────────┐
│ 1. 读取项目状态                  │
│    - progress.json (历史工作)       │
│    - tasks.json (待办任务)         │
│    - git log (最近提交)           │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 2. 选择下一个任务                  │
│    - 优先级最高的 pending 任务      │
│    - 依赖已满足                   │
│    - 状态改为 in_progress          │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 3. 调用 Claude Code              │
│    - 传递固定prompt                │
│    - --accept-all 自动接受权限       │
│    - 实现任务功能                 │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 4. 提交更改                      │
│    - git add 修改文件              │
│    - git commit (conventional format) │
│    - 更新 tasks.json → completed    │
│    - 更新 progress.json             │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 5. 输出总结                       │
│    - 完成的任务ID/标题            │
│    - 修改的文件列表                 │
│    - 项目整体进度 (X/总数)          │
└─────────────────────────────────────────┘
```

## 日志输出示例

```
[INFO] 2025-02-13 12:00:00 - 项目根目录: /d/ai/fullstack-merged
========================================
ScholarAI 自动化开发流程启动
========================================
[INFO] 2025-02-13 12:00:01 - 计划运行 5 次开发循环
[INFO] 2025-02-13 12:00:01 - 项目目录: /d/ai/fullstack-merged
[INFO] 2025-02-13 12:00:02 - 当前状态: 0/18 已完成, 18 待处理
[INFO] 2025-02-13 12:00:03 - 将执行 5 次循环（最多处理所有pending任务）

========================================
循环 1/5
========================================
[INFO] 2025-02-13 12:00:04 - 下一个任务: task-001
[INFO] 2025-02-13 12:00:05 - 启动Claude Code进行开发...
[SUCCESS] 2025-02-13 12:05:30 - 循环 1 完成
[INFO] 2025-02-13 12:05:31 - 进度更新: 1/18 已完成, 17 待处理
```

## 传给 Claude 的 Prompt

每次循环会传递固定的 prompt，包含：

1. **读取项目状态** - 查看 progress.json、tasks.json、git log
2. **选择任务** - 从 tasks.json 选择优先级最高且依赖满足的 pending 任务
3. **实现任务** - 根据 verification_steps 实现，编写测试
4. **提交更改** - git add/commit，更新 tasks.json 和 progress.json
5. **输出总结** - 完成的任务、修改的文件、进度

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `-Cycles <n>` | 循环次数 | `-Cycles 5` |
| 位置参数 | 循环次数 | `./run-dev-cycle.sh 5` |

## 错误处理

- **Git 未初始化**: 脚本会报错退出
- **tasks.json 缺失**: 脚本会报错退出
- **Claude 未安装**: 脚本会报错退出
- **Claude 执行失败**: 会询问是否继续，输入 `y` 继续，`n` 退出

## 停止脚本

- **Linux/Mac**: `Ctrl + C`
- **Windows**: `Ctrl + C`

## 注意事项

1. **自动接受权限**: 使用 `--accept-all` 参数，无需手动确认
2. **一次一任务**: Claude 被指示每次只完成一个任务
3. **Git 提交**: 每次循环结束会自动提交代码
4. **进度跟踪**: 自动更新 tasks.json 和 progress.json
5. **等待时间**: 每次循环后等待3秒，避免过快调用

## 示例场景

### 场景1: 完成所有任务

```bash
# 假设有18个待办任务
./run-dev-cycle.sh 20

# 脚本会在完成所有18个任务后自动停止
# 实际只执行18次循环
```

### 场景2: 分批完成

```bash
# 第一批：完成5个任务
./run-dev-cycle.sh 5

# 第二批：再完成5个
./run-dev-cycle.sh 5
```

### 场景3: 单个任务测试

```bash
# 只运行1次，测试脚本
./run-dev-cycle.sh 1
```

## 故障排查

### 问题：Claude 命令未找到

**解决方案**: 确保 Claude Code CLI 已安装并在 PATH 中
```bash
# 检查
claude --version

# 如果未安装，参考官方文档
```

### 问题：tasks.json 格式错误

**解决方案**: 确保 JSON 格式正确
```bash
# 验证 JSON
cat tasks.json | jq .

# 或使用 node
node -e "console.log(require('./tasks.json'))"
```

### 问题：Git 有未提交更改

**解决方案**: 脚本会警告但不会停止。手动检查：
```bash
git status
```

## 进度文件

### tasks.json

```json
{
  "tasks": [
    {
      "id": "task-001",
      "status": "pending",  // pending | in_progress | completed
      "priority": 1,
      ...
    }
  ]
}
```

### progress.json

```json
{
  "current_session": {
    "session_id": "session-xxx",
    "work_completed": ["task-001"]
  },
  "history": [
    {
      "task_id": "task-001",
      "action": "completed",
      "timestamp": "2025-02-13T12:00:00Z"
    }
  ]
}
```

## 更新日志

- 2025-02-13: 初始版本，支持 Bash 和 PowerShell
