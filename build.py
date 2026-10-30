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
import base64
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
@font-face {
  font-family: "Source Serif 4"; font-weight: 600; font-style: normal; font-display: swap;
  src: url("/source-serif-4-600.woff2") format("woff2");
}
@font-face {
  font-family: "IBM Plex Mono"; font-weight: 400; font-style: normal; font-display: swap;
  src: url("/ibm-plex-mono-400.woff2") format("woff2");
}
:root {
  color-scheme: light;
  --paper: #f6f4ee;
  --card: #fffdf8;
  --hair: #e2dbc9;
  --hair2: #ece7d8;
  --ink: #1e1a13;
  --muted: #7c7361;
  --teal: #0e7c6b;
  --teal2: #0a5a4e;
  --risk: #b3402e;
  --measure: 34rem;
  --wide: 64rem;
  --serif: "Source Serif 4", Georgia, "Times New Roman", serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; background: var(--paper); }
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font: 400 1rem/1.65 Inter, system-ui, -apple-system, "Segoe UI", sans-serif;
  font-feature-settings: "tnum" 1;
  -webkit-font-smoothing: antialiased;
}
main { max-width: var(--wide); margin: 0 auto; padding: 3rem 1.5rem 4rem; }
.prose, footer { max-width: var(--measure); }
.bar {
  border-top: 4px solid var(--ink);
  border-bottom: 1px solid var(--hair);
  view-transition-name: bar;
}
.bar-in {
  max-width: var(--wide); margin: 0 auto; padding: 1rem 1.5rem 0;
  display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 0 2rem;
}
.wordmark {
  display: flex; align-items: center; gap: 0.75rem;
  font-family: var(--serif);
  font-size: 1.3125rem;
  font-weight: 600;
  margin: 0;
  padding-bottom: 1rem;
}
.wordmark::before {
  content: "G" / "";
  flex: none; display: flex; align-items: center; justify-content: center;
  width: 2.125rem; height: 2.125rem; border: 1.5px solid var(--ink); border-radius: 50%;
  font-size: 1.125rem; color: var(--teal2);
}
.wordmark .wm { white-space: nowrap; }
.wordmark .wm span { color: var(--teal2); }
main > .wordmark { margin: 0 0 2.5rem; }
.wordmark a { text-decoration: none; }
nav {
  font-size: 0.84375rem; font-weight: 500;
  display: flex; flex-wrap: wrap; gap: 0 1.75rem;
  align-self: stretch; align-items: flex-end;
}
nav a {
  color: var(--muted); text-decoration: none;
  padding: 0.8125rem 0.125rem; margin-bottom: -1px; border-bottom: 2px solid transparent;
}
nav a:hover { color: var(--ink); }
nav a[aria-current="page"] { color: var(--ink); font-weight: 600; border-bottom-color: var(--teal2); }
.pill {
  font-size: 0.875rem; font-weight: 600;
  display: inline-block; margin-bottom: 1rem;
  padding: 0.5rem 1.125rem; border-radius: 8px;
  border: 1.5px solid var(--teal2); color: var(--teal2); text-decoration: none;
  transition: background-color 0.2s ease;
}
.pill:hover { background: var(--card); }
.mid { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 0 1.75rem; align-self: stretch; }
.change { align-self: center; padding-bottom: 1rem; font-size: 0.8125rem; color: var(--muted); text-decoration: none; white-space: nowrap; }
.change:hover { color: var(--ink); }
@media (max-width: 44rem) {
  .bar-in { grid-template-columns: 1fr auto; column-gap: 0.75rem; }
  .bar .mid { grid-column: 1 / -1; grid-row: 2; gap: 0 1.125rem; }
  .bar nav { gap: 0 1.125rem; font-size: 0.8125rem; }
  .bar .wordmark { font-size: 1rem; gap: 0.5rem; }
  .bar .wordmark::before { width: 1.75rem; height: 1.75rem; font-size: 0.9375rem; }
  .pill { padding: 0.4375rem 0.75rem; font-size: 0.8125rem; }
}
h1 {
  font-family: var(--serif);
  font-size: clamp(1.875rem, 1.1rem + 3.2vw, 3.25rem);
  font-weight: 600;
  letter-spacing: -0.01em;
  line-height: 1.12;
  max-width: 22ch;
  margin: 1rem 0 2.5rem;
  text-wrap: balance;
}
p { margin: 0 0 1.25rem; color: var(--ink); }
h2 {
  font-family: var(--serif); font-size: 1.375rem; font-weight: 600;
  color: var(--ink); margin: 2.5rem 0 1rem;
}
.roles { list-style: none; margin: 0 0 2.5rem; padding: 0; }
.roles li { margin: 0; padding: 0.875rem 0; border-top: 1px solid var(--hair); color: var(--ink); }
.roles li:last-child { border-bottom: 1px solid var(--hair); }
.roles a { font-family: var(--mono); font-size: 0.78125rem; color: var(--teal2); white-space: nowrap; }
footer {
  margin-top: 3.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--hair);
  font-size: 0.8125rem;
  line-height: 1.6;
  color: var(--muted);
}
footer p { margin: 0 0 0.375rem; color: inherit; }
.sub { color: var(--ink); font-size: 1.125rem; }
.cta { margin-top: 2rem; }
.cta a { font-weight: 600; color: var(--teal2); text-decoration: none; border-bottom: 1px solid var(--teal2); }
strong { color: var(--ink); font-weight: 600; }
a { color: inherit; text-underline-offset: 2px; }
a:focus-visible { outline: 2px solid var(--teal2); outline-offset: 3px; }
.ticks {
  height: 11px; margin: 3rem 0;
  --x: linear-gradient(var(--muted), var(--muted));
  background:
    var(--x) 5px 0 / 1px 11px no-repeat, var(--x) 0 5px / 11px 1px no-repeat,
    var(--x) 50% 0 / 1px 11px no-repeat, var(--x) 50% 5px / 11px 1px no-repeat,
    var(--x) calc(100% - 5px) 0 / 1px 11px no-repeat, var(--x) 100% 5px / 11px 1px no-repeat,
    linear-gradient(var(--hair), var(--hair)) 0 5px / 100% 1px no-repeat;
}
.art {
  margin: 0 0 3rem; border-radius: 8px; overflow: hidden;
  background: var(--card); border: 1px solid var(--hair);
  aspect-ratio: 16 / 7;
}
.art img { display: block; width: 100%; height: 100%; object-fit: cover; object-position: 100% 50%; }
@media (max-width: 44rem) { .art { aspect-ratio: 4 / 3; } .card { min-height: 5.5rem; } }
.cards {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr)); gap: 1rem;
  margin: 0 0 1rem;
}
.card {
  position: relative; display: flex; align-items: flex-end;
  min-height: 9rem; padding: 1.25rem; border-radius: 8px;
  background: var(--card); border: 1px solid var(--hair); color: var(--ink); text-decoration: none;
  font-family: var(--serif); font-size: 1.25rem; font-weight: 600;
  transition: border-color 0.2s ease, transform 0.2s ease;
}
.card::after {
  content: ""; position: absolute; top: 1.25rem; right: 1.25rem;
  width: 0.625rem; height: 0.625rem; color: var(--teal2);
  border-top: 1.5px solid currentColor; border-right: 1.5px solid currentColor;
  background: linear-gradient(to bottom right, transparent calc(50% - 0.75px), currentColor 0 calc(50% + 0.75px), transparent 0);
  transition: transform 0.2s ease;
}
.card:hover { border-color: var(--teal2); }
.card:hover::after { transform: translate(2px, -2px); }
.brief {
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
  margin: 1rem 0 0; padding: 1.75rem 1.5rem; border-radius: 8px;
  background: var(--card); border: 1px solid var(--hair); color: var(--ink); text-decoration: none;
  font-family: var(--serif); font-size: clamp(1.125rem, 0.9rem + 1vw, 1.5rem); font-weight: 600;
  transition: border-color 0.2s ease;
}
.brief:hover { border-color: var(--teal2); }
.brief::after {
  content: ""; flex: none; width: 3rem; height: 3rem; border-radius: 50%;
  background:
    linear-gradient(var(--card), var(--card)) 50% 55% / 1.5px 1rem no-repeat,
    linear-gradient(45deg, transparent 45%, var(--card) 45% 55%, transparent 55%) 38% 62% / 0.6rem 0.6rem no-repeat,
    linear-gradient(-45deg, transparent 45%, var(--card) 45% 55%, transparent 55%) 62% 62% / 0.6rem 0.6rem no-repeat,
    var(--teal2);
  transition: transform 0.2s ease;
}
.brief:hover::after { transform: translateY(2px); }
.todo {
  font-family: var(--mono);
  font-size: 0.8125rem;
  color: var(--risk);
  background: var(--card);
  border: 1px dashed var(--risk);
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


def _mail_link(target_id: str, label_id: str | None = None, attrs: str = "") -> str:
    label = page_copy.text(label_id or target_id)
    return f'<a href="{html.escape(mail_href(target_id))}"{attrs}>{_markup(label)}</a>'


# The stage 2 pages, in nav order. The address is the file's name without `.html`, which
# is how the host serves it; `SITEMAP` below is what declares it.
PAGES = {
    "/eu-banks/intraday-liquidity": ("il", "nav-1"),
    "/eu-banks/audit-evidence": ("ae", "nav-2"),
    "/eu-banks/deployment": ("dep", "nav-3"),
}


# Two funnels (Cowork's ask 202, 2026-10-30), each with its own landing, feature pages and deployment page, and each
# linking only to itself. Each US page names the lines it renders, in order; a line the EU page carries in the same
# words is the EU page's approved line, not a copy of it. Each idea appears on one page per funnel.
US_TRACK = "/us-banks"
EU_TRACK = "/eu-banks"
US_PAGES = {
    "/us-banks/intraday-liquidity": {
        "nav": "nav-1", "title": "us-il-meta-title", "description": "il-meta-description", "h1": "il-h1",
        "sub": "il-sub", "cta": "il-cta", "body": ("il-body-2", "us-il-body-5"),
    },
    "/us-banks/audit-evidence": {
        "nav": "nav-2", "title": "ae-meta-title", "description": "ae-meta-description", "h1": "ae-h1",
        "sub": "ae-sub", "cta": "ae-cta", "body": ("ae-body-2", "us-ae-body-3", "us-ae-body-4"),
    },
    "/us-banks/deployment": {
        "nav": "nav-3", "title": "us-dep-meta-title", "description": "us-dep-h1", "h1": "us-dep-h1", "cta": "dep-cta",
        "body": ("us-dep-where", "us-dep-reads", "dep-body-3", "us-dep-upgrades", "dep-body-5", "dep-body-6"),
    },
}
US_NAV = {path: spec["nav"] for path, spec in US_PAGES.items()}
EU_NAV = {path: nav_id for path, (_, nav_id) in PAGES.items()}

# The addresses the EU pages had until 2026-10-30. Pages serves a permanent redirect from each (`render_redirects`).
MOVED = {
    "/intraday-liquidity": "/eu-banks/intraday-liquidity",
    "/audit-evidence": "/eu-banks/audit-evidence",
    "/deployment": "/eu-banks/deployment",
}


def region_of(path: str | None) -> str | None:
    for region, track in (("us", US_TRACK), ("eu", EU_TRACK)):
        if path and (path == track or path.startswith(track + "/")):
            return region
    return None


# Asset labels for measurement (Spot's ask of 2026-10-30, `CODY_ASK_GOOGLE_ANALYTICS_LABELS`, revised by Cowork's ask
# 202): Cody names each measurable thing, Cowork's tag reads the names. They are inert attributes: nothing here sends or
# fetches anything, and a page without the tag behaves exactly as before. Each label belongs to a canonical address,
# never to a visitor. `docs/ANALYTICS_LABELS.md` is the table Cowork maps its tags to.
PAGE_LABELS = {
    "/us-banks": ("us-track", "us"),
    "/us-banks/intraday-liquidity": ("us-intraday-liquidity", "us"),
    "/us-banks/audit-evidence": ("us-audit-evidence", "us"),
    "/us-banks/deployment": ("us-deployment", "us"),
    "/eu-banks": ("eu-track", "eu"),
    "/eu-banks/intraday-liquidity": ("eu-intraday-liquidity", "eu"),
    "/eu-banks/audit-evidence": ("eu-audit-evidence", "eu"),
    "/eu-banks/deployment": ("eu-deployment", "eu"),
    "/privacy": ("privacy", "shared"),
}


def _body(path: str) -> str:
    asset, region = PAGE_LABELS[path]
    served = f' data-region-served="{region}"' if region in ("us", "eu") else ""
    return f'<body data-asset="{asset}" data-asset-region="{region}" data-page="{path}"{served}>'


def asset_attrs(asset: str, event: str, **params: str) -> str:
    """The attributes one measurable element carries: its label, the event the tag sends for it, and the event's
    parameters, each a fixed value from the page's address. `destination_track` becomes `data-destination-track`."""
    out = f' data-asset="{asset}" data-event="{event}"'
    for name, value in params.items():
        out += f' data-{name.replace("_", "-")}="{html.escape(value, quote=True)}"'
    return out


def _demo_attrs(path: str, where: str) -> str:
    return asset_attrs(f"demo-request-{where}", "demo_request_click", landing_page=path)


def _region_change(current: str | None) -> str:
    """The one cross-region element on a page: a small link to the other funnel's landing page. A plain link, so it
    works with scripts off; with them on, the click also stores the choice for the root (`REGION_SCRIPT`)."""
    here = region_of(current)
    if here is None:
        return ""
    there, track = ("eu", EU_TRACK) if here == "us" else ("us", US_TRACK)
    labels = asset_attrs(f"region-change-to-{there}", "region_switch", destination_track=there, source_page=current)
    return f'          <a class="change" href="{track}"{labels}>{_markup(page_copy.text(f"region-change-to-{there}"))}</a>'


# The visitor's own choice, and where the visit began. A click on the change link sets `region`, a first-party cookie
# holding `us` or `eu` and nothing else, which the edge reads at the root (`functions/index.js`). No click, no cookie.
# The first page of a visit records how it was reached, for the tag to read, and takes `region_source` out of the address.
REGION_SCRIPT = """    <script>
(function () {
  document.querySelectorAll('a[data-event="region_switch"]').forEach(function (a) {
    a.addEventListener("click", function () {
      document.cookie = "region=" + a.getAttribute("data-destination-track") + "; Path=/; Max-Age=31536000; SameSite=Lax; Secure";
    });
  });
  try {
    var query = new URLSearchParams(location.search), asked = query.get("region_source");
    if (asked) {
      query.delete("region_source");
      var rest = query.toString();
      history.replaceState(null, "", location.pathname + (rest ? "?" + rest : "") + location.hash);
    }
    if (!sessionStorage.getItem("galinstan-visit")) {
      sessionStorage.setItem("galinstan-visit", "1");
      document.body.setAttribute("data-region-source", asked === "stored-choice" || asked === "edge-country" ? asked : "explicit-url");
    }
  } catch (e) {}
})();
    </script>
"""


def _nav(current: str | None, pages: dict[str, str]) -> str:
    if not pages:
        return ""  # a page in neither funnel links to neither
    links = []
    for path, nav_id in pages.items():
        mark = ' aria-current="page"' if path == current else ""
        links.append(f'<a href="{path}"{mark}>{_markup(page_copy.text(nav_id))}</a>')
    return "        <nav>\n          " + "\n          ".join(links) + "\n        </nav>\n"


def _wordmark() -> str:
    """The demo's masthead: the product name, then its product line in the accent. The ringed
    G before it is drawn by the stylesheet and hidden from screen readers (Antwain, 2026-10-22)."""
    t = page_copy.text
    return f'<span class="wm">{_markup(t("wordmark"))} <span>{_markup(t("wordmark-product"))}</span></span>'


def _bar(current: str | None) -> str:
    """The header that stays at the top while the page scrolls: wordmark, the funnel's nav, the link to the other
    funnel, and the demo request. The wordmark goes to this funnel's landing page: the root would ask the edge, which
    could send someone who chose this funnel's address to the other one."""
    region = region_of(current)
    home = {"us": US_TRACK, "eu": EU_TRACK}.get(region, "/")
    pages = {"us": US_NAV, "eu": EU_NAV}.get(region, {})
    demo = html.escape(mail_href("cta-demo-target"))
    return f"""    <header class="bar">
      <div class="bar-in">
        <p class="wordmark"><a href="{home}">{_wordmark()}</a></p>
        <div class="mid">
{_nav(current, pages)}{_region_change(current)}
        </div>
        <a class="pill" href="{demo}"{_demo_attrs(current or "/", "header")}>{_markup(page_copy.text("cta-demo"))}</a>
      </div>
    </header>"""


# Section divider: a hairline with a cross at each end and the middle, like the marks on a
# drawing. Drawn by the stylesheet, so it carries no text and fetches nothing.
TICKS = '      <div class="ticks" aria-hidden="true"></div>\n'


def _cards(pages: dict[str, str]) -> str:
    """A funnel's pages as cards on its landing page. Titles only: they are the nav
    labels, and a line of description under each would be new copy."""
    t = page_copy.text
    cards = "\n".join(
        f'        <a class="card reveal" href="{path}">{_markup(t(nav_id))}</a>'
        for path, nav_id in pages.items()
    )
    return f'      <div class="cards">\n{cards}\n      </div>\n'


def _roles() -> str:
    """The role block on the home page: one line for each seat on the buying committee.

    Each approved line ends with the name of the page that carries its argument, and that
    name is a nav label, so it renders as a link to the page and nothing is invented. A line
    that does not end with a nav label fails the build rather than shipping without its link.
    """
    t = page_copy.text
    by_label = {t(nav_id): path for path, (_, nav_id) in PAGES.items()}
    items = []
    for line_id in ("roles-treasury", "roles-dora", "roles-security", "roles-audit"):
        raw = t(line_id)
        label = next((lab for lab in by_label if raw.endswith(" " + lab)), None)
        if label is None:
            raise ValueError(f"{line_id} does not end with a page name")
        lead = raw[: -len(label)].rstrip()
        items.append(f'        <li>{_markup(lead)} <a href="{by_label[label]}">{_markup(label)}</a></li>')
    return (
        f'      <h2>{_markup(t("roles-h2"))}</h2>\n'
        '      <ul class="roles">\n' + "\n".join(items) + "\n      </ul>\n"
    )


# The hero image, served from this site rather than an image host: it is two files in
# the allowlist, like the brief, so it adds no third party. Two widths so a phone does not
# download the desktop one: the 2000 is Antwain's WebP as he supplied it, the 800 a JPEG
# made from it. Below 44rem the frame is 4:3 and the image is cropped to its height, so it
# is drawn at about 1.75 times the frame's width, which is what `sizes` says. `alt=""` marks it decorative: a description a screen reader
# reads aloud is copy, and none has been approved, so it says nothing rather than
# something unapproved. Width and height are set so the page does not jump as it loads.
HERO = ("hero-800.jpg", "hero-2000.webp")

# The headline and evidence voices, Source Serif 4 at 600 and IBM Plex Mono at 400, are the
# demo's own files (`src/galinstan/demo/fonts` in the product repository), served from this
# site so no font service is fetched. Their SIL Open Font Licenses sit beside them in
# `assets/fonts`, with Source Serif 4 at 400, which only the brief uses.
FONTS = ("source-serif-4-600.woff2", "ibm-plex-mono-400.woff2")
FONTS_DIR = pathlib.Path(__file__).resolve().parent / "assets" / "fonts"
HERO_IMG = """\
      <figure class="art">
        <img src="/hero-2000.webp" srcset="/hero-800.jpg 800w, /hero-2000.webp 2000w" sizes="(max-width: 44rem) 175vw, (max-width: 67rem) 100vw, 64rem" width="2000" height="857" alt="" fetchpriority="high">
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


def render_structured_data(description: str = "meta-description") -> str:
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
        "description": t(description),
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
  {_body(path)}
{_bar(path)}
    <main>
      <h1>{_markup(t(f"{prefix}-h1"))}</h1>
      <div class="prose">
      <p class="sub">{_markup(t(f"{prefix}-sub"))}</p>
{body}
      </div>
      <div class="prose">
      <p class="cta">{_mail_link("cta-demo-target", f"{prefix}-cta", _demo_attrs(path, "body"))}</p>
      </div>
{_brief_link(path)}{_footer()}
    </main>
{REGION_SCRIPT}  </body>
</html>
"""


def render_us_page(path: str) -> str:
    spec = US_PAGES[path]
    t = page_copy.text
    sub = f'      <p class="sub">{_markup(t(spec["sub"]))}</p>\n' if "sub" in spec else ""
    body = "\n".join(f"      <p>{_markup(t(k))}</p>" for k in spec["body"])
    return f"""{_head(t(spec["title"]), path, t(spec["description"]))}
  {_body(path)}
{_bar(path)}
    <main>
      <h1>{_markup(t(spec["h1"]))}</h1>
      <div class="prose">
{sub}{body}
      </div>
      <div class="prose">
      <p class="cta">{_mail_link("cta-demo-target", spec["cta"], _demo_attrs(path, "body"))}</p>
      </div>
{_footer()}
    </main>
{REGION_SCRIPT}  </body>
</html>
"""


# Between the two landings only (ask 202). A crawler reaches the EU funnel through this and the sitemap, never through
# the root's redirect: Googlebot crawls from the US.
HREFLANG = f"""
    <link rel="alternate" hreflang="en-US" href="{SITE_URL}{US_TRACK}">
    <link rel="alternate" hreflang="en" href="{SITE_URL}{EU_TRACK}">
    <link rel="alternate" hreflang="x-default" href="{SITE_URL}/">"""


def render_us_track() -> str:
    """The US landing: the lead that stood at the root until 2026-10-30, the surplus example, and its pages."""
    t = page_copy.text
    body = "\n".join(f"      <p>{_markup(t(k))}</p>" for k in ("home-body-1", "home-body-2", "us-il-figure"))
    extra = HREFLANG + render_structured_data("home-meta-description")
    return f"""{_head(t("us-meta-title"), US_TRACK, t("home-meta-description"), extra=extra)}
  {_body(US_TRACK)}
{_bar(US_TRACK)}
    <main>
      <h1>{_markup(t("home-h1"))}</h1>
{HERO_IMG}      <div class="prose">
{body}
      <p class="cta">{_mail_link("cta-demo-target", "cta-demo", _demo_attrs(US_TRACK, "body"))}</p>
      </div>
{TICKS}{_cards(US_NAV)}{_footer()}
    </main>
{REGION_SCRIPT}  </body>
</html>
"""


def render_eu_track() -> str:
    """The EU landing: the home page as it stood until 2026-10-30, minus what its feature pages say."""
    t = page_copy.text
    body = "\n".join(f"      <p>{_markup(t(k))}</p>" for k in ("body-1", "body-2"))
    body += "\n" + _roles() + f"      <p>{_markup(t('body-3'))}</p>"
    return f"""{_head(t("meta-title"), EU_TRACK, t("meta-description"), extra=HREFLANG + render_structured_data())}
  {_body(EU_TRACK)}
{_bar(EU_TRACK)}
    <main>
      <h1>{_markup(t("headline"))}</h1>
{HERO_IMG}      <div class="prose">
{body}
      <p class="cta">{_mail_link("cta-demo-target", "cta-demo", _demo_attrs(EU_TRACK, "body"))}</p>
      </div>
{TICKS}{_cards(EU_NAV)}{_brief_link(EU_TRACK)}{_footer()}
    </main>
{REGION_SCRIPT}  </body>
</html>
"""


def render_privacy() -> str:
    t = page_copy.text
    return f"""{_head(t("privacy-meta-title"), "/privacy")}
  {_body("/privacy")}
{_bar("/privacy")}
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
{REGION_SCRIPT}  </body>
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
      <p class="wordmark">{_wordmark()}</p>
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
BRIEF_LINKED_FROM = (EU_TRACK, "/eu-banks/audit-evidence", "/eu-banks/deployment")

BRIEF_CSS = """\
@page {
  size: A4;
  margin: 24mm 22mm 24mm 22mm;
  @bottom-left { content: "Galinstan"; font: 600 8pt "Source Serif 4", serif; color: #7c7361; }
  @bottom-right { content: counter(page); font: 400 8pt "IBM Plex Mono", monospace; color: #7c7361; }
}
@page :first { @bottom-left { content: none; } @bottom-right { content: none; } }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; color: #1e1a13; font: 400 10pt/1.5 "Source Serif 4", Georgia, serif; }
.wordmark { display: flex; align-items: center; gap: 3mm; font-size: 13pt; font-weight: 600; margin: 0 0 30mm; }
.wordmark::before {
  content: "G"; display: flex; align-items: center; justify-content: center;
  width: 8.5mm; height: 8.5mm; border: 0.75pt solid #1e1a13; border-radius: 50%; font-size: 11pt; color: #0a5a4e;
}
.wm span { color: #0a5a4e; }
h1 { font-size: 28pt; font-weight: 600; line-height: 1.15; margin: 0 0 6mm; }
.sub { font-size: 13.5pt; line-height: 1.45; color: #7c7361; max-width: 130mm; margin: 0 0 12mm; }
.edition { font: 400 8.5pt/1.5 "IBM Plex Mono", monospace; color: #7c7361; border-top: 0.5pt solid #e2dbc9; padding-top: 3mm; margin: 0 0 14mm; }
h2 { font-size: 15pt; font-weight: 600; margin: 8mm 0 2.5mm; break-after: avoid; }
h3 { font-size: 11pt; font-weight: 600; margin: 6mm 0 1.5mm; break-after: avoid; }
p { margin: 0 0 3mm; orphans: 3; widows: 3; }
ul { margin: 0 0 3.5mm; padding-left: 5mm; }
li { margin: 0 0 1.8mm; }
ol.sources { font-size: 9pt; line-height: 1.45; padding-left: 6mm; color: #7c7361; }
strong { font-weight: 600; }
a { color: #0a5a4e; }
.close { margin-top: 10mm; padding-top: 3mm; border-top: 0.5pt solid #e2dbc9; font-size: 9.5pt; }
.close p { margin: 0 0 1.5mm; }
.cover { break-after: page; }
"""

_BRIEF_BODY = re.compile(r"brief-(h|h3|p|li|ref)-.+")


def _brief_faces() -> str:
    """The demo's fonts inlined as data, so Chrome prints the brief with nothing to fetch."""
    faces = ""
    for family, weight, name in (("Source Serif 4", 400, "source-serif-4-400"),
                                 ("Source Serif 4", 600, "source-serif-4-600"),
                                 ("IBM Plex Mono", 400, "ibm-plex-mono-400")):
        data = base64.b64encode((FONTS_DIR / f"{name}.woff2").read_bytes()).decode("ascii")
        faces += (f'@font-face {{ font-family: "{family}"; font-weight: {weight}; font-style: normal; '
                  f'src: url(data:font/woff2;base64,{data}) format("woff2"); }}\n')
    return faces


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
{_brief_faces()}{BRIEF_CSS}    </style>
  </head>
  <body>
    <section class="cover">
      <p class="wordmark">{_wordmark()}</p>
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


def render_redirects() -> str:
    """Cloudflare Pages' `_redirects`: each address that moved, and its `.html` form, permanently to its new one."""
    lines = [f"{old}{suffix} {new} 301" for old, new in MOVED.items() for suffix in ("", ".html")]
    return "\n".join(lines) + "\n"


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
    US_TRACK: lambda: render_us_track(),
    **{path: (lambda p=path: render_us_page(p)) for path in US_PAGES},
    EU_TRACK: lambda: render_eu_track(),
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
    "_redirects": render_redirects,
    f"{US_TRACK[1:]}.html": render_us_track,
    **{f"{path[1:]}.html": (lambda p=path: render_us_page(p)) for path in US_PAGES},
    f"{EU_TRACK[1:]}.html": render_eu_track,
    **{f"{path[1:]}.html": (lambda p=path: render_stage_2(p)) for path in PAGES},
    "privacy.html": render_privacy,
    "404.html": render_404,
    "robots.txt": render_robots,
    "sitemap.xml": render_sitemap,
    "galinstan-brief.pdf": render_brief_pdf,
    **{name: (lambda n=name: (ASSETS / n).read_bytes()) for name in HERO},
    **{name: (lambda n=name: (FONTS_DIR / n).read_bytes()) for name in FONTS},
}


def build(target: pathlib.Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for name, render in ALLOWLIST.items():
        (target / name).parent.mkdir(parents=True, exist_ok=True)
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
        stray = sorted(p.relative_to(PUBLIC).as_posix() for p in PUBLIC.rglob("*") if p.is_file()) if PUBLIC.exists() else []
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
