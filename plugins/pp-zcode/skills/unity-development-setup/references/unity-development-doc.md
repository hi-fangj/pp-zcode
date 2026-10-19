# Unity Development

Project-specific implementation and verification rules for <project name>. Use these rules with `pp-zcode:unity-development`; they take precedence over generic implementation and TDD workflow assumptions.

## Project shape

- Unity version: <version from ProjectSettings/ProjectVersion.txt>
- Render pipeline and key packages: <pipeline; test framework; asset system>
- Runtime code: <folders and assemblies>
- Editor code: <folders and assemblies>
- Generated code (read-only): <folders and the generator or configuration that owns them>
- Third-party code (read-only): <folders>

## Architecture and ownership

<Layer diagram in dependency order. State which layer owns gameplay rules, presentation, scene-bound components, reusable infrastructure, and editor tooling. Record the runtime/Editor reference direction and any assembly-reference rule that agents must not violate.>

## Compiler checks

| Area or layer | Smallest compiler check | Behavior evidence |
| --- | --- | --- |
| <domain/core> | `<command>` | <test, worked example, or manual scenario> |
| <runtime / MonoBehaviour> | `<command>` | <PlayMode scenario or manual check> |
| <UI / prefab / scene> | `<command>` | <open, interact, close, reopen scenario> |
| <asset loading> | `<command>` | <play mode, package, manifest, and expected result> |
| <Editor tooling> | `<command>` | <menu operation on a representative input> |
| <platform build> | `<command>` | <device or build configuration> |

A successful check has zero errors and no new warnings from modified files. Report existing unrelated warnings rather than cleaning them up.

## Development loop

- Use a red-green loop only when: <deterministic behavior, existing public seam, available runner, and a loop that does not depend on fragile Editor state>.
- Otherwise use a compile-and-exercise slice: <name the expected behavior, make one minimal change, compile the affected assembly, run the nearest Unity-facing behavior>.
- Existing test runner: <EditMode/PlayMode command and the supported filters; write "none" when absent>.
- New test infrastructure is in scope only when: <the repository's policy>.

## Unity-facing validation

- Startup / hot update: <scene, menu, expected result>.
- Gameplay / battle: <scene, replay, or debug entrypoint; expected result>.
- UI / prefab / scene: <scenario and lifecycle checks>.
- Asset loading / manifests: <play mode, package, manifest, and expected result>.
- Editor tooling: <menu and representative input>.
- Networking / protocol: <send, receive, reconnect, and failure scenarios>.
- Platform: <device or build configuration>.

## High-risk paths

- <Path>: <what to trace> -> <evidence required>.
- <Path>: <what to trace> -> <evidence required>.

## Completion report

Report the affected layer, the compiler checks actually run, the focused runtime or Editor scenario, the generated or serialized diff, and every item left for manual validation. A manual result stays `unverified: <what is needed>` until the user reports it; never record it as passed.
