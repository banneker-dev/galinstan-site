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

**Every string is approved as of 2026-09-22** — the stage 1 page, the demo route (ask 47)
and the stage 2 release set (ask 54), each on Antwain's approval as recorded in
`50_Claude_Outputs/SITE_COPY_STAGE1.md` and `SITE_COPY_STAGE2.md`. That is not a reason to
relax the mechanism: the next string added starts unapproved.
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
    # For a mail-bearing string: the approved pre-filled subject. The build renders every
    # such string as a `mailto:` carrying it, and both the build-time guard and the live
    # verifier assert that it is served that way (CURRENT_STATE_REPO.md Round 9, ask 47).
    mail_subject: str = ""

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
        approved_on="2026-09-23",
        text=(
            "Air-gapped optimization and audit software for European banks. The analysis runs inside your perimeter, not ours."
        ),
        note="Revision approved 2026-09-23 (Antwain): no dashes in client-facing copy.",
    ),
    Line(
        id="body-1",
        status=APPROVED,
        approved_on="2026-09-22",
        text=(
            "Galinstan is built for treasury and resilience teams at EU and EEA "
            "institutions in scope of DORA. It is built to do two things inside your own "
            "hardware boundary: find the most efficient way to hold a regulatory liquidity "
            "position, and produce audit evidence that can be relied on."
        ),
        note=(
            "Revision approved 2026-09-22: 'Galinstan is built to...' throughout, so the "
            "live page and stage 2 read the same. Previously 'is being built... designed to'."
        ),
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
        id="cta-demo",
        status=APPROVED,
        approved_on="2026-09-22",
        text="Request a demo",
        note=(
            "The demo route (SITE_COPY_STAGE2.md section 1). A mail link, not a form: the "
            "site does not say a demo is ready, it lets an institution ask."
        ),
    ),
    Line(
        id="cta-demo-target",
        status=APPROVED,
        approved_on="2026-09-22",
        text="partners@banneker.net",
        mail_subject="Galinstan demo request",
        note="Where every 'Request a demo' link points, with its pre-filled subject.",
    ),
    Line(
        id="contact",
        status=APPROVED,
        approved_on="2026-09-22",
        mail_subject="Galinstan enquiry via galinstan.ai",
        text="partners@banneker.net",
        note=(
            "Rendered as a mail link with the subject pre-filled 'Galinstan enquiry via "
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
        approved_on="2026-09-22",
        text=(
            "The data controller for this site is Sherman A. Cross, trading as Banneker. "
            "Contact: partners@banneker.net."
        ),
        note=(
            "A reviewed legal string. The law asks for the controller's identity here. "
            "Revision approved 2026-09-22: partners@ replaces antwain@, an alias onto the "
            "same monitored mailbox."
        ),
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
        approved_on="2026-09-23",
        text="Galinstan: air-gapped liquidity optimization and audit software for EU banks",
        note="Revision approved 2026-09-23 (Antwain): no dashes in client-facing copy.",
    ),
    Line(
        id="meta-description",
        status=APPROVED,
        approved_on="2026-09-22",
        text=(
            "Software built for intraday liquidity, ALM and DORA third-party risk work, "
            "to run on-premise inside the institution's own hardware boundary with no "
            "outbound connection."
        ),
        note="Revision approved 2026-09-22: the 'built to' tense, as body-1.",
    ),
]


# --------------------------------------------------------------------------------------
# Stage 2, the release set. Source: 50_Claude_Outputs/SITE_COPY_STAGE2.md section 2,
# approved by Antwain 2026-09-22 (ask 54). Parsed from that table rather than retyped, and
# `**...**` marks a bold lead-in exactly as the approved text carries it.
# --------------------------------------------------------------------------------------

STAGE_2 = [
    Line(id="dep-meta-title", status=APPROVED, approved_on="2026-09-22", text="How Galinstan is deployed: no egress, your hardware, escrow and exit"),
    Line(id="dep-meta-description", status=APPROVED, approved_on="2026-09-22", text="What an institution installs, what it must buy, what leaves the perimeter, how an offline instance is upgraded, and what happens at exit."),
    Line(id="dep-h1", status=APPROVED, approved_on="2026-09-22", text="The questions a diligence reviewer asks first, answered on the page rather than in the third meeting."),
    Line(id="dep-sub", status=APPROVED, approved_on="2026-09-22", text="Galinstan is built as software you install and run inside your own perimeter. There is no tenancy and no console on our side."),
    Line(id="dep-body-1", status=APPROVED, approved_on="2026-09-23", text="**What leaves.** Nothing, by design. The software makes no outbound connection of any kind. Not for licensing, not for telemetry, not for model weights, not for updates. It is built to run on a machine with no route to the internet, and it has nothing to reach if it is given one."),
    Line(
        id="dep-body-2", status=APPROVED, approved_on="2026-09-22", text="**What you buy.** Galinstan is built to run on hardware you already know how to procure.", note="Revision approved 2026-09-22 (Antwain): a sentence removed from the approved text."),
    Line(
        id="dep-body-3", status=APPROVED, approved_on="2026-09-22", text="**What we are to your register.** We license Galinstan annually with support, patches and calibration. None of your data reaches us, and no part of the analysis depends on us being reachable.", note="Revision approved 2026-09-22 (Antwain): a sentence removed from the approved text."),
    Line(id="dep-body-4", status=APPROVED, approved_on="2026-09-22", text="**Upgrades.** Every version is cut as a signed release: an offline bundle with a checksum for every file and a software bill of materials. It installs with no package index and no network, and the instance never reaches out for it."),
    Line(id="dep-body-5", status=APPROVED, approved_on="2026-09-23", text="**Escrow and exit.** Every release is built to be deposited: source, bundle and checksums as one versioned artefact. We agree escrow and exit terms in the contract rather than pointing at a policy page."),
    Line(id="dep-cta", status=APPROVED, approved_on="2026-09-22", text="Request a demo"),
    Line(id="il-meta-title", status=APPROVED, approved_on="2026-09-23", text="Galinstan: intraday liquidity optimization that runs on your own hardware"),
    Line(id="il-meta-description", status=APPROVED, approved_on="2026-09-22", text="Software built to decide what an EU bank should hold against its intraday and LCR requirements, and to run the decision inside the institution's own hardware boundary."),
    Line(id="il-h1", status=APPROVED, approved_on="2026-09-22", text="Knowing where the money is, and knowing what to hold, are two different problems."),
    Line(id="il-sub", status=APPROVED, approved_on="2026-09-23", text="Intraday monitoring tells a treasurer what happened. Galinstan is built to answer what to do about it: which assets to hold, which to release, and what the surplus is costing."),
    Line(id="il-body-1", status=APPROVED, approved_on="2026-09-22", text="The intraday tooling on the market is built to make positions visible: balances across accounts, payment flows, throttling decisions, the data a supervisor asks for. That work is necessary and it is well served. What we have not found is software that chooses the position."),
    Line(id="il-body-2", status=APPROVED, approved_on="2026-09-23", text="The choice is hard on purpose. Assets are held in lots, haircuts and caps interact, and encumbrance removes collateral from the buffer. The objective is to give up as little yield as possible while staying above the requirement all day. That is a combinatorial problem rather than a report, and Galinstan is built to solve it as one."),
    Line(id="il-body-3", status=APPROVED, approved_on="2026-09-22", text="The surplus is worth measuring before it is defended. The FY2025 Pillar 3 disclosures of three European banks show average liquidity coverage ratios between 156% and 256%. Some of that headroom is deliberate. The part that is not is high-quality liquid assets the requirement did not call for."),
    Line(id="il-body-4", status=APPROVED, approved_on="2026-09-22", text="Galinstan is built to connect to nothing. It reads the position you give it, computes inside your hardware boundary, and writes its answer back to you. There is no service on our end of a line, because there is no line."),
    Line(id="il-cta", status=APPROVED, approved_on="2026-09-22", text="Request a demo"),
    Line(id="ae-meta-title", status=APPROVED, approved_on="2026-09-23", text="Galinstan: audit evidence produced inside your own perimeter"),
    Line(id="ae-meta-description", status=APPROVED, approved_on="2026-09-22", text="Software built to produce control-testing and gap-analysis evidence inside the institution's own hardware boundary, with the inputs and method recorded alongside the result."),
    Line(id="ae-h1", status=APPROVED, approved_on="2026-09-23", text="Audit evidence that never leaves the institution that produced it."),
    Line(id="ae-sub", status=APPROVED, approved_on="2026-09-23", text="Galinstan is built to produce control testing and gap analysis evidence inside your own hardware boundary, with each finding citing where it came from."),
    Line(id="ae-body-2", status=APPROVED, approved_on="2026-09-22", text="A different standard is possible when the software runs inside the institution. The inputs never leave. The version that produced the result sits on the institution's own disk. Nothing is rewritten between the calculation and the report by a service neither party controls."),
    Line(id="ae-body-3", status=APPROVED, approved_on="2026-09-22", text="Module 2 is built around that: control testing and gap analysis against DORA and the EBA outsourcing guidelines, with the evidence for each finding citing where it came from, and with the model and method that produced it recorded beside it rather than described afterwards."),
    Line(id="ae-cta", status=APPROVED, approved_on="2026-09-22", text="Request a demo"),
    Line(id="nav-1", status=APPROVED, approved_on="2026-09-22", text="Intraday liquidity"),
    Line(id="nav-2", status=APPROVED, approved_on="2026-09-22", text="Audit evidence"),
    Line(id="nav-3", status=APPROVED, approved_on="2026-09-22", text="Deployment"),
    Line(
        id="foot-claim", status=APPROVED, approved_on="2026-09-25", text="Galinstan is built to run inside your perimeter and produce evidence.", note="Revision approved 2026-09-25 (Antwain): the disclaimer sentence is cut. A footer carries a tagline, the entity and the legal links, not a disclaimer."),
]

LINES += STAGE_2

# Part of the approved `contact` string, kept separate because it is an attribute rather
# than page text: the pre-filled subject that makes every enquiry self-attributing.
CONTACT_SUBJECT = "Galinstan enquiry via galinstan.ai"
assert CONTACT_SUBJECT == next(item for item in LINES if item.id == "contact").mail_subject

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
