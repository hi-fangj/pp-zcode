---
name: unity-development-setup
description: "Configure a Unity repository for pp-zcode's Unity workflow. Detects the project's Unity version, assemblies, generated-code boundaries, compiler checks, test runner, and Unity-facing validation paths; writes docs/agents/unity-development.md and wires the Unity development block into AGENTS.md or CLAUDE.md. Run once per Unity project before implementation, bug fixes, refactors, or test-first work."
disable-model-invocation: true
---

# Unity Development Setup

Scaffold the per-repository configuration that `pp-zcode:unity-development` assumes:

- **Project map**: the affected layers and their assemblies, generated-code ownership, and the runtime/Editor boundary.
- **Verification matrix**: for each layer, the smallest compiler check and the behavior evidence that proves a change.
- **Agent declaration**: the `### Unity development` block that tells every agent to use `pp-zcode:unity-development` and this project's validation matrix.

This is a prompt-driven skill, not a deterministic script. Explore, present what you found, confirm with the user, then write. When the repository already has precise Unity documentation, update it in place instead of replacing it.

## Process

### 1. Explore

Look at the current repository and record what exists; don't assume:

- `ProjectSettings/ProjectVersion.txt`: the Unity version.
- `Packages/manifest.json` and `Packages/packages-lock.json`: render pipeline, test framework, asset system, and code-generation packages.
- `AGENTS.md` and `CLAUDE.md` at the root. Does either exist? Is there already an `## Agent skills` section, and a `### Unity development` block?
- `docs/agents/unity-development.md`: this skill's prior output. Is it current?
- `*.csproj` and `*.sln` at the root: Unity-generated compiler entrypoints. Note which assemblies they represent and whether git ignores them.
- Every `.asmdef`: map folder to assembly, list references, and mark Editor-only and test-only assemblies.
- Test assemblies: asmdefs referencing `UnityEngine.TestRunner` or `UnityEditor.TestRunner`, plus `Tests`/`Editor` folders and any batch-mode command in the repository docs.
- `Assets/Editor`, `#if UNITY_EDITOR` code, and editor menu classes: the Editor-tooling boundary.
- Generated-code directories and their generators (`Assets/Gen`, `*Generated*`, `*.g.cs`, codegen config). Generated output is read-only.
- Asset loading: Addressables, YooAsset, Resources, or a custom bundle system; note manifests, play modes, and build entrypoints.
- Networking, save data, deterministic simulation, and other high-risk paths named in the repository docs.
- `.gitignore`: `Library/`, `Temp/`, `Logs/`, `obj/`, generated `.csproj`, build output, and bundle output.
- Unity Editor automation: check `.zcode/mcp.json`, `.dsh/mcp.json`, `.mcp.json`, and the available tools. Note whether Editor state, scene/prefab operations, Console logs, screenshots, and test runs are reachable.
- Node.js sidecars (`package.json`, npm scripts) when the Unity project uses TypeScript, config pipelines, or asset tooling.

If `ProjectSettings/ProjectVersion.txt` and `Assets/` are both missing, stop: this is not a Unity project root. Ask for the project root instead of inventing a matrix.

### 2. Build the project map and verification matrix

For each affected layer, find the smallest check that proves a change compiled and the cheapest evidence that proves it behaves. Use [unity-development-doc.md](references/unity-development-doc.md) as the shape, but replace every placeholder with the repository's real paths and commands.

- Prefer a Unity-generated `.csproj` build for the fast compiler check. Never edit a generated `.csproj`; regenerate it through Unity when it is missing or stale.
- Prefer the repository's existing EditMode/PlayMode runner for behavior evidence. A matrix that names a runner the repository does not have is a guess, not a setup.
- When no automated check can observe the behavior, name the exact manual scenario, the scene or prefab, and the expected result; it stays `unverified` until someone runs it.
- Record high-risk paths separately: startup and hot update, asset manifests and bundles, networking and reconnects, generated code, deterministic battle or simulation, and platform builds.
- If the repository uses a second language or runtime (TypeScript, Lua, a config pipeline), give that side its own compiler check and behavior evidence instead of treating it as C#.

### 3. Present findings and confirm

Summarize what you found and what is missing. Show the draft `docs/agents/unity-development.md` and the `### Unity development` block. Let the user correct layer names, commands, and manual scenarios before writing.

Ask only about what detection cannot settle:

- Which layer owns a behavior when two layers could host it.
- Which command is authoritative when several exist (Unity menu, batch mode, generated `.csproj`, CI).
- Which high-risk paths require extra evidence for this project.
- Which manual scenarios the user will run, and on which scene, device, or platform.

### 4. Write

**Project doc.** Write `docs/agents/unity-development.md` from the template. If the file exists, update it in place and preserve project-specific rules that are still true. Keep it short enough to read before a change: layers, commands, evidence, high-risk paths, and the completion report.

**Agent declaration.** Pick the file to edit:

- If `CLAUDE.md` exists, edit it.
- Else if `AGENTS.md` exists, edit it.
- If neither exists, ask the user which one to create; don't pick for them.

Never create `AGENTS.md` when `CLAUDE.md` already exists, or the reverse. If an `## Agent skills` block already exists, add or update the `### Unity development` subsection in place rather than appending a duplicate. Don't overwrite unrelated sections.

The block:

```markdown
### Unity development

Use `pp-zcode:unity-development` for implementation, fixes, refactors, and testing decisions in this Unity repository. It replaces generic implementation and TDD assumptions with the project validation matrix in `docs/agents/unity-development.md`.
```

### 5. Prove the setup

Run the cheapest compiler check from the matrix. It must complete with zero errors; if it cannot run, report the exact missing prerequisite (Unity Editor not installed, generated `.csproj` missing, package restore needed, platform module missing).

If the repository has a cheap focused test target, run one and record the pass/fail/skip counts. Do not run full suites, player builds, or broad PlayMode passes just to prove the setup.

### 6. Report

Tell the user:

- what was detected (Unity version, assemblies, generated-code boundaries, test runner, Editor automation);
- what was written (project doc and `AGENTS.md`/`CLAUDE.md` block);
- which command proved the setup and its result;
- what remains manual or unverified.

Re-running this skill updates the doc and the declaration; it is idempotent.
