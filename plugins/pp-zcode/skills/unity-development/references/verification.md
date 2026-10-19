# Unity Verification Selection

Use this reference to choose the cheapest evidence that faithfully observes the changed behavior. Repository instructions override this generic matrix.

## Evidence matrix

| Change type | Primary feedback | Completion evidence |
| --- | --- | --- |
| Pure domain rule, calculation, or state transition | Existing unit or EditMode test when a public seam exists; compile the affected assembly | Worked examples pass and the affected assembly compiles |
| Unity API that does not depend on frame or scene lifecycle | EditMode test when stable; compile the affected assembly | Serialized or API behavior observed through the public boundary |
| `MonoBehaviour`, coroutine, physics, animation, rendering | Targeted PlayMode check; compile the affected assembly | The owning lifecycle or frame sequence behaves correctly |
| UI panel or interaction | Presenter/system test for pure decisions; targeted PlayMode or manual UI flow | Open, interact, close, reopen, and cleanup all succeed |
| Prefab, scene, inspector, serialized field | Scene/prefab smoke check plus serialized diff inspection | References survive reload and the target flow runs |
| Editor tooling or importer | Editor test when available; otherwise run the exact menu or import operation | The operation succeeds on a representative asset with no collateral changes |
| Asset loading, bundles, Addressables, YooAsset | Compile plus the narrowest initialization or loading scenario | The target asset resolves in the expected play mode or build configuration |
| Network or protocol path | Contract/dispatcher test when available, plus a targeted connection scenario | Send, receive, reconnect, and failure behavior relevant to the change are covered |
| Deterministic or lockstep simulation | Pure simulation test or a known replay/log comparison, plus a view consistency check | The same input produces the same logic result and the view consumes it correctly |
| Generated code | Change the generator or source configuration, then regenerate | Regeneration is repeatable and only the expected generated output changes |

## Test-first eligibility

Use test-first development only when all of these hold:

- The assertion observes caller- or player-visible behavior through a stable boundary.
- The result is deterministic, or time, randomness, networking, and asset boundaries can be controlled cleanly.
- The repository already has a suitable test assembly and runner, or adding one is explicitly in scope.
- The cycle is fast enough to repeat without depending on incidental Editor state.

Prefer compile-and-exercise slices when any of these dominate:

- Correctness depends on frame order, Unity callbacks, scene loading, serialized references, animation, rendering, or platform integration.
- The proposed test mostly mocks `GameObject`, `MonoBehaviour`, UI framework objects, or internal collaborators.
- Creating the harness would exceed the request or would hide the behavior being fixed.

## Boundary rules

- Test public systems and domain operations, not private helpers.
- Control real boundaries such as time, randomness, network transport, file access, and asset services. Use real project objects for internal collaborators when practical.
- Take expected values from specifications, worked examples, fixtures, known replays, or serialized reference assets, not from the implementation.
- Pair logic-side and view-side verification when gameplay state and presentation must agree.

## Command hierarchy

1. Use the command or existing test runner the repository records.
2. When the generated project is a reliable compiler check, compile the smallest affected project.
3. Run a focused EditMode or PlayMode test target when one exists.
4. Use Unity batch mode only when the project supports it and no conflicting Editor instance holds the project.
5. Use a targeted manual check when automation cannot observe the behavior faithfully; report the exact unverified scenario when it cannot be run at all.
