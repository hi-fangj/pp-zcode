# Third-party notices

## pstack

This plugin vendors and adapts material from
https://github.com/cursor/plugins/tree/main/pstack ("pstack") by Lauren Tan,
licensed MIT, through the ZCode adaptation at
https://github.com/ChHsiching/pstack-zcode. Upstream version at the time of
porting: 0.15.28 (pstack-zcode HEAD `ab00d07`).

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
- `skills/blast-radius/`, `skills/correct/`, `skills/teach/`,
  `skills/typescript-best-practices/`, `skills/show-me-your-work/`,
  `skills/reflect/`, `skills/recall/`, and the four verification skills
  (`create-verification-skill`, `maintain-verification-skill`,
  `create-formal-verification-skill`, `maintain-formal-verification-skill`)
- `skills/interrogate/references/{reviewer-prompt,rubric,code-quality-review,lead-judgment}.md`
  from [pstack-zcode](https://github.com/ChHsiching/pstack-zcode), which adapts
  upstream pstack's `skills/interrogate/references/`.
- `skills/no-comments/SKILL.md`; its `references/comment-sicko.md` is the
  upstream agent brief copied for the `general-purpose` fallback.
- `agents/comment-sicko.md` is upstream `agents/comment-sicko.md`, registered
  through the plugin manifest's `agents` field.
- `skills/poteto-mode/playbooks/{investigation,bug-fix,feature,refactoring,prototype,session-pickup,pause-safely,shipping,opening-a-pr}.md`
- `skills/poteto-mode/scripts/session-store.py` (read-only local session index
  used by `recall` and the session-pickup playbook)

Cursor-specific names inside vendored files are resolved by the Harness adapter
in `skills/poteto-mode/SKILL.md`. Where a bundled skill still had to be edited,
the edits are mechanical: the vendored `how`, `why`, `arena`, `swarm`,
`no-comments`, and new upstream skills name the bundled execution skill, every
skill reference uses the qualified `pp-zcode:<name>` form so a user-level skill
of the same name cannot shadow the bundled copy, and every model-role lookup
reads `~/.zcode/pp-zcode/models.md` instead of upstream's Cursor rule
`~/.cursor/rules/pstack-models.mdc`. Five files were synced past the earlier
snapshot because their old text invoked Cursor-only mechanics: `why` (MCP
discovery), `bug-fix` (Cursor `/loop`), `shipping` (Cursor cloud agents and
`cursor-team-kit` controls), `opening-a-pr` (`Task` and `/deslop`), and
`no-comments` (`Task` plus an unqualified agent type).

Host-portability edits made beyond renaming: `teach` no longer requires an
image-generation tool (it falls back to mermaid or ASCII), `show-me-your-work`
and `recall` read model roles from
`~/.zcode/pp-zcode/models.md` instead of asking for a "different family" or a
"fast, cheap model" with no configured seat, `reflect` files backlog items to
the project tracker named in `docs/agents/issue-tracker.md`, `pipeline-accept`
records a browser-driven row as `unverified` when the browser-use plugin is
absent, and `typescript-best-practices` drops the unsupported `paths`
frontmatter key.

**Original to this plugin:** `skills/ask/`, `skills/implement-spec/`,
`skills/pipeline-accept/`, `skills/pipeline-status/`, `skills/setup-models/`
(the zcode model-role data file and preset-agent scheme, after
[pstack-zcode](https://github.com/ChHsiching/pstack-zcode)'s `setup-pstack`),
and `skills/unity-development/` + `skills/unity-development-setup/` (adapted from
the per-repository Unity workflow used by this machine's Unity projects; no
upstream text is vendored).

## Matt Pocock's skills

Bundled from https://github.com/mattpocock/skills (MIT), taken from the user-level
install present at the time of porting.

**Vendored verbatim:**

- `skills/grilling/`, `skills/grill-me/`, `skills/grill-with-docs/`
- `skills/domain-modeling/`
- `skills/to-spec/`, `skills/to-tickets/`
- `skills/setup-matt-pocock-skills/`
- `skills/triage/`
- `skills/tdd/`, `skills/codebase-design/`, `skills/code-review/`
- `skills/diagnosing-bugs/` (SKILL.md, `agents/openai.yaml`, and
  `scripts/hitl-loop.template.sh`)

Each skill keeps its upstream `SKILL.md`, reference files, and `agents/openai.yaml`
metadata.

**Adapted:** only the skill references were qualified. Calls to another bundled
skill now use `pp-zcode:<name>` (for example `pp-zcode:grilling`), so a user-level
skill of the same name cannot shadow the bundled copy. The same qualification was
applied to references in this plugin's own skills and in generated project docs.
Upstream prose and process are otherwise unchanged. `skills/code-review/` goes
one step further: its two reviewers spawn through the host's `Agent` tool
(`glm-reviewer` when present), its issue lookup follows the tracker workflow in
`docs/agents/issue-tracker.md`, and it is wired into the pipeline as the
independent review in `poteto-mode` and the code → spec sweep in
`pipeline-accept`. `skills/diagnosing-bugs/` keeps its upstream text and is
wired into the pipeline by reference: the `bug-fix` playbook runs it for hard
bugs, `tdd` defers to its Phase 5 seam rule, and `ask` routes hard bugs to it.
