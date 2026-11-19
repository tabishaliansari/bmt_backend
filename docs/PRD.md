# BMT · Product Requirements (Buildathon MVP)

## One-liner

BMT is an AI-native marketplace where clients anywhere in the world hire video editors
as easily as they order food, by browsing fixed-price packages from editors whose past
work Gemini has verified. BMT stands behind both sides: clients only pay when they
approve the final cut, and editors get paid reliably in their own currency through Ramp.

## Problem

- **Clients** (creators, small brands, agencies) can't find good editors on generic
  freelance sites, can't tell real portfolios from copied reels, and don't know how to
  brief an editor. Projects drag through revisions and disputes.
- **Editors**, especially in India, can't prove their best work, and when a foreign client
  pays, PayPal fees, currency conversion, taxes and bank charges eat their earnings.
- Both sides work on blind trust.

## Users

| User | Who | What they need |
|---|---|---|
| Client | YouTuber, podcaster, D2C brand, agency (India, US, UK, Canada, Australia, UAE) | Proof an editor is good, a clear brief, a known price and date, no risk of losing money |
| Editor | Freelance video editor, often in India | A way to prove their work, steady clients, reliable payment in INR |

Co-founder Mustafa (editor and creator, runs FilmPulse, 211K+ Instagram followers) is
our reference editor user and the quality judge for every AI output.

## Product pillars

1. **Menus, not bids.** Fixed-price packages, starting with a cheap taste test.
2. **Verified credits.** Real published work, confirmed and cross-checked by Gemini.
3. **Client guarantee.** Money is held in escrow until the client approves the cut.
4. **Editor guarantee.** Payout on approval, in local currency, via Ramp.

## AI features (Gemini)

| Feature | What it does | MVP status |
|---|---|---|
| **Brief Builder** | Watches the client's raw clips plus a note, writes a structured brief, recommends a package | **Build tonight** |
| **Review Copilot** | Compares a delivered cut with the brief, returns timestamped notes; rewrites vague client feedback into timestamped notes | **Build tonight** |
| Taste Match | Embeds a reference reel, ranks editors by style similarity (Vertex AI multimodal embeddings) | Stretch, Day 1 evening |
| Proof Engine | Cross-checks an editor's export against a published video; YouTube stats | Stretch / roadmap |
| Gemini Live, Nano Banana, Lyria | Voice briefs, thumbnail drafts, royalty-free music | Roadmap (in deck only) |

## MVP happy path (must work end to end)

1. Client opens **Start with your footage**, uploads 1–3 short clips and a note.
2. **Brief Builder** returns a brief: format, length, hook, best moments with timestamps,
   style notes, must-haves, recommended package.
3. Client taps **Find editors**, opens an editor storefront, orders the recommended package.
   The brief is attached to the order.
4. Order is **funded** (escrow simulated). Status timeline shows it.
5. Editor delivers a cut (we upload a finished video as the "cut").
6. Client runs **AI review**: Review Copilot returns a match score, a checklist and
   timestamped notes, shown as markers on the review player. Client can type vague
   feedback and get it rewritten into timestamped notes.
7. Client **approves**: escrow released, payout record shown as
   "Paid to editor in INR via Ramp (simulated)".

## Out of scope for the buildathon

Auth and accounts, real payments, real Ramp integration, chat, notifications, editor
onboarding, search ranking, Proof Engine, mobile apps, admin tools. Stubs or labels only.

## Success criteria (mapped to judging)

| Judging criterion | How the MVP shows it |
|---|---|
| Founder profile | Team slide, Mustafa's real work in the demo |
| Product potential | The happy path works live on real footage |
| Market viability | India to US corridor, two-sided guarantee, business model slide |
| Technical architecture | Clean backend with env switches, deployed on Cloud Run |
| Use of Google AI | Gemini does the two hardest jobs live; Vertex AI, Cloud Storage, Firestore, Cloud Run in production |

## Business model (for reference)

Platform fee per order (kept on approval), small margin on cross-border payouts (still far
cheaper than PayPal plus FX), share of course and 1:1 sales, later an Editor Pro subscription.
