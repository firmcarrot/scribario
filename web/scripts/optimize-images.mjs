#!/usr/bin/env node
/**
 * One-time image optimization script.
 * Resizes oversized icons/logo to @2x display size and converts to WebP.
 * Run: node scripts/optimize-images.mjs
 */

import sharp from 'sharp';
import { existsSync, unlinkSync, readdirSync } from 'fs';
import { join } from 'path';

const PUBLIC = join(process.cwd(), 'public');
const ICONS_DIR = join(PUBLIC, 'images/icons');

// Icons: displayed at 40x40, resize to 80x80 @2x → WebP
const icons = ['restaurants', 'agencies', 'local-shops', 'salons', 'gyms', 'real-estate'];

async function optimizeIcons() {
  for (const name of icons) {
    const src = join(ICONS_DIR, `${name}.png`);
    const dest = join(ICONS_DIR, `${name}.webp`);
    if (!existsSync(src)) {
      console.log(`⚠️  Missing: ${name}.png`);
      continue;
    }
    await sharp(src)
      .resize(80, 80, { fit: 'cover' })
      .webp({ quality: 85 })
      .toFile(dest);
    const srcSize = (await sharp(src).metadata()).size || 0;
    const destStat = (await sharp(dest).metadata()).size || 0;
    console.log(`✅ ${name}: PNG → WebP 80x80 (was ~${Math.round(srcSize/1024)}KB)`);
    // Remove original PNG
    unlinkSync(src);
  }
}

async function optimizeLogo() {
  const src = join(PUBLIC, 'images/scribario-logo-final.png');
  const dest = join(PUBLIC, 'images/scribario-logo-final.webp');
  if (!existsSync(src)) return;
  await sharp(src)
    .resize(144, 144, { fit: 'cover' })
    .webp({ quality: 90 })
    .toFile(dest);
  console.log('✅ Logo: PNG 2048x2048 → WebP 144x144');
  unlinkSync(src);
}

async function optimizeFbProof() {
  const src = join(PUBLIC, 'images/fb-post-proof.png');
  const dest = join(PUBLIC, 'images/fb-post-proof.webp');
  if (!existsSync(src)) return;
  await sharp(src)
    .webp({ quality: 85 })
    .toFile(dest);
  console.log('✅ FB proof: PNG → WebP');
  unlinkSync(src);
}

async function optimizeHandPhone() {
  const src = join(PUBLIC, 'images/hand-phone.png');
  const dest = join(PUBLIC, 'images/hand-phone.webp');
  if (!existsSync(src)) return;
  await sharp(src)
    .webp({ quality: 90, nearLossless: true })
    .toFile(dest);
  console.log('✅ Hand phone: PNG → WebP');
  unlinkSync(src);
}

async function deleteUnused() {
  const unused = [
    'images/hand-phone-greenscreen.png',
    'images/hand-phone-greenscreen-v2.jpg',
    'images/hand-phone-raw.jpg',
    'images/icons/icons-grid.png',
    'images/logo-orange-transparent.png',
    'images/scribario-logo.png',
  ];
  for (const file of unused) {
    const path = join(PUBLIC, file);
    if (existsSync(path)) {
      unlinkSync(path);
      console.log(`🗑️  Deleted unused: ${file}`);
    }
  }
}

async function deleteUnusedVideos() {
  const unused = ['videos/phone-demo.mp4', 'videos/fb-result.mp4'];
  for (const file of unused) {
    const path = join(PUBLIC, file);
    if (existsSync(path)) {
      unlinkSync(path);
      console.log(`🗑️  Deleted unused video: ${file}`);
    }
  }
}

async function main() {
  console.log('🖼️  Optimizing images...\n');
  await optimizeIcons();
  console.log('');
  await optimizeLogo();
  await optimizeFbProof();
  await optimizeHandPhone();
  console.log('');
  await deleteUnused();
  console.log('');
  await deleteUnusedVideos();
  console.log('\n✨ Done! Update component imports to use .webp extensions.');
}

main().catch(err => {
  console.error('❌ Error:', err);
  process.exit(1);
});
