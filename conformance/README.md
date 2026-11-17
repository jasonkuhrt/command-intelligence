# Conformance

- [Core cases](core/README.md) test the requirements shared by every
  implementation. Their applicability follows the capabilities each case needs.
- [Reference cases](reference/README.md) test the optional, detailed algorithm
  in [REFERENCE.md](../REFERENCE.md). An implementation runs the relevant
  reference cases only for the parts it claims to follow.

Both suites use synthetic bindings; neither substitutes for the host-owned
boundary checks in [SPEC.md](../SPEC.md). Run `just check` to validate the
case schemas and fixture invariants. A passing fixture check validates the test
data, not an implementation's conformance.
