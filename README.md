# galinstan.ai

The marketing site for Galinstan, and later the host for the Module 1 demo instance.
Separate from the product repository on purpose: the product repo becomes
escrow-deposited and diligence-inspected, and the two need opposite cadences.

Specification: `50_Claude_Outputs/WEB_SPEC.md` in the Galinstan drive.
What exists and what is decided: `00_Start_Here/CURRENT_STATE_REPO.md`.

## Build

```
python3 build.py            # writes public/
python3 build.py --check    # fails if public/ is stale
python3 tools/guards.py     # the guards CI runs on every push
python3 -m unittest discover -s tests
```

No dependencies. No package manager. No `node_modules`. Python 3.12 and the standard
library, which is what CI installs and what the site's whole toolchain consists of.

## The two things to understand before changing anything

**Copy lives in `src/page_copy.py`, with a status and the date it was approved.** Nothing
else in this repository may contain page prose. A string is `approved`, `pending` or
`placeholder`, and only `approved` may reach production. This is not bureaucracy: approved strings are the
scarce input in this venture, and a session that invents one to fill a gap is the failure
mode the practice has already paid for.

**`public/` is assembled, not published.** `build.py` names every file that may reach the
web. The deploy publishes `public/` and nothing else, so adding a file to the repository
does not put it on the internet.

## Status

**Publishable.** All twelve strings were approved on 2026-09-21 and the analytics choice is
made, so `python3 tools/guards.py --production` passes and a `site-*` tag would deploy.

What is left is not copy and not code: the GitHub organisation, the Cloudflare Pages
project, the signing key and the DNS move. `RELEASE.md` lists them, and
`50_Claude_Outputs/SETUP_GITHUB_CLOUDFLARE.md` walks through each one field by field.

The gate itself stays. The next page added starts unapproved, and stage 2 copy has to come
from what discovery finds rather than from what we currently assume.
