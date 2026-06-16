# NoteForge

A project-local, Claude-Code-driven multi-agent system for turning **source materials
(PDFs / slides / lecture notes / past exams) or a topic** into a compiled, audited LaTeX
study note — a 复习讲义 / 复习笔记 / textbook chapter set — where every outline item is
covered and (in source mode) grounded in the source.

It packages the workflow proven by hand in `~/astro_review`, `~/intro_phil`, and
`~/Agents-Textbook-Handson`: a shared style contract, a fixed palette of colored
knowledge-boxes, parallel one-subagent-per-chapter fan-out, an audit pass, and a
`tectonic` compile-and-fix loop.

## ⚠️ 数据与版权 / Data & copyright

NoteForge 只是一套**工具**，仓库里**不附带任何课件、讲义、教材、真题或受版权保护的语料**。
你"喂"给它的源材料（课程 PPT、讲义 PDF、教材、历年试题、扫描件等）很可能受版权保护，使用前请注意：

- **先确认你对这些材料拥有合法使用权**——例如本人选课所得、授课教师/作者授权、公开许可
  （CC 等），或落入个人学习研究 / 合理使用范畴。来路不明或未经授权的材料不要使用。
- 生成的讲义是源材料的**衍生作品**：请仅用于**个人复习与学习**，不要公开分发、商用，或
  二次售卖对受版权材料的实质性再现；引用他人观点/数据时注明出处、尊重署名。
- **不要把受版权保护或涉密的源材料提交到本仓库**——`.gitignore` 已默认忽略 `sources/`
  （你的输入）与 `note/`（生成的输出）。本仓库只应保存系统本身。
- 各课程材料的版权归原作者/院校所有；你对自己输入数据的合法性与最终用途负责。

> Plainly: NoteForge ships **no** copyrighted corpus. You are responsible for having the
> right to use whatever you feed it. Keep generated notes for personal study, don't
> redistribute derivatives of copyrighted material, and never commit source corpora to
> this repo (`sources/` and `note/` are git-ignored by default).

## Use it on a new note set
```bash
cp -r agent-for-notes/.claude  ~/my-notes/.claude     # or symlink
cd ~/my-notes
mkdir -p sources && cp ~/lecture*.pdf ~/past-exam*.pdf sources/   # source mode
# then, in Claude Code:  "把 sources/ 里的材料整理成一份复习讲义"   (or a topic for topic mode)
```
The `note-orchestrator` skill triggers, builds the outline + style contract (you approve
them at the HITL gate), fans out the chapters, audits and refines them, compiles
`note/master.pdf`, and writes a coverage report.

## Architecture
```
.claude/
  skills/
    note-orchestrator/   # entry: the FRAME→DRAFT→AUDIT→REFINE→BUILD→SUMMARY controller
    note-preamble/       # outline.json -> preamble.tex + master.tex (box palette = source of truth)
      base/ profiles/    # ctexart/report bases + science|humanities|tech box palettes
    note-latex-build/    # tectonic compile + classified error report
    note-summary/        # coverage report + execution summary
  agents/
    outline-architect    # FRAME: mode detect, outline, profile, style contract
    chapter-writer       # DRAFT/REFINE: one chapter, parallel fan-out
    chapter-auditor      # AUDIT: one chapter, parallel fan-out (never edits)
  prompts/               # _plan.md (state machine), _style_contract.md (template), role contracts
  memory/notes_hints.md  # advisory recurring LaTeX/style fixes
docs/superpowers/specs/  # design spec
```

## Two modes (auto-detected in FRAME)
- **source** — `sources/` has material → cover its outline item-by-item, cite the source.
- **topic** — only a topic/TOC → generate, optional web augmentation.

## Style profiles
`science` (concept/derive/worked/estimate/trap/focus) · `humanities`
(concept/argument/objection/thinker/quote/distinction) · `tech`
(def/idea/demo/pitfall). All share common review/exam/key/note boxes. Add your own under
`note-preamble/profiles/`.

## Per-run layout (created in the note project)
```
note/ _run/{job,outline,style_contract,audit/,refine_ledger,build_report}
      preamble.tex master.tex chapters/chNN_slug.tex
      master.pdf coverage_report.md execution_summary.md
sources/   # your input PDFs (source mode)
```

Requires `tectonic` on PATH (+ a CJK font for `zh`).
