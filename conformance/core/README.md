# Core conformance cases

[`cases.json`](cases.json) and [`schema.json`](schema.json) describe portable
checks of [SPEC.md](../../SPEC.md). They deliberately prescribe no scores,
weights, promotion thresholds, or exact order for unlike inputs. Every
implementation runs each case whose `requires` capabilities it supports, using
its own algorithm and the synthetic inventory below. Passing them does not
replace the implementation-owned boundary checks in the specification.

`text_surface` and `structured_surface` are independent capabilities.
`resource_slots`, `native_promotions`, and `flows` mean the host offers those
features. A case applies only when all its listed capabilities are present.
In particular, typed-resource cases require a text surface and resource slots,
not a structured surface. Native promotions and flows are optional, but the
cases for either apply when the feature exists.

## Synthetic binding

Each case starts with empty history and the declared time, project, context,
writer, node inventory, and resource index. Install the fixture's safe and
destructive actions, ordered slots, resources and labels as a test provider.
The tokenizer uses unescaped whitespace and `|` as separators, `\` escapes
the next character, and cursor offsets count UTF-8 bytes. An `edit` case supplies
its accepted spelling directly; it need not be a member of the inventory.
Run the host's usual capture, validation, execution, log, and replay boundaries,
using test actions to observe calls. Reset history, execution observations, and
interaction state before each case.

A host's actual horizon, timezone, gap/fold policy, context model, decay, and
promotion algorithm remain its own binding choices. A `choose` through
`promotion` presents the stated path as a test promotion; it does not require
that this empty-history fixture makes the path eligible by itself.

## Interaction cases

Perform `actions` in order. `choose` opens the given path, either directly or
through the offered promotion. `change_path` changes the selected semantic path
without committing. `pick_resource` selects an index ID; `type_resource` enters
the decoded text and attempts resolution at commit. `ordinary_value` supplies
an ordinary slot value and `native_arguments` supplies native argument text.
`cancel` abandons the interaction. `internal` executes the path programmatically,
without making a separate explicit user commit.

`commit` uses the named surface and is the host's normal commit gesture.
`available: false` means the action becomes unavailable after commitment and
before execution. `confirmation: decline` declines its destructive confirmation;
the default is available and confirmed. A flow's `unavailable_step` or
`declined_step` becomes unavailable or has its confirmation declined before that
step starts. A `failed_step` starts and then fails. `executions` lists actions
or flow steps that actually started, in order; it includes a failed step. The
flow itself is the committed command, while its internal steps are not separate
user commits.

Compare `expected.events` to the recorded user intents in order, projecting
exactly the fields shown. Also check the stored time, project, context and
writer against the fixture, and check the full stored records for the facts-only
rules. An `expected.forbidden_text` string must occur nowhere in retained
records, including diagnostic records. `status`, when present, lists acceptable
end states; open and refused are both allowed for unresolved resource text. No
event or execution is allowed when the corresponding expected list is empty.

## Other cases

For an `edit`, apply the operation at the byte cursor and compare the full line
and cursor. A `type` operation inserts the supplied text without rewriting the
surrounding input; an `accept` operation replaces the token under the cursor.

For `cutoff`, independently compute the cutoff at `now` using the host's
**declared** horizon and calendar policy. Retain two facts: one exactly at the
cutoff and one at the immediately preceding representable timestamp. Ask the
host for eligibility at `now`, then at `earlier` with both facts still present.
Compare the three booleans. This checks inclusion and backward-clock behavior
without imposing a timezone, duration, or ambiguity policy on the host. The
host's boundary tests also exercise its single calendar operation wherever it
uses a cutoff.

For `consistency`, install the projected `history` as actual facts with the
fixture's time, context and writer. Obtain the complete underlying ranking of
`candidates` twice with identical inputs. For `surfaces`, query both named
surface types with the same frontier and match results; for `replay`, rebuild
from the same retained history between queries. The two ordered lists must be
equal and contain exactly the declared candidates. The order of the candidates
in `expected` is a set, not a prescribed ranking.
