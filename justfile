set positional-arguments

# The reference adapter is optional; pass a cmdux checkout to compare its output.
check-cmdux source:
    python3 conformance/reference/check-cmdux.py "$1"

lua-fmt:
    stylua conformance/reference/cmdux.lua

lua-check:
    stylua --check conformance/reference/cmdux.lua
    luac -p conformance/reference/cmdux.lua
