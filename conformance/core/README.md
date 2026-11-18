# Core conformance cases

[`cases.json`](cases.json) and [`schema.json`](schema.json) describe portable
checks of [SPEC.md](../../SPEC.md). They prescribe no scores, weights, promotion
thresholds, or exact ranking for unlike inputs. Run each case whose `requires`
capabilities the host supports, using its own algorithm and the synthetic
binding below. Passing these cases does not replace the host boundary checks.

`text_surface` and `structured_surface` are independent. `resource_slots` and
`native_promotions` mean the host offers those features.
`typed_resource_text` and `typed_resource_structured` separately mean that the
corresponding surface accepts typed resource input. Each implies its surface
and `resource_slots`. A case applies only when all its requirements are met;
a structured-only host that supports typed resource input runs the structured
cases without a text surface.

## Synthetic binding

Each case starts with empty history and the declared time, project, context,
and writer. Install the nodes referenced by the case, including its observed
structural choices, and their ancestors. Install every declared slot of each
installed action or hybrid and every candidate of each installed resource slot.
This keeps an unfilled slot and all of its candidates in the fixture. Install
the capabilities used by those nodes. Node order in `binding.nodes` declares
sibling and slot order. A node's command token is the last component of its ID.
The fixture provider's owner is `fixture`. Actions and hybrids are executable,
namespaces are expandable, and the native root has no semantic owner.

The test index and matcher replace the host's resource index and matcher for
these cases through its provider or test binding. After the host decodes input,
the synthetic matcher compares it to each current candidate's entire label,
exactly and case-sensitively. One matching ID resolves. Zero matches are
unresolved and multiple matches are ambiguous. Verify the exact `matches` set
for each typed input against the installed matcher. Ordinary slots
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
the offered promotion. If the fixture declares a required slot that is still
unfilled, verify that its slot ID is pending in the interaction. `change_path`
changes the selected semantic path without
committing. `advance` expands the current hybrid or moves from a slot to the
next. `back` returns to its parent or preceding slot. Record the current node
and its available structural child or slot positions after each `advance` and
`back` as `navigation`. When the case skips an optional slot, verify that it
remains empty and the later value is bound to its own slot.

`pick_resource` selects an index ID. `remove_resource` updates the index while
the interaction is pending. Attempt commit even if the host clears the stale
input during refresh.
`type_resource` enters decoded text on its specified surface. Its `matches`
describe the index at entry. Resolve the text against the index at commit,
including any intervening removal. `ordinary_value` supplies an ordinary
slot value. `native_arguments` supplies native argument text.
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
`confirmation: decline` declines its destructive confirmation. The default is
available and confirmed. A handler with `fails: true` starts and reports a
failure. A handler with `context_after_start` changes the working context to
that value during execution. Verify the effect has taken place by the recording
deadline. `executions` lists the handlers that actually started, in order.

The `capabilities` binding describes one instrumented capability. Register it
through the host's actual capability boundary; its implementation and policy
names identify the test callback and the host safety policy under observation.
When `expected.capabilities` is present, record which implementation actually
ran and which policy and safety were actually checked for each capability call,
in order. Do not infer those observations from the selected path or expected
values. The direct and promoted cases use this same capability. The flow
variant runs at the host boundary with a supported flow shape.

Compare `expected.events` to recorded user intents in order, projecting exactly
the shown fields. Check stored time, project, context and writer against the
fixture's pre-execution values and the full records against the facts-only rules.
Inspect each capture by the first of host readiness for another command or
normal termination, and before any subsequent commit. A string in
`expected.forbidden_text` must occur nowhere in retained records, including
diagnostic records. `status`, when present, lists acceptable end states. No
event or execution is allowed when the expected list is empty.

## Other cases

For an `edit`, apply the operation at the byte cursor and compare the full
line. Typing inserts the supplied text without rewriting surrounding input and
uses the expected cursor in the fixture. Acceptance replaces the token under
the cursor. Check the resulting cursor against the host's declared policy.

For `cutoff`, independently calculate the instant 365 local calendar days
before `now` using the host's declared timezone and gap/fold policy. Retain one
fact exactly at that instant and one at the immediately preceding representable
timestamp. Keep the fixture records physically available across both requests,
for example in live-writer storage that does not purge during the check; this
sets up the still-existing-history precondition and does not require production
storage to retain expired records. Check eligibility at `now`. Move the clock
back to the cutoff instant and check the earlier fact again. It is then in the
past and inside the 365-day horizon. Compare the three booleans; do not use the
host's horizon length or cutoff result as the oracle. If the binding's timezone
permits an offset change between `now` and its 365-calendar-day cutoff, run the
same probe at such an instant. If the fixture instant already distinguishes
calendar days from elapsed days, it also serves as that probe. Check the single
calendar operation wherever the host uses a cutoff.

For `consistency`, install the projected ordinary command `history` as actual
facts with the fixture's time, context and writer. A history event with a
`surface` uses that surface and requires its capability. Otherwise use any one
claimed commit surface supported by the host; hold that choice fixed across
the two requests. Obtain the complete underlying ranking of `candidates` twice
with identical inputs. For `surfaces`, use a text and a structured surface
under the [§4 equality condition](../../SPEC.md#4-derived-state-time-and-ranking).
For `replay`, rebuild from the same retained history between queries. The
ordered lists must match and contain exactly the declared candidates.

## Host boundary checks

Run and report each applicable [§7 check](../../SPEC.md#7-implementation-boundary-checks)
through the binding's normal surfaces, execution, storage, and ranking.
Inspect actual events and count handler starts at those boundaries.

### Capture and commitment

- **Commit timing.** On each claimed commit surface, start at one time, change
  the controlled clock after opening the interaction and before submitting,
  then advance it again during execution and before any deferred write. Change
  a captured working-context identifier at both transitions and change the
  active project at each transition the host supports.
  For a surface with an immediate gesture, set the commit values before the
  gesture and change them inside the handler. Verify the transitions occurred
  and that the stored values match the gesture. At the §3 deadline, also check
  command, surface, origin, kind, argument presence, any applicable resource
  IDs, and exclusion of ordinary values. For deferred writers, exercise
  readiness, normal termination and a subsequent commit as recording deadlines.
- **Native and replay capture.** Commit an unowned native command directly on
  every surface accepting native commands, with and without arguments where
  supported. Check root, argument presence, and surface. If the host offers
  recall, replay an owned command from each accepting surface. Require exactly
  one new intent for the underlying command with the surface used for replay.
- **Incomplete input.** Attempt an explicit submit with a required ordinary
  slot empty and check for zero intents and handler starts. Fill the slot with
  a valid value and repeat through the same path. Require one intent and one
  handler start. Exercise a promotion both through slot completion and through
  leaving its prefix. Verify shortcut origin only on completion through the
  promotion. Abandoned input and nested execution add no intent.

### Resource identity

- **Index at commit.** On each surface accepting typed resources, check unique,
  missing, and ambiguous matches. Type a label while it matches exactly one
  candidate, then remove that match or add a second before submission.
  Require zero intents and handler starts. Also attempt commit after removing a
  picked ID and require the same counts. Commit two resource selections in one
  event and check each mapping under its own slot ID.
- **Usage by slot.** Put the same two resources in two slots with equal matching
  conditions, using a test provider if needed. Seed opposing histories in
  the two slots, then swap the histories assigned to the slots while keeping
  each resource's total usage and other derivation inputs fixed. At a fixed
  slot frontier, require the candidates' relative order to change.
- **Rename and reuse.** Exercise each declared rename kind. Record usage for a
  resource, rename it, and create a different resource at the old label or path
  while the old intent and any mapping are retained. Check the replacement ID
  differs from the original resource's IDs before and after rename. Rebuild
  from retained facts and verify the renamed resource keeps its usage, the new
  one starts without it, and a new invocation credits only the replacement. The
  rename itself adds neither an invocation nor credit. For hosts that use
  mappings, also reject or safely skip ambiguous and cyclic mappings without
  conflating resources or disturbing unrelated valid history.

### Resolution and execution

- **Independent resolution.** Resolve the same command with availability on
  and off. Change only learned history and verify grammar, ownership and
  availability stay fixed. Verify unconsumed input cannot dispatch.
- **Refusal after a complete submit.** Submit an already-unavailable action
  on each surface that permits explicit submission in that state. Supply a
  valid ordinary slot value where supported. Also make the action unavailable
  between commit and execution, and separately decline destructive
  confirmation, on direct and promoted paths. Submit an invalid ordinary
  value directly and by completing a promoted path. Each refusal retains
  exactly one intent with the correct path, surface and origin, and never
  starts the handler or stores the value.
  Separately, make a committed standalone handler start and fail. Require
  exactly one intent by the deadline.
- **Shared capability and flow stops.** Observe the same instrumented
  capability's actual implementation and safety policy directly, through a
  promotion, and as a step of a supported flow. Probe unavailability and
  destructive confirmation in separate runs. For a flow with multiple steps,
  have the first step succeed and make the next step unavailable in one run
  and destructive in the other, where the binding supports each transition.
  Where a property is fixed or the flow has a single step, use a step with
  that property set. Decline the destructive step's confirmation. Require
  zero starts for the blocked step and any subsequent steps. Also exercise
  invalid step input and failure after a step starts, using a second step
  after a successful first where supported. Invalid input prevents its
  handler from starting, and both cases prevent subsequent steps from running.

### Storage and replay

- **Replay order.** Rebuild from the actual log and compare results for equal
  inputs. Move a stable node and check its history and recorded ancestor edges.
  Check equal-time events within one writer across log segments if the host
  uses them. For multiple writers, replay equal-time records from two writers
  twice with storage enumeration reversed. Compare the observed replay order
  to the binding's declared tie-break in each run.
- **Time.** Exercise the calendar cutoff and backward clock operation with
  retained records through the actual log, crossing a UTC offset change if the
  binding's timezone permits one. Follow the independent cutoff calculation
  used by the portable case.
- **Writer, reader, and reset.** Send a well-formed record with an undeclared ID
  to the production writer and inspect storage for its absence. Check that
  readers skip malformed records and read valid records without the original
  provider. Verify storage failures are reported. Reset with a pending capture,
  then make a new commit and verify only the new one appears. For selective
  reset, seed in-scope and out-of-scope records. Verify the former are removed
  and the latter preserved in storage and after rebuilding derived state.

### Ranking and cache freshness

- **Witnesses and invariance.** Use the reproducible [binding witnesses](../../BINDINGS.md).
  Keep the compared facts eligible at both decay observations and obtain a
  promotion from real recorded history. Hold derivation inputs fixed when
  comparing ranking and promotions before and after navigation, and separately
  before and after adding diagnostic friction.
- **Cross-surface ranking.** For each group of claimed ranking surfaces that
  can issue an equivalent request, compare the complete underlying order on
  every surface, including surfaces of the same kind. Hold all §4 inputs equal,
  including active project, frontier, inventory, index snapshot and complete
  match results.
- **Changed inputs.** For each applicable §4 input, prime any cache and compare
  the next result after changing that input with a fresh result. Choose an
  observable transition where the binding says the input affects results.
  Otherwise check the declared invariant. Where active project affects ranking,
  switch only project, holding working context and other inputs fixed. Keep
  recorded history for removed inventory or index entries and require the
  removed commands, affected promotion paths, and removed resources to be
  absent from the next result.

### Text input

- **Live suggestions and handoffs.** On each claimed text boundary, type a query
  that makes a live choice available. Where learned promotions are supported,
  seed history and verify a promotion is offered. Check the entire line after
  the suggestion appears and before accepting it, then verify the edit follows
  §6 on acceptance. Check line and cursor preservation on text and structured
  handoffs from text.
