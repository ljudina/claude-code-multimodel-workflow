#!/bin/sh
# Run one Claude Code session on a single model, with subagents disabled.
# Usage: .claude/solo.sh [model] [claude args...]   (model defaults to opus)

model="${1:-opus}"
[ $# -gt 0 ] && shift

exec claude --model "$model" --disallowedTools "Agent" \
  --append-system-prompt "Solo mode: subagents are disabled. Ignore the multi-model workflow rules in CLAUDE.md and do all search, planning and review yourself." \
  "$@"
