# Third-party notices

## pstack

This plugin vendors and adapts material from
https://github.com/cursor/plugins/tree/main/pstack ("pstack") by Lauren Tan,
licensed MIT. Upstream version at the time of porting: 0.15.28.

**Adapted (rewritten for zcode):**

- `skills/poteto-mode/SKILL.md` — upstream `skills/poteto-mode/SKILL.md` with
  the Harness adapter and Substitutions tables added (modeled on upstream's own
  `docs/harness/claude-code.md` porting approach), the playbook index pruned to
  the bundled set, model-selection sections replaced by host agent mapping, and
  a Pipeline integration section added for the pp pipeline.

**Vendored verbatim:**

- `skills/principle-*/SKILL.md` (23 skills)
- `skills/how/`, `skills/why/`, `skills/architect/`, `skills/swarm/`,
  `skills/arena/`, `skills/unslop/`, `skills/technical-writing/`,
  `skills/benchmark-checklist/`
- `skills/no-comments/SKILL.md`; its `references/comment-sicko.md` is upstream
  `agents/comment-sicko.md`, relocated because zcode plugins ship no agents
  directory.
- `skills/poteto-mode/playbooks/{investigation,bug-fix,feature,refactoring,prototype,shipping,opening-a-pr}.md`

Cursor-specific names inside vendored files are resolved by the Harness adapter
in `skills/poteto-mode/SKILL.md`, not by editing the upstream text.

**Original to this plugin:** `skills/pp/`, `skills/pp-accept/`.

## Matt Pocock's skills

Referenced, not vendored: https://github.com/mattpocock/skills. The requirements
half of the pipeline expects those skills installed at user level.
