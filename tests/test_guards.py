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
from tools import verify_live  # noqa: E402


class BuildTests(unittest.TestCase):
    def test_every_allowlisted_file_renders(self):
        for name, render in build.ALLOWLIST.items():
            with self.subTest(name=name):
                self.assertTrue(render().strip(), f"{name} rendered empty")

    def test_public_matches_a_fresh_build(self):
        """CI fails if a generated file differs from what is committed."""
        for name, render in build.ALLOWLIST.items():
            with self.subTest(name=name):
                built = render()
                path = ROOT / "public" / name
                committed = path.read_bytes() if isinstance(built, bytes) else path.read_text(encoding="utf-8")
                self.assertEqual(
                    committed,
                    built,
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
        self.assertIn("mailto:partners@banneker.net?subject=", body)
        self.assertIn("via%20galinstan.ai", body)
        self.assertNotIn("antwain@banneker.net", body, "the retired address is still served")

    def test_the_footer_domain_is_not_invented_into_a_link(self):
        body = (ROOT / "public" / "index.html").read_text("utf-8")
        self.assertIn("banneker.net", body)
        self.assertNotIn('href="https://banneker.net', body)


class GuardsPassOnTheRealBuild(unittest.TestCase):
    def test_no_external_references(self):
        self.assertEqual(guards.no_external_references(), [])

    def test_no_dashes_as_punctuation(self):
        self.assertEqual(guards.no_dashes_as_punctuation(), [])

    def test_page_prose_comes_from_the_register(self):
        self.assertEqual(guards.page_prose_comes_from_the_register(), [])

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

    def test_each_dash_as_punctuation_is_caught(self):
        """RULES.md D2. Every sample is a string this site actually served."""
        samples = {
            "em dash in the old headline": "European banks \u2014 the analysis runs inside your perimeter",
            "em dash in the old privacy title": "Privacy \u2014 Galinstan",
            "en dash": "Tier A \u2013 Tier B",
            "spaced hyphen": "inside your perimeter - not ours",
            "hyphen opening a clause": "no outbound connection -not for licensing",
            "hyphen closing a clause": "no outbound connection- not for licensing",
        }
        for label, text in samples.items():
            with self.subTest(dash=label):
                self.assertTrue(
                    guards._LOOSE_HYPHEN.search(text)
                    or any(ch in text for ch, _ in guards._DASH_AS_PUNCTUATION),
                    f"{label!r} passed the dash guard",
                )

    def test_hyphenated_compounds_are_spelling_and_pass(self):
        """The other half of D2: hyphenated compounds are fine."""
        for text in (
            "Air-gapped, on-premise, high-quality liquid assets.",
            "Air-gapped optimization and audit software for European banks.",
            "air-gapped",
        ):
            with self.subTest(text=text):
                self.assertFalse(guards._LOOSE_HYPHEN.search(text))
                self.assertFalse(any(ch in text for ch, _ in guards._DASH_AS_PUNCTUATION))

    def test_a_dash_in_a_page_outside_the_copy_register_is_caught(self):
        """The half that matters. The /privacy and /404 titles were never register strings,
        which is how they kept their dashes through every copy review.
        """
        page = [("privacy.html", "<title>Privacy \u2014 Galinstan</title>")]
        self.assertTrue(guards.no_dashes_as_punctuation(page))

    def test_css_arithmetic_is_not_a_dash(self):
        """Why the served-page pass is limited to real dashes: the build inlines CSS."""
        page = [("index.html", "<style>main { width: calc(100% - 2rem); margin: -1.5rem 0; }</style>")]
        self.assertEqual(guards.no_dashes_as_punctuation(page), [])

    def test_prose_invented_in_the_renderer_is_caught(self):
        """The whole point. Six strings sat in build.py until this guard existed, and two of
        them carried an em dash through every copy review by not being register strings.
        """
        page = [("404.html", "<h1>That page does not exist.</h1>")]
        self.assertEqual(guards.page_prose_comes_from_the_register(page), [])
        invented = [("404.html", "<h1>Sorry, we could not find that.</h1>")]
        self.assertTrue(guards.page_prose_comes_from_the_register(invented))

    def test_a_fragment_of_an_approved_string_passes(self):
        """A `**lead-in**` renders as two text nodes around a <strong>, so a node is
        legitimately a fragment rather than a whole string.
        """
        page = [("deployment.html", "<p><strong>What leaves.</strong> Nothing, by design.</p>")]
        self.assertEqual(guards.page_prose_comes_from_the_register(page), [])

    def test_css_and_script_are_not_prose(self):
        page = [("index.html", "<style>body { font-family: Georgia; }</style>"
                               "<script>const x = 'not copy';</script>")]
        self.assertEqual(guards.page_prose_comes_from_the_register(page), [])

    def test_a_search_description_is_prose(self):
        """It is what a search result shows, so it is read by a visitor like any other string."""
        page = [("index.html", '<meta name="description" content="Invented by a renderer.">')]
        self.assertTrue(guards.page_prose_comes_from_the_register(page))

    def test_missing_metadata_is_caught(self):
        page = [("index.html", "<html><title>x</title></html>")]
        self.assertTrue(guards.required_metadata(page))


class DeclaredAddresses(unittest.TestCase):
    """One address per page, in the sitemap, the canonical and every internal link.

    The host serves `privacy.html` at `/privacy` and redirects the `.html` form to it, so
    the first release declared a URL that could not be indexed and indexed a URL it had
    never declared. None of that was visible from the build.
    """

    def test_the_real_build_agrees_with_itself(self):
        self.assertEqual(guards.declared_addresses_agree(), [])

    def test_a_canonical_pointing_somewhere_else_is_caught(self):
        page = build.render_privacy().replace(
            f'rel="canonical" href="{build.SITE_URL}/privacy"',
            f'rel="canonical" href="{build.SITE_URL}/privacy.html"',
        )
        failures = guards.declared_addresses_agree(pages=[("privacy.html", page)])
        self.assertTrue(any("canonical" in f for f in failures), failures)

    def test_a_link_to_the_redirecting_form_is_caught(self):
        page = build.render_index().replace('href="/privacy"', 'href="/privacy.html"')
        failures = guards.declared_addresses_agree(pages=[("index.html", page)])
        self.assertTrue(any("redirects" in f for f in failures), failures)

    def test_an_undeclared_url_in_the_sitemap_is_caught(self):
        sitemap = build.render_sitemap().replace(f"{build.SITE_URL}/privacy", f"{build.SITE_URL}/privacy.html")
        failures = guards.declared_addresses_agree(sitemap=sitemap)
        self.assertTrue(any("is not declared" in f for f in failures), failures)


class CrawlerPolicy(unittest.TestCase):
    """Decision 13, approved 2026-09-21: present, not trained on."""

    def test_the_built_robots_carries_the_signal_inside_the_group(self):
        self.assertEqual(guards.crawler_policy(), [])
        self.assertIn(build.CONTENT_SIGNAL, build.render_robots())

    def test_a_missing_signal_is_caught(self):
        served = build.render_robots().replace(build.CONTENT_SIGNAL + "\n", "")
        self.assertTrue(guards.crawler_policy(served=served))

    def test_a_signal_outside_the_group_is_caught(self):
        """A content signal applies to the group it sits in, so placement is the policy."""
        served = build.render_robots().replace(build.CONTENT_SIGNAL + "\n", "")
        served = f"{build.CONTENT_SIGNAL}\n\n{served}"
        failures = guards.crawler_policy(served=served)
        self.assertTrue(any("outside" in f for f in failures), failures)


class TheVerifierRefusesRedirects(unittest.TestCase):
    """Following a redirect is how a verifier confirms a URL that does not exist."""

    def test_a_redirect_on_a_declared_address_fails(self):
        original = verify_live.fetch

        def redirected(url, accept=None):
            raise verify_live.Redirected(url, 308, "https://galinstan.ai/privacy")

        verify_live.fetch = redirected
        try:
            failures = verify_live.verify("https://galinstan.ai/privacy.html")
        finally:
            verify_live.fetch = original
        self.assertEqual(len(failures), 1)
        self.assertIn("308", failures[0])

    def test_the_handler_does_not_follow(self):
        handler = verify_live._RefuseRedirects()
        self.assertIsNone(
            handler.redirect_request(None, None, 308, "", {}, "https://galinstan.ai/privacy")
        )


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

    def test_every_declared_address_has_an_expectation(self):
        """A page nobody said what to expect from is unchecked, not passing.

        Keyed by the address the site declares rather than by the filename the build
        writes. They are not the same thing: the host serves `privacy.html` at `/privacy`,
        and the verifier now refuses redirects, so a filename here would name a URL that
        cannot be verified.
        """
        covered = set(self.verify_live.EXPECTED) | self.verify_live.BINARY
        self.assertTrue(
            set(build.SITEMAP) <= covered,
            f"no expectation for {set(build.SITEMAP) - covered}",
        )

    def test_an_unlisted_path_is_reported_rather_than_passing(self):
        self.assertIsNone(self.verify_live.EXPECTED.get("/something-nobody-listed"))


class MailTargets(unittest.TestCase):
    """Round 9, ask 47: every mail link is an approved target with its approved subject."""

    def test_the_real_build_serves_every_approved_mail_link(self):
        self.assertEqual(guards.mail_targets_carry_their_subjects(), [])

    def test_a_link_that_lost_its_subject_is_caught(self):
        pages = [("index.html", '<a href="mailto:partners@banneker.net">partners@banneker.net</a>')]
        failures = guards.mail_targets_carry_their_subjects(pages)
        self.assertTrue(any("is not an approved target" in f for f in failures))
        self.assertTrue(any("no page serves" in f for f in failures))

    def test_an_unapproved_address_is_caught(self):
        href = build.mail_href("contact").replace("partners@", "antwain@")
        pages = [("index.html", f'<a href="{href}">x</a>')]
        self.assertTrue(any("antwain@" in f for f in guards.mail_targets_carry_their_subjects(pages)))

    def test_the_live_verifier_names_a_missing_demo_link(self):
        """Over a served body: the contact link present and the demo link rewritten away."""
        body = (ROOT / "public" / "deployment.html").read_text("utf-8")
        rewritten = body.replace(build.mail_href("cta-demo-target"), "/cdn-cgi/l/email-protection")
        original = verify_live.fetch
        verify_live.fetch = lambda url, accept=None: rewritten
        try:
            failures = verify_live.verify("https://galinstan.ai/deployment")
        finally:
            verify_live.fetch = original
        self.assertTrue(any("cta-demo-target mail link is not served" in f for f in failures))
        self.assertTrue(any("/cdn-cgi/l/email-protection" in f for f in failures))


class Whitepaper(unittest.TestCase):
    """The committed PDF is tied to the register's strings, and carries nothing else."""

    def setUp(self):
        import json

        self.pdf = build.WHITEPAPER_PDF.read_bytes()
        self.lock = json.loads(build.WHITEPAPER_LOCK.read_text(encoding="utf-8"))
        self.source = build.render_whitepaper_source()

    def test_the_committed_pdf_matches_its_source(self):
        self.assertEqual(guards.whitepaper_matches_its_source(), [])

    def test_a_string_changed_without_reprinting_is_caught(self):
        failures = guards.whitepaper_matches_its_source(
            self.pdf, self.lock, self.source.replace("How Galinstan works", "How it works")
        )
        self.assertTrue(any("source has changed" in f for f in failures), failures)

    def test_a_swapped_pdf_is_caught(self):
        failures = guards.whitepaper_matches_its_source(self.pdf + b"\n", self.lock, self.source)
        self.assertTrue(any("not the one the lock records" in f for f in failures), failures)

    def test_an_author_field_is_caught(self):
        failures = guards.whitepaper_matches_its_source(self.pdf + b"/Author (Someone)", self.lock, self.source)
        self.assertTrue(any("author field" in f for f in failures), failures)

    def test_a_link_to_a_third_party_is_caught(self):
        failures = guards.whitepaper_matches_its_source(
            self.pdf + b"/URI (https://example.com/x)", self.lock, self.source
        )
        self.assertTrue(any("example.com" in f for f in failures), failures)

    def test_the_approved_contact_is_the_only_link(self):
        self.assertEqual(guards._pdf_uris(self.pdf), {build.mail_href("wp-contact")})

    def test_every_word_of_the_source_is_from_the_register(self):
        self.assertEqual(
            guards.page_prose_comes_from_the_register([("whitepaper source", self.source)]), []
        )

    def test_the_paper_is_linked_from_the_pages_approved_for_it(self):
        for path in build.WHITEPAPER_LINKED_FROM:
            name = "index.html" if path == "/" else f"{path[1:]}.html"
            with self.subTest(page=name):
                self.assertIn(f'href="{build.WHITEPAPER_PATH}"', (build.PUBLIC / name).read_text(encoding="utf-8"))
        self.assertNotIn(build.WHITEPAPER_PATH, (build.PUBLIC / "intraday-liquidity.html").read_text(encoding="utf-8"))
