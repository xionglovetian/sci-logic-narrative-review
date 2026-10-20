# Methodology — where this framework comes from

This page exists because a review framework that hides its assumptions is not trustworthy. It states the core thesis, the provenance of each lens, what the skill added beyond the original method, how strictness is tuned, and — importantly — what the framework does **not** claim.

---

## 1. The core thesis

> A large share of first drafts do not fail because the experiments are insufficient, but because **the narrative chain is broken**. Scattered parameter sweeps and ablations are assembled as a pile of metrics instead of a closed loop of `discover a scientific gap → propose a targeted solution → verify causally`. Reviewers read that as an engineering trial-and-error report and recommend major revision or rejection.

This skill runs the same reasoning **backwards**. If broken narrative links are what reviewers penalize, then walking the same chain and checking each link is a predictor of where reviewers will strike.

The chain has four links, and this skill reviews them in order:

1. **Gap** — a field assumption that is treated as true but has never been systematically quantified, plus the concrete bias its failure causes.
2. **Targeted solution** — every module or strategy explicitly answers one gap from step 1. Not "to improve performance".
3. **Layered causal verification** — three experiment layers: main comparison; **capacity-matched control** (the anchor); generalization and robustness. Plus statistics, and negative results kept rather than hidden.
4. **Boundary self-limitation** — discussion states mechanism, essential difference from prior work, failure conditions, and the limits of the evaluated data range.

## 2. Where each lens comes from

| Lens | Origin in the source method | How this skill operationalizes it |
|---|---|---|
| L1 Gap reality | "Mine the field's implicit assumption; name the gap it creates." Common failure #1: opening with no field gap. | Testable criteria: does the gap point at an assumption, quantify the consequence, and carry negative evidence? (`core/gap-checklist.md` §1) |
| L2 Targeting | "Every design element answers a previously named pain point." Failure #2: the innovation hides inside a results table. | One-to-one mapping check: each module ↔ one defect (§2) |
| L3 Causal closure | "Layered experiments: main comparison / control / generalization." Failure #5: sloppy attribution, no alternative explanations excluded. | Three-layer checklist, with the capacity-matched control promoted to P0 (§3) |
| L4 Contribution separability | "Distill three independent contributions, placed in three locations." | Side-by-side comparison of placements + same-sentence test for homogeneity (§4) |
| L5 Figure layering | "Mechanism figure first; tables grouped by logic; trends visualized." | Layering criteria plus a 30-second comprehensibility standard (§5) |
| L6 Boundary self-limitation | "Proactively discuss limitations and applicability." Failure #6: discussion only replays results. | Hard test: can you find one sentence naming a failure condition? (§6) |

Two further claims from the source method became **verdict scaffolding** rather than lenses:

- **Two possible destinations** — strong control group → method-innovation paper; weak control group → evaluation-insight paper. This becomes the **P-A / P-B** verdict, with a third added: **P-C insufficient evidence**. That third path exists because the source method assumes the control experiments already exist, while a real pre-submission draft often has none. Closing that gap was necessary; otherwise a tuning report gets pushed into an innovation slot and gets rejected.
- **Five red lines** — no causal claims without controls; never fabricate, never hide negative results; wording must match evidence; prose cannot substitute for missing experiments. These became the red lines in `core/stance.md` and the wording bans in `core/report-contract.md`.

## 3. What this skill added

The source method is a **writing guide** (how to write). This skill is an **auditor** (whether what you wrote holds). Four additions:

1. **Dual-track comparison** — track A manuscript vs track B experimental ledger. The writing guide assumes the data is sound; a reviewer does not. Hence number traceability, claim-strength, and protocol-consistency checks.
2. **Severity levels and hard thresholds** — the guide says controls matter. The skill says *a missing control group is P0, and P-A is forbidden*. Importance becomes a non-negotiable verdict.
3. **A report contract** — the guide has no deliverable. The skill requires one report per round, with pinned locations, prescriptions, and pass criteria, chained into a multi-round diff.
4. **The P-C path** — "you cannot submit this yet", plus the rescue sequence: withdraw claims → downgrade positioning → resubmit.

## 4. Strictness tiers

Calibrated per occasion; the default is **standard**.

| Tier | Trigger | Adjustment |
|---|---|---|
| **Lenient** (internal pre-check) | Group meeting draft, >1 month to submission | Only P0/P1; P2/P3 collapsed into one paragraph; minimum experiment set optional |
| **Standard** (default) | 2–4 weeks before submission | All seven checklists; all severities; minimum upgrade set required |
| **Strict** (top-tier / previously rejected) | Q1 target, prior rejection, or explicit request | Adds: per-figure integrity re-check (duplicates/stitching/suspicious regularity), **full** number verification instead of sampling, a necessity audit per module ("could a simpler design do this?"), and capacity controls must align both parameter count **and** FLOPs |

### Weights by paper type

| Type | Gap | Targeting | Causal | Contribution | Figures | Boundary |
|---|---|---|---|---|---|---|
| Empirical / applied (default) | 20 | 15 | 30 | 15 | 10 | 10 |
| Pure method / algorithm | 15 | 20 | 30 | 20 | 10 | 5 |
| Evaluation / benchmark | 25 | 10 | 25 | 15 | 10 | 15 |
| Review / survey | 25 | 10 | 5 | 30 | 15 | 15 |

Hard thresholds stay unchanged — F1–F6 apply in every type (for surveys, F1 becomes "no critical synthesis").

## 5. What this framework does not claim

1. **It is not journal policy.** It predicts high-probability structural objections. It does not predict acceptance, and different journals weight different things.
2. **The weights are calibrated on empirical/applied work.** Other paper types need the table above.
3. **Capacity-matched control is not universally mandatory.** In some subfields (e.g. pure benchmark studies) it may not be required — but it is almost always *asked about*, which is why the framework treats it as the highest-frequency, highest-cost omission.
4. **The checkers check structure, not quality.** A report can pass `check_report.py` and still be a shallow review. The contract lowers that risk; it does not eliminate it.
5. **A verdict can be overturned — by evidence, not by request.** That is what the mandatory "why not the other two paths" section is for.

## 6. Why "zero findings" is treated as impossible

Every manuscript has unverified boundaries: scenarios untested, protocols unstated, anomalies unexplained. A report claiming zero vulnerabilities means the reviewer only looked at what it wanted to see — which is itself a review failure. The framework therefore treats "no findings" as a signal of **incomplete input**, and requires an information-gap list instead of a pass.
