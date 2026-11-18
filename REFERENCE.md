# Reference algorithm 0.4.0

This algorithm is **informative**. An implementation can conform to [SPEC.md](SPEC.md)
without using these weights, ranking windows, eligibility rules, or tie-breakers. A
binding states which parts it follows. The [reference cases](conformance/reference/README.md)
exercise this algorithm with a synthetic binding. They do not replace core
cases or implementation-owned boundary checks.

The reference was extracted from cmdux `842338bcd4dca02d66b9a6fc03e1f7792edfa3d9`.
The documented projections and gaps mean that passing its adapter does not
establish native cmdux conformance. Defaults below are configurable except for
the 365-day horizon required by the core.

## Facts and time

For equal timestamps, replay orders ascending writer ID in UTF-8 byte order,
then ascending logical writer position. Recency is the order of credited events
in that replay. The horizon is 365 local calendar days. Its cutoff
for `N` days is the same local wall time `N` dates earlier. A clock gap moves
forward by its size; a repeated time uses the later occurrence. The cutoff is
inclusive. The same operation applies to flow lookback.

Each project advances its active-day counter when a new local day has activity;
calendar days without activity do not advance it. With window `W = 21`, a
bucket `a` active days old has weight `W - a` for `0 <= a < W`, otherwise zero.
Durable score is the sum of credits multiplied by bucket weight. Freshness also
uses active days. Current-writer session heat uses the same identities and
contexts without day weights; it is derived, reset for a new session, and can
be disabled.

## Credits and composition

A direct semantic invocation gives its target 100 credits and its ancestors 35,
12, and 4 at distances one, two, and three; further ancestors get zero. A native
or free-form invocation without a declared path credits its root. A direct
invocation also gives each recorded tree edge and its full path 100 credits.
This includes the implicit root-to-command edge. Derive node, edge, and path
evidence globally and for each exact and facet context. Shortcut use records
freshness but adds no node, edge, or path score credit, including for native
shortcuts. A per-root vector can replace the default node credits.
Each filled resource selection independently gives its `(slot ID, resource ID)`
100 credits, including through a shortcut, with the same context, project,
active-day, and session rules and no propagation to other resources. A rename
fact gives no credit or active day.

For a metric in one project, let `G` be global score, `E` exact-context score,
and `F` the greatest matching-facet score. Compose `G + 6E + 2F`; facets are
alternatives, not a sum. A context-specific transition uses `G = 0`, and a
relaxed transition uses only `G`. Apply the same composition to session heat.

Mix each durable component as `4 × current project + 1 × strongest other
project`; mix session components independently as `6 × current project + 1 ×
strongest other project`. Compose within each project before selecting the
strongest other project. For structural ranking, choose it separately for the
context-specific transition, relaxed transition, and node activation. For
promotion, choose it separately for context-specific path, relaxed path, and
node activation; for resources, choose it for resource activation. Durable and
session maxima are independent. Add the mixed durable and session components.
Disabling cross-project influence retains the current-project weights.

For recency, use the latest relevant credited event across all enabled projects,
including a project that did not supply the strongest score. For each project,
use the global and exact metrics and the selected greatest-scoring facet; a
facet-score tie uses its latest event. Combine the relevant transition and
node recencies by taking their maximum. With cross-project influence disabled,
only the current project's events participate.

## Ranking and promotion

A structural choice with mixed context-specific transition `T`, relaxed
transition `R`, and node activation `N` has score `8T + 3R + 2N`. Within each
ranked matching group, positive scores precede unscored choices. Sort scored
choices by descending score, descending recency, then ascending structural
position; unscored choices retain their original order. Ordinary-slot suggestions
share their slot-position score and retain provider order on a tie. A resource
candidate has score `N + M`, where `M` is the host's nonnegative match quality;
sort by descending score, descending resource-credit recency, then ascending
index position. The reference does not disable ranking for a large frontier.

A promotion is a shortcut to a full semantic path, shown separately from root
children. Render a path with slots only to its first slot; slot values are not
part of its identity. The path must still be valid and executable or expandable,
and have recorded depth at least two. By default it qualifies if it has two
direct dispatches in the last five active days and a positive score, or a
shortcut dispatch in that window. Counts use the strongest single relevant
project. A shortcut can keep a path eligible after its original direct history
expires. Filter by match, validity, and eligibility before taking at most three.

In each project, context-specific path score is the greatest exact or matching
facet score; relaxed path score is global. Mix each as above. Promotion score is
`6 × context-specific path + 2 × relaxed path + mixed node activation`. Sort by
descending score, descending direct path-credit recency, then ascending rendered
path and node ID. Shortcut use does not update direct-credit recency.

## Flow proposals

A host may offer proposals of complete capability steps. Group occurrences by
project, exact context, and the full ordered steps including declared arguments.
The proposal ID derives from that whole group key and is unique in one query.
Use invocation facts only: a rename or other non-invocation fact neither breaks
adjacency nor counts against the history limit. Intervening invocations remain
in the stream. A different writer, project, or (by default) exact context breaks
an occurrence. A native invocation, a semantic invocation with arguments present,
an existing flow, or a missing, incomplete, or unresolvable capability also
breaks it. The binding identifies existing flows separately from ordinary
multi-step actions.

Consider at most the latest 512 invocations at or after the calendar cutoff for
`max(window, freshness) + 30` days. Start at each eligible event and extend
through consecutive eligible events, with at most 180 seconds between them,
until the combined steps would exceed four. Each prefix with two to four steps
is an occurrence; overlapping prefixes count independently. Append an event's
complete steps together, never split: an event with two to four steps can itself
be an occurrence. Require support of two and a score of 180. Each occurrence
adds `20 × step count + 40 × project weight`. Sort all qualifying proposals by
descending score, support, and recency, then ascending proposal ID; return at
most six. Proposal lookback does not change the event horizon. Proposals do not
affect live ranking until explicitly represented and invoked as commands.

## Open reference items

- **R5-A2/B1 — promotion path identity:** distinct recorded paths can end at
  the same node and render alike. The current reference fixture result reports
  only the final node ID; it cannot distinguish those paths or test a final
  tie-break between them. Define a full-path result and tie-break, then migrate
  the reference adapter and cases together.
- **R5-A5 — token separators:** the synthetic binding permits `/` within a
  token, but the adapter's token-path projection uses `/` as an internal
  separator. Encode token boundaries reversibly before claiming coverage for
  such promotions.
