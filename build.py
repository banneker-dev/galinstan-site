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
    """Escapes a copy string, then re-marks the placeholder tokens so they are visible."""
    escaped = html.escape(raw, quote=False)
    if escaped.startswith("[[TODO:"):
        return f'<span class="todo">{escaped}</span>'
    return escaped


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
    address = page_copy.text("contact")
    subject = urllib.parse.quote(page_copy.CONTACT_SUBJECT)
    return f'<a href="mailto:{html.escape(address)}?subject={subject}">{html.escape(address)}</a>'


def render_index() -> str:
    t = page_copy.text
    body = "\n".join(
        f"      <p>{_markup(t(k))}</p>" for k in ("body-1", "body-2", "body-3")
    )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(t("meta-title"))}</title>
    <meta name="description" content="{html.escape(t("meta-description"), quote=True)}">
    <link rel="canonical" href="{SITE_URL}/">
    <meta name="robots" content="index, follow">
    <style>
{CSS}    </style>
  </head>
  <body>
    <main>
      <p class="wordmark">{_markup(t("wordmark"))}</p>
      <h1>{_markup(t("headline"))}</h1>
{body}
      <footer>
        <p>{_markup(t("entity"))}</p>
        <p>{_contact_link()}</p>
        <p><a href="/privacy.html">Privacy</a></p>
        <p>{_markup(t("legal-footer"))}</p>
      </footer>
    </main>
  </body>
</html>
"""


def render_privacy() -> str:
    t = page_copy.text
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Privacy — Galinstan</title>
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{SITE_URL}/privacy.html">
    <style>
{CSS}    </style>
  </head>
  <body>
    <main>
      <p class="wordmark">{_markup(t("wordmark"))}</p>
      <h1>Privacy</h1>
      <p><strong>Data controller.</strong> {_markup(t("privacy-controller"))}</p>
      <p><strong>Analytics.</strong> {_markup(t("privacy-analytics"))}</p>
      <p><strong>Contact.</strong> {_contact_link()}</p>
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
    <title>Not found — Galinstan</title>
    <meta name="robots" content="noindex">
    <style>
{CSS}    </style>
  </head>
  <body>
    <main>
      <p class="wordmark">{_markup(t("wordmark"))}</p>
      <h1>That page does not exist.</h1>
      <p><a href="/">Return to the front page.</a></p>
    </main>
  </body>
</html>
"""


def render_robots() -> str:
    # Owned from the first release rather than left to the host's default. The practice
    # shipped its own robots.txt at release 54 and regretted the gap.
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n"


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
SITEMAP = {
    "/": lambda: render_index(),
    "/privacy.html": lambda: render_privacy(),
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
    "privacy.html": render_privacy,
    "404.html": render_404,
    "robots.txt": render_robots,
    "sitemap.xml": render_sitemap,
}


def build(target: pathlib.Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for name, render in ALLOWLIST.items():
        (target / name).write_text(render(), encoding="utf-8")


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
