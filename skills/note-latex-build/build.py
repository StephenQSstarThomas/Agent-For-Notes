#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
note-latex-build — compile master.tex with tectonic and classify the log.

Deterministic: it compiles and reports. It does NOT edit .tex files — the
calling agent reads the report and fixes the source (then re-runs this).

Usage:
  python build.py --note-dir note/ [--report note/_run/build_report.json]

Exit code 0 = PDF produced (even with warnings); 1 = compile failed.
"""
import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys

# (regex, kind, hint) — hint tells the agent where to look.
PATTERNS = [
    (r"! Undefined control sequence", "undefined_macro",
     "A \\command is undefined. Check spelling, or it belongs to a package/box not in preamble.tex."),
    (r"Environment (\w+) undefined", "undefined_environment",
     "A \\begin{env} is not defined. Writers may only use environments in style_contract.md."),
    (r"! LaTeX Error: \\begin\{(\w+)\} on input line \d+ ended by", "unbalanced_env",
     "A box/environment \\begin has no matching \\end (or they are crossed). Balance them per chapter."),
    (r"Runaway argument", "runaway_argument",
     "Usually a missing } or a stray % / unescaped special char swallowing text."),
    (r"! Missing \$ inserted", "math_mode",
     "Math used outside $...$ (often a stray _ or ^ in text). Escape \\_ in prose."),
    (r"! Misplaced alignment tab character &", "stray_ampersand",
     "An & outside align/tabular. Escape it as \\& in prose."),
    (r"LaTeX Warning: Reference `([^']+)' on page", "undefined_ref",
     "A \\ref/\\eqref to a missing \\label. Add the label or remove the ref."),
    (r"LaTeX Warning: Citation `([^']+)'", "undefined_cite",
     "A \\cite key not in the .bib. Fix the key or add the reference."),
    (r"! Package fontspec error|Font .* (?:cannot be found|not found)", "font_missing",
     "A required font is unavailable (often CJK). Install/select a CJK font for ctexart."),
    (r"Font .* does not contain (?:a |the )?", "font_glyph",
     "A glyph fell back / is missing in the chosen font. Cosmetic unless a CJK char shows as tofu."),
    (r"Overfull \\hbox \(([\d.]+)pt", "overfull",
     "Line too wide (cosmetic). Often a long unbreakable token / URL / inline code."),
    (r"! LaTeX Error: File `([^']+)' not found", "missing_file",
     "An \\input/\\includegraphics target is missing. Check chapters/ filenames vs outline ids."),
]


def classify(log_text):
    findings = []
    for rx, kind, hint in PATTERNS:
        for m in re.finditer(rx, log_text):
            findings.append({"kind": kind, "match": m.group(0)[:160], "hint": hint})
    # de-dup by (kind, match)
    seen, uniq = set(), []
    for f in findings:
        k = (f["kind"], f["match"])
        if k not in seen:
            seen.add(k)
            uniq.append(f)
    return uniq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--note-dir", required=True)
    ap.add_argument("--report", default=None)
    args = ap.parse_args()

    note_dir = pathlib.Path(args.note_dir).resolve()
    master = note_dir / "master.tex"
    if not master.exists():
        sys.stderr.write(f"[note-latex-build] master.tex not found in {note_dir}\n")
        sys.exit(1)
    if not shutil.which("tectonic"):
        sys.stderr.write("[note-latex-build] tectonic not on PATH\n")
        sys.exit(1)

    report_path = pathlib.Path(args.report) if args.report else note_dir / "_run" / "build_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    proc = subprocess.run(
        ["tectonic", "--keep-logs", "--print", master.name],
        cwd=str(note_dir), capture_output=True, text=True,
    )
    log_text = proc.stdout + "\n" + proc.stderr
    pdf = note_dir / "master.pdf"
    ok = pdf.exists() and proc.returncode == 0
    findings = classify(log_text)
    # A produced PDF (returncode 0) means nothing blocked the build — everything is a
    # warning. Only a failed compile yields blockers (the non-cosmetic findings).
    warn_kinds = {"overfull", "undefined_ref", "undefined_cite", "font_glyph"}
    if ok:
        blockers, warnings = [], findings
    else:
        blockers = [f for f in findings if f["kind"] not in warn_kinds]
        warnings = [f for f in findings if f["kind"] in warn_kinds]

    report = {
        "ok": ok,
        "returncode": proc.returncode,
        "pdf": str(pdf) if pdf.exists() else None,
        "n_blockers": len(blockers),
        "n_warnings": len(warnings),
        "blockers": blockers,
        "warnings": warnings,
        "log_tail": log_text.strip().splitlines()[-40:],
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    status = "OK" if ok and not blockers else ("PDF-with-blockers" if ok else "FAILED")
    print(f"[note-latex-build] {status}: blockers={len(blockers)} warnings={len(warnings)}")
    print(f"[note-latex-build] report -> {report_path}")
    if pdf.exists():
        print(f"[note-latex-build] pdf -> {pdf}")
    for f in blockers[:12]:
        print(f"  ! {f['kind']}: {f['match']}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
