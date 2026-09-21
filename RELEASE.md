# Releasing galinstan.ai

Tags are date based: `site-2026.09.1`, then `.2`, `.3` within the month.

## What a release does

1. `build.py --check` — the committed `public/` must match a fresh build.
2. Tests, then guards. Red means no deploy, which is why both run before the deploy step.
3. On a `site-*` tag only: **the tag must carry a valid SSH signature** from a key listed
   in `.github/allowed_signers`, and the **production guards** must pass.
4. Deploy `public/` — the allowlist, not the checkout — to Cloudflare Pages. A tag deploys
   to the `production` branch; every branch push, `main` included, deploys to a branch of
   its own name and is therefore a preview.
5. `tools/verify_live.py` fetches the live pages with a cache-buster and checks two things:
   the approved headline is in the body, and no third-party host is fetched except the one
   permitted analytics beacon. A status code cannot tell a stale hit from a live one, and
   a build-time guard cannot see what the edge injects afterwards.

## Before the first release can happen

| # | Outstanding | Whose |
|---|---|---|
| 1 | ~~Approve the stage 1 copy~~ | **Done 2026-09-21. All twelve strings approved.** |
| 2 | ~~Analytics choice~~ | **Done. Cloudflare Web Analytics.** See `docs/ANALYTICS.md` |
| 3 | ~~Publish now or hold~~ | **Done. The page publishes independent of the interviews.** |
| 4 | ~~The GitHub org, the repo, and the Cloudflare project — A5 and A7~~ | **Done 2026-09-21** |
| 5 | ~~The SSH signing key~~ | **Done 2026-09-21** |
| 6 | ~~`galinstan.ai` nameservers moved, custom domain attached~~ | **Done 2026-09-21** |
| 7 | **Two repository secrets, named exactly `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`** | Antwain |

**Secret names are not cosmetic.** The workflow reads those two names and no others. A secret carrying the
token under a different name is the same as no secret at all — and until this was hardened, the release
would have skipped the deploy, skipped the live verification, and reported success. A tag now fails on
missing credentials; only a branch preview is allowed to no-op.

Steps 4 to 6 are written out field by field in `50_Claude_Outputs/SETUP_GITHUB_CLOUDFLARE.md`.

**Note on what the domain serves today.** `galinstan.ai` currently returns a Squarespace
"Coming Soon" page, which pulls Google Fonts. So the domain is not silently parked — there
is a live page on it now, and the nameserver move in A7 step 2.2 replaces it. Worth knowing
before the switch rather than during it.

## Before the first visitor

Not after. None of this backfills.

- [ ] Cloudflare Web Analytics added for the hostname. Six months of history is the free
      plan's limit and cannot be raised — recorded rather than worked around.
- [ ] Search property created and verified. It does not backfill.
- [x] `sitemap.xml` and an owned `robots.txt` — shipped in the first build.
- [x] Source attribution on every enquiry — the contact link carries a pre-filled subject,
      so every mail from the site arrives labelled. No form, no CRM, nothing to pay for.
- [ ] Sitemap submitted to the search property.

## Free-plan limits, recorded so nobody expects otherwise

- **No custom events and no form attribution.** Page views only.
- **Six months of analytics history.**
- **No EU data localization.** It is a Cloudflare Enterprise feature. An earlier version of
  this file listed it as a setup step, which was wrong. The site stores no visitor data of
  its own, so at stage 1 this costs little — but it is a real answer owed to a diligence
  question later, not a resolved one.
- **Branch protection on the site repo only**, because GitHub Free enforces it on public
  repositories. The site repo is public; the product repo is private and is protected by
  its CI guards instead.
