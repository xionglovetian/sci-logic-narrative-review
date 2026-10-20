# SCI Logic & Narrative Review

> **Your paper is not rejected because the experiments are weak. It is rejected because the story is broken — and nobody told you where.**

A pre-submission peer review, simulated. Not a proofreader, not a polisher: an auditor that walks the entire narrative chain of your manuscript, hunts structurally for the holes a reviewer will find, and **hands you a written verdict report for every review round** — with evidence-pinned locations, actionable fixes, and pass criteria for the next round.

**中文版：[README.zh-CN.md](README.zh-CN.md)** · **方法论溯源：[docs/METHODOLOGY.md](docs/METHODOLOGY.md)** · **示例报告：[examples/demo-report.md](examples/demo-report.md)**

---

## Why this exists

Most drafts that get desk-rejected or bounced at major revision do not lack experiments. They lack **narrative closure**: scattered ablations and parameter sweeps are presented as a pile of numbers instead of a `discover the gap → propose a targeted solution → verify causally` chain. The reviewer reads a tuning report, calls the scientific contribution weak, and recommends rejection.

> A 90/100 manuscript can be blocked by one missing control group. A claim of "4% improvement" may be nothing but 4% more parameters. **Which of these is yours?**

This skill is designed to answer that — before a reviewer does.

---

## The 9 advantages

### 1. A report is mandatory — silence is impossible

The skill has one non-negotiable rule: **a review without a report is not a review**. Zero vulnerabilities is treated as an impossibility; if nothing is found, the only legitimate explanation is incomplete input, and the report must say so. You never get "looks fine overall" — you get a verdict.

### 2. Every finding is pinned to real evidence

Each finding is a card with eight mandatory fields: category, severity, **location (section + quoted text)**, evidence, *the reviewer's own sentence*, why it fails, the fix, and the pass criterion. A vague hunch with no locatable position is deleted, not softened. The result is a report you can argue with — or fix from.

### 3. Six lenses, in a dependency order

Lenses run in an order where each depends on the previous one, so conclusions stay focused:

| Lens | What it audits | Typical failure caught |
|---|---|---|
| **L1 Gap reality** | Does the intro name an *implicit field assumption* that no one has quantified? Does it state the concrete bias that assumption causes? | Opens with the dataset and model; gap is "existing methods are inaccurate" |
| **L2 Targeting** | Does every module map to a specific L1 defect? | Modules appear from nowhere; motivation written as "to improve performance" |
| **L3 Causal closure** | Are all three experiment layers present — main comparison / **capacity-matched control** / generalization & robustness — with statistics? | Attribution to design while parameter count also went up |
| **L4 Contribution separability** | Are the three contributions independent, each with its own supporting experiment, placed consistently in abstract / intro / conclusion? | Three contributions that are the same sentence reworded |
| **L5 Figure & table layering** | Does the mechanism figure come before the number dump? Are tables grouped by logic? Are significance marks present? | One giant table mixing ablations, comparisons and robustness |
| **L6 Boundary self-limitation** | Does the discussion state failure conditions, data range, and essential difference from prior work? | Discussion that only replays results; "general/universal" claims with no cross-domain evidence |

### 4. Dual-track comparison — claims versus the lab notebook

This is the hardest check and the one nearly every writing guide omits. The review runs **track A: the manuscript** against **track B: the experimental record** on three axes:

- **Number track** — can every number (dataset, split, seed policy, evaluation protocol) be found in the ledger under the same protocol?
- **Claim track** — does every verb match the strength of the evidence? `significantly` requires a test; `prove / due to` requires a capacity-matched control; `state-of-the-art` requires current, same-protocol comparison.
- **Protocol track** — same metric, same value, everywhere: abstract, tables, body text, captions.

Missing track B is never treated as "numbers are probably fine" — it is reported as a **P0 no-evidence-base** finding, and the path verdict is capped accordingly.

### 5. A three-way narrative verdict, not a vague score

Review ends with exactly one verdict, plus why the other two are excluded, plus the **minimum cost to upgrade one tier**:

| Path | Trigger | Positioning | Likely outcome |
|---|---|---|---|
| **P-A Method-innovation** | Capacity-matched control clearly weaker than the proposal, and significant | Method contribution with causal closure | Accept after major revision |
| **P-B Evaluation-insight** | Control missing or gap tiny, but the gap is real and negative results are solid | Rigorous empirical-evaluation paper, weighted to scientific finding | Accept after moderate-to-minor revision |
| **P-C Insufficient evidence** | Causal claim without control, untraceable numbers, hidden negative results | Add the missing experiment, or withdraw the claim | Reject |

Most real drafts belong in **P-B**. Insisting on P-A without a capacity-matched control is the single most common way a publishable paper gets rejected. This skill names that path and gives you the downgrade.

### 6. Scores that cannot override the thresholds

Seven weighted dimensions total 100 (gap 20 / targeting 15 / causal closure 30 / contribution 15 / figures 10 / boundary 10), with number traceability as a **mandatory deduction**, not a bonus. Then the verdict checks **hard thresholds first**: six fatal findings (F1–F6) block P-A regardless of the score. A 90-point paper missing a capacity-matched control is a P-C paper, and the report says so in one line.

### 7. A fix, not just a complaint

Every finding carries an executable prescription, and each of the three paths comes with a section-by-section rewrite playbook, a **minimum experiment set** that actually changes the verdict, and the specific report items that would flip. "Add more experiments" is forbidden — only experiments that can flip the path are allowed.

### 8. Multi-round closure tracking

Findings get stable IDs (`V-01` …) across rounds. From round 2 on, a **closure diff table** is mandatory: fixed / partially fixed / not fixed / appeal upheld — with the new evidence. Partial fixes must state what is still missing. This is the only audit trail that shows whether the paper actually improved or just changed.

### 9. Contract enforcement in code

Two dependency-free Python checkers make the contract machine-checkable:

```bash
python skills/sci-logic-narrative-review/scripts/check_report.py   examples/demo-report.md
python skills/sci-logic-narrative-review/scripts/check_manifest.py
```

`check_report.py` validates 12 classes of hard requirements — metadata fields, all eleven sections, placeholder residue, the eight card fields, legal severities, **at least one P1/P2 finding**, ≥8 number-verification rows with legal verdicts, **verdict/outcome self-consistency (P-C can never be paired with "minor revision")**, banned soft phrases, the closure diff table for non-first rounds, the three-part boundary statement, and the filename convention. A report that fails self-check is not delivered.

---

## How it differs from generic AI rewriting

| | Generic "polish my paper" | SCI Logic & Narrative Review |
|---|---|---|
| Output | Rewritten prose | Verdict + findings + prescriptions + pass criteria |
| Ground truth | The manuscript alone | Manuscript **plus** experimental ledger (dual-track) |
| Missing evidence | Smoothed over | Reported as P0, verdict capped |
| Finding quality | "Could be clearer" | Section + quote + reviewer sentence + fix |
| Zero findings | Plausible | Explicitly impossible |
| Multi-round | Starts over | Stable IDs + closure diff |
| Consistency | Trust the writer | Machine-checked contract |

---

## The non-negotiables

The skill refuses to trade integrity for acceptance:

1. Never invent experiments, controls, or results.
2. Never hide negative results — they are load-bearing evidence for the gap.
3. Never let wording substitute for evidence. When the closure isn't there, **downgrade the narrative**.
4. Never push for P-A without a capacity-matched control.
5. Never end a review with "suggest polishing".

> A downgraded paper is a paper that passes. A paper held up by adjectives is a paper that gets rejected.

---

## Install

The skill is a self-contained folder: `SKILL.md` + `manifest.yaml` + `core/` + `references/` + `assets/` + `scripts/`. It is written for DeepSeek Harness (DSH) skill loaders; the content is plain Markdown and portable to any agent that reads a `SKILL.md`.

```bash
git clone https://github.com/xionglovetian/sci-logic-narrative-review.git
cd sci-logic-narrative-review

# user-level (all projects) — bash / macOS / Linux / Git Bash
mkdir -p ~/.agents/skills
cp -r skills/sci-logic-narrative-review ~/.agents/skills/

# project-level (this project only)
mkdir -p /path/to/your/project/.dsh/skills
cp -r skills/sci-logic-narrative-review /path/to/your/project/.dsh/skills/
```

```powershell
# Windows PowerShell equivalent
git clone https://github.com/xionglovetian/sci-logic-narrative-review.git
cd sci-logic-narrative-review
New-Item -ItemType Directory -Force "$env:USERPROFILE\.agents\skills" | Out-Null
Copy-Item -Recurse -Force "skills\sci-logic-narrative-review" "$env:USERPROFILE\.agents\skills\"
```

Then ask, in Chinese or English:

- 「用 SCI逻辑叙事审查 审一下这篇稿」
- "Review this manuscript before submission — what will the reviewer attack?"

First round needs: manuscript + figures/tables (with captions) + target journal. **Provide the experimental ledger to get the full dual-track comparison** — without it, the report is marked `G1 partial` and P-A is disallowed.

---

## Repository layout

```
skills/sci-logic-narrative-review/    the skill (drop into any skill loader)
  SKILL.md                            router: pipeline, six lenses, output contract
  manifest.yaml                       declarative load table (stage → files)
  core/stance.md                      reviewer stance, P0–P3, red lines, self-failure modes
  core/flow.md                        seven-step sequence, mandatory output per step
  core/gap-checklist.md               7 finding classes, 60+ checkable items, F1–F6
  core/rubric.md                      weighted scoring, hard thresholds, path verdicts
  core/report-contract.md             mandatory report structure and wording bans
  references/judgment-paths.md        per-section rewrite playbooks for P-A / P-B / P-C
  references/methodology-source.md    provenance, strictness tiers, type-based weights
  references/input-intake.md          intake, quote extraction, sampling, round diffs
  assets/report-template.md           the report skeleton
  assets/example-report.md            a filled, passing report
  scripts/check_report.py             report contract checker
  scripts/check_manifest.py           load-table integrity checker
examples/demo-report.md               publishable demo report
docs/METHODOLOGY.md                   where the framework comes from and its limits
index.html                            landing page (served by GitHub Pages)
```

## Honest limits

- This is a **heuristic review framework**, not a journal's official policy. It predicts high-probability structural objections, not acceptance.
- Weights are calibrated for empirical / applied research; theory, pure-method and review papers should shift weights (see `references/methodology-source.md`).
- The checkers validate **structure and self-consistency, not review quality**. A technically passing report can still be a shallow review — the contract reduces that risk, it does not eliminate it.
- The skill diagnoses. It does not write your paper for you.

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, tighten the thresholds.

## Contributing

Missing a finding class your field always gets attacked on? Add it to `core/gap-checklist.md` with a severity and a pass criterion, keep the eight card fields intact, and make sure `check_report.py` still passes on `examples/demo-report.md`. See [CONTRIBUTING.md](CONTRIBUTING.md).
