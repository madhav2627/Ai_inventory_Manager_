# AI Command Center — UI Upgrade (Second Pass)

This pass focuses on the AI Command Center shown in the screenshots.

## Visual changes
- Rebuilt the AI page header using the existing `page-head` design system so its spacing, divider, typography and responsiveness match Inventory/Billing.
- Added an offline-intelligence eyebrow, LOCAL MODEL badge, decision-layer rail and subtle orbit animation.
- Reworked the AI status bar into a structured operator status strip with live metrics and a restrained sheen effect.
- Rebuilt the AI command input as a contextual command surface with focus glow, press feedback and a suggestion pill.
- Added subtle panel hover elevation, top-edge highlight, table/list row hover feedback and button sheen.
- Added ambient page lighting and staggered motion while keeping animations short and purpose-driven.
- Kept touch/coarse pointer behavior safe and reduced-motion support intact.

## Functional safety
- Existing AI element IDs used by `ai_center.js` are preserved.
- No new API/server dependency was introduced.
