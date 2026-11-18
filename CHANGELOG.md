# Changelog

## 0.2.0

- Restore the single 365-day core horizon, require per-resource learning and
  binding-specific behavioral witnesses, and strengthen the portable cases and
  host boundary checks for navigation, execution, replay, and cache inputs.
- New cmdux gaps checked at `ac2b52d`: the structured picker cannot advance a
  hybrid without dispatch; path-derived node IDs change on a move or token
  rename, so history does not follow the same node; flow safety is checked as
  a group before execution and is not rechecked for each step. A safe test
  capability changed the next step to destructive during a flow and that step
  ran without the configured destructive confirmation.
- cmdux has no indexed resource slots. Native core witnesses and boundary
  checks remain to be supplied and run before a conformance claim.

## 0.1.0

- Define the normative semantic command model, committed intent, privacy,
  deterministic derivation, safety, and input behavior. Publish an optional
  reference algorithm with separate core and reference case suites.
- cmdux `842338b` adoption gaps against the core: shortcut origin replaces the
  committing surface instead of being recorded independently; a provider can
  suppress capture with `learn = false`; without `persistable_nodes`, a named
  invocation can lose its recorded path and incorrectly mark arguments present.
  A conforming binding must correct these behaviors or explicitly exclude the
  affected commands from its claim.
- Other cmdux core gaps: equal-time events in one writer's numbered segments can
  replay in filename order rather than writer order after a backward clock move;
  structured slot navigation cannot skip an empty optional slot to reach a later
  required slot.
- Reference-only cmdux differences: native shortcut use receives direct credit;
  the pinned calendar cutoff chooses the earlier occurrence at the tested Lord
  Howe fold, while the reference chooses the later one; and flow proposal IDs
  omit project and context. The reference adapter projects these differences
  where needed. cmdux has no indexed resource slots, so resource cases use a
  surrogate and are not evidence of native support.
- The open reference questions on full promotion-path identity and literal `/`
  in adapter token paths are tracked in [REFERENCE.md](REFERENCE.md).
