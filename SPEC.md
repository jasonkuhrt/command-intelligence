# Command Intelligence Specification 0.3.0

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
retain the ID or use a fact mapping the old ID to the new one; mappings MUST
be unambiguous and acyclic. A rename is not an invocation.
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
Ordinary slot value validation gates execution under §5. A supplied ordinary
value that fails this validation still leaves one committed intent. Native
invocations use the host's commit gesture and native grammar.

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
goal signals. Replaying an owned command records that command. Failure,
unavailability after commitment, or a declined confirmation MUST NOT alter a
committed signal. Abandoned or incomplete input has not committed.

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
facts, configuration, time, current session, inventory, resource index snapshot,
requested frontier, query, match results, and working context. Cached results
MUST reflect a change to any input on the next result. Replay uses the ID path
recorded at commit. A node keeps its own history across a move or token rename,
and its historical paths stay associated with their recorded ancestors. Equal-time
events from one writer MUST replay in recorded writer order, including across
log segments; the binding defines a deterministic tie-break across writers.
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
resource-slot binding MUST show contrasting candidate histories
changing their relative order under equal matching conditions, and show rename
continuity. Witnesses specify the host's own outcomes, not common scores or
thresholds.

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

An implementation MUST run the applicable core cases and the following checks
against its actual boundaries. A check for an unsupported feature does not apply.

- Capture on each claimed commit surface, including an action that changes the
  working context during execution. Check the pre-execution facts at the
  recording deadline, including surface, origin, command kind, argument
  presence, applicable resource IDs, and exclusion of ordinary values.
- Direct unowned native capture on every claimed surface accepting native
  commands. Check the native root, argument presence, and committing surface.
- A committed standalone action that fails still records exactly one intent.
- An incomplete promotion through slot completion and leaving its prefix.
- Nested execution and abandoned input add no goal signal.
- Typed resource resolution, including resolved, unresolved, and ambiguous input,
  on each text or structured surface that supports typed resource input.
- A picked resource removed from the index before commit yields no intent or
  execution.
- Two resource selections in one event, each retained under its own slot ID.
- Resource history survives each declared kind of rename.
- A rename adds no invocation or invocation credit.
- Ambiguous and cyclic rename mappings are rejected or safely skipped without
  conflating resources or disturbing unrelated valid history.
- The binding's contrasting-history witness.
- The binding's context witness.
- The binding's decay witness.
- The binding's promotion witness, produced from real recorded history.
- The binding's per-resource history and rename-continuity witnesses, if supported.
- Resolution with availability already on and off yields the same command.
- Unconsumed input cannot dispatch.
- Changing only learned history leaves grammar, ownership, and availability
  unchanged, with host state held fixed.
- A supplied invalid ordinary slot value commits intent and never reaches the
  handler. The log excludes the value.
- Navigation and diagnostic activity, where supported, leave ranking and
  promotions unchanged with derivation inputs held fixed.
- An action unavailable after commit does not run, direct or promoted.
- Declined destructive confirmation stops execution, direct or promoted.
- One instrumented capability's implementation and safety policy through direct
  and promoted execution, and through a supported flow shape if offered.
- Each flow step checks current availability and safety, obtains required
  confirmation, and stops on failure, unavailability, or decline.
- A flow step with an invalid slot value never starts and the flow stops. Use a
  second step after a successful first step when the binding supports it.
- Persistence and replay through the actual log.
- The 365-day horizon and backward-clock behavior, with a cutoff that crosses a
  UTC offset change if the binding's timezone permits one.
- Deterministic replay and results for the same inputs.
- A deferred capture recorded by the first of readiness for another command or
  normal termination, and before a subsequent commit; inspect at that deadline.
- Reset with a pending capture, ensuring the old capture cannot reappear and a
  subsequent commit can be recorded.
- Selective reset removes seeded stored history and preserves other stored history.
- The writer rejects a well-formed but undeclared ID before storing the record.
- Malformed records are skipped.
- Valid records are read without the original provider installed.
- Storage failures are reported.
- A moved stable node retains its history and its recorded historical edges.
- Equal-time events retain their writer order, including across log segments.
- Consecutive requests after a change to retained facts.
- Consecutive requests after a change to configuration.
- Consecutive requests after a change to the current session.
- Consecutive requests after a change to the command inventory.
- Consecutive requests after a change to time.
- Consecutive requests after a change to working context.
- Consecutive requests after a change to the frontier.
- Consecutive requests after a change to the query.
- Consecutive requests after a change to the resource index, where supported.
- Consecutive requests after a change to match results.
- Cross-surface ranking under §4's equality condition.
- Line and cursor preservation across text handoffs.

For each consecutive-request check, compare with a fresh result for the changed
input. Choose an observable change when the binding says it affects results;
otherwise check the declared invariant. Prime the cache first if one exists.
When inventory or index entries are removed, require their commands, promotion
paths, or resource choices to be absent from the next result. Synthetic cases
do not replace these checks.
