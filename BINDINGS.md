# Host bindings

A conforming implementation MUST document the following host-specific choices
in its own binding document, beside its declared specification version.

| Binding | What the implementation defines |
| --- | --- |
| Commit surfaces | Each surface, its commit gesture, its editing context, and the lifecycle that meets the recording deadline. |
| Inventory and ownership | How live commands, named nodes, slots, capabilities, ownership, and changes are discovered; how a collision is handled; which commands or surfaces are excluded from the claim. |
| Identities and resource index | How node IDs are formed and maintained. For each resource slot, declare the index, matching and any quality scale, refresh, typed-value resolution, and whether unresolved or ambiguous input is refused or kept open. Describe identity through rename and how ID reuse respects retained intent and rename mappings. |
| Context and scope | How the host identifies the active project and the underlying working context, which closed identifiers are persisted, and how any exact or facet keys it uses are derived. State how active project affects ranking, if at all. |
| Derivation and time | The calendar operation for the 365-day horizon, including timezone and gap/fold handling; context, decay and promotion behavior; whether each part follows or departs from the reference. |
| Behavioral witnesses | Reproducible contrasts for history, context, and decay, plus a promotion produced from recorded history. Resource-capable hosts also cover usage by slot and identity through rename and reuse of a label or path. |
| Log and writer | Storage location, writer/session identity, format, synchronization, replay ordering, retention, selectable reset scopes, and error reporting. |
| Acceptance | Token boundaries, cursor units and placement after acceptance, choice selection, editing owner, and how a resulting line is dispatched. |
| Matching | How a query matches and groups choices before ranking. |
| Flows | If offered, supported step shapes and commit surfaces, plus how the host obtains steps and any proposal IDs. |

Each witness supplies the inventory, index snapshot where applicable, facts,
configuration, session, time, active project, working context, frontier, query,
and match results for both observations and their expected results. History
witnesses compare different committed histories. Context witnesses hold history
and query fixed while changing context. Decay witnesses hold the compared
candidates' usage fixed and eligible at both observations under the 365-day
horizon, while time or neutral activity changes as the binding requires. A
promotion witness compares real recorded history with a control and observes
a promotion produced by the implementation. Resource witnesses follow the
per-slot and rename setups in the [boundary runner](conformance/core/README.md#resource-identity).
A binding explains any coupled input changes needed to observe its algorithm.

## Implementations

- cmdux, for Neovim, declares 0.4.0 in its `BINDING.md`. Its exclusions and
  known deviations are listed there, not here.

The planned Obsidian binding has its own picker and a `Note open <note>` path
with a typed note slot. Its inventory comes from an index and its ranking uses
that inventory with usage data. It must define the bindings above, including how
the index refreshes and preserves resource identity across renames, before making
a conformance claim.
