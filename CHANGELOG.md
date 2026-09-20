# Changelog

Keep a Changelog format. Site releases are date tagged: `site-YYYY.MM.N`.

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

### Blocked
- **`site-2026.09.1` cannot be cut.** Ten of twelve strings are unapproved, analytics is
  unchosen, and no Cloudflare project exists. The pipeline is finished and proven; the
  release is waiting on decisions, not on work. See `RELEASE.md`.
