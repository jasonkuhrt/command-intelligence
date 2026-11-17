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
