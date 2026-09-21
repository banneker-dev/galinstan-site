#!/usr/bin/env python3
"""Verifies what is actually being served, not what was built.

    python3 tools/verify_live.py https://galinstan.ai/

Two things are checked, and each exists because of a specific way the build-time guards
can pass while the live page is wrong.

**The approved headline is in the body.** *"A status code cannot tell a stale hit from a
live one."* The practice once had a 200 serving its 404 page. So the body is fetched with
a cache-buster and the approved sentence is grepped out of it.

**Only permitted hosts are fetched.** Cloudflare injects its analytics beacon at the edge,
after the build. `public/index.html` is silent about it, so the build-time guard cannot see
it — and could not see a second injected file either. This can. See `docs/ANALYTICS.md`.

Standard library only, like the rest of this repository.
"""

from __future__ import annotations

import pathlib
import sys
import urllib.request
import uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import page_copy  # noqa: E402
from tools import guards  # noqa: E402

TIMEOUT = 20


def fetch(url: str) -> str:
    # A cache-buster, because the point of this check is to see the deploy that just
    # happened rather than whatever an edge is still holding.
    separator = "&" if "?" in url else "?"
    request = urllib.request.Request(
        f"{url}{separator}cb={uuid.uuid4().hex}",
        headers={"User-Agent": "galinstan-release-verifier", "Cache-Control": "no-cache"},
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
        return response.read().decode("utf-8", errors="replace")


# What must appear in each page's body, keyed by path. The page escapes as it renders, so
# these are distinctive fragments rather than whole sentences with their punctuation.
#
# Per page rather than one fragment for the whole site, because the first version asserted
# the front page's headline on every URL — so /privacy.html failed a check it could never
# have passed. It was caught on a preview deploy, which is the argument for running one.
EXPECTED = {
    "/": ("headline", "runs inside your perimeter, not ours"),
    "/index.html": ("headline", "runs inside your perimeter, not ours"),
    "/privacy.html": ("privacy-controller", "The data controller for this site is"),
}

# Rewrites the edge performs on the response, which no build-time guard can see because
# they happen after the build. Each entry is a marker that must NOT appear, and the reason.
#
# This list exists because Cloudflare's Email Address Obfuscation silently replaced the
# approved contact address with "[email protected]" on the first production release.
# The page still looked right in a browser, because a script decoded it — but an approved
# string was not what was served, and the pre-filled subject line that carries the site's
# only source attribution had become dependent on JavaScript running.
FORBIDDEN_MARKERS = [
    ("__cf_email__", "Cloudflare Email Address Obfuscation is rewriting the contact address"),
    ("/cdn-cgi/l/email-protection", "the same, in the href"),
    ("[email\u00a0protected]", "the same, in the visible text"),
]


def _path_of(url: str) -> str:
    from urllib.parse import urlparse

    return urlparse(url).path or "/"


def verify(url: str) -> list[str]:
    body = fetch(url)
    failures = guards.live_response_has_only_permitted_fetches(url, body)

    path = _path_of(url)
    expected = EXPECTED.get(path)
    if expected is None:
        # Silence here would mean a page could be verified by accident. A path nobody has
        # said what to expect from is not a passing page, it is an unchecked one.
        failures.append(f"{url}: no expected content is recorded for {path!r}")
        return failures

    for marker, why in FORBIDDEN_MARKERS:
        if marker in body:
            failures.append(f"{url}: {why} (found {marker!r})")

    # The contact address and its subject are the whole of the site's source attribution
    # at stage 1, so they are checked on every page that carries them rather than left to
    # the per-page expectation below.
    address = page_copy.text("contact")
    if address in body and "mailto:" + address not in body:
        failures.append(f"{url}: the contact address is present but not as a mail link")
    if "mailto:" + address in body and "subject=" not in body:
        failures.append(f"{url}: the contact link has lost its pre-filled subject")

    line_id, fragment = expected
    if fragment not in body:
        failures.append(f"{url}: the approved {line_id} text is not in the body")
    # The fragment is a quotation from an approved string. If the string is reworded and
    # this is not, the check would quietly start testing nothing.
    assert fragment in page_copy.line(line_id).text, (
        f"the fragment this check greps for is no longer in the approved {line_id!r} string"
    )
    return failures


def main() -> int:
    urls = sys.argv[1:] or ["https://galinstan.ai/"]
    failed = 0
    for url in urls:
        try:
            failures = verify(url)
        except Exception as exc:  # a fetch that does not complete is a failed release
            print(f"FAIL  {url}\n        {type(exc).__name__}: {exc}")
            failed += 1
            continue
        if failures:
            failed += 1
            print(f"FAIL  {url}")
            for f in failures:
                print(f"        {f}")
        else:
            label = EXPECTED.get(_path_of(url), ("content", ""))[0]
            print(f"ok    {url} — approved {label} present, no unexpected third-party host")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
