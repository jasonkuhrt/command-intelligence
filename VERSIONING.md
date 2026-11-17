# Versioning

The specification uses `MAJOR.MINOR.PATCH`, starting at 0.1.0. The rules apply
also while the major version is zero.

- **Major:** stored facts or the ranking result for the same inputs change. An
  incompatible change to another required observable behavior is also major.
- **Minor:** a concept or rule is added without changing existing results.
- **Patch:** wording changes without changing behavior.

An implementation MUST declare the specification version it conforms to. A
conformance claim covers the specification and its applicable host binding; the
fixtures are checks of selected behavior, not a substitute for the specification.
