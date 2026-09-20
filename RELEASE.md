# Releasing galinstan.ai

Tags are date based: `site-2026.09.1`, then `.2`, `.3` within the month.

## What a release does

1. `build.py --check` — the committed `public/` must match a fresh build.
2. Tests, then guards. Red means no deploy, which is why both run before the deploy step.
3. On a `site-*` tag only: the **production guards**, which fail while any string is
   unapproved or analytics is unconfigured.
4. Deploy `public/` — the allowlist, not the checkout — to Cloudflare Pages.
5. Fetch the live page with a cache-buster and grep the body for the approved headline.
   A status code cannot tell a stale hit from a live one.

## Before the first release can happen

Four things are outstanding, and none of them is work this repository can do.

| # | Outstanding | Whose | Where it is recorded |
|---|---|---|---|
| 1 | Approve the remaining stage 1 copy — nine strings | Antwain | `50_Claude_Outputs/SITE_COPY_STAGE1.md` |
| 2 | The contact route, the legal footer line, and the privacy notice's controller | Antwain | `WEB_SPEC.md` open items 3 and 5 |
| 3 | Analytics: cookieless and banner-free, or GA4 with consent management | Antwain | `WEB_SPEC.md` open item 4 |
| 4 | Decide whether to publish stage 1 now or hold until G3 | Antwain | `CURRENT_STATE.md` open decision 1 |

And three of infrastructure, which are Cody's once the account exists:

- A GitHub repository under an organisation with SSO and 2FA enforced, branch protection,
  and signed commits.
- A Cloudflare Pages project named `galinstan`, with EU data localization enabled, and
  `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` as repository secrets.
- `galinstan.ai` DNS pointed at it.

## Before the first visitor

Not after. None of this backfills, and the practice lost eleven days of event data to
exactly this sequence (`50_Claude_Outputs/METHOD_FROM_JJ.md` section 6).

- [ ] Analytics retention set to the maximum the plan allows.
- [ ] Every custom dimension registered before any event using it fires.
- [ ] Search property created and verified.
- [ ] `sitemap.xml` and an owned `robots.txt` shipped — **done, in the first build.**
- [ ] Source attribution captured on the first form submission, not the hundredth.
