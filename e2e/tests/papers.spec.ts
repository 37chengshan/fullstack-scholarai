import { test, expect } from '@playwright/test';

/**
 * E2E Test: Paper Search and Details
 *
 * Tests paper search functionality and viewing paper details
 */
test.describe('Paper Search and Details', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home page
    await page.goto('/');
  });

  test('should search for papers by keyword', async ({ page }) => {
    // Enter search query
    await page.fill('[placeholder="搜索论文..."]', 'machine learning');

    // Click search button
    await page.click('button[aria-label="搜索"]');

    // Wait for results
    await expect(page.locator('.paper-card')).toHaveCountGreaterThan(0, {
      timeout: 10000
    });

    // Verify search results are displayed
    await expect(page.locator('.paper-card').first()).toBeVisible();
  });

  test('should display paper details', async ({ page }) => {
    // Search for papers first
    await page.fill('[placeholder="搜索论文..."]', 'neural networks');
    await page.click('button[aria-label="搜索"]');

    // Wait for results
    await expect(page.locator('.paper-card')).toHaveCountGreaterThan(0, {
      timeout: 10000
    });

    // Click on first paper
    await page.locator('.paper-card').first().click();

    // Verify paper detail page
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('text=作者')).toBeVisible();
    await expect(page.locator('text=摘要')).toBeVisible();
  });

  test('should filter papers by year', async ({ page }) => {
    // Enter search query
    await page.fill('[placeholder="搜索论文..."]', 'deep learning');

    // Set year filter
    await page.selectOption('[name="year_min"]', '2020');
    await page.selectOption('[name="year_max"]', '2023');

    // Click search button
    await page.click('button[aria-label="搜索"]');

    // Wait for results
    await expect(page.locator('.paper-card')).toHaveCountGreaterThan(0, {
      timeout: 10000
    });
  });

  test('should add paper to favorites', async ({ page }) => {
    // Login first (you need to be logged in to add favorites)
    await page.click('text=登录');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Wait for login
    await expect(page.locator('text=欢迎')).toBeVisible();

    // Search for papers
    await page.fill('[placeholder="搜索论文..."]', 'AI');
    await page.click('button[aria-label="搜索"]');

    // Wait for results
    await expect(page.locator('.paper-card')).toHaveCountGreaterThan(0, {
      timeout: 10000
    });

    // Click favorite button on first paper
    await page.locator('.paper-card').first()
      .locator('button[aria-label="收藏"]').click();

    // Verify favorite notification
    await expect(page.locator('text=已添加到收藏夹')).toBeVisible();
  });

  test('should load more papers on scroll', async ({ page }) => {
    // Enter search query with many results
    await page.fill('[placeholder="搜索论文..."]', 'machine learning');

    // Click search button
    await page.click('button[aria-label="搜索"]');

    // Wait for initial results
    await expect(page.locator('.paper-card')).toHaveCountGreaterThan(0, {
      timeout: 10000
    });

    const initialCount = await page.locator('.paper-card').count();

    // Scroll to bottom
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

    // Wait for more papers to load
    await page.waitForTimeout(2000);

    const newCount = await page.locator('.paper-card').count();

    // Verify more papers loaded
    expect(newCount).toBeGreaterThan(initialCount);
  });

  test('should display paper PDF link', async ({ page }) => {
    // Search for papers
    await page.fill('[placeholder="搜索论文..."]', 'test');
    await page.click('button[aria-label="搜索"]');

    // Wait for results
    await expect(page.locator('.paper-card')).toHaveCountGreaterThan(0, {
      timeout: 10000
    });

    // Click on first paper
    await page.locator('.paper-card').first().click();

    // Verify PDF link is present
    const pdfLink = page.locator('a:has-text("PDF")');
    await expect(pdfLink).toBeVisible();
    await expect(pdfLink).toHaveAttribute('href', /arxiv\.org\/pdf/);
  });
});
