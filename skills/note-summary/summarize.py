#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
note-summary — deterministic coverage + status report for a NoteForge run.

Cross-checks _run/outline.json against the written chapters and _run/audit/*.json,
and writes note/coverage_report.md. (The orchestrator additionally writes a narrative
execution_summary.md.)

Coverage is a substring heuristic: an item counts as "present" if its text (or its first
significant token) literally appears in the chapter .tex. It is a signal, not a proof —
the chapter-auditor is the authority on real coverage.

Usage:
  python summarize.py --note-dir note/
"""
import argparse
import json
import pathlib
import re


def load_json(p, default=None):
    try:
        return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    except Exception:
        return default


def present(item, text):
    item = item.strip()
    if not item:
        return True
    if item in text:
        return True
    # fall back to the longest alpha/CJK token in the item
    toks = re.findall(r"[A-Za-z]{4,}|[一-鿿]{2,}", item)
    toks.sort(key=len, reverse=True)
    return bool(toks) and toks[0] in text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--note-dir", required=True)
    args = ap.parse_args()
    note = pathlib.Path(args.note_dir)

    outline = load_json(note / "_run" / "outline.json", {})
    chapters = outline.get("chapters", [])
    build = load_json(note / "_run" / "build_report.json", {})

    lines = ["# Coverage report", ""]
    lines.append(f"- mode: `{outline.get('mode','?')}` · lang: `{outline.get('lang','?')}` · "
                 f"profile: `{outline.get('profile','?')}` · chapters: {len(chapters)}")
    if build:
        lines.append(f"- build: ok=`{build.get('ok')}` blockers={build.get('n_blockers')} "
                     f"warnings={build.get('n_warnings')}")
    lines += ["", "| chapter | items | covered | audit | lines |", "|---|---|---|---|---|"]

    total_items = total_cov = 0
    detail = []
    for ch in chapters:
        cid = ch.get("id", "?")
        cov = ch.get("coverage", []) or []
        ch_file = note / "chapters" / f"{cid}.tex"
        text = ch_file.read_text(encoding="utf-8") if ch_file.exists() else ""
        nlines = text.count("\n") if text else 0
        missing = [it for it in cov if not present(it, text)]
        n_cov = len(cov) - len(missing)
        total_items += len(cov)
        total_cov += n_cov
        audit = load_json(note / "_run" / "audit" / f"{cid}.json", {})
        verdict = audit.get("verdict", "—")
        lines.append(f"| {cid} | {len(cov)} | {n_cov}/{len(cov)} | {verdict} | {nlines} |")
        if missing:
            detail.append((cid, missing, audit.get("missing_coverage", [])))

    pct = (100 * total_cov / total_items) if total_items else 100.0
    lines += ["", f"**Heuristic coverage: {total_cov}/{total_items} = {pct:.0f}%** "
              f"(auditor verdicts are authoritative)."]

    if detail:
        lines += ["", "## Items not literally found (verify against auditor)"]
        for cid, miss, amiss in detail:
            lines.append(f"- **{cid}**: " + "; ".join(miss[:12]) + (" …" if len(miss) > 12 else ""))
            if amiss:
                lines.append(f"  - auditor flagged missing: {'; '.join(amiss[:12])}")

    out = note / "coverage_report.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[note-summary] coverage {total_cov}/{total_items} ({pct:.0f}%) -> {out}")


if __name__ == "__main__":
    main()
