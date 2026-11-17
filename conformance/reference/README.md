# Reference algorithm cases

[`cases.json`](cases.json) contains a synthetic host binding and independent
cases, described by [`schema.json`](schema.json). These cases exercise the
optional [reference algorithm](../../REFERENCE.md), not the shared core ranking
contract. An implementation that claims a part of the reference algorithm runs
the applicable cases for that part and compares each ordered result to
`expected`. Resource cases apply when resource slots are supported, acceptance
cases when text is supported, navigation cases when structured navigation is
supported, and flow cases when flow proposals are supported. The core suite
independently tests typed resources on any text surface with resource slots;
it does not require structured navigation. Host boundary checks are also
required: synthetic cases cannot prove capture, persistence, or privacy.

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
`existing_flow: true` marks an action the host identifies as an existing flow;
an ordinary action with multiple capability steps is not a flow by that fact
alone. Unspecified `existing_flow` is false.

## Runner contract

For ranking and flow cases, replay `events` by ascending timestamp, ascending
writer ID in lexicographic UTF-8 byte order, then ascending numeric `position`.
Positions are unique within a writer and describe its logical log, independent
of array order or physical segments. `query.current_writer` identifies the
current session. Every commit includes its actual `surface`, independent
`origin`, `command_kind` (semantic or native), `arguments_present`, and the
`resource_selections` map from each selected slot ID to its resource ID.
`recorded_path` is the root-to-target node-ID sequence recorded at commit, or
the single root ID for a native command. A semantic path appends filled slot
IDs in declaration order, even when the slots are declared as siblings; the
last ID is its target. A `resource_rename` fact maps `from`
to `to` for its `slot_id` and adds no credit or active day. All event times
precede or equal the query time.

`tree` is the inventory at replay. An optional `recording_tree` illustrates an
earlier inventory; it is not a replay input and need not describe every event.
Replay uses each event's recorded IDs and path, including removed nodes, without
reconstructing that path from any inventory. For a stable ID, a move or token
rename does not erase node usage or move historical edges. Only current choices
are offered.

A ranking query provides `text`. A null `parent` denotes the implicit root.
At the root, a nonempty text identifies a case-sensitive prefix: rank only the
leading contiguous block of matching roots, and retain the remaining roots in
structural order. Derive each root's match status and the groups from the query
and tokens; neither is an input. Return the match-status map as `matches` and
the ranked `prefix` and unranked `rest` groups as `groups`. Their items
concatenate to `choices`. Return separately shown shortcuts in `promotions`.
Ordinary promotions match a case-insensitive prefix of the rendered path.
Suppress them entirely while a root query is nonempty, even when a path matches;
with empty root text all paths match. Root miss recovery is not modeled by this
synthetic binding.

For a resource-slot parent, `matches` supplies the index's match status. Return
only current candidates whose value is true; an omitted status means true.
Every ranking query has a `match_quality` map; use `{}` outside a resource
frontier. For a resource frontier it maps every current candidate ID, including
non-matches, to a nonnegative integer. The repository's `just check` validates
coverage and reports missing or extra IDs. A false match remains excluded even
if its quality is zero. For an ordinary-slot parent, return the transient
`suggestions` IDs in display order, using the slot-position score, not
persisted suggestion values.

A flow query returns `proposals` in display order, each with its `id`, project,
synthetic context's `resource`, complete capability `steps`, support, and score.
The grouping uses project, exact context, and the complete ordered steps. The
synthetic proposal ID is the UTF-8 JSON Canonicalization Scheme (RFC 8785)
encoding of `[project, exact_context, steps]`, where `exact_context` is the
ordered vector of normalized values named by the binding's `exact` fields.
The `flow_order` case supplies unordered proposal groups with score, support,
and recency as comparator inputs; derive IDs and return the ordered proposals.
Flow queries return at most six proposals after sorting all qualifying groups.
Resource rename and other non-invocation facts are excluded before finding
adjacent invocations and before applying the event limit. Invocations from
another project remain in the stream and break a sequence.

For text `acceptance`, apply `choice` at `line` and `cursor`; `replace_root`
identifies root completion. When `select_from_frontier` is true, use the actual
slot suggestion. Return the resulting line and cursor. Structured `navigation`
starts at `current` with the given slot-to-resource `selections` and the
slot-to-transient-suggestion-ID `ordinary_values`. `accept`,
`advance`, and `commit` choose the corresponding action; `select` records the
chosen candidate without dispatching and advances to any next slot. `back`
clears the current slot's selection and returns to the preceding slot or parent.
`type_commit` resolves its decoded slot `text` by exact, case-sensitive candidate
label; tokenization and escapes apply before matching. One match commits its ID,
while zero or multiple matches keep the slot open.
Return the current node,
selections, ordinary values, the ordered IDs of required slots still missing,
and whether dispatch committed.
Only a commit includes the selections as `event_resources`; otherwise that map
is empty. Where `event` is expected, return the shown event-fact projection or
null; ordinary values never appear in it. The boundary checks verify that the
complete stored event excludes them. An absent optional slot does not block commit.

The expectations were generated with cmdux at
`842338bcd4dca02d66b9a6fc03e1f7792edfa3d9` in isolated headless sessions. cmdux
has no resource slots or independent origin, so the adapter projects resource
IDs to synthetic nodes, computes their scores with cmdux, and supplies the
match, rename, typed-resource resolution, multi-slot navigation, and optional-slot
behavior. It projects a host-declared existing flow into a flow-stream breaker,
without changing its stored commit. For ranking, it projects a native shortcut
onto cmdux's no-credit semantic-shortcut replay; flow cases retain a native
invocation so it still breaks sequences. Slot paths come from cmdux's prepared
capture; a skipped optional position before a filled slot is projected because
cmdux cannot advance past the empty slot. For replay, the adapter
encodes each recorded ID path independently, projects node and edge identities
separately, and normalizes logical writer positions. It
applies the specified horizon and flow lookback before replay: pinned cmdux
chooses the wrong occurrence in the Lord Howe fold for both cutoffs. It projects
proposal IDs from the group key because cmdux uses the steps alone. The
`flow_order` case exercises the same comparator with synthetic tied candidates.
These projections generate expectations; they do not establish native cmdux
conformance to those boundaries.
