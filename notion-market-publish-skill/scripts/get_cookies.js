#!/usr/bin/env node
/**
 * Get Notion cookies by opening browser and navigating to templates page
 * Uses Chrome CDP to automate browser and extract cookies
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

async function getCookies() {
  try {
    // Use puppeteer to launch Chrome and get cookies
    const puppeteer = require('puppeteer');

    console.error('Launching Chrome...');
    const browser = await puppeteer.launch({
      headless: false, // Show browser so user can login if needed
      defaultViewport: null
    });

    const page = await browser.newPage();

    console.error('Navigating to Notion templates page...');
    await page.goto('https://www.notion.so/profile/templates', {
      waitUntil: 'networkidle2',
      timeout: 60000
    });

    // Wait a bit for user to login if needed
    console.error('Waiting for page to load... (login if needed)');
    await page.waitForTimeout(5000);

    // Get all cookies
    const cookies = await page.cookies();

    // Extract specific cookies we need
    const cookieMap = {};
    cookies.forEach(cookie => {
      cookieMap[cookie.name] = cookie.value;
    });

    // Get user_id
    const userId = cookieMap['notion_user_id'] || '';

    // Format cookies as header string
    const cookieString = cookies.map(c => `${c.name}=${c.value}`).join('; ');

    // Save to file
    const configDir = path.join(os.homedir(), '.config', 'notion');
    if (!fs.existsSync(configDir)) {
      fs.mkdirSync(configDir, { recursive: true });
    }

    const cookieFile = path.join(configDir, 'cookies.txt');
    fs.writeFileSync(cookieFile, cookieString);

    const userIdFile = path.join(configDir, 'user_id.txt');
    fs.writeFileSync(userIdFile, userId);

    console.error(`\nCookies saved to: ${cookieFile}`);
    console.error(`User ID saved to: ${userIdFile}`);
    console.error(`User ID: ${userId}`);

    // Output JSON for programmatic use
    console.log(JSON.stringify({
      cookies: cookieString,
      userId: userId,
      cookieFile: cookieFile,
      userIdFile: userIdFile
    }));

    await browser.close();

  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

// Check if puppeteer is installed
try {
  require.resolve('puppeteer');
  getCookies();
} catch (e) {
  console.error('Puppeteer not installed. Installing...');
  console.error('Run: npm install -g puppeteer');
  console.error('Or: npx puppeteer browsers install chrome');
  process.exit(1);
}
