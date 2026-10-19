---
name: ask
description: "Ask which pp-zcode skill or flow fits your situation. A router over the skills bundled in this plugin: requirements, execution, acceptance, status, and standalone references. Use for /pp-zcode:ask."
disable-model-invocation: true
---

# Ask

You don't have to remember every bundled skill. Describe the situation and this skill names the route.

Before stating what a skill does or recommending that a stage be skipped, read that skill's `SKILL.md`; the map below is for orientation only. Each bundled skill lives at `../<name>/SKILL.md` relative to this file, so resolve this file's directory before reading one.

A **flow** is a path through the skills. Most work runs along the main flow; a few on-ramps merge onto it; the rest are standalone or a vocabulary layer underneath.

Reply in the language of the conversation.

## How to route

1. Read the situation for the **deliverable** (a decision, a spec, a code change, a review, a status answer) and for what **already exists** (a settled idea, a spec, tickets, a failing test).
2. Pick the earliest unresolved stage on the main flow, or the matching standalone skill. State the route in one line, with the reason.
3. If the user asked for the work to be done, invoke the chosen skill by its qualified name and proceed. If the `Skill` tool refuses a user-invoked skill, `Read` its `SKILL.md` and follow it. If they only asked which skill fits, stop after the route. When two routes are genuinely tied, name both and ask one question.

## Main flow: idea → ship

This is the default path, not a gate. Skip any stage the work does not earn; a small task can go straight to execution.

1. **Requirements** — `pp-zcode:grill-with-docs` when working in a repo: it keeps what it learns in `GLOSSARY.md` and ADRs. `pp-zcode:grill-me` when there is no repo or no paper trail is wanted. Both run `pp-zcode:grilling`; reach for the primitive directly only when you want the interview with no wrapper around it.
2. **Spec** — `pp-zcode:to-spec` turns settled decisions into a spec on the tracker, with acceptance criteria and test seams. It synthesizes; it does not reopen the interview.
3. **Tickets, only when earned** — `pp-zcode:to-tickets` splits a multi-part or cross-cutting spec into tracer-bullet tickets with blocking edges. One coherent feature does not need tickets: a spec without them goes straight to execution.
4. **Execution** — `pp-zcode:implement-spec` loads the spec (and tickets, when they exist) from the tracker, builds the handoff brief, and hands it to `pp-zcode:poteto-mode`. A task that never earned a spec skips the bridge and goes straight to `pp-zcode:poteto-mode`. The engine selects a playbook by task shape — investigation, bug-fix, feature, refactoring, prototype, shipping, opening-a-pr — and drives `pp-zcode:tdd` for test-first work. Each unit's diff is independently reviewed through `pp-zcode:code-review` before it counts as done.
5. **Acceptance** — `pp-zcode:pipeline-accept` matches every spec and ticket criterion against real evidence, emits pass / fail / unverified, and borrows the Spec axis of `pp-zcode:code-review` to catch unrequested behaviour before declaring completion. A direct `pp-zcode:poteto-mode` run has no spec to accept against: its hand-back report is the delivery record.

Keep the requirement stages (1–3) in one context window so the interview, spec, and tickets build on the same thinking. Start execution from the written brief.

## On-ramps

- **Bugs and requests arriving from outside** → `pp-zcode:triage`. It moves issues through triage roles and produces agent-ready briefs. Do not triage tickets that `pp-zcode:to-tickets` created; they are already agent-ready.
- **A bug with a cheap local test path** → `pp-zcode:tdd`: write the failing regression test first, confirm it fails for the intended reason, then fix. No practical test path → `pp-zcode:poteto-mode` and its bug-fix playbook: reproduce, root-cause, fix, prove.
- **Small, clear work with no spec** → `pp-zcode:poteto-mode` directly. Do not manufacture a spec to satisfy the flow.

## Status

- **Where does this feature stand?** → `pp-zcode:pipeline-status`. Read-only: phase verdict, ticket table, the first ticket that can move, and the next owner. It never advances work or judges quality.

## Execution-side references

Standalone, reachable at any point:

- `pp-zcode:how` — how a subsystem works, its runtime flow, or where code should live.
- `pp-zcode:why` — why the code took this shape: decisions, tradeoffs, regressions, postmortems.
- `pp-zcode:teach` — one plain explanation built from `how` + `why`, scaled to the listener.
- `pp-zcode:blast-radius` — what a change could break beyond the diff, with the safety fact proven by running code.
- `pp-zcode:architect` — sketch types, signatures, and module boundaries before writing code.
- `pp-zcode:arena` — run several candidates at one non-trivial task, pick a base, graft the strongest parts.
- `pp-zcode:swarm` — fan out parallel workers and return one report.
- `pp-zcode:code-review` — routine two-axis diff review: repo standards plus a Fowler smell baseline, and spec fidelity including scope creep. The default review pass; `pp-zcode:interrogate` is the adversarial escalation when findings are contested.
- `pp-zcode:interrogate` — adversarial review from one reviewer per configured model, synthesized into one verdict.
- `pp-zcode:technical-writing` — docs, RFCs, READMEs, PR descriptions, commit messages.
- `pp-zcode:unslop` — cut AI tells from any prose.
- `pp-zcode:no-comments` — strip comments before review; keep only what the code cannot say.
- `pp-zcode:benchmark-checklist` — vet a performance number before reporting or acting on it.
- `pp-zcode:typescript-best-practices` — TypeScript type disciplines, with patterns for every rule.
- `pp-zcode:correct` — turn a repeated agent mistake into architecture, a type, a lint, or a test that makes it impossible.
- `pp-zcode:show-me-your-work` — a reviewable TSV decision trail for long, autonomous, or multi-phase work.
- `pp-zcode:poteto-mode`'s Pause safely playbook — leave a resume note and a `wip:` commit so a cold-start agent can continue.
- `pp-zcode:recall` — rebuild recent working context across chats before resuming work.
- `pp-zcode:reflect` — mine this session for durable learnings and route them into skill edits.
- `pp-zcode:tdd` — the red → green loop, including the bug-fix regression loop.
- `pp-zcode:unity-development` — implementation, fixes, refactors, and testing in a Unity repository: compile, EditMode/PlayMode, scene/prefab, and manual evidence instead of assuming a conventional test suite. Pair with `pp-zcode:unity-development-setup` once per Unity project.

The 24 `principle-*` micro-skills are not routes: `pp-zcode:poteto-mode` loads them by name while it works.

## Model roles

`pp-zcode:setup-models` writes `~/.zcode/pp-zcode/models.md`, the role → model table every execution-side skill reads at spawn time. With no file, every role runs on the session model. Reach for it when the user wants one role on a stronger or cheaper model, or wants a review panel spanning model families.

## Vocabulary underneath

- `pp-zcode:domain-modeling` — sharpen the project's domain language; record hard-to-reverse decisions as ADRs.
- `pp-zcode:codebase-design` — the deep-module vocabulary (module, interface, depth, seam, adapter, leverage, locality).

These are references, not sessions: reach for them when the words, not the process, are the problem.

## Failure routes

- **Review or verification fails** → reopen the ticket and return to `pp-zcode:poteto-mode` with the failing evidence.
- **The spec itself is wrong** → stop execution, return to `pp-zcode:to-spec` with the named problem, and re-ticket only the delta.
- **A defect reported after delivery** → spec was right: reopen the ticket and return to execution. Requirements were wrong: change the spec and re-ticket the delta.
- **A verification the environment cannot run** → record `unverified: <what is needed>`; never call it done.

## First run

`pp-zcode:setup-matt-pocock-skills` configures the issue tracker, triage labels, and domain docs the flow assumes. Run it once per project before the first flow.

A Unity project also runs `pp-zcode:unity-development-setup` once: it writes the project's verification matrix to `docs/agents/unity-development.md` and declares `pp-zcode:unity-development` in the repository's agent instructions.

A project with no scripted way to drive its real surface can run `pp-zcode:create-verification-skill` once, which writes a project-local `verify-<app>` skill and a feature map; `pp-zcode:maintain-verification-skill` keeps that map honest. For a property tests cannot reach, `pp-zcode:create-formal-verification-skill` builds a project-local formal check, and `pp-zcode:maintain-formal-verification-skill` brings it back in line after code changes.
