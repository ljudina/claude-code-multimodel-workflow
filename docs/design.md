# Design notes

This document explains why the workflow is shaped the way it is, so that you can change it with the trade-offs in view.

## The goal

Spend the most capable model only where it changes the outcome, and keep the main session's context small.

Three facts about Claude Code subagents drive most of the decisions:

- A subagent starts with an empty context. It knows only its own system prompt, the project's `CLAUDE.md`, and the brief it is given.
- Only the subagent's final report returns to the main session. Everything it read along the way stays out of the main context.
- Every spawn has a fixed cost: the system prompt, the tool definitions and `CLAUDE.md` are loaded again each time.

So a subagent pays off in two cases. One is when the work would otherwise fill the main context with material that is needed once, such as the output of a wide search. The other is when an independent read is worth more than a continuation, such as a review by a model that did not write the code.

## Who does what

**Opus writes the code.** The main session makes the most requests and carries the most context, so its model dominates the cost of a task.

**Sonnet searches.** A search is mostly reading. What matters is that the report is short and exact, because every line of it lands in the main context. The agent's prompt is written around that: locations as `path:line`, the patterns that were searched, what was not found, and no pasted files.

**Fable plans and reviews.** These are the two points where a wrong call is expensive and the amount of text produced is small. A flaw in the plan costs the whole implementation; a bug missed in review ships.

## Decisions and their reasons

**One search agent.** Two agents with the same tools and similar descriptions, for example one for "exploring" and one for "finding usages", give the main session no reliable way to choose between them.

**Small lookups are not delegated.** A spawn costs a fresh context. Finding one symbol in a known file is cheaper done directly, so the rule sets a threshold of about three queries or several files.

**One plan check, not two.** The planner reviews the draft once. A second fresh-context pass over the same plan by the same model adds cost and rarely adds findings.

**The reviewer may read beyond the diff.** A diff shows what changed. It does not show a caller that now breaks or a place that should have changed and did not. The reviewer starts from the plan and the diff, then reads whatever surrounding code it needs and runs the tests.

**The reviewer does not get the author's reasoning.** Briefs carry requirements, the plan and paths. A reviewer handed the author's conclusions tends to confirm them.

**No quota of risks.** Asking a reviewer to always list two or three additional risks produces filler, and filler trains the reader to skim. The reviewer reports residual risks only when they are real and says so when there are none.

**A verdict on the first line.** `APPROVE` or `REJECT` first, so the main session can act on it without interpreting a paragraph. Each rejection names a location, the input or state that triggers the problem, and what goes wrong.

**A cap on review rounds.** After two rejected rounds, the main session stops and asks the user. This prevents a loop in which two models disagree at the user's expense.

**A second job for the reviewer.** When the same error occurs twice, the main session stops retrying and asks the reviewer for a diagnosis. A fresh context is useful here for the same reason it is useful in review: it has not absorbed the wrong assumption that caused the first two attempts.

**Trivial changes skip both Fable agents.** Without this rule, a one-line fix would cost two Fable spawns.

**The planner matches its length to the change.** Fable's output is the most expensive text in the workflow. In the test run below, the planner wrote almost as much as the main session for a three-file task, which led to the instruction to keep small plans short.

**The model is set in `settings.json`.** `CLAUDE.md` can describe which model should be used, but it cannot select one. The settings file can.

**`CLAUDE.md` is short.** It is loaded into the main session and into every subagent spawn.

**No "show me a diff first" rule.** A rule that makes the model print each change in chat and wait for approval makes it write every edit twice. Claude Code's permission prompt already shows each edit as a diff before applying it, and plan mode covers larger work.

## Measurements

Token counts from one test session, in which Claude built a three-file Python tool with tests in an otherwise empty project:

| Agent | Model | Requests | Input tokens | Cached | Output tokens |
|---|---|---|---|---|---|
| main | Opus | 12 | 581,253 | 95% | 5,183 |
| planner | Fable | 2 | 12,867 | 43% | 4,055 |
| reviewer | Fable | 3 | 23,123 | 72% | 1,945 |
| search | Sonnet | 2 | 11,843 | 44% | 657 |

Two things follow from these numbers:

- The main session accounts for about 92% of input tokens. Almost all of that is context re-read from the prompt cache on each request, which is billed at a lower rate than fresh input but is still where the volume is. The model the main session runs on, and how much is in its context, matter more than anything done to the subagents.
- The subagents are cheap in absolute terms. Running the reviewer at a higher effort level costs little, which is why it is set to `xhigh`.

This is a single small session, measured before the planner length instruction and the reviewer effort setting were added. Treat it as an illustration of where tokens go and measure your own sessions with `.claude/models.py`.

## Beyond this repository

The measurements point at the main session, so the next savings are there:

- Run `/context` in a fresh session to see what is loaded before you type anything, and disable MCP servers and plugins you do not use.
- Use `/clear` between unrelated tasks. Everything left in context is re-read on every later request.
- Use `/compact` with a focus instruction at natural breakpoints in long tasks.
- Give the model exact file paths and acceptance criteria. Less exploration means less context.
