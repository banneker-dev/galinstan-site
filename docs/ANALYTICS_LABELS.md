# Asset labels for galinstan.ai

Spot's ask of 2026-10-30 (`CODY_ASK_GOOGLE_ANALYTICS_LABELS_2026-10-30.md`): Cody defines the labels, Cowork applies
the tags. Every label is an attribute on the page, set by `build.py` (`PAGE_LABELS`, `asset_attrs`) and pinned by
`tests/test_guards.py` (`AssetLabels`). The labels send, store and fetch nothing. Every parameter value is a canonical
path, a track (`us`, `eu`) or an action; none names a visitor, a session or a bank.

## Pages

A tag reads the page's label from `<body data-asset="…" data-asset-region="…" data-page="…">` and sends it with the
page view as `asset_label`, `site_region` and `page_path`.

| Label | Region | Canonical URL |
|---|---|---|
| `home` | `all` | https://galinstan.ai/ |
| `us-track` | `us` | https://galinstan.ai/us-banks |
| `us-intraday-liquidity` | `us` | https://galinstan.ai/us-banks/intraday-liquidity |
| `us-audit-evidence` | `us` | https://galinstan.ai/us-banks/audit-evidence |
| `eu-track` | `eu` | https://galinstan.ai/eu-banks |
| `eu-intraday-liquidity` | `eu` | https://galinstan.ai/intraday-liquidity |
| `eu-audit-evidence` | `eu` | https://galinstan.ai/audit-evidence |
| `deployment` | `shared` | https://galinstan.ai/deployment |
| `privacy` | `shared` | https://galinstan.ai/privacy |

## Clicks and the banner

A tag listens for clicks on elements with `data-event`, and sends that event with `asset_label` from `data-asset` and
every other `data-*` parameter on the element, `-` read as `_`.

| Label | Event | Parameters | Where |
|---|---|---|---|
| `home-door-us` | `door_click` | `destination_track=us`, `source_page=/` | `/` |
| `home-door-eu` | `door_click` | `destination_track=eu`, `source_page=/` | `/` |
| `switcher-to-us` | `region_switch` | `destination_track=us`, `source_page=<this page's path>` | every page |
| `switcher-to-eu` | `region_switch` | `destination_track=eu`, `source_page=<this page's path>` | every page |
| `root-banner-view` | `region_banner` | `banner_action=view`, `source_page=/` | `/`, when the banner is shown |
| `root-banner-click` | `region_banner` | `banner_action=click`, `destination_track=us`, `source_page=/` | `/` |
| `root-banner-dismiss` | `region_banner` | `banner_action=dismiss`, `source_page=/` | `/` |
| `demo-request-header` | `demo_request_click` | `landing_page=<this page's path>` | every page's header |
| `demo-request-body` | `demo_request_click` | `landing_page=<this page's path>` | the call to action in the page |

`demo_request_click` is the one to mark as the key event.

**The banner's view is the one asset a click cannot show.** When the banner is shown, the page dispatches
`galinstan:asset` on `document`, with `detail` `{event: "region_banner", asset: "root-banner-view",
banner_action: "view", source_page: "/"}`. A tag listens for it; without one, nothing happens.

**The demo-request link opens the visitor's own mail client.** It carries no form and no address, so the parameter is
the landing page only.
