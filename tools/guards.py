"""Guards for galinstan.ai. Every one of these fails a build; none of them warns.

`50_Claude_Outputs/METHOD_FROM_JJ.md` section 5, verbatim: *"Do not delete a guard to make
a build pass."* If a guard is wrong, it gets changed on purpose, in its own commit, with
the reason written down. It does not get deleted to unblock a release.

Each guard returns a list of failure strings. Empty means it passed. `run_all` is what CI
calls, and `tests/test_guards.py` breaks each one in both directions, because counting the
absence of something is not a test until the thing has been confirmed to run.
"""

from __future__ import annotations

import html as _html
import pathlib
import re
import sys
from html.parser import HTMLParser

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
    # The product brief's source is checked with the pages: it is prose a visitor reads, in
    # the PDF, so the dash, register and mail-link guards apply to it as to any page.
    pages = [(n, (PUBLIC / n).read_text(encoding="utf-8")) for n in _HTML if (PUBLIC / n).exists()]
    return pages + [("brief source", build.render_brief_source())]


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


# RULES.md D2, Antwain 2026-09-24: "No dashes as punctuation in the middle of a sentence in
# any marketing, website, whitepaper, product brief or report copy; hyphenated compounds are
# fine." (product brief added 2026-09-25)
#
# Two passes, because the rule was broken in two different ways and one pass catches only one.
# Ten violations lived in the copy register. Two lived in page titles that were not in the
# register at all, which is how they survived every copy review. A register-only guard would
# have missed those two; a page-only guard would report a served byte without naming the
# string that produced it.
#
# The served-page pass looks for the two real dashes only. A hyphen with spaces around it is
# legitimate inside the CSS this build inlines, as in calc(100% - 2rem), so applying the
# loose-hyphen rule to a whole page would fail on stylesheet arithmetic.
_DASH_AS_PUNCTUATION = [("\u2014", "em dash"), ("\u2013", "en dash")]

# A hyphen with a space on at least one side is doing a dash's job rather than spelling one.
# air-gapped, on-premise and high-quality are untouched, which is the half of D2 that says
# hyphenated compounds are fine.
_LOOSE_HYPHEN = re.compile(r"(?:\s-\s|\s-(?=\w)|(?<=\w)-\s)")


def no_dashes_as_punctuation(pages=None) -> list[str]:
    """RULES.md D2. A dash used as punctuation reads as machine written, and this buyer notices."""
    failures = []
    for item in page_copy.LINES:
        for field in ("text", "mail_subject"):
            value = getattr(item, field, "") or ""
            for ch, label in _DASH_AS_PUNCTUATION:
                if ch in value:
                    failures.append(f"copy {item.id!r}.{field}: {label}")
            if _LOOSE_HYPHEN.search(value):
                failures.append(f"copy {item.id!r}.{field}: hyphen used as punctuation")
    for name, text in pages if pages is not None else _pages():
        for ch, label in _DASH_AS_PUNCTUATION:
            if ch in text:
                failures.append(f"{name}: {label} in the served page")
    return failures


class _Prose(HTMLParser):
    """Every string a visitor can read: text nodes, plus the description a search result shows.

    Skips style and script, which are not prose, and attributes other than the description,
    which are addresses and markup rather than copy.
    """

    _SKIP = {"style", "script"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._open: list[str] = []
        self.found: list[str] = []

    def handle_starttag(self, tag, attrs):
        self._open.append(tag)
        pairs = dict(attrs)
        if tag == "meta" and pairs.get("name") == "description" and pairs.get("content"):
            self.found.append(pairs["content"])

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self._open.pop()

    def handle_endtag(self, tag):
        if self._open and self._open[-1] == tag:
            self._open.pop()

    def handle_data(self, data):
        if any(t in self._SKIP for t in self._open):
            return
        text = " ".join(data.split())
        if text:
            self.found.append(text)


def _flat(text: str) -> str:
    return " ".join(_html.unescape(text).split())


def page_prose_comes_from_the_register(pages=None) -> list[str]:
    """src/page_copy.py says nothing else in this repository may contain page prose. Until this
    guard existed that was an intention rather than a fact, and six strings were outside it.

    A text node passes when it is contained in some approved string. Containment rather than
    equality, because `**lead-in**` renders as two nodes around a <strong>, so a node is
    legitimately a fragment of the string that produced it.
    """
    approved = [_flat(item.text.replace("**", "")) for item in page_copy.LINES]
    approved += [_flat(item.mail_subject) for item in page_copy.LINES if item.mail_subject]

    failures = []
    for name, text in pages if pages is not None else _pages():
        parser = _Prose()
        parser.feed(text)
        for node in parser.found:
            flat = _flat(node)
            if not any(flat in candidate for candidate in approved):
                failures.append(f"{name}: prose not in the copy register: {node!r}")
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
    canonical_of = {
        path: ("index.html" if path == "/" else f"{path[1:]}.html")
        for path in build.SITEMAP
        if path != build.BRIEF_PATH  # a PDF has no canonical tag to agree with
    }

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


def _pdf_uris(pdf: bytes) -> set[str]:
    return {u.decode("latin-1").replace("\\(", "(").replace("\\)", ")")
            for u in re.findall(rb"/URI\s*\(((?:[^()\\]|\\.)*)\)", pdf)}


def brief_matches_its_source(pdf=None, lock=None, source=None) -> list[str]:
    """The committed PDF is the one the register's strings describe, and says nothing else.

    `tools/make_brief.py` prints the source and records both hashes. If a `brief-` string
    or the template changes and the PDF is not printed again, the source hash disagrees;
    if the PDF is swapped or edited, its own hash does. Either way the build fails rather
    than serving a paper nobody approved. It also fails on an author field (RULES.md D5:
    no direct reference to Antwain in the whitepaper or the product brief), and on any
    link but the approved contact, since a PDF's links are not in the pages the other
    guards read.
    """
    import hashlib
    import json

    failures = []
    if lock is None:
        if not build.BRIEF_LOCK.exists():
            return [f"{build.BRIEF_LOCK.name}: missing; run tools/make_brief.py"]
        lock = json.loads(build.BRIEF_LOCK.read_text(encoding="utf-8"))
    if pdf is None:
        if not build.BRIEF_PDF.exists():
            return [f"{build.BRIEF_PDF.name}: missing; run tools/make_brief.py"]
        pdf = build.BRIEF_PDF.read_bytes()
    if source is None:
        source = build.render_brief_source()

    if hashlib.sha256(source.encode("utf-8")).hexdigest() != lock.get("source_sha256"):
        failures.append(
            "galinstan-brief.pdf: its source has changed since it was printed; "
            "run tools/make_brief.py"
        )
    if hashlib.sha256(pdf).hexdigest() != lock.get("pdf_sha256"):
        failures.append("galinstan-brief.pdf: the file is not the one the lock records")
    if re.search(rb"/Author\s*\(", pdf):
        failures.append("galinstan-brief.pdf: carries an author field")
    allowed = {build.mail_href("brief-contact")}
    for uri in sorted(_pdf_uris(pdf) - allowed):
        host = re.match(r"https?://([^/]+)", uri)
        if host and (host.group(1) == OWN_HOST or host.group(1).endswith("." + OWN_HOST)):
            continue
        failures.append(f"galinstan-brief.pdf: links to {uri!r}, which is not the approved contact")
    return failures


ALWAYS = {
    "no external references": no_external_references,
    "no dashes as punctuation": no_dashes_as_punctuation,
    "page prose comes from the register": page_prose_comes_from_the_register,
    "required metadata": required_metadata,
    "declared addresses agree": declared_addresses_agree,
    "crawler policy": crawler_policy,
    "mail targets carry their subjects": mail_targets_carry_their_subjects,
    "brief matches its source": brief_matches_its_source,
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
