---
name: unity-development
description: "Adapt implementation, bug-fix, refactoring, and test-first work to a Unity project. Use when changing Unity C#, assembly definitions, MonoBehaviours, scenes, prefabs, editor tools, UI, asset loading, or deterministic gameplay, or when a generic implementation/TDD workflow assumes a conventional command-line test suite. Reads docs/agents/unity-development.md when the repository has one."
---

# Unity Development

Use the project's real Unity verification surface. Treat test-first development as an optional feedback loop, not a universal precondition.

## Ground the task

1. Read the repository's `AGENTS.md` or `CLAUDE.md`, the relevant domain documentation, and `docs/agents/unity-development.md` when it exists. Project rules win over this skill's generic matrix.
2. Locate the affected assembly, the Unity boundary it crosses, generated-code ownership, and the existing validation entrypoints.
3. State important assumptions before editing, and turn the request into observable success criteria.

When choosing between pure C# tests, EditMode tests, PlayMode tests, compilation, scene/prefab checks, and manual validation, read [references/verification.md](references/verification.md). If the repository's own Unity development document gives a more precise command or constraint, use it.

A Unity repository with no `docs/agents/unity-development.md` has no agreed verification surface yet: say so and offer `pp-zcode:unity-development-setup` instead of inventing commands.

## Choose the feedback loop

Classify each changed behavior before choosing tests:

- Use a red-green loop when the behavior is deterministic, an observable seam already exists, a test runner is available, and the loop does not depend on fragile Editor state.
- Otherwise use the smallest checkable vertical slice: name the expected behavior, make the minimal change, compile the affected assembly, then run the nearest Unity-facing behavior.
- If the user explicitly asks for TDD but the repository has no suitable harness, explain the constraint and use the closest repeatable loop. A TDD request does not authorize new test infrastructure; add it only when the user explicitly includes that work in scope.

Keep gameplay rules and state transitions in domain code so they can earn fast tests later. Verify Unity lifecycle, rendering, animation, prefab wiring, and UI interaction at the real boundary; a mock-heavy test is not a substitute for the owning PlayMode scenario.

## Implement in slices

1. Close one behavior at a time, respecting the repository's architecture and code-generation boundaries.
2. Run the cheapest relevant compile or test after each meaningful slice.
3. Add a Unity-facing check only when the changed behavior depends on the Editor, PlayMode, assets, scenes, or the target platform.
4. For high-risk systems such as startup, asset manifests, networking, code generation, or deterministic simulation, trace the impact path and verify every affected side.

## Verify completion

- Prefer the commands the repository records. Otherwise, when Unity-generated `.csproj` files support it, compile the smallest affected project: `dotnet build <project>.csproj --no-restore --nologo --verbosity:minimal`.
- Require zero compilation errors and no new warnings from the files you changed. Report existing unrelated warnings; do not clean them up as part of this change.
- Run full suites, player builds, resource builds, or broad PlayMode passes only when the change's risk or the acceptance criteria require it.
- Report every check you ran, its result, and every behavior that still needs a human or an open Unity Editor to verify. An unrun check is `unverified: <what is needed>`, never a pass.
- Review the final diff for architecture boundaries, generated files, serialized assets, event cleanup, and API comments. Commit or invoke a separate review workflow only when the user asks.

## Unity Editor automation

When a Unity MCP server or equivalent Editor automation is available, use it for what it can observe faithfully: Editor state, scene and prefab inspection, Console logs, screenshots, and EditMode/PlayMode test runs. Clear the Console before a compile when the toolchain supports it, so the remaining errors belong to the current run. When no such tool is available, name the exact manual scenario instead of guessing.
