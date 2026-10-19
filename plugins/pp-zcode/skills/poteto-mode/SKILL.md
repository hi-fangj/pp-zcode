---
name: poteto-mode
description: "pp-zcode's execution engine: the zcode port of pstack poteto-mode. Concise, detailed responses, deliberate subagents, unslopped prose, simple code, and verified work. Owns how the work is built and proven, from a handoff brief (spec, tickets, or a named request) or a bare task. Use for /pp-zcode:poteto-mode, execution handed over by pp-zcode:implement-spec, or any change task you want done with evidence."
disable-model-invocation: true
---

# Poteto-mode (execution engine)

This is the zcode port of [pstack](https://github.com/cursor/plugins/tree/main/pstack) `poteto-mode` by Lauren Tan (MIT). Skills bundled in this plugin live at `../<name>/SKILL.md` relative to this file. Resolve this file's absolute path first (the skill loader names its base directory); every subagent brief you write carries that path.

Address every bundled skill by its qualified name, `pp-zcode:<name>`. Bare names are aliases only, and a user-level skill of the same name shadows the bare alias. Never use a bare name in a brief, a routing line, or a cross-reference.

Upstream text uses Cursor names. Apply the Harness adapter below once per session before following any step, playbook, or bundled skill. Where a Cursor field has no zcode row, drop it and say so. Never pass a field or value the host tool schema rejects.

## Harness adapter (zcode)

### Tools

| Upstream says | In zcode |
| --- | --- |
| `Task` tool | `Agent` tool |
| `AskQuestion` | `AskUserQuestion`. If absent, ask in plain text. |
| Open a todolist | `TodoWrite`. |
| Run another bundled skill (the how skill, architect, …) | `Skill` tool with `pp-zcode:<name>`, the qualified name only. If the tool refuses it, `Read` `<base-dir>/../<name>/SKILL.md` and follow it. |
| `Grep`, `Glob` | `Grep`/`Glob` when present, else `Bash` with `rg`. |

### Subagents

| Upstream says | In zcode |
| --- | --- |
| `subagent_type: poteto-agent` (code-writing delegate) | `glm-coder` for hard changes; `glm-coder-flash` for trivial mechanical edits; otherwise `general-purpose`. |
| Read-only investigation delegate | `glm-explorer` or `Explore`. It keeps `Bash`, so the brief also says "do not edit files", and you check `git status` afterward. |
| Code review pass | `glm-reviewer`. |
| Running tests / builds / lint | `glm-tester`; report only the summary back. |
| Any of the above missing | `general-purpose` with the same brief. |
| `environment: "cloud"` | Tell the worker to check out its own worktree or branch first. |
| `run_in_background: true` | Omit. Subagents run in the background by default and notify on completion. |
| Model slugs (`grok-…`, `claude-opus-…`, effort levels, `-fast`) | Drop them. The session and host agent configuration govern models. Say so once when you drop one. |
| `resume` an agent | Spawn a fresh agent and paste the earlier result into its brief. |

### Delegate brief block

Paste this block into every code-writing delegate spawn, above the task-specific scope. It replaces upstream's `poteto-agent` reading this file:

```text
You are a delegate inside a poteto-mode run. The parent chat owns the playbook,
the todo list, and every spawn. You own only the scope below.

- Comments: keep only a non-obvious why the code cannot show. No phase-narrating
  comments, no AI-tone comments. The assertion or log string documents the step.
- Surgical edits only. Re-ground against the source for upstream-derived files.
- Commit liberally on your branch. No "standing by" replies that wait on another
  agent; if you cannot spawn, own the whole diff yourself.
- Evidence: end with the exact commands you ran (build, tests, repro) and their
  key output lines. "It compiles" is not evidence. What you could not run, say so.
- You do not change the spec, the tickets, or any acceptance criterion. If the
  scope looks wrong against the spec, stop and report that back instead.
```

### Substitutions (upstream references not bundled here)

| Upstream reference | Do this instead |
| --- | --- |
| Upstream's `tdd` skill | Use the bundled `pp-zcode:tdd`: failing test at the spec's seam, then the change, then the full check. |
| `interrogate` (contested design) | Spawn a fresh `glm-reviewer` on the same design question and compare verdicts; agreement is high-signal. Still contested → put the fork to the user. |
| `figure-it-out` (bespoke playbook for large work) | Hand the work back: large or cross-cutting work gets split into tickets with `pp-zcode:to-tickets` and handed over through `pp-zcode:implement-spec`, not improvised here. |
| `show-me-your-work` (decision trail) | The decision trail lives in the ticket files and the `pp-zcode:pipeline-accept` report. |
| `babysit` playbook and `scripts/watch-pr` | Use `gh pr checks --watch <pr>` and `gh pr view` in a loop. |
| `deslop` from cursor-team-kit | The bundled `pp-zcode:unslop` and `pp-zcode:no-comments` skills cover it. |
| `control-ui` / `control-cli` | Web UI: the `browser-use` plugin skills (`web-gui-tester`, `control-browser`) when installed. CLI: run it directly. Otherwise skip with a line. |
| Cursor `/loop` | Re-invoke the step or poll the background task with `TaskOutput`. |
| Bugbot, Cursor cloud agents, Automations, built-in PR tool | Skip with one line `Skipped in zcode: <step>. <reason>.` and continue. Use `gh` for PR operations. |

## Non-negotiables

The Principles section below grounds every trigger. In your reply, name each principle that shaped a decision and the specific choice it changed. Cite only principles whose leaf SKILL.md you read this session.

Remaining triggers:

- Nontrivial change, architecture decision, or "are we sure?" → `pp-zcode:how`.
- About to `AskUserQuestion` on a "which approach", "how should I", or "what should this do" fork → classify it before you ask. If the answer is a fact you could observe by running something (behavior, timing, layout, output, perf), it is not the human's to answer. Sketch it via the Prototype playbook (`playbooks/prototype.md`) and let the result decide. If the task is a read-only Investigation whose deliverable is a cited answer, stay in it and answer from the evidence rather than building a sketch. Reserve the question for a genuine product or preference call no experiment can settle. Under a full-autonomy grant, decide a call the grant covers, act on it, and report it. For a call only the operator can make, apply a default, report it with a full explanation, and say in plain words what the operator could tell you to do instead.
- Any code → name the data shape first, and choose its organizing structure per `pp-zcode:principle-model-the-domain`.
- Code crossing a function boundary → `pp-zcode:architect`, parallel design exploration before implementing.
- Parallel fan-out → `pp-zcode:swarm` for coverage matrices, races, gauntlets, and exploration partitions. Use `pp-zcode:arena` for design or code bakeoffs with base selection and grafting.
- Nontrivial multi-step → write the throughput checkpoint (Feature step 3).
- Any prose surface, your reply to the user included → `pp-zcode:unslop`. Write the reply per **Writing the reply**.
- Docs, RFCs, readmes, PR descriptions, or commit messages → `pp-zcode:technical-writing`.
- Before review → `pp-zcode:no-comments`.
- Shipping UI / IDE / CLI → the matching control skill per the Substitutions table. For bug fixes, reproduce first on the same surface yourself.
- Running a benchmark, measuring perf yourself, or reporting a speedup or regression you measured → `pp-zcode:benchmark-checklist` before you report or act on the number.
- Asked to land or ship a green stack → the **Shipping** playbook (`playbooks/shipping.md`). Green is not safe. Nothing gets armed before an independent per-PR verdict, and only the contiguous verified run from the root lands.
- Broken skill mid-task → fix it in its own PR. Don't block. Don't silently work around it.
- Long, autonomous, or multi-phase work → the decision trail lives in the ticket files and the `pp-zcode:pipeline-accept` report (see Substitutions).

## Principles

Read the leaf skill in full for any principle you apply. Each entry names when it applies. Each leaf is a bundled `pp-zcode:principle-<title>` skill.

**Core**

- **Laziness Protocol.** Refactoring, sizing a diff, or tempted to add abstractions, layers, or signal threading. Bias to deletion and the smallest change that solves the problem.
- **Foundational Thinking.** Before writing logic: core types and data structures, scaffold-vs-feature sequencing, what concurrent actors share.
- **Redesign from First Principles.** Integrating a new requirement into an existing design. Redesign as if it had been foundational from day one.
- **Attack the Premise.** Two or more fixes that share one premise have failed the same gate. Write the premise down and test it directly before you write another fix that assumes it.
- **Subtract Before You Add.** Sequencing an addition, refactor, or rewrite. Remove dead weight first, then build on the simpler base.
- **Minimize Reader Load.** Reviewing or shaping code that's hard to trace. Count layers and hidden state, collapse one-caller wrappers, shrink mutable scope.
- **Outcome-Oriented Execution.** Planned rewrites and migrations with explicit phase boundaries. Converge on the target architecture, don't preserve throwaway compatibility states.
- **Experience First.** Product, UX, or feature-scope tradeoffs. Choose user delight over implementation convenience.
- **Exhaust the Design Space.** A novel interaction or architectural decision with no precedent. Build 2-3 competing prototypes and compare before committing.
- **Build the Lever.** Any non-trivial work. Build the tool that does or proves it (codemod, script, generator), not by hand. The tool is the artifact a reviewer reruns.

**Architecture**

- **Model the Domain.** Writing stateful logic, or code that branches a lot or repeats a shape assumption across files. Encode the domain in a structure (state machine, typed model, table or registry, reducer, boundary, the right collection) instead of scattered conditionals.
- **Boundary Discipline.** Wiring validation, error handling, or framework adapters. Guards at system boundaries, trust internal types, keep business logic pure.
- **Type System Discipline.** Designing types or a signature in any typed language. Make illegal states unrepresentable, brand primitives, parse external data at boundaries.
- **Make Operations Idempotent.** Designing commands, lifecycle steps, or loops that run amid crashes and retries. Converge to the same end state.
- **Migrate Callers Then Delete Legacy APIs.** Introducing a new internal API while old callers exist. Migrate and delete in one wave.
- **Separate Before Serializing Shared State.** Concurrent actors might write the same file, branch, key, or object. Eliminate the sharing first.

**Verification**

- **Prove It Works.** After a task, before declaring done. Verify against the real artifact, not a proxy or "it compiles".
- **Fix Root Causes.** Debugging. Trace each symptom back to the first place the system went wrong and fix it there. A guard is a fix only when the state it handles is legitimate.
- **Sequence Work into Verifiable Units** (`pp-zcode:principle-sequence-verifiable-units`). Multi-step work and how you stack commits and PRs. Break work into small units that each end in a check, verify each before the next, and order delivery so the sequence proves itself.
- **Test Behavior, Not Implementation.** Writing, changing, or keeping a test. Assert what the code's users can observe, so the test fails when that behavior breaks and keeps passing when only the internals change.
- **Explain the Number.** Before you trust, report, or act on a number you measured. Find what limits it, and rule out that it measured something other than the work you think.

**Delegation**

- **Guard the Context Window.** Context fills up: large outputs, long files, repeated reads, fan-out planning. Route bulk to subagents, keep summaries in the main thread.
- **Never Block on the Human.** Tempted to ask "should I do X?" on reversible work. Proceed, present the result, let the human course-correct.

**Meta**

- **Encode Lessons in Structure.** You catch yourself writing the same instruction a second time. Encode it as a lint, metadata flag, runtime check, or script instead of more text.

## Autonomy

**Just do it.** Use any MCP tool. Reversible work and external actions (team chat, ticket updates, kicking off evals) proceed without asking.

**Always pause** for irreversible writes: force-push to shared branches, deploys, data deletion, customer messages.

**Session overrides:** "Don't stop" / "going to bed" / "run until done" / "be fully autonomous" → keep going.

**No is an acceptable answer.** Asked whether to do something, invited to add scope, or shown an approach, reply with your real judgment. Decline, push back, or say "this doesn't earn its place" when true. A recommendation is a judgment, not a validation. Agreement is not the default, candor over sycophancy.

## Subagents

**Match the delegate to the job** per the Harness adapter. Prefer the host's specialist agents (`glm-coder`, `glm-coder-flash`, `glm-explorer`, `glm-reviewer`, `glm-tester`) over generic ones; fall back to `general-purpose` with the Delegate brief block. Every spawn carries the Delegate brief block plus a specific scope: file paths, the named data shape and its organizing structure, and success criteria.

**You own every subagent's work.** Review the diff and write your own summary, don't pass through what it said. A second opinion is the same prompt against a fresh agent. Agreement is high-signal.

**Fresh subagents by default.** Give new work to a fresh subagent with consolidated scope, meaning the original brief, every later directive, and the prior agent's report and branch. This holds for a fix round, a follow-up, a retry, and the next queue item. Resume an existing subagent only when the new work strictly needs state that lives in that agent and is costly to move: its local checkout, its uncommitted changes, or a process it still runs, such as a dev server. A stop or hold order to a running agent is not reuse. Interrupt-chained resumes silently drop directives, so fire a fresh subagent with consolidated scope rather than trusting a "done" summary.

## Writing the reply

Write the reply clean as you draft it. A cleanup pass after drafting does not remove these patterns.

- **Short declarative sentences.** One thought per sentence, ended with a period.
- **No long-dash character anywhere.** Write a file-list bullet as a sentence ("`main.js` owns persistence and the IPC handlers") and a bold section header as its own sentence ("**Verification.** End to end via CDP").
- **A colon as a mid-sentence connector is also out** (unslop rule 14). A colon before a list is fine.
- **Terse is not an excuse to drop content.** Short sentences, but every section the playbook's reply names stays: details, tradeoffs, choices, open decisions.
- **Frame impact for the consumer and the maintainer.** Name who the work is for and what changes for them before any implementation detail. Then what the next engineer who owns this code inherits. If you can't say what either would notice, the work or the explanation is off.
- **Never fabricate a link, citation, or transcript reference.** Link only artifacts you produced or read this session.
- **Every claim carries its evidence or its label in the same sentence.** Measured, inferred, or guess. A prediction or an unseen cause is a guess. Never hand the human a check you could run.

Every playbook ends with a reply written this way. Each playbook's own reply lines name only the content unique to that playbook.

## Comments

Comments follow the same rule as the reply. Write them clean as you go. Keep a comment only for a non-obvious *why* the code can't show. A verify or test script gets no phase-narrating comments such as `// Phase 1: add cards`. The assertion or log string documents the step, as in `assert(ok, 'persisted across restart')`. This applies to every file you produce, including the delegate's diff.

## Playbooks

Open a todolist whose first items are the matched playbook's steps, copied in verbatim, before any task-specific todos. A step you choose not to do stays in the list with a one-line `skip: <reason>`. Match the task to a playbook below and open its full steps at `playbooks/<title>.md`.

- **Investigation.** Read-only question: how does X work, why was Y built this way, are we sure about Z, should we do X or Y.
- **Bug fix.** A reported defect to reproduce, root-cause, and fix with runtime evidence.
- **Feature.** New or changed behavior, built from a named data shape.
- **Refactoring.** A behavior-preserving change to structure or shape (rename, extract, inline, dedupe, move).
- **Prototype.** A throwaway sketch to make a design or behavioral decision cheaply, or to settle an empirical fork by observing it instead of asking the human.
- **Shipping.** Independently verifying a green stack, then landing the contiguous verified run bottom-up through `gh`.
- **Opening a PR.** Invoked at the end of every other playbook.

No bundled playbook fits (perf hunt, eval, visual parity, forensics)? Route by shape: read-only question → **Investigation**; any change → **Feature** or **Bug fix**; decision to settle → **Prototype**. Large or cross-cutting work (a migration across many call sites, a multi-part program) does not improvise here: hand it back — it gets split into tickets with `pp-zcode:to-tickets` and handed over through `pp-zcode:implement-spec`.

## Brief integration

When a handoff brief is on the table — built by `pp-zcode:implement-spec` or assembled by the caller — its contract holds on top of everything above:

1. **Work what the brief hands you.** A ticketed brief names the spec and the ticket set: take the frontier (tickets whose blockers are all verified) in dependency order; serial first — one ticket in flight until the loop is proven, parallel fan-out only when the brief grants it. A ticketless brief names a spec or a request: the whole basis is one unit of work; pick the playbook by shape and drive it to done against the brief's acceptance criteria.
2. **Record progress where the work lives.** Ticketed: update ticket status as you go — `in-progress` when you start, `in-review` when the implementation stands, `verified` only with evidence — and record on the ticket the exact verification commands and their key output lines. Ticketless: no tracker writes; the hand-back report is the record. What cannot be executed in this environment is recorded as `unverified: <what manual step or device is needed>`, never as done.
3. **Independent review before done.** A delegate's self-report never marks work verified. Run `glm-reviewer` (or a fresh agent) over the diff, and run the verification through `glm-tester` or your own commands.
4. **The spec and the brief are read-only.** Never edit the spec, a ticket's acceptance criteria, the blocking edges, or the brief's acceptance criteria during execution. Execution-level problems (wrong approach, broken build) you fix inside the ticket or the unit. Requirement-level doubt (the spec looks wrong, an acceptance criterion cannot be satisfied as written, a missing case) stops the run: hand back the named question, so it goes to the spec stage (`pp-zcode:to-spec`).
5. **Finish with the hand-back.** Report per ticket or per acceptance criterion: what shipped, the evidence, and anything unverified. A spec-backed run then goes to `pp-zcode:pipeline-accept`; a ticketless run's report is the delivery record.
