#!/usr/bin/env python3
"""Assembles the galinstan.ai public directory.

Run:  python3 build.py            (writes public/, reports what blocks publication)
      python3 build.py --check    (fails if public/ differs from what this would write)

Two rules this file exists to enforce.

**It deploys an allowlist, not the checkout.** `public/` is assembled here, file by file,
and the deploy publishes `public/` and nothing else. The practice published its whole
repository once, build script and internal docs included
(`50_Claude_Outputs/METHOD_FROM_JJ.md` section 5).

**Nothing on the page is fetched at page load.** No font CDN, no analytics script tag, no
stylesheet link, no image host. The CSS is inlined; the markup carries no external
reference at all. On this site that is a performance choice. In the product it is the only
claim that cannot be recovered once broken, so the habit is the same in both repositories
and `tools/guards.py` fails the build over it.
"""

import argparse
import filecmp
import html
import json
import pathlib
import re
import shutil
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import page_copy  # noqa: E402

PUBLIC = ROOT / "public"
SITE_URL = "https://galinstan.ai"

# Cloudflare Web Analytics, chosen 2026-09-21: free, cookieless, no consent banner, six
# months of history, no custom events.
#
# **It is not a script tag in this file, and that is the point to understand.** Cloudflare
# injects its beacon at the edge, into the response, after this build has produced the
# HTML. So `public/index.html` contains no reference to it, and the build-time guard that
# forbids external references cannot see it — a guard that passes here says nothing about
# what a visitor is actually served.
#
# The resolution is in tools/guards.py: one named beacon is permitted on marketing paths,
# and the deploy verifies the *live* response rather than the artifact. See
# docs/ANALYTICS.md for why the rule is scoped to the path rather than waived.
ANALYTICS = "cloudflare-web-analytics (edge-injected; verified against the live response)"

CSS = """\
:root {
  --ink: #101418;
  --ink-soft: #3d474f;
  --rule: #d5dade;
  --paper: #fbfbfa;
  --panel: #eef0f1;
  --flag: #8a3a12;
  --measure: 34rem;
  --wide: 64rem;
  --sans: ui-sans-serif, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; scroll-padding-top: 6rem; }
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font: 400 1.0625rem/1.65 ui-serif, Georgia, "Times New Roman", serif;
}
main { max-width: var(--wide); margin: 0 auto; padding: 3rem 1.5rem 4rem; }
.prose, footer { max-width: var(--measure); }
.bar {
  position: sticky; top: 0; z-index: 10;
  background: color-mix(in srgb, var(--paper) 90%, transparent);
  -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--rule);
  view-transition-name: bar;
}
.bar-in {
  max-width: var(--wide); margin: 0 auto; padding: 0.875rem 1.5rem;
  display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 0.5rem 2rem;
}
.wordmark {
  font-family: var(--sans);
  font-size: 0.9375rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin: 0;
}
main > .wordmark { margin: 0 0 2.5rem; }
.wordmark a { text-decoration: none; }
nav {
  font-family: var(--sans);
  font-size: 0.875rem;
  display: flex; flex-wrap: wrap; gap: 0.25rem 1.25rem;
}
nav a { color: var(--ink-soft); text-decoration: none; }
nav a:hover { color: var(--ink); text-decoration: underline; }
nav a[aria-current="page"] { color: var(--ink); font-weight: 600; }
.pill {
  font-family: var(--sans); font-size: 0.8125rem; font-weight: 600; letter-spacing: 0.02em;
  display: inline-flex; align-items: center; gap: 0.5rem;
  padding: 0.5rem 1rem; border-radius: 999px;
  background: var(--ink); color: var(--paper); text-decoration: none;
  transition: transform 0.2s ease;
}
.pill::before { content: ""; width: 0.375rem; height: 0.375rem; border-radius: 50%; background: currentColor; }
.pill:hover { transform: translateY(-1px); }
@media (max-width: 44rem) {
  .bar-in { grid-template-columns: 1fr auto; }
  .bar nav { grid-column: 1 / -1; grid-row: 2; }
}
h1 {
  font-family: var(--sans);
  font-size: clamp(1.875rem, 1.1rem + 3.4vw, 3.5rem);
  font-weight: 500;
  letter-spacing: -0.02em;
  line-height: 1.1;
  max-width: 22ch;
  margin: 1rem 0 2.5rem;
  text-wrap: balance;
}
p { margin: 0 0 1.25rem; color: var(--ink-soft); }
footer {
  margin-top: 3.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--rule);
  font-family: var(--sans);
  font-size: 0.8125rem;
  line-height: 1.6;
  color: var(--ink-soft);
}
footer p { margin: 0 0 0.375rem; color: inherit; }
.sub { color: var(--ink); font-size: 1.125rem; }
.cta { margin-top: 2rem; }
strong { color: var(--ink); font-weight: 600; }
a { color: inherit; text-underline-offset: 2px; }
a:focus-visible { outline: 2px solid var(--ink); outline-offset: 3px; }
.ticks {
  height: 11px; margin: 3rem 0;
  --x: linear-gradient(var(--ink-soft), var(--ink-soft));
  background:
    var(--x) 5px 0 / 1px 11px no-repeat, var(--x) 0 5px / 11px 1px no-repeat,
    var(--x) 50% 0 / 1px 11px no-repeat, var(--x) 50% 5px / 11px 1px no-repeat,
    var(--x) calc(100% - 5px) 0 / 1px 11px no-repeat, var(--x) 100% 5px / 11px 1px no-repeat,
    linear-gradient(var(--rule), var(--rule)) 0 5px / 100% 1px no-repeat;
}
.art {
  margin: 0 0 3rem; border-radius: 1.25rem; overflow: hidden;
  background: var(--panel);
  aspect-ratio: 16 / 7;
}
.art img { display: block; width: 100%; height: 100%; object-fit: cover; object-position: 62% 55%; }
@media (max-width: 44rem) { .art { aspect-ratio: 4 / 3; } .card { min-height: 5.5rem; } }
.cards {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr)); gap: 1rem;
  margin: 0 0 1rem;
}
.card {
  position: relative; display: flex; align-items: flex-end;
  min-height: 9rem; padding: 1.25rem; border-radius: 1rem;
  background: var(--panel); color: var(--ink); text-decoration: none;
  font-family: var(--sans); font-size: 1.25rem; font-weight: 500; letter-spacing: -0.01em;
  transition: background-color 0.2s ease, transform 0.2s ease;
}
.card::after {
  content: ""; position: absolute; top: 1.25rem; right: 1.25rem;
  width: 0.625rem; height: 0.625rem;
  border-top: 1.5px solid currentColor; border-right: 1.5px solid currentColor;
  background: linear-gradient(to bottom right, transparent calc(50% - 0.75px), currentColor 0 calc(50% + 0.75px), transparent 0);
  transition: transform 0.2s ease;
}
.card:hover { background: var(--rule); }
.card:hover::after { transform: translate(2px, -2px); }
.brief {
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
  margin: 1rem 0 0; padding: 2rem 1.5rem; border-radius: 1.25rem;
  background: var(--ink); color: var(--paper); text-decoration: none;
  font-family: var(--sans); font-size: clamp(1.125rem, 0.9rem + 1vw, 1.5rem); font-weight: 500;
}
.brief::after {
  content: ""; flex: none; width: 3rem; height: 3rem; border-radius: 50%;
  background:
    linear-gradient(var(--ink), var(--ink)) 50% 55% / 1.5px 1rem no-repeat,
    linear-gradient(45deg, transparent 45%, var(--ink) 45% 55%, transparent 55%) 38% 62% / 0.6rem 0.6rem no-repeat,
    linear-gradient(-45deg, transparent 45%, var(--ink) 45% 55%, transparent 55%) 62% 62% / 0.6rem 0.6rem no-repeat,
    var(--paper);
  transition: transform 0.2s ease;
}
.brief:hover::after { transform: translateY(2px); }
.todo {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.8125rem;
  color: var(--flag);
  background: #fdf2ec;
  border: 1px dashed var(--flag);
  border-radius: 2px;
  padding: 0.0625rem 0.375rem;
}
@view-transition { navigation: auto; }
@media (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: view()) {
    .reveal {
      animation: rise linear both;
      animation-timeline: view();
      animation-range: entry 0% entry 35%;
    }
    @keyframes rise { from { opacity: 0; transform: translateY(1.25rem); } }
  }
}
@media (prefers-color-scheme: dark) {
  :root {
    --ink: #eef1f3; --ink-soft: #b3bcc3; --rule: #2b3238;
    --paper: #0f1216; --panel: #181d22; --flag: #e8a87c;
  }
  .todo { background: #24170f; }
  .art img { filter: brightness(0.86); }
}
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
  @view-transition { navigation: none; }
}
"""


def _markup(raw: str) -> str:
    """Escapes a copy string, then re-marks the placeholder tokens so they are visible.

    A `**lead-in**` in an approved string renders bold. That is the only markup the
    register carries, and it is carried because the approved text carries it.
    """
    escaped = html.escape(raw, quote=False)
    if escaped.startswith("[[TODO:"):
        return f'<span class="todo">{escaped}</span>'
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)


def _contact_link() -> str:
    """The contact address as a mail link, with the approved subject pre-filled.

    A `mailto:` opens the visitor's own mail client. It fetches nothing and reaches no
    third party, so it does not touch the no-external-references rule. The pre-filled
    subject is the whole of the site's source attribution at stage 1: every enquiry
    arrives labelled, with no form, no CRM and nothing to pay for.

    The footer's "banneker.net" stays plain text rather than becoming a link. The approved
    string does not mark it as one, and a session inventing a link out of an approved
    string is the thing the register exists to stop.
    """
    return _mail_link("contact")


def mail_href(line_id: str) -> str:
    """The `mailto:` for a mail-bearing string, with its approved subject. One place, so
    the build, the build-time guard and the live verifier cannot disagree about it."""
    item = page_copy.line(line_id)
    subject = urllib.parse.quote(item.mail_subject)
    return f"mailto:{item.text}?subject={subject}"


def _mail_link(target_id: str, label_id: str | None = None) -> str:
    label = page_copy.text(label_id or target_id)
    return f'<a href="{html.escape(mail_href(target_id))}">{_markup(label)}</a>'


# The stage 2 pages, in nav order. The address is the file's name without `.html`, which
# is how the host serves it; `SITEMAP` below is what declares it.
PAGES = {
    "/intraday-liquidity": ("il", "nav-1"),
    "/audit-evidence": ("ae", "nav-2"),
    "/deployment": ("dep", "nav-3"),
}


def _nav(current: str | None) -> str:
    links = []
    for path, (_, nav_id) in PAGES.items():
        mark = ' aria-current="page"' if path == current else ""
        links.append(f'<a href="{path}"{mark}>{_markup(page_copy.text(nav_id))}</a>')
    return "        <nav>\n          " + "\n          ".join(links) + "\n        </nav>"


def _bar(current: str | None, link: bool = True) -> str:
    """The header that stays at the top while the page scrolls: wordmark, nav, and the demo
    request, so the one thing a visitor can do is never further than the top of the screen.
    Every word in it is already approved: the wordmark, the three nav labels, `cta-demo`."""
    mark = _markup(page_copy.text("wordmark"))
    mark = f'<a href="/">{mark}</a>' if link else mark
    demo = html.escape(mail_href("cta-demo-target"))
    return f"""    <header class="bar">
      <div class="bar-in">
        <p class="wordmark">{mark}</p>
{_nav(current)}
        <a class="pill" href="{demo}">{_markup(page_copy.text("cta-demo"))}</a>
      </div>
    </header>"""


# Section divider: a hairline with a cross at each end and the middle, like the marks on a
# drawing. Drawn by the stylesheet, so it carries no text and fetches nothing.
TICKS = '      <div class="ticks" aria-hidden="true"></div>\n'


def _cards() -> str:
    """The three stage 2 pages as cards on the home page. Titles only: they are the nav
    labels, and a line of description under each would be new copy."""
    t = page_copy.text
    cards = "\n".join(
        f'        <a class="card reveal" href="{path}">{_markup(t(nav_id))}</a>'
        for path, (_, nav_id) in PAGES.items()
    )
    return f'      <div class="cards">\n{cards}\n      </div>\n'


# The hero photograph, served from this site rather than an image host: it is two files in
# the allowlist, like the brief, so it adds no third party. Two widths so a phone does not
# download the desktop one. `alt=""` marks it decorative: a description a screen reader
# reads aloud is copy, and none has been approved, so it says nothing rather than
# something unapproved. Width and height are set so the page does not jump as it loads.
HERO = ("hero-800.jpg", "hero-1408.jpg")
HERO_IMG = """\
      <figure class="art">
        <img src="/hero-1408.jpg" srcset="/hero-800.jpg 800w, /hero-1408.jpg 1408w" sizes="(max-width: 67rem) 100vw, 64rem" width="1408" height="768" alt="" fetchpriority="high">
      </figure>
"""


def _footer() -> str:
    t = page_copy.text
    return f"""      <footer>
        <p>{_markup(t("foot-claim"))}</p>
        <p>{_markup(t("entity"))}</p>
        <p>{_contact_link()}</p>
        <p><a href="/privacy">Privacy</a></p>
        <p>{_markup(t("legal-footer"))}</p>
      </footer>"""


def render_structured_data() -> str:
    """JSON-LD saying what Galinstan is and who publishes it, for search and AI answers.

    "Galinstan" is also a gallium alloy, and a model asked about the name answers about the
    metal. This tells a crawler that galinstan.ai is software, published by Banneker.
    Approved by Antwain on 2026-09-25. Every value a reader could see is a register string;
    the rest is schema.org vocabulary and our own and the publisher's addresses, which
    `tools/guards.py` permits inside this block and nowhere else.
    """
    t = page_copy.text
    data = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": t("wordmark"),
        "url": f"{SITE_URL}/",
        "description": t("meta-description"),
        "applicationCategory": "BusinessApplication",
        "publisher": {"@type": "Organization", "name": t("ld-publisher"), "url": "https://banneker.net"},
    }
    body = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'\n    <script type="application/ld+json">{body}</script>'


def _head(title: str, canonical: str, description: str | None = None, robots: str = "index, follow", extra: str = "") -> str:
    desc = f'\n    <meta name="description" content="{html.escape(description, quote=True)}">' if description else ""
    canon = f'\n    <link rel="canonical" href="{SITE_URL}{canonical}">' if canonical else ""
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)}</title>{desc}{canon}
    <meta name="robots" content="{robots}">{extra}
    <style>
{CSS}    </style>
  </head>"""


def render_stage_2(path: str) -> str:
    prefix, _ = PAGES[path]
    t = page_copy.text
    bodies = [i.id for i in page_copy.LINES if re.fullmatch(rf"{prefix}-body-\d+", i.id)]
    body = "\n".join(f"      <p>{_markup(t(k))}</p>" for k in bodies)
    return f"""{_head(t(f"{prefix}-meta-title"), path, t(f"{prefix}-meta-description"))}
  <body>
{_bar(path)}
    <main>
      <h1>{_markup(t(f"{prefix}-h1"))}</h1>
      <div class="prose">
      <p class="sub">{_markup(t(f"{prefix}-sub"))}</p>
{body}
      </div>
      <div class="prose">
      <p class="cta">{_mail_link("cta-demo-target", f"{prefix}-cta")}</p>
      </div>
{_brief_link(path)}{_footer()}
    </main>
  </body>
</html>
"""


def render_index() -> str:
    t = page_copy.text
    body = "\n".join(
        f"      <p>{_markup(t(k))}</p>" for k in ("body-1", "body-2", "body-3")
    )
    return f"""{_head(t("meta-title"), "/", t("meta-description"), extra=render_structured_data())}
  <body>
{_bar(None, link=False)}
    <main>
      <h1>{_markup(t("headline"))}</h1>
{HERO_IMG}      <div class="prose">
{body}
      <p class="cta">{_mail_link("cta-demo-target", "cta-demo")}</p>
      </div>
{TICKS}{_cards()}{_brief_link("/")}{_footer()}
    </main>
  </body>
</html>
"""


def render_privacy() -> str:
    t = page_copy.text
    return f"""{_head(t("privacy-meta-title"), "/privacy")}
  <body>
{_bar(None)}
    <main>
      <h1>{_markup(t("privacy-meta-title"))}</h1>
      <div class="prose">
      <p>{_markup(t("privacy-controller"))}</p>
      <p>{_markup(t("privacy-analytics"))}</p>
      <p>{_markup(t("privacy-contact-label"))} {_contact_link()}</p>
      </div>
      <footer>
        <p>{_markup(t("entity"))}</p>
        <p>{_markup(t("legal-footer"))}</p>
      </footer>
    </main>
  </body>
</html>
"""


def render_404() -> str:
    t = page_copy.text
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(t("notfound-meta-title"))}</title>
    <meta name="robots" content="noindex">
    <style>
{CSS}    </style>
  </head>
  <body>
    <main>
      <p class="wordmark">{_markup(t("wordmark"))}</p>
      <h1>{_markup(t("notfound-h1"))}</h1>
      <p><a href="/">{_markup(t("notfound-link"))}</a></p>
    </main>
  </body>
</html>
"""


# The product brief, the public paper, served at /galinstan-brief.pdf.
#
# **The PDF is committed, not built here**, because this build has no dependencies and a
# typeset PDF needs a browser engine. So the build renders the paper's *source*, an HTML
# page made only of strings from the copy register, and `tools/make_brief.py` prints
# that source to `assets/galinstan-brief.pdf` with a local Chrome and records both hashes in
# `assets/galinstan-brief.lock.json`. The guard `brief_matches_its_source` fails the build
# if the register, this template or the PDF changes without the other two: a paper that
# ships is always the one its approved strings describe.
#
# No URL in it but the contact mail link, no author field, no NDA offer (Antwain,
# 2026-09-25: the technical detail is not offered without a direct conversation first).
ASSETS = ROOT / "assets"
BRIEF_PDF = ASSETS / "galinstan-brief.pdf"
BRIEF_LOCK = ASSETS / "galinstan-brief.lock.json"
BRIEF_PATH = "/galinstan-brief.pdf"
BRIEF_LINKED_FROM = ("/", "/audit-evidence", "/deployment")

BRIEF_CSS = """\
@page {
  size: A4;
  margin: 24mm 22mm 24mm 22mm;
  @bottom-left { content: "Galinstan"; font: 400 8pt Charter, serif; letter-spacing: 0.14em; color: #6b747b; }
  @bottom-right { content: counter(page); font: 400 8pt Charter, serif; color: #6b747b; }
}
@page :first { @bottom-left { content: none; } @bottom-right { content: none; } }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; color: #101418; font: 400 10.5pt/1.55 Charter, Georgia, serif; }
.wordmark { font-size: 9pt; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; margin: 0 0 30mm; }
h1 { font-size: 28pt; font-weight: 400; line-height: 1.15; margin: 0 0 6mm; }
.sub { font-size: 13.5pt; line-height: 1.45; color: #3d474f; max-width: 130mm; margin: 0 0 12mm; }
.edition { font-size: 9pt; color: #6b747b; border-top: 0.5pt solid #b8c0c6; padding-top: 3mm; margin: 0 0 14mm; }
h2 { font-size: 15pt; font-weight: 700; margin: 9mm 0 3mm; break-after: avoid; }
h3 { font-size: 11pt; font-weight: 700; margin: 6mm 0 1.5mm; break-after: avoid; }
p { margin: 0 0 3mm; orphans: 3; widows: 3; }
ul { margin: 0 0 3.5mm; padding-left: 5mm; }
li { margin: 0 0 1.8mm; }
ol.sources { font-size: 9pt; line-height: 1.45; padding-left: 6mm; color: #3d474f; }
strong { font-weight: 700; }
a { color: inherit; }
.close { margin-top: 10mm; padding-top: 3mm; border-top: 0.5pt solid #b8c0c6; font-size: 9.5pt; }
.close p { margin: 0 0 1.5mm; }
.cover { break-after: page; }
"""

_BRIEF_BODY = re.compile(r"brief-(h|h3|p|li|ref)-.+")


def render_brief_source() -> str:
    """The paper as HTML, every visible word from the register, in the register's order.

    The cover carries the summary, so it reads as a one-page brief on its own; the rest
    follows on the pages after it.
    """
    t = page_copy.text
    items = [(m.group(1), i.id) for i in page_copy.LINES if (m := _BRIEF_BODY.fullmatch(i.id))]
    out: list[str] = []
    open_list = ""
    for kind, line_id in items:
        wanted = {"li": "ul", "ref": "ol"}.get(kind, "")
        if open_list and open_list != wanted:
            out.append(f"      </{open_list}>")
            open_list = ""
        if kind == "h":
            if line_id == "brief-h-problem":  # the cover ends with the summary
                out.append("    </section>\n    <section>")
            out.append(f"      <h2>{_markup(t(line_id))}</h2>")
        elif kind == "h3":
            out.append(f"      <h3>{_markup(t(line_id))}</h3>")
        elif kind == "p":
            out.append(f"      <p>{_markup(t(line_id))}</p>")
        else:
            if not open_list:
                cls = ' class="sources"' if wanted == "ol" else ""
                out.append(f"      <{wanted}{cls}>")
                open_list = wanted
            out.append(f"        <li>{_markup(t(line_id))}</li>")
    if open_list:
        out.append(f"      </{open_list}>")
    body = "\n".join(out)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{html.escape(t("brief-meta-title"))}</title>
    <style>
{BRIEF_CSS}    </style>
  </head>
  <body>
    <section class="cover">
      <p class="wordmark">{_markup(t("wordmark"))}</p>
      <h1>{_markup(t("brief-title"))}</h1>
      <p class="sub">{_markup(t("brief-sub"))}</p>
      <p class="edition">{_markup(t("brief-edition"))}</p>
{body}
      <div class="close">
        <p>{_markup(t("brief-contact-label"))} {_mail_link("brief-contact")}</p>
        <p>{_markup(t("entity"))}</p>
        <p>{_markup(t("legal-footer"))}</p>
      </div>
    </section>
  </body>
</html>
"""


def _brief_link(path: str) -> str:
    if path not in BRIEF_LINKED_FROM:
        return ""
    return f'      <a class="brief reveal" href="{BRIEF_PATH}">{_markup(page_copy.text("brief-link"))}</a>\n'


def render_brief_pdf() -> bytes:
    return BRIEF_PDF.read_bytes()


# The crawler policy, RULES.md r11, revised by Antwain on 2026-09-25: "AI crawlers: search,
# live AI answers and training are all allowed. The site carries no IP; the method is not
# published." It was option A in `50_Claude_Outputs/MARKETING_STRATEGY.md` §7a (present,
# not trained on) from 2026-09-21 until then.
#
# The signal is scoped to the group it sits in, so it goes inside `User-agent: *` rather
# than above it. Content signals are advisory, and the edge has to agree: Cloudflare's AI
# bot policy for the Training category is set to Allow with this release. The policy of
# record is still this committed file. Cloudflare's own managed robots.txt stays off
# precisely so there are not two places to read it from (SETUP_GITHUB_CLOUDFLARE.md Part 3).
CONTENT_SIGNAL = "Content-Signal: search=yes, ai-input=yes, ai-train=yes"


def render_robots() -> str:
    # Owned from the first release rather than left to the host's default. The practice
    # shipped its own robots.txt at release 54 and regretted the gap.
    return (
        f"User-agent: *\n{CONTENT_SIGNAL}\nAllow: /\n"
        f"\nSitemap: {SITE_URL}/sitemap.xml\n"
    )


def _content_date(render) -> str | None:
    """The newest approval date among the strings a page actually renders.

    Collected by rendering the page with the copy accessor recording what it is asked
    for, rather than by keeping a second list of line ids beside the renderers. Two
    lists drift, and this one would drift silently: a sitemap is read by crawlers and
    by nobody else.

    None when the page renders no dated string, and then the entry carries no `lastmod`
    at all. The field is optional, and a crawler that is told nothing is better served
    than one that is told a date we made up.
    """
    seen: list[str] = []
    accessor = page_copy.text

    def recording(line_id: str) -> str:
        seen.append(line_id)
        return accessor(line_id)

    page_copy.text = recording
    try:
        render()
    finally:
        page_copy.text = accessor

    dates = [d for d in (page_copy.line(i).approved_on for i in seen) if d]
    return max(dates) if dates else None


# What each declared URL is built from. The sitemap dates an address by the copy served
# at it, so the two have to be named together.
# The addresses this site declares. Not the filenames it builds: Cloudflare Pages serves
# `privacy.html` at `/privacy` and permanently redirects the `.html` form to it, so the
# one URL the sitemap used to declare was the one URL that could not be indexed, and the
# page that was indexed had never been declared. Canonicals and internal links are checked
# against this map by `tools/guards.py`, so the three cannot drift apart again.
SITEMAP = {
    "/": lambda: render_index(),
    **{path: (lambda p=path: render_stage_2(p)) for path in PAGES},
    "/privacy": lambda: render_privacy(),
    BRIEF_PATH: lambda: render_brief_source(),
}


def render_sitemap() -> str:
    # `lastmod` used to be `date.today()`, which made every release claim every page had
    # changed — and made the committed build go stale at midnight UTC without a single
    # edit, so CI failed a pull request that had touched nothing on the page. It is the
    # only field in this file still weighed by a crawler, and the way to lose that weight
    # is to make it always true. The copy register already records the date each string
    # was approved, which is a real content date sitting one function away.
    urls = ""
    for path in SITEMAP:
        lastmod = _content_date(SITEMAP[path])
        stamp = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
        urls += f"  <url><loc>{SITE_URL}{path}</loc>{stamp}</url>\n"
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}</urlset>\n"
    )


# The allowlist. A file reaches galinstan.ai if and only if it is named here.
ALLOWLIST = {
    "index.html": render_index,
    **{f"{path[1:]}.html": (lambda p=path: render_stage_2(p)) for path in PAGES},
    "privacy.html": render_privacy,
    "404.html": render_404,
    "robots.txt": render_robots,
    "sitemap.xml": render_sitemap,
    "galinstan-brief.pdf": render_brief_pdf,
    **{name: (lambda n=name: (ASSETS / n).read_bytes()) for name in HERO},
}


def build(target: pathlib.Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for name, render in ALLOWLIST.items():
        content = render()
        if isinstance(content, bytes):
            (target / name).write_bytes(content)
        else:
            (target / name).write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the committed public/ differs from a fresh build",
    )
    args = parser.parse_args()

    if args.check:
        scratch = ROOT / ".build-check"
        build(scratch)
        match, mismatch, errors = filecmp.cmpfiles(
            scratch, PUBLIC, list(ALLOWLIST), shallow=False
        )
        stray = sorted(p.name for p in PUBLIC.iterdir()) if PUBLIC.exists() else []
        unexpected = [n for n in stray if n not in ALLOWLIST]
        shutil.rmtree(scratch)
        problems = sorted(mismatch + errors)
        if problems or unexpected:
            if problems:
                print(f"public/ is stale or missing: {', '.join(problems)}", file=sys.stderr)
            if unexpected:
                print(
                    f"public/ holds files the allowlist does not name: {', '.join(unexpected)}",
                    file=sys.stderr,
                )
            print("Run python3 build.py, commit the result, and push.", file=sys.stderr)
            return 1
        print(f"public/ is current ({len(match)} files).")
        return 0

    build(PUBLIC)
    print(f"Built {len(ALLOWLIST)} files into {PUBLIC}")

    blockers = page_copy.blockers()
    if blockers:
        print(f"\nNot publishable. {len(blockers)} strings are not approved:")
        for item in blockers:
            print(f"  {item.status:<11} {item.id}")
        print("\nA preview deploy is fine. A production release is not, and is blocked.")
    else:
        print("\nEvery string is approved. Publishable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
