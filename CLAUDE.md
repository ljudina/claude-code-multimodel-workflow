## Multi-model workflow

The main session runs on Opus and writes the code. Three subagents support it: `search` (Sonnet), `planner` (Fable) and `reviewer` (Fable).

- **Search.** Do a single lookup in a known place yourself. Delegate to `search` when it would take more than about three queries or mean reading several files, and run several in parallel for independent questions.
- **Trivial changes** (one file, under about 30 lines, no change to behaviour or interfaces) need no planner and no reviewer.
- **Everything else:**
  1. Draft the plan, then send the requirements and the draft to `planner` once before locking it.
  2. Implement.
  3. Before calling the work done, send the plan to `reviewer` and tell it to read the diff. Fix what it rejects and have it re-check the fixes. After two rejected rounds, stop and ask me.
- **Same error twice.** Stop retrying. Send the error, what you tried, and the relevant paths to `reviewer` for a fresh diagnosis.
- **Briefs** to `planner` and `reviewer` carry requirements, the plan, and paths. Leave out your own reasoning and conclusions, so their read is independent.
