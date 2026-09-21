"""The copy register for galinstan.ai.

Every string that reaches a visitor lives here with an explicit status, and nothing
else in this repository is allowed to contain page prose. The reason is in
`50_Claude_Outputs/METHOD_FROM_JJ.md` section 3: sessions do not improvise a string to
fill a gap, and an approval is only complete when it is written down.

Three statuses, and the build treats them differently:

  APPROVED     Antwain approved this exact text, on the date recorded. Ships.
  PENDING      Drafted by Cowork, not yet approved. Renders in a preview build,
               and blocks a production release.
  PLACEHOLDER  A fact nobody has supplied yet — an address, a registration number.
               Renders as a visible marker, and blocks a production release.

`publishable()` is the whole point: it is False until every string on the page is
APPROVED, and the production deploy refuses to run while it is False. A preview URL
still builds, so the page can be looked at and argued about before it can be published.

**All twelve strings are approved as of 2026-09-21.** That is not a reason to relax the
mechanism: the next page added starts unapproved, and stage 2 copy has to come from
discovery rather than from what we currently assume.
"""

from dataclasses import dataclass

APPROVED = "approved"
PENDING = "pending"
PLACEHOLDER = "placeholder"


@dataclass(frozen=True)
class Line:
    id: str
    status: str
    text: str
    note: str = ""
    approved_on: str = ""

    @property
    def blocks_publication(self) -> bool:
        return self.status != APPROVED


# --------------------------------------------------------------------------------------
# The page, in document order. Source: 50_Claude_Outputs/SITE_COPY_STAGE1.md
# --------------------------------------------------------------------------------------

LINES = [
    Line(
        id="wordmark",
        status=APPROVED,
        text="Galinstan",
        approved_on="2026-09-20",
        note="The product name.",
    ),
    Line(
        id="headline",
        status=APPROVED,
        approved_on="2026-09-20",
        text=(
            "Air-gapped optimization and audit software for European banks \u2014 "
            "the analysis runs inside your perimeter, not ours."
        ),
        note="Approved 2026-09-20.",
    ),
    Line(
        id="body-1",
        status=APPROVED,
        approved_on="2026-09-21",
        text=(
            "Galinstan is being built for treasury and resilience teams at EU and EEA "
            "institutions in scope of DORA. It is designed to do two things inside your own "
            "hardware boundary: find the most efficient way to hold a regulatory liquidity "
            "position, and produce audit evidence that can be relied on."
        ),
        note="Tense is deliberate: 'is being built', 'designed to'.",
    ),
    Line(
        id="body-2",
        status=APPROVED,
        approved_on="2026-09-21",
        text=(
            "By design, no data leaves the institution, there is no cloud service to depend "
            "on, and the software makes no outbound connection of any kind."
        ),
        note=(
            "Revised 2026-09-21. The earlier draft claimed there is no entry to add to the "
            "critical ICT provider register. Supervisory guidance says a licence sold with "
            "ongoing support can itself be an ICT service, so a bank would likely still "
            "record Banneker. This states only what the design guarantees."
        ),
    ),
    Line(
        id="body-3",
        status=APPROVED,
        approved_on="2026-09-21",
        text=(
            "We want to hear from group treasurers, heads of ALM and DORA programme leads "
            "about how this work gets done today, and what it costs. If that is your remit, "
            "write to us."
        ),
        note=(
            "Revised 2026-09-21. 'We are currently talking with...' was not yet true \u2014 "
            "discovery has not started."
        ),
    ),
    Line(
        id="entity",
        status=APPROVED,
        approved_on="2026-09-21",
        text="Galinstan is a product of Banneker.",
        note="Banneker is a sole proprietorship. No 'LLC', and no 'Strategy & Compliance'.",
    ),
    Line(
        id="contact",
        status=APPROVED,
        approved_on="2026-09-21",
        text="antwain@banneker.net",
        note=(
            "Rendered as a mail link with the subject pre-filled 'Galinstan \u2014 via "
            "galinstan.ai', which is free source attribution: every enquiry from the site "
            "arrives labelled, with no form and no paid analytics. The subject is part of "
            "the approved string and lives in CONTACT_SUBJECT below."
        ),
    ),
    Line(
        id="legal-footer",
        status=APPROVED,
        approved_on="2026-09-21",
        text="\u00a9 2026 Banneker \u00b7 banneker.net",
        note=(
            "A US sole proprietorship has no registration number to show, so the footer "
            "stays minimal. Rendered as plain text rather than a link \u2014 see the note "
            "on rendering below."
        ),
    ),
    Line(
        id="privacy-controller",
        status=APPROVED,
        approved_on="2026-09-21",
        text=(
            "The data controller for this site is Sherman A. Cross, trading as Banneker. "
            "Contact: antwain@banneker.net."
        ),
        note="A reviewed legal string. The law asks for the controller's identity here.",
    ),
    Line(
        id="privacy-analytics",
        status=APPROVED,
        approved_on="2026-09-21",
        text=(
            "This site uses Cloudflare Web Analytics to count visits. It sets no cookies "
            "and does not track you across other sites. Cloudflare, which hosts the site, "
            "processes your IP address to deliver the page and protect it from abuse. Our "
            "lawful basis is our legitimate interest in knowing how the site is used."
        ),
        note=(
            "Cloudflare Web Analytics is free, cookieless and needs no consent banner. Its "
            "limits are six months of history and no custom events."
        ),
    ),
    Line(
        id="meta-title",
        status=APPROVED,
        approved_on="2026-09-21",
        text="Galinstan \u2014 air-gapped liquidity optimization and audit software for EU banks",
        note="Segment keywords, not index terms. 'FinTech' does not appear.",
    ),
    Line(
        id="meta-description",
        status=APPROVED,
        approved_on="2026-09-21",
        text=(
            "Software being built for intraday liquidity, ALM and DORA third-party risk "
            "work, designed to run on-premise inside the institution's own hardware "
            "boundary with no outbound connection."
        ),
        note="Revised 2026-09-21: 'that runs' became 'being built... designed to run'.",
    ),
]

# Part of the approved `contact` string, kept separate because it is an attribute rather
# than page text: the pre-filled subject that makes every enquiry self-attributing.
CONTACT_SUBJECT = "Galinstan \u2014 via galinstan.ai"

BY_ID = {line.id: line for line in LINES}


def line(line_id: str) -> Line:
    return BY_ID[line_id]


def text(line_id: str) -> str:
    """The text to render. A placeholder renders as a visible marker, never as a blank.

    METHOD_FROM_JJ.md section 3: 'No silent blanks. Enumerate every placeholder; a blank
    and a zero read differently.'
    """
    item = BY_ID[line_id]
    if item.status == PLACEHOLDER:
        return f"[[TODO: {item.id} — {item.note.splitlines()[0]}]]"
    return item.text


def blockers() -> list[Line]:
    return [item for item in LINES if item.blocks_publication]


def publishable() -> bool:
    return not blockers()


# Named `page_copy` and not `copy` on purpose: `src/` goes on sys.path in build.py and in
# the tests, and a module called `copy.py` there would shadow the standard library's copy
# module for every import in the process. That is the kind of failure that surfaces later,
# somewhere unrelated, as a missing attribute.
