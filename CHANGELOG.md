# Changelog

Keep a Changelog format. Site releases are date tagged: `site-YYYY.MM.N`.

## [site-2026.09.2] — the stage 1 holding page

The first release of `galinstan.ai`. Five files, no dependencies, every string approved.

`site-2026.09.1` was cut first and **failed its own signature check on a validly signed
tag** — the check grepped `git verify-tag --raw` for `GOODSIG`, which is a GPG status
token that an SSH signature never emits. It failed closed, so nothing was published, and
the tag is left in place rather than deleted: a release that did not happen is part of the
record. The check now asks two questions instead of one — is there a signature at all, and
is it from a trusted key — and each is exercised in both directions.

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
