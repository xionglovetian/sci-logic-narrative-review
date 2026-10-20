# Contributing

This repository is a review **framework**, so contributions are mostly new checks, new verdict criteria, and better wording — not new prose styles.

## Good contributions

1. **A new finding class** your field is always attacked on. Add it to `core/gap-checklist.md` with:
   - a checkable item (a question that can be answered yes/no from the manuscript),
   - the severity it triggers (P0/P1/P2/P3),
   - what a pass looks like.
2. **A sharper hard threshold** in `core/rubric.md`. If a verdict rule is ambiguous, show the two papers it would judge differently and propose the tighter condition.
3. **A rewrite playbook** for a path in `references/judgment-paths.md` — a section-by-section mapping from the "innovation" version of a sentence to the downgraded version.
4. **Checker improvements** in `scripts/`. Keep them dependency-free (standard library only) and Windows-safe (`encoding="utf-8"`, no ANSI assumptions).

## Rules the framework itself obeys

- **Every finding must be locatable.** Section + quoted text + evidence. If a check cannot be pinned to text, it does not belong in the checklist.
- **No soft language.** Contributions may not introduce "consider", "might be improved", "suggest polishing" as a finding. See the bans in `core/report-contract.md`.
- **Severity must map to an editorial outcome.** P0 = reject, P1 = must appear in the review, P2 = will be asked about, P3 = cosmetic.
- **Never weaken a threshold to make a demo pass.** Fix the demo instead.

## Before opening a PR

```bash
python skills/sci-logic-narrative-review/scripts/check_manifest.py
python skills/sci-logic-narrative-review/scripts/check_report.py examples/demo-report.md
```

Both must pass (a filename WARN is fine for the demo). If you changed `assets/report-template.md`, make sure `examples/demo-report.md` still satisfies the new contract — and if you added a mandatory field, update the template, the checker, and the demo together.

## Translations

`README.md` is English and `README.zh-CN.md` is Chinese. Keep the two versions structurally parallel: same sections, same tables, same claims. Do not add a claim to one that the other cannot support.

## Reporting a problem

Open an issue with: the paper type, the target journal tier, the finding you expected the framework to catch, and the text it missed. **A concrete miss is more valuable than a general impression** — the same rule the framework applies to manuscripts.
