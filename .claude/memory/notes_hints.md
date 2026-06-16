# NoteForge advisory memory — recurring LaTeX / style fixes

Human-readable hints. FRAME (architect) and chapter-writers consult this; the auditor and
the BUILD loop append new lessons. Advisory, not law — verify before applying.

## LaTeX traps (seeded from astro_review / Agents-Textbook experience)
- Prose `%` must be `\%`; prose `_` must be `\_`; prose `&` must be `\&`. In math/align/tabular
  they are normal. This is the single most common build blocker.
- Every colored box is `breakable` — fine across pages, but `\begin{env}`/`\end{env}` must
  balance within a chapter. An unbalanced box reports as "ended by \end{document}".
- Boxes with a required argument (e.g. `conceptbox{term}`, `exambox{label}`) crash if called
  with none. No-arg boxes (`trapbox`, `focusbox`, `keybox`, `reviewbox`, `ideabox`,
  `pitfallbox`) take no `{}`.
- Do not use `physics`-package macros except the provided `\pdv` / `\dv`.
- zh builds use `ctexart`; tectonic needs a CJK font available (e.g. a Fandol/Noto/Droid CJK
  font). If "Font ... does not contain", install a CJK font or switch `lang` handling.
- Writers must emit body fragments only — a stray `\documentclass`/`\usepackage` in a chapter
  breaks the build.

## Style lessons
- In source mode, a concept box per outline term + item-by-item coverage is what makes the
  note exam-useful; thin chapters are the top audit failure.
- Keep the chapter recap (`reviewbox`) to one-line must-memorize facts.

<!-- BUILD/auditor: append dated lessons below this line -->
