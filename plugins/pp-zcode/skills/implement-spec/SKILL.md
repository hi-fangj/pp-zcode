---
name: implement-spec
description: "Bridge the bundled Pocock chain to pp-zcode's execution engine: load the spec (and its tickets, when pp-zcode:to-tickets split them) from the tracker, build the handoff brief, and run it through pp-zcode:poteto-mode with the evidence discipline intact. The engine-backed stand-in for Matt Pocock's implement-spec skill. Use for /pp-zcode:implement-spec, 'implement the spec', or whenever a spec or ticket set is ready to build."
disable-model-invocation: true
---

# Implement spec: from tracker to engine

The bundled Pocock skills settle **what to build and to what standard**; `pp-zcode:poteto-mode` owns **how it is built and proven**. This skill is the bridge between them: it loads the requirement from the tracker, hands it to the engine in one brief, and brings the hand-back report home. It never writes code and never reviews diffs itself.

```
pp-zcode:to-spec → (pp-zcode:to-tickets) │ pp-zcode:implement-spec │ pp-zcode:poteto-mode → pp-zcode:pipeline-accept
      Pocock             Pocock          │       this bridge       │        engine             验收
```

`pp-zcode:to-tickets` owns task breakdown and dependencies; `pp-zcode:poteto-mode` owns execution order and technical risk inside that breakdown. Never re-derive or re-split the other side's plan.

## Prerequisites (run once per project)

1. **Tracker configured?** Look for `docs/agents/issue-tracker.md` (written by `pp-zcode:setup-matt-pocock-skills`) or an existing `.scratch/<slug>/issues/` layout. Missing → tell the user to run `/pp-zcode:setup-matt-pocock-skills`, and stop.
2. **Project rules present?** The target repo's `AGENTS.md` should name the build, test, and lint commands and the definition of done. Missing → offer the snippet in `references/target-agents-snippet.md`, and let the user confirm it before execution starts.

## Load the work

A user-supplied reference (spec path, issue number, URL) always wins over discovery. With none, find the spec the way the tracker is configured (`docs/agents/issue-tracker.md`): a GitHub issue whose body carries `## Problem Statement`, or a local spec under `.scratch/<feature-slug>/`. Several open → list them one line each and ask which.

- **Spec with tickets** → the brief carries the ticket set and its frontier in dependency order.
- **Spec without tickets** → the brief carries the spec; its acceptance criteria are the unit of done. Do not send the work back for tickets unless the user asks for `pp-zcode:to-tickets` — one coherent feature does not earn that ceremony.
- **No spec, work named in conversation** → no brief beyond what the work earns: hand the request straight to `pp-zcode:poteto-mode`.

## Build the brief

Fill `references/handoff-brief.md` from the tracker and the project's `AGENTS.md`, and save the filled brief to `.scratch/<feature-slug>/brief.md` so a later session can resume it. The spec and tickets stay the source of truth; the brief only points at them.

Then invoke the `pp-zcode:poteto-mode` skill with the brief.

## Bring the hand-back home

`pp-zcode:poteto-mode` finishes with a per-ticket or per-criterion report: what shipped, the evidence, anything unverified.

- A fail, or a requirement-level doubt handed back with a named question → back to the spec stage (`pp-zcode:to-spec`); re-ticket only the delta afterward.
- Spec-backed, all rows pass → hand to `pp-zcode:pipeline-accept` for the final gate.
- Ticketless work → the hand-back report is the delivery record; done.

One ticket in flight at a time until a run has passed end to end. Parallel execution only when the brief grants it, with file ownership and merge order named.
