---
name: pipeline
description: "The fused pipeline router: requirements through the Pocock skills (grilling → to-spec → to-tickets), execution through pp-zcode's pipeline-execute, acceptance through pipeline-accept. Detects the current phase from artifacts, hands off to the one owning skill, and gates every transition. Use for /pipeline, 'run the pipeline', or driving any request from idea to verified delivery."
disable-model-invocation: true
---

# Pipeline: one conveyor, two engines, five gates

Pocock decides **what to build and to what standard**. pipeline-execute decides **how to build it and how to prove it**. This skill is the conveyor between them: it routes the work to exactly one owner per phase, checks the gate, and moves on. It never plans tickets, never writes code, and never reviews diffs itself.

```
grilling → spec → tickets │ pipeline-execute │ pipeline-accept
   Matt        Matt  Matt  │  pstack (here)   │  joint handoff
```

## Phase 0: prerequisites (run once per project)

Check, in order, and fix the first failure before anything else:

1. **Pocock skills present?** The session must offer `grilling` (or `grill-with-docs`), `to-spec`, `to-tickets`, and preferably `domain-modeling` and `tdd`. These are user-level skills from [mattpocock/skills](https://github.com/mattpocock/skills), not part of this plugin. Missing → tell the user exactly which skill to install, and stop.
2. **Tracker configured?** Look for `docs/agents/issue-tracker.md` (written by `setup-matt-pocock-skills`) or an existing `.scratch/<slug>/issues/` layout. Missing → tell the user to run `/setup-matt-pocock-skills`, and stop.
3. **Project rules present?** The target repo's `AGENTS.md` should name the build, test, and lint commands and the definition of done. Missing → offer the snippet in `references/target-agents-snippet.md`, and let the user confirm it before execution starts. Specs and tickets stay out of `AGENTS.md`; it holds only long-lived rules.

## Phase table

| # | Phase | Owner | Artifact | Gate to next phase |
| --- | --- | --- | --- | --- |
| 1 | Requirements grilling | `grilling` / `grill-with-docs` (+ `domain-modeling` when the domain is complex) | decisions captured in the conversation | Every blocking ambiguity, boundary condition, and non-goal has a decision. |
| 2a | Spec | `to-spec` | spec on the tracker, labeled `ready-for-agent` | Acceptance criteria are testable; test seams named and confirmed with the user. |
| 2b | Tickets | `to-tickets` | one ticket per file/issue with blocking edges and its own acceptance criteria | The user approved granularity and blocking edges; every ticket is independently verifiable. |
| 3 | Execution | `pipeline-execute` (this plugin) | code changes, ticket statuses, evidence | Plan consistent with the spec; every `verified` ticket carries real command evidence; no spec edits happened during execution. |
| 4 | Acceptance | `pipeline-accept` (this plugin) | acceptance report | Every spec criterion is `pass`, or explicitly routed: a named ticket reopened, or a spec amendment. |

## Routing

Classify the current state, then hand the work to the single owner of the next unfinished phase. Say the classification out loud before invoking.

- **No spec exists for this request** → Phase 1. If the conversation already holds a settled design, skip to `to-spec` (it synthesizes; it does not interview).
- **Spec exists, no tickets** → Phase 2b, `to-tickets` against that spec.
- **Tickets exist** → Phase 3. Build the handoff brief (`references/handoff-brief.md`) and invoke the `pp-zcode:pipeline-execute` skill with it.
- **All tickets `verified` (or explicitly `unverified` with reason)** → Phase 4, `pp-zcode:pipeline-accept`.
- **User reports a defect in delivered work** → reopen the ticket (Phase 3) if the spec was right, amend the spec (Phase 2a) if the requirement was wrong.

Find the spec and tickets the way the tracker is configured (`docs/agents/issue-tracker.md`): GitHub/GitLab issues via `gh`/`glab`, or local files under `.scratch/<feature-slug>/issues/`. A user-supplied reference (spec path, issue number, URL) always wins over discovery.

## Pipeline contract

These hold in every phase. They resolve the two-system conflicts up front:

1. **One planner per kind.** `to-tickets` owns task breakdown and dependencies. pipeline-execute owns only execution order and technical risk inside an approved ticket. Never re-derive the other side's plan, and never let execution re-split tickets.
2. **One review per axis.** The spec's completeness was judged at Phase 2 by the user. Code correctness and regression risk are judged in Phase 3 by pipeline-execute's independent review. No extra full-pipeline review pass.
3. **Skills are not agents.** Pocock's side runs as skills in this conversation. pipeline-execute spawns the host's specialist agents (`glm-coder`, `glm-reviewer`, `glm-tester`, …) as delegates. The pipeline itself creates no new agents.
4. **Specs and rules live apart.** `AGENTS.md` holds long-lived project rules, commands, and the definition of done. The spec and tickets hold this requirement only. Never copy a requirement's details into `AGENTS.md`.
5. **Done is evidenced.** A ticket is `verified` only against real command output or a real artifact inspection, produced or re-run in this session. Environment cannot run it → `unverified: <the manual step or device needed>`. Self-report is never evidence.
6. **Failures route backward, work flows forward.** A review or verification failure reopens its ticket. A requirement-level discovery (spec wrong, criterion unsatisfiable, case missing) pauses execution and returns to Phase 2a with the named question; only the delta is re-specced and re-ticketed.

## Ticket states

`ready-for-agent` (pending) → `in-progress` → `in-review` → `verified`, plus `blocked` and `unverified: <reason>`. Write the state in the ticket's `Status:` field where the tracker is local files, or as the issue's state/label where the tracker is real. `pipeline` reads the same field to route.

## Serial first

One ticket in flight at a time until a full pipeline run has passed end to end. Parallel execution is an explicit later grant recorded in the handoff brief, with file ownership and merge order named, and within the host's concurrency limits.
