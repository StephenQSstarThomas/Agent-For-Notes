---
name: note-orchestrator
description: Use when the user wants to turn source materials (PDFs, slides, lecture notes, past exams) OR a topic/outline into a compiled, audited LaTeX study note — a 复习讲义 / 复习笔记 / textbook chapter set / exam-prep note. Triggers include "把这些PDF整理成复习讲义", "做一份 X 的复习笔记/讲义", "generate LaTeX notes on X", "turn these slides into a note/textbook", "整理成 tex 笔记". Drives the FRAME→DRAFT→AUDIT→REFINE→BUILD→SUMMARY pipeline via subagents.
---

# note-orchestrator

Top-level controller for NoteForge: produces a colored-box, chapter-structured LaTeX
study note where (in source mode) every outline item is covered and grounded in the
source material. Mirrors the proven `astro_review` fan-out-with-audit workflow.

## When to use
- "把这些 PDF / slides / 讲义 / 真题整理成一份复习讲义" (source mode)
- "做一份 / 出一份 X 的复习笔记 / tex 笔记 / 教材" (topic mode if no files given)
- Any request to produce a multi-chapter LaTeX note from materials or a topic.

**Not** for: editing one existing `.tex` by hand, or a single short answer (just answer).

## How to run
> **`$BUNDLE`** = the folder this bundle is installed in — `.claude/` for Claude Code, or
> `.codex/` / `.cursor/` if you copied it there. Substitute it in every path/command below.

Follow `$BUNDLE/prompts/_plan.md` exactly — it is the authoritative state machine. In short:

1. **FRAME** — dispatch the `outline-architect` agent (writes `_run/job.json`,
   `_run/outline.json`, `_run/style_contract.md`), then run note-preamble:
   `python $BUNDLE/skills/note-preamble/build_preamble.py --outline note/_run/outline.json --out note/`.
2. **HITL gate** — if `job.json.hitl`, show the user the chapter list + coverage counts +
   allowed environments; let them edit before fan-out. Re-run note-preamble if changed.
3. **DRAFT** — dispatch one `chapter-writer` per chapter **in parallel** (all Agent calls in
   one message), each carrying its outline slice + a pointer to the style contract.
4. **AUDIT** — dispatch one `chapter-auditor` per chapter **in parallel** → `_run/audit/*`.
5. **REFINE** — for each `verdict == revise`, re-dispatch its writer in revise mode with the
   issue list, then re-audit. Cap per `job.loop_budget.refine_per_chapter`; then accept-with-disclosure.
6. **BUILD** — run note-latex-build; fix blockers per its report (edit the chapter or
   `preamble.tex`); cap per `job.loop_budget.build_fix`.
7. **SUMMARY** — run note-summary; report `master.pdf` path, coverage %, unresolved items.

## Quick reference
| Need | Use |
|---|---|
| build outline + contract + preamble | `outline-architect` agent + `note-preamble` skill |
| write/revise a chapter | `chapter-writer` agent (parallel fan-out) |
| audit a chapter | `chapter-auditor` agent (parallel fan-out) |
| compile + classify errors | `note-latex-build` skill |
| coverage + execution report | `note-summary` skill |

## Common mistakes
- Dispatching writers sequentially — fan out in ONE message for parallelism.
- Skipping the HITL gate — the outline+contract is where note quality is set; confirm it.
- Re-running upstream phases on a single failure — loop only the failing chapter/artifact.
- Letting a loop run forever — always decrement the ledger; accept-with-disclosure at zero.
- Inventing data in source mode — every fact traces to `sources/`; the auditor enforces this.

## Memory
Consult and append `$BUNDLE/memory/notes_hints.md` with recurring LaTeX/style fixes so later
runs avoid them.
