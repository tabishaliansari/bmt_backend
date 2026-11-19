# BMT · Design

The look is already designed. `frontend/` starts as a copy of `mock-ui/` and must keep its
system. Source of truth: `frontend/css/tokens.css` (tokens, light and dark) and the Figma
file "BMT · App Design".

## Principles

1. **Content is the hero.** Quiet greyscale UI; the editors' work is the loudest thing on screen.
2. **One colour, one meaning.** Never use a semantic colour for anything else.
3. **Familiar first.** Browse like Zomato, profiles like Instagram, tracking like a delivery app.
4. **Depth on demand.** Every tap reveals one more layer (sheets), never a settings maze.
5. **Show the AI working.** AI steps show progress and then a clear, editable result.

## Colour roles

| Token | Light | Meaning |
|---|---|---|
| `--ink` | `#0B0B0C` | Primary buttons, headings, decisions |
| `--cut` | `#FF5A1F` | Brand "playhead". Action and creative moments: ADD, active tab, Approve, AI results |
| `--trust` | `#0A84FF` | **Verified only** (blue check, credits) |
| `--safe` | `#1E9E5A` | **Money is safe** (escrow, payout) and ratings |
| `--canvas` / `--grouped` / `--line` | white / `#F2F2F7` / `#E5E5EA` | Surfaces and separators |

Dark theme is `body.T-dark` in `tokens.css`. Always use tokens; never hard-code a hex in JS.
In JS, use `BMT.ui.C.*`, which maps to the CSS variables.

## Type

SF Pro (system font stack). Large Title 34, Title 1 28, Title 2 22, Headline 17/600,
Body 17, Subhead 15, Footnote 13, Caption 12. SF Pro Rounded only for big live numbers.

## Layouts

Three layouts are already handled by `js/layout.js`: phone (full-bleed), phone frame
(scaled mockup), desktop (sidebar, grids, modal sheets). New screens must work in all three.
Test at 390 px and 1440 px.

## Reuse these components (`js/ui.js`)

`icon`, `seal`, `av`, `thumb`, `chip`, `rating`, `tabbar`/`sidebar`, `sheet`, `toast`,
`peek`. Cards: `.card-gray`, `.card-ink`, `.list-row`, `.stat-box`. Buttons: `.btn.primary`,
`.btn.secondary`, `.btn.accent`.

## New screens for the MVP

### 1. Start with your footage (`#/start`)
- Entry: a hero card on Discover, "Start with your footage · Gemini writes the brief".
- Drop zone (reuse `.dropzone`) for 1–3 clips, each with a thumbnail, name, size and an
  upload progress bar. A text area: "What's this video for?".
- Primary button "Write my brief". Disabled until at least one upload finishes.

### 2. Brief result (`#/brief/{id}`)
- While waiting: an ink card with a calm, honest progress line that cycles through
  "Watching your clips…", "Finding the best moments…", "Writing the brief…". No fake percentages.
- Result as a document-like card: title, format chip, target length, hook (highlighted),
  best moments as rows with timestamp chips in `--cut`, style notes, must-include checklist,
  questions for the client.
- Small label: "Written by Gemini · you can edit before ordering". Fields are editable inline.
- Footer: "Find editors for this" → recommended editors list → storefront.
- On the storefront, the recommended package shows a chip "Matches your brief".

### 3. Order tracking additions (`#/order/{id}`)
- A collapsible "Your brief" card.
- In demo mode, a secondary button "Upload the editor's cut" (stands in for the editor app).

### 4. AI review on the review screen (`#/review/{id}`)
- Button "Run AI review" (accent). While running: a progress line as above.
- Result panel: match score as a large rounded number (e.g. 82%), one-line summary,
  checklist with ticks and crosses, and notes. Each note becomes an orange marker on the
  scrubber; tapping a note seeks to its timestamp (the screen already supports this).
- Feedback box: "Tell the editor what you want, in your own words". Submitting runs the
  rewrite and adds the resulting notes with a "From your feedback" label.

### 5. Approval and payout
- Confirmation sheet as today. After approval, a receipt card in `--safe`:
  "Paid to Riya: ₹1,071.43 (US$12.74 at 84.10) via Ramp · simulated".

## States every new screen needs

Empty, uploading, waiting for AI, success, and error. Errors are plain and actionable:
"Gemini couldn't read this clip. Try a shorter MP4 under 50 MB." with a retry button.

## Copy rules

Short, plain, friendly. Sentence case. No jargon ("escrow" appears only in help sheets;
the UI says "Payment held safely"). Name the AI honestly ("Written by Gemini").
Simulated things are labelled as simulated.
