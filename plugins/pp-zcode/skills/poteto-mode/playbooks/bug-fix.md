### Bug fix

**You own this task. Plan, review, verify.** Delegate investigation and the fix to subagents, stay in the lead. Code delegates run on the `bug-fix` role: the preset `pp-zcode-bug-fix` when `~/.zcode/pp-zcode/models.md` pins it, the session model otherwise.

Be scientific. Every shipped line traces to runtime evidence. Belt-and-suspenders that "might help" is a hypothesis, not a fix. It does not ship. When evidence refutes a hypothesis, revert what it motivated. The smallest change the evidence justifies ships, nothing more.

**Hard bugs.** No clean reproduction after the first attempt, intermittent, a performance regression, or two fixes that failed against the same symptom means load `pp-zcode:diagnosing-bugs` and run its phases inside this playbook. It owns the red-capable feedback loop, minimisation, ranked falsifiable hypotheses, and one-variable probes. This playbook owns delegation, commit order, review, and the PR. Do not form a fix theory before the loop exists.

1. Reproduce it yourself on the matching surface via the control skill (Non-negotiables), even when a debug or instrumentation protocol says to ask the user to reproduce. Ask the user only with a stated, specific reason the control surface cannot reach the target, and only after driving it as far as it goes. If it won't reproduce directly, synthesize the trigger, tighten conditions, or instrument until it fires. For a hard bug, that loop is `pp-zcode:diagnosing-bugs` Phase 1, and it must be red-capable before step 2 starts.
2. Binary-search the cause. Form the candidate hypotheses, then rule them out until one survives. Seed them with `pp-zcode:how` over the affected subsystem and `pp-zcode:why` for regression history. Each pass, take the split that cuts the most remaining problem space, get runtime evidence, eliminate. When program state is unclear, add instrumentation or logging and read it as the code runs. Don't guess. For a long or stubborn hunt, re-invoke this step each round and read the background task's output; a background agent notifies on completion. For a hard bug, taking the hypotheses and probes from `pp-zcode:diagnosing-bugs` Phases 3–4 (ranked, falsifiable, one variable at a time) is mandatory. Confirm the surviving *mechanism* with runtime evidence before the step-3 architect/interrogate fan-out.
3. Plan the fix. If it crosses a function boundary, `pp-zcode:architect` first. Delegate implementation to a subagent on the `bug-fix` role with a specific scope.
4. Verify on the same surface. The original repro now passes. "Inconclusive" or wrong-surface is not a pass. Flag it. Unit tests show branch behavior, not bug absence.
5. Stage the commits so the failing repro lands before the fix in git history. See `pp-zcode:tdd` for the failing-test-first cadence when the bug has a cheap local test path. Skip it when the test would be expensive, integration-heavy, or unclear. A hard bug's regression test follows the correct-seam rule in `pp-zcode:diagnosing-bugs` Phase 5, and a missing seam is itself a finding to report.
   This is `pp-zcode:principle-sequence-verifiable-units`, the failing test first and the fix on top.
6. Run **Opening a PR**.

**Reply:** what was broken, root cause, fix, how you verified. Paste failing-then-passing repro output verbatim.
