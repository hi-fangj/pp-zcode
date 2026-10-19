---
name: setup-models
description: "Configure which model pp-zcode uses for each role and at what reasoning level. Detects the models this machine can run, then writes ~/.zcode/pp-zcode/models.md and any preset agents the pinned roles need. Use for /pp-zcode:setup-models, \"configure pp-zcode models\", or changing a role's model."
disable-model-invocation: true
---

# Setup models

Write `~/.zcode/pp-zcode/models.md`, a data file that sets pp-zcode's model per role. Skills read it at spawn time. With no file, every role runs on the session model.

The file is scoped to this plugin, not shared with any other pstack install. Preset agents go to `~/.zcode/agents/pp-zcode-<role>.md`, so they cannot collide with another plugin's presets.

## Steps

### 1. Detect available models

Enumerate the model ids you can pin, as `providerId/modelId`. Query the model catalog first (`ListModels` when present) and record each model's reasoning levels. When no catalog is available, read the configured providers instead: the union of `~/.zcode/v2/provider_config.json` (providers with access credentials contribute their `modelOrder` and `personalModelIds`) and `~/.zcode/v2/config.json` (providers not `enabled: false` and without `systemDisabledReason` contribute their `models` keys, whose `reasoning.variants` are the levels). Deduplicate by `providerId/modelId`. Never read `~/.zcode/v2/model-providers.json`: it is a template catalog listing models you may not be able to run. Never quote an API key. When neither source yields models, ask the user to paste the ids they have access to. Never write a model id you have not confirmed is available. `inherit-parent` is always valid even though it is not a detected model.

Tag every detected model with a family, judged from the model id first and from the provider id only when the model id yields none. Then drop blocked models: any model id matching `deepseek[-_]?v?\d*[-_]?flash` case-insensitively is never proposed.

### 2. Load current state

The default table is every role `inherit-parent`, as shown in step 5. If `~/.zcode/pp-zcode/models.md` already exists, read it and treat its `# budget` line and role values as the current choices. Drop any line whose role is not in step 5; it is from a retired role.

### 3. Budget, map, and confirm

**(a) Ask for a budget.** Prefer `AskUserQuestion`, and name the current budget when the file records one. With no file, say that `large` is the default.

- `unlimited — max reasoning`
- `large — xhigh reasoning`
- `medium — high reasoning`
- `small — medium reasoning`

**(b) Offer a diversity panel once.** When the detected set holds at least two distinct families and the panel roles still sit at their default, ask one `AskUserQuestion` right after the budget answer:

- `two-family panel — inherit-parent, <other-family model> (Recommended)` — name a concrete detected model from a family other than the session model's, preferring a provider that is not a localhost endpoint. Adopting sets `arena runners`, `arena cross-judge pool`, `architect runners`, and `interrogate reviewers` to `inherit-parent, <other-family model>`. All other roles stay `inherit-parent`.
- `keep all-inherit` — the default. Re-run this skill anytime.
- `customize per role` — skip the presets and go to the per-role confirm.

A decline leaves no trace, so a later run offers again. Never record a decline as a per-role choice.

**(c) Apply it.** `unlimited`, `large`, `medium`, and `small` set the reasoning level of every pinned model, panel entries included, to `max`, `xhigh`, `high`, or `medium`. For each model, use the highest level it supports at or below that target; a model with no levels keeps its own default. `inherit-parent` does not change.

**(d) Show the roles and confirm.** Show every role with its model, marking any real model id not in the detected set. List every line step 2 dropped. Ask whether to accept as-is or change specific roles, offering the detected models plus `inherit-parent`. Prefer `AskUserQuestion`.

For panel roles (`arena runners`, `architect runners`, `interrogate reviewers`) the value is a list, and one subagent runs per entry, so the list length sets the fan-out. `arena cross-judge pool` is also a list, but Arena selects one value whose model's provider differs from the parent's when possible. `swarm workers` is the default model for every worker unless a race assigns another model per arm.

### 4. Validate

Every real model id written must be in the detected set. `inherit-parent` always passes. If a chosen id is not available, stop and ask again.

### 5. Write the file and the presets

Overwrite `~/.zcode/pp-zcode/models.md` so re-runs stay idempotent. Shape:

```
# pp-zcode model configuration. One line per role. Delete a line to fall back to
# the default (`inherit-parent`).
# `inherit-parent`: the role runs on the session model (omit the model).
# `providerId/modelId[@<level>]`: the role runs on its preset agent, or on the
# workflow agent, with that model and reasoning level. Alias entries in a panel
# list still count toward its fan-out.
# budget: large (thoughtLevel: xhigh)
feature, refactoring: inherit-parent
bug-fix: inherit-parent
hardest tasks: inherit-parent
judgment and prose: inherit-parent
how explorer: inherit-parent
how explainer: inherit-parent
why investigators: inherit-parent
why synthesizer: inherit-parent
arena runners: inherit-parent
arena cross-judge pool: inherit-parent
swarm workers: inherit-parent
architect runners: inherit-parent
interrogate reviewers: inherit-parent
reflect judgment, divergent, synthesizer: inherit-parent
reflect tooling: inherit-parent
```

Then generate `~/.zcode/agents/pp-zcode-<role>.md` for every scalar role pinned to a real model. Panel roles name their models in the list and get no preset. The preset name is `pp-zcode-` plus the role line lowercased, with each `", "` sequence and each remaining space replaced by one hyphen (`feature, refactoring` → `pp-zcode-feature-refactoring`). Put the model in `model`, the leveled form `providerId/modelId@<level>` split into `model` plus `thoughtLevel`, and this body with the role and its owning skill filled in:

```markdown
---
name: pp-zcode-<role>
description: "Pinned-model preset for the pp-zcode <role> role."
model: <providerId/modelId>
thoughtLevel: <level>
---

You are the pp-zcode <role> role. Read `<owning skill path>` in full before any
work, then the brief your parent hands you. The parent owns the plan, the todo
list, and every decision. You own only your scope. Report the exact commands you
ran and their key output lines; say what you could not run.
```

Owning skill per role:

| Role | Owning skill |
| --- | --- |
| `feature, refactoring` | `../poteto-mode/playbooks/feature.md` and `refactoring.md` |
| `bug-fix` | `../poteto-mode/playbooks/bug-fix.md` |
| `hardest tasks` | `../poteto-mode/SKILL.md` |
| `judgment and prose` | `../unslop/SKILL.md` and `../technical-writing/SKILL.md` |
| `how explorer` | `../how/references/explorer-prompt.md` |
| `how explainer` | `../how/references/explainer-prompt.md` |
| `why investigators` | `../why/references/investigator-prompt.md` |
| `why synthesizer` | `../why/references/synthesizer-prompt.md` |
| `swarm workers` | `../swarm/SKILL.md` |
| `reflect judgment, divergent, synthesizer` | `../reflect/SKILL.md` |
| `reflect tooling` | `../reflect/SKILL.md` |

Resolve every path against the installed pp-zcode skills directory before writing, and write the absolute resolved path into the preset. Delete any preset whose role is no longer pinned. Preset files apply to new sessions.

### 6. Refresh saved panel workflows

The panel skills save global workflows at `~/.zcode/workflows/pp-zcode-arena.dwf.ts`, `pp-zcode-swarm.dwf.ts`, and `pp-zcode-interrogate.dwf.ts`. A saved script pins the model table of the run that saved it, because the workflow compiler rejects runtime-string model pins. After writing `models.md`, refresh each saved copy so it does not run the old panel.

Read each of the three files that exists. A missing file was never saved, and saving stays the user's decision. Each workflow serves rows of the file just written: `pp-zcode-arena` serves `arena runners`, `arena cross-judge pool`, and `architect runners`; `pp-zcode-swarm` serves `swarm workers`; `pp-zcode-interrogate` serves `interrogate reviewers`. Normalize each entry to the saved literal's spelling: `providerId/modelId@<level>` becomes `providerId/modelId$<level>`; `inherit-parent` stays an alias. A file is fresh when its embedded evidence matches the rows it serves:

- Every served row `inherit-parent`: fresh iff the file carries the inherit-only guard (a runtime `throw` on any non-`inherit-parent` entry) and no `model("...")` or `model: "..."` literal.
- A served row pins a real model: fresh iff the file's set of `model("...")` and `model: "..."` literals equals the normalized set of real models in the served rows.

Regenerate each stale file: load the `dynamic-workflows` skill, rebuild the script per the owning panel skill, and save under the same name at global scope; a same-name save replaces. Each overwrite asks the user, as any save does. A save refused in a headless run leaves that workflow stale: report it and continue.

### 7. Confirm

Tell the user the file was written, that skills read it at spawn time, and that new preset agent files apply to new sessions. Re-running this skill updates both. Name each saved panel workflow as fresh, regenerated, or left stale.
