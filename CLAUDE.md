# ScholarAI - Claude Code 工作指南

## 测试凭据

### 用户账号
- **Email**: `test@qq.com`
- **Password**: `Test123456`

**说明**: 所有测试流程使用此���号登录。

### API Keys

#### 智谱AI API
- **API Key**: `1c27785e91624438af006527c35bdc07.2Xmz8XG6ZM9n3MXn`
- **免费模型**:
  - `glm-4-flash` (推荐)
  - `glm-4-flashx`
  - `glm-4-air`

**说明**: 测试所有AI功能（聊天、摘要、论文分析等）时使用此API Key。

---

## 开发工作流程

### 每次任务完成后的强制测试流程

**重要**: 每次实现或修改功能后，**必须**使用 Chrome DevTools MCP 进行浏览器测试验证。

#### 测试步骤

1. **启动服务器**
   ```bash
   # 后端
   cd backend && python run.py

   # 前端
   cd frontend && npm run dev
   ```

2. **使用 Chrome DevTools MCP 进行测试**
   - 导航到测试页面: `mcp__chrome-devtools__navigate_page`
   - 获取页面快照: `mcp__chrome-devtools__take_snapshot`
   - 截取测试证据: `mcp__chrome-devtools__take_screenshot`
   - 填写表单/点击按钮: `mcp__chrome-devtools__fill` / `mcp__chrome-devtools__click`
   - 执行JavaScript: `mcp__chrome-devtools__evaluate_script`

3. **验证清单**
   - [ ] 页面正常加载
   - [ ] 表单验证正确
   - [ ] API调用成功（检查network请求）
   - [ ] 用户反馈正确（成功/错误消息）
   - [ ] 控制台无JavaScript错误
   - [ ] UI布局正确显示
   - [ ] 响应式设计正常

4. **保存测试证据**
   - 所有截图保存到: `test-results/screenshots/`
   - 文件命名: `task-{id}-{scenario}-{status}.png`
   - 示例: `task-029-login-success.png`

5. **更新任务状态**
   - 只有**所有测试通过**后才能标记任务完成
   - 测试失败必须修复代码或记录问题

---

## 核心功能测试流程

### 1. 用户认证 (task-029)

**测试账号**: test@qq.com / Test123456

**验证步骤**:
1. 导航到 `http://localhost:5173/login`
2. 填写邮箱和密码
3. 验证表单验证（无效邮箱/短密码应显示错误）
4. 填写有效凭据并登录
5. 验证登录成功后跳转到仪表板
6. 验证 token 存储到 localStorage
7. 截图保存所有关键步骤

**API端点**:
- `POST /api/auth/login`
- `GET /api/auth/me`

### 2. 论文搜索 (task-021, task-030)

**验证步骤**:
1. 登录后导航天到 `http://localhost:5173/search`
2. 输入搜索关键词（如"deep learning"）
3. 验证搜索结果展示
4. 验证分页功能
5. 点击论文查看详情
6. 验证搜索历史和过滤功能

**API端点**:
- `GET /api/papers/search`
- `GET /api/papers/details/:id`

### 3. AI聊天助手 (task-023, task-031)

**智谱API Key**: `1c27785e91624438af006527c35bdc07.2Xmz8XG6ZM9n3MXn`

**验证步骤**:
1. 导航到 `http://localhost:5173/ai-chat`
2. 输入问题并测试流式响应
3. 验证实时打字效果
4. 验证Markdown渲染
5. 验证对话历史
6. 测试关联论文问答
7. 截图保存流式输出过程

**API端点**:
- `POST /api/ai/chat/stream`
- `POST /api/ai/mindmap`

### 4. 项目管理 (task-025, task-033)

**验证步骤**:
1. 导航到 `http://localhost:5173/projects`
2. 创建新项目
3. 添加论文到项目
4. 更新论文阅读状态
5. 验证进度统计
6. 编辑和删除项目
7. 截图保存所有CRUD操作

**API端点**:
- `GET /api/projects`
- `POST /api/projects`
- `PUT /api/projects/:id`
- `DELETE /api/projects/:id`
- `POST /api/projects/:id/papers`

### 5. 收藏管理 (task-026)

**验证步骤**:
1. 在搜索结果页面点击收藏按钮
2. 导航到收藏页面 `http://localhost:5173/favorites`
3. 验证收藏项显示
4. 创建收藏文件夹
5. 移动收藏到文件夹
6. 添加笔记和标签
7. 取消收藏

**API端点**:
- `GET /api/favorites`
- `POST /api/favorites/toggle`
- `PUT /api/favorites/:id`
- `DELETE /api/favorites/:id`

### 6. 文件上传 (task-028)

**验证步骤**:
1. 导航到论文详情页
2. 点击上传按钮
3. 选择PDF文件或输入URL
4. 验证上传进度显示
5. 验证上传成功提示
6. 截图保存进度条

**API端点**:
- `POST /api/upload/file`
- `POST /api/upload/url`
- `POST /api/knowledge/upload`

### 7. 用户设置 (task-027)

**验证步骤**:
1. 导航到 `http://localhost:5173/settings`
2. 切换主题（light/dark/system）
3. 切换语言（zh-CN/en-US）
4. 配置智谱API Key
5. 验证加密存储
6. 查看使用统计
7. 截图保存所有设置变更

**API端点**:
- `GET /api/settings`
- `PUT /api/settings`
- `GET /api/settings/stats`
- `POST /api/settings/api-config`

---

## Chrome DevTools MCP 测试命令参考

### 基础操作
```javascript
// 导航到页面
mcp__chrome-devtools__navigate_page("http://localhost:5173/path")

// 获取页面快照
mcp__chrome-devtools__take_snapshot()

// 截图（保存测试证据）
mcp__chrome-devtools__take_screenshot({
  filePath: "test-results/screenshots/task-xxx-test-name.png"
})

// 点击元素
mcp__chrome-devtools__click({ uid: "1_10" })

// 填写表单
mcp__chrome-devtools__fill({
  uid: "1_5",
  value: "test value"
})
```

### 高级操作
```javascript
// 执行JavaScript
mcp__chrome-devtools__evaluate_script({
  function: `() => {
    // 你的测试代码
    return document.querySelector('h1').textContent;
  }`
})

// 列出网络请求
mcp__chrome-devtools__list_network_requests({
  pageSize: 50
})

// 列出控制台消息
mcp__chrome-devtools__list_console_messages({
  types: ["error"],
  pageSize: 50
})
```

### 常用测试脚本

#### 登录脚本
```javascript
mcp__chrome-devtools__evaluate_script({
  function: `(email, password) => {
    const emailInput = document.querySelector('input[type="email"]');
    const passwordInput = document.querySelector('input[type="password"]');

    if (emailInput) {
      emailInput.value = email;
      emailInput.dispatchEvent(new Event('input', { bubbles: true }));
    }

    if (passwordInput) {
      passwordInput.value = password;
      passwordInput.dispatchEvent(new Event('input', { bubbles: true }));
    }

    return { success: true };
  }`,
  args: ["test@qq.com", "Test123456"]
})
```

#### 检查API调用
```javascript
// 获取最新的API请求
const requests = await mcp__chrome-devtools__list_network_requests({ pageSize: 20 });
const apiCalls = requests.filter(r => r.url.includes('/api/'));
console.log('API调用:', apiCalls);
```

#### 检查控制台错误
```javascript
const errors = await mcp__chrome-devtools__list_console_messages({
  types: ["error"],
  pageSize: 50
});

if (errors.length > 0) {
  throw new Error(`发现 ${errors.length} 个控制台错误`);
}
```

---

## 测试报告模板

每次完成任务后，生成测试报告保存到 `Progress-Logs/task-xxx-summary.md`:

```markdown
# Task-XXX 测试报告

## 功能描述
[简要描述实现的功能]

## 测试环境
- 前端: http://localhost:5173
- 后端: http://localhost:5000
- 测试账号: test@qq.com / Test123456
- 智谱API: 1c27785e91624438af006527c35bdc07.2Xmz8XG6ZM9n3MXn

## 测试步骤

### ✅ 步骤1: [步骤名称]
- 操作: [具体操作]
- 预期结果: [预期结果]
- 实际结果: [实际结果]
- 截图: `test-results/screenshots/task-xxx-step1.png`

### ✅ 步骤2: [步骤名称]
...

## 发现的问题

### [如果无问题则写"无"]

## 测试结论

**状态**: ✅ 通过 / ❌ 失败

**说明**: [测试通过或失败的说明]

**改进建议**: [如果有问题，提出改进建议]

## 测试截图

1. `task-xxx-step1.png` - [截图说明]
2. `task-xxx-step2.png` - [截图说明]
...
```

---

## 重要提醒

### ⚠️ 测试是强制步骤
- **代码能运行 ≠ 功能正确**
- **必须使用浏览器验证真实用户交互**
- **测试失败不能标记任务完成**

### ✅ 质量守门规则
1. **UI修改**: 必须浏览器测试（表单、按钮、导航）
2. **API集成**: 必须验证API调用和错误处理
3. **用户反馈**: 必须验证成功/失败消息显示
4. **响应式**: 必须验证不同屏幕尺寸（可选）
5. **控制台**: 必须无JavaScript错误

### 📸 测试证据保存
- 所有截图按规范命名
- 保存到 `test-results/screenshots/`
- 测试报告保存到 `Progress-Logs/`

---

## 快速参考

### 端口信息
- 前端: `http://localhost:5173`
- 后端: `http://localhost:5000`
- 后端API前缀: `/api`

### 数据库
- MongoDB: `mongodb+srv://root:<ttTT23772377>@cluster0.p3qi0gw.mongodb.net/?appName=Cluster0`

### API文档端点
- Swagger/ReDoc: `[TODO: 如果实现则添加URL]`

---

## 下次任务提示

开始任务前，检查：
1. [ ] 后端服务器运行 (`python backend/run.py`)
2. [ ] 前端服务器运行 (`cd frontend && npm run dev`)
3. [ ] 已读取此文件了解测试账号和API Keys
4. [ ] 准备好使用Chrome DevTools MCP进行测试

---

**最后更新**: 2026-02-14
**维护者**: Claude Code Agent
