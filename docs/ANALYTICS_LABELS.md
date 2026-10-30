# Asset labels for galinstan.ai

Spot's ask of 2026-10-30 (`CODY_ASK_GOOGLE_ANALYTICS_LABELS_2026-10-30.md`), revised by Cowork's ask 202 (Option C): Cody
defines the labels, Cowork applies the tags through Zaraz. Every label is an attribute on the page, set by `build.py`
(`PAGE_LABELS`, `asset_attrs`) and pinned by `tests/test_guards.py` (`AssetLabels`). The labels send and fetch nothing.
Every parameter value is a canonical path, a region (`us`, `eu`) or a fixed word; none names a visitor, a session or a bank.

**Retired:** `home`, `deployment`, `home-door-us`, `home-door-eu`, `root-banner-*`, `switcher-to-*`, and the banner's
`galinstan:asset` event.

## Pages

A tag reads the page's label from `<body data-asset="…" data-asset-region="…" data-page="…" data-region-served="…">` and
sends it with the page view as `asset_label`, `site_region`, `page_path` and `region_served`. The privacy page belongs to
neither funnel and has no `data-region-served`.

| Label | Region served | Canonical URL |
|---|---|---|
| `us-track` | `us` | https://galinstan.ai/us-banks |
| `us-intraday-liquidity` | `us` | https://galinstan.ai/us-banks/intraday-liquidity |
| `us-audit-evidence` | `us` | https://galinstan.ai/us-banks/audit-evidence |
| `us-deployment` | `us` | https://galinstan.ai/us-banks/deployment |
| `eu-track` | `eu` | https://galinstan.ai/eu-banks |
| `eu-intraday-liquidity` | `eu` | https://galinstan.ai/eu-banks/intraday-liquidity |
| `eu-audit-evidence` | `eu` | https://galinstan.ai/eu-banks/audit-evidence |
| `eu-deployment` | `eu` | https://galinstan.ai/eu-banks/deployment |
| `privacy` | none | https://galinstan.ai/privacy |

**`region_source`, on the first page of a visit only.** The page sets `data-region-source` on `<body>` when it loads, so a
tag reads it after that:

| Value | Meaning |
|---|---|
| `edge-country` | The visitor came through `/`, and the edge chose by country |
| `stored-choice` | The visitor came through `/`, and the edge used the `region` cookie |
| `explicit-url` | The visitor came straight to an address |

The edge passes the first two in the address as `region_source`, and the page removes it at once, so a tag should read the
attribute and not the address. "A visit" is the browser tab's `sessionStorage`.

## Clicks

A tag listens for clicks on elements with `data-event`, and sends that event with `asset_label` from `data-asset` and
every other `data-*` parameter on the element, `-` read as `_`.

| Label | Event | Parameters | Where |
|---|---|---|---|
| `region-change-to-eu` | `region_switch` | `destination_track=eu`, `source_page=<this page's path>` | every US page |
| `region-change-to-us` | `region_switch` | `destination_track=us`, `source_page=<this page's path>` | every EU page |
| `demo-request-header` | `demo_request_click` | `landing_page=<this page's path>` | every page's header |
| `demo-request-body` | `demo_request_click` | `landing_page=<this page's path>` | the call to action in the page |

`demo_request_click` is the one to mark as the key event.

**The demo-request link opens the visitor's own mail client.** It carries no form and no address, so the parameter is
the landing page only.
