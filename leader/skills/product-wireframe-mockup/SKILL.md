---
name: product-wireframe-mockup
description: Generate simple product wireframes/prototypes for web pages (login, forms, dashboards) as images (PNG) without paid tools or API keys. Use when asked for "原型图/线框图/流程图"; produces a minimal HTML wireframe and optionally screenshots it via Playwright.
---

# Wireframe → PNG (local, no paid tools)

## Quick workflow
1) Confirm target page(s), key components, states (normal/error/loading), and target viewport.
2) Generate `wireframe.html` (simple boxes + labels). Use assets template if helpful.
3) If Playwright is available, screenshot to PNG.

## Commands (optional)
- Install Playwright once (if not present):

```bash
npm i -D playwright
npx playwright install chromium
```

- Screenshot:

```bash
node scripts/screenshot.mjs --html wireframe.html --out wireframe.png --width 1280 --height 720
```

## Flow chart
If a flow chart is needed, write a Mermaid flow in Markdown (no external services). Keep nodes short.
