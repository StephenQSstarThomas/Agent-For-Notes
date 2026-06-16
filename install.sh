#!/usr/bin/env bash
# Install the NoteForge bundle into a note project's agent folder.
#
#   ./install.sh <project-dir> [harness-dir]
#
# harness-dir defaults to .claude (Claude Code). Use .codex, .cursor, or any
# folder your agent harness reads from. The four bundle dirs (skills, agents,
# prompts, memory) are copied verbatim; the helper scripts self-locate via
# __file__, so they work regardless of which folder you install into.
#
# Examples:
#   ./install.sh ~/my-notes            # -> ~/my-notes/.claude/{skills,agents,prompts,memory}
#   ./install.sh ~/my-notes .codex     # -> ~/my-notes/.codex/...
#   ./install.sh ~/my-notes .cursor    # -> ~/my-notes/.cursor/...
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
PROJECT="${1:?usage: ./install.sh <project-dir> [harness-dir=.claude]}"
HARNESS="${2:-.claude}"
DEST="$PROJECT/$HARNESS"

mkdir -p "$DEST"
for d in skills agents prompts memory; do
  cp -R "$SRC/$d" "$DEST/"
done
mkdir -p "$PROJECT/sources"

echo "NoteForge installed -> $DEST/{skills,agents,prompts,memory}"
echo "Drop source PDFs/slides/exams into $PROJECT/sources/ (source mode),"
echo "then ask your agent: \"把 sources/ 整理成一份复习讲义\" / \"make LaTeX notes\"."
echo "Note: in this bundle, \$BUNDLE = $HARNESS"
