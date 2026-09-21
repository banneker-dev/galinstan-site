# Changelog

Keep a Changelog format. Site releases are date tagged: `site-YYYY.MM.N`.

## [site-2026.09.3] — the stage 1 holding page

The first release of `galinstan.ai`. Five files, no dependencies, every string approved.

Two tags were cut before this one and both failed the same step, for different reasons.
Both failed closed; nothing was published either time, and both tags stay in place, because
a release that did not happen is part of the record.

- **`site-2026.09.1`** — the check grepped `git verify-tag --raw` for `GOODSIG`, a GPG
  status token an SSH signature never emits. It could not have passed on any tag this
  project will ever cut.
- **`site-2026.09.2`** — the check was correct and the tag was not there to read.
  `actions/checkout` passes `--no-tags` even at `fetch-depth: 0`, so the annotated tag
  object never reached the runner and a fetch problem was reported as a signing one.

The step now distinguishes three states — object missing, lightweight tag, annotated tag —
so a checkout problem can never again be read as an unsigned tag, and it fetches the tag
explicitly rather than trusting an action default that has already changed once. The whole
block was run against a clone made with `--no-tags`, which is the condition the runner is
actually in.

## [Unreleased]

### Added
- The stage 1 holding page, built from the copy register in `src/page_copy.py`.
- `build.py`: assembles `public/` from an allowlist; `--check` fails on a stale tree.
- Guards that fail the build: no external references, no forbidden claims, required
  metadata, and a production-only publication gate.
- 19 standard-library tests, each guard exercised in both directions.
- CI on every branch; preview deploys on `main`, `feat/**`, `fix/**`, `chore/**`;
  production deploy on a `site-*` tag, gated on the production guards.
- `robots.txt` and `sitemap.xml`, owned from the first release rather than the 54th.

### Changed — 2026-09-21
- **All twelve strings approved** and promoted in the register, with the dates recorded.
  `body-2` no longer claims there is no register entry to add: a licence sold with ongoing
  support can itself be an ICT service under DORA. `body-3` no longer claims discovery is
  under way. The entity is Banneker, a sole proprietorship.
- The contact address renders as a mail link with the approved subject pre-filled, which is
  the whole of the site's source attribution at stage 1.
- **Analytics: Cloudflare Web Analytics.** Its beacon is injected at the edge, so the
  build-time guard cannot see it. The rule was scoped rather than waived, and
  `tools/verify_live.py` now checks the live response instead. See `docs/ANALYTICS.md`.
- **A release tag deploys to `production`, not `main`.** Previously a tag and a push to
  `main` landed on the same Cloudflare branch, so with `main` as the production branch an
  ordinary push would have reached the live domain without passing the production guards.
- **Release tags must carry a valid SSH signature** from a key in `.github/allowed_signers`.
  The file is a placeholder and fails the release deliberately until the key exists.
- The `Banneker Strategy & Compliance LLC` exemption is removed from the claims guard. That
  entity does not exist, and "compliance" is now banned outright.

### Blocked
- **`site-2026.09.1` cannot be cut yet**, and no longer for any reason inside this
  repository: the GitHub organisation, the Cloudflare project, the signing key and the DNS
  move are all outstanding. See `RELEASE.md`.
