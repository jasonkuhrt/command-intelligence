# Versioning

The specification uses `MAJOR.MINOR.PATCH`, starting at 0.1.0. A change to
existing stored facts or a ranking result required by the normative core for
the same inputs is major, including before 1.0. Another incompatible change to
existing required observable behavior is also major.

- Before 1.0, a new mandatory requirement that does not change existing stored
  facts or results is minor; from 1.0 onward it is major. An optional new
  concept or rule that leaves existing results unchanged is minor.
- Wording, fixture, and runner corrections that leave normative results and
  requirements unchanged are patches.

A change to the informative reference algorithm is minor before 1.0. From
1.0 onward it is major if it changes reference outputs, and minor otherwise.
If a change also alters a normative requirement, the normative rules above
apply independently.

An implementation MUST declare the specification version it conforms to. A
new mandatory requirement may require an implementation to change and may
affect its consumers, even when existing results are unchanged. A patch does
not change the contract for consumers; a corrected fixture can expose an
implementation's existing nonconformance. A conformance claim covers the
normative specification and applicable host binding, not just its fixtures. A
reference-algorithm claim additionally covers the declared parts of that algorithm.
