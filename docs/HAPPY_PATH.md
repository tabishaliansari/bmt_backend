# BMT · The happy path we submit and present

**Status:** v2, updated Fri 20 Nov, 12:54. Everything built today serves this path.
Anything not on it does not get built, fixed or demoed. v1 (12:18) was the starting point;
v2 adds more Google AI where it strengthens the story (see "Why these Google services").

**Story:** a cafe owner turns two raw phone clips into a paid, approved reel. Gemini writes
the brief and reviews the cut, Nano Banana drafts the thumbnail, Gemma screens what people
type, and BMT guarantees both sides.
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

Priority: **P0** must ship. **P1** ships if P0 is on track at 16:00. **P2** only if P0 and P1
pass on the cloud URL by 18:00; otherwise it goes in the deck as roadmap.

| # | Screen | User action | What happens | Google service | Must show | Pri |
|---|---|---|---|---|---|---|
| 0 | Sign in (before going on stage) | **Continue with Google** | Session persists; footage, briefs and orders are private to this account | **Firebase Authentication** | Name in the sidebar | P0 |
| 1 | Discover | Tap **Start with your footage** | Opens the upload screen | **Cloud Run** | Live public URL | P0 |
| 2 | Start with your footage | Upload `raw_1`, `raw_2`; note: "Launch reel for my cafe, warm and fun, 30 seconds" | Files stored | **Cloud Storage** | Upload progress, thumbnails | P0 |
| 3 | Start → Brief result | Tap **Write my brief** | **Gemma** screens the note (abuse, personal data), then **Gemini** watches both clips and returns a structured brief | **Gemma**, **Gemini on Vertex AI** | Hook, best moments with timestamps, must-haves, recommended package. Small label "Note checked by Gemma". Under 60 s | P0 (Gemma P1) |
| 4 | Brief result | Tap **Draft a thumbnail** | **Nano Banana** generates a thumbnail concept from the brief's title, hook and style | **Nano Banana** (Gemini image) | One thumbnail image on the brief, labelled "Drafted by Nano Banana" | P1 |
| 5 | Recommended editors → Mustafa's storefront | Tap **Find editors**, open Mustafa, tap the blue check | Matching editors; verified credits sheet | **Firestore** | "Matches your brief" chip on the package; real FilmPulse credits | P0 |
| 6 | Order | Tap **ADD** on the matched package, then **Place order** | Order created with the brief (and thumbnail) attached; payment held | **Firestore** | "Payment held safely", order timeline | P0 |
| 7 | Order tracking | Tap **Upload the editor's cut** (stands in for the editor app), choose `cut.mp4` | Order moves to review | **Cloud Storage** | Status changes to "Cut is ready" | P0 |
| 8 | Review | Tap **Run AI review** | Gemini compares the cut with the brief (Gemini Omni if it tests clearly better on audio and music) | **Gemini on Vertex AI** / **Gemini Omni** | Match score, checklist, notes as markers; catches the planted flaw | P0 |
| 9 | Review | Type "make it more cinematic", send | **Gemma** screens it, then Gemini turns vague feedback into timestamped notes | **Gemma**, **Gemini on Vertex AI** | New notes labelled "From your feedback" | P0 (Gemma P1) |
| 10 | Approve | Tap **Approve · release**, confirm | Payment released, payout record created | **Firestore** | Receipt: paid to Mustafa in INR via Ramp, **labelled simulated** | P0 |
| 11 | `/api/v1/healthz` | Open in a tab | Shows the running mode and which model does which job | **Cloud Run** | `vertex / gcs / firestore`, plus the model per task | P0 |

### P2 additions (only if green at 18:00)

| Where | Feature | Google service |
|---|---|---|
| Step 4, brief result | **Suggest music**: a 30 s royalty-free track matching the brief's style notes, tied to the "Licensed music" add-on | **Lyria** |
| Step 2, start | **Say it instead**: speak the note instead of typing it | **Gemini Live** |

## Why these Google services

Each one does a job the others would do worse, which is the story for "Google AI Integration &
Implementation Depth" (20%):

| Job | Model | Why this one |
|---|---|---|
| Watch footage, write the brief, review the cut | Gemini (Vertex AI) | Native video understanding with structured output |
| Judge a cut's audio, music and pacing | Gemini Omni (if it tests better) | Any-to-any model; stronger on audio |
| Screen what people type | Gemma | Small open model: cheap, fast, right-sized for a filter |
| Draft a thumbnail | Nano Banana | Image generation from the brief |
| Suggest music (P2) | Lyria | Royalty-free music generation |
| Voice brief (P2) | Gemini Live | Real-time voice |

Platform: **Cloud Run** (one service: API + frontend), **Cloud Storage** (clips and cuts),
**Firestore** (orders, briefs, editors), **Firebase Authentication** (Google sign-in; each
account sees only its own data), **Secret Manager** (Gemini key, media signing key), **Cloud Build** and
**Artifact Registry** (image build), **Cloud Logging**. Tools: prompts tuned in **Google AI
Studio**; say "built with **Antigravity**" only for work actually done in it today. Ask a mentor
what **Google Agent Skills** means for judging before planning around it.

## Not on the path (do not demo, do not fix)

Search, Learn, Community, Studio, Inbox, favourites, layout and theme switching, Taste Match,
anything with real money or auth.

## Definition of done (all must be true by 20:00)

- [ ] The whole P0 path runs on the **public Cloud Run URL**, from a laptop and from a phone.
- [ ] `/healthz` reports `vertex`, `gcs`, `firestore` and the model per task.
- [ ] No mock data on the path, except the payout, which is labelled simulated.
- [ ] Each Gemini step finishes in under 60 s with the demo clips (otherwise: background job + polling).
- [ ] The path passes **3 times in a row** from a clean state.
- [ ] A reset command restores the clean demo state in under a minute.
- [ ] A pre-made backup order exists at each stage (briefed, funded, in review), in case
      Gemini is slow on stage.
- [ ] Security minimum: rate limits on the AI endpoints; order ids not guessable.

## Submission package (target: submit at 23:00 when the form opens)

1. **Live URL** (Cloud Run).
2. **GitHub repos** (`bmt_backend`, `bmt_frontend`), public or shared, with READMEs covering what
   it is, the architecture, and how to run it.
3. **Demo video**, 2–3 minutes, recording exactly this path (screen recording plus voice-over).
4. **Pitch deck PDF**, updated with real screenshots from this path, the live URL and the
   "Why these Google services" table.
5. **Miro flowchart** of this path (board linked in the README).

Confirm the exact submission fields when the form opens. If it asks for something extra, it's
probably already in the repo docs.

## Checkpoints for today

| Time | Checkpoint |
|---|---|
| 13:45 | Steps 3, 8 and 9 work locally on **Vertex AI** with real clips; Mustafa's profile seeded |
| 14:30 | Demo assets ready |
| 15:00 | Deployed to **Cloud Run** (SQLite and `--max-instances=1` allowed); Gemini key in Secret Manager |
| 16:00 | **4 PM check-in:** show the cloud URL. Nano Banana (step 4) and Gemma (steps 3, 9) in |
| 18:00 | Cloud Storage and Firestore switched on; P0 + P1 path passes on the cloud URL. Go / no-go on P2 |
| **20:00** | **Feature freeze.** Path passes 3 times in a row. After this, only fixes that protect the path |
| 20:00–22:30 | Record the demo video, take deck screenshots, finish the READMEs |
| 23:00 | Submit. Then sleep |

## Fallbacks on stage

- Gemini slow: open the backup order already at that stage and keep talking.
- Upload fails: use the backup order that already has the clips.
- Nano Banana slow or fails: the brief still works without a thumbnail; skip step 4.
- Anything else: play the demo video and narrate over it.
