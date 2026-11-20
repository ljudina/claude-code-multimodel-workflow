#!/bin/sh
# Run one Claude Code session with the main model doing the workflow's search,
# planning and review itself. Only this workflow's subagents (planner, reviewer,
# search) are disabled; built-in subagents such as Explore still work.
# Usage: .claude/solo.sh [model] [claude args...]   (model defaults to opus)
# If an agent in .claude/agents/ is added or renamed, update the list below.

model="${1:-opus}"
[ $# -gt 0 ] && shift

exec claude --model "$model" --disallowedTools "Agent(planner),Agent(reviewer),Agent(search)" \
  --append-system-prompt "Solo mode: the planner, reviewer and search subagents are disabled. Ignore the multi-model workflow rules in CLAUDE.md and do that search, planning and review yourself. Other subagents remain available as usual." \
  "$@"
