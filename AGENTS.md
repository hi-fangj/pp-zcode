# AGENTS.md

## Agent skills

### Issue tracker

Issues are tracked as GitHub issues via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage roles, label strings equal to role names. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Pipeline

Work runs through the pipeline: grilling → spec → tickets → execution → acceptance.
Specs and tickets live on the tracker configured in docs/agents/issue-tracker.md.

## Commands

- Build: none — the plugin is pure markdown; structure is validated by the test suite
- Test (single file): python3 -m unittest discover -s tests -p test_plugin_structure.py
- Test (full suite): python3 -m unittest discover -s tests — run once before any ticket is marked verified
- Lint / static analysis: none

## Definition of done

A ticket is verified only against real output from the commands above, run in the
session that claims it. What this environment cannot run is recorded as
`unverified: <manual step or device>`, never as done.

## Hard rules

- Root `marketplace.json` is the only catalog; its version must match `plugins/pp-zcode/.zcode-plugin/plugin.json`.
- A skill directory's name must match its `SKILL.md` frontmatter `name`, and every skill needs a description.
- `pipeline`, `pipeline-accept`, `pipeline-execute` stay user-invoked (`disable-model-invocation: true`).
- Fusion skills ship no unresolved `{{ }}` placeholders.

## Manual acceptance items

- Plugin loading behavior in the ZCode UI (structure tests cover the rest).
