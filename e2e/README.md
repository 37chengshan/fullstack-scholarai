# ScholarAI E2E 测试

此目录包含 ScholarAI 应用的端到端 (E2E) 测试，使用 [Playwright](https://playwright.dev/) 框架。

## 目录

- [快速开始](#快速开始)
- [测试场景](#测试场景)
- [运行测试](#运行测试)
- [编写测试](#编写测试)
- [故障排查](#故障排查)

---

## 快速开始

### 前置要求

1. **启动后端服务器**：
   ```bash
   cd backend
   python run.py
   ```
   ��端将运行在 `http://localhost:5000`

2. **启动前端服务器**：
   ```bash
   cd frontend
   npm run dev
   ```
   前端将运行在 `http://localhost:5173`

3. **安装 E2E 测试依赖**：
   ```bash
   cd e2e
   npm install
   npx playwright install
   ```

---

## 测试场景

### 1. 认证流程 (`auth.spec.ts`)

测试用户注册、登录和登出功能：
- ✅ 用户注册
- ✅ 用户登录
- ✅ 用户登出
- ✅ 无效凭证处理
- ✅ 邮箱格式验证

### 2. 论文搜索和详情 (`papers.spec.ts`)

测试论文搜索、详情查看和交互：
- ✅ 关键词搜索
- ✅ 查看论文详情
- ✅ 年份过滤
- ✅ 添加到收藏夹
- ✅ 加载更多结果
- ✅ PDF 链接显示

### 3. AI 助手 (`ai-assistant.spec.ts`)

测试 AI 聊天、摘要生成和思维导图功能：
- ✅ 打开 AI 聊天面板
- ✅ 发送消息给 AI
- ✅ 生成论文摘要
- ✅ 生成研究大纲
- ✅ 生成思维导图
- ✅ 显示对话历史
- ✅ 错误处理

### 4. 项目管理 (`projects.spec.ts`)

测试项目创建、论文管理功能：
- ✅ 创建新项目
- ✅ 添加论文到项目
- ✅ 更新论文阅读状态
- ✅ 删除项目
- ✅ 显示项目进度
- ✅ 编辑项目详情

### 5. 收藏夹管理 (`favorites.spec.ts`)

测试收藏夹文件夹组织和论文收藏：
- ✅ 创建收藏夹文件夹
- ✅ 添加论文到收藏
- ✅ 从收藏移除论文
- ✅ 添加笔记
- ✅ 移动到文件夹
- ✅ 按文件夹过滤
- ✅ 编辑文件夹
- ✅ 删除文件夹

---

## 运行测试

### 运行所有测试

```bash
npm test
```

### 运行特定测试文件

```bash
npx playwright test auth.spec.ts
```

### 运行特定测试

```bash
npx playwright test -g "should login existing user"
```

### 调试模式（可视化）

```bash
npm run test:headed
```

### UI 模式（交互式）

```bash
npm run test:ui
```

### 调试特定测试

```bash
npm run test:debug
```

---

## 测试报告

测试完成后，HTML 报告将自动生成：

```bash
npm run report
```

或在 `playwright-report/index.html` 中查看。

---

## 编写测试

### 测试模板

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup before each test
    await page.goto('/');
  });

  test('should do something', async ({ page }) => {
    // Test implementation
    await expect(page.locator('element')).toBeVisible();
  });
});
```

### 最佳实践

1. **使用 Page Object Model**：将页面选择器封装为可重用的对象
2. **等待元素**：使用 `await expect().toBeVisible()` 而不是固定延迟
3. **清晰命名**：测试名称应该描述正在测试的功能
4. **独立测试**：每个测试应该能独立运行
5. **清理数据**：使用 `test.afterEach` 清理测试数据

---

## 故障排查

### 问题：测试失败 "Element not found"

**解决方案**：
1. 确保后端和前端服务器都在运行
2. 增加超时时间：`test.setTimeout(60000)`
3. 检查选择器是否正确

### 问题：MongoDB 连接失败

**解决方案**：
1. 检查 `.env` 文件配置
2. 确保数据库正在运行
3. 验证连接字符串

### 问题：AI API 调用失败

**解决方案**：
1. 检查 `ZHIPU_API_KEY` 是否配置
2. 验证 API 密钥是否有效
3. 检查 API 额度

### 问题：前端启动超时

**解决方案**：
1. 手动启动前端：`cd frontend && npm run dev`
2. 在 `playwright.config.ts` 中增加超时：
   ```typescript
   webServer: {
     timeout: 180 * 1000, // 3 minutes
   }
   ```

---

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: |
          cd e2e
          npm install
          npx playwright install --with-deps

      - name: Run tests
        run: npm test

      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: e2e/playwright-report/
```

---

## 相关文档

- [Playwright 官方文档](https://playwright.dev/)
- [项目部署文档](../deployment/DEPLOYMENT.md)
- [API 文档](../backend/API_TESTING_GUIDE.md)
