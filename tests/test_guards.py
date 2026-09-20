"""Tests for the site build and its guards. Standard library only — `python3 -m unittest`.

Zero dependencies is deliberate. The practice runs 268 headless tests with none
(`50_Claude_Outputs/METHOD_FROM_JJ.md` section 5), and a test suite that needs an install
is a test suite that does not run on the machine where the mistake is being made.

Every guard is tested in both directions: a page that should pass, and a page that should
fail. *"Counting the absence of something is not a test until you have confirmed the thing
ran."*
"""

import pathlib
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

    def test_a_placeholder_renders_as_a_marker_and_never_as_a_blank(self):
        self.assertTrue(page_copy.text("contact").startswith("[[TODO:"))
        self.assertIn("[[TODO: contact", (ROOT / "public" / "index.html").read_text("utf-8"))


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

    def test_the_registered_entity_name_is_not_a_forbidden_claim(self):
        page = [("index.html", "<p>Banneker Strategy & Compliance LLC</p>")]
        self.assertEqual(guards.no_forbidden_claims(page), [])

    def test_missing_metadata_is_caught(self):
        page = [("index.html", "<html><title>x</title></html>")]
        self.assertTrue(guards.required_metadata(page))


class PublicationGate(unittest.TestCase):
    def test_unapproved_copy_blocks_a_production_release(self):
        failures = guards.publication_gate()
        self.assertTrue(
            failures,
            "the publication gate passed while copy is still unapproved — "
            "if the copy really was approved, this test is the thing to update, "
            "deliberately and in its own commit",
        )

    def test_the_gate_names_every_blocker_rather_than_the_first(self):
        self.assertGreaterEqual(len(guards.publication_gate()), len(page_copy.blockers()))

    def test_analytics_absence_is_itself_a_blocker(self):
        self.assertTrue(any("analytics" in f for f in guards.publication_gate()))


if __name__ == "__main__":
    unittest.main()
