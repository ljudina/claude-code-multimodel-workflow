#!/usr/bin/env python3
"""Print which models the recent Claude Code sessions in the current folder used,
and how many tokens each agent consumed.

Run from the project root:  python3 .claude/models.py
Shows the three most recent sessions, newest last, with one line per subagent.

Columns: requests made, input tokens (fresh + cache writes + cache reads),
the share of input that was read from cache, and output tokens.

The script reads Claude Code's session transcripts under ~/.claude/projects/.
That format is not a documented interface and may change between versions.
"""
import glob
import json
import os
import re

# Claude Code names each project's transcript folder after its path, with every
# character that is not a letter or digit replaced by "-".
project_dir = os.path.expanduser("~/.claude/projects/" + re.sub(r"[^A-Za-z0-9]", "-", os.getcwd()))


def summarize(path):
    """Return one summary string per model used in a transcript file."""
    # A reply is logged once per content block, so keep one usage record per message id.
    replies = {}
    for line in open(path):
        record = json.loads(line)
        message = record.get("message")
        if isinstance(message, dict) and message.get("model") and message.get("usage"):
            replies[message.get("id") or record.get("uuid")] = message

    per_model = {}
    for message in replies.values():
        usage = message["usage"]
        total = per_model.setdefault(message["model"], {"n": 0, "in": 0, "cached": 0, "out": 0})
        cached = usage.get("cache_read_input_tokens", 0)
        total["n"] += 1
        total["cached"] += cached
        total["in"] += usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0) + cached
        total["out"] += usage.get("output_tokens", 0)

    if not per_model:
        return ["(no replies yet)"]
    return [
        f"{model:20} {t['n']:3} req  {t['in']:>9,} in ({100 * t['cached'] // max(t['in'], 1):2}% cached)  {t['out']:>7,} out"
        for model, t in per_model.items()
    ]


def show(label, path):
    for row in summarize(path):
        print(f"  {label:10} {row}")
        label = ""


sessions = sorted(glob.glob(project_dir + "/*.jsonl"), key=os.path.getmtime)[-3:]
if not sessions:
    print("No sessions found for", os.getcwd())

for session in sessions:
    print("session", os.path.basename(session)[:8])
    show("main", session)
    subagents = glob.glob(session[:-6] + "/subagents/*.jsonl")
    for path in sorted(subagents, key=os.path.getmtime):
        meta = path[:-6] + ".meta.json"
        kind = json.load(open(meta)).get("agentType", "?") if os.path.exists(meta) else "?"
        show(kind, path)
