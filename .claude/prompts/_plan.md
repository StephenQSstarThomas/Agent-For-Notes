# NoteForge orchestration plan (the state machine note-orchestrator follows)

Six phases on one spine. A loop controller routes each phase result
(advance / loop / accept) against a capped ledger so the run always terminates.

```
FRAME ─▶ [HITL gate] ─▶ DRAFT ─▶ AUDIT ─▶ REFINE ─▶ BUILD ─▶ SUMMARY
                          ▲          │        │         │
                          └──────────┴─ loop ─┘   loop ─┘
```

Work happens in a `note/` dir inside the user's project; sources in `sources/`.

## FRAME
- Dispatch the **outline-architect** agent. It writes `_run/job.json`, `_run/outline.json`,
  `_run/style_contract.md`.
- Run `note-preamble`: `python .claude/skills/note-preamble/build_preamble.py
  --outline note/_run/outline.json --out note/` → `preamble.tex`, `master.tex`,
  empty `chapters/`.
- **HITL gate** (if `job.json.hitl`): show the user the chapter list + coverage counts +
  the allowed-environment list; let them edit `outline.json`/`style_contract.md` before
  fan-out. Re-run note-preamble if the outline changed.

## DRAFT (fan-out)
- Dispatch **one chapter-writer per chapter IN PARALLEL** (all Agent calls in a single
  message). Each dispatch carries: the chapter's outline entry, a pointer to
  `style_contract.md`, and (source mode) the source spans to read.
- A writer that returns null/fails → re-dispatch once, then mark for the audit loop.

## AUDIT (fan-out)
- Dispatch **one chapter-auditor per chapter IN PARALLEL**. Each writes
  `_run/audit/<id>.json` with `verdict` + issues.

## REFINE (bounded loop)
- For each chapter whose audit `verdict == revise`: re-dispatch its **chapter-writer in
  revise mode** with the issue list. Then re-audit just that chapter.
- Ledger: `_run/refine_ledger.json` counts attempts per chapter. Max
  `job.loop_budget.refine_per_chapter` (default 2). On exhaustion, force-accept the chapter
  and record the unresolved blockers (surface them in the summary).

## BUILD (bounded loop)
- Run `note-latex-build`: `python .claude/skills/note-latex-build/build.py --note-dir note/`.
- If `build_report.json.ok` and no blockers → advance.
- Else fix the source per `build_report.blockers[].hint` (edit the offending chapter or
  `preamble.tex`), append any new lesson to `.claude/memory/notes_hints.md`, and rebuild.
  Max `job.loop_budget.build_fix` (default 3) fix→rebuild cycles, then stop and report the
  remaining blockers honestly.

## SUMMARY
- Run `note-summary` → `coverage_report.md` (per-chapter outline-item coverage + audit
  verdicts + line counts) and `execution_summary.md` (phase log, file index, unresolved items).
- Final message: path to `master.pdf`, coverage %, any force-accepted chapters / remaining
  build warnings.

## Loop controller rules
- Never restart a completed upstream phase wholesale; loop only the failing chapter/artifact.
- Every loop decrements the relevant ledger budget; at zero, accept-with-disclosure and move on.
- Record each phase transition in `execution_summary.md` so the run is auditable.
