# Changelog

## 0.1.0

- Define the semantic command model, intent events, ranking, promotion, flows,
  safety, and input rules.
- Define host binding requirements and portable conformance cases.
- Known cmdux gap: at `842338b` shortcut origin is encoded as the surface,
  so the original surface and origin cannot both be recovered. Adoption must
  persist them separately.
- Known cmdux gap: equal-time events in one writer's numbered segments can replay
  in filename order rather than writer position after a backward clock movement.
- Known cmdux gap: at the repeated local time in the Lord Howe fixture, the
  pinned implementation chooses the earlier cutoff instead of the required later
  occurrence.
- Known cmdux gap: the same repeated-time disagreement also affects the flow
  lookback cutoff.
- Known cmdux gap: proposal IDs are derived from steps alone, so groups with
  different projects or contexts can have the same ID.
