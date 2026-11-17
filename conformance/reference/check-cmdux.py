#!/usr/bin/env python3
"""Run the portable cases through cmdux, with one isolated state per case."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def check_slot_events(case, case_dir):
    def slots(nodes):
        for node in nodes:
            if node["kind"] == "slot":
                yield node
            yield from slots(node.get("children", []))

    declared = {node["id"]: node for node in slots(case["tree"])}
    expected = [
        event["node"]
        for event in case["events"]
        if event["session"] == "previous" and event["node"] in declared
    ]
    if not expected:
        return
    directory = case_dir / "state" / "nvim" / "cmdux" / "events" / "learning"
    records = []
    for path in sorted(directory.glob("*.jsonl")):
        for line in path.read_text().splitlines():
            if line:
                records.append((line, json.loads(line)))
    observed = []
    for line, record in records:
        node = "/".join([record["root"], *record.get("path", [])])
        if node in declared:
            assert record["arguments"] is True
            assert all(value not in line for value in declared[node].get("values", []))
            observed.append(node)
    assert observed == expected, f"slot events: expected {expected}, got {observed}"


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: check-cmdux.py /path/to/cmdux")
    source = Path(sys.argv[1]).resolve(strict=True)
    conformance = Path(__file__).resolve().parent.parent
    oracle = conformance / "reference" / "cmdux.lua"
    cases = json.loads((conformance / "cases.json").read_text())
    revision = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
    ).strip()
    print(f"cmdux {revision}", flush=True)
    with tempfile.TemporaryDirectory(prefix="command-intelligence-") as temp:
        directory = Path(temp)
        for case in cases:
            case_dir = directory / case["id"]
            case_dir.mkdir()
            case_file = case_dir / "case.json"
            case_file.write_text(json.dumps(case, ensure_ascii=False))
            env = dict(
                os.environ,
                TZ="UTC",
                CMDUX_TEST="1",
                CMDUX_SOURCE=str(source),
                CMDUX_CASE=str(case_file),
                CMDUX_FIXTURE_DIR=str(case_dir),
            )
            for name in ("CONFIG", "CACHE", "STATE", "DATA"):
                env[f"XDG_{name}_HOME"] = str(case_dir / name.lower())
            phases = ("previous", "query") if case["type"] == "ranking" else ("query",)
            for phase in phases:
                run = subprocess.run(
                    ["nvim", "--headless", "-u", "NONE", "-i", "NONE", "-l", str(oracle)],
                    env=dict(env, CMDUX_PHASE=phase),
                    cwd=case_dir,
                    capture_output=True,
                    text=True,
                    timeout=90,
                )
                if run.returncode:
                    raise RuntimeError(f"{case['id']} ({phase}):\n{run.stdout}{run.stderr}")
                if phase == "previous":
                    check_slot_events(case, case_dir)
                if phase == "query":
                    actual = json.loads(run.stdout)
                    if actual != case["expected"]:
                        raise AssertionError(
                            f"{case['id']}: expected {case['expected']}, got {actual}"
                        )
            print(f"ok {case['id']}", flush=True)
    print(f"{len(cases)} cases passed")


if __name__ == "__main__":
    main()
