# Command Intelligence

A specification for command systems that learn from committed intent while
keeping the command vocabulary, execution, and user input under explicit control.
It applies to command lines, pickers, palettes, and other hosts with a semantic
command model.

- [Specification](SPEC.md): normative behavior and default scoring.
- [Host bindings](BINDINGS.md): decisions each implementation supplies, with a
  Neovim example.
- [Conformance](conformance/README.md): portable cases and runner contract.
- [Versioning](VERSIONING.md) and [changelog](CHANGELOG.md).

The current specification is **0.1.0**. An implementation declares the version
it conforms to. cmdux is the reference used to derive these semantics and the
initial fixtures; the Obsidian command palette is planned.
