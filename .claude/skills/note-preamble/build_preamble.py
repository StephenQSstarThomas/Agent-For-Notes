#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
note-preamble — deterministic generator for a NoteForge note.

Reads _run/outline.json and emits, into the run's note dir:
  preamble.tex   = base/preamble_<lang>.tex  +  profiles/<profile>.tex
  master.tex     = base/master.tmpl with title/author/chapters filled in

Every box environment a chapter-writer is allowed to use is defined here, so
the preamble, the style contract, and the writers can never drift apart.

Usage:
  python build_preamble.py --outline note/_run/outline.json --out note/

outline.json (minimal):
{
  "title": "...", "subtitle": "...", "author": "...",
  "lang": "zh"|"en", "profile": "science"|"humanities"|"tech",
  "frontmatter": "optional usage-note paragraph (LaTeX) or ''",
  "chapters": [ {"id": "ch01_intro", "title": "..."}, ... ]
}
"""
import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE / "base"
PROFILES = HERE / "profiles"
KNOWN_PROFILES = {"science", "humanities", "tech"}
KNOWN_LANGS = {"zh", "en"}


def die(msg):
    sys.stderr.write(f"[note-preamble] ERROR: {msg}\n")
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outline", required=True, help="path to _run/outline.json")
    ap.add_argument("--out", required=True, help="note dir to write preamble.tex + master.tex")
    args = ap.parse_args()

    outline_path = pathlib.Path(args.outline)
    if not outline_path.exists():
        die(f"outline not found: {outline_path}")
    spec = json.loads(outline_path.read_text(encoding="utf-8"))

    lang = spec.get("lang", "zh")
    profile = spec.get("profile", "science")
    if lang not in KNOWN_LANGS:
        die(f"lang must be one of {sorted(KNOWN_LANGS)}, got {lang!r}")
    if profile not in KNOWN_PROFILES:
        die(f"profile must be one of {sorted(KNOWN_PROFILES)}, got {profile!r}")

    chapters = spec.get("chapters", [])
    if not chapters:
        die("outline has no chapters")
    for ch in chapters:
        if "id" not in ch:
            die(f"chapter missing 'id': {ch}")

    out_dir = pathlib.Path(args.out)
    (out_dir / "chapters").mkdir(parents=True, exist_ok=True)

    # ---- preamble.tex = base(lang) + profile ----
    base_pre = (BASE / f"preamble_{lang}.tex").read_text(encoding="utf-8")
    prof_pre = (PROFILES / f"{profile}.tex").read_text(encoding="utf-8")
    (out_dir / "preamble.tex").write_text(base_pre + "\n" + prof_pre, encoding="utf-8")

    # ---- master.tex = filled template ----
    tmpl = (BASE / "master.tmpl").read_text(encoding="utf-8")
    subtitle = spec.get("subtitle", "").strip()
    subtitle_tex = f"\\large {subtitle}" if subtitle else ""
    frontmatter = spec.get("frontmatter", "").strip()
    if frontmatter:
        frontmatter_tex = (
            "\\begin{tcolorbox}[colback=gray!5!white,colframe=black!50,"
            "sharp corners,boxrule=0.6pt]\n\\small\n" + frontmatter + "\n\\end{tcolorbox}\n"
        )
    else:
        frontmatter_tex = ""
    chapter_inputs = "\n".join(f"\\input{{chapters/{ch['id']}}}" for ch in chapters)

    master = (
        tmpl.replace("@@TITLE@@", spec.get("title", "Study Notes"))
        .replace("@@SUBTITLE@@", subtitle_tex)
        .replace("@@AUTHOR@@", spec.get("author", ""))
        .replace("@@FRONTMATTER@@", frontmatter_tex)
        .replace("@@CHAPTERS@@", chapter_inputs)
    )
    (out_dir / "master.tex").write_text(master, encoding="utf-8")

    # ---- echo the allowed environments for this profile (for the contract) ----
    env_header = (PROFILES / f"{profile}.tex").read_text(encoding="utf-8").split("\\newtcolorbox")[0]
    print(f"[note-preamble] lang={lang} profile={profile} chapters={len(chapters)}")
    print(f"[note-preamble] wrote {out_dir/'preamble.tex'} and {out_dir/'master.tex'}")
    print("[note-preamble] COMMON envs (all profiles): reviewbox, exambox{label}, keybox, notebox")
    print("[note-preamble] profile content envs documented in:")
    print(env_header.rstrip())


if __name__ == "__main__":
    main()
