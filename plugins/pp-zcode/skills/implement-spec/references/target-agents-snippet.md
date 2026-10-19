# Recommended AGENTS.md section for target projects

Long-lived project rules only. The current requirement lives in the spec and tickets on the tracker, never in here. Offer this to the user before execution starts when the target repo has none of it; let them edit before it lands.

```markdown
## Pipeline

Grilling settles requirements; `pp-zcode:to-spec` publishes a spec to the tracker;
large work is split into tickets with `pp-zcode:to-tickets`. Execution is
`pp-zcode:implement-spec` (spec or ticket backed) or `pp-zcode:poteto-mode` (a direct
task). Specs and tickets live on the tracker configured in docs/agents/issue-tracker.md.

## Commands

- Build: <command>
- Test (single file): <command>
- Test (full suite): <command — run once before any ticket is marked verified>
- Lint / static analysis: <command>

## Definition of done

A ticket is verified only against real output from the commands above, run in the
session that claims it. What this environment cannot run is recorded as
`unverified: <manual step or device>`, never as done.

## Hard rules

- <Forbidden areas or operations, release constraints, convention requirements.>

## Manual acceptance items

- <Behavior that only a device, a deploy, or a human can confirm. These are named
  in specs as unverified rows at acceptance, not skipped.>
```
