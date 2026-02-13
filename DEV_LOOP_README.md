# 自动化开发循环脚本使用指南

## 概述

这套脚本用于自动化调用Claude Code执行ScholarAI项目的开发流程。它会循环执行指定次数的开发迭代，每次自动：
1. 从tasks.json中选择下一个未完成任务
2. 调用Claude Code完成该任务
3. 自动提交代码
4. 更新任务状态
5. 生成会话总结

## 脚本文件

- `run-dev-loop.sh` - Bash版本（Linux/Git Bash/WSL）
- `run-dev-loop.bat` - Windows批处理版本
- `run-dev-loop.ps1` - PowerShell版本（推荐Windows使用）
- `check-progress.sh` / `check-progress.ps1` - 进度查看脚本

## 使用方法

### Windows（推荐PowerShell）

```powershell
# 运行5次开发循环
.\run-dev-loop.ps1 5

# 运行10��开发循环
.\run-dev-loop.ps1 10
```

**注意**: 首次运行可能需要执行以下命令允许脚本执行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Windows（批处理）

```cmd
run-dev-loop.bat 5
```

### Linux/Git Bash/WSL

```bash
# 给脚本添加执行权限
chmod +x run-dev-loop.sh
chmod +x check-progress.sh

# 运行5次开发循环
./run-dev-loop.sh 5
```

## 脚本功能

### 自动化流程

每次迭代会自动执行以下步骤：

1. **检查任务状态**
   - 读取tasks.json
   - 统计剩余未完成任务
   - 如果所有任务完成，自动退出

2. **选择下一个任务**
   - 按优先级排序（Priority 1最高）
   - 跳过已完成的任务
   - 显示待执行任务信息

3. **调用Claude Code**
   - 传递项目上下文信息
   - 传递开发流程指引
   - 传递当前任务ID

4. **记录日志**
   - 所有操作记录到dev-loop.log
   - 包含时间戳和状态信息
   - 记录每次迭代的耗时

5. **错误处理**
   - 如果Claude执行失败，询问是否继续
   - 支持用户中断执行

### 日志输出示例

```
========================================
迭代 #1 / 5
========================================
[INFO] 剩余未完成任务: 20
[INFO] 下一个任务: task-019 | 创建前端API服务层基础架构 | Priority: 1
[INFO] 调用Claude Code...
[INFO] 执行中...
[SUCCESS] 迭代完成 (耗时: 245秒)
```

## 查看进度

### PowerShell

```powershell
.\check-progress.ps1
```

### Bash

```bash
./check-progress.sh
```

这会显示：
- 总任务数
- 已完成任务数
- 进行中任务
- 待办任务数
- 完成百分比
- 最近5次git提交

## 配置选项

### 修改Claude Code参数

编辑脚本中的`claude`命令调用部分，根据实际CLI参数调整：

常见参数：
- `--yes` - 自动确认所有提示
- `--no-input` - 非交互模式
- `--allow-dangerous` - 允许危险操作
- `--bypass-permissions` - 跳过权限检查

### 修改项目路径

脚本会自动检测项目目录（脚本所在目录），通常不需要修改。

如需指定其他目录：
```bash
# Bash版本
PROJECT_DIR=/path/to/project ./run-dev-loop.sh 5

# PowerShell版本
$env:PROJECT_DIR="C:\path\to\project"; .\run-dev-loop.ps1 5
```

## 注意事项

1. **Claude Code CLI必须安装**
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Git必须配置**
   - 确保在git仓库中
   - 配置了用户名和邮箱

3. **Python必须安装**
   - 用于解析tasks.json
   - Python 3.7+

4. **环境变量**
   - 如果需要API密钥，确保.env文件已配置

5. **网络连接**
   - 需要访问Claude API
   - 需要访问arXiv和智谱AI（如使用）

## 故障排查

### 问题：脚本无法执行（PowerShell）

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 问题：找不到claude命令

确保Claude Code已安装：
```bash
npm install -g @anthropic-ai/claude-code
```

或使用完整路径：
```bash
C:\Users\YourName\AppData\Roaming\npm\claude "prompt" --yes
```

### 问题：tasks.json解析错误

确保Python正确安装：
```bash
python --version
```

### 问题：Git提交失败

确保git已配置：
```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

## 工作流程建议

1. **首次运行前**
   - 确保所有服务可以启动（前端/后端）
   - 运行一次完整测试：`npm test`
   - 检查git状态：`git status`

2. **运行循环**
   ```bash
   .\run-dev-loop.ps1 10
   ```

3. **监控进度**
   - 查看日志：`cat dev-loop.log`
   - 查看任务：`.\check-progress.ps1`
   - 查看git历史：`git log --oneline -10`

4. **完成后**
   - 运行完整测试套件
   - 检查代码覆盖率
   - 部署到测试环境

## 自定义

### 修改提示词

编辑脚本中的`PROMPT`变量，添加自定义指令。

### 修改日志位置

修改`PROGRESS_LOG`变量，指定其他日志文件。

### 添加邮件通知

在脚本末尾添加：
```bash
# 发送完成通知
echo "开发循环完成" | mail -s "通知" your@email.com
```

## 许可

这些脚本是ScholarAI项目的一部分，遵循项目许可协议。
