# Handoff brief: the work → pp-zcode:poteto-mode

Fill this in and hand it to the `pp-zcode:poteto-mode` skill. It is the channel between the requirement and the execution engine. Everything the engine may know about the work must be in here; everything in here must trace to the spec, the tickets, or the project's rules.

```text
## Work

<One sentence: what this delivery is for, in the spec's own words.>

## Basis

<What the run is judged against, one of:
  Spec + tickets: spec at <tracker reference or path>; tickets at <location>.
  Spec only: <reference>. The spec's acceptance criteria are the unit of done.
  Request: no tracker artifact; the acceptance criteria below are the record.>

## Tickets

<Ticketed briefs only — delete for a spec-only or request brief.
Ticket set location, plus the frontier in dependency order:
  1. <ticket ref>: <title> — blocked by <none|refs>
  2. …
Work the frontier top to bottom.>

## Acceptance criteria

<Spec-backed: where the criteria live in the spec. Request-shaped: the testable
statements this run is judged by, distilled from the decisions in hand.>

## Project rules

<AGENTS.md path and the commands that define done: build, test, lint.
Any hard constraints: forbidden areas, conventions, release rules.>

## Seams

<Test seams the spec (or the caller) confirmed. Tests land at these seams.>

## Verification

<The commands whose real output marks the work verified.
Anything only checkable on a device or by a human: name it now,
it will be recorded as unverified, not assumed.>

## Concurrency

<serial (default: one ticket in flight) | parallel: <grant, file ownership, merge order, limit>>

## Out of scope

<Non-goals the spec named. A request to do these during execution
is requirement-level: it goes back to the spec stage, not into the diff.>
```

The spec's acceptance criteria and the tickets' blocking edges are read-only for the receiver. Requirement-level doubt comes back as a named question, never as a quiet spec edit.
