## 2024-05-30 - Keyboard Navigation for Scrollable Areas
**Learning:** Elements with `overflow: auto` (like `<pre>` blocks or scrollable tables) must have `tabindex="0"` if they contain content that might not fit the visible area. Otherwise, keyboard-only users cannot scroll them. Also, focus states should be explicitly styled so users know when the container has focus.
**Action:** Always check `overflow: auto` or scrollable containers for `tabindex="0"` and ensure they have a visible `:focus-visible` outline.
