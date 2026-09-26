# Changelog

Keep a Changelog format. Site releases are date tagged: `site-YYYY.MM.N`.

## [site-2026.09.19] — the product brief addresses banks

### Changed
- **`brief-p-summary-1`** opens "Galinstan is software for banks", previously "software for
  European banks", approved by Antwain 2026-09-26 with the US and EU audience. The PDF is
  reprinted and its lock updated.
- `_brief` takes an approval date, so a revised brief string records its own.

## [site-2026.09.18] — the site addresses US and EU banks

### Changed
- **Four strings revised for a US and EU audience**, approved by Antwain 2026-09-26 (option C in
  `SITE_COPY_STAGE1.md`, "Proposed 2026-09-26"): `headline` ("Air-gapped liquidity optimization and
  audit software for banks. The analysis runs inside your perimeter, not ours."), `body-1` (banks bound
  by a liquidity coverage requirement, including EU and EEA institutions in scope of DORA),
  `il-meta-description` ("a bank") and `meta-title`, "Galinstan: Air-Gapped Liquidity Optimization And
  Audit Software For Banks", in title case as every page title, his choice the same day.
- Figures that describe European banks, such as the Pillar 3 range in `il-body-3`, are unchanged.

## [site-2026.09.17] — titles in title case

### Changed
- **Every page title capitalizes each word**, approved by Antwain 2026-09-25 ("website titles
  should have each word capitalized, not random lowercase words"; the table of new wording
  approved as shown). `meta-title`, `il-meta-title`, `ae-meta-title`, `dep-meta-title`,
  `notfound-meta-title`; `privacy-meta-title` was already one capitalized word.
- **The product brief's title** follows: `brief-meta-title` and `brief-title` read "How
  Galinstan Works" (Antwain, same day). The PDF is reprinted and its lock updated.
- Page headings are sentences and are unchanged.

### Fixed
- The test that proves a brief string changed without reprinting is caught replaced a
  hardcoded copy of the old title, so after this change it replaced nothing and caught
  nothing. It now takes the title from the register.

## [site-2026.09.16] — layout, after a review of lusion.co

No string changes. Every word a visitor reads is the same approved string in the same
register; what changes is how the pages are laid out. Nothing is fetched from anywhere but
galinstan.ai: the additions are CSS and one photograph served from the site itself.

### Added
- **A header that stays at the top while scrolling**, with the wordmark, the nav and a
  `Request a demo` button (`cta-demo`, to the approved `cta-demo-target` with its subject).
- **The three stage 2 pages as cards on the home page.** Titles only, which are the nav
  labels; a line under each would be new copy.
- **The product brief as a panel** on `/`, `/audit-evidence` and `/deployment`, in place of
  a text link. Same string, same address.
- **A hero photograph on the home page**, liquid metal on a machined cube. Served from this
  site as two allowlisted files (`hero-800.jpg`, `hero-1408.jpg`, 44 KB and 120 KB), so it
  adds no third party. `alt=""`: a description read aloud would be copy, and none is approved.
- **Section marks**: a hairline with crosses, drawn by the stylesheet.
- **Motion, all of it CSS and all of it off under `prefers-reduced-motion`**: the browser's
  own cross-fade between pages (`@view-transition`), with the header held still across it,
  and cards and panels rising in as they scroll into view where `animation-timeline` is
  supported.

### Changed
- The `h1` is set in the system sans at a size that scales with the viewport, up to 3.5rem.
  Body text stays serif at the 34rem measure; the page container widens to 64rem around it.

## [site-2026.09.15] — AI may learn about Galinstan, and knows it is software

### Changed
- **`robots.txt` allows training: `ai-train=yes`.** `RULES.md` r11 revised by Antwain on
  2026-09-25: search, live AI answers and training are all allowed, because the site
  carries no IP. Cloudflare's AI bot policy for Training is set to Allow to match.

### Added
- **Structured data on the home page**, approved by Antwain 2026-09-25: a JSON-LD
  SoftwareApplication naming Galinstan, its address, its approved description and its
  publisher, Banneker. "Galinstan" is also a gallium alloy; this tells search and AI answers
  which one the site is. New approved string `ld-publisher`.
- **Guard change, in its own commit:** URLs inside JSON-LD are names, not fetches, so
  schema.org and banneker.net pass there and only there. Four tests. Suite is 65.

## [site-2026.09.14] — the product brief, at /galinstan-brief.pdf

### Added
- **The product brief**, a four-page PDF at `/galinstan-brief.pdf`, approved by Antwain
  2026-09-25 in full. It says what Galinstan does and why, with its published sources, and
  deliberately stops short of the method: "whitepaper" is reserved for the document shared
  under NDA, and the brief does not offer it. Every word is a `brief-` string in
  `src/page_copy.py`.
- Linked from `/`, `/audit-evidence` and `/deployment` as "How Galinstan works: product
  brief (PDF)", and declared in `sitemap.xml`.
- Its contact link carries its own subject, "Galinstan enquiry via the product brief",
  because Cloudflare Web Analytics cannot count a PDF download.
- `tools/make_brief.py` prints the brief's source with a local Chrome and records both
  hashes in `assets/galinstan-brief.lock.json`. The build keeps no dependencies; the PDF is
  committed.
- **Guard: the brief matches its source.** Fails if the strings, the template or the PDF
  change without the others, if the PDF carries an author field (`RULES.md` D5), or if it
  links anywhere but the approved contact. Eight tests. Suite is 61.
- **The live verifier checks the served PDF's bytes** against the lock, and that it is
  served as `application/pdf`.

## [site-2026.09.13] — every string a visitor reads comes from the register

No served byte changes. The pages are identical; what changes is where their strings
live, and therefore whether one can reach a visitor without being approved.

### Added
- **Guard: page prose comes from the register**, approved by Antwain 2026-09-25. Every text
  node in every built page, plus the description a search result shows, must be contained in
  an approved string in `src/page_copy.py`.
- Containment rather than equality, because a `**lead-in**` renders as two text nodes around
  a `<strong>`, so a node is legitimately a fragment of the string that produced it.
- `style` and `script` contents are not prose. Attributes other than the description are
  addresses and markup.
- Five tests, and the runner was broken on a real built page to confirm a non-zero exit.
  Suite is 53.

### Changed
- **Six strings of page prose moved into the register**, all wording unchanged and live since
  `site-2026.09.1`. The `/privacy` labels "Data controller." and "Analytics." fold into their
  approved strings, the convention every stage 2 body line already follows. The privacy `h1`
  reads `privacy-meta-title`. New strings: `privacy-contact-label`, `notfound-h1`,
  `notfound-link`.
- The guard found six. Reading the renderers by eye had found two, which is the argument for
  having it rather than a habit.

### Why this is a release and not housekeeping
- `publishable()` only looks at register strings, so prose outside the register could be
  reworded and go live with no approval gate at all. That was the actual hole. The dash was
  the symptom that revealed it.

## [site-2026.09.12] — D2 asserted over the response

### Added
- **The live verifier checks `RULES.md` D2 on every page it fetches**, approved by Antwain
  2026-09-25. The build guard from `site-2026.09.10` checks the register and the assembled
  pages; this checks what a visitor is actually served.
- The reason is specific rather than theoretical. Cloudflare's Email Address Obfuscation
  rewrote the approved contact address on the first production release, which is why
  `FORBIDDEN_MARKERS` exists. A guard that cannot see the edge cannot speak for the edge.
- Confirmed in both directions against the real production response: clean as served, and
  failing when a dash is put back into the fetched body.

## [site-2026.09.11] — the last two strings into the copy register

Both titles render exactly as they did in `site-2026.09.9`; what changes is where they
come from. One served byte does move: `/privacy` takes `lastmod` `2026-09-25` instead of
`2026-09-22`, because the page now renders a register string approved today. That is
correct rather than incidental, since its title did change today.

### Changed
- **`/privacy` and `/404` titles move into `src/page_copy.py`** as `privacy-meta-title`
  and `notfound-meta-title`, approved by Antwain 2026-09-25. They were hardcoded in
  `build.py`, and being outside the register is how they kept an em dash through every
  copy review. Nothing a visitor sees is now outside the register except the `/404`
  body, which is noted below.
- **Three approvals recorded** (Antwain, 2026-09-25): the `headline`, which closes
  rejected row `r01`, and both mail subjects, which closes `r12`. All three went live in
  `site-2026.09.8` carrying wording he had not yet signed off.

### Known gap
- The `/404` heading and its link text are still hardcoded prose. The dash guard's
  served-page pass covers them for D2, but they are not register strings.

## [site-2026.09.10] — a guard for D2

### Added
- **Guard: no dashes as punctuation**, approved by Antwain 2026-09-25. Enforces `RULES.md` D2,
  which has been a binding row since 2026-09-24 and was broken on the live site for two days
  because nothing checked it.
- Two passes. The copy register, every string's text and mail subject, for em dash, en dash and
  a hyphen with a space on either side. Then the served pages, for em and en dashes only,
  because a spaced hyphen is legitimate in the CSS this build inlines.
- The second pass is the one that matters: the `/privacy` and `/404` titles were not register
  strings, which is how they kept their dashes through every copy review.
- Hyphenated compounds are untouched. air-gapped, on-premise and high-quality are spelling,
  which is the other half of D2.
- Five tests, both directions, and the runner was broken on a real built page to confirm it
  exits non-zero rather than warning. Suite is 48.

## [site-2026.09.9] — two page titles

### Changed
- **`/privacy` is titled "Privacy"** and **`/404` is titled "Not found"** (Antwain, 2026-09-25).
  Neither repeats the product name: the wordmark is already on the page, and a tab that says
  the product twice says it once too often. Both were "Galinstan: …" for one release.
- Still hardcoded in `build.py` rather than held in `src/page_copy.py`. Moving them into the
  register is open, because anything a visitor sees belongs there.

## [site-2026.09.8] — dashes out, reperformance off the pages, claims guard deleted

### Changed
- **No dashes in client-facing copy** (Antwain, 2026-09-23, restated 2026-09-25). Ten strings
  revised so the dash used as punctuation is gone: `headline`, `meta-title`, `dep-body-1`,
  `dep-body-5`, `il-meta-title`, `il-sub`, `il-body-2`, `ae-meta-title`, `ae-h1`, `ae-sub`.
  Both mail subjects lose theirs, so an enquiry now arrives as "Galinstan enquiry via
  galinstan.ai" and a demo request as "Galinstan demo request".
- **Two page titles** that were never in the register, `/privacy` and `/404`, now follow the
  same colon pattern as the approved titles. Cody's wording, not an approved string.
- The live verifier's expected fragments for `/audit-evidence` and `/deployment` follow the
  revised text.
- Hyphenated compounds are untouched: air-gapped, high-quality and on-premise are spelling.

### Removed
- **`il-body-5`, `il-body-6` and `ae-body-1`** (Antwain, 2026-09-23): reperformance is
  demonstrated, not marketed. It is the moment in a demo where a reviewer repeats a run, and
  a page that claims it spends that moment. `ae-body-2` and `ae-body-3` stand.

### Removed
- **Guard: no forbidden claims**, and everything behind it. The word list ("compliant" in
  any form, "certified", "guarantee", "audit-ready", the licensor names, "demo", "quantum"
  and the two price patterns), the legal-name exemption, the demo-route exemption and the
  placeholder stripper that served only this guard. Four tests go with it, so the suite is
  43 rather than 47.
- Deleted on Antwain's instruction of 2026-09-25, restated 2026-09-25 (ask 66). Its own
  commit, which is what `RULES.md` r32 asks of a guard change: on purpose, not to make a
  build pass. Nothing served changes, so this carries no site release on its own.
- **The publication gate stays.** Every string a visitor sees still has to be APPROVED in
  `src/page_copy.py`, and a production deploy still refuses to run while one is not.

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
