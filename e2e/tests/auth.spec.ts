import { test, expect } from '@playwright/test';

/**
 * E2E Test: Authentication Flow
 *
 * Tests user registration, login, and logout functionality
 */
test.describe('Authentication Flow', () => {
  const testUser = {
    email: `test-${Date.now()}@example.com`,
    password: 'TestPass123!',
    name: 'Test User'
  };

  test.beforeEach(async ({ page }) => {
    // Navigate to home page
    await page.goto('/');
  });

  test('should register a new user', async ({ page }) => {
    // Click on register button
    await page.click('text=注册');

    // Wait for registration form
    await expect(page.locator('form')).toBeVisible();

    // Fill registration form
    await page.fill('[name="email"]', testUser.email);
    await page.fill('[name="password"]', testUser.password);
    await page.fill('[name="name"]', testUser.name);

    // Submit form
    await page.click('button[type="submit"]');

    // Verify successful registration (redirect to dashboard or home)
    await expect(page).toHaveURL(/\/dashboard|\/$/);

    // Verify user is logged in
    await expect(page.locator(`text=${testUser.name}`)).toBeVisible();
  });

  test('should login existing user', async ({ page }) => {
    // Click on login button
    await page.click('text=登录');

    // Wait for login form
    await expect(page.locator('form')).toBeVisible();

    // Fill login form (using existing test user)
    await page.fill('[name="email"]', testUser.email);
    await page.fill('[name="password"]', testUser.password);

    // Submit form
    await page.click('button[type="submit"]');

    // Verify successful login
    await expect(page).toHaveURL(/\/dashboard|\/$/);
    await expect(page.locator(`text=${testUser.name}`)).toBeVisible();
  });

  test('should logout user', async ({ page }) => {
    // First login
    await page.click('text=登录');
    await expect(page.locator('form')).toBeVisible();
    await page.fill('[name="email"]', testUser.email);
    await page.fill('[name="password"]', testUser.password);
    await page.click('button[type="submit"]');

    // Wait for login
    await expect(page.locator(`text=${testUser.name}`)).toBeVisible();

    // Click logout
    await page.click('button:has-text("退出")');

    // Verify logout
    await expect(page.locator('text=登录')).toBeVisible();
    await expect(page.locator(`text=${testUser.name}`)).not.toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    // Click on login button
    await page.click('text=登录');

    // Fill with invalid credentials
    await page.fill('[name="email"]', 'invalid@example.com');
    await page.fill('[name="password"]', 'WrongPassword123!');

    // Submit form
    await page.click('button[type="submit"]');

    // Verify error message
    await expect(page.locator('text=邮箱或密码错误')).toBeVisible();
  });

  test('should validate email format', async ({ page }) => {
    // Click on register button
    await page.click('text=注册');

    // Fill with invalid email
    await page.fill('[name="email"]', 'invalid-email');
    await page.fill('[name="password"]', testUser.password);
    await page.fill('[name="name"]', testUser.name);

    // Submit form
    await page.click('button[type="submit"]');

    // Verify validation error
    await expect(page.locator('text=请输入有效的邮箱地址')).toBeVisible();
  });
});
