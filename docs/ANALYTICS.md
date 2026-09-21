# Analytics, and the rule it appeared to break

**The short version.** Cloudflare Web Analytics is used. Its beacon is fetched from
`static.cloudflareinsights.com` at page load, which the site's own rule 3 forbade. The rule
was not waived for a vendor — it was scoped to the thing it was actually protecting, and a
second check was added in the place where the old one could not see.

## What happened

Rule 3 of `CLAUDE.md` read: *nothing is fetched at page load.* It was written as a habit —
practising the product's hardest constraint somewhere cheap.

Ask 23 pointed out the collision. Plausible has no free tier, and free-tier only is a
standing decision. Cloudflare Web Analytics is free, cookieless and needs no consent
banner, and it injects its beacon **at the edge**, into the response, after the build has
run. So `public/index.html` contains no reference to it at all.

That is the part worth dwelling on. The build-time guard reads the built files. A beacon
injected after the build is invisible to it. **The guard would have passed while a visitor
was served a page that fetched a third-party script** — and it would have passed just as
happily if Cloudflare had begun injecting something else, or if a future setting added a
second file. The rule was not the weak point. The place it was checked was.

## What the rule says now

Two rules, because there are two different things on this property.

**Marketing paths.** Exactly one third-party host may be fetched, named in
`PERMITTED_BEACON_HOSTS` in `tools/guards.py`. Today that is
`static.cloudflareinsights.com` and nothing else. A second host is a build failure, not a
judgement call. No fonts, no libraries, no embeds, no tag manager.

**Demo paths** (`/demo`, nothing served there yet). Nothing at all, with no exception. This
is the product's constraint, and the reason the two rules are written down separately now
rather than argued about later: the hosted demo instance is the one place where a
convenience added for the marketing site would land inside the claim that cannot be
recovered. The guard fails if the beacon appears on an air-gapped path.

## Where it is checked

- **At build time**, over `public/`, unchanged: no external reference of any kind.
- **After deploy**, over the fetched live response, with a cache-buster:
  `tools/verify_live.py`. Any host that is not ours and not the one permitted beacon fails
  the release. This is the check that can see edge injection, and it is the reason the
  scoping is honest rather than a concession.

## What is given up

Six months of history rather than the maximum retention `WEB_SPEC.md` section 6a asks for,
and no custom events, so no funnel instrumentation and no form attribution.

The mitigation is already in the approved copy: the contact link carries a pre-filled
subject, so every enquiry that comes from the site arrives labelled. That is source
attribution without an analytics product, and it costs nothing.

**What cannot be mitigated is the history window.** Six months is a limit of the free plan,
and by the time it binds, the plan says operations should be covering costs. Search Console
data does not backfill either, which is why creating that property is on the publish-day
checklist rather than a later one.
