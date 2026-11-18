# Host bindings

A conforming implementation MUST document the following host-specific choices.
The Neovim column describes cmdux at commit `fea859b7b39125a9009c3bbea0f25fd23fcc60af`.
It describes current behavior, including the adoption gaps in the
[changelog](CHANGELOG.md); it is not itself a conformance claim or a
requirement to use Neovim's APIs or storage format.

| Binding | What the implementation defines | cmdux / Neovim |
| --- | --- | --- |
| Commit surfaces | Each surface, its commit gesture, its editing context, and the lifecycle that meets the recording deadline. | Ex command line on non-aborted command submission, picker on dispatch, and explicit `dispatch` for mappings. Promotions and Recall use the submitting surface. Capture precedes execution, with recording on return to input, at the next commit if still pending, or on normal exit. A plain programmatic command is not a commit. |
| Inventory and ownership | How live commands, named nodes, slots, capabilities, ownership, and changes are discovered; how a collision is handled; which commands or surfaces are excluded from the claim. | Neovim's command inventory plus registered providers. Global and buffer-local commands determine the effective owner. cmdux claims a semantic root when its name is unoccupied or already owned; a foreign or shadowing command remains native. Provider-declared structural nodes are eligible for persistence. A provider can suppress capture with `learn = false`; a provider without `persistable_nodes` can lose named path segments and report arguments present. These behaviors need an explicit exclusion or correction before a conforming claim. |
| Identities and resource index | How node IDs are formed and maintained. For each resource slot, declare the index, matching and any quality scale, refresh, typed-value resolution, and whether unresolved or ambiguous input is refused or kept open. Describe identity through rename and how ID reuse respects retained intent and rename mappings. | Node IDs are paths of canonical tokens; a token rename changes the ID and does not automatically move its history. cmdux declares no resource slots: buffer numbers are transient ordinary slot values. |
| Context and scope | How the host identifies the active project and the underlying working context, which closed identifiers are persisted, and how any exact or facet keys it uses are derived. State how active project affects ranking, if at all. | Project is the edited file's Git root, else the working directory's Git root, else the working directory. Unnamed buffers and panels use the working directory. The project is hashed and its history is weighted separately from other projects'. The editing window supplies the context even while a picker is open. |
| Derivation and time | The calendar operation for the 365-day horizon, including timezone and gap/fold handling; context, decay and promotion behavior; whether each part follows or departs from the reference. | Horizon 365 local calendar days and the cmdux scoring and promotion rules from which the reference is derived. Its local calendar operation passes the adjusted date to `os.time` with `isdst` unset, so gap/fold normalization follows the runtime. At the tested repeated Lord Howe time, it chooses the earlier occurrence, while the reference chooses the later one; its flow lookback has the same difference. Other reference projections and gaps are in the changelog and reference runner contract. |
| Behavioral witnesses | Reproducible contrasts for history, context, and decay, plus a promotion produced from recorded history. Resource-capable hosts also cover usage by slot and identity through rename and reuse of a label or path. | Reference cases illustrate cmdux's algorithm through projections. Native core witnesses and boundary checks still need to be supplied and run before a conformance claim. |
| Log and writer | Storage location, writer/session identity, format, synchronization, replay ordering, retention, selectable reset scopes, and error reporting. | Separate learning and friction JSONL directories under `stdpath("state")/cmdux/events/`. Each Neovim process has its own uniquely named, numbered writer segments; filenames identify the session. Replay sorts by timestamp, filename, and offset, which can disagree with writer position across segments. Shortcut origin and `recall` can replace the submitting surface in the event. Segments rotate after their oldest event exceeds 30 calendar days; finished segments can be removed after both their last observed modification and all events cross the 365-day horizon. Reset deletes the selected channel and invalidates pending captures. |
| Acceptance | Token boundaries, cursor units and placement after acceptance, choice selection, editing owner, and how a resulting line is dispatched. | Neovim and Blink use zero-based byte offsets for edits. Unescaped whitespace and `\|` delimit a token. Blink owns acceptance in its menu. cmdux places the cursor at the end of the replacement when it applies the edit. Picker handoff carries the line and cursor. Enter uses an explicitly selected choice or the line as typed. In the picker, both confirmation and drill-in use the same Enter action, so a hybrid cannot be explicitly advanced without dispatch. Native argument completion and dispatch remain Neovim's. |
| Matching | How a query matches and groups choices before ranking. | For typed root searches, cmdux reorders only the leading block of case-sensitive prefix-matching roots and suppresses ordinary promotions while the root query is nonempty. Root miss recovery can match learned paths case-insensitively and offer a hyphenated alias such as `project-files` that accepts `Project files`. |
| Flows | If offered, supported step shapes and commit surfaces, plus how the host obtains steps and any proposal IDs. | cmdux exposes predefined one- and two-step `Flow` commands and resolves complete steps for learned proposals from live providers. Each proposal ID combines capability-label slugs with a hash of the complete steps. It omits project and context, so different groups can share an ID. |

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

For Neovim, the persisted context has `surface`, `surface_detail`, `filetype`,
`buftype`, and `mode`. It excludes the path and invoking command surface. The
exact key combines all five fields. Facets are the deduplicated legacy context
key; surface; surface plus detail; filetype; surface plus filetype; buftype;
and mode. Empty filetype and buftype are represented as `*` in keys. The
legacy key is derived from the surface and resource: `buffer`, `panel:<detail>`,
`buftype:<buftype>`, `config:filetype:<filetype>` or `config:file`, and
`filetype:<filetype>` or `file`. Undeclared live filetypes normalize to `other`;
replay does not consult the currently installed filetypes.

The planned Obsidian binding has its own picker and a `Note open <note>` path
with a typed note slot. Its inventory comes from an index and its ranking uses
that inventory with usage data. It must define the bindings above, including how
the index refreshes and preserves resource identity across renames, before making
a conformance claim.
