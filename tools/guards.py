"""Guards for galinstan.ai. Every one of these fails a build; none of them warns.

`50_Claude_Outputs/METHOD_FROM_JJ.md` section 5, verbatim: *"Do not delete a guard to make
a build pass."* If a guard is wrong, it gets changed on purpose, in its own commit, with
the reason written down. It does not get deleted to unblock a release.

Each guard returns a list of failure strings. Empty means it passed. `run_all` is what CI
calls, and `tests/test_guards.py` breaks each one in both directions, because counting the
absence of something is not a test until the thing has been confirmed to run.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import build  # noqa: E402
import page_copy  # noqa: E402

PUBLIC = ROOT / "public"
OWN_HOST = "galinstan.ai"

# Anything that would make the browser open a second connection.
_EXTERNAL_PATTERNS = [
    (re.compile(r"<script\b[^>]*\bsrc\s*=", re.I), "external <script src>"),
    (re.compile(r"<link\b[^>]*\brel\s*=\s*[\"']?stylesheet", re.I), "<link rel=stylesheet>"),
    (re.compile(r"@import\b", re.I), "CSS @import"),
    (re.compile(r"url\(\s*[\"']?https?:", re.I), "CSS url() over http"),
    (re.compile(r"<(?:img|iframe|video|audio|source|embed|object)\b[^>]*\b(?:src|data)\s*=\s*[\"']https?:", re.I), "remote embedded resource"),
    (re.compile(r"<link\b[^>]*\brel\s*=\s*[\"']?(?:preconnect|dns-prefetch|preload)", re.I), "resource hint to a third party"),
]

# Every page the build publishes, taken from the allowlist so a page added there cannot be
# missed here.
_HTML = tuple(name for name in build.ALLOWLIST if name.endswith(".html"))


def _pages() -> list[tuple[str, str]]:
    return [(n, (PUBLIC / n).read_text(encoding="utf-8")) for n in _HTML if (PUBLIC / n).exists()]


def no_external_references(pages=None) -> list[str]:
    """Nothing on a Galinstan page is fetched from somewhere else."""
    failures = []
    for name, text in pages if pages is not None else _pages():
        for pattern, label in _EXTERNAL_PATTERNS:
            if pattern.search(text):
                failures.append(f"{name}: {label}")
        for url in re.findall(r"https?://([^\s\"'<>)]+)", text):
            host = url.split("/")[0].lower()
            if host != OWN_HOST and not host.endswith("." + OWN_HOST):
                if host in ("www.sitemaps.org", "www.w3.org"):  # XML namespaces, not fetched
                    continue
                failures.append(f"{name}: absolute URL to {host}")
    return failures


def required_metadata(pages=None) -> list[str]:
    """The metadata that cannot be added retroactively to a visit that already happened."""
    failures = []
    content_page = ["<html lang=", "<title>", 'name="description"', 'rel="canonical"', "viewport"]
    required = {
        "index.html": content_page,
        **{f"{path[1:]}.html": content_page for path in build.PAGES},
        "privacy.html": ["<html lang=", "<title>", 'rel="canonical"', "viewport"],
        "404.html": ["<html lang=", "<title>", 'name="robots" content="noindex"'],
    }
    for name, text in pages if pages is not None else _pages():
        for needle in required.get(name, []):
            if needle not in text:
                failures.append(f"{name}: missing {needle}")
    for name in ("robots.txt", "sitemap.xml"):
        if not (PUBLIC / name).exists():
            failures.append(f"{name}: not built")
    return failures


# Exactly one host may be fetched by a marketing page, and only because Cloudflare injects
# it at the edge after the build. See docs/ANALYTICS.md. Anything else, including a second
# Cloudflare product, is a build failure.
PERMITTED_BEACON_HOSTS = {"static.cloudflareinsights.com"}

# Paths that host the demo instance carry the product's rule, not the marketing rule:
# nothing at all, no exception. Nothing is served under it yet; the rule is written before
# the path exists so it is not decided in a hurry later.
AIR_GAPPED_PATH_PREFIXES = ("/demo",)


def live_response_has_only_permitted_fetches(url: str, body: str) -> list[str]:
    """Checked against what a visitor is served, not against what the build produced.

    The build-time guard reads `public/`. Cloudflare's beacon is injected into the
    response afterwards, so the artifact is silent about it and a green build proves
    nothing about the live page. This runs after a deploy, over the fetched body.
    """
    failures = []
    for host in sorted(set(re.findall(r"https?://([A-Za-z0-9.\-]+)", body))):
        if host == OWN_HOST or host.endswith("." + OWN_HOST):
            continue
        if host in ("www.sitemaps.org", "www.w3.org"):
            continue
        if host in PERMITTED_BEACON_HOSTS:
            if any(url.rstrip("/").endswith(p) or p in url for p in AIR_GAPPED_PATH_PREFIXES):
                failures.append(f"{url}: the beacon is present on an air-gapped path ({host})")
            continue
        failures.append(f"{url}: unexpected third-party host in the live response: {host}")
    return failures


def publication_gate() -> list[str]:
    """Only consulted for a production release. Previews are exempt on purpose."""
    import build

    failures = [
        f"copy {item.id!r} is {item.status}, not approved" for item in page_copy.blockers()
    ]
    if build.ANALYTICS is None:
        failures.append(
            "analytics is not configured — WEB_SPEC.md section 6a requires measurement "
            "to be complete before the first visitor, and it does not backfill"
        )
    return failures


def declared_addresses_agree(pages=None, sitemap=None) -> list[str]:
    """One address per page, in the sitemap, the canonical and every internal link.

    Three defects on the first release were one defect: the build wrote `privacy.html`
    and the host served `/privacy`, so the sitemap declared a URL that redirects, the
    canonical pointed somewhere other than where the page was served, and the footer sent
    every visitor through a hop. None of it was visible from the build, because the
    redirect belongs to the host and does not exist until the bytes are published.

    So the build now names the addresses it declares — `build.SITEMAP` — and this fails if
    a canonical, a sitemap entry or an internal link disagrees with that list. The host's
    behaviour is still the host's; what is checked here is that we only ever declare one
    address per page.
    """
    failures = []
    declared = {path: f"{build.SITE_URL}{path}" for path in build.SITEMAP}
    canonical_of = {path: ("index.html" if path == "/" else f"{path[1:]}.html") for path in build.SITEMAP}

    if sitemap is None:
        sitemap = (PUBLIC / "sitemap.xml").read_text(encoding="utf-8")
    rendered = dict(pages) if pages is not None else None
    for path, url in declared.items():
        if f"<loc>{url}</loc>" not in sitemap:
            failures.append(f"sitemap.xml: {url} is not declared")
        name = canonical_of.get(path)
        if name is None:
            continue
        if rendered is not None:
            if name not in rendered:
                continue  # a caller checking one page only
            page = rendered[name]
        else:
            page = (PUBLIC / name).read_text(encoding="utf-8")
        if f'rel="canonical" href="{url}"' not in page:
            failures.append(f"{name}: its canonical is not {url}")

    for name, text in (pages if pages is not None else _pages()):
        for path in build.SITEMAP:
            stale = f'href="{path}.html"' if path != "/" else 'href="/index.html"'
            if stale in text:
                failures.append(f"{name}: links to {stale[6:-1]}, which the host redirects")
    return failures


def crawler_policy(served=None) -> list[str]:
    """The approved crawler policy is a committed file, so it is checked like one.

    `robots.txt` carries the content signal from decision 13 — present, not trained on.
    Cloudflare's managed robots.txt is off so this file is the only place the policy
    lives, and `tools/verify_live.py` asserts the same line in the served response,
    because a file that is right in the repository says nothing about what a crawler was
    handed.
    """
    if served is None:
        served = (PUBLIC / "robots.txt").read_text(encoding="utf-8")
    if build.CONTENT_SIGNAL not in served:
        return [f"robots.txt: the crawler policy line is missing ({build.CONTENT_SIGNAL})"]
    group = served.split("User-agent: *", 1)[-1].split("\n\n", 1)[0]
    if build.CONTENT_SIGNAL not in group:
        return ["robots.txt: the content signal is outside the User-agent group it applies to"]
    return []


def mail_targets_carry_their_subjects(pages=None) -> list[str]:
    """Every mail link is an approved target with its approved subject (Round 9, ask 47).

    Two directions. Each mail-bearing string in the register must be served somewhere as
    exactly its `mailto:` with subject — a template edit that drops a subject is caught on
    the commit. And every `mailto:` on every page must be one of those — a link to an
    address nobody approved is caught too. `tools/verify_live.py` asserts the same over the
    served response, which is where an edge rewrite would show.
    """
    failures = []
    pages = pages if pages is not None else _pages()
    approved = {build.mail_href(item.id) for item in page_copy.LINES if item.mail_subject}
    served = set()
    for name, text in pages:
        for href in re.findall(r'href="(mailto:[^"]*)"', text):
            href = href.replace("&amp;", "&")
            served.add(href)
            if href not in approved:
                failures.append(f"{name}: mail link {href!r} is not an approved target and subject")
    for href in sorted(approved - served):
        failures.append(f"no page serves the approved mail link {href!r}")
    return failures


ALWAYS = {
    "no external references": no_external_references,
    "required metadata": required_metadata,
    "declared addresses agree": declared_addresses_agree,
    "crawler policy": crawler_policy,
    "mail targets carry their subjects": mail_targets_carry_their_subjects,
}

PRODUCTION_ONLY = {"publication gate": publication_gate}


def run_all(production: bool) -> int:
    checks = dict(ALWAYS)
    if production:
        checks.update(PRODUCTION_ONLY)
    failed = 0
    for label, check in checks.items():
        failures = check()
        if failures:
            failed += 1
            print(f"FAIL  {label}")
            for f in failures:
                print(f"        {f}")
        else:
            print(f"ok    {label}")
    return 1 if failed else 0


if __name__ == "__main__":
    production = "--production" in sys.argv
    if production:
        print("Running production guards (a release, not a preview).\n")
    raise SystemExit(run_all(production))
