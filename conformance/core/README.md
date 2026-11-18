# Core conformance cases

[`cases.json`](cases.json) and [`schema.json`](schema.json) describe portable
checks of [SPEC.md](../../SPEC.md). They prescribe no scores, weights, promotion
thresholds, or exact ranking for unlike inputs. Run each case whose `requires`
capabilities the host supports, using its own algorithm and the synthetic
binding below. Passing these cases does not replace the host boundary checks.

`text_surface` and `structured_surface` are independent. `resource_slots`,
`native_promotions`, and `flows` mean the host offers those features.
`typed_resource_text` and `typed_resource_structured` separately mean that the
corresponding surface accepts typed resource input. Each implies its surface
and `resource_slots`. A case applies only when all its requirements are met;
a structured-only host that supports typed resource input runs the structured
cases without a text surface.

## Synthetic binding

Each case starts with empty history and the declared time, project, context,
and writer. Install only the fixture nodes, slots, capabilities and resources
referenced by that case, their required ancestors, and its observed choices or
flow steps. Do not install the other resource slots, flow commands, or surface
features merely because they appear elsewhere in the shared binding. Node order
in `binding.nodes` declares sibling and slot order. A node's command token is
the last component of its ID; the fixture provider's owner is `fixture`.
Install an action or a hybrid as executable, and a namespace as expandable.

The test index and matcher replace the host's resource index and matcher for
these cases through its provider or test binding. After the host decodes input,
the synthetic matcher compares it to each current candidate's entire label,
exactly and case-sensitively. One matching ID resolves; zero or multiple IDs
remain unresolved. Duplicate labels are distinct candidates. Ordinary slots
accept all values unless `valid_values` is present; then they accept exactly
one of those values. The tokenizer uses unescaped whitespace and `|` as
separators, `\` escapes the next character, and cursor offsets count UTF-8
bytes. An `edit` supplies its accepted spelling directly and needs no provider.

Use the host's usual capture, validation, execution, log, and replay boundaries.
Reset history, execution observations, and interaction state before each case.
Timezone, gap/fold policy, context model, decay, and promotion algorithm remain
binding choices. The horizon is 365 local calendar days. A `choose` through
`promotion` presents the stated path as a test promotion; it tests the
interaction, not eligibility. Each host also runs its own witness where real
recorded history produces a promotion without injection.

## Interaction cases

Perform `actions` in order. `choose` opens the given path directly or through
the offered promotion. `change_path` changes the selected semantic path without
committing. `advance` expands the current hybrid or moves from a slot to the
next; `back` returns to its parent or preceding slot. Record the current node
and its available child or slot choices after each `advance` and `back` as
`navigation`. An optional empty slot can be advanced past.

`pick_resource` selects an index ID; `type_resource` enters decoded text on its
specified surface and attempts resolution at commit. `ordinary_value` supplies
an ordinary slot value; `native_arguments` supplies native argument text.
`cancel` abandons the interaction. `internal` executes a path programmatically,
without creating a separate user commit.

`resolve` asks the host to resolve the given synthetic grammar tokens after
setting the action's availability to the given value, before resolution. Tokens
identify fixture choices and can be supplied to a structured path resolver;
the case does not require a text surface. Record the resolved target, owner and
unconsumed tokens in `resolutions`; availability is not part of that projection.
It neither commits nor executes the action.

`commit` uses the named surface and the host's normal commit gesture. `trailing`
adds the given unconsumed input after the selected action. `available: false`
means the action becomes unavailable after commitment and before execution.
`confirmation: decline` declines its destructive confirmation; the default is
available and confirmed. For a flow, `unavailable_step` or `declined_step`
becomes unavailable or has confirmation declined before it starts. A
`failed_step` starts and then fails. `executions` lists actions or flow steps
that actually started, in order, including a failed step. The flow itself is
the committed command; its internal steps are not separate user commits.

The `capabilities` binding describes one instrumented capability. Register it
through the host's actual capability boundary; its implementation and policy
names identify the test callback and the host safety policy under observation.
When `expected.capabilities` is present, record which implementation actually
ran and which policy and safety were actually checked for each capability call,
in order. Do not infer those observations from the selected path or expected
values. Accepted confirmations apply at every required check, including a flow
step. The direct, promoted, and flow cases use this same capability.

Compare `expected.events` to recorded user intents in order, projecting exactly
the shown fields. Check stored time, project, context and writer against the
fixture and the full records against the facts-only rules. Inspect each capture
by the first of host readiness for another command or normal termination, and
before any subsequent commit; an implementation may record sooner. A string in
`expected.forbidden_text` must occur nowhere in retained records, including
diagnostic records. `status`, when present, lists acceptable end states. No
event or execution is allowed when the expected list is empty.

## Other cases

For an `edit`, apply the operation at the byte cursor and compare the full line
and cursor. Typing inserts the supplied text without rewriting surrounding
input; accepting replaces the token under the cursor.

For `cutoff`, independently calculate the instant 365 local calendar days
before `now` using the host's declared timezone and gap/fold policy. Retain one
fact exactly at that instant and one at the immediately preceding representable
timestamp. Keep the fixture records physically available across both requests,
for example in live-writer storage that does not purge during the check; this
sets up the still-existing-history precondition and does not require production
storage to retain expired records. Check eligibility at `now`. Move the clock
back to the cutoff instant and check the earlier fact again. It is then in the
past and inside the 365-day horizon. Compare the three booleans; do not use the
host's horizon length or cutoff result as the oracle. The boundary checks also
exercise its single calendar operation wherever it uses a cutoff.

For `consistency`, install the projected ordinary command `history` as actual
facts with the fixture's time, context and writer. A history event with a
`surface` uses that surface and requires its capability. Otherwise use any one
claimed commit surface supported by the host; hold that choice fixed across
the two requests. Obtain the complete underlying ranking of `candidates` twice
with identical inputs. For `surfaces`, query both surface types with the same
frontier and match results; for `replay`, rebuild from the same retained history
between queries. The ordered lists must match and contain exactly the declared
candidates. Their order in `expected` is a set, not a prescribed ranking.

## Host boundary checks

Run and report each applicable [§7 check](../../SPEC.md#7-implementation-boundary-checks):

- Capture on each claimed surface.
- Promotion origin through completion and leaving its prefix.
- Nested execution and abandoned input.
- Typed resource commits on every surface supporting that input.
- Two resource selections in one event.
- Resource rename continuity.
- Rename adds no invocation or invocation credit.
- Invalid rename mappings.
- Binding history witness.
- Binding context witness.
- Binding decay witness.
- Binding promotion witness from real recorded history.
- Binding resource-history and rename-continuity witnesses, when supported.
- Availability-independent resolution.
- Whole-input consumption.
- Learning-independent grammar and ownership.
- Invalid ordinary slot values.
- Direct and promoted availability.
- Direct and promoted destructive confirmation.
- Shared capability implementation and safety policy through each applicable path.
- Per-step flow availability, safety, confirmation, and stopping.
- Persistence and replay through the actual log.
- The 365-day horizon and backward clock.
- Deterministic replay.
- Deferred-capture deadline and the next commit.
- Reset with pending capture and a later commit.
- Malformed records.
- Replay without the original provider.
- Storage-failure reporting.
- Moved-node history and historical edges.
- Equal-time writer order, including across segments.
- Consecutive requests after facts change.
- Consecutive requests after configuration changes.
- Consecutive requests after session changes.
- Consecutive requests after inventory changes.
- Consecutive requests after time changes.
- Consecutive requests after context changes.
- Consecutive requests after query changes.
- Consecutive requests after resource-index changes, when supported.
- Consecutive requests after match results change.
- Cross-surface ranking.
- Text handoff preservation.

Compare each changed-input result with a fresh result. Prime any cache first.
A binding's reproducible witnesses supply contrasting inputs and observable
expected results for history, context, decay and real-history promotion; a
resource binding also supplies per-resource and rename witnesses. The binding
chooses the thresholds, weights and exact results.
