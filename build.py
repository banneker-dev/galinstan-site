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
  --flag: #8a3a12;
  --measure: 34rem;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0;
  padding: 3rem 1.5rem 4rem;
  background: var(--paper);
  color: var(--ink);
  font: 400 1.0625rem/1.65 ui-serif, Georgia, "Times New Roman", serif;
}
main { max-width: var(--measure); margin: 0 auto; }
.wordmark {
  font-family: ui-sans-serif, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 0.9375rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin: 0 0 2.5rem;
}
h1 {
  font-size: 1.5rem;
  font-weight: 400;
  line-height: 1.35;
  margin: 0 0 2rem;
  text-wrap: balance;
}
p { margin: 0 0 1.25rem; color: var(--ink-soft); }
footer {
  margin-top: 3.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--rule);
  font-family: ui-sans-serif, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 0.8125rem;
  line-height: 1.6;
  color: var(--ink-soft);
}
footer p { margin: 0 0 0.375rem; color: inherit; }
.wordmark a { text-decoration: none; }
nav {
  font-family: ui-sans-serif, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 0.875rem;
  margin: -1.5rem 0 2.5rem;
  display: flex; flex-wrap: wrap; gap: 0.25rem 1.25rem;
}
nav a { color: var(--ink-soft); }
nav a[aria-current="page"] { color: var(--ink); text-decoration: none; font-weight: 600; }
.sub { color: var(--ink); font-size: 1.125rem; }
.cta { margin-top: 2rem; }
strong { color: var(--ink); font-weight: 600; }
a { color: inherit; text-underline-offset: 2px; }
.todo {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.8125rem;
  color: var(--flag);
  background: #fdf2ec;
  border: 1px dashed var(--flag);
  border-radius: 2px;
  padding: 0.0625rem 0.375rem;
}
@media (prefers-color-scheme: dark) {
  :root {
    --ink: #eef1f3; --ink-soft: #b3bcc3; --rule: #2b3238;
    --paper: #0f1216; --flag: #e8a87c;
  }
  .todo { background: #24170f; }
}
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
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
    return "      <nav>\n        " + "\n        ".join(links) + "\n      </nav>"


def _footer() -> str:
    t = page_copy.text
    return f"""      <footer>
        <p>{_markup(t("foot-claim"))}</p>
        <p>{_markup(t("entity"))}</p>
        <p>{_contact_link()}</p>
        <p><a href="/privacy">Privacy</a></p>
        <p>{_markup(t("legal-footer"))}</p>
      </footer>"""


def _head(title: str, canonical: str, description: str | None = None, robots: str = "index, follow") -> str:
    desc = f'\n    <meta name="description" content="{html.escape(description, quote=True)}">' if description else ""
    canon = f'\n    <link rel="canonical" href="{SITE_URL}{canonical}">' if canonical else ""
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)}</title>{desc}{canon}
    <meta name="robots" content="{robots}">
    <style>
{CSS}    </style>
  </head>"""


def _wordmark(link: bool = True) -> str:
    mark = _markup(page_copy.text("wordmark"))
    return f'      <p class="wordmark"><a href="/">{mark}</a></p>' if link else f'      <p class="wordmark">{mark}</p>'


def render_stage_2(path: str) -> str:
    prefix, _ = PAGES[path]
    t = page_copy.text
    bodies = [i.id for i in page_copy.LINES if re.fullmatch(rf"{prefix}-body-\d+", i.id)]
    body = "\n".join(f"      <p>{_markup(t(k))}</p>" for k in bodies)
    return f"""{_head(t(f"{prefix}-meta-title"), path, t(f"{prefix}-meta-description"))}
  <body>
    <main>
{_wordmark()}
{_nav(path)}
      <h1>{_markup(t(f"{prefix}-h1"))}</h1>
      <p class="sub">{_markup(t(f"{prefix}-sub"))}</p>
{body}
{_whitepaper_link(path)}      <p class="cta">{_mail_link("cta-demo-target", f"{prefix}-cta")}</p>
{_footer()}
    </main>
  </body>
</html>
"""


def render_index() -> str:
    t = page_copy.text
    body = "\n".join(
        f"      <p>{_markup(t(k))}</p>" for k in ("body-1", "body-2", "body-3")
    )
    return f"""{_head(t("meta-title"), "/", t("meta-description"))}
  <body>
    <main>
{_wordmark(link=False)}
{_nav(None)}
      <h1>{_markup(t("headline"))}</h1>
{body}
{_whitepaper_link("/")}      <p class="cta">{_mail_link("cta-demo-target", "cta-demo")}</p>
{_footer()}
    </main>
  </body>
</html>
"""


def render_privacy() -> str:
    t = page_copy.text
    return f"""{_head(t("privacy-meta-title"), "/privacy")}
  <body>
    <main>
{_wordmark()}
{_nav(None)}
      <h1>{_markup(t("privacy-meta-title"))}</h1>
      <p>{_markup(t("privacy-controller"))}</p>
      <p>{_markup(t("privacy-analytics"))}</p>
      <p>{_markup(t("privacy-contact-label"))} {_contact_link()}</p>
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


# The public whitepaper, served at /whitepaper.pdf.
#
# **The PDF is committed, not built here**, because this build has no dependencies and a
# typeset PDF needs a browser engine. So the build renders the paper's *source*, an HTML
# page made only of strings from the copy register, and `tools/make_whitepaper.py` prints
# that source to `assets/whitepaper.pdf` with a local Chrome and records both hashes in
# `assets/whitepaper.lock.json`. The guard `whitepaper_matches_its_source` fails the build
# if the register, this template or the PDF changes without the other two: a paper that
# ships is always the one its approved strings describe.
#
# No URL in it but the contact mail link, no author field, no NDA offer (Antwain,
# 2026-09-25: the technical detail is not offered without a direct conversation first).
ASSETS = ROOT / "assets"
WHITEPAPER_PDF = ASSETS / "whitepaper.pdf"
WHITEPAPER_LOCK = ASSETS / "whitepaper.lock.json"
WHITEPAPER_PATH = "/whitepaper.pdf"
WHITEPAPER_LINKED_FROM = ("/", "/audit-evidence", "/deployment")

WHITEPAPER_CSS = """\
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

_WP_BODY = re.compile(r"wp-(h|h3|p|li|ref)-.+")


def render_whitepaper_source() -> str:
    """The paper as HTML, every visible word from the register, in the register's order.

    The cover carries the summary, so it reads as a one-page brief on its own; the rest
    follows on the pages after it.
    """
    t = page_copy.text
    items = [(m.group(1), i.id) for i in page_copy.LINES if (m := _WP_BODY.fullmatch(i.id))]
    out: list[str] = []
    open_list = ""
    for kind, line_id in items:
        wanted = {"li": "ul", "ref": "ol"}.get(kind, "")
        if open_list and open_list != wanted:
            out.append(f"      </{open_list}>")
            open_list = ""
        if kind == "h":
            if line_id == "wp-h-problem":  # the cover ends with the summary
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
    <title>{html.escape(t("wp-meta-title"))}</title>
    <style>
{WHITEPAPER_CSS}    </style>
  </head>
  <body>
    <section class="cover">
      <p class="wordmark">{_markup(t("wordmark"))}</p>
      <h1>{_markup(t("wp-title"))}</h1>
      <p class="sub">{_markup(t("wp-sub"))}</p>
      <p class="edition">{_markup(t("wp-edition"))}</p>
{body}
      <div class="close">
        <p>{_markup(t("wp-contact-label"))} {_mail_link("wp-contact")}</p>
        <p>{_markup(t("entity"))}</p>
        <p>{_markup(t("legal-footer"))}</p>
      </div>
    </section>
  </body>
</html>
"""


def _whitepaper_link(path: str) -> str:
    if path not in WHITEPAPER_LINKED_FROM:
        return ""
    return f'      <p><a href="{WHITEPAPER_PATH}">{_markup(page_copy.text("wp-link"))}</a></p>\n'


def render_whitepaper_pdf() -> bytes:
    return WHITEPAPER_PDF.read_bytes()


# The crawler policy, approved by Antwain on 2026-09-21 as option A in
# `50_Claude_Outputs/MARKETING_STRATEGY.md` §7a: present, not trained on. Search and live
# AI answers yes, training no.
#
# The signal is scoped to the group it sits in, so it goes inside `User-agent: *` rather
# than above it. Content signals are advisory and some crawlers ignore them, which is why
# Cloudflare's AI Crawl Control blocks the training category as well — but the policy of
# record is this committed file. Cloudflare's own managed robots.txt stays off precisely
# so there are not two places to read it from (SETUP_GITHUB_CLOUDFLARE.md Part 3).
CONTENT_SIGNAL = "Content-Signal: search=yes, ai-input=yes, ai-train=no"


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
    WHITEPAPER_PATH: lambda: render_whitepaper_source(),
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
    "whitepaper.pdf": render_whitepaper_pdf,
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
