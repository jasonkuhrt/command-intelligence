# Conformance cases

[`cases.json`](cases.json) contains a synthetic host binding and independent
cases, described by [`schema.json`](schema.json). A runner compares the complete
ordered result to each case's `expected` value with the specification defaults.
Run all common ranking cases; resource cases apply when resource slots are
supported, text or navigation cases when the respective surface is supported,
and flow cases when flow proposals are supported. The specification's real
surface and storage checks are required separately; these synthetic cases cannot
prove capture, persistence, or privacy.

## Synthetic binding

Use the binding declared in the suite for these cases, regardless of the host's
own tokenizer or facets. Its IANA timezone is UTC unless a case supplies
`timezone`.
Its tokenizer treats unescaped ASCII whitespace and `|` as separators, a
backslash as escaping the next byte, and cursors as zero-based UTF-8 byte
offsets. Root matching ranks the leading case-sensitive prefix-matching block.

A context consists of the binding's `fixed` fields, with the case's `resource`
as the field named by `resource_field`; `project` is a separate scope. Replace
empty field values by `empty_value` when forming keys. The exact key is the
ordered `exact` field tuple. Each list in `facets` forms a facet tuple including
its field names; deduplicate equal facets. The case time is a UTC instant and
the timezone determines local days and cutoff normalization.

Every case starts with empty history. Its `tree` is the full inventory in
structural order. Node IDs are unique host-declared identifiers and need not be
paths or token spellings. `token` supplies a spelling. A slot's `values` are
ordinary live suggestions; a resource slot's `candidates` have declared IDs and
labels. Resource IDs are distinct from node IDs and ordinary slot values.

## Runner contract

For ranking and flow cases, replay `events` by timestamp, writer ID in
lexicographic UTF-8 byte order, then numeric `position`. Positions are unique
within a writer and describe its logical log, independent of the array order or
physical segments. `query.current_writer` identifies the current session. Every
commit has its actual `surface` and an independent `origin`; a
`resource_rename` fact maps `from` to `to` for its slot and adds no credit or
active day. All event times precede or equal the query time.

A ranking query returns all structural child IDs as `choices` and separately
shown shortcut IDs as `promotions`. A null parent denotes the implicit root. A
resource-slot parent returns current candidate IDs as `choices`; the query's
`match_quality` gives each candidate's nonnegative integer match contribution.
Return both arrays in display order.

A flow query returns `proposals` in display order, each with its project,
synthetic context's `resource`, complete capability `steps`, support, and score.
The grouping uses project, exact context, and the complete ordered steps.

For text `acceptance`, apply `choice` at `line` and `cursor`; `replace_root`
identifies root completion. When `select_from_frontier` is true, use the actual
slot suggestion. Return the resulting line and cursor. For structured
`navigation`, apply `action` to the named choice at `current`: `advance` and
`commit` choose the corresponding hybrid action, and `accept` selects a
namespace. Return the resulting current node ID and whether it committed.

The existing command, replay, flow, navigation, and text expectations were
checked with cmdux at `842338bcd4dca02d66b9a6fc03e1f7792edfa3d9` in isolated
headless sessions. That revision has no resource slots or independent origin:
the resource cases project each resource ID to a synthetic cmdux node and add
match quality to the real node score. The adapter normalizes logical writer
positions and maps fixture IDs to cmdux token-path IDs. These projections yield
expected results; they do not establish cmdux conformance to the new boundaries.
