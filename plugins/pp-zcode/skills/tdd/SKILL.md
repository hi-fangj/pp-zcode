---
name: tdd
description: Test-driven development. Use when the user wants to build features or fix bugs test-first, mentions "red-green-refactor", wants a regression test, or wants integration tests.
---

# Test-Driven Development

TDD is the red → green loop. This skill is the reference that makes that loop produce tests worth keeping: what a good test is, where tests go, the anti-patterns, the bug-fix loop, and the rules of the loop. Every section applies on every cycle: consult them before and during the loop, not after.

When exploring the codebase, read `GLOSSARY.md` (if it exists) so test names and interface vocabulary match the project's domain language, and respect ADRs in the area you're touching.

## What a good test is

Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification: "user can checkout with valid cart" tells you exactly what capability exists, and it survives refactors because it doesn't care about internal structure.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

## Seams: where tests go

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

**Test only at pre-agreed seams.** Before writing any test, write down the seams under test and confirm them with the user. No test is written at an unconfirmed seam. When running unattended, state the seams you will test and proceed; list them in the final report so the user can correct them. You can't test everything, so agreeing the seams up front is how testing effort lands on the critical paths and complex logic instead of every edge case.

Ask: "What's the public interface, and which seams should we test?" Give each proposed seam a one-line note on what it catches and what it misses.

When the shape of that interface is itself in question (how deep the module is, where the seam belongs, what the interface should expose), call the Skill tool with `pp-zcode:codebase-design` for the vocabulary. It is the shared source of the module, interface, depth, seam, adapter, leverage and locality terms, and it is a reference to consult, not a session to run.

## Anti-patterns

- **Implementation-coupled**: mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks when you refactor but behavior hasn't changed.
- **Tautological**: the assertion recomputes the expected value the way the code does (`expect(add(a, b)).toBe(a + b)`, a snapshot derived by hand the same way, a constant asserted equal to itself), so it passes by construction and can never disagree with the code. Expected values must come from an independent source of truth: a known-good literal, a worked example, the spec.
- **Horizontal slicing**: writing all tests first, then all implementation. Bulk tests verify _imagined_ behavior: you test the _shape_ of things rather than user-facing behavior, the tests go insensitive to real changes, and you commit to test structure before understanding the implementation. Work in **vertical slices** instead: one test → one implementation → repeat, each test a **tracer bullet** that responds to what the last cycle taught you.

## Rules of the loop

- **Red before green.** Write the failing test first, then only enough code to pass it. Don't anticipate future tests or add speculative features.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Refactoring is not part of the loop.** It belongs to the review stage, not the red → green implementation cycle. `pp-zcode:poteto-mode` owns that stage: `pp-zcode:code-review` finds the smells, the Refactoring playbook fixes them.

## Fixing a bug

When the task is a bug with a cheap local test path, make the broken behavior executable before changing production code. The goal is a focused regression test that fails before the fix and passes after it.

When the bug is hard — no clean reproduction, intermittent, or a performance regression — load `pp-zcode:diagnosing-bugs` first. It builds and tightens a red-capable feedback loop, minimises the repro, and ranks falsifiable hypotheses before any fix. Its Phase 5 is this loop: turn the minimised repro into the failing test at a correct seam, then fix.

1. **Understand the bug.** State the intended behavior, the current behavior, the affected path, and the smallest observable reproduction.
2. **Choose the narrowest executable check.** Prefer the closest unit, component, integration, or regression test already used for that codepath. Do not build a harness from scratch just to satisfy the loop.
3. **Write the failing test first.** Add the smallest focused test that would have caught the bug. It encodes intended behavior, not the current implementation.
4. **Run it before fixing.** Confirm it fails for the intended reason. If it passes, or fails for an unrelated reason, fix the test or the reproduction before touching production code.
5. **Fix the bug.** Make the smallest production change that satisfies the intended behavior while preserving nearby contracts.
6. **Rerun the regression test.** Confirm it passes, then run the closest nearby validation.

### When a failing test is impractical

Skip the new test and use the closest executable regression check instead: a targeted script, manual reproduction command, browser automation, snapshot comparison, log assertion, or focused integration check. Prefer no new test over a bad test. A bad test mostly exercises mocks, encodes implementation details, depends on timing or unrelated global state, needs expensive infrastructure for a small fix, or would be deleted as soon as it proved the fix.

## Guardrails

- Do not change tests to match a wrong implementation.
- Do not weaken existing assertions unless the expected behavior has genuinely changed, and say why.
- Keep a regression test focused on the bug; no broad fixture churn or unrelated coverage expansion.
- If the bug is flaky, make the test deterministic where possible and document the signal it locks down.
- If the bug exposes a broader class of failures, land the focused regression path first, then consider sibling coverage.

## Report evidence

State the evidence, not just the outcome:

- The failing-before test or executable check, and the failure it produced.
- The passing-after run, and any nearby validation performed.
- If failing-before evidence could not be demonstrated, why, and the closest regression check used instead.
