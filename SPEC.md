# Command Intelligence Specification 0.1.0

## 1. Conformance and inputs

The terms **MUST**, **MUST NOT**, and **SHOULD** state requirements and
recommendations; **MAY** denotes an option. An implementation MUST declare
this specification version and document its host bindings as described in
[BINDINGS.md](BINDINGS.md). A conformance claim MUST pass every applicable
[shared case](conformance/README.md) and the boundary checks in §11. String
sort keys compare ascending lexicographic UTF-8 bytes unless a binding declares
another deterministic total order.

Given the same retained facts, current session, configuration, command
inventory, candidate-index snapshot, query, match results, context, and time,
derived state and ordering MUST be deterministic. An implementation MAY cache
derived state, but MUST recompute affected results when any input changes. In
particular, an event crossing the horizon, a backward clock movement, a
configuration change, a log disappearing, or a changed query, index or match
result MUST be reflected in the next result. A backward clock movement rereads
still-existing history when needed.

## 2. Command model

The command vocabulary is one semantic tree, which MAY be represented as a
forest under an implicit root. Each node MUST have a stable host-declared ID;
the binding defines its formation and lifetime. IDs need not equal tokens,
labels, or aliases. A namespace groups children, a leaf is a terminal action,
and a hybrid is executable and has children. A typed
slot identifies an argument position, its kind, and whether it is required; it
MAY provide validation and a preview. Open-ended values are not permanent
children or node IDs.

A resource slot draws candidates from a host index. Each candidate has a
host-declared stable resource ID, a current label, and a query match quality.
The resource ID and the slot ID together identify its usage; the label and the
text used to find it do not. The binding defines index refresh and how identity
survives a rename: either the host retains the ID or records an old-to-new ID
rename fact and resolves earlier usage to the new ID. A rename fact contributes
no usage credit or active day. It identifies the slot, old and new resource IDs,
time, writer, and log position; replay resolves earlier usage through the rename.
The binding MUST prevent ambiguous or cyclic mappings. Readers need not have
the original index installed to replay the facts; only current candidates are
offered.

At commit, each filled resource slot MUST resolve to exactly one ID declared by
its index, whether the user selected a candidate or typed a value. The binding
defines matching and whether unresolved or ambiguous input is refused or kept
open. Neither case commits or stores the input text.

The inventory and ownership MUST come from the host's live declarations. A
node can refer to a capability: an identified executable ability with its own
implementation, availability, safety, and optional preview. Multiple nodes can
refer to one capability. A direct invocation and a flow invoking that capability
MUST use the same implementation and safety policy.

Resolution MUST identify a command from its grammar independently of whether
its capability is currently available. Availability and executability are
checked against the live host when presenting or executing the resolved action;
learning MUST NOT change the grammar, ownership, or availability. An owned
command MUST consume its whole input through declared nodes, slots, or an
explicit free-form argument before execution. Native commands retain their
host's parsing and validation rules.

## 3. Intent and events

A goal signal is a fully specified invocation committed on an explicit user
surface. The surface MUST capture the intended command, working context, project,
commit time, and shortcut origin at commit, before execution. It MUST record the
intent no later than when the host becomes ready for another user command or
before normal termination, whichever comes first; recording at commit satisfies
this deadline. An earlier pending intent MUST be recorded before the next commit
even if readiness is not observable. The binding defines the host's lifecycle.
Nested actions and ordinary programmatic execution MUST NOT create additional
signals. Replaying an owned command records that command. Failure, unavailability after commitment, or a
declined confirmation MUST NOT change a committed signal. An abandoned path or
cancelled, incomplete slot has not committed an invocation.

An intent event MUST contain facts only: a commit time, committing surface, an
independent `origin` of `direct` or `shortcut`, project identifier, closed
context identifiers, whether arguments were present, and whether the command is
semantic or native. Arguments are present when a native invocation has
arguments, or a semantic invocation supplies a slot value or free-form input,
including a value selected through a structured surface. Arguments already
declared on capability steps are not invocation arguments.

A semantic event MUST retain the node-ID path as it was at commit. It starts at
the root and follows the named nodes to the action, then appends each filled slot
ID in declared order. The last ID is the recorded target; with no filled slots,
the action is the target. Thus a terminal slot is the target, and multiple slot
positions form successive path entries even if the host declares them as
siblings. A native event retains its command root as its target. For each filled
resource slot, the event MUST retain a mapping from that slot's ID to its
resolved resource ID. Absent optional slots have no entry. A writer or session
identifier MUST be recoverable for replay. The log MUST NOT contain ordinary
argument or slot values, resource labels, free-form query text, command bodies, provider or
capability IDs, execution outcomes, or latency. Writers MUST validate declared
identifiers; readers MUST validate record shape without requiring the original
provider to be installed.
Malformed records are skipped. Storage failures MUST be reported. Reset MUST
invalidate this writer's unrecorded captures and remove the selected channel's
history; later commits remain recordable.

Intermediate selections, previews, help, and discovery MUST NOT add goal credit.
Friction MAY be recorded separately for diagnosis; it MUST NOT affect live
ranking. Its kinds and any diagnostic weights are host-defined.

## 4. Context and scopes

The host MUST identify the project and the working context behind a command
surface, not the command surface itself. The semantic parent is part of a tree
transition. Context is a typed vector of closed identifiers; the host binding
MUST define its vocabulary, an exact key, and a bounded, deduplicated set of
facet keys.

Learning has a project scope and, optionally, a cross-project view derived from
other projects. Context-specific and global evidence coexist; context is a
weighted contribution, not an absolute priority. All surfaces presenting the
same frontier in the same context MUST use the same underlying ranking.

## 5. Credits and transitions

A direct semantic dispatch gives its target node 100 credits by default. Its
ancestors receive 35, 12, and 4 credits at distances one, two, and three;
further ancestors receive zero. The root receives only its share, unless it is
the direct target. A configured per-root vector MAY replace these absolute
credit values. A native command or free-form invocation without a declared path
credits its root as the direct target. Credits are nonnegative integers.

For each direct dispatch, every tree edge on its recorded path, including the
implicit root-to-command edge, receives the direct credit, as does the full
path. Node, edge, and path evidence is derived globally and for the event's exact and facet
contexts. A shortcut dispatch records a shortcut use for freshness but adds no
node, tree-edge, or path score credit. Execution counts and credit totals are
distinct. Workflow sequences are derived from ordered events; they are not
tree-edge credits. Replay MUST NOT reconstruct a recorded path from the current
inventory: a removed or moved node retains its recorded ancestors and edges.
A stable node's own credit remains associated with its ID after a move or token
rename; only current choices are offered.

Each committed resource selection gives the slot root's direct credit, 100 by
default, to its `(slot ID, resource ID)` independently of the command path.
This includes a selection reached through a shortcut: it does not give the
shortcut path score credit. Resource credits use the same project, context,
active-day, and session rules as node activation, without propagation to other
resources.

## 6. Time and session

Replay MUST order events by ascending time, then ascending writer ID, then
ascending position within that writer's log. Recency is the order of relevant
credited events in that replay, not timestamp alone. The cutoff for `N` local
calendar days is the same local wall time `N` dates earlier, using the
timezone's offset on that date. If the target time falls in a clock gap, move it
forward by the gap; if it is repeated, choose the later occurrence. An event at
the cutoff remains; an older one is excluded. Apply this operation with
`N = 365` for the event horizon. Retained events may physically remain in a live
writer's log until safe to remove, but MUST NOT influence derived results after
the cutoff.

Each project has active-day buckets in the host's local timezone. A project
advances to the next active day only when it records activity on a new local
calendar day. An inactive calendar gap does not itself age active-day scores,
although it can cross the retention horizon. With default window `W = 21`, the
weight of a bucket `a` active days old is `W - a` when `0 <= a < W`, otherwise
zero. A metric's durable score is the sum of bucket credits times their weights.
Freshness uses active days as well.

Session heat is derived from retained events of the current writer session,
using the same identities and context slices, without active-day weighting. It
MUST NOT be stored as a separate source of truth and MUST reset on a new session
or reset. Session heat MAY be disabled. It is included in the calculations below.

## 7. Score composition and ranking

For a metric in one project, let `G` be its global score, `E` its exact-context
score, and `F` the greatest score among matching facets. The default contextual
score is `G + 6E + 2F`. A tree transition's context-specific component uses
`G = 0`; its relaxed component uses only `G`. Apply the same composition to
session heat. Facets are alternatives: do not sum their scores.

Mix each durable component as `4 × current project + 1 × strongest other
project`. Mix session components independently as `6 × current project + 1 ×
strongest other project`. Add the durable and session components. Cross-project
influence MAY be disabled; when disabled the current-project weights still
apply. Compose `G`, `E`, and `F` within each project before choosing a strongest
other project. For structural ranking, choose it separately for the composed
context-specific transition, the relaxed global transition, and the composed
node activation. For promotion, choose it separately for the context-specific
path, relaxed global path, and composed node activation; for a resource candidate,
choose it for the composed resource activation. Choose durable and session
maxima independently. Evidence from multiple other projects is not summed.
Weights are configurable.

For a structural choice, with mixed context-specific tree transition `T`,
relaxed tree transition `R`, and node activation `N`, the default score is
`8T + 3R + 2N`. `N` includes direct and propagated credit. The binding defines
which choices match a query and the order of any matching groups. Within each
ranked group, positive-score choices precede unscored choices. Order scored
choices by descending score, then descending recency, then ascending original
structural position. Unscored choices keep their original order. Ranking MUST NOT
be disabled for a large frontier. Recency breaks a tie; it is not an additive score.

Ordinary-slot suggestions use the score of the slot position, not the suggested
value. Suggestions tied at that position retain the provider's order.

For each current resource-slot candidate matching the query, compute `N` from
its own credits as node activation above, scoped to its slot. The host supplies
a nonnegative integer match quality `M` for the query, with larger values meaning
a better match; its binding defines the scale. Rank candidates by descending
`N + M`, then descending resource credit recency, then ascending index position.
Candidates without usage have `N = 0`.

## 8. Promotion

A promotion is a shortcut to a full semantic path, presented separately from
structural children at the root frontier. A path with slots is rendered only to
the first slot; its identity may include slot positions, never slot values.
Selecting an incomplete promoted path expands to the next valid state; an
executable one can be dispatched. Expansion or display alone adds no goal signal.

The default eligibility rules are: the path is still valid and executable or
expandable; its recorded depth, counting the command root, is at least two; and
either at least two direct dispatches are within the last five active days and
its promotion score is positive, or at least one shortcut dispatch is within
that freshness window. Counts are taken from the strongest single relevant
project, not summed across projects. A recent shortcut can keep a path eligible
after its direct credits or original events expire. Check the query match,
validity, and eligibility before applying the default limit of three.

For a path in each project, its context-specific path score is the greatest of
the exact and matching facet scores; its relaxed path score is the global path
score. Mix each across projects and session as in section 7. Promotion score is
`6 × context-specific path + 2 × relaxed path + mixed node activation`. Sort
eligible promotions by descending score, then descending recency of retained
direct path-credit events, then ascending rendered path and ascending node ID.
Shortcut uses do not update this recency, even when they keep the path eligible.
These limits and weights are configurable. Demotion follows the freshness gate
and competition; it does not require negative credits.

## 9. Flows

A flow is an ordered list of capability steps, including declared arguments,
rather than an opaque command string. Its safety is the highest safety of its
steps. Check availability and safety before each applicable execution; execute
in order and stop when a step fails or is unavailable. A flow and its direct
commands share capability implementations.

A host MAY provide flow proposals. If it does, it MUST group occurrences by
project, the first event's exact context, and the ordered complete capability
steps, including declared arguments. Different arguments or groups MUST NOT be
combined. It MUST resolve steps from the live inventory and MUST NOT infer
argument values from the event log. It MUST use consecutive eligible semantic
events from one writer and project, by default in the same exact context, with
at most 180 seconds between events. A native event, a semantic event with
arguments present, or an incomplete, missing, or unresolvable capability breaks
a sequence, as does an existing flow. It considers at most the latest 512 events
at or after the §6 cutoff for `max(window, freshness) + 30` calendar days. Start
at each eligible event and extend through consecutive eligible events until the
combined steps would exceed four. Each prefix containing two to four steps is an
occurrence; overlapping prefixes count independently. An event's complete steps
are appended together, never split: an event that supplies two to four steps can
itself be an occurrence. A group requires support of two and a score of 180. Each occurrence adds
`20 × step count + 40 × project weight`,
with the section 7 durable project weights. It sorts by descending score,
descending support, descending recency, then ascending proposal ID, and returns
at most six after sorting all qualifying groups. The host MUST derive each proposal ID from the full group key:
project, exact context, and complete ordered steps. IDs MUST be distinct within
one query.
These proposal settings are configurable; the proposal lookback does not alter
the 365-day event horizon. Workflow proposals do not affect live ranking until
explicitly represented and invoked as commands.

## 10. Safety and input

A text surface has an editable line and cursor. Typing alone MUST NOT rewrite
the line. Accepting a choice MUST replace exactly the token at the cursor and
preserve text and spacing outside it; the choice may expand that token into a
longer path. Only one component owns the edit. A handoff between text surfaces
MUST preserve the line and cursor. A handoff through a structured surface MUST
also preserve them on return, except for an accepted choice's edit. The binding
defines tokenization and cursor units.

A structured surface navigates choices without requiring a line or cursor.
Accepting a namespace or incomplete slot advances to its choices. A hybrid
exposes an explicit choice between advancing and dispatching. A terminal action
or completed slot is dispatched only on commit; navigation or backtracking
alone records no goal signal.

The user may execute the text as typed, or explicitly accept a choice. Slots
MUST be validated before an owned action executes. An unavailable action MUST
NOT execute; safety policy MAY require confirmation and show an outcome preview.
A declined confirmation stops execution. The default safety levels are safe,
reversible, and destructive, in increasing order; destructive actions require
confirmation by default. Learning and promotions MUST NOT bypass these checks.

## 11. Implementation boundary checks

An implementation MUST test capture through every claimed commit surface,
including its surface, origin, context, and selected identity, and verify that
nested actions do not duplicate it and abandoned input records none. It MUST
test persistence and replay through its actual log, including command kind,
argument presence, resource IDs for any resource slot, and the exclusion of
ordinary slot values. Every log's replay checks MUST cover logical writer order
and backward clock movement. A segmented
log MUST also check writer positions across segments. Where a handoff carries
text, the implementation MUST check preservation of the line and cursor.
It MUST also prime cached ranking results, change the query, candidate-index
snapshot, and match results, and verify that the next result reflects each
change.
Synthetic scoring cases do not establish these boundary guarantees.
