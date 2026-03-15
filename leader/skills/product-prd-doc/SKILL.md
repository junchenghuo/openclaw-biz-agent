---
name: product-prd-doc
description: Write and revise Product Requirement Documents (PRD) for internal projects. Use when acting as a Product Manager to produce clear requirements, scope, user stories, UX flow, edge cases, and acceptance criteria; and when asked to output a PRD as .docx (export via pandoc if available, otherwise provide a Markdown PRD ready for export).
---

# PRD workflow (concise)

## 1) Inputs to ask (minimum)
- Goal (what success looks like)
- Users + key scenarios
- In-scope / out-of-scope
- Required pages/flows
- API/permission constraints (if any)
- Delivery form (Markdown vs .docx) + target audience

## 2) PRD outline (copy/paste)
Use this structure unless the user provides another:

- Background & goals
- Personas / user stories
- Scope (in / out)
- UX flows (happy path + failure paths)
- Requirements (functional)
- Non-functional (perf, security, accessibility)
- Error handling & edge cases
- Analytics (optional)
- Acceptance criteria (AC) + test checklist
- Open questions / risks

## 3) Acceptance criteria rules
- Each AC must be testable and unambiguous.
- Include: success path, common failures, network/server failures, and "no sensitive logging".

## 4) .docx export (no paid services)
Prefer local export.

1) Write PRD in Markdown.
2) If `pandoc` is available, export:

```bash
pandoc PRD.md -o PRD.docx
```

If `pandoc` is not available, keep Markdown and provide a ready-to-export PRD (no special syntax).
