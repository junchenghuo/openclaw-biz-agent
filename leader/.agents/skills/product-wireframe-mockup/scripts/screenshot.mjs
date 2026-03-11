#!/usr/bin/env node
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

function arg(name, defVal=null) {
  const idx = process.argv.indexOf(`--${name}`);
  if (idx === -1) return defVal;
  return process.argv[idx+1] ?? defVal;
}

const htmlPath = arg('html');
const outPath = arg('out', 'wireframe.png');
const width = Number(arg('width', '1280'));
const height = Number(arg('height', '720'));

if (!htmlPath) {
  console.error('Missing --html <file.html>');
  process.exit(2);
}

const absHtml = path.resolve(htmlPath);
if (!fs.existsSync(absHtml)) {
  console.error(`HTML not found: ${absHtml}`);
  process.exit(2);
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width, height } });
await page.goto(`file://${absHtml}`, { waitUntil: 'networkidle' });
await page.screenshot({ path: outPath, fullPage: true });
await browser.close();

console.log(`Wrote ${outPath}`);
