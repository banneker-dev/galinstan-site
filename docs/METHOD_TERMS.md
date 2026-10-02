# Galinstan: method terms

**Cowork's list for the disclosure policy** (`50_Claude_Outputs/MARKETABILITY_REVIEW_2026-10-02.md` 5.7; Antwain,
2026-10-02: "Our competitors' key resource is people. We have to protect our product."). A term here describes how
Galinstan finds its answers. It must not appear in anything that leaves the drive below escrow: pages, posts, video,
decks, the public summary of an application, a roadmap. Binding on both lanes through `RULES.md` D14 (approved by
Antwain, 2026-10-02; Cody writes the row, ask 142).

**How it is used.** `50_Claude_Outputs/TOOLS/method_check.py <files>` checks the files named, and only those: research and
records on the drive use these words freely. The `Pattern` column is a case-insensitive regular expression. A term inside
quotation marks is read as a record and passes. Naming the solver or the open models by product name is allowed (r20 was
rejected); the formulation is not. Rows are added by Cowork or Cody and reported in the living documents.

| Id | What it reveals | Pattern |
|---|---|---|
| M1 | The class of optimisation problem | `mixed[- ]integer\|\bMILP\b\|\bMIP\b\|integer program\|linear program` |
| M2 | How the problem is set up | `formulat` |
| M3 | Splitting the problem | `decompos` |
| M4 | How stress scenarios enter the solve | `constraint (set\|window\|rows?)\|constrained scenarios?\|scenario window\|window of \d+ scenarios` |
| M5 | How scenarios are ranked | `severity score` |
| M6 | Search methods tried | `branch[- ]and[- ](bound\|cut)\|\btabu\b\|heuristic\|simulated annealing\|quantum anneal` |
| M7 | Internal evidence files kept off the public host (ask 105) | `shape\.json\|timing\.json\|trails/` |
| M8 | Calibration material (confidential, decided 2026-09-30) | `band files?\b\|calibration files?\b\|calibration method` |
| M9 | Module 2's pipeline | `\bprompt(s\|ing)?\b\|retrieval\|embedding\|\bRAG\b\|fine[- ]tun\|K[- ]quant\|quanti[sz]\|GGUF\|\bggml\b` |
| M10 | Solve time broken into parts | `solve time\|model build\|building the model takes` |
