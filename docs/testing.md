# Testing the workflow

This walk-through checks that each agent runs when it should and on the model it should. It takes a few minutes and uses a throwaway folder.

## 1. Set up a test folder

Create an empty folder, install the workflow into it as described in the [README](../README.md#install-in-a-project), and make it a git repository:

```sh
mkdir ~/multi-model-test && cd ~/multi-model-test
# copy the files as described in the README, then:
git init
```

Start Claude Code in the folder.

## 2. Check the configuration

| Check | Expected |
|---|---|
| Startup banner | `Using Opus … (from .claude/settings.json)` |
| `/model` | Opus |
| `/agents` | `search` on Sonnet, `planner` and `reviewer` on Fable |

`/agents` shows the configured agents and their models. `/list-agents` is a different command: it shows which agents are running, without their models.

## 3. Test the full workflow

Paste this prompt. The task is small, but it touches three files, so the rules should send it through the planner and the reviewer without you naming them:

```
Run git init if this folder is not a repository yet. Then build a tiny Python tool:
slug.py with a slugify(text) function, cli.py that reads one line from stdin and
prints its slug, and test_slug.py with pytest tests for empty input, punctuation
and repeated spaces. Follow the workflow in CLAUDE.md.
```

When it finishes, run the usage script. Inside Claude Code, the `!` prefix runs a shell command in the session:

```
! python3 .claude/models.py
```

Expected: `main` on Opus, exactly one `planner` line and one `reviewer` line, both on Fable.

```
session e4381898
  main       claude-opus-5-5       12 req    581,253 in (95% cached)    5,183 out
  planner    claude-fable-5-1       2 req     12,867 in (43% cached)    4,055 out
  reviewer   claude-fable-5-1       3 req     23,123 in (72% cached)    1,945 out
```

A second `reviewer` line is correct only if the first review rejected the work. Your token counts will differ from these.

## 4. Test that trivial changes skip the Fable agents

In the same session:

```
Rename the parameter of slugify from text to s
```

Run the script again. No new `planner` or `reviewer` line should appear for this change.

## 5. Test the search agent

```
Find every place slugify is defined, imported or called in this project, including tests.
```

Expected: a `search` line on Sonnet.

In a project this small, the main session may do the lookup itself, which is what the rules tell it to do for small searches. To see the agent run regardless, either name it:

```
Use the search agent to find every place slugify is defined, imported or called.
```

or ask a question with a wide scope, such as where a library is used across a folder containing many projects.

## Reading the script output

The script prints the three most recent sessions for the current folder, newest last. Each line is one agent and one model:

| Column | Meaning |
|---|---|
| `req` | Requests the agent made to the model |
| `in` | Input tokens: fresh input, cache writes and cache reads added together |
| `% cached` | Share of the input that was read from the prompt cache |
| `out` | Output tokens |

Run it from the project root. It finds the transcripts by the current directory.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `/agents` does not list the three agents | The session started before the files were added. Restart Claude Code in the project folder. |
| The main session is not on Opus | `.claude/settings.json` is missing from the project root, or the model was changed with `/model` during the session. |
| No `planner` or `reviewer` line after a multi-file task | Check that the workflow section is in the project's `CLAUDE.md`, then restart. `CLAUDE.md` is read when the session starts. |
| The reviewer does not start, or reports a problem with its effort level | Change `effort: xhigh` to `effort: high` in `.claude/agents/reviewer.md` and restart. |
| The reviewer reviews whole files instead of a diff | The repository has no commits yet, so there is nothing to diff against. Make a first commit. |
| No `search` line | Expected in small projects. See step 5. |
| The script prints `No sessions found` | Run it from the folder where Claude Code was started. |
