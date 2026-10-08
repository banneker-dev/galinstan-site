# Galinstan: struck statements

**Binding through `RULES.md` (row text approved by Antwain, 2026-09-30, "ok"):** "A statement Antwain has struck is listed in
the struck statements file with his words and date. No copy, page, report or funding draft may contain it, and the checks
in both lanes fail on a match."

**How it is used.** Both lanes read this one file. Cody's build guard runs over the copy register, every rendered page and
the bundle's pages; Cowork's `50_Claude_Outputs/TOOLS/struck_check.py` runs over drive documents before they are shown and
over every pass of a funding draft. The `Pattern` column is a case-insensitive regular expression. A new row needs
Antwain's words and date. Records that quote a struck statement as history (the living documents, `RULES.md`, the
changelogs, session logs, `NSF_PROJECT_PITCH.md` as submitted, superseded and archived files) are not checked. Elsewhere, a struck phrase directly inside quotation marks is read as a record of the strike and passes.

| Id | Struck | Pattern | Antwain's words, date | Use instead |
|---|---|---|---|---|
| S1 | "It certifies nothing." and any "does not certify" | `certifies nothing\|(Galinstan\|it\|we\|this\|report\|evidence\|product) (do\|does) not certify` | "The former 'does not certify compliance' rule is deleted permanently ... not to be reintroduced in any form, internal or client-facing" (2026-09-25); "yes remove it" (2026-09-30) | The shared responsibility model's line (Decided, 2026-09-29) |
| S2 | "does not make anyone compliant" | `(does not\|doesn't\|never) make[s]? (anyone\|an institution\|a bank) compliant` | "There are specific steps that an entity must follow to reach compliance and Galinstan supports those steps and provides audit evidence. Therefore, compliance is accomplished." (2026-09-29) | "Galinstan supports the steps an institution follows to reach compliance and provides the audit evidence" |
| S3 | "DORA-compliant" | `DORA[- ]compliant` | "DORA-compliant" ... not used (2026-09-22) | "makes it easier for an institution to become compliant" |
| S4 | "exponentially more accurate" | `exponentially more accurate` | not used (2026-09-22) | "improves its accuracy" |
| S5 | "working software, not a design" | `working software, not a design\|working, not a design` | "your hedging now has a demonstrated loss of funding" (2026-09-30) | State what exists: "Both engines are built and measured ..." |
| S6 | "no account to suspend", "nothing switches off" | `no account to suspend\|nothing switches off` | cut as contradicting the annual term licence (2026-09-22) | The licence terms in `CURRENT_STATE.md` §4 |
| S7 | "byte for byte" | `byte[- ]for[- ]byte` | "I dont like byte for byte" (2026-10-01); "byte for byte is not a good expression to use. why would you recommend keeping it after I said it has to go" (2026-10-02) | "exactly", "identical", or "the same figures" (Decided, Round 91: "An auditor can run any result on another machine and get the same figures.") |
| S8 | "Icosa royalty" and any royalty owed to Icosa | `Icosa('s)? royalt(y\|ies)\|royalt(y\|ies) (owed \|payable \|paid \|due )?to Icosa` | "remove those terms, I was exploring that path before we successfully built our own" (2026-10-07), on Cowork's ask 1 of the same day | "No royalty is owed to anyone" (`CURRENT_STATE.md` §1) |
| S9 | "Icosa's engine" and any Icosa component as part of Galinstan | `Icosa('s)? (physics-based \|QUBO \|optimi[sz]ation \|core \|combinatorial reasoning )?engine\b\|solved (locally )?on Icosa` | "remove those terms, I was exploring that path before we successfully built our own" (2026-10-07), on Cowork's ask 1 of the same day | "built on open source end to end" (`CURRENT_STATE.md` §1) |
