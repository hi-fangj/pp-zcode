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
  a Brief integration section added for spec- and ticket-backed runs.

**Vendored verbatim:**

- `skills/principle-*/SKILL.md` (24 skills)
- `skills/how/`, `skills/why/`, `skills/architect/`, `skills/swarm/`,
  `skills/arena/`, `skills/unslop/`, `skills/technical-writing/`,
  `skills/benchmark-checklist/`
- `skills/no-comments/SKILL.md`; its `references/comment-sicko.md` is upstream
  `agents/comment-sicko.md`, relocated because zcode plugins ship no agents
  directory.
- `skills/poteto-mode/playbooks/{investigation,bug-fix,feature,refactoring,prototype,shipping,opening-a-pr}.md`

Cursor-specific names inside vendored files are resolved by the Harness adapter
in `skills/poteto-mode/SKILL.md`, not by editing the upstream text. The edits
made anyway are mechanical: the vendored `how`, `why`, `arena`, `swarm`, and
`no-comments` skills name the bundled execution skill, and every skill reference
uses the qualified `pp-zcode:<name>` form so a user-level skill of the same name
cannot shadow the bundled copy.

**Original to this plugin:** `skills/implement-spec/`, `skills/pipeline-accept/`,
`skills/pipeline-status/`.

## Matt Pocock's skills

Bundled from https://github.com/mattpocock/skills (MIT), taken from the user-level
install present at the time of porting.

**Vendored verbatim:**

- `skills/grilling/`, `skills/grill-me/`, `skills/grill-with-docs/`
- `skills/domain-modeling/`
- `skills/to-spec/`, `skills/to-tickets/`
- `skills/setup-matt-pocock-skills/`
- `skills/triage/`
- `skills/tdd/`, `skills/codebase-design/`

Each skill keeps its upstream `SKILL.md`, reference files, and `agents/openai.yaml`
metadata.

**Adapted:** only the skill references were qualified. Calls to another bundled
skill now use `pp-zcode:<name>` (for example `pp-zcode:grilling`), so a user-level
skill of the same name cannot shadow the bundled copy. The same qualification was
applied to references in this plugin's own skills and in generated project docs.
Upstream prose and process are otherwise unchanged.
