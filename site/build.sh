#!/usr/bin/env bash
# Renders the specification documents to _site/ with spec-md, the renderer the GraphQL spec uses.
set -euo pipefail
cd "$(dirname "$0")/.."
out=_site
repo=https://github.com/jasonkuhrt/command-intelligence/blob/main
rm -rf "$out"
mkdir -p "$out"
render() {
  npx --yes spec-md@3.1.0 "$1" |
    sed -E \
      -e 's#href="SPEC\.md#href="index.html#g' \
      -e 's#href="REFERENCE\.md#href="reference.html#g' \
      -e 's#href="BINDINGS\.md#href="bindings.html#g' \
      -e "s#href=\"((conformance|VERSIONING|CHANGELOG|README)[^\"]*)\"#href=\"$repo/\\1\"#g" \
      >"$out/$2"
}
render SPEC.md index.html
render REFERENCE.md reference.html
render BINDINGS.md bindings.html
