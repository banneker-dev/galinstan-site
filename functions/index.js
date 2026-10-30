// The root, and only the root (Cowork's ask 202). Cloudflare Pages Functions, on the free plan.
//
// An explicit address never reaches this. At `/`: the visitor's stored choice, then the country Cloudflare already
// knows. EEA, UK or Switzerland goes to the EU funnel; every other country, and an unknown one, to the US funnel. Nothing
// is stored or logged here. 302 and no-store, so the answer for one visitor is never served to another.
const EUROPE = new Set([
  "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU",
  "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE", // the EU
  "IS", "LI", "NO", // the rest of the EEA
  "GB", "CH",
]);

export function onRequest({ request }) {
  const stored = /(?:^|;\s*)region=(us|eu)(?:;|$)/.exec(request.headers.get("Cookie") || "");
  const region = stored ? stored[1] : EUROPE.has(request.cf && request.cf.country) ? "eu" : "us";
  const target = new URL(request.url);
  target.pathname = `/${region}-banks`;
  target.searchParams.set("region_source", stored ? "stored-choice" : "edge-country");
  return new Response(null, { status: 302, headers: { Location: target.toString(), "Cache-Control": "no-store" } });
}
