---
name: note-latex-build
description: Use when a NoteForge note needs to be compiled to PDF and its LaTeX errors triaged — i.e. the BUILD phase, or any time the user asks to "build/compile the note", "render master.pdf", or "fix the LaTeX errors". Runs tectonic on master.tex and classifies the log into blockers vs cosmetic warnings with a fix hint per error. Invoked by note-orchestrator in BUILD.
---

# note-latex-build

Compile + triage. It compiles and reports; it does NOT edit `.tex` — the calling agent reads
the report and fixes the source, then re-runs.

## Run it
(`$BUNDLE` = your install dir: `.claude/` for Claude Code, or `.codex/` / `.cursor/`.)
```bash
python $BUNDLE/skills/note-latex-build/build.py --note-dir note/
```
Compiles `note/master.tex` with `tectonic`, writes `note/_run/build_report.json`, prints a
PASS/blockers summary. Exit 0 if a PDF was produced, 1 if compile failed.

## Report
`build_report.json` has `ok`, `n_blockers`, `n_warnings`, `blockers[]`/`warnings[]` (each
with `kind`, `match`, and a `hint` telling you where to look), and `log_tail`.

| kind | typical fix |
|---|---|
| undefined_macro / undefined_environment | writer used a non-contract command/env — restore to an allowed one |
| unbalanced_env / runaway_argument | balance `\begin`/`\end`; find the missing `}` or stray `%` |
| math_mode / stray_ampersand | escape `\_` / `\&` in prose, or wrap math in `$...$` |
| font_missing | install/select a CJK font for ctexart (zh) — blocks the build |
| font_glyph | a glyph fell back (cosmetic) — only act if a CJK char renders as tofu |
| undefined_ref / undefined_cite / overfull | cosmetic warnings — fix if cheap, else leave |

## Loop
Fix → rerun, bounded by `job.loop_budget.build_fix` (default 3). Append any new lesson to
`$BUNDLE/memory/notes_hints.md`. If blockers remain at the cap, stop and report them honestly
— do not claim success.

## Common mistakes
- "Fixing" a cosmetic overfull warning by hacking content — leave warnings unless trivial.
- Editing the wrong file — `match`/`hint` + the log tail point at the offending chapter.
