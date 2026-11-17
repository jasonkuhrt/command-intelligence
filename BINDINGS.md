# Host bindings

A conforming implementation MUST document the following host-specific choices.
The Neovim column describes cmdux at commit `842338bcd4dca02d66b9a6fc03e1f7792edfa3d9`.
It is an example, not a requirement to use Neovim's APIs or storage format.

| Binding | What the implementation defines | cmdux / Neovim |
| --- | --- | --- |
| Commit surfaces | Each surface, its commit gesture, its editing context, and when a captured intent is recorded. | Ex command line on non-aborted command submission; picker when it dispatches; promoted shortcut when dispatched; Recall when replaying an owned command; explicit `dispatch` for mappings. Capture precedes execution; record on return to input, at the next commit if still pending, or on normal exit. A plain programmatic command is not a commit. |
| Inventory and ownership | How live commands, named nodes, slots, capabilities, ownership, and changes are discovered; how a collision is handled. | Neovim's command inventory plus registered providers. Global and buffer-local commands determine the effective owner. cmdux claims a semantic root only if available; a foreign or shadowing command remains native. Provider-declared structural nodes are eligible for persistence. |
| Context and scope | How the host identifies a project and the underlying working context, which closed identifiers are persisted, and how exact and facet keys are derived. | Project is the edited file's Git root, else the working directory's Git root, else the working directory. Unnamed buffers and panels use the working directory. The project is hashed. The editing window supplies the context even while a picker is open. |
| Log and writer | Storage location, writer/session identity, format, synchronization, replay ordering, retention, reset, and error reporting. | Separate learning and friction JSONL directories under `stdpath("state")/cmdux/events/`. Each Neovim process has its own uniquely named, numbered writer segments; filenames identify the session. Replay sorts by timestamp, filename, and offset. Segments rotate after their oldest event exceeds 30 calendar days; finished segments can be removed after both their last observed modification and all events cross the 365-day horizon. Reset deletes the selected channel and invalidates pending captures. |
| Acceptance | Token boundaries, cursor units, choice selection, editing owner, and how a resulting line is dispatched. | Neovim and Blink use zero-based byte offsets for edits. Unescaped whitespace and `|` delimit a token. Blink owns acceptance when its menu is involved; otherwise cmdux applies the edit. Picker handoff carries the line and cursor. Enter uses an explicitly selected choice or the line as typed. Native argument completion and dispatch remain Neovim's. |

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
that inventory with usage data. It must define the bindings above before making a
conformance claim.
