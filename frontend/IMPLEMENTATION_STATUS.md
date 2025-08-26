# Frontend Implementation Status — Royal Ink Glass UI

Last updated: 2025-08-24

## Executive Summary

Core chat UX is production-ready under the Royal Ink Glass design system (single scroll region, translucent header with content behind, bottom-anchored input, subtle jump-to-latest). Milestone A is complete. Milestone B is largely complete (streaming visuals deferred). Milestone C is complete: safe Markdown rendering with Prism, finalized code block visuals, autosizing input, and per‑message copy actions (TXT/MD) in a clean footer row. Next major focus: Milestone D — Blog Generation, Preview & Editor UX with a responsive 3‑pane framework, pure‑black glass blog pane, segmented pane toggles, and an input‑row “Generate blog” action that includes the current text.

## What changed today (highlights)

- Markdown rendering is production-grade and consistent across bubbles:
	- `react-markdown` + `remark-gfm` + `rehype-sanitize` (extended default schema) with safe links.
	- Prism highlighting with long-line wrapping; no horizontal scroll; hydration issues resolved.
	- Code blocks retain a minimal dark-glass look and a built‑in copy button with transient feedback.
- Finalized neutral code block visual style shared across user/assistant; soft wrapping preserved.
- Input replaced with `react-textarea-autosize` (minRows=1, maxRows=6) with IME-safe Enter/Shift+Enter behavior.
- Per‑message copy actions implemented and decluttered: bottom‑footer row inside the bubble with a copy icon and TXT/MD labels; hover‑to‑reveal, keyboard accessible.
- Fixed prior compile issues and cleaned up message overlay logic.

## Current Status

### Milestone A — Structure & Layout
Status: COMPLETE

- Single scroll container with messages; translucent header overlays content.
- Bottom-anchored messages with stable autoscroll behavior.
- Input fixed at bottom with safe-area; scrollable content is the chat panel only.
- Empty state: 2x2 suggestion grid + “Write Blog”; hides after first message.
- Jump-to-latest: subtle glass arrow appears when > 200px from bottom; smooth scroll.
- Accessibility: role="log", aria-live="polite", semantic message roles, predictable tab order.

Acceptance: 1 scrollbar, input pinned, no layout thrash, a11y attributes present, jump control works, empty state correct — ✅ Met.

### Milestone B — Streaming & Input
Status: COMPLETE (streaming polish deferred)

- Input behaviors:
	- Enter=send, Shift+Enter=newline — complete.
	- Auto-resize via `react-textarea-autosize` (minRows=1, maxRows=6), IME-safe — complete.
	- Optimistic user bubble on send — complete.
- Streaming UI: Baseline acceptable; advanced visuals deferred.
- Error handling: Lightweight glass toasts still planned.

### Milestone C — Markdown Rendering & Copy
Status: COMPLETE

Delivered:
- Safe Markdown pipeline (`react-markdown` + `remark-gfm` + `rehype-sanitize` with extended default schema).
- Prism syntax highlighting with soft line wrapping (no horizontal scroll); preserves indentation and hydration safety.
- Safe links (noopener, noreferrer, nofollow where appropriate).
- Code blocks with integrated Copy and transient feedback.
- Neutral, shared code block visual style that works in both blue/black bubbles.
- Per‑message footer actions: Copy TXT and Copy MD, hover‑only, within the bubble, with clear iconography.

Acceptance: ✅ Met
- GFM coverage; no horizontal scrolling; block-level and message-level copy; timestamps/hover behaviors intact.

Open follow-ups:
- Add lightweight glass toasts for errors and “Copied” confirmations (optional micro‑toast).

---

### Milestone D — Blog Generation, Preview & Editor UX
Status: NEXT MAJOR FOCUS

Decisions locked (from product MCQs):
- Source: Use full conversation context + current input text; clarify in UI.
- 3‑pane framework: Left (Original, if forked) • Center (Chat) • Right (Blog Preview/Editor); responsive collapse to tabs on small screens.
- Preview rendering: Use the same `MarkdownRenderer` with sanitize + Prism.
- Styling: Pure‑black pane with subtle glass and hairline borders; clear separations between panes.
- Pane toggles: Segmented control in the header area (Original | Chat | Blog); defaults to Chat; Original only if forked.
- Edit affordance: “Edit and Post” only for assistant messages with `isBlog=true`; opens the editor prefilled with that message.
- Custom blog: “New Blog Draft” opens an empty editor (no LLM call).
- Drafts: Autosave in localStorage keyed by `conversationId` + `messageId` (or `new-draft`) with last‑saved indicator.
- Multiple generated blogs: Each is a message (`isBlog=true`); right pane shows latest; “Edit and Post” from any blog message opens that version.
- Input/controls: Send and Generate Blog on the same line; Generate is a stronger secondary with subtle glow; helper text clarifies it sends current input.
- Visibility: If no blog exists, the right pane is hidden/inaccessible.
- Accessibility: Visible focus, ARIA on toggles/actions; keyboard‑first flows; optional Ctrl/Cmd+G shortcut.

Work items:
1) Input row actions
	- Place “Generate blog” button to the right of Send, same row; text‑only label; subtle glow/bold treatment to feel special.
	- Tooltip/helper: “Includes current input as context.”

2) Segmented pane control
	- Replace floating chips with a compact segmented control in the header: [Original] [Chat] [Blog].
	- Respect forked state to enable Original. Persist last selection per conversation.

3) 3‑pane layout with responsive behavior
	- Desktop: three columns with equal widths.
	- Medium: two panes (Chat + toggled right pane).
	- Small/mobile: single‑pane with tabs; Chat default; Original/Blog via tabs; right pane hidden when no blog exists.

4) Blog preview pane (pure black + glass)
	- Render blog content via `MarkdownRenderer` (same code styles, sanitize + Prism).
	- Style: pure black background, subtle white‑glass overlay, hairline borders; clear vertical separators from chat.
	- Header includes “Edit and Post” (enabled for blog content), timestamp, and word count.

5) “Edit and Post” flow
	- From any assistant blog message (`isBlog=true`), open the right‑pane Editor with the message content preloaded.
	- Editor supports autosave (localStorage), last‑saved indicator, and cancel.

6) Zero‑message empty state
	- Centered, beautiful CTA: “Start a new blog draft” (opens empty editor) and “Generate blog” (kicks off generation) — clean, no emojis.

7) Error and empty states
	- Glass toasts for failures (generation, publish); concise messages.
	- If no generated blog, right pane cannot be toggled; show an inline hint near the generate button instead.

Acceptance criteria:
- Generate Blog is clearly distinct, in the input row, and communicates inclusion of current input.
- Right pane renders Markdown with identical renderer and code block styles; pure‑black glass aesthetic; clear pane separation.
- Segmented control replaces floating chips; Original only shows if forked; Blog only when a blog exists or when editing.
- Clicking “Edit and Post” on a blog message preloads the editor with that message’s content; autosave works and persists per key.
- Responsive behavior matches desktop/medium/mobile specs; no layout shifts or content overflow.
- Zero‑message state surfaces cohesive CTAs for New Draft and Generate Blog, centered and clean.

### Milestone E — Export & Share
Status: NOT STARTED (planned)

- Conversation-level: Copy all as Markdown; Download .md.
- Print-to-PDF route with native print dialog; theme-aligned print styles.
- Optional per-message print view if low risk.

Acceptance:
- Clean PDF export with theme and code styles; .md export correct.

### Milestone F — Performance (long histories)
Status: NOT STARTED (planned)

- Virtualize messages with `react-virtuoso` after baseline stabilizes.
- Memoize items; lazy images.
- Progressive pagination (deferred until backend cursors exist).

Acceptance:
- Smooth with large histories; consistent autoscroll and jump behavior.

### Milestone D — Export & Share
Status: NOT STARTED (planned)

- Conversation-level: Copy all as Markdown; Download .md.
- Print-to-PDF route with native print dialog; theme-aligned print styles.
- Optional per-message print view if low risk.

Acceptance:
- Clean PDF export with theme and code styles; .md export correct.

### Milestone E — Performance (long histories)
Status: NOT STARTED (planned)

- Virtualize messages with `react-virtuoso` after baseline stabilizes.
- Memoize items; lazy images.
- Progressive pagination (deferred until backend cursors exist).

Acceptance:
- Smooth with large histories; consistent autoscroll and jump behavior.

## Design System — Royal Ink Glass

### Palette (reference)
- Pure Black: #000000 (background)
- Royal Ink Blue (primary): #1E3A8A–#2563EB range
- Brilliant Blue: #3B82F6 (interactive)
- Light Blue: #60A5FA (accents)
- Ice White: #E6F3FF (text/gradients)
- Vibrant Red: #DC2626 (destructive)
- Soft Gray: #6B7280 (neutral)

### Glass effects (reference)
```css
background: rgba(255, 255, 255, 0.03);
backdrop-filter: blur(20–32px) saturate(160–180%);
border: 1–2px solid rgba(255, 255, 255, 0.08–0.2) or blue-tinted for primaries;
border-radius: 12px (controls) / 24px (cards) / 9999px (chips);
box-shadow: layered outer + subtle inset highlight for real-glass feel;
```

### Jump-to-Latest control (finalized)
- Minimal glass button (28px circle) near the input; heavy blur.
- Visible only when > 200px from bottom and user messages exist.
- Smooth scroll to the last message.

## Acceptable Use Patterns (locked)

- No transform/translate animations for macro layout; rely on opacity/blur only.
- One scrolling region for content; header remains translucent.
- Timestamps hidden by default, visible on hover.
- Group consecutive messages by author with subtle radius changes.
- Max chat width ~800px centered.
- Suggestion grid appears only when there are 0 messages; disappears on first send.

## Implementation details (recent corrections)

- Hook order error fixed by moving scroll detection `useEffect` to the top-level hooks and deriving `hasUserMessages` inside the handler.
- De-duplicated textarea in the input row; kept a single controlled input.
- Replaced bulky “Jump to Latest” chip with subtle glass arrow; anchored to the input container to avoid drift.
- Restored proper glass morphism for controls and message surfaces.
- A11y doc added: `docs/frontend/accessibility-guide.md`.
 - Introduced Markdown renderer with sanitize + Prism; resolved initial hydration mismatch by rendering fenced code via a pre-based renderer.
 - Extended sanitize schema and styles for tables/images; enabled long-line wrapping.
 - Replaced textarea with autosizing input; added IME-safe key handling; capped growth to 6 rows.
 - Moved per‑message copy to a footer row with TXT/MD options and copy iconography; removed cluttering overlay.

## Next Steps (actionable plan)

1) Blog UX foundation (Milestone D)
- Implement segmented pane control (Original | Chat | Blog) and responsive 3‑pane behavior; hide Blog when none exists.
- Add “Generate blog” to input row (right of Send) with subtle glow; helper text clarifies current input is included.
- Render Blog preview via `MarkdownRenderer`; apply pure‑black glass styling and pane separators.

2) Editor flows (Milestone D)
- “Edit and Post” on assistant blog messages opens Editor prefilled with that content.
- Autosave drafts (localStorage) keyed per conversation/message; last‑saved indicator.
- Zero‑message empty state: centered “New Blog Draft” (empty editor) and “Generate blog”.

3) Error handling (Milestone B follow‑up)
- Lightweight glass toasts for failures and copy confirmations.

4) Export & Share (Milestone E)
- Copy all as Markdown; download .md; print styles.

5) Performance (Milestone F)
- Virtualization after UX stabilizes; preserve autoscroll semantics.

## Agent Working Guidelines (keep in mind)

- Preserve Royal Ink Glass: heavy blur, subtle white glass backgrounds, soft borders, no flat grays for glass.
- Maintain professional tone: no emojis in UI copy; minimal, clear labels.
- Accessibility first: role/aria semantics, tab order, visible focus, readable contrast.
- Zero scroll fights: don’t force-scroll if the user has scrolled up; show the glass arrow.
- Avoid macro animations; prefer opacity/blur micro-interactions under 300ms.
- Keep input UX stable: auto-resize, Enter=send, Shift+Enter=newline.
- Favor composable, testable components; don’t introduce heavy deps without discussion.
- When adding public behavior, add/update minimal tests or stories.

### Agent behavior — Senior Software Engineer (production mindset)
- Code quality: idiomatic, typed-first TypeScript; strict TS config; meaningful names; clear interfaces and contracts.
- Component design: small, composable components; predictable props; no hidden side effects; SSR/CSR hydration-safe.
- Testing: fast happy-path + 1–2 edge tests per new behavior; include a11y checks where relevant.
- Accessibility: keyboard-first flows, focus management, ARIA where needed, color contrast, reduced motion support.
- Performance: avoid unnecessary renders; memoize thoughtfully; virtualize long lists; measure before optimizing.
- Reliability: defensive error handling; graceful fallbacks; avoid throwing uncaught errors in UI; retries where safe.
- Security & privacy: sanitize user content, safe links, avoid XSS; no accidental PII logging; handle copy/export carefully.
- Observability: add structured logs in dev; ensure errors surface with actionable context; avoid noisy logs in prod.
- DX & maintainability: clear folder structure, docs for new modules, minimal dependencies, pinned versions when needed.
- Internationalization readiness: avoid hard-coded concatenations; date/number formatting centralized; RTL-safe layouts.
- Build & CI: typecheck, lint, tests green before merge; avoid regressing quality gates.

## Quality Gates

- Build/Typecheck: PASS for edited Markdown components and integration; keep `page.tsx` clean.
- Hydration: 0 warnings on Markdown demo and conversation pages.
- Lint/Format: Keep Tailwind class ordering consistent; run formatter before commit.
- Unit/Smoke: Add fast smoke checks for code-block copy, input key handling, and error toasts when added.

## How to verify locally (optional)

1) Start dev server and navigate to a conversation.
2) Scroll up to see the glass arrow near the input; click to jump down.
3) Send a message: verify optimistic bubble and auto-scroll behavior.
4) Paste Markdown with a fenced code block: ensure code highlights, long lines wrap (no horizontal scroll), and Copy works.
5) After autosize lands: type multiple lines and confirm growth caps at ~6 rows; Enter/Shift+Enter semantics remain.
6) After per-message copy lands: hover a bubble to copy Markdown or Plain Text; verify “Copied” feedback.

---

This document reflects the current source of truth for the frontend chat experience. Implement the next steps in small PR-sized increments; after each increment, update this file and notify for verification.

