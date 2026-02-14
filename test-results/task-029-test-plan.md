# Task-029: 登录注册页面测试计划

## 测试环境
- **前端服务器**: http://localhost:5173
- **后端服务器**: http://localhost:5000
- **测试工具**: Chrome DevTools MCP
- **测试页面**: HomePage (登录/注册页面)

## Chrome DevTools MCP 测试命令

### 1. 导航到登录页面
```javascript
chrome_devtools_navigate_page(url)
```
参数:
- `url`: "http://localhost:5173"

### 2. 获取页面快照
```javascript
chrome_devtools_take_snapshot({
  include_snapshot: true
})
```

### 3. 测试登录功能
```javascript
// 填写邮箱
chrome_devtools_evaluate_script({
  function: `(email) => {
    document.querySelector('input[type="email"]').value = email;
  }`,
  args: ["test@example.com"]
})

// 填写密码
chrome_devtools_evaluate_script({
  function: `(password) => {
    document.querySelector('input[type="password"]').value = password;
  }`,
  args: ["TestPass123"]
})

// 点击登录按钮
chrome_devtools_click({
  uid: "<登录按钮的uid>",
  includeSnapshot: true
})
```

### 4. 测试注册功能
```javascript
// 切换到注册模式
chrome_devtools_click({
  uid: "<注册按钮的uid>"
})

// 填写表单
chrome_devtools_evaluate_script({
  function: `(data) => {
    document.querySelector('input[placeholder*="姓名"]').value = data.name;
    document.querySelector('input[type="email"]').value = data.email;
    document.querySelector('input[placeholder*="确认密码"]').value = data.password;
    document.querySelector('input[placeholder*="再次输入密码"]').value = data.password;
  }`,
  args: [{
    name: "测试用户",
    email: "register@example.com",
    password: "TestPass123"
  }]
})

// 点击注册按钮
chrome_devtools_click({
  uid: "<注册按钮的uid>",
  includeSnapshot: true
})
```

### 5. 测试表单验证
```javascript
// 测试无效邮箱
chrome_devtools_evaluate_script({
  function: `() => {
    document.querySelector('input[type="email"]').value = "invalid-email";
    document.querySelector('button[type="submit"]').click();
  }`
})

// 等待错误提示
chrome_devtools_wait_for({
  text: "邮箱格式不正确",
  timeout: 3000
})

// 截图保存证据
chrome_devtools_take_screenshot({
  filePath: "test-results/screenshots/task-029-validation-error.png"
})
```

## 测试场景清单

### 场景 1: 正常登录流程 ✅
- [ ] 导航到 http://localhost:5173
- [ ] 确认显示"登录您的账户"
- [ ] 输入有效邮箱和密码
- [ ] 点击登录按钮
- [ ] 验证显示"登录成功！"
- [ ] 验证跳转到 /dashboard
- [ ] 截图保存

### 场景 2: 正常注册流程 ✅
- [ ] 导航到 http://localhost:5173
- [ ] 点击"注册"tab
- [ ] 确认显示"创建新账户"
- [ ] 输入姓名、邮箱、密码、确认密码
- [ ] 点击注册按钮
- [ ] 验证显示"注册成功！正在自动登录..."
- [ ] 验证跳转到 /dashboard
- [ ] 截图保存

### 场景 3: 表单验证 - 无效邮箱 ✅
- [ ] 在登录/注册模式
- [ ] 输入无效邮箱格式（如 "test"）
- [ ] 触发验证（失去焦点或提交）
- [ ] 验证显示错误提示"邮箱格式不正确"
- [ ] 截图保存

### 场景 4: 表单验证 - 短密码 ✅
- [ ] 在注册模式
- [ ] 输入5字符密码
- [ ] 触发验证
- [ ] 验证显示错误提示"密码至少需要6个字符"
- [ ] 截图保存

### 场景 5: 表单验证 - 密码不匹配 ✅
- [ ] 在注册模式
- [ ] 输入密码和不同的确认密码
- [ ] 触发验证
- [ ] 验证显示错误提示"两次输入的密码不一致"
- [ ] 截图保存

### 场景 6: 密码显示切换 ✅
- [ ] 点击密码显示/隐藏按钮
- [ ] 验证密码在显示和隐藏之间切换
- [ ] 截图保存

### 场景 7: 记住我功能 ✅
- [ ] 在登录模式
- [ ] 勾选"记住我"复选框
- [ ] 登录成功
- [ ] 验证 token 保存到 localStorage
- [ ] 刷新页面
- [ ] 验证仍然保持登录状态
- [ ] 截图保存

### 场景 8: 登录失败 - 错误处理 ✅
- [ ] 输入错误的邮箱或密码
- [ ] 点击登录按钮
- [ ] 验证显示错误提示"登录失败，请检查邮箱和密码"
- [ ] 截图保存

### 场景 9: API 错误处理 ✅
- [ ] 断开后端服务器
- [ ] 尝试登录或注册
- [ ] 验证显示友好的错误提示
- [ ] 截图保存

### 场景 10: 加载状态 ✅
- [ ] 提交登录/注册表单
- [ ] 验证按钮显示加载动画
- [ ] 验证按钮文字显示"登录中..."或"注册中..."
- [ ] ���证加载期间按钮禁用
- [ ] 截图保存

### 场景 11: Enter 键提交 ✅
- [ ] 在密码输入框按 Enter 键
- [ ] 验证触发表单提交
- [ ] 截图保存

### 场景 12: 模式切换 ✅
- [ ] 在登录模式点击"注册"tab
- [ ] 验证切换到注册表单
- [ ] 验证清空表单数据
- [ ] 验证清空错误提示
- [ ] 在注册模式点击"登录"tab
- [ ] 验证切换回登录表单
- [ ] 截图保存

## 测试结果记录模板

### 测试场景 X：[场景名称]
**测试时间**: 2026-02-14 HH:MM:SS
**测试结果**: ✅ 通过 / ❌ 失败
**期望行为**: [描述期望的行为]
**实际行为**: [描述实际观察到的行为]
**截图**: test-results/screenshots/task-029-scene-x.png
**备注**: [任何额外的观察或问题]

## 测试完成标准

- [ ] 所有 12 个测试场景执行完成
- [ ] 每个场景都有截图证据
- [ ] 所有期望行为验证通过
- [ ] 无阻塞性问题
- [ ] 用户体验符合预期

## 发现的问题记录

### 问题 1: [问题描述]
- **严重程度**: Critical / High / Medium / Low
- **重现步骤**: [如何重现]
- **预期行为**: [应该发生什么]
- **实际行为**: [实际发生了什么]
- **截图**: [问题截图路径]
