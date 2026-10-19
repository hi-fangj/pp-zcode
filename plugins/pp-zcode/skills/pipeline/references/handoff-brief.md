# Handoff brief: tickets → pipeline-execute

Fill this in and hand it to the `pp-zcode:pipeline-execute` skill. It is the only channel between the requirements half and the execution half. Everything pipeline-execute may know about the work must be in here; everything in here must trace to the spec or the project's rules.

```text
## Work

<One sentence: what this delivery is for, in the spec's own words.>

## Spec

<Where the spec lives: tracker reference or file path.>

## Tickets

<Ticket set location, plus the frontier in dependency order:
  1. <ticket ref>: <title> — blocked by <none|refs>
  2. …
Work the frontier top to bottom.>

## Project rules

<AGENTS.md path and the commands that define done: build, test, lint.
Any hard constraints: forbidden areas, conventions, release rules.>

## Seams

<Test seams the spec confirmed. Tests land at these seams.>

## Verification

<The commands whose real output marks a ticket verified.
Anything only checkable on a device or by a human: name it now,
it will be recorded as unverified, not assumed.>

## Concurrency

<serial (default: one ticket in flight) | parallel: <grant, file ownership, merge order, limit>>

## Out of scope

<Non-goals the spec named. A request to do these during execution
is requirement-level: it goes back to the spec stage, not into the diff.>
```

The spec's acceptance criteria and the tickets' blocking edges are read-only for the receiver. Requirement-level doubt comes back as a named question, never as a quiet spec edit.
