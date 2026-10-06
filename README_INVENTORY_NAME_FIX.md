# Inventory column readability fix

Updated `templates/inventory.html` + `static/css/style.css` to correct the Item/Category body alignment and make product names clearly readable.

## Changes
- Removed the table-row pseudo-element that could introduce an anonymous table column in Chromium and shift body cells.
- Gave the Item column a fixed 380px track so product names use the available left-side space.
- Kept Category, Brand, Code, Price, Stock, Status, Expiry and Actions on their own fixed tracks.
- Prevented product names from breaking in the middle of normal words.
- Kept the hover accent inside the first real table cell.
- Preserved horizontal scrolling on narrower screens.
