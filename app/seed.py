"""Demo editors, packages and add-ons, ported from mock-ui/js/api.js.

INR prices are the mock's prices. USD prices are set by hand (about INR / 84, ending in .99).
Written to the database on every startup, so edits here apply after a restart.
"""

from app.db.base import Database
from app.models import Addon, Catalog, Credit, Editor, Package, Review


def pkg(editor_id: str, id: str, title: str, desc: str, inr: float, usd: float,
        eta_hours: int, g: int, tag: str | None = None) -> Package:
    return Package(id=id, editor_id=editor_id, title=title, desc=desc, price_inr=inr,
                   price_usd=usd, eta_hours=eta_hours, tag=tag, g=g)


def credit(g: int, title: str, channel: str, views: str, date: str, length: str) -> Credit:
    return Credit(g=g, title=title, channel=channel, views=views, date=date, len=length)


def review(name: str, av: int, stars: int, text: str, item: str, when: str) -> Review:
    return Review(name=name, av=av, stars=stars, text=text, item=item, when=when)


EDITORS: list[Editor] = [
    # The demo editor: co-founder Mustafa Bhagat. TODO before 14:30: replace credit_list,
    # credits, channels and views with his real FilmPulse work (title, link, views, date).
    Editor(
        id="mustafa", featured=True, name="Mustafa Bhagat", initials="MB", av=3, handle="filmpulse",
        city="India", styles=["Reels", "Cinematic"], categories=["reels", "youtube"], cover=2,
        rating=4.9, rating_count=48, credits=0, channels=0, views="0", on_time=99,
        reply="15 min", from_inr=999, days="2 days",
        packages=[
            pkg("mustafa", "taste", "Taste test", "15 sec from your own footage. See the style before you commit.", 199, 2.49, 12, 5, "try"),
            pkg("mustafa", "reel", "Instagram Reel", "Up to 60s · captions · colour grade · 2 revisions", 999, 12.99, 48, 2, "best"),
            pkg("mustafa", "yt", "YouTube edit", "Up to 12 min · pacing, B-roll, sound design · 2 revisions", 3499, 41.99, 96, 0),
        ],
        credit_list=[],
        reviews=[],
        work=[2, 7, 0, 5],
    ),
    Editor(
        id="riya", name="Riya Kapoor", initials="RK", av=0, handle="riyacuts", city="Mumbai",
        styles=["Vlogs", "Reels"], categories=["reels", "youtube"], cover=7,
        rating=4.9, rating_count=212, credits=34, channels=9, views="12.4M", on_time=98,
        reply="20 min", from_inr=999, days="2 days",
        packages=[
            pkg("riya", "taste", "Taste test", "15 sec from your own footage. See her style before you commit.", 199, 2.49, 12, 5, "try"),
            pkg("riya", "reel", "Instagram Reel", "Up to 60s · captions · colour grade · 2 revisions", 999, 12.99, 48, 2, "best"),
            pkg("riya", "yt", "YouTube edit", "Up to 12 min · pacing, B-roll, sound design · 2 revisions", 3499, 41.99, 96, 0),
            pkg("riya", "shorts", "Long video → 5 Shorts", "Hooks rewritten, vertical reframe, captions", 1999, 23.99, 72, 3),
        ],
        credit_list=[
            credit(0, "I Lived on ₹500 for a Week in Mumbai", "Rohan Explores", "2.1M", "Oct 2026", "14:32"),
            credit(6, "Street Food Tour: Old Delhi at 2 AM", "Foodie Nomads", "1.4M", "Sep 2026", "18:10"),
            credit(2, "How I Built a ₹1 Crore Brand", "The Bootstrap Show", "890K", "Aug 2026", "22:47"),
            credit(8, "Monsoon in Kerala · 4K Cinematic", "Wander Frames", "640K", "Jul 2026", "09:05"),
        ],
        reviews=[
            review("Arjun M.", 1, 5, "Turned 40 minutes of rambling into a reel that did 300K. Fast, and she actually listens to notes.", "Instagram Reel", "2 days ago"),
            review("Sana K.", 4, 5, "Did the taste test first, ordered the full edit the same night. Captions were on point.", "Taste test", "1 week ago"),
            review("Vikram R.", 3, 4, "Great pacing. One revision took a day longer than promised, but quality was worth it.", "YouTube edit", "2 weeks ago"),
        ],
        work=[7, 2, 0, 5, 3, 9],
    ),
    Editor(
        id="kabir", name="Kabir Shah", initials="KS", av=1, handle="kabirgrades", city="Bengaluru",
        styles=["Cinematic", "Ads"], categories=["ads", "weddings", "youtube"], cover=1,
        rating=4.8, rating_count=96, credits=21, channels=6, views="5.8M", on_time=95,
        reply="1 hr", from_inr=2499, days="3 days",
        packages=[
            pkg("kabir", "taste", "Taste test", "One 10s graded shot from your footage.", 249, 2.99, 24, 4, "try"),
            pkg("kabir", "ad", "30s Product Ad", "Cinematic grade, sound design, 3 aspect ratios", 2499, 29.99, 72, 6, "best"),
            pkg("kabir", "grade", "Colour grade only", "Up to 10 min, look-matched across cameras", 1799, 21.99, 48, 1),
        ],
        credit_list=[
            credit(1, "Bengaluru After Dark · Short Film", "Lens & Lights", "1.9M", "Sep 2026", "11:20"),
            credit(6, "We Tried the ₹50,000 Tasting Menu", "Foodie Nomads", "1.1M", "Aug 2026", "16:44"),
        ],
        reviews=[review("Meher P.", 2, 5, "The ad looked like a TV spot. Our CTR doubled.", "30s Product Ad", "5 days ago")],
        work=[1, 6, 4, 8],
    ),
    Editor(
        id="ananya", name="Ananya Nair", initials="AN", av=4, handle="ananyamotion", city="Pune",
        styles=["Motion", "Explainers"], categories=["ads", "youtube"], cover=9,
        rating=4.9, rating_count=143, credits=28, channels=11, views="8.2M", on_time=99,
        reply="15 min", from_inr=1499, days="3 days",
        packages=[
            pkg("ananya", "taste", "Taste test", "A 5s animated title card in your brand colours.", 199, 2.49, 12, 5, "try"),
            pkg("ananya", "titles", "Animated titles pack", "Intro, lower thirds, outro. Editable source files.", 1499, 17.99, 72, 9, "best"),
            pkg("ananya", "explainer", "60s Explainer", "Script polish, motion graphics, voiceover sync", 4999, 59.99, 144, 0),
        ],
        credit_list=[credit(9, "How UPI Actually Works", "Finance Simplified", "3.2M", "Oct 2026", "08:12")],
        reviews=[review("Rahul D.", 3, 5, "Explainer was crisp, delivered a day early.", "60s Explainer", "3 days ago")],
        work=[9, 0, 5],
    ),
    Editor(
        id="arjun", name="Arjun Mehta", initials="AM", av=2, handle="arjunclips", city="Delhi",
        styles=["Podcasts", "Shorts"], categories=["podcasts", "reels"], cover=3,
        rating=4.7, rating_count=188, credits=52, channels=14, views="21M", on_time=96,
        reply="30 min", from_inr=1999, days="3 days",
        packages=[
            pkg("arjun", "taste", "Taste test", "One 30s clip from your episode.", 149, 1.99, 12, 3, "try"),
            pkg("arjun", "pod", "Podcast → 5 Shorts", "Best moments found for you, captions, reframing", 1999, 23.99, 72, 3, "best"),
            pkg("arjun", "full", "Full episode edit", "Multi-cam switching, cleanup, chapters", 3999, 47.99, 96, 4),
        ],
        credit_list=[credit(3, "The Founder Who Said No to ₹100 Crore", "The Bootstrap Show", "4.4M", "Oct 2026", "01:02")],
        reviews=[review("Priya S.", 0, 5, "He finds the moments I'd never have picked. Shorts keep going viral.", "Podcast → 5 Shorts", "1 day ago")],
        work=[3, 4, 2],
    ),
    Editor(
        id="meera", name="Meera Iyer", initials="MI", av=5, handle="meeraweds", city="Chennai",
        styles=["Weddings", "Films"], categories=["weddings"], cover=7,
        rating=4.9, rating_count=61, credits=12, channels=3, views="1.1M", on_time=100,
        reply="2 hr", from_inr=7999, days="10 days",
        packages=[
            pkg("meera", "teaser", "Wedding teaser", "90s cinematic teaser for socials", 7999, 94.99, 168, 7, "best"),
            pkg("meera", "film", "Wedding film", "8–12 min story edit, licensed music", 24999, 297.99, 504, 5),
        ],
        credit_list=[credit(7, "A Monsoon Wedding in Kochi", "Meera Films", "520K", "Aug 2026", "10:40")],
        reviews=[review("Karan & Diya", 1, 5, "We cried. Our parents cried. Worth every rupee.", "Wedding film", "1 month ago")],
        work=[7, 5],
    ),
    Editor(
        id="dev", name="Dev Patel", initials="DP", av=3, handle="devframes", city="Ahmedabad",
        styles=["Gaming", "Montage"], categories=["gaming", "youtube"], cover=8,
        rating=4.6, rating_count=77, credits=18, channels=7, views="6.3M", on_time=93,
        reply="45 min", from_inr=1299, days="2 days",
        packages=[
            pkg("dev", "montage", "Gaming montage", "Beat-synced, up to 3 min, SFX pack", 1299, 15.99, 48, 8, "best"),
            pkg("dev", "stream", "Stream → highlights", "Find the best plays from a 3h VOD", 1799, 21.99, 72, 1),
        ],
        credit_list=[credit(8, "BGMI Clutch Moments · Season 4", "ClutchKing", "2.7M", "Oct 2026", "12:00")],
        reviews=[review("Yash T.", 2, 5, "Sync on the drops is insane.", "Gaming montage", "4 days ago")],
        work=[8, 1],
    ),
]


CATALOG = Catalog(
    addons=[
        Addon(id="captions", icon="cc", title="Animated captions", sub="Word-by-word, on-brand", price_inr=199, price_usd=2.00),
        Addon(id="thumb", icon="image", title="Custom thumbnail", sub="1 design, 2 options", price_inr=149, price_usd=1.79),
        Addon(id="music", icon="music", title="Licensed music", sub="Royalty-free track", price_inr=99, price_usd=1.19),
        Addon(id="revision", icon="repeat", title="Extra revision", sub="3 rounds instead of 2", price_inr=99, price_usd=1.19),
    ],
    rush_fee_inr=300,
    rush_fee_usd=3.59,
)


def seed(db: Database) -> None:
    for editor in EDITORS:
        db.put("editors", editor.id, editor.model_dump(mode="json"))
