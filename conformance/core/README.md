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
selection during refresh.
`type_resource` enters decoded text on its specified surface for resolution at
commit. `ordinary_value` supplies an ordinary slot value. `native_arguments`
supplies native argument text.
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
with identical inputs. For `surfaces`, query both surface types under the
[§4 equality condition](../../SPEC.md#4-derived-state-time-and-ranking): hold
the frontier and every derivation input equal, including the inventory, index
snapshot, and complete match results. For `replay`, rebuild from the same
retained history between queries. The ordered lists must match and contain
exactly the declared candidates in any shared order.

## Host boundary checks

Run and report each applicable [§7 check](../../SPEC.md#7-implementation-boundary-checks)
through the binding's normal surfaces, execution, storage, and ranking. In
addition to the portable cases, use these setups where applicable.

- On each claimed commit surface, make the handler change a captured context
  identifier, for example by opening a note of a different context kind.
  Verify the change occurred and inspect the stored pre-execution context,
  project and time at the §3 recording deadline. Commit an unowned native
  command on every surface that accepts native commands. Exercise absence
  and presence of arguments where supported, without depending on promotions.
- Make a standalone committed handler start and fail. Count exactly one
  persisted intent by the deadline. Check direct invalid ordinary input
  separately: one intent with its filled slot ID and zero handler starts.
- Run one instrumented capability directly, through a promotion, and, when
  supported, as a step of a flow the binding can execute. Observe the actual
  implementation and safety checks for that capability in each run. Use a
  supported sequence for the stopping probes. When it can have multiple steps,
  let the first succeed, then supply an invalid slot value to the second.
  Verify the second handler never starts and any later steps remain unrun.
  Check the same stop boundary for unavailability and declined confirmation,
  and for failure after a step starts. Change a later step's availability or
  safety from the first step to distinguish current checks from preflight.
- Hold host state fixed when changing only learned history for the
  availability, grammar, and ownership check. Compare underlying rankings
  and promotions before and after uncommitted navigation, and separately
  after adding diagnostic friction where supported. Keep all derivation
  inputs fixed for each comparison.
- Send a well-formed record with an undeclared ID to the production writer
  and inspect storage for its absence. For selective reset, record both
  in-scope and out-of-scope history before reset. Verify both from storage
  after reset and after rebuilding derived state.
- For changed inputs, prime any cache first and compare the next result with a
  fresh result. Keep recorded history for the removed commands or resources.
  Verify a command removed from inventory, a promotion whose path was
  removed, and a resource removed from the index are each absent from the
  relevant next result.
- Use the reproducible [binding witnesses](../../BINDINGS.md), including decay
  while the compared facts stay eligible at both observations and a promotion
  obtained from captured history.
