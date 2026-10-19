---
name: pipeline-status
description: "Read-only pipeline status. Answer 'where does feature X stand' from the tracker: phase verdict with basis, ticket state table, first ticket that can move, and the next skill owner. With no reference, list open features one line each. Never writes to the tracker, never judges quality."
---

# Pipeline Status: where the pipeline stands, never what it is worth

Status answers one question: where does a feature sit in the pipeline, and who owns the next move. It reads the tracker and reports. It never advances the work.

## Contract

- **Zero writes.** Never add or remove labels, never comment on an issue, never close or edit one. Every tracker call in this skill is a read.
- **No quality judgment.** Whether the work is good belongs to `grilling` and `pipeline-accept`. Status reports state and evidence, not opinions.
- Reply in the language of the conversation.

## Prerequisite

Read the target repo's tracker config at `docs/agents/issue-tracker.md`. If the configured tracker is not GitHub, say so in one line and stop; this skill only knows GitHub issues.

## What counts as a feature

- A **spec** is an issue whose body contains the spec template's opening section `## Problem Statement`.
- A feature's **tickets** are that spec issue's native sub-issues.
- Other issues labeled `ready-for-agent` are plain bugs or one-off tasks. They are not features and never appear in list mode.
- Work that has not reached the tracker — the requirements phase, `grilling` — is invisible to this skill by design. Say so rather than inferring it.

## Input

An explicit reference always wins: a feature slug, issue number, or URL. Resolve it, then report.

With no reference, list every open spec issue as one line: feature, phase, next step. Then stop. No deep report uninvited.

## Phase

The mapping is mechanical, derived only from tracker state:

| Tracker state | Phase | Next owner |
| --- | --- | --- |
| No spec matches the reference | no spec found | none — name what was searched; never guess |
| Spec open, no tickets yet | ticketing | `to-tickets` |
| Spec open, one or more open tickets | execution | `pipeline-execute` |
| All tickets closed, or the only open tickets are explicitly `unverified` with a reason, spec still open | acceptance | `pipeline-accept` |
| Spec issue closed | delivered | none |

`grilling`-phase work leaves no tracker footprint, so it cannot appear in the table above; that is expected, not missing data.

This table mirrors the phase table in the `pipeline` skill: `grilling` → `to-spec` → `to-tickets` → `pipeline-execute` → `pipeline-accept`. `pipeline` is the source of truth; if they diverge, `pipeline` wins.

## Reading ticket state

Ticket state comes from the workflow labels exactly as defined in the "Pipeline ticket states" section of `docs/agents/issue-tracker.md`; do not restate that table here.

- The `unverified` reason and the `verified` evidence live in the ticket's comments.
- Blockers come from the tracker's native dependency edges. A ticket can move when every blocker is closed.

## Report

When a reference resolves, emit exactly these four blocks and nothing else:

### 1. Phase verdict

The phase from the table plus the evidence it was judged from: issue states, labels, ticket counts.

### 2. Ticket table

One row per ticket, in tracker order:

| # | Title | State | Blocked by |

### 3. First ticket that can move

The earliest ticket in tracker order whose blockers are all cleared and whose state allows work. If none, write `none can move` and name the blocker or state holding each ticket back.

### 4. Next owner

The next skill from the phase table, plus one line saying why it owns the work.

## Honesty rule

Contradictory or missing tracker data is reported, never smoothed over. If a spec has no readable body, a ticket carries two workflow labels, or a dependency points outside the feature, say `cannot determine` and give the specific reason. A confident wrong answer is worse than a named gap.
