# AI Inventory Manager — UI Craft Upgrade

This pass applies the supplied design/animation skills to the existing Flask application without replacing its business logic.

## Visual direction
- Calm premium operator-console layout
- Strong editorial hierarchy using the existing Inter / Fraunces / IBM Plex Mono type system
- Brass used as a restrained semantic accent rather than as decoration everywhere
- Reduced reliance on large shadows and hover lifts
- Clearer separation between inventory intelligence, alerts, and billing

## Interaction + motion
- High-frequency interactions use short `transform`/`opacity` transitions instead of broad `transition: all`
- Hover behavior is gated for mouse-capable pointers
- Touch targets get immediate press feedback
- Existing number counters respect `prefers-reduced-motion`
- Mobile drawer can be dismissed with Escape and exposes `aria-expanded`
- Reduced-motion media styles remove non-essential animation

## Mobile
- Re-enabled normal browser zoom by removing `maximum-scale` / `user-scalable=no`
- Added `viewport-fit=cover`
- Added safe-area-aware mobile header/sidebar/footer spacing
- Uses `100dvh` for app-height behavior
- Prevents root pull-to-refresh chaining
- Prevents sticky hover states on touch-capable devices
- Input controls use a mobile-safe 16px minimum font size

## Dashboard
- Reworked the dashboard hero into a business snapshot
- Added direct links for inventory review and AI signals
- Added compact operational signal row
- Kept existing backend data, forecast status, transactions, and sales chart intact

## Validation
- All Jinja templates parsed successfully.
- `static/js/app.js` passed Node syntax validation.
- Python source files passed `py_compile`.
- CSS passed a TinyCSS2 parse with no syntax errors.
- A rendered dashboard preview was checked at 1440px and 390px viewports; mobile had no horizontal overflow.

The full Flask runtime could not be launched in the sandbox because its dependencies are not installed and the sandbox has no package-download access. The project remains runnable through its existing `requirements.txt` / Windows startup scripts.
