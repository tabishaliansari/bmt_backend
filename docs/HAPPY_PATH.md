# BMT · The happy path we submit and present

**Status:** locked on Fri 20 Nov, 12:18. Everything built today serves this path.
Anything not on it does not get built, fixed or demoed.

**Story:** a cafe owner turns two raw phone clips into a paid, approved reel, with Gemini
writing the brief and reviewing the cut, and BMT guaranteeing both sides.
**Length on stage:** about 3 minutes, including AI wait time.

## Cast

- **Client:** "Chai & Co.", a cafe launching in Pune. Played by Tabish on the laptop.
- **Editor:** **Mustafa Bhagat**, a real seeded editor profile with his real FilmPulse work as
  verified credits. Played by Mustafa. (Real founder plus real work beats a fake "Riya".)

## Demo assets (Mustafa prepares by 14:30)

- `raw_1.mp4`, `raw_2.mp4`: raw cafe-style clips, under 1 minute each, MP4.
- `cut.mp4`: a finished reel made **from those same raw clips**, about 30 s, with one deliberate
  flaw (for example, captions missing for a few seconds), so Review Copilot has something real to catch.
- 3 or 4 real FilmPulse credits for his profile: title, link, views, date.

## The path

| # | Screen | User action | What happens | Google service | Must show |
|---|---|---|---|---|---|
| 1 | Discover | Tap **Start with your footage** | Opens the upload screen | Cloud Run | Live public URL |
| 2 | Start with your footage | Upload `raw_1`, `raw_2`; note: "Launch reel for my cafe, warm and fun, 30 seconds" | Files stored | **Cloud Storage** | Upload progress, thumbnails |
| 3 | Brief result | Tap **Write my brief** | Gemini watches both clips and returns a structured brief | **Gemini on Vertex AI** | Hook, best moments with timestamps, must-haves, recommended package. Under 60 s |
| 4 | Recommended editors → Mustafa's storefront | Tap **Find editors**, open Mustafa, tap the blue check | Matching editors; verified credits sheet | Firestore | "Matches your brief" chip on the package; real FilmPulse credits |
| 5 | Order | Tap **ADD** on the matched package, then **Place order** | Order created with the brief attached; payment held | **Firestore** | "Payment held safely", order timeline |
| 6 | Order tracking | Tap **Upload the editor's cut** (stands in for the editor app), choose `cut.mp4` | Order moves to review | Cloud Storage | Status changes to "Cut is ready" |
| 7 | Review | Tap **Run AI review** | Gemini compares the cut with the brief | **Gemini on Vertex AI** | Match score, checklist, notes as markers; catches the planted flaw |
| 8 | Review | Type "make it more cinematic", send | Vague feedback becomes timestamped notes | Gemini on Vertex AI | New notes labelled "From your feedback" |
| 9 | Approve | Tap **Approve · release**, confirm | Payment released, payout record created | Firestore | Receipt: paid to Mustafa in INR via Ramp, **labelled simulated** |
| 10 | `/api/v1/healthz` | Open in a tab | Shows the running mode | Cloud Run | `vertex / gcs / firestore` |

## Not on the path (do not demo, do not fix)

Search, Learn, Community, Studio, Inbox, favourites, layout and theme switching, Taste Match
(unless finished and stable before the feature freeze), anything with real money or auth.

## Definition of done (all must be true by 20:00)

- [ ] The whole path runs on the **public Cloud Run URL**, from a laptop and from a phone.
- [ ] `/healthz` reports `vertex`, `gcs`, `firestore`.
- [ ] No mock data on the path, except the payout, which is labelled simulated.
- [ ] Each Gemini step finishes in under 60 s with the demo clips.
- [ ] The path passes **3 times in a row** from a clean state.
- [ ] A reset command restores the clean demo state in under a minute.
- [ ] A pre-made backup order exists at each stage (briefed, funded, in review), in case
      Gemini is slow on stage.

## Submission package (target: submit at 23:00 when the form opens)

1. **Live URL** (Cloud Run).
2. **GitHub repo**, public or shared, with the README covering what it is, the architecture, and how to run it.
3. **Demo video**, 2–3 minutes, recording exactly this path (screen recording plus voice-over).
4. **Pitch deck PDF**, updated with real screenshots from this path and the live URL.

Confirm the exact submission fields when the form opens. If it asks for something extra, it's
probably already in the repo docs.

## Checkpoints for today

| Time | Checkpoint |
|---|---|
| 13:30 | Steps 3, 7 and 8 work locally on **Vertex AI** with the real demo clips |
| 14:30 | Demo assets ready; Mustafa's profile seeded with real credits |
| 16:00 | Whole path works on **Cloud Run** (SQLite and `--max-instances=1` allowed). Show it at the 4 PM check-in |
| 18:00 | Cloud Storage and Firestore switched on; path passes on the cloud URL |
| **20:00** | **Feature freeze.** Path passes 3 times in a row. After this, only fixes that protect the path |
| 20:00–22:30 | Record the demo video, take deck screenshots, finish the README |
| 23:00 | Submit. Then sleep |

## Fallbacks on stage

- Gemini slow: open the backup order already at that stage and keep talking.
- Upload fails: use the backup order that already has the clips.
- Anything else: play the demo video and narrate over it.