# Command Intelligence Specification 0.1.0

## 1. Conformance and inputs

The terms **MUST**, **MUST NOT**, and **SHOULD** state requirements and
recommendations; **MAY** denotes an option. An implementation MUST declare
this specification version and document its host bindings as described in
[BINDINGS.md](BINDINGS.md).

Given the same retained facts, current session, configuration, command
inventory, context, and time, derived state and ordering MUST be deterministic.
An implementation MAY cache derived state, but MUST rebuild it when those inputs
change. In particular, an event crossing the horizon, a backward clock movement,
a configuration change, or a log disappearing MUST be reflected in the next
result. A backward clock movement rereads still-existing history when needed.

## 2. Command model

The command vocabulary is one semantic tree, which MAY be represented as a
forest under an implicit root. Each node MUST have a stable semantic identity;
aliases and labels MUST NOT become identity. A namespace groups children, a
leaf is a terminal action, and a hybrid is executable and has children. A typed
slot identifies an argument position, its kind, and whether it is required; it
MAY provide validation and a preview. Open-ended values are not permanent
children or node IDs.

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
intent when the surface returns to input or on normal exit; an earlier pending
commit is recorded before the next commit. Nested actions and ordinary
programmatic execution MUST NOT create additional signals. Replaying an owned
command records that command. Failure, unavailability after commitment, or a
declined confirmation MUST NOT change a committed signal. An abandoned path or
cancelled, incomplete slot has not committed an invocation.

An event MUST contain facts only: a commit time, committing surface, project
identifier, closed context identifiers, whether arguments were present, and a
semantic node path or native command root. A writer or session identifier MUST
be recoverable for replay. The log MUST NOT contain argument or slot values,
free-form query text, command bodies, provider or capability IDs, execution
outcomes, or latency. Writers MUST validate declared identifiers; readers MUST
validate record shape without requiring the original provider to be installed.
Malformed records are skipped. Storage failures MUST be reported. Reset MUST
invalidate this writer's unrecorded captures and remove the selected channel's
history; later commits remain recordable.

Intermediate selections, previews, help, and discovery MUST NOT add goal credit.
Friction MAY be recorded separately for diagnosis; it MUST NOT affect live
ranking. Its kinds and any diagnostic weights are host-defined.

## 4. Context and scopes

The host MUST identify the project and the working context behind a command
surface, not the command surface itself. The semantic parent is part of a tree
transition; resource kind and working-surface class are context facets. Context
is a typed vector of closed identifiers. The host binding MUST define an exact
key and a bounded, deduplicated set of facet keys.

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

For each direct dispatch, every tree edge on the path, including implicit
root-to-command, receives the direct credit, as does the full path. Node, edge,
and path evidence is derived globally and for the event's exact and facet
contexts. A shortcut dispatch records a shortcut use for freshness but adds no
node, tree-edge, or path score credit. Execution counts and credit totals are
distinct. Workflow sequences are derived from ordered events; they are not
tree-edge credits.

## 6. Time and session

Replay MUST order events by commit time, then writer file or equivalent stable
writer order, then position within that writer. Events older than **365 local
calendar days** at the query time MUST be ignored; an event exactly on the
cutoff remains. Retained events may physically remain in a live writer's log
until safe to remove, but MUST NOT influence derived results after the cutoff.

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
apply. The strongest other project is selected separately for each component;
evidence from multiple other projects is not summed. Weights are configurable.

For a structural choice, with mixed context-specific tree transition `T`,
relaxed tree transition `R`, and node activation `N`, the default score is
`8T + 3R + 2N`. `N` includes direct and propagated credit. Positive-score
choices precede unscored choices. Order scored choices by descending score,
then descending recency, then their original structural position. Unscored
choices keep their original order. Ranking MUST NOT be disabled for a large
frontier. In a typed root search, reorder only the leading block of root names
matching the typed prefix; subsequent matches keep their original order. Recency
breaks a tie; it is not an additive score.

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
after its direct credits or original events expire. Check the current prefix,
validity, and eligibility before applying the default limit of three.

For a path in each project, its context-specific path score is the greatest of
the exact and matching facet scores; its relaxed path score is the global path
score. Mix each across projects and session as in section 7. Promotion score is
`6 × context-specific path + 2 × relaxed path + mixed node activation`. Sort
eligible promotions by descending score, then descending recency, then rendered
path. These limits and weights are configurable. Demotion follows the freshness
gate and competition; it does not require negative credits.

## 9. Flows

A flow is an ordered list of capability steps, including declared arguments,
rather than an opaque command string. Its safety is the highest safety of its
steps. Check availability and safety before each applicable execution; execute
in order and stop when a step fails or is unavailable. A flow and its direct
commands share capability implementations.

A proposal, if provided, MUST compare complete capability steps from the live
inventory, including declared arguments. It MUST NOT infer argument values from
the event log. The reference proposal algorithm uses consecutive eligible
semantic events from one writer and project, by default in the same exact
context, with at most 180 seconds between events. A native, incomplete, missing,
or unresolvable capability breaks a sequence, as does an existing flow. It
considers at most the latest 512 events within `max(window, freshness) + 30`
calendar days, combines two to four steps, and requires support of two and a
score of 180. Each occurrence adds
`20 × step count + 40 × project weight`, with the section 7 durable project
weights. It sorts by score, support, recency, then ID, and returns at most six.
These proposal settings are configurable; the proposal lookback does not alter
the 365-day event horizon. Workflow proposals do not affect live ranking until
explicitly represented and invoked as commands.

## 10. Safety and input

Typing alone MUST NOT rewrite input. An accepted choice MUST replace exactly the
token at the cursor, preserving text and spacing outside that token; the choice
may expand that token into a longer semantic path. Only one component owns the
edit on a given surface. Cursor and line MUST survive a handoff between surfaces.
A host binding defines token boundaries and cursor units.

The user may execute the text as typed, or explicitly accept a choice. Slots
MUST be validated before an owned action executes. An unavailable action MUST
NOT execute; safety policy MAY require confirmation and show an outcome preview.
A declined confirmation stops execution. The default safety levels are safe,
reversible, and destructive, in increasing order; destructive actions require
confirmation by default. Learning and promotions MUST NOT bypass these checks.
