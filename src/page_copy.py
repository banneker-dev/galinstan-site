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
        approved_on="2026-09-25",
        text=(
            "Air-gapped optimization and audit software for European banks. The analysis runs inside your perimeter, not ours."
        ),
        note='Approved 2026-09-25 (Antwain), rejected row r01 closed. Dashes out per RULES.md D2; this wording is now his.',
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
        approved_on="2026-09-25",
        text="partners@banneker.net",
        mail_subject="Galinstan demo request",
        note='Subject approved 2026-09-25 (Antwain), rejected row r12 closed.',
    ),
    Line(
        id="contact",
        status=APPROVED,
        approved_on="2026-09-25",
        mail_subject="Galinstan enquiry via galinstan.ai",
        text="partners@banneker.net",
        note="Rendered as a mail link with the subject pre-filled 'Galinstan enquiry via galinstan.ai', which is free source attribution: every enquiry from the site arrives labelled, with no form and no paid analytics. Subject approved 2026-09-25 (Antwain).",
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
            "**Data controller.** The data controller for this site is Sherman A. Cross, trading as Banneker. Contact: partners@banneker.net."
        ),
        note=(
            "A reviewed legal string. The law asks for the controller's identity here. Revision approved 2026-09-22: partners@ replaces antwain@, an alias onto the same monitored mailbox. Label folded into the string on 2026-09-25 so no page prose sits outside the register. The served bytes are unchanged: the renderer used to emit the same <strong> itself."
        ),
    ),
    Line(
        id="privacy-analytics",
        status=APPROVED,
        approved_on="2026-09-21",
        text=(
            "**Analytics.** This site uses Cloudflare Web Analytics to count visits. It sets no cookies and does not track you across other sites. Cloudflare, which hosts the site, processes your IP address to deliver the page and protect it from abuse. Our lawful basis is our legitimate interest in knowing how the site is used."
        ),
        note=(
            "Cloudflare Web Analytics is free, cookieless and needs no consent banner. Its limits are six months of history and no custom events. Label folded into the string on 2026-09-25 so no page prose sits outside the register. The served bytes are unchanged: the renderer used to emit the same <strong> itself."
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
    # Moved into the register on 2026-09-25 (Antwain). Both were hardcoded in build.py, and
    # being outside the register is how they kept an em dash through every copy review.
    Line(
        id="privacy-meta-title", status=APPROVED, approved_on="2026-09-25", text="Privacy",
        note="Approved 2026-09-25 (Antwain): 'just say Privacy, you dont need to repeat the product'. The wordmark is already on the page.",
    ),
    Line(
        id="notfound-meta-title", status=APPROVED, approved_on="2026-09-25", text="Not found",
        note="Approved 2026-09-25 (Antwain), same reason as privacy-meta-title. The page is noindex and absent from the sitemap; it exists so the host does not serve its own error page instead.",
    ),
    # Moved in on 2026-09-25 so that no prose a visitor can read sits outside this register.
    # The wording of all three is unchanged and has been live since site-2026.09.1; what is
    # new is that it is now recorded, approvable and checked.
    Line(
        id="privacy-contact-label", status=APPROVED, approved_on="2026-09-25", text="**Contact.**",
        note="The bold label on the privacy page's contact line. Was hardcoded in build.py; wording unchanged.",
    ),
    Line(
        id="notfound-h1", status=APPROVED, approved_on="2026-09-25", text="That page does not exist.",
        note="The /404 heading. Was hardcoded in build.py; wording unchanged since the first release.",
    ),
    Line(
        id="notfound-link", status=APPROVED, approved_on="2026-09-25", text="Return to the front page.",
        note="The /404 link home. Was hardcoded in build.py; wording unchanged since the first release.",
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

# --------------------------------------------------------------------------------------
# The public whitepaper, served as /whitepaper.pdf. Drafted by Cody on Antwain's
# instruction of 2026-09-25 ("you prepare pdf"), from the three-layer proposal he approved
# the same day: what the product does and why, with its published sources; how it does it
# stays out. Rendered by `build.render_whitepaper_source`, in this order. The id says what
# each string is: wp-h- a section heading, wp-h3- a subheading, wp-li- a list item,
# wp-ref- a source, wp-p- a paragraph.
# --------------------------------------------------------------------------------------

_WP_NOTE = "Drafted by Cody, 2026-09-25, on Antwain's instruction. Awaiting his approval."


def _wp(line_id: str, text: str, **kw) -> Line:
    return Line(id=line_id, status=PENDING, text=text, note=_WP_NOTE, **kw)


WHITEPAPER = [
    _wp("wp-meta-title", "How Galinstan works"),
    _wp("wp-title", "How Galinstan works"),
    _wp("wp-sub", "Liquidity optimization and DORA audit evidence, produced inside the bank's own perimeter and open to re-performance by its reviewers."),
    _wp("wp-edition", "Describes release v1.6.0. September 2026."),

    _wp("wp-h-summary", "Summary"),
    _wp("wp-p-summary-1", "Galinstan is software for European banks that runs entirely on the bank's own machines, with no network connection, and writes evidence a reviewer can check for themselves. It reads the regulatory returns and records a bank already keeps, and does three things with them."),
    _wp("wp-li-summary-1", "**Liquidity.** It finds the holding of high-quality liquid assets that gives up the least yield while keeping the liquidity coverage ratio above the floor the bank sets, under a thousand stress scenarios as well as on the day. An independent calculator confirms every result."),
    _wp("wp-li-summary-2", "**DORA policy evidence.** It assesses the bank's policy on ICT third-party services against the EU technical standard for that policy and proposes a grade for each article, with every finding quoting the policy's own words."),
    _wp("wp-li-summary-3", "**The Register of Information.** It checks the bank's DORA register against the European Banking Authority's own published checks before the register is submitted, and shows, contract by contract, which of DORA's required contract terms the register records."),
    _wp("wp-p-summary-2", "Every method choice rests on a published source: the regulation itself, supervisory assessment practice, and auditing and model risk standards. Every proposal is left to a person to decide."),

    _wp("wp-h-problem", "Why this work is hard today"),
    _wp("wp-p-problem-1", "Liquidity buffers are expensive to hold and dangerous to trim. Assets are held in lots, haircuts and caps interact, and an allocation that looks efficient on the reporting date can fall below the floor as soon as markets move. Choosing the position is a combinatorial problem, and a choice made without stress in view is not one a treasurer can defend."),
    _wp("wp-p-problem-2", "DORA's registers and policies are new, detailed and checked mechanically. In the European Supervisory Authorities' 2024 dry run, only 6.5% of 947 registers passed every data quality check, and 86% of the errors were missing mandatory information."),
    _wp("wp-p-problem-3", "Both jobs turn on data a bank cannot easily send to an outside service: its positions, its contracts and its providers. Galinstan is built so that none of it has to leave."),

    _wp("wp-h-principles", "How it works, in principle"),
    _wp("wp-h3-perimeter", "It runs inside the perimeter"),
    _wp("wp-p-perimeter", "Galinstan arrives as an offline bundle cut from a signed release, with every dependency, a checksum for every file and a software bill of materials. It installs with no package index and no network, and it makes no outbound connection of any kind. The released bundle has been installed and run on a machine with its network disconnected, with the network sampled throughout the run and never answering."),
    _wp("wp-h3-reads", "It reads what the bank already files"),
    _wp("wp-p-reads", "Galinstan does not ask for a new data feed. It reads the returns and records a bank already produces, in the formats the regulators define:"),
    _wp("wp-li-reads-1", "the LCR return, templates C 72.00 to C 76.00, and the NSFR return, templates C 80.00, C 81.00 and C 84.00, in the EBA's xBRL-CSV format;"),
    _wp("wp-li-reads-2", "holdings of securities, in the attributes the ECB defines for its statistics on holdings by banking groups, which the largest euro area groups already report;"),
    _wp("wp-li-reads-3", "the DORA Register of Information, and the policy on ICT third-party services as Word, PDF or plain text."),
    _wp("wp-h3-reconciles", "It reconciles before it recommends"),
    _wp("wp-p-reconciles", "Before Galinstan proposes any change to the liquidity position, it shows that it gets the ratios the bank reported. Each return is checked against the instructions in the implementing technical standard on supervisory reporting, then reproduced by an independent calculator written from the regulation's text, and the holdings must reconcile to the return. If any step fails, no figure is stated, and the output says which step."),
    _wp("wp-h3-apart", "Two calculations that must agree are built apart"),
    _wp("wp-p-apart", "Every allocation the optimizer proposes is recomputed by a separate calculator that shares no code with it. If the two shared a helper, they would share its mistakes, and the check would prove nothing."),
    _wp("wp-h3-stress", "Stress is part of the answer"),
    _wp("wp-p-stress", "The optimizer holds the ratio above the bank's floor across a thousand stress scenarios, not only on the reporting date. On a demonstration book calibrated to published disclosures, the allocation found without stress fell below the floor in 993 of 1,000 scenarios. The allocation Galinstan proposed fell below it in 18."),
    _wp("wp-h3-cites", "Every finding cites its source"),
    _wp("wp-p-cites-1", "For the DORA policy, the criteria are the numbered paragraphs of Commission Delegated Regulation (EU) 2024/1773, in the regulation's own words. A language model running on the machine reads the whole policy and, for each criterion, says how far the policy addresses it, citing a section and quoting it. A claim counts only if its quotation is the policy's own words, in the section it cites."),
    _wp("wp-p-cites-2", "Each article receives a proposed grade on the four-grade scale the Basel Committee uses to assess how its standards are implemented. The grade is a proposal. The Basel Committee and the IMF both describe grading as a judgement, and the reviewer makes it."),
    _wp("wp-h3-errors", "Errors are measured, and lean the safe way"),
    _wp("wp-p-errors-1", "The method is measured against test policies whose answer keys were fixed before any model read them, and each error rate is reported with an exact statistical upper bound."),
    _wp("wp-p-errors-2", "Auditing treats two errors differently. ISA 530 names crediting a control with more than it provides as the error the auditor is primarily concerned with, while crediting it with less only creates work. Galinstan follows that. A favourable finding is held back until a reviewer confirms it, as the PRA's model risk principles ask a known limitation to be met with a documented adjustment, and the report shows each grade both with and without it."),
    _wp("wp-h3-reperform", "A reviewer can re-perform everything"),
    _wp("wp-p-reperform-1", "Every run writes one directory of evidence: every result hashed, a hash-chained record of every step including each output of the model, and a workpaper for each article. The time of the run is kept in a separate manifest, so the same inputs give the same evidence."),
    _wp("wp-p-reperform-2", "A reviewer does not have to take that evidence on trust. One command re-performs a run on the reviewer's own machine and reports, check by check, whether it came out the same. Under the same conditions the evidence is byte-identical on Apple Silicon and on Linux. Each release is a signed tag with a changelog, which answers what changed between the version a bank validated and the version it runs."),

    _wp("wp-h-limits", "What Galinstan does not do"),
    _wp("wp-li-limits-1", "**It does not decide.** Grades and allocations are proposals. The reviewer and the treasurer decide."),
    _wp("wp-li-limits-2", "**It does not guess.** A check that needs something an offline machine cannot have, such as the global LEI database, is listed with its reason rather than assumed to pass. Where a figure cannot be reproduced, it is not stated."),
    _wp("wp-li-limits-3", "**It does not send anything.** There is no service on our side, and nothing in the analysis depends on reaching one."),

    _wp("wp-h-sources", "Sources"),
    _wp("wp-ref-1", "Regulation (EU) 2022/2554, the Digital Operational Resilience Act (DORA)."),
    _wp("wp-ref-2", "Commission Delegated Regulation (EU) 2024/1773, on the policy on the use of ICT services provided by ICT third-party service providers."),
    _wp("wp-ref-3", "Commission Delegated Regulation (EU) 2015/61, on the liquidity coverage requirement."),
    _wp("wp-ref-4", "Commission Implementing Regulation (EU) 2024/3117, the implementing technical standards on supervisory reporting."),
    _wp("wp-ref-5", "EBA, reporting framework 4.2, and its overview of the Register of Information technical checks and validation rules (April 2025)."),
    _wp("wp-ref-6", "ECB, guidance notes to reporting agents on the SHS Regulation for reporting banking groups (May 2020)."),
    _wp("wp-ref-7", "ESAs, DORA dry run exercise summary report (December 2024)."),
    _wp("wp-ref-8", "Basel Committee on Banking Supervision, Regulatory Consistency Assessment Programme: Assessment of Basel III regulations, Brazil (2013)."),
    _wp("wp-ref-9", "IMF, Country Report No. 14/264, Switzerland: Detailed Assessment of Compliance with the Basel Core Principles (2014)."),
    _wp("wp-ref-10", "IAASB, ISA 530, Audit Sampling."),
    _wp("wp-ref-11", "Prudential Regulation Authority, SS1/23, Model risk management principles for banks (2023)."),

    _wp("wp-contact-label", "To discuss Galinstan, write to"),
    _wp(
        "wp-contact",
        "partners@banneker.net",
        mail_subject="Galinstan enquiry via the whitepaper",
    ),
    _wp("wp-link", "How Galinstan works, as a PDF"),
]

LINES += WHITEPAPER

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
