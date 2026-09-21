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


def verify(url: str) -> list[str]:
    body = fetch(url)
    failures = guards.live_response_has_only_permitted_fetches(url, body)

    headline = page_copy.line("headline").text
    # The page escapes as it renders, so compare on a distinctive fragment rather than on
    # the whole sentence and its punctuation.
    fragment = "runs inside your perimeter, not ours"
    if fragment not in body:
        failures.append(f"{url}: the approved headline is not in the body")
    assert fragment in headline, "the fragment this check greps for left the approved string"
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
            print(f"ok    {url} — headline present, no unexpected third-party host")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
