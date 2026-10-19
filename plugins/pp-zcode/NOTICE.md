# Third-party notices

## pstack

This plugin vendors and adapts material from
https://github.com/cursor/plugins/tree/main/pstack ("pstack") by Lauren Tan,
licensed MIT. Upstream version at the time of porting: 0.15.28.

**Adapted (rewritten for zcode):**

- `skills/pipeline-execute/SKILL.md` (directory renamed from `poteto-mode` when the
  plugin's own skills took `pipeline-*` names) — upstream `skills/poteto-mode/SKILL.md` with
  the Harness adapter and Substitutions tables added (modeled on upstream's own
  `docs/harness/claude-code.md` porting approach), the playbook index pruned to
  the bundled set, model-selection sections replaced by host agent mapping, and
  a Pipeline integration section added for the pp pipeline.

**Vendored verbatim:**

- `skills/principle-*/SKILL.md` (24 skills)
- `skills/how/`, `skills/why/`, `skills/architect/`, `skills/swarm/`,
  `skills/arena/`, `skills/unslop/`, `skills/technical-writing/`,
  `skills/benchmark-checklist/`
- `skills/no-comments/SKILL.md`; its `references/comment-sicko.md` is upstream
  `agents/comment-sicko.md`, relocated because zcode plugins ship no agents
  directory.
- `skills/pipeline-execute/playbooks/{investigation,bug-fix,feature,refactoring,prototype,shipping,opening-a-pr}.md`

Cursor-specific names inside vendored files are resolved by the Harness adapter
in `skills/pipeline-execute/SKILL.md`, not by editing the upstream text. The one
upstream edit made anyway is mechanical: the vendored `how`, `why`, `arena`,
`swarm`, and `no-comments` skills reference the bundled execution skill by its
new name (`poteto-mode` → `pipeline-execute`).

**Original to this plugin:** `skills/pipeline/`, `skills/pipeline-accept/`,
`skills/pipeline-status/`.

## Matt Pocock's skills

Referenced, not vendored: https://github.com/mattpocock/skills. The requirements
half of the pipeline expects those skills installed at user level.
