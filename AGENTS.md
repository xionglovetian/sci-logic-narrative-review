# AGENTS.md — SCI逻辑叙事审查 (sci-logic-narrative-review)

This repository distributes one Agent Skill. It works in **Claude Code, Codex (CLI / IDE / desktop), DeepSeek Harness, and any host that reads `SKILL.md`** — all four read the same `skills/sci-logic-narrative-review/SKILL.md`. Platform-specific packaging (plugin manifests, marketplaces) is documented in [PLATFORMS.md](PLATFORMS.md).

If you are an agent and the user asks for a **pre-submission review of a manuscript** — 投稿前自审、模拟审稿、挑漏洞、会不会被拒、审稿人会问什么 — follow this skill.

## Where the skill lives

- Skill entry: `skills/sci-logic-narrative-review/SKILL.md` (relative to this repo root)
- Its own directory: `skills/sci-logic-narrative-review/`
- If the skill was installed elsewhere, use the path the user points at; all references inside `SKILL.md` are relative to that directory.

## What this skill does

It runs a **simulated first-round peer review** and **must produce a written report every round**. It does not polish, rewrite, or encourage; it diagnoses.

Three non-negotiable rules:

1. **Zero findings is impossible.** A review must yield at least one P1/P2 finding with a pinned location. If genuinely nothing is found, the only legitimate explanation is incomplete input — output an information-gap list, still produce a report, never declare a pass.
2. **Every finding must be locatable.** Section + quoted text + ledger/table/figure id. A vague hunch with no location is deleted, not softened.
3. **Only existing evidence is reviewed.** Never invent experiments, numbers, or controls. When the evidence is insufficient, **downgrade the narrative** — that is the core action, not an option.

## Six lenses (run in this order; each depends on the previous)

| Lens | What it checks |
|---|---|
| **L1 Gap reality** | Does the introduction name an implicit field assumption that nobody has quantified, and the concrete bias it causes? (Failure: opens with dataset/model; gap is "existing methods are inaccurate".) |
| **L2 Targeting** | Does every module/strategy answer one specific L1 defect? (Failure: motivation written as "to improve performance".) |
| **L3 Causal closure** | Are all three layers present — main comparison, **capacity-matched control**, generalization/robustness — with statistics? (Failure: gain attributed to design while parameter count also rose.) |
| **L4 Contribution separability** | Are the three contributions independent, each with its own supporting experiment, placed consistently in abstract / intro / conclusion? |
| **L5 Figure & table layering** | Mechanism figure before number dump; tables grouped by logic; significance marks present. |
| **L6 Boundary self-limitation** | Does the discussion state failure conditions, evaluated data range, and the essential difference from prior work? |

## Dual-track comparison (the hardest check)

Compare **track A (manuscript)** against **track B (experimental ledger)** on three axes:

- **Number track** — can every number be found in the ledger under the same protocol (dataset, split, seed policy, evaluation protocol)?
- **Claim track** — does every verb match evidence strength? `significantly` needs a test; `prove / due to` needs a capacity-matched control; `state-of-the-art` needs current, same-protocol comparison.
- **Protocol track** — same metric, same value, same protocol across abstract, tables, body, captions.

**Missing track B is never treated as "numbers are probably fine"** — record a **P0 no-evidence-base** finding and cap the verdict accordingly.

## Severity and the three-way verdict

Severity maps to editorial outcome: **P0** reject · **P1** the reviewer will write a paragraph · **P2** the reviewer will ask · **P3** cosmetic.

Exactly one verdict per review, plus why the other two are excluded and the minimum cost to upgrade:

| Path | Trigger | Positioning | Likely outcome |
|---|---|---|---|
| **P-A Method-innovation** | Capacity-matched control clearly weaker, and significant | Method contribution + causal closure | Accept after major revision |
| **P-B Evaluation-insight** | Control missing or gap tiny, but the gap is real and negative results are solid | Rigorous empirical-evaluation paper | Accept after moderate–minor revision |
| **P-C Insufficient evidence** | Causal claim without control, untraceable numbers, hidden negative results | Add the experiment or withdraw the claim | Reject |

Scoring cannot override the thresholds: seven weighted dimensions total 100, with number traceability as a **mandatory deduction**, and six fatal findings (F1–F6) block P-A regardless of score.

## Report contract (mandatory, every round)

Write to the manuscript's directory as:

```
审稿报告_SCI逻辑叙事审查_<YYYYMMDD>_r<N>.md
```

Must contain: metadata (8 fields) · verdict summary · fatal-finding list · score table · **finding cards (8 fields each: category / severity / location / evidence / reviewer's sentence / why it fails / fix / pass criterion)** · number-verification table (≥8 rows) · claim-strength escalation list · positive assets · path-verdict reasoning · ordered next steps · closure diff table (rounds ≥ 2) · boundary statement (covered / not covered / out of scope).

Wording bans: "overall quality is fine", "suggest polishing", "consider adding more experiments", "the authors presumably realize".

## Verify a report

```bash
python skills/sci-logic-narrative-review/scripts/check_report.py <report.md>
python skills/sci-logic-narrative-review/scripts/check_manifest.py
```

A report that fails self-check is not delivered. `check_manifest.py` validates the DSH load table; on other hosts it is informational only.

## Read next

For the full procedure, load these from the skill directory, in order:

1. `SKILL.md` — router, pipeline, output contract, discipline
2. `core/stance.md` — reviewer stance, P0–P3, red lines
3. `core/flow.md` — seven-step execution, mandatory output per step
4. `core/gap-checklist.md` — seven finding classes, 60+ checkable items, F1–F6
5. `core/rubric.md` — scoring, hard thresholds, path verdicts
6. `core/report-contract.md` — report structure and wording bans
7. `assets/report-template.md` — the report skeleton
8. `references/judgment-paths.md` — per-path rewrite playbooks (as needed)
