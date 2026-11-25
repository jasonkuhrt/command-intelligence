# Command Intelligence Specification 0.4.1

## 1. Conformance and bindings

**MUST**, **MUST NOT**, and **SHOULD** state requirements and recommendations.
**MAY** denotes an option. An implementation MUST declare its specification
version, document the host choices in [BINDINGS.md](BINDINGS.md), pass every
applicable [core case](conformance/core/README.md), and perform the boundary
checks in §7. [REFERENCE.md](REFERENCE.md) is informative: an implementation
MAY use its algorithm, and declares which parts it follows or changes.

## 2. Commands and resources

A command vocabulary is a semantic tree, possibly a forest under an implicit
root. Each declared node MUST have a stable host-declared ID; its binding
defines the ID's formation and lifetime. IDs need not be tokens or labels. A
namespace groups children, a leaf is a terminal action, and a hybrid can both
execute and have children. A typed slot identifies an argument position, its
kind, and whether it is required. A slot MAY validate its input and offer a
preview. Open-ended values are not permanent node IDs.

A resource slot draws candidates from a host index. Each candidate has a
stable, declared resource ID and a current label. Usage identifies a resource
by its slot ID and resource ID, not by the label or search text. The binding
specifies index refresh, matching, and identity through rename. A rename MAY
retain the ID or use a fact mapping the old ID to the new one. Mappings MUST
be unambiguous and acyclic. A rename is not an invocation. A binding MUST NOT
reassign a resource ID to a different resource under the same slot while
retained intent refers to that ID or a retained rename mapping uses it as
either endpoint. A new resource at a vacated label or path needs a distinct
ID while those facts remain.
Each resource candidate's ranking MUST use its own usage history under its
slot, and that history MUST survive its declared rename. The binding defines
how history combines with matching, context, and decay.

At commit, a filled resource slot MUST resolve to exactly one declared ID in
the current index, whether the value was typed or selected. The binding
specifies whether an unresolved or ambiguous value is refused or remains
open. Neither outcome commits or stores the text. This applies to text and
structured surfaces.

A provider of claimed semantic commands MUST declare safe, stable IDs for its
nodes. The binding identifies any commands or surfaces excluded from its claim;
an excluded command is not represented as a covered semantic command. A
claimed command MUST NOT silently opt out of recording. A native command on a
claimed surface is captured as native, even if no semantic provider owns it.

## 3. Committed intent and facts

A goal signal is an invocation committed by an explicit user gesture. At that
gesture, a semantic invocation commits if its grammar resolves the whole input
to an action, its required slots are filled, and each filled resource slot
resolves per §2.
Availability and ordinary slot value validation gate execution under §5.
A complete invocation still commits when unavailable or when a supplied
ordinary value fails validation. Native invocations use the host's commit
gesture and native grammar.

The surface MUST capture the intended command, context, project, time, and
origin at commit, before execution. It MUST record that intent no later than
the host becoming ready for another user command or normal termination,
whichever comes first; recording at commit satisfies this deadline. A pending
intent MUST be recorded before the next commit. The binding defines the host's
lifecycle and each surface's commit gesture.

A promotion is a shortcut into an existing command path and can leave input to
complete. Origin is `shortcut` when the user chooses a promotion and completes
the invocation through that choice; otherwise it is `direct`. An incomplete
promoted path retains shortcut origin while the user fills its slots or continues
within that promoted path. Leaving its semantic prefix clears the origin;
returning to that path manually does not restore it. A new explicit promotion
choice can set it again. If a host promotes native commands, the same origin
rule applies to them. Showing, previewing, or selecting an incomplete path is
not itself a committed invocation.

Nested actions and ordinary programmatic execution MUST NOT create additional
goal signals. A user replaying an owned command records the underlying command
and the surface that received the replay gesture. Failure, unavailability, or
a declined confirmation MUST NOT alter a committed signal. Abandoned or
incomplete input has not committed.

An intent event MUST retain facts only: commit time, committing surface,
independent origin, project, closed context identifiers, command kind (semantic
or native), argument presence, and a writer or session identity for replay.
Arguments are present when a native invocation has arguments or a semantic
invocation supplies a slot value or free-form input, including a structured
selection. Arguments already declared on capability steps are not invocation
arguments.

A semantic event MUST retain the node-ID path as it was at commit: root and
named nodes through the action, followed by filled slot IDs in declared order.
The final ID is the target; without filled slots the action is the target.
Slot positions form successive path entries even if declared as siblings. A
native event retains its command root. Each filled resource slot contributes a
mapping from its slot ID to its resolved resource ID; an absent optional slot
has no mapping.

The log MUST NOT persist ordinary argument or slot values, resource labels,
free-form query text, command bodies, provider or capability IDs, execution
outcomes, or latency as such. Text that is itself a resolved declared ID MAY be
stored in that ID's role. Writers MUST validate declared identifiers; readers
MUST validate record shape without the original provider installed. Malformed
records are skipped and storage failures reported. Reset MUST invalidate this
writer's unrecorded captures and remove only the selected stored history.
Uncommitted navigation MUST NOT add goal credit. With derivation inputs held
fixed, navigation and diagnostic friction MUST NOT affect ranking or promotions.

## 4. Derived state, time, and ranking

Derived state MUST be a deterministic function of retained intent and rename
facts, configuration, time, current session, active project, working context,
inventory, resource index snapshot, requested frontier, query, and complete
match results. The binding defines any effect of active project on ranking.
Cached results MUST reflect a change to any input on the next result. Replay
uses the ID path recorded at commit. A node keeps its own history across a move
or token rename. Its historical paths stay associated with their recorded
ancestors. Equal-time events from one writer MUST replay in recorded writer
order, including across log segments. The binding defines a deterministic
tie-break across writers.
Only current choices are offered.

A host MUST use one event horizon of 365 local calendar days and one
calendar-cutoff operation. The operation finds the same local wall time the
given number of calendar days earlier; the binding defines the timezone and
gap/fold handling. The same operation is used wherever a cutoff is needed.
An event at the horizon cutoff remains eligible; an older
event MUST NOT influence derived state, even if its physical record remains.
A backward clock movement MUST make still-existing eligible history visible.

Ranking MUST use committed history, working context, and decay over time. The
binding defines their effects, promotion eligibility, and any surface-specific
matching or presentation. Working context identifies where the user is working
independently of the commit surface. Surfaces MUST produce the same underlying
ranking when all derivation inputs above are equal, including the frontier,
inventory, index snapshot, and complete match results.

Each binding MUST provide reproducible witnesses showing history, context, and
decay changing an observable ranking or promotion result. The compared facts
MUST stay eligible under the horizon at both points in the decay witness. The
binding MUST also show a promotion produced from recorded history. A
resource-slot binding MUST show candidate order responding to history earned
in the slot being ranked under equal matching conditions. It MUST show
rename continuity and isolation from a new resource at the former label or
path. Witnesses specify the host's own outcomes, not common scores or thresholds.

## 5. Resolution and execution

Resolution MUST identify a command from its grammar independently of whether
its capability is available. Learning MUST NOT change grammar, ownership, or
availability. An owned command MUST consume its whole input through declared
nodes, slots, or an explicit free-form argument before execution; native
commands retain the host's parsing and validation rules.

A capability is an identified executable ability with one implementation and
safety policy. A host MAY offer flows. A flow is one committed command that
runs an ordered sequence of capability steps. Direct, promoted, and flow
invocations of a capability MUST use its implementation and safety policy.
Before each execution, including each flow step, the host MUST validate slots
and check current availability and safety.
An unavailable action MUST NOT execute. Destructive actions require explicit
confirmation by default. A declined confirmation MUST stop execution. A flow
MUST stop when a step has invalid input, is unavailable, is declined, or fails.
Ranking and promotions MUST NOT bypass these checks.

## 6. Input surfaces

A text surface has an editable line and cursor. Typing alone MUST NOT rewrite
it. Accepting a choice MUST replace exactly the token at the cursor and preserve
text and spacing outside that token; the choice MAY expand it into a path. A
text-surface handoff MUST preserve line and cursor. A structured handoff from a
text surface MUST preserve them on return, apart from an accepted choice's edit.
The binding defines tokenization, cursor units, and cursor placement after
acceptance.

A structured surface navigates choices without requiring a line or cursor.
Accepting a namespace or incomplete slot advances to its choices. A hybrid
exposes an explicit choice between advancing and dispatching. A terminal action
or completed slot dispatches only on commit; navigation and backtracking alone
record no goal signal. A user MUST be able to leave an optional slot empty while
completing later required slots. The user MAY execute text as typed or accept a
choice.

## 7. Implementation boundary checks

An implementation MUST run the applicable core cases and the following
[boundary checks](conformance/core/README.md#host-boundary-checks) through
its actual surfaces, execution, storage, and ranking. Checks apply where
the binding supports the feature.

- **Capture and commitment.** Verify commit-time facts and the recording
  deadline on each claimed surface. Exercise unowned native capture, user
  replay, incomplete promotions, nested execution, and abandoned input.
  Attempt commit with an empty required ordinary slot and again after filling it.
- **Resource identity.** Resolve typed and picked inputs against the index at
  commit. Check two selections in one event, the per-slot usage witness,
  continuity and isolation on rename, and rejection or safe skipping of
  ambiguous and cyclic mappings.
- **Resolution and execution.** Check grammar independently of availability
  and learning, and refuse unconsumed input. Check that direct and promoted
  submissions retain intent through execution refusals and that a committed
  failure retains exactly one intent. Compare implementation and safety policy
  across paths. In flows, check stopping on invalid input, failure, and
  separately on a later step becoming unavailable or destructive.
- **Storage and replay.** Check the actual log, deterministic replay, equal-time
  ordering within and across writers, node moves, the calendar horizon and
  backward clock behavior, writer validation, malformed entries, reads without
  the provider, storage failure reporting, and both pending and selective reset.
- **Ranking and cache freshness.** Run the binding's witnesses. Compare ranking
  and promotions before and after navigation and diagnostic activity. Compare
  rankings across all surfaces with equivalent requests, including surfaces
  of the same kind. Change each applicable §4 input across consecutive
  requests, comparing the next result with a fresh one.
- **Text input.** Check line and cursor across handoffs, and verify that a live
  suggestion leaves the line as typed until acceptance.
