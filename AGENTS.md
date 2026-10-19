# AGENTS.md

## Agent skills

### Issue tracker

Issues are tracked as GitHub issues via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage roles, label strings equal to role names. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Pipeline

Requirements skills ship bundled (`pp-zcode:grilling`, `pp-zcode:to-spec`, `pp-zcode:to-tickets`, plus `grill-me`, `grill-with-docs`, `domain-modeling`, `setup-matt-pocock-skills`, `triage`, `tdd`, and `codebase-design`). Grilling settles requirements; `pp-zcode:to-spec` publishes a spec to the tracker; large work is split into tickets with `pp-zcode:to-tickets`. Execution is `pp-zcode:implement-spec` (spec or ticket backed) or `pp-zcode:poteto-mode` (a direct task); `pp-zcode:pipeline-accept` gates delivery on evidence.
Specs and tickets live on the tracker configured in docs/agents/issue-tracker.md.

Every skill is invoked and cross-referenced by its qualified name `pp-zcode:<name>`. The bare alias can be shadowed by a user-level skill of the same name; never rely on it.

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
- `implement-spec`, `poteto-mode`, `pipeline-accept` stay user-invoked (`disable-model-invocation: true`).
- Bundled Pocock skills keep their upstream invocation policy: `grilling`, `domain-modeling`, `tdd`, and `codebase-design` stay model-invocable; the entry skills stay user-invoked.
- Every bundled skill is called and cross-referenced as `pp-zcode:<name>`; bare names may appear only as descriptive prose, never as an invocation or routing target.
- Fusion skills ship no unresolved `{{ }}` placeholders.

## Manual acceptance items

- Plugin loading behavior in the ZCode UI (structure tests cover the rest).
