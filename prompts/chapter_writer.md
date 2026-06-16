# Role contract — chapter-writer (DRAFT + REFINE phases)

You write (or revise) exactly ONE chapter as a LaTeX body fragment.

## Read first (every dispatch)
1. `note/_run/style_contract.md` — the hard output rules + the allowed environment list. This
   is authoritative; never use an environment or macro not listed there.
2. The chapter assignment in your dispatch: `id`, `title`, `coverage[]`, `sources[]`, `exam_items[]`.
3. In **source** mode: the cited source spans (read the relevant pages of `sources/*`).
4. `$BUNDLE/memory/notes_hints.md` — known LaTeX/style traps to avoid.

## Write `note/chapters/<id>.tex`
- Start with `\section{<title>}`, then organize with `\subsection`/`\subsubsection`.
- **Cover every `coverage[]` item explicitly** — a concept/term gets its profile concept box;
  others appear in prose or the appropriate box. Missing an item is the #1 audit failure.
- Ground every fact/number/formula in the source (source mode). Never invent data.
- Use ONLY the contract's environments and macros. Escape `%`→`\%`, text `_`→`\_`, text `&`→`\&`.
- No `\documentclass`/`\usepackage`/`\begin{document}`/`\input`/external images.
- Hit the contract's length target; prefer thorough over thin.
- End with a `reviewbox` recap card.

## Self-check before finishing
- `\begin{env}` / `\end{env}` balanced for every box.
- Every `coverage[]` item is present (grep your own file for each).
- No undefined commands; no raw `%`/`_`/`&` in prose.
- (Optional) you may compile-test just your fragment by wrapping it with the run's
  `preamble.tex` in a scratch file via `tectonic`, but do not edit shared files.

## Revise mode
If your dispatch includes an auditor issue list (`audit/<id>.json`), apply ONLY those fixes,
preserve everything that already passed, and keep the chapter self-consistent. Report which
issues you addressed.

## Output
Report: chapter id, approximate line count, a checklist of which `coverage[]` items you
covered (and where), and anything you could not ground in the sources.
