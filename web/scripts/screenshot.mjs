#!/usr/bin/env node
/**
 * Screenshot tool for visual development feedback loop.
 *
 * Usage:
 *   node scripts/screenshot.mjs                    # Full page screenshot
 *   node scripts/screenshot.mjs --viewport         # Viewport only (above the fold)
 *   node scripts/screenshot.mjs --section hero     # Screenshot a specific section by ID
 *   node scripts/screenshot.mjs --url /getting-started  # Screenshot a different page
 *   node scripts/screenshot.mjs --compare ref.png  # Take screenshot and note comparison needed
 *
 * Screenshots saved to: tmp_screenshots/ (gitignored)
 */

import puppeteer from 'puppeteer';
import { mkdirSync, existsSync } from 'fs';
import { join } from 'path';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3851';
const SCREENSHOT_DIR = join(process.cwd(), 'tmp_screenshots');
const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'mobile', width: 375, height: 812 },
];

// Parse args
const args = process.argv.slice(2);
const flags = {};
for (let i = 0; i < args.length; i++) {
  if (args[i].startsWith('--')) {
    const key = args[i].slice(2);
    flags[key] = args[i + 1] && !args[i + 1].startsWith('--') ? args[++i] : true;
  }
}

const urlPath = flags.url || '/';
const viewportOnly = flags.viewport || false;
const sectionId = flags.section || null;

async function takeScreenshots() {
  if (!existsSync(SCREENSHOT_DIR)) {
    mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);

  for (const vp of VIEWPORTS) {
    const page = await browser.newPage();
    await page.setViewport({ width: vp.width, height: vp.height });

    const fullUrl = `${BASE_URL}${urlPath}`;
    console.log(`📸 ${vp.name} (${vp.width}x${vp.height}) → ${fullUrl}`);

    try {
      await page.goto(fullUrl, { waitUntil: 'networkidle0', timeout: 15000 });
    } catch {
      console.log(`   ⚠️  Timeout waiting for networkidle, continuing anyway...`);
    }

    // Wait a beat for animations to settle
    await new Promise(r => setTimeout(r, 1500));

    let filename;

    if (sectionId) {
      // Screenshot a specific section
      const element = await page.$(`#${sectionId}, [data-section="${sectionId}"]`);
      if (element) {
        filename = `${timestamp}_${vp.name}_section-${sectionId}.png`;
        await element.screenshot({ path: join(SCREENSHOT_DIR, filename) });
      } else {
        console.log(`   ⚠️  Section "${sectionId}" not found`);
        continue;
      }
    } else if (viewportOnly) {
      // Viewport screenshot (above the fold)
      filename = `${timestamp}_${vp.name}_viewport.png`;
      await page.screenshot({ path: join(SCREENSHOT_DIR, filename) });
    } else {
      // Full page screenshot
      filename = `${timestamp}_${vp.name}_fullpage.png`;
      await page.screenshot({
        path: join(SCREENSHOT_DIR, filename),
        fullPage: true,
      });
    }

    console.log(`   ✅ Saved: tmp_screenshots/${filename}`);
    await page.close();
  }

  await browser.close();
  console.log(`\n📁 All screenshots in: tmp_screenshots/`);
}

takeScreenshots().catch((err) => {
  console.error('Screenshot failed:', err.message);
  process.exit(1);
});
