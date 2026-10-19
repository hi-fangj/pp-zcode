---
name: pipeline-accept
description: "Final acceptance gate: walk every acceptance criterion in the spec and each ticket, match it against real evidence (re-run verification commands, read build and test output, inspect the diff), and emit a per-criterion pass / fail / unverified report with routing. Use after execution finishes, or for 'accept this against the spec' / '验收'."
disable-model-invocation: true
---

# Pipeline Accept: the spec is the only judge

Acceptance compares the delivered work against the spec's acceptance criteria and each ticket's criteria, one by one, with evidence. It does not re-review code style (that was Phase 3's independent review), and it does not discover new requirements.

## Process

### 1. Build the criteria matrix

Load the spec and every ticket from the tracker. Lay out one row per acceptance criterion: its source (spec section or ticket number), the criterion text, and an empty evidence cell. A ticket left `unverified` or `blocked` enters the matrix as a row with its reason, not as a silent omission. A spec without tickets — a spec-only run — fills the matrix from the spec's criteria alone. A bare task with no spec never enters this skill; the execution hand-back report is its record.

### 2. Match every criterion to evidence

For each row, in order of strength:

1. **Re-run it now.** The project's verification commands from `AGENTS.md` (build, tests, lint) against the delivered state. Prefer running them yourself or through the `glm-tester` agent; the summary returns here. This is the only evidence that makes a row `pass` without argument.
2. **Read this session's real output.** A verification run from Phase 3 counts only if its output is present in the session and covers the delivered commit. Cite the command and the key output line.
3. **Inspect the artifact.** For behavior a command cannot reach (visual output, device-only behavior, manual acceptance items the spec named), inspect the actual artifact or screenshots from this session, or drive the surface yourself via the browser-use skills when it is a web UI.

Classify each row:

- **pass** — evidence cited in the row, from one of the three sources above.
- **fail** — evidence contradicts the criterion. Name the exact expectation, the actual result, and the ticket to reopen.
- **unverified** — no executable evidence exists and the surface is out of reach. Name precisely what is needed (a device, a deploy, a human observation). Never let an unverified row read as done.

### 3. Emit the acceptance report

One line per criterion plus a verdict:

```text
Acceptance: <spec title> — <PASS | FAIL | PARTIAL, N unverified>
  [PASS] spec §Solution: <criterion> — <command run> → <key output line>
  [FAIL] ticket 03: <criterion> — expected <X>, got <Y> (evidence: <run>)
  [UNVERIFIED] spec §Stories: <criterion> — needs <manual step / device>
Routing: <one sentence per fail or unverified row>
```

### 4. Route by the failure's home

- A `fail` whose criterion is right → reopen the named ticket: back to `pp-zcode:poteto-mode` with the failing evidence attached. Execution bugs do not touch the spec.
- A `fail` or `unverified` that reveals the criterion itself is wrong, missing, or untestable → back to `pp-zcode:to-spec` with the named question; re-ticket only the delta afterward.
- All rows `pass` → the run is complete. Update ticket states to their final values and say so plainly.

Push back when it is warranted. If the work satisfies the spec but the spec now looks wrong, say it in the report's routing section. Acceptance reports the truth of spec versus evidence; it does not bless effort.
