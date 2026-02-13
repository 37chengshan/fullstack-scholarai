import { test, expect } from '@playwright/test';

/**
 * E2E Test: Project Management
 *
 * Tests project creation, paper management, and organization
 */
test.describe('Project Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/');
    await page.click('text=登录');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=欢迎')).toBeVisible();
  });

  test('should create new project', async ({ page }) => {
    // Navigate to projects page
    await page.click('text=项目');

    // Click "新建项目" button
    await page.click('button:has-text("新建项目")');

    // Fill project details
    await page.fill('[name="name"]', '机器学习研究');
    await page.fill('[name="description"]', '关于机器学习的论文集合');

    // Select color
    await page.click('[name="color"]');
    await page.click('text=蓝色');

    // Submit
    await page.click('button:has-text("创建")');

    // Verify project created
    await expect(page.locator('text=机器学习研究')).toBeVisible();
  });

  test('should add paper to project', async ({ page }) => {
    // First search for a paper
    await page.fill('[placeholder="搜索论文..."]', 'AI');
    await page.click('button[aria-label="搜索"]');

    // Wait for results
    await expect(page.locator('.paper-card')).toHaveCountGreaterThan(0, {
      timeout: 10000
    });

    // Click "添加到项目" on first paper
    await page.locator('.paper-card').first()
      .locator('button:has-text("添加到项目")').click();

    // Select project (or create new one)
    const projectOption = page.locator('text=选择项目');
    if (await projectOption.isVisible()) {
      await page.selectOption('select', '0'); // First project

      // Confirm
      await page.click('button:has-text("确认")');

      // Verify success message
      await expect(page.locator('text=已添加到项目')).toBeVisible();
    }
  });

  test('should update paper reading status', async ({ page }) => {
    // Navigate to projects
    await page.click('text=项目');

    // Click on a project
    await page.locator('.project-card').first().click();

    // Wait for papers list
    await expect(page.locator('.paper-item')).toBeVisible();

    // Click status dropdown on first paper
    await page.locator('.paper-item').first()
      .locator('select[name="status"]').click();

    // Select "in_progress"
    await page.selectOption('select[name="status"]', 'in_progress');

    // Verify status updated
    await expect(page.locator('text=进行中')).toBeVisible();
  });

  test('should delete project', async ({ page }) => {
    // Navigate to projects
    await page.click('text=项目');

    // Get initial project count
    const initialCount = await page.locator('.project-card').count();

    // Click on project options
    await page.locator('.project-card').first()
      .locator('button[aria-label="更多选项"]').click();

    // Click delete
    await page.click('text=删除项目');

    // Confirm deletion
    await page.click('button:has-text("确认")');

    // Verify project deleted
    const newCount = await page.locator('.project-card').count();
    expect(newCount).toBeLessThan(initialCount);
  });

  test('should display project progress', async ({ page }) => {
    // Navigate to projects
    await page.click('text=项目');

    // Click on a project with papers
    await page.locator('.project-card').first().click();

    // Verify progress bar
    await expect(page.locator('.progress-bar')).toBeVisible();

    // Verify statistics
    await expect(page.locator('text=论文数')).toBeVisible();
    await expect(page.locator('text=已完成')).toBeVisible();
  });

  test('should edit project details', async ({ page }) => {
    // Navigate to projects
    await page.click('text=项目');

    // Click on project options
    await page.locator('.project-card').first()
      .locator('button[aria-label="更多选项"]').click();

    // Click edit
    await page.click('text=编辑');

    // Modify project name
    await page.fill('[name="name"]', '更新的项目名称');

    // Save
    await page.click('button:has-text("保存")');

    // Verify changes
    await expect(page.locator('text=更新的项目名称')).toBeVisible();
  });
});
