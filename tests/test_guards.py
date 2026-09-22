"""Tests for the site build and its guards. Standard library only — `python3 -m unittest`.

Zero dependencies is deliberate. The practice runs 268 headless tests with none
(`50_Claude_Outputs/METHOD_FROM_JJ.md` section 5), and a test suite that needs an install
is a test suite that does not run on the machine where the mistake is being made.

Every guard is tested in both directions: a page that should pass, and a page that should
fail. *"Counting the absence of something is not a test until you have confirmed the thing
ran."*
"""

import dataclasses
import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import build  # noqa: E402
import page_copy  # noqa: E402
from tools import guards  # noqa: E402


class BuildTests(unittest.TestCase):
    def test_every_allowlisted_file_renders(self):
        for name, render in build.ALLOWLIST.items():
            with self.subTest(name=name):
                self.assertTrue(render().strip(), f"{name} rendered empty")

    def test_public_matches_a_fresh_build(self):
        """CI fails if a generated file differs from what is committed."""
        for name, render in build.ALLOWLIST.items():
            with self.subTest(name=name):
                committed = (ROOT / "public" / name).read_text(encoding="utf-8")
                self.assertEqual(
                    committed,
                    render(),
                    f"public/{name} is stale. Run python3 build.py and commit the result.",
                )

    def test_the_sitemap_dates_a_page_by_its_copy_and_not_by_the_clock(self):
        """`lastmod` was `date.today()`, so the committed build went stale at midnight
        UTC and CI failed a pull request that had changed nothing on the page."""
        approved = {item.approved_on for item in page_copy.LINES if item.approved_on}
        stamped = re.findall(r"<lastmod>([^<]+)</lastmod>", build.render_sitemap())
        self.assertTrue(stamped, "the sitemap carried no lastmod at all")
        for stamp in stamped:
            self.assertIn(stamp, approved, "a lastmod no string in the register accounts for")

    def test_the_sitemap_follows_the_register_when_a_string_is_re_approved(self):
        """The other direction: the date has to move when the copy's approval moves,
        or the test above would pass just as well on a constant."""
        before = re.findall(r"<lastmod>([^<]+)</lastmod>", build.render_sitemap())
        headline = page_copy.BY_ID["headline"]
        page_copy.BY_ID["headline"] = dataclasses.replace(headline, approved_on="2027-01-01")
        try:
            after = re.findall(r"<lastmod>([^<]+)</lastmod>", build.render_sitemap())
        finally:
            page_copy.BY_ID["headline"] = headline
        self.assertNotEqual(before, after)
        self.assertEqual(after[0], "2027-01-01", "the front page ignored its own copy")

    def test_public_holds_nothing_the_allowlist_does_not_name(self):
        """Deploy an allowlist, not the checkout."""
        actual = {p.name for p in (ROOT / "public").iterdir()}
        self.assertEqual(actual, set(build.ALLOWLIST))

    def test_the_approved_headline_ships_verbatim(self):
        headline = page_copy.line("headline")
        self.assertEqual(headline.status, page_copy.APPROVED)
        self.assertIn(
            headline.text.replace("&", "&amp;"),
            (ROOT / "public" / "index.html").read_text(encoding="utf-8"),
        )

    def test_a_placeholder_would_render_as_a_marker_and_never_as_a_blank(self):
        """No placeholders remain, so this checks the mechanism rather than the page."""
        probe = page_copy.Line(id="probe", status=page_copy.PLACEHOLDER, text="", note="a fact nobody supplied")
        page_copy.BY_ID["probe"] = probe
        try:
            self.assertTrue(page_copy.text("probe").startswith("[[TODO:"))
        finally:
            del page_copy.BY_ID["probe"]

    def test_the_page_carries_no_placeholder_markers(self):
        self.assertNotIn("[[TODO:", (ROOT / "public" / "index.html").read_text("utf-8"))

    def test_the_contact_address_is_a_mail_link_with_the_approved_subject(self):
        """The pre-filled subject is the whole of the site's source attribution."""
        body = (ROOT / "public" / "index.html").read_text("utf-8")
        self.assertIn("mailto:antwain@banneker.net?subject=", body)
        self.assertIn("via%20galinstan.ai", body)

    def test_the_footer_domain_is_not_invented_into_a_link(self):
        body = (ROOT / "public" / "index.html").read_text("utf-8")
        self.assertIn("banneker.net", body)
        self.assertNotIn('href="https://banneker.net', body)


class GuardsPassOnTheRealBuild(unittest.TestCase):
    def test_no_external_references(self):
        self.assertEqual(guards.no_external_references(), [])

    def test_no_forbidden_claims(self):
        self.assertEqual(guards.no_forbidden_claims(), [])

    def test_required_metadata(self):
        self.assertEqual(guards.required_metadata(), [])


class GuardsFailWhenTheyShould(unittest.TestCase):
    """The other direction. A guard that has never failed has never been shown to run."""

    def test_external_script_is_caught(self):
        page = [("index.html", '<script src="https://cdn.example.com/a.js"></script>')]
        self.assertTrue(guards.no_external_references(page))

    def test_external_stylesheet_is_caught(self):
        page = [("index.html", '<link rel="stylesheet" href="/local.css">')]
        self.assertTrue(guards.no_external_references(page))

    def test_font_cdn_is_caught(self):
        page = [("index.html", "<style>@import url(https://fonts.googleapis.com/x);</style>")]
        self.assertTrue(guards.no_external_references(page))

    def test_absolute_url_to_a_third_party_is_caught(self):
        page = [("index.html", '<a href="https://example.com/x">x</a>')]
        self.assertTrue(guards.no_external_references(page))

    def test_our_own_absolute_url_is_not_caught(self):
        page = [("index.html", '<link rel="canonical" href="https://galinstan.ai/">')]
        self.assertEqual(guards.no_external_references(page), [])

    def test_each_forbidden_claim_is_caught(self):
        samples = {
            "compliant": "Galinstan keeps you compliant.",
            "certified": "An ISO certified platform.",
            "guarantee": "We guarantee the outcome.",
            "audit-ready": "Audit-ready evidence.",
            "Icosa": "Built with Icosa technology.",
            "Zeno": "Runs on Zeno.",
            "demo": "Book a demo today.",
            "quantum": "Quantum optimization for banks.",
            "price": "From €45,000 per engagement.",
            "currency code": "From EUR 45,000 per engagement.",
        }
        for label, text in samples.items():
            with self.subTest(claim=label):
                self.assertTrue(
                    guards.no_forbidden_claims([("index.html", f"<p>{text}</p>")]),
                    f"{label!r} passed the claims guard",
                )

    def test_the_entity_name_no_longer_needs_an_exemption(self):
        """Banneker is a sole proprietorship. The word "Compliance" left the page with it,
        so the exemption that once let it through is gone and the word is banned outright.
        """
        self.assertEqual(guards._LEGAL_NAMES, [])
        page = [("index.html", "<p>Banneker Strategy & Compliance LLC</p>")]
        self.assertTrue(guards.no_forbidden_claims(page))

    def test_missing_metadata_is_caught(self):
        page = [("index.html", "<html><title>x</title></html>")]
        self.assertTrue(guards.required_metadata(page))


class PublicationGate(unittest.TestCase):
    """Updated 2026-09-21, deliberately: all twelve strings were approved.

    The previous version asserted the gate *fails*, and said in its own message that
    approval was the only thing that should change it. That is what happened. The
    mechanism is still tested in both directions — an unapproved string must still
    block, which is what matters when the next page is added.
    """

    def test_the_gate_passes_now_that_every_string_is_approved(self):
        self.assertEqual(guards.publication_gate(), [])

    def test_every_string_carries_the_date_it_was_approved(self):
        for line in page_copy.LINES:
            self.assertEqual(line.status, page_copy.APPROVED, line.id)
            self.assertRegex(line.approved_on, r"^\d{4}-\d{2}-\d{2}$", line.id)

    def test_an_unapproved_string_still_blocks_a_release(self):
        original = page_copy.BY_ID["body-1"]
        replacement = page_copy.Line(id="body-1", status=page_copy.PENDING, text=original.text)
        position = page_copy.LINES.index(original)
        page_copy.LINES[position] = replacement
        page_copy.BY_ID["body-1"] = replacement
        try:
            self.assertTrue(any("body-1" in f for f in guards.publication_gate()))
        finally:
            page_copy.LINES[position] = original
            page_copy.BY_ID["body-1"] = original

    def test_analytics_is_configured(self):
        self.assertIsNotNone(build.ANALYTICS)


class LiveResponseVerification(unittest.TestCase):
    """Guards over what a visitor is served. The beacon is injected after the build."""

    URL = "https://galinstan.ai/"

    def test_the_permitted_beacon_passes_on_a_marketing_path(self):
        body = '<script src="https://static.cloudflareinsights.com/beacon.min.js"></script>'
        self.assertEqual(guards.live_response_has_only_permitted_fetches(self.URL, body), [])

    def test_any_other_third_party_host_fails(self):
        body = '<script src="https://cdn.example.com/a.js"></script>'
        failures = guards.live_response_has_only_permitted_fetches(self.URL, body)
        self.assertTrue(any("cdn.example.com" in f for f in failures))

    def test_a_font_service_fails_even_though_it_is_ordinary(self):
        body = '<link href="https://fonts.googleapis.com/css2?family=X">'
        self.assertTrue(guards.live_response_has_only_permitted_fetches(self.URL, body))

    def test_the_beacon_is_not_permitted_on_an_air_gapped_path(self):
        body = '<script src="https://static.cloudflareinsights.com/beacon.min.js"></script>'
        failures = guards.live_response_has_only_permitted_fetches("https://galinstan.ai/demo", body)
        self.assertTrue(any("air-gapped path" in f for f in failures))

    def test_our_own_host_passes(self):
        body = '<link rel="canonical" href="https://galinstan.ai/">'
        self.assertEqual(guards.live_response_has_only_permitted_fetches(self.URL, body), [])


if __name__ == "__main__":
    unittest.main()


class LiveVerifierExpectations(unittest.TestCase):
    """The live verifier's per-page expectations, checked against the register.

    The first version asserted the front page's headline on every URL, so /privacy.html
    failed a check it could never have passed — and because the deploy workflow passes
    both URLs, a release would have failed on it. Caught on a preview deploy rather than
    on the tag, which is the argument for running one.
    """

    def setUp(self):
        from tools import verify_live

        self.verify_live = verify_live

    def test_every_expectation_quotes_a_string_that_is_still_approved(self):
        for path, (line_id, fragment) in self.verify_live.EXPECTED.items():
            with self.subTest(path=path):
                line = page_copy.line(line_id)
                self.assertEqual(line.status, page_copy.APPROVED)
                self.assertIn(fragment, line.text)

    def test_every_published_html_page_has_an_expectation(self):
        """A page nobody said what to expect from is unchecked, not passing."""
        published = {f"/{n}" for n in build.ALLOWLIST if n.endswith(".html")}
        published.discard("/404.html")  # not fetched by a release; it has no canonical content
        covered = set(self.verify_live.EXPECTED)
        self.assertTrue(published <= covered, f"no expectation for {published - covered}")

    def test_an_unlisted_path_is_reported_rather_than_passing(self):
        self.assertIsNone(self.verify_live.EXPECTED.get("/something-nobody-listed"))
