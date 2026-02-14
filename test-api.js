#!/usr/bin/env node

/**
 * API Test for ScholarAI Backend
 * Tests the backend API endpoints directly
 */

import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const REPORT_DIR = join(__dirname, 'Progress-Logs');
const SCREENSHOT_DIR = join(__dirname, 'test-results', 'screenshots');

if (!existsSync(SCREENSHOT_DIR)) {
  mkdirSync(SCREENSHOT_DIR, { recursive: true });
}
if (!existsSync(REPORT_DIR)) {
  mkdirSync(REPORT_DIR, { recursive: true });
}

async function testAPIEndpoint(url, method = 'GET', body = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    'Accept': 'application/json'
    }
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);

  const result = {
    status: response.status,
    ok: response.ok,
    data: await response.json().catch(() => null),
    headers: Object.fromEntries(response.headers.entries())
  };

  return result;
}

async function main() {
  console.log('=================================================');
  console.log('  ScholarAI API Test');
  console.log('=================================================\n');

  const results = [];
  const BASE_URL = 'http://localhost:5000';

  console.log('Testing Backend API...\n');
  console.log('Base URL: ' + BASE_URL + '\n');

  // Test 1: Health check
  console.log('[1] Testing health endpoint...');
  try {
    const healthResult = await testAPIEndpoint(BASE_URL + '/health');
    results.push({
      test: 'Health Check',
      endpoint: 'GET /health',
      status: healthResult.status,
      success: healthResult.ok
    });
    console.log('  Status: ' + healthResult.status + ' - ' + (healthResult.ok ? 'OK' : 'FAILED'));
  } catch (error) {
    console.log('  ERROR: ' + error.message);
    results.push({
      test: 'Health Check',
      endpoint: 'GET /health',
      error: error.message,
      success: false
    });
  }

  // Test 2: Papers search endpoint
  console.log('\n[2] Testing papers search endpoint...');
  try {
    const searchParams = new URLSearchParams({
      query: 'machine learning',
      page_size: '5'
    });

    const searchResult = await testAPIEndpoint(BASE_URL + '/api/papers/search?' + searchParams);
    results.push({
      test: 'Papers Search',
      endpoint: 'GET /api/papers/search',
      status: searchResult.status,
      success: searchResult.ok
    });
    console.log('  Status: ' + searchResult.status + ' - ' + (searchResult.ok ? 'OK' : 'FAILED'));

    if (searchResult.data) {
      console.log('  Papers found: ' + (searchResult.data.data?.papers?.length || 0));
      console.log('  Total results: ' + (searchResult.data.data?.total || 0));
    }
  } catch (error) {
    console.log('  ERROR: ' + error.message);
    results.push({
      test: 'Papers Search',
      endpoint: 'GET /api/papers/search',
      error: error.message,
      success: false
    });
  }

  // Test 3: Fields endpoint
  console.log('\n[3] Testing fields endpoint...');
  try {
    const fieldsResult = await testAPIEndpoint(BASE_URL + '/api/papers/fields');
    results.push({
      test: 'Fields List',
      endpoint: 'GET /api/papers/fields',
      status: fieldsResult.status,
      success: fieldsResult.ok
    });
    console.log('  Status: ' + fieldsResult.status + ' - ' + (fieldsResult.ok ? 'OK' : 'FAILED'));
  } catch (error) {
    console.log('  ERROR: ' + error.message);
    results.push({
      test: 'Fields List',
      endpoint: 'GET /api/papers/fields',
      error: error.message,
      success: false
    });
  }

  // Generate report
  console.log('\n=================================================');
  console.log('Generating Test Report...');
  console.log('=================================================\n');

  const reportPath = join(REPORT_DIR, 'api-test-report.md');
  let markdown = '# API Test Report\n\n';
  markdown += '**Test Date**: ' + new Date().toLocaleString('zh-CN') + '\n\n';
  markdown += '**Environment**:\n';
  markdown += '- Backend: http://localhost:5000\n\n';

  markdown += '## Test Results\n\n';

  for (const result of results) {
    const statusIcon = result.success ? 'OK' : 'FAIL';
    markdown += '### [' + statusIcon + '] ' + result.test + '\n\n';
    markdown += '**Endpoint**: ' + result.endpoint + '\n\n';
    markdown += '**Status**: ' + (result.status || 'ERROR') + '\n\n';

    if (result.error) {
      markdown += '**Error**: ' + result.error + '\n\n';
    }

    if (result.data) {
      markdown += '**Data**: ' + JSON.stringify(result.data, null, 2) + '\n\n';
    }
  }

  markdown += '## Summary\n\n';
  const passed = results.filter(r => r.success).length;
  const total = results.length;
  markdown += '- Total Tests: ' + total + '\n';
  markdown += '- Passed: ' + passed + '\n';
  markdown += '- Failed: ' + (total - passed) + '\n';
  markdown += '- Pass Rate: ' + ((passed / total) * 100).toFixed(1) + '%\n\n';

  writeFileSync(reportPath, markdown, 'utf8');
  console.log('Report saved to: ' + reportPath);
  console.log('\n=================================================');
  console.log('  API Test Summary');
  console.log('=================================================');
  console.log('Total Tests: ' + total);
  console.log('Passed: ' + passed);
  console.log('Failed: ' + (total - passed));
  console.log('Pass Rate: ' + ((passed / total) * 100).toFixed(1) + '%');
}

main().catch(console.error);
