# Conformance cases

[`cases.json`](cases.json) is a language-neutral array of independent cases,
described by [`schema.json`](schema.json). A runner MUST check every case with
the specification's default configuration and compare the entire ordered
result with `expected`. Passing these cases does not establish every requirement
of the specification.

Each case supplies its complete tree. Array order is structural order; `id` is
the stable path identity and `token` is its spelling. Slash-separated IDs and
`$` slot positions are fixture conventions. Node IDs are unique within a case;
event and parent IDs refer to that tree. A slot's `values`, when present,
are live suggestions, not children or stored facts. All fixture nodes are
available and their terminal actions executable. No other inventory contributes
choices. Start every case with empty history.

For a `ranking` case:

1. Replay its events in timestamp order, preserving input order for equal times.
   `previous` is one earlier writer session and `current` is the querying writer
   session; the latter contributes session heat. `surface: shortcut` is a
   dispatched, previously promoted shortcut. Other surfaces are direct commits.
2. Use UTC for local calendar days. Each context's `project` is an opaque,
   distinct project identity. The complete context vector is `surface=file`,
   `surface_detail=buffer`, `filetype=resource`, `buftype=""`, `mode=n`.
   Its exact key is the five values; its deduplicated facets are
   `filetype:<resource>`, `surface:file`, `surface:file|detail:buffer`,
   `surface:file|filetype:<resource>`, `buftype:*`, and `mode:n`.
3. At `query.time` in `query.context`, rank the children of `query.parent`;
   `null` means the implicit root. Return their IDs as `choices` and the IDs of
   separately displayed shortcuts as `promotions`, both in display order.

When an event targets a slot, a runner that records an invocation MUST also
verify that its persisted event identifies the slot and contains none of the
slot's suggested values. The reference adapter supplies the first suggestion as
the transient argument and inspects the resulting log.

For an `acceptance` case, choose `input.choice` in the given tree and apply it
to `input.line` at `input.cursor`. `replace_root` identifies root completion;
when `select_from_frontier` is true, accept the actual suggestion from the slot
frontier. Offsets are zero-based UTF-8 bytes, including the resulting cursor.
Unescaped whitespace and `|` delimit tokens; a backslash escapes the next byte.
Return the resulting line and cursor.

The expected results were generated with the actual cmdux ranking and completion
code at `842338bcd4dca02d66b9a6fc03e1f7792edfa3d9`, using headless Neovim and
isolated XDG directories. The optional [reference adapter](reference/) can
check a cmdux checkout against the committed cases via the root `justfile`'s
`check-cmdux` recipe. Implementations of other hosts write their own runner for
the contract above; neither Neovim nor the adapter is required for the cases.
