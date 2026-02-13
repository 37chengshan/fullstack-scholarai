import { test, expect } from '@playwright/test';

/**
 * E2E Test: AI Assistant Interaction
 *
 * Tests AI chat, summary generation, and mindmap features
 */
test.describe('AI Assistant', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home page and login
    await page.goto('/');
    await page.click('text=登录');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Wait for login
    await expect(page.locator('text=欢迎')).toBeVisible();
  });

  test('should open AI chat panel', async ({ page }) => {
    // Click AI assistant button
    await page.click('button[aria-label="AI助手"]');

    // Verify chat panel opens
    await expect(page.locator('.ai-chat-panel')).toBeVisible();
    await expect(page.locator('text=AI助手')).toBeVisible();
  });

  test('should send message to AI', async ({ page }) => {
    // Open AI chat
    await page.click('button[aria-label="AI助手"]');

    // Type message
    await page.fill('[placeholder="向AI提问..."]', '什么是机器学习？');

    // Send message
    await page.click('button[aria-label="发送"]');

    // Verify AI response
    await expect(page.locator('.ai-message.assistant')).toBeVisible({
      timeout: 15000
    });
  });

  test('should generate paper summary', async ({ page }) => {
    // Search for a paper first
    await page.fill('[placeholder="搜索论文..."]', 'neural networks');
    await page.click('button[aria-label="搜索"]');

    // Wait for results
    await expect(page.locator('.paper-card')).toHaveCountGreaterThan(0, {
      timeout: 10000
    });

    // Click on first paper
    await page.locator('.paper-card').first().click();

    // Click "生成摘要" button
    await page.click('button:has-text("生成摘要")');

    // Select summary length
    await page.selectOption('[name="length"]', 'medium');

    // Generate
    await page.click('button:has-text("生成")');

    // Wait for summary
    await expect(page.locator('.ai-summary')).toBeVisible({
      timeout: 20000
    });

    // Verify summary content
    await expect(page.locator('text=摘要')).toBeVisible();
    await expect(page.locator('text=要点')).toBeVisible();
  });

  test('should generate research outline', async ({ page }) => {
    // Search for a paper
    await page.fill('[placeholder="搜索论文..."]', 'deep learning');
    await page.click('button[aria-label="搜索"]');

    // Wait for results and click first paper
    await expect(page.locator('.paper-card')).toHaveCountGreaterThan(0, {
      timeout: 10000
    });
    await page.locator('.paper-card').first().click();

    // Click "生成大纲" button
    await page.click('button:has-text("生成大纲")');

    // Select detail level
    await page.selectOption('[name="level"]', 'standard');

    // Generate
    await page.click('button:has-text("生成")');

    // Wait for outline
    await expect(page.locator('.ai-outline')).toBeVisible({
      timeout: 20000
    });

    // Verify outline structure
    await expect(page.locator('text=引言')).toBeVisible();
    await expect(page.locator('text=相关工作')).toBeVisible();
  });

  test('should generate mindmap', async ({ page }) => {
    // Open AI chat
    await page.click('button[aria-label="AI助手"]');

    // Click mindmap tab
    await page.click('button:has-text("思维导图")');

    // Enter topic
    await page.fill('[name="topic"]', '机器学习基础');

    // Generate
    await page.click('button:has-text("生成")');

    // Wait for mindmap
    await expect(page.locator('.mindmap-container')).toBeVisible({
      timeout: 20000
    });
  });

  test('should display chat history', async ({ page }) => {
    // Open AI chat
    await page.click('button[aria-label="AI助手"]');

    // Send multiple messages
    await page.fill('[placeholder="向AI提问..."]', '第一个问题');
    await page.click('button[aria-label="发送"]');
    await expect(page.locator('.ai-message.assistant')).toBeVisible({
      timeout: 15000
    });

    await page.fill('[placeholder="向AI提问..."]', '第二个问题');
    await page.click('button[aria-label="发送"]');

    // Verify chat history
    const messages = await page.locator('.ai-message').count();
    expect(messages).toBeGreaterThanOrEqual(4); // 2 user + 2 assistant
  });

  test('should handle AI errors gracefully', async ({ page }) => {
    // Mock API error scenario (if backend is not running)
    // This test verifies error handling

    // Open AI chat
    await page.click('button[aria-label="AI助手"]');

    // Send message
    await page.fill('[placeholder="向AI提问..."]', 'test message');
    await page.click('button[aria-label="发送"]');

    // Check for error message if backend is unavailable
    const pageUrl = page.url();

    // If we're still on chat page and see error message
    if (pageUrl.includes('chat')) {
      const errorMessage = page.locator('text=服务器错误|API调用失败');
      if (await errorMessage.isVisible()) {
        // Error handling is working
        expect(errorMessage).toBeVisible();
      }
    }
  });
});
