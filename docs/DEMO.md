# BMT · Demo script

Everything we build serves this script. Target: **3 minutes** live, plus a recorded
backup video of the same flow. Mustafa narrates the editor's side, Tabish the product and tech.

## Setup before going on stage

- Cloud Run URL open in a browser, desktop layout, light theme. Phone ready for the mobile layout.
- Clean demo data. Two short raw clips and one finished edit ready on the laptop.
- One brief already generated (fallback if the network is slow).
- `/api/v1/healthz` open in a tab: shows `vertex / gcs / firestore`.
- Recorded demo video ready to play if anything breaks.

## Script

**0:00 · Problem (20 s, Mustafa)**
"I'm Mustafa. I edit videos and run FilmPulse, with over 211K followers. Clients can't tell
whether I'm good, they don't know how to brief me, and when a US client pays me, PayPal
and conversion fees take a real chunk of it."

**0:20 · Brief Builder (50 s, Tabish)**
Upload two raw clips, type "Reel for a cafe launch, fun, 30 seconds". Tap **Write my brief**.
While Gemini works: "Gemini on Vertex AI is watching the actual footage." Show the brief:
hook, best moments with timestamps, must-haves, recommended package.

**1:10 · Order (25 s)**
Tap **Find editors**, open Riya, the package shows "Matches your brief". Order.
"The money is now held safely. The editor can see it's funded, so they start right away."

**1:35 · Review Copilot (50 s)**
Upload the finished edit as the editor's cut. Tap **Run AI review**. Show the match score,
checklist, and notes as markers on the scrubber. Type "make it more cinematic", show it
turned into timestamped notes. Mustafa: "As an editor, this is the brief I always wanted."

**2:25 · Approve and payout (20 s)**
Approve. Show the receipt: paid to the editor in INR via Ramp (simulated, labelled).
"We guarantee the work for the client and the payment for the editor."

**2:45 · Close (15 s)**
Flash `/healthz` and the architecture slide: Cloud Run, Vertex AI, Cloud Storage, Firestore.
"Verified editors, AI-written briefs, AI-reviewed cuts, and payments that just work."

## If something breaks

- Gemini slow: switch to the pre-generated brief and keep talking.
- Upload fails: use the clips already uploaded in the demo data.
- Anything else: play the recorded video and narrate over it.
