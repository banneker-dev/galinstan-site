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
        note="The product name. Approved by virtue of being the product name.",
    ),
    Line(
        id="headline",
        status=APPROVED,
        approved_on="2026-09-20",
        text=(
            "Air-gapped optimization and audit software for European banks — "
            "the analysis runs inside your perimeter, not ours."
        ),
        note="Approved 2026-09-20. Recorded in 00_Start_Here/CURRENT_STATE.md section 6a.",
    ),
    Line(
        id="body-1",
        status=PENDING,
        text=(
            "Galinstan is being built for treasury and resilience teams at EU and EEA "
            "institutions in scope of DORA. It is designed to do two things inside your own "
            "hardware boundary: find the most efficient way to hold a regulatory liquidity "
            "position, and produce audit evidence that can be relied on."
        ),
        note="Drafted by Cowork. Tense is deliberate: 'is being built', 'designed to'.",
    ),
    Line(
        id="body-2",
        status=PENDING,
        text=(
            "By design, no data leaves the institution, there is no cloud service to depend "
            "on, and there is no entry to add to your critical ICT provider register."
        ),
        note="The register line is the highest-value sentence on the page for a DORA lead.",
    ),
    Line(
        id="body-3",
        status=PENDING,
        text=(
            "We are currently talking with group treasurers, heads of ALM and DORA programme "
            "leads about how this work gets done today, and what it costs. If that is your "
            "remit, we would like to hear from you."
        ),
        note="The discovery invitation. This is the page's only conversion path at stage 1.",
    ),
    Line(
        id="entity",
        status=PENDING,
        text="Galinstan is a product of Banneker Strategy & Compliance LLC.",
        note=(
            "WEB_SPEC.md open item 3 — whether the entity shown is Banneker or Galinstan "
            "as a product of Banneker. This draft takes the second reading."
        ),
    ),
    Line(
        id="contact",
        status=PLACEHOLDER,
        text="",
        note=(
            "WEB_SPEC.md open item 5. A personal address, a role address, or a form. "
            "The form option is the only one that carries source attribution, which "
            "WEB_SPEC.md section 6a requires from the first submission."
        ),
    ),
    Line(
        id="legal-footer",
        status=PLACEHOLDER,
        text="",
        note=(
            "Entity, jurisdiction and registration details, as one line. "
            "SITE_COPY_STAGE1.md lists this as still needed before publishing."
        ),
    ),
    Line(
        id="privacy-controller",
        status=PLACEHOLDER,
        text="",
        note=(
            "The named data controller for the privacy notice. Required by "
            "WEB_SPEC.md section 6 and it is a legal string, so it is not ours to draft."
        ),
    ),
    Line(
        id="privacy-analytics",
        status=PLACEHOLDER,
        text="",
        note=(
            "What the privacy notice says about analytics. Depends on WEB_SPEC.md open "
            "item 4 — cookieless and banner-free, or GA4 with consent management. "
            "The lawful basis differs between them, so the sentence cannot be drafted first."
        ),
    ),
    Line(
        id="meta-title",
        status=PENDING,
        text="Galinstan — air-gapped liquidity optimization and audit software for EU banks",
        note=(
            "WEB_SPEC.md section 6: segment keywords, not index terms. Carries "
            "'air-gapped', 'liquidity optimization', 'EU banks'. 'FinTech' does not appear."
        ),
    ),
    Line(
        id="meta-description",
        status=PENDING,
        text=(
            "Intraday liquidity, ALM and DORA third-party risk work that runs on-premise, "
            "inside the institution's own hardware boundary, with no outbound connection."
        ),
        note="Segment keywords: intraday liquidity, ALM, DORA, ICT third-party risk, on-premise.",
    ),
]

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
