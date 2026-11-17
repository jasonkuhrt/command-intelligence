# Conformance cases

[`cases.json`](cases.json) contains a synthetic host binding and independent
cases, described by [`schema.json`](schema.json). A runner compares the complete
ordered result to each case's `expected` value using the specification defaults.
All common ranking cases apply; resource cases apply when resource slots are
supported, text or navigation cases when the respective surface is supported,
and flow cases when flow proposals are supported. The implementation's actual
surface and storage checks are required separately: synthetic cases cannot prove
capture, persistence, or privacy.

## Synthetic binding

Use the binding declared in the suite for these cases, regardless of the host's
own tokenizer or facets. Its IANA timezone is UTC unless a case supplies
`timezone`. Its tokenizer treats unescaped ASCII whitespace and `|` as
separators, a backslash as escaping the next byte, and cursors as zero-based
UTF-8 byte offsets. Strings use ascending UTF-8 byte order wherever the
specification calls for a string tie-breaker.

A context consists of the binding's `fixed` fields, with the case's `resource`
as the field named by `resource_field`; `project` is a separate scope. Replace
empty field values by `empty_value` when forming keys. The exact key is the
ordered `exact` field tuple. Each list in `facets` forms a facet tuple including
its field names; deduplicate equal facets. The case time is a UTC instant; the
timezone determines local days and cutoff normalization.

Every case starts with empty history. Its `tree` is the current full inventory
in structural order. Node IDs are unique host-declared identifiers and need
not be paths or token spellings; `token` supplies a spelling. A slot declares
whether it is `required`. Its `values` are ordinary live suggestions used by
text cases. For an ordinary-slot frontier, `suggestions` supplies each value and
a transient fixture ID; neither is a persistent node ID. A resource slot's
`candidates` have declared IDs and labels. Resource IDs are distinct from node
IDs and ordinary slot values.

## Runner contract

For ranking and flow cases, replay `events` by ascending timestamp, ascending
writer ID in lexicographic UTF-8 byte order, then ascending numeric `position`.
Positions are unique within a writer and describe its logical log, independent
of array order or physical segments. `query.current_writer` identifies the
current session. Every commit includes its actual `surface`, independent
`origin`, `command_kind` (semantic or native), `arguments_present`, and the
`resource_selections` map from each selected slot ID to its resource ID.
`recorded_path` is the root-to-target node-ID sequence recorded at commit, or
the single root ID for a native command. A `resource_rename` fact maps `from`
to `to` for its `slot_id` and adds no credit or active day. All event times
precede or equal the query time.

When present, `recording_tree` is the inventory when events were recorded;
`tree` is the inventory at replay. Otherwise both are `tree`. Replay uses the
recorded IDs and path, including removed nodes, rather than reconstructing the
path from the current inventory. For a stable ID, a token rename does not erase
usage. Only current choices are offered.

A ranking query provides `text`. A null `parent` denotes the implicit root.
At the root, a nonempty text identifies a case-sensitive prefix: rank only the
leading contiguous block of matching roots, and retain the remaining roots in
structural order. When supplied, `matches` states each candidate's match status,
and `groups` describes the pre-ranking groups in order, including whether a
group is ranked. Root groups are derived from the query and tokens, not simply
copied into the result. Return all resulting structural IDs in `choices`,
separately shown shortcut IDs in `promotions`, and, when groups are given, each
resulting named group in `groups`. The group items concatenate to `choices`.

For a resource-slot parent, return only current candidates whose `matches` value
is true; an omitted match status means true. `match_quality` maps candidate IDs
to nonnegative integers. A false match remains excluded even if its quality is
zero. For an ordinary-slot parent, return the transient `suggestions` IDs in
display order, using the slot-position score, not persisted suggestion values.

A flow query returns `proposals` in display order, each with its project,
synthetic context's `resource`, complete capability `steps`, support, and score.
The grouping uses project, exact context, and the complete ordered steps.

For text `acceptance`, apply `choice` at `line` and `cursor`; `replace_root`
identifies root completion. When `select_from_frontier` is true, use the actual
slot suggestion. Return the resulting line and cursor. Structured `navigation`
starts at `current` with the given slot-to-resource `selections`. `accept`,
`advance`, and `commit` choose the corresponding action; `select` records the
chosen candidate without dispatching, and `back` clears the current slot's
selection and returns to its parent. Return the current node, selections, the
ordered IDs of required slots still missing, and whether dispatch committed.
Only a commit includes the selections as `event_resources`; otherwise that map
is empty. An absent optional slot does not block commit.

The expectations were generated with cmdux at
`842338bcd4dca02d66b9a6fc03e1f7792edfa3d9` in isolated headless sessions. cmdux
has no resource slots or independent origin, so the adapter projects resource
IDs to synthetic nodes, computes their scores with cmdux, and supplies the
match, rename, selection, and optional-slot behavior. It maps fixture IDs to
cmdux token paths and projects stable identity across tree changes. It also
normalizes logical writer positions and applies the specified calendar horizon
before replay: pinned cmdux itself chooses the wrong occurrence in the Lord Howe
fold. These projections generate expectations; they do not establish native
cmdux conformance to those boundaries.
