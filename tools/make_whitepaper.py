#!/usr/bin/env python3
"""Prints the whitepaper's source to `assets/whitepaper.pdf` and records both hashes.

Run on a Mac with Google Chrome installed, after any change to a `wp-` string in the
copy register or to the whitepaper template in `build.py`:

    python3 tools/make_whitepaper.py
    python3 build.py

It is a local tool, not a build step: the site build has no dependencies, and a browser
engine is one. CI never runs it. CI runs the guard that checks its output, which is
`whitepaper_matches_its_source` in `tools/guards.py`.

The source is printed from a file in a temporary directory, with no network: every
word and style is inline and the font is the machine's own (Charter, whose embedding
permission is preview and print), so there is nothing for Chrome to fetch.
"""

import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import build  # noqa: E402

CHROME = pathlib.Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    if not CHROME.exists():
        print(f"Google Chrome is not at {CHROME}", file=sys.stderr)
        return 1
    source = build.render_whitepaper_source()
    build.ASSETS.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        page = pathlib.Path(tmp) / "whitepaper.html"
        page.write_text(source, encoding="utf-8")
        out = pathlib.Path(tmp) / "whitepaper.pdf"
        # Headless Chrome on macOS writes the PDF and then does not always exit, so the
        # file is watched rather than the process: once Chrome reports the bytes written
        # and the size stops changing, it is stopped.
        chrome = subprocess.Popen(
            [
                str(CHROME),
                "--headless",
                "--disable-gpu",
                "--no-pdf-header-footer",
                "--generate-pdf-document-outline",
                f"--user-data-dir={tmp}/profile",
                f"--print-to-pdf={out}",
                page.as_uri(),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            last, deadline = -1, time.monotonic() + 120
            while time.monotonic() < deadline:
                size = out.stat().st_size if out.exists() else -1
                if size > 0 and size == last:
                    break
                if chrome.poll() is not None and size <= 0:
                    print("Chrome exited without writing the PDF", file=sys.stderr)
                    return 1
                last = size
                time.sleep(1)
            else:
                print("Chrome did not write the PDF within 120 s", file=sys.stderr)
                return 1
        finally:
            if chrome.poll() is None:
                chrome.terminate()
                chrome.wait(timeout=10)
        pdf = out.read_bytes()
    build.WHITEPAPER_PDF.write_bytes(pdf)
    lock = {
        "source_sha256": sha256(source.encode("utf-8")),
        "pdf_sha256": sha256(pdf),
        "printed_with": subprocess.run(
            [str(CHROME), "--version"], check=True, capture_output=True, text=True
        ).stdout.strip(),
    }
    build.WHITEPAPER_LOCK.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {build.WHITEPAPER_PDF.relative_to(ROOT)} ({len(pdf):,} bytes)")
    print(f"Wrote {build.WHITEPAPER_LOCK.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
