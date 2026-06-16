---
name: note-summary
description: Use at the end of a NoteForge run (the SUMMARY phase), or whenever the user asks "did it cover everything?", "summarize the run", or "coverage report". Cross-checks the outline against the written chapters and audit verdicts to produce coverage_report.md, and guides writing the narrative execution_summary.md. Invoked by note-orchestrator in SUMMARY.
---

# note-summary

Closes a run with two artifacts: a deterministic coverage report and a narrative execution
summary.

## Run it
(`$BUNDLE` = your install dir: `.claude/` for Claude Code, or `.codex/` / `.cursor/`.)
```bash
python $BUNDLE/skills/note-summary/summarize.py --note-dir note/
```
Writes `note/coverage_report.md`: per-chapter item count, heuristic covered/total, audit
verdict, line count, an overall coverage %, and a list of outline items not literally found
(cross-check these against the auditor — its verdict is authoritative).

## Then write `note/execution_summary.md`
A short narrative the deterministic report can't produce:
- run info (subject, mode, lang, profile, chapter count, date);
- per-phase log (FRAME → … → BUILD), including refine loops taken per chapter;
- force-accepted chapters and their unresolved blockers (be honest);
- remaining build warnings;
- file index (`master.pdf`, `master.tex`, `chapters/`, `_run/`).

## Common mistakes
- Reporting heuristic coverage as ground truth — it is a substring signal; defer to the
  auditor for real coverage.
- Claiming success while blockers remain in `build_report.json` — state them plainly.
