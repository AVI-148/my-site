"""Builds the static site from _src/ into the repo root.

Run:  python build.py
Each page body lives in _src/pages/<name>.html. This script wraps it with the
shared <head>, header menu, footer and WhatsApp button, and writes
<folder>/index.html. Destination cards come from the DESTINATIONS list below.
Vercel serves the generated HTML as-is (no build step on Vercel).
"""
import json
import os
from html import escape
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "_src", "pages")
SITE = "https://tziunei-derech.vercel.app"
PHONE = "058-3210-148"
PHONE_INTL = "972583210148"
EMAIL = "a0583210148@gmail.com"
GOOGLE_REVIEW = "https://g.page/r/CWj-uxINh2JdEAI/review"
OG_IMAGE = SITE + "/assets/og-image.png"
YEAR = 2026

# ---------------------------------------------------------------- pages
# path: URL path ("/" or "/שם"); out: output file relative to ROOT
PAGES = [
    dict(name="home", path="/", out="index.html", nav="בית",
         title="ציוני דרך | סוכנות נסיעות לקברי צדיקים",
         description="ציוני דרך – סוכנות נסיעות לקברי צדיקים באירופה ובכל העולם: אומן, ליז'ענסק, קרעסטיר ועוד. טיסות, לינה והסעות מהשדה ליחידים ולקבוצות. סוכנות הנסיעות של שמעון אולמן, טל' 058-3210-148"),
    dict(name="destinations", path="/יעדים", nav="יעדים",
         title="יעדים – נסיעות לקברי צדיקים באירופה ובעולם | ציוני דרך",
         description="נסיעות לקברי צדיקים באוקראינה, פולין, הונגריה, צ'כיה, ארה\"ב ולכל יעד אחר בעולם. טיסות, לינה והסעות מסודרות עם ציוני דרך."),
    dict(name="services", path="/שירותים", nav="שירותים",
         title="השירותים שלנו – טיסות, לינה והסעות | ציוני דרך",
         description="ציוני דרך דואגים לכל הנסיעה: כרטיסי טיסה לכל יעד, לינה קרובה לציון, הסעות משדה התעופה וארגון נסיעות לקבוצות."),
    dict(name="luach", path="/שבת-חנוכה", nav="לוח טיסות",
         title="שבת חנוכה באומן תשפ\"ז – לוח טיסות | ציוני דרך",
         description="שבת חנוכה באומן תשפ\"ז: לוח טיסות הלוך וחזור לשבת חנוכה באומן דרך קישינב ובוקרשט, מחירים ופרטי כבודה. ציוני דרך, טל' 058-3210-148"),
    dict(name="contact", path="/צור-קשר", nav="צור קשר",
         title="צור קשר | ציוני דרך – נסיעות לקברי צדיקים",
         description="דברו עם ציוני דרך: טלפון 058-3210-148, וואטסאפ ומייל. נשמח לתכנן איתכם את הנסיעה הבאה לקברי צדיקים."),
    dict(name="404", path="/404", out="404.html", nav=None, noindex=True,
         title="הדף לא נמצא | ציוני דרך",
         description="הדף שחיפשתם לא נמצא באתר ציוני דרך."),
]

# ---------------------------------------------------------------- destinations
# Draft list – confirm with the business which destinations to show.
DESTINATIONS = [
    ("אוקראינה", [
        ("אומן", "רבי נחמן מברסלב", True),
        ("מז'יבוז'", "הבעל שם טוב", True),
        ("ברסלב", "רבי נתן מברסלב", False),
        ("ברדיטשוב", "רבי לוי יצחק מברדיטשוב", True),
        ("אניפולי", "רבי זושא מאניפולי והמגיד ממזריטש", False),
    ]),
    ("פולין", [
        ("ליז'ענסק", "רבי אלימלך מליז'ענסק", True),
        ("קרקוב", "הרמ\"א", False),
        ("לובלין", "החוזה מלובלין", False),
    ]),
    ("הונגריה", [
        ("קרעסטיר", "רבי ישעיה מקרעסטיר", True),
    ]),
    ("צ'כיה", [
        ("פראג", "המהר\"ל מפראג", True),
    ]),
    ("ארצות הברית", [
        ("ניו יורק", "האוהל – ציון הרבי מליובאוויטש", True),
    ]),
]

# ---------------------------------------------------------------- icons (lucide, MIT)
def icon(paths, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"{c}>{paths}</svg>')

ICONS = {
    "phone": '<path d="M13.832 16.568a1 1 0 0 0 1.213-.303l.355-.465A2 2 0 0 1 17 15h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2A18 18 0 0 1 2 4a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2v3a2 2 0 0 1-.8 1.6l-.468.351a1 1 0 0 0-.292 1.233 14 14 0 0 0 6.392 6.384"/>',
    "mail": '<path d="m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7"/><rect x="2" y="4" width="20" height="16" rx="2"/>',
    "plane": '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>',
    "hotel": '<path d="M10 22v-6.57"/><path d="M12 11h.01"/><path d="M12 7h.01"/><path d="M14 15.43V22"/><path d="M15 16a5 5 0 0 0-6 0"/><path d="M16 11h.01"/><path d="M16 7h.01"/><path d="M8 11h.01"/><path d="M8 7h.01"/><rect x="4" y="2" width="16" height="20" rx="2"/>',
    "bus": '<path d="M8 6v6"/><path d="M15 6v6"/><path d="M2 12h19.6"/><path d="M18 18h3s.5-1.7.8-2.8c.1-.4.2-.8.2-1.2 0-.4-.1-.8-.2-1.2l-1.4-5C20.1 6.8 19.1 6 18 6H4a2 2 0 0 0-2 2v10h3"/><circle cx="7" cy="18" r="2"/><path d="M9 18h5"/><circle cx="16" cy="18" r="2"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><path d="M16 3.128a4 4 0 0 1 0 7.744"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><circle cx="9" cy="7" r="4"/>',
    "star": '<path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"/>',
    "menu": '<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/>',
    "arrow": '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
}

WA_SVG = ('<svg viewBox="0 0 448 512" fill="currentColor" aria-hidden="true"><path d="M380.9 97.1C339 55.1 283.2 32 223.9 32c-122.4 0-222 99.6-222 222 0 39.1 10.2 77.3 29.6 111L0 480l117.7-30.9c32.4 17.7 68.9 27 106.1 27h.1c122.3 0 224.1-99.6 224.1-222 0-59.3-25.2-115-67.1-157zm-157 341.6c-33.2 0-65.7-8.9-94-25.7l-6.7-4-69.8 18.3L72 359.2l-4.4-7c-18.5-29.4-28.2-63.3-28.2-98.2 0-101.7 82.8-184.5 184.6-184.5 49.3 0 95.6 19.2 130.4 54.1 34.8 34.9 56.2 81.2 56.1 130.5 0 101.8-84.9 184.6-186.6 184.6zm101.2-138.2c-5.5-2.8-32.8-16.2-37.9-18-5.1-1.9-8.8-2.8-12.5 2.8-3.7 5.6-14.3 18-17.6 21.8-3.2 3.7-6.5 4.2-12 1.4-32.6-16.3-54-29.1-75.5-66-5.7-9.8 5.7-9.1 16.3-30.3 1.8-3.7.9-6.9-.5-9.7-1.4-2.8-12.5-30.1-17.1-41.2-4.5-10.8-9.1-9.3-12.5-9.5-3.2-.2-6.9-.2-10.6-.2-3.7 0-9.7 1.4-14.8 6.9-5.1 5.6-19.4 19-19.4 46.3 0 27.3 19.9 53.7 22.6 57.4 2.8 3.7 39.1 59.7 94.8 83.8 35.2 15.2 49 16.5 66.6 13.9 10.7-1.6 32.8-13.4 37.4-26.4 4.6-13 4.6-24.1 3.2-26.4-1.3-2.5-5-3.9-10.5-6.7z"/></svg>')


def wa_link(text=None):
    base = f"https://wa.me/{PHONE_INTL}"
    return base + ("?text=" + quote(text) if text else "")


# ---------------------------------------------------------------- partials
def dest_card(city, tzadik, country):
    msg = f"שלום, אשמח לקבל פרטים על נסיעה ל{city}"
    return f'''<article class="td-card td-dest">
  <span class="td-dest__country">{escape(country)}</span>
  <h3>{escape(city)}</h3>
  <p>{escape(tzadik)}</p>
  <a class="td-dest__link" href="{escape(wa_link(msg))}" target="_blank" rel="noopener noreferrer">לפרטים בוואטסאפ {icon(ICONS["arrow"])}</a>
</article>'''


def destinations_all():
    out = []
    for country, places in DESTINATIONS:
        cards = "\n".join(dest_card(c, t, country) for c, t, _ in places)
        out.append(f'<section class="td-region" aria-labelledby="r-{escape(country)}">\n'
                   f'<h2 id="r-{escape(country)}">{escape(country)}</h2>\n<div class="td-grid">\n{cards}\n</div>\n</section>')
    return "\n".join(out)


def destinations_popular():
    cards = [dest_card(c, t, country) for country, places in DESTINATIONS for c, t, pop in places if pop]
    cards.append('''<a class="td-card td-dest td-dest--more" href="/יעדים">
  <h3>ועוד יעדים</h3>
  <p>אנחנו מגיעים לכל יעד באירופה ובעולם</p>
  <span>לכל היעדים ←</span>
</a>''')
    return "\n".join(cards)


def header(active_path):
    links = []
    for p in PAGES:
        if not p.get("nav"):
            continue
        cur = ' aria-current="page"' if p["path"] == active_path else ""
        links.append(f'<a href="{p["path"]}"{cur}>{p["nav"]}</a>')
    links.append(f'<a class="td-nav__cta" href="tel:{PHONE}">{icon(ICONS["phone"])} {PHONE}</a>')
    return f'''<header class="td-header">
  <div class="td-header__inner">
    <a class="td-brand" href="/" aria-label="ציוני דרך – לדף הבית">
      <img src="/favicon.png" alt="" width="40" height="40">
      <span><strong>ציוני דרך</strong><small>פשוט להגיע לצדיקים</small></span>
    </a>
    <button class="td-menu-btn" type="button" aria-expanded="false" aria-controls="td-nav" aria-label="פתיחת תפריט">{icon(ICONS["menu"])}</button>
    <nav id="td-nav" class="td-nav" aria-label="ניווט ראשי">
      {"\n      ".join(links)}
    </nav>
  </div>
</header>'''


def footer():
    nav = "\n".join(f'<li><a href="{p["path"]}">{p["nav"]}</a></li>' for p in PAGES if p.get("nav"))
    return f'''<footer class="td-footer">
  <div class="td-footer__inner">
    <div class="td-footer__brand">
      <strong>ציוני דרך</strong>
      <p>סוכנות נסיעות לקברי צדיקים באירופה ובכל העולם. טיסות, לינה והסעות – כדי שאתם תתפנו לתפילה.</p>
    </div>
    <div>
      <h2>ניווט</h2>
      <ul>
{nav}
      </ul>
    </div>
    <div>
      <h2>יצירת קשר</h2>
      <ul>
        <li><a href="tel:{PHONE}" dir="ltr">{PHONE}</a></li>
        <li><a href="{wa_link()}" target="_blank" rel="noopener noreferrer">וואטסאפ</a></li>
        <li><a href="mailto:{EMAIL}" dir="ltr">{EMAIL}</a></li>
        <li><a href="{GOOGLE_REVIEW}" target="_blank" rel="noopener noreferrer">דרגו אותנו בגוגל</a></li>
      </ul>
    </div>
  </div>
  <div class="td-footer__bottom">© {YEAR} ציוני דרך · פשוט להגיע לצדיקים</div>
</footer>'''


WA_FLOAT = f'''<a class="wa-float" href="{wa_link()}" target="_blank" rel="noopener noreferrer" aria-label="דברו איתנו בוואטסאפ" dir="ltr">
  <span class="wa-float__text" dir="rtl">דברו איתנו</span>
  <span class="wa-float__icon">{WA_SVG}</span>
</a>'''

MENU_JS = """<script>
(function () {
  var h = document.querySelector('.td-header'), b = h && h.querySelector('.td-menu-btn');
  if (!b) return;
  b.addEventListener('click', function () {
    var open = h.classList.toggle('is-open');
    b.setAttribute('aria-expanded', open ? 'true' : 'false');
    b.setAttribute('aria-label', open ? 'סגירת תפריט' : 'פתיחת תפריט');
  });
})();
</script>"""

PARALLAX_JS = """<script>
(function () {
  var hero = document.querySelector('.hero-parallax');
  if (!hero) return;
  var box = hero.parentElement;
  box.addEventListener('mousemove', function (e) {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var r = box.getBoundingClientRect();
    var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
    hero.style.transform = 'scale(1.06) translate(' + (x * -14) + 'px, ' + (y * -10) + 'px)';
  });
  box.addEventListener('mouseleave', function () { hero.style.transform = 'scale(1.06)'; });
})();
</script>"""

AGENCY_LD = {
    "@context": "https://schema.org", "@type": "TravelAgency", "@id": SITE + "/#agency",
    "name": "ציוני דרך", "slogan": "פשוט להגיע לצדיקים", "url": SITE + "/",
    "telephone": "+972-58-321-0148", "email": EMAIL, "areaServed": "ישראל",
    "founder": {"@type": "Person", "name": "שמעון אולמן"},
    "alternateName": ["ציוני דרך פשוט להגיע לצדיקים", "ציוני דרך שמעון אולמן", "שמעון אולמן סוכן נסיעות",
                      "ציוני דרך סוכנות נסיעות", "ציוני דרך נסיעות לקברי צדיקים"],
    "address": {"@type": "PostalAddress", "addressCountry": "IL"},
    "sameAs": [GOOGLE_REVIEW],
    "knowsAbout": ["נסיעות מאורגנות לקברי צדיקים", "טיסות לקברי צדיקים", "נסיעה לאומן",
                   "נסיעה לליז'ענסק", "נסיעה לקרעסטיר", "קברי צדיקים באירופה"],
}


def abs_url(path):
    return SITE + ("/" if path == "/" else quote(path))


def render(page, body):
    url = abs_url(page["path"])
    t, d = escape(page["title"]), escape(page["description"])
    robots = '<meta name="robots" content="noindex">\n' if page.get("noindex") else ""
    canonical = "" if page.get("noindex") else f'<link rel="canonical" href="{url}">\n'
    ld = ""
    if page["name"] == "home":
        ld = ('<script type="application/ld+json">' + json.dumps(AGENCY_LD, ensure_ascii=False) + "</script>\n")
    preload = '<link rel="preload" as="image" href="/assets/banner-hero.webp">\n' if "banner-hero" in body else ""
    scripts = MENU_JS + ("\n" + PARALLAX_JS if "hero-parallax" in body else "")
    return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<meta name="google-site-verification" content="7ME-5ucrADBLRziH-3HPLdJvumnlnYWjXZVPeO7KJRw">
{robots}<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="he_IL">
<meta property="og:site_name" content="ציוני דרך">
<meta property="og:image" content="{OG_IMAGE}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{OG_IMAGE}">
{canonical}{ld}<link rel="icon" type="image/png" href="/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{preload}<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700;800&amp;display=swap">
<link rel="stylesheet" href="/assets/styles.css">
<link rel="stylesheet" href="/assets/layout.css">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
{header(page["path"])}
<main class="min-h-screen bg-background text-foreground">
{body}
</main>
{footer()}
{WA_FLOAT}
{scripts}
</body>
</html>
"""


def build():
    for page in PAGES:
        body = open(os.path.join(SRC, page["name"] + ".html"), encoding="utf-8").read()
        body = (body.replace("{{DESTINATIONS_ALL}}", destinations_all())
                    .replace("{{DESTINATIONS_POPULAR}}", destinations_popular())
                    .replace("{{PHONE}}", PHONE)
                    .replace("{{EMAIL}}", EMAIL)
                    .replace("{{GOOGLE_REVIEW}}", GOOGLE_REVIEW)
                    .replace("{{WA}}", escape(wa_link()))
                    .replace("{{WA_SVG}}", WA_SVG))
        for name, paths in ICONS.items():
            body = body.replace("{{ICON_" + name.upper() + "}}", icon(paths))
        out = page.get("out") or page["path"].strip("/") + "/index.html"
        path = os.path.join(ROOT, out)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(render(page, body))
        print("built", out)

    urls = [abs_url(p["path"]) for p in PAGES if not p.get("noindex")]
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        f.writelines(f"<url><loc>{u}</loc></url>\n" for u in urls)
        f.write("</urlset>\n")
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    build()
