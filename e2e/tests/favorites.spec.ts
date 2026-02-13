import { test, expect } from '@playwright/test';

/**
 * E2E Test: Favorites Management
 *
 * Tests favorites folder organization and paper collection
 */
test.describe('Favorites Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/');
    await page.click('text=登录');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=欢迎')).toBeVisible();
  });

  test('should create favorites folder', async ({ page }) => {
    // Navigate to favorites
    await page.click('text=收藏');

    // Click "新建文件夹" button
    await page.click('button:has-text("新建文件夹")');

    // Fill folder details
    await page.fill('[name="name"]', '重要论文');
    await page.click('[name="color"]');

    // Select color
    await page.click('text=红色');

    // Create
    await page.click('button:has-text("创建")');

    // Verify folder created
    await expect(page.locator('text=重要论文')).toBeVisible();
  });

  test('should add paper to favorites', async ({ page }) => {
    // Search for papers
    await page.fill('[placeholder="搜索论文..."]', 'machine learning');
    await page.click('button[aria-label="搜索"]');

    // Wait for results
    await expect(page.locator('.paper-card')).toHaveCountGreaterThan(0, {
      timeout: 10000
    });

    // Toggle favorite on first paper
    await page.locator('.paper-card').first()
      .locator('button[aria-label="收藏"]').click();

    // Verify success message
    await expect(page.locator('text=已收藏')).toBeVisible();

    // Navigate to favorites to verify
    await page.click('text=收藏');
    await expect(page.locator('.favorite-item')).toHaveCountGreaterThan(0);
  });

  test('should remove paper from favorites', async ({ page }) => {
    // Navigate to favorites
    await page.click('text=收藏');

    // Wait for favorites list
    await expect(page.locator('.favorite-item')).toBeVisible();

    // Click on first favorite item
    await page.locator('.favorite-item').first()
      .locator('button[aria-label="取消收藏"]').click();

    // Verify removed
    await expect(page.locator('text=已取消收藏')).toBeVisible();
  });

  test('should add notes to favorite paper', async ({ page }) => {
    // Navigate to favorites
    await page.click('text=收藏');

    // Click on first favorite
    await page.locator('.favorite-item').first().click();

    // Add notes
    await page.fill('[name="notes"]', '这是一篇非常重要的论文，值得深入研究');

    // Save
    await page.click('button:has-text("保存")');

    // Verify notes saved
    await expect(page.locator('text=笔记已保存')).toBeVisible();
  });

  test('should move paper to folder', async ({ page }) => {
    // Search and favorite a paper first
    await page.fill('[placeholder="搜索论文..."]', 'AI');
    await page.click('button[aria-label="搜索"]');

    await expect(page.locator('.paper-card')).toHaveCountGreaterThan(0, {
      timeout: 10000
    });

    await page.locator('.paper-card').first()
      .locator('button[aria-label="收藏"]').click();

    // Navigate to favorites
    await page.click('text=收藏');

    // Select first item
    await page.locator('.favorite-item').first().click();

    // Move to folder
    await page.selectOption('[name="folder_id"]', '1');

    // Save
    await page.click('button:has-text("保存")');

    // Verify
    await expect(page.locator('text=已移动到文件夹')).toBeVisible();
  });

  test('should filter favorites by folder', async ({ page }) => {
    // Navigate to favorites
    await page.click('text=收藏');

    // Click on folder filter
    await page.click('[name="folder_filter"]');

    // Select a folder
    await page.selectOption('[name="folder_filter"]', '1');

    // Verify filtered results
    await expect(page.locator('.favorite-item')).toBeVisible();
  });

  test('should edit folder', async ({ page }) => {
    // Navigate to favorites
    await page.click('text=收藏');

    // Click on folder options
    await page.locator('.folder-item').first()
      .locator('button[aria-label="编辑"]').click();

    // Update folder name
    await page.fill('[name="name"]', '更新的文件夹名称');

    // Save
    await page.click('button:has-text("保存")');

    // Verify updated
    await expect(page.locator('text=更新的文件夹名称')).toBeVisible();
  });

  test('should delete folder', async ({ page }) => {
    // Navigate to favorites
    await page.click('text=收藏');

    // Click on folder options
    await page.locator('.folder-item').first()
      .locator('button[aria-label="删除"]').click();

    // Confirm deletion
    await page.click('button:has-text("确认")');

    // Verify folder deleted
    await expect(page.locator('text=文件夹已删除')).toBeVisible();
  });
});
