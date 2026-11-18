# Command Intelligence

A specification for command systems that learn from committed intent while
keeping the command vocabulary, execution, and user input under explicit control.
It applies to command lines, pickers, palettes, and other hosts with a semantic
command model.

- [Specification](SPEC.md): the normative, tool-independent guarantees.
- [Reference algorithm](REFERENCE.md): optional scoring, promotion, and flows.
- [Host bindings](BINDINGS.md): decisions each implementation supplies, with a
  Neovim example.
- [Conformance](conformance/README.md): portable cases and runner contract.
- [Versioning](VERSIONING.md) and [changelog](CHANGELOG.md).

The current specification is **0.4.0**. An implementation declares the version
it conforms to. The reference algorithm and its fixtures are based on cmdux;
passing their adapter is not a native cmdux conformance claim. The Obsidian
command palette is planned.
