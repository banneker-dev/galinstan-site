# Changelog

Keep a Changelog format. Site releases are date tagged: `site-YYYY.MM.N`.

## [site-2026.09.7] — the disclaimer off the footer

Antwain's copy decisions of 2026-09-25, the first two parts of ask 66 in
`00_Start_Here/CURRENT_STATE.md`. The third part of that ask is not in this release.

### Changed
- **`foot-claim`** loses its first sentence, "We do not certify that any institution meets a
  regulatory obligation." The string is now "Galinstan is built to run inside your perimeter
  and produce evidence." A footer carries a tagline, the entity and the legal links.

### Removed
- **`ae-body-4`.** `/audit-evidence` ends at `ae-body-3` and its "Request a demo" link.

## [site-2026.09.6] — two sentences out of `/deployment`

### Changed
- **`dep-body-2`** drops the sentence on sizing against named machines, measuring on the
  machine and publishing the specification. None of it exists before Gate B.
- **`dep-body-3`** drops the sentences on how supervisory guidance treats a licence with
  support and on the register entry. "None of your data reaches us" now begins its
  sentence, and that capital is the only change beyond the cut.
- Both are Antwain's revisions of 2026-09-22.

## [site-2026.09.5] — stage 2, the demo route, and partners@

Three pages, a nav and a footer line (ask 54), and the demo route and address change
(ask 47), on Antwain's approvals of 2026-09-22. Stage 2 was to be coined at G3; his
approval supersedes that.

### Added
- **`/intraday-liquidity`, `/audit-evidence`, `/deployment`**, in that nav order, each with
  its "Request a demo" link and the `foot-claim` line. The 34 strings are parsed from
  `SITE_COPY_STAGE2.md` §2 rather than retyped.
- **"Request a demo"** on the front page, a mail link to `partners@banneker.net` with the
  subject "Galinstan — demo request". No form; the privacy notice does not change.
- **Guard: mail targets carry their subjects** (Round 9, ask 47). Every approved mail
  target must be served with its subject, and every served `mailto:` must be approved.
  The live verifier makes the same assertion over the response.
- The live verifier takes an origin and checks **every declared address**; the deploy
  passes the origin, so a page added to the sitemap is verified without editing the
  workflow.

### Changed
- **`partners@banneker.net` replaces `antwain@banneker.net`** in `contact` and
  `privacy-controller` — an alias onto the same monitored mailbox, which delivered a test
  message on 2026-09-22 (A10). The contact subject, the site's source attribution, is
  unchanged.
- `body-1` and `meta-description` take the "Galinstan is built to…" tense.
- **The claims guard lets the approved demo route through, and nothing else** — in its own
  commit. "Request a demo" invites a request; any other use of the word still fails.
- Pages, canonicals and required metadata are derived from the allowlist and the sitemap.

## [site-2026.09.4] — one address per page, and a crawler policy

Everything a crawler is told, in one release, so the property presents one new state
rather than three.

### Fixed
- **The sitemap declares `/privacy`, not `/privacy.html`.** Cloudflare Pages serves the
  file at `/privacy` and permanently redirects the `.html` form to it, so the one URL the
  site explicitly declared was the one URL that could not be indexed, and the page that
  was indexed had never been declared.
- **The privacy page's canonical is self-referencing.** It named `/privacy.html` while
  being served at `/privacy`; a canonical that redirects elsewhere is one a crawler
  discards in favour of its own choice.
- **The footer links to `/privacy`**, so no visitor takes a redirect hop.
- **`tools/verify_live.py` no longer follows redirects.** `urlopen` followed the 308 in
  silence, landed on the served page, found the approved string and reported success —
  correct about the bytes and wrong about the address, which is the one thing the sitemap
  needed it to check. A 3xx on a declared address is now a failed release.

### Added
- **The crawler policy is a committed file.** `robots.txt` carries
  `Content-Signal: search=yes, ai-input=yes, ai-train=no` inside the `User-agent: *`
  group, expressing decision 13 — present, not trained on. Content signals are advisory,
  so Cloudflare's AI Crawl Control blocks the training category as well; the managed
  `robots.txt` stays off so the policy has one home.
- **Two guards.** *declared addresses agree* fails when a canonical, a sitemap entry or an
  internal link names an address the build does not declare. *crawler policy* fails when
  the signal is missing from `robots.txt`, or sits outside the group it applies to.
- **The live verifier checks the policy in the response**, not just in the repository: the
  signal must be present, and the served file must match the committed one. A file that is
  right in the repository says nothing about what a crawler was handed — the edge prepends
  to this file if either of two Cloudflare features is on.
- Nine tests, each new guard exercised in both directions.

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
