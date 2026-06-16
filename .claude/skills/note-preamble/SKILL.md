---
name: note-preamble
description: Use when a NoteForge run needs its LaTeX scaffold generated or regenerated — i.e. after outline-architect has written _run/outline.json, or whenever the chapter list, language, or style profile changes. Deterministically emits preamble.tex (the colored-box palette every chapter-writer is constrained to) and master.tex (with one \input per chapter). Invoked by note-orchestrator in FRAME.
---

# note-preamble

Deterministic generator: `outline.json` → `preamble.tex` + `master.tex`. It is the single
source of truth for the box palette, so the preamble, the style contract, and the writers
can never drift apart.

## Run it
```bash
python .claude/skills/note-preamble/build_preamble.py \
    --outline note/_run/outline.json --out note/
```
Writes `note/preamble.tex` (= `base/preamble_<lang>.tex` + `profiles/<profile>.tex`),
`note/master.tex` (filled `base/master.tmpl`), and an empty `note/chapters/`. It prints the
profile's allowed-environment list — paste that into `style_contract.md`.

## Style profiles (the discipline box palette)
| profile | content boxes (on top of common review/exam/key/note) |
|---|---|
| science | `conceptbox{}` `derivebox{}` `workedbox{}` `estbox{}` `trapbox` `focusbox` |
| humanities | `conceptbox{}` `argumentbox{}` `objectionbox{}` `thinkerbox{}` `quotebox{}` `distinctionbox{}` |
| tech | `defbox{}` `ideabox` `demobox{}` `pitfallbox` |

`lang`: `zh` → ctexart base · `en` → report+fontspec base. Built with `tectonic`.

## Extending
Add a new discipline by dropping `profiles/<name>.tex` (define `\newtcolorbox`es + a header
comment listing them) and adding `<name>` to `KNOWN_PROFILES` in `build_preamble.py`. Common
boxes live in `base/preamble_*.tex`; shared math macros too.

## Common mistakes
- Editing `preamble.tex` by hand and losing it on regen — change `base/` or `profiles/` instead.
- A chapter `id` that isn't an ascii `chNN_slug` — it becomes the filename; keep it clean.
- Forgetting to re-run after the user edits the outline at the HITL gate.
